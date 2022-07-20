# 需要外部库flask(pip install flask)
# 需要外部库requests(pip install requests)
# 需要外部库yaml(pip install pyyaml)
def start_server():
    import time
    from send_msg import send_msg
    import threading
    from flask import Flask,request
    from requests import post
    from os.path import exists
    import yaml
    import os

    app = Flask(__name__)

    @app.route('/') #网页主页
    def index():
        return 'Hello World'

    @app.route('/getmsg',methods=["POST"]) #接收QQ消息
    def getmsg():
        flage = False
        msg=request.get_json()
        from configparser import ConfigParser
        config=ConfigParser()
        config.read('../config.ini', encoding='utf-8')
        if "post_type" in msg and msg["post_type"]=='request' and msg['request_type']=='friend' and config['基础设置']['自动加好友审批']=='开启':
            import requests
            requests.get(f"http://{sendip}:{sendprot}/set_friend_add_request?approve=true&flag={msg['flag']}").json()
            flage=True
        if 'notice_type' in msg and msg['notice_type']=='friend_add' and 'post_type' in msg and msg['post_type']=='notice':
            print(f'已同意{msg["user_id"]}的好友请求')
            flage=True
        if "meta_event_type" in msg and msg["meta_event_type"]=='heartbeat':
            flage=True
        if flage:
            return "None"
        type=msg["message_type"] #消息种类
        message=msg["raw_message"] #原始消息
        uname=msg["sender"]["nickname"] #发送者昵称
        uid=msg["user_id"] #发送者QQ
        localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if type=="group":
            gid=msg["group_id"] #QQ群号
            gname = post(f'http://{sendip}:{sendprot}/get_group_info?group_id={gid}').json()["data"]["group_name"] #QQ群名
            print(f'[{localtime}]收到消息：{gname}({gid}) - {uname}({uid}) >>> {message}')
        elif type=="private":
            gid=0
            gname=''
            print(f'[{localtime}]收到消息：{uname}({uid}) >>> {message}')

        def plugin():
            class Platform:
                def __init__(self):
                    self.loadPlugins()
                def sendgroupprivate(self,uid,gid,replymsg):
                    import socket
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client.connect((sendip, sendprot))
                    replymsg = replymsg.replace(" ", "%20")
                    replymsg = replymsg.replace("\n", "%0a")
                    payload = f"GET /send_private_msg?group_id={gid}&user_id=" + str(uid) + "&message=" + replymsg + " HTTP/1.1\r\nHost:" + sendip + f":{sendprot}\r\nConnection: close\r\n\r\n"
                    print(f'[{localtime}]发送消息：{uid} >>> {replymsg}')
                    client.send(payload.encode("utf-8"))
                    client.close()
                def sendmsg(self, msgtype, id, replymsg):
                    send_msg(sendip, sendprot, {'msg_type': msgtype, 'number': id, 'msg': replymsg})
                def loadPlugins(self):
                    for filename in os.listdir("plugins"):
                        if not filename.endswith(".py") or filename.startswith("_"):
                            continue
                        self.runPlugin(filename)
                def runPlugin(self, filename):
                    pluginName = os.path.splitext(filename)[0]
                    plugin = __import__("plugins." + pluginName, fromlist=[pluginName])
                    plugin.run(self, type, uid, gid, message,BOTQQ)
            platform = Platform()

        plg = threading.Thread(target=plugin)
        plg.start()
        return "None"

    with open('../go-cqhttp/config.yml', 'r',encoding='utf-8') as f: #获取接收和发送的ip和端口
        cqconfig=yaml.load(f.read(),Loader=yaml.FullLoader)
        BOTQQ=cqconfig['account']['uin']
        sendip=cqconfig['servers'][0]['http']['host']
        sendprot=cqconfig['servers'][0]['http']['port']
        receiveurl=cqconfig['servers'][0]['http']['post'][0]['url']
        flage=False
        receiveip=receiveprot=''
        for i in range(len(receiveurl)):
            if receiveurl[i]=='/' and receiveurl[i-1]=='/':
                flage=True
            if flage:
                if receiveurl[i] == ':':
                    break
                elif receiveurl[i] == '.' or '0'<=receiveurl[i]<='9':
                    receiveip+=receiveurl[i]
        for j in range(i+1,len(receiveurl)):
            if flage:
                if receiveurl[j] == '/':
                    break
                elif '0'<=receiveurl[j]<='9':
                    receiveprot+=receiveurl[j]
        receiveprot=int(receiveprot)
    # if __name__ == '__main__':
    #     print(f'启动成功\n接收地址：{receiveip}:{receiveprot}\n发送地址：{sendip}:{sendprot}')
    #     app.run(debug=False, host=receiveip, port=receiveprot)
    print(f'启动成功\n接收地址：{receiveip}:{receiveprot}\n发送地址：{sendip}:{sendprot}')
    app.run(debug=False, host=receiveip, port=receiveprot)

start_server()
