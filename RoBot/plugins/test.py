#测试插件，用于检测机器人是否运行
def run(platform,type,uid,gid,msg,BOTQQ):
    if type=='group' and f'[CQ:at,qq={BOTQQ}]' in msg and '在吗' in msg:
        platform.sendmsg(type, gid, '我在')
    elif type=='private' and msg=='在吗':
        platform.sendmsg(type, uid, '我在')