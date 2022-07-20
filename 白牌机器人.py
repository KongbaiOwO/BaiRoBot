#本模块仅用于启动机器人，具体代码详见Robot文件夹下 
import threading
from os import system,popen
from os.path import exists
from configparser import ConfigParser

def start_cqhttp():
   system('cd go-cqhttp&&.\go-cqhttp.exe faststart')

def start_server():
    system('cd RoBot&&python receive_msg.py')

def start():
    config = ConfigParser()
    if not exists('config.ini'):
        with open('config.ini', 'w+',encoding='utf-8') as f:
            config = '''[外部库安装]
flask=未完成
requests=未完成
pyyaml=未完成'''
            f.write(config)
    config.read('./config.ini', encoding='utf-8')
    if config["外部库安装"]["flask"] == "未完成":
        installflask = popen('pip install flask').read()
        print('\033[36m'+installflask)
        if 'Requirement already satisfied' in installflask:
            print("\033[36mflask模块已安装完成")
            config["外部库安装"]["flask"] = '完成'
            with open('./config.ini', 'w', encoding='utf-8') as f:
                config.write(f)
    if config["外部库安装"]["requests"] == "未完成":
        installrequests = popen('pip install requests').read()
        print('\033[36m'+installrequests)
        if 'Requirement already satisfied' in installrequests:
            print("\033[36mrequests模块已安装完成")
            config["外部库安装"]["requests"] = '完成'
            with open('./config.ini', 'w', encoding='utf-8') as f:
                config.write(f)
    if config["外部库安装"]["pyyaml"] == "未完成":
        installpyyaml = popen('pip install pyyaml').read()
        print('\033[36m'+installpyyaml)
        if 'Requirement already satisfied' in installpyyaml:
            print("\033[36mpyyaml模块已安装完成")
            config["外部库安装"]["pyyaml"] = '完成'
            with open('./config.ini', 'w', encoding='utf-8') as f:
                config.write(f)
    t1 = threading.Thread(target=start_server)
    t2 = threading.Thread(target=start_cqhttp)
    t1.start()
    t2.start()

start()
