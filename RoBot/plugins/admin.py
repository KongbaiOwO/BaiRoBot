#管理员管理插件
def adminadd(message,uid,gid,config,admin):
    id=''
    for i in range(len(config['命令设置']['添加管理员']),len(message)):
        if '0'<=message[i]<='9':
            id+=message[i]
    if id in admin['管理员']['管理员'].split(','):
        return '该用户已经是管理员'
    admin['管理员']['管理员']+=','+id
    with open('../config.ini', 'w', encoding='utf-8') as f:
        admin.write(f)
    return f'[CQ:at,qq={uid}]已添加[CQ:at,qq={id}]为机器人管理员'

def admindel(message,uid,gid,config,admin):
    id = ''
    for i in range(len(config['命令设置']['撤销管理员']), len(message)):
        if '0' <= message[i] <= '9':
            id += message[i]
    if id not in admin['管理员']['管理员'].split(','):
        return '该用户本就不是管理员'
    if admin['管理员']['管理员'].split(',')[0]!=id:
        admin['管理员']['管理员']=admin['管理员']['管理员'].replace(','+id,'')
    else:
        admin['管理员']['管理员']=admin['管理员']['管理员'][len(id)+1:]
    with open('../config.ini', 'w', encoding='utf-8') as f:
        admin.write(f)
    return f'[CQ:at,qq={uid}]已撤销[CQ:at,qq={id}]的机器人管理员身份'

def run(platform,type,uid,gid,msg,BOTQQ):
    from os import mkdir
    from os.path import exists
    from configparser import ConfigParser
    if not exists('plugins/admin/'):
        mkdir('plugins/admin/')
        with open('plugins/admin/config.ini', 'w+', encoding='utf-8') as f:
            config = '''[命令设置]
添加管理员 = 添加管理员
撤销管理员 = 撤销管理员'''
            f.write(config)
    elif not exists('plugins/admin/config.ini'):
        with open('plugins/admin/config.ini', 'w+', encoding='utf-8') as f:
            config = '''[命令设置]
添加管理员 = 添加管理员
撤销管理员 = 撤销管理员'''
            f.write(config)
    config = admin = ConfigParser()
    config.read('plugins/admin/config.ini', encoding='utf-8')
    admin.read('../config.ini',encoding='utf-8')
    if type=='group' and f'[CQ:at,qq={BOTQQ}]' in msg and '在吗' in msg:
        platform.sendmsg(type, gid, '我在')
    if msg[0:len(config['命令设置']['添加管理员'])]==config['命令设置']['添加管理员'] and str(uid) in admin['管理员']['管理员'].split(','):
        platform.sendmsg(type, gid, adminadd(msg,uid,gid,config,admin))
    if msg[0:len(config['命令设置']['撤销管理员'])]==config['命令设置']['撤销管理员'] and str(uid) in admin['管理员']['管理员'].split(','):
        platform.sendmsg(type, gid, admindel(msg, uid, gid, config, admin))
