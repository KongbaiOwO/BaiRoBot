import socket
import requests
import time

def get_group(sendip,sendprot,id):
    response = requests.post(f'http://{sendip}:{sendprot}/get_group_info?group_id='+str(id)).json()
    return response['data']["group_name"]

def send_msg(sendip,sendprot,resp_dict):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((sendip, sendprot))
    msg_type = resp_dict['msg_type']  # 回复类型（群聊/私聊）
    number = resp_dict['number']  # 回复账号（群号/好友号）
    msg = resp_dict['msg']  # 要回复的消息
    msg = msg.replace(" ", "%20")
    msg = msg.replace("\n", "%0a")
    if msg_type == 'group':
        payload = "GET /send_group_msg?group_id=" + str(number) + "&message=" + msg + " HTTP/1.1\r\nHost:" + sendip + f":{sendprot}\r\nConnection: close\r\n\r\n"
    elif msg_type == 'private':
        payload = "GET /send_private_msg?user_id=" + str(number) + "&message=" + msg + " HTTP/1.1\r\nHost:" + sendip + f":{sendprot}\r\nConnection: close\r\n\r\n"
    # print("发送" + payload)
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if msg_type=='group':
        print(f'[{localtime}]发送消息：{get_group(sendip,sendprot,number)}({number}) >>> {msg}')
    elif msg_type=='private':
        print(f'[{localtime}]发送消息：{number} >>> {msg}')
    client.send(payload.encode("utf-8"))
    client.close()
    return 0
