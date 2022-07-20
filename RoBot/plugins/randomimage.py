#随机图片插件 需要外部库PIL(pip install Pillow)
def run(platform,type,uid,gid,msg,BOTQQ):
    from io import BytesIO
    from requests import get
    from json import loads
    from os import mkdir,popen
    from os.path import exists
    from configparser import ConfigParser
    def rdimage(gid):
        from PIL import Image
        r = get('https://acg.toubiec.cn/random.php?ret=json')
        r = r.text
        rjson = loads(r)
        response = get(rjson[0]['imgurl'])
        image = Image.open(BytesIO(response.content))
        image.save('../go-cqhttp/data/images/随机图.png')
        platform.sendmsg(type, gid, '[CQ:image,file=随机图.png]')

    def rddog(gid):
        from PIL import Image
        r = get('https://shibe.online/api/shibes?count=1&urls=true&httpsUrls=true')
        r = r.text
        rjson = loads(r)
        response = get(rjson[0])
        image = Image.open(BytesIO(response.content))
        image.save('../go-cqhttp/data/images/随机狗.png')
        platform.sendmsg(type, gid, '[CQ:image,file=随机狗.png]')

    def rdcat(gid):
        from PIL import Image
        response = get("https://thiscatdoesnotexist.com/")
        image = Image.open(BytesIO(response.content))
        image.save('../go-cqhttp/data/images/随机猫.png')
        platform.sendmsg(type, gid, '[CQ:image,file=随机猫.png]')

    if not exists('plugins/randomimage/'):
        mkdir('plugins/randomimage/')
        with open('plugins/randomimage/config.ini', 'w+', encoding='utf-8') as f:
            config='''[功能开关]
随机猫 = 开启
随机狗 = 开启
随机图 = 开启

[命令设置]
随机猫 = 来只猫
随机狗 = 来只狗
随机图 = 来张图
[外部库安装]
安装=未完成'''
            f.write(config)
    elif not exists('plugins/randomimage/config.ini'):
        with open('plugins/randomimage/config.ini', 'w+', encoding='utf-8') as f:
            config = '''[功能开关]
随机猫 = 开启
随机狗 = 开启
随机图 = 开启

[命令设置]
随机猫 = 来只猫
随机狗 = 来只狗
随机图 = 来张图
[外部库安装]
安装=未完成'''
            f.write(config)
    config = ConfigParser()
    config.read('plugins/randomimage/config.ini', encoding='utf-8')
    if config["外部库安装"]["安装"]=="未完成":
        installPIL=popen('pip install Pillow').read()
        if 'Requirement already satisfied' in installPIL:
            print("PIL模块已安装完成")
            config["外部库安装"]["安装"]='完成'
            with open('plugins/randomimage/config.ini', 'w', encoding='utf-8') as f:
                config.write(f)
    if msg==config['命令设置']['随机图'] and type == 'group' and config['功能开关']['随机图']=='开启':
        rdimage(gid)
    if msg==config['命令设置']['随机狗'] and type == 'group' and config['功能开关']['随机狗']=='开启':
        rddog(gid)
    if msg==config['命令设置']['随机猫'] and type == 'group' and config['功能开关']['随机猫']=='开启':
        rdcat(gid)