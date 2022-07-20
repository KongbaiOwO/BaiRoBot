#真心话大冒险插件 
def loaddata(gid):
    from json import loads
    f = open(f'plugins/Truth_OR_Dare/{gid}/data.json', 'r')
    data = loads(f.read())
    f.close()
    return data

def writedata(gid,data):
    from json import dump
    f = open(f'plugins/Truth_OR_Dare/{gid}/data.json', 'w')
    dump(data,f,sort_keys=True, indent=2)
    f.close()

def reset(gid):
    from json import dump
    from os.path import exists
    from os import mkdir
    if not exists(f'./plugins/Truth_OR_Dare/{gid}/data.json'):
        mkdir(f"./plugins/Truth_OR_Dare/{gid}")
    f = open(f'./plugins/Truth_OR_Dare/{gid}/data.json', 'w+')
    data = {"start": False, "player": {}, "pd": False, "cf": -1, "cfxz": "", "cfdone": False, "true": [],"false": [], "end": []}
    dump(data,f,sort_keys=True, indent=2)
    f.close()

def join(gid,uid,data):
    if str(uid) in data['player']:
        send_msg({'msg_type': 'group', 'number': gid, 'msg': f'[CQ:at,qq={uid}] 你已经加入了真心话大冒险'})
    elif data["start"]:
        send_msg({'msg_type': 'group', 'number': gid, 'msg': f'[CQ:at,qq={uid}] 真心话大冒险已开始，请结束后再加入'})
    else:
        data['player'][str(uid)] = -1
        writedata(gid, data)
        send_msg({'msg_type': 'group', 'number': gid, 'msg': f'[CQ:at,qq={uid}] 加入真心话大冒险成功（{len(data["player"])}）'})

def quit(gid,uid,data):
    if str(uid) not in data['player']:
        send_msg({'msg_type': 'group', 'number': gid, 'msg': f'[CQ:at,qq={uid}] 你尚未加入真心话大冒险'})
    elif data["start"]:
        send_msg({'msg_type': 'group', 'number': gid, 'msg': f'[CQ:at,qq={uid}] 真心话大冒险已开始，请结束后再退出'})
    else:
        del data['player'][str(uid)]
        writedata(gid, data)
        send_msg({'msg_type': 'group', 'number': gid, 'msg': f'[CQ:at,qq={uid}] 退出真心话大冒险成功（{len(data["player"])}）'})

def start(gid,uid,data,msg):
    if len(data['player']) > 1:
        data["start"] = True
        data["pd"] = True
        writedata(gid,data)
        send_msg({'msg_type': 'group', 'number': gid, 'msg': f'真心话大冒险已开始，输入“{msg}”参与拼点'})
    else:
        send_msg({'msg_type': 'group', 'number': gid, 'msg': f'[CQ:at,qq={uid}] 加入人数不足，需要2人才可开始'})

def points(gid,uid,data):
    from random import randint
    if not data["start"]:
        send_msg({'msg_type': 'group', 'number': gid, 'msg': f'[CQ:at,qq={uid}] 真心话大冒险尚未开始'})
    elif str(uid) not in data['player']:
        send_msg({'msg_type': 'group', 'number': gid, 'msg': f'[CQ:at,qq={uid}] 你尚未加入真心话大冒险'})
    elif data['player'][str(uid)] != -1:
        send_msg({'msg_type': 'group', 'number': gid, 'msg': f'[CQ:at,qq={uid}] 你已经拼过点了'})
    elif not data['pd']:
        send_msg({'msg_type': 'group', 'number': gid, 'msg': f'[CQ:at,qq={uid}] 拼点尚未开始'})
    else:
        pds = randint(0, 100)
        data['player'][str(uid)] = pds
        writedata(gid,data)
        send_msg({'msg_type': 'group', 'number': gid, 'msg': f'[CQ:at,qq={uid}] 拼点成功，你的点数为{pds}'})
        all_points(gid,data)

def all_points(gid,data):
    for i in data['player']:
        if data['player'][i] == -1:
            return None
    data['pd'] = False
    d_order = sorted(data['player'].items(), key=lambda x: x[1], reverse=False)
    data["cf"] = int(d_order[0][0])
    writedata(gid,data)
    send_msg({'msg_type': 'group', 'number': gid, 'msg': f'所有人拼点完成，[CQ:at,qq={d_order[0][0]}] 拼的点数最小，请选择 真心话 还是 大冒险(请输入对应文字)'})

def punish(message,gid,uid,data,dataconfig,msg):
    if message==msg['选真心话']:
        message='真心话'
    else:
        message='大冒险'
    from random import choice
    a = {'真心话': 'zxh', "大冒险": "dmx"}
    data["cfxz"] = a[message]
    writedata(gid,data)
    punishchoice=choice(dataconfig[message].split('+'))
    send_msg({'msg_type': 'group', 'number': gid,'msg': f'[CQ:at,qq={uid}] 你选择了{message}，下面请听题\n{punishchoice}\n完成请输入“{msg["完成之后"]}”'})

def punishdone(gid,uid,data,config):
    data["cfdone"] = True
    writedata(gid,data)
    send_msg({'msg_type': 'group', 'number': gid, 'msg': f'[CQ:at,qq={uid}] 惩罚已完成\n请各位判断是否完成(完成输入“{config["肯定态度"]}”，未完成输入“{config["否定态度"]}”)'})

def judge(message,gid,uid,data,config,msg):
    if uid not in data["false"]+data["true"]:
        if message==msg['肯定态度']:
            message='真的'
            flag='true'
        else:
            message='假的'
            flag='false'
        data[flag].append(uid)
        writedata(gid,data)
        send_msg({'msg_type': 'group', 'number': gid, 'msg': f'[CQ:at,qq={uid}] 你选择了{message}'})
        if len(data["true"]) + len(data["false"]) == len(data["player"]) - 1:
            alljudge(gid,data,config)

def alljudge(gid,data,config):
    from random import randint
    from os.path import exists
    if len(data["true"]) >= len(data["false"]):
        coinadd = randint(int(config['最小奖励值']), int(config['最大奖励值']))
        if not exists(f'data/个人数据/{data["cf"]}/data.json'):
            creatpersondata(data["cf"])
        pdata=getpersondata(data["cf"])
        if "coin" not in pdata:
            pdata['coin']=coinadd
        else:
            pdata['coin']+=coinadd
        writepersondata(data["cf"],pdata)
        send_msg({'msg_type': 'group', 'number': gid,'msg': f'[CQ:at,qq={data["cf"]}]判断完成，结果为真的，获得{coinadd}个金币，现有{pdata["coin"]}个金币'})
        end(gid,data)
    else:
        coindel = randint(int(config['最小惩罚值']), int(config['最大惩罚值']))
        if not exists(f'data/个人数据/{data["cf"]}/data.json'):
            creatpersondata(data["cf"])
        pdata=getpersondata(data["cf"])
        if "coin" not in pdata:
            pdata['coin']=-coindel
        else:
            pdata['coin']-=coindel
        writepersondata(data["cf"],pdata)
        send_msg({'msg_type': 'group', 'number': gid,'msg': f'[CQ:at,qq={data["cf"]}]判断完成，结果为假的，没收{coindel}个金币，现有{pdata["coin"]}个金币'})
        end(gid,data)

def creatpersondata(uid):
    from json import dump
    from os.path import exists
    from os import mkdir
    if not exists('userdata'):
        mkdir(f"userdata")
    if not exists(f'userdata/{uid}'):
        mkdir(f'userdata/{uid}')
    f = open(f'userdata/{uid}/data.json', 'w+', encoding='utf-8')
    data={"coin":0}
    dump(data, f, sort_keys=True, indent=2)
    f.close()

def getpersondata(uid):
    from json import loads
    f = open(f'userdata/{uid}/data.json', 'r', encoding='utf-8')
    pdata=loads(f.read())
    f.close()
    return pdata

def writepersondata(uid,pdata):
    from json import dump
    f = open(f'userdata/{uid}/data.json', 'w', encoding='utf-8')
    dump(pdata, f, sort_keys=True, indent=2)
    f.close()

def end(gid,data):
    data["start"]=data["pd"]=data["cfdone"]=False
    data["cfxz"] = ""
    data['cf']= 0
    data["true"]=data['false']=data['end']=[]
    for i in data['player']:
        data["player"][i]=-1
    writedata(gid,data)
    send_msg({'msg_type': 'group', 'number': gid, 'msg': f'真心话大冒险已结束'})

def smpd(gid,data):
    if data['pd']:
        no_pd='以下玩家还未拼点：\n'
        for i in data['player']:
            if data['player'][i]==-1 :
                no_pd+=f'[CQ:at,qq={i}]\n'
        no_pd+="请以上玩家赶紧拼点"
        send_msg({'msg_type': 'group', 'number': gid, 'msg': no_pd})

def jgpd(uid, gid,data):
    if data['pd']:
        no_pd_count=0
        for i in data['player']:
            if data['player'][i]==-1 :
                no_pd_count+=1
        if no_pd_count<=len(data["player"])//2:
            data["pd"]=False
            min = 101
            min_uid = 0
            for i in data['player']:
                if data['player'][i]==-1 :
                    continue
                if min > data['player'][i]:
                    min = data['player'][i]
                    min_uid = int(i)
            data["cf"] = min_uid
            writedata(gid,data)
            send_msg({'msg_type': 'group', 'number': gid, 'msg': f'结果拼点完成，[CQ:at,qq={min_uid}] 拼的点数最小，请选择 真心话 还是 大冒险(请输入对应文字)'})
        else:
            send_msg({'msg_type': 'group', 'number': gid, 'msg': f'[CQ:at,qq={uid}]结果拼点失败，还有{no_pd_count}/{len(data["player"])}位玩家没有拼点，至少还需要{no_pd_count-len(data["player"])//2}位玩家拼点后才能结果拼点'})

def smzj(gid,data):
    if data['cfdone']:
        no_pd='以下玩家还未判断：\n'
        for i in data['player']:
            if int(i) not in data['true'] and int(i) not in data['false'] and int(i)!=data["cf"]:
                no_pd+=f'[CQ:at,qq={i}]\n'
        no_pd+="请以上玩家赶紧判断"
        send_msg({'msg_type': 'group', 'number': gid, 'msg': no_pd})

def jgzj(uid, gid,data,config):
    if data['cfdone']:
        no_pd_count = 0
        for i in data['player']:
            if data['player'][i] not in data['true'] and data['player'][i] not in data['false'] and data['player'][i]!=data["cf"]:
                no_pd_count += 1
        if (no_pd_count) < (len(data["player"])-1 // 2):
            alljudge(gid,data,config)
        else:
            send_msg({'msg_type': 'group', 'number': gid, 'msg': f'[CQ:at,qq={uid}]结果真假失败，还有{no_pd_count-1}/{len(data["player"])-1}位玩家没有判断，至少还需要{(no_pd_count-1) - (len(data["player"])-1) // 2}位玩家判断后才能结果真假'})

def addzxh(message,uid, gid):
    from configparser import ConfigParser
    config = ConfigParser()
    config.read('./plugins/Truth_OR_Dare/settings.ini', encoding='utf-8')
    config['真心话大冒险设置']['真心话']+='+'+message[len(config['真心话大冒险命令设置']['加真心话']):]
    with open('./plugins/Truth_OR_Dare/settings.ini', 'w', encoding='utf-8') as f:
        config.write(f)
    send_msg({'msg_type': 'group', 'number': gid, 'msg': f'[CQ:at,qq={uid}]真心话添加成功'})

def adddmx(message,uid, gid):
    from configparser import ConfigParser
    config = ConfigParser()
    config.read('./plugins/Truth_OR_Dare/settings.ini', encoding='utf-8')
    config['真心话大冒险设置']['大冒险'] += '+' + message[len(config['真心话大冒险命令设置']['加大冒险']):]
    with open('./plugins/Truth_OR_Dare/settings.ini', 'w',encoding='utf-8') as f:
        config.write(f)
    send_msg({'msg_type': 'group', 'number': gid, 'msg': f'[CQ:at,qq={uid}]大冒险添加成功'})

def deldmx(message, uid, gid):
    from configparser import ConfigParser
    config = ConfigParser()
    config.read('./plugins/Truth_OR_Dare/settings.ini', encoding='utf-8')
    delt=''
    addp=str(message[len(config['真心话大冒险命令设置']['删大冒险']):])
    dmx = config['真心话大冒险设置']['大冒险'].split('+')
    for i in range(len(dmx)):
        if addp==dmx[i]:
            delt=dmx.pop(i)
            break
    config['真心话大冒险设置']['大冒险']='+'.join(dmx)
    with open('./plugins/Truth_OR_Dare/settings.ini', 'w',encoding='utf-8') as f:
        config.write(f)
    if delt!='':
        send_msg({'msg_type': 'group', 'number': gid, 'msg': f'[CQ:at,qq={uid}]大冒险"{delt}"删除成功'})
    else:
        send_msg({'msg_type': 'group', 'number': gid, 'msg': f'[CQ:at,qq={uid}]未找到内容为"{addp}"的大冒险'})

def delzxh(message, uid, gid):
    from configparser import ConfigParser
    config = ConfigParser()
    config.read('./plugins/Truth_OR_Dare/settings.ini', encoding='utf-8')
    delt = ''
    addp = str(message[len(config['真心话大冒险命令设置']['删真心话']):])
    zxh = config['真心话大冒险设置']['真心话'].split('+')
    for i in range(len(zxh)):
        if addp == zxh[i]:
            delt = zxh.pop(i)
            break
    config['真心话大冒险设置']['真心话'] = '+'.join(zxh)
    with open('./plugins/Truth_OR_Dare/settings.ini', 'w', encoding='utf-8') as f:
        config.write(f)
    if delt != '':
        send_msg({'msg_type': 'group', 'number': gid, 'msg': f'[CQ:at,qq={uid}]大冒险"{delt}"删除成功'})
    else:
        send_msg({'msg_type': 'group', 'number': gid, 'msg': f'[CQ:at,qq={uid}]未找到内容为"{addp}"的大冒险'})

def run(platform,type,uid,gid,msg,BOTQQ):
    if type=='group':
        from configparser import ConfigParser
        from os.path import exists
        config=admin=ConfigParser()
        admin.read('../config.ini', encoding='utf-8')
        admin=map(int,admin['管理员']['管理员'].split(','))
        if not exists('plugins/Truth_OR_Dare/'):
            from os import mkdir
            mkdir('plugins/Truth_OR_Dare/')
        if not exists('./plugins/Truth_OR_Dare/settings.ini'):
            with open('./plugins/Truth_OR_Dare/settings.ini', 'w+', encoding='utf-8') as f:
                config = '''[真心话大冒险命令设置]
重置游戏 = 重置真心话大冒险
加入游戏 = 加入真心话大冒险
退出游戏 = 退出真心话大冒险
开始游戏 = 开始真心话大冒险
结束游戏 = 结束真心话大冒险
拼点结果 = 结果拼点
意见结果 = 结果真假
选真心话 = 真心话
选大冒险 = 大冒险
肯定态度 = 真的
否定态度 = 假的
抽点数 = 拼点
完成之后 = 已发
查没抽点 = 谁没拼点
查没投票 = 谁没投票
查大冒险 = 大冒险列表
查真心话 = 真心话列表
删真心话 = 删真心话
删大冒险 = 删大冒险
加真心话 = 添加真心话
加大冒险 = 添加大冒险
    
[真心话大冒险设置]
真心话 = 你的初吻是几岁在什么地方被什么人夺去的?+自己最丢人的事+你的初恋对象是谁?+最喜欢在座哪位异性+如果有来生，你选择当?+如果让你选择做一个电影中的角色，你会选谁呢?+哭得最伤心的是哪一次?为什么?+ 如果请你从在座的里面选一位做你的男女朋友+你会选谁?+ 最喜欢吃的食物?+曾经看了流泪的电影?（至少说出三个）+无聊的时候一般做什么?+理想中的另一半是什么样子?+你在寂寞时，会想起谁?+只给你一天时间当异性，你最想做什么?+平生最成功的一次撒谎?+如果一天之内要用光十万元，你要怎么样花?+你最讨厌什么样的人?+ 你觉得自己的脸皮厚还是薄?+你最怕的事情或东西是什么(说出三件)。+结婚后希望生男孩还是女孩(只能选择一个，说出原因)。+最欣赏自己哪个部位?对自己那个部位最不满意?+在坐的人中谁是你最崇拜的人？为什么？+ 异性知己有几个？+说出你最近做的糗事+拉完屎你会回头看坑吗!+如果你即将要死了+你会做什么?+说出几个你喜欢过的人的名字（最少3个）+去你喜欢的人家里，想拉肚子怎么办。+你喜欢裸睡么？+上厕所后洗手么？+打算什么时候结婚?+你在意你的老婆(老公)不是处女(处男)吗?+你会为了爱情牺牲一切+包括生命吗?+与喜欢的人见面+想要穿成什么样?+如果你爱的人不爱你怎么办?（认真回答，禁止凉拌）+对你而言，爱情和友情哪个比较重要?+如果你在野外上厕所没带纸你会怎么做?+你最喜欢的粗话是什么?+用四个字形容你的长相+你敢向喜欢的异性表白么?+如果别人看到你们新婚之夜那事+你会如何?+你们家里谁的脾气最大?+说出自己的一个异性知己。+你最受不了别人对你做什么。+觉得失去什么最可怕。+如果你心情不好，会怎样？+你最喜欢的小说是什么。+你最害怕的东西是什么。（说出3件)+你觉得自己放的屁臭不臭。+收到过最难忘的礼物是什么。+你现在暗恋谁？（异性非明星，敢玩敢做）+你最讨厌别人说的关于你的绯闻是什么+你看过或者收藏了多少黄色小电影。（都是老司机，别藏着掖着了。）+你认为在座的哪一位异性可以成为你的性幻想对象？+你会为爱自杀吗？+如果看到自己最爱的人熟睡在你面前你会做什么？（实话实说！）+自己最爱的一首歌+比较喜欢爸爸还是妈妈（是不是很难抉择呢？）+你最想要的两个东西。+如果给你一个机会去世界上任何一个地方旅行你会去：+说一个你的愿望！+如果让你有一种超能力，你会选择？+最喜欢的电影+梦中情人？+如果有一天，你生命中最重要的东西离你而去了，你会怎么办？+你在乎别人看你的眼光吗？会为了众人的反对放弃自己想要的东西或人吗？+在你心中谁最可信？+如果你有100万元，让在座的某个人帮你保存，你会选择谁？+你希望在座的谁得到幸福？+你会选择你爱的人还是爱你的人。+如果有一天在座的某个人和你吵架，你会怎么办？（@那个人并说怎么办）+你最不开心的时候会有什么表现？+你的理想职业。+如果有一天在座的某个人对你说：“我爱上你了。”你怎么办？（@他并说怎么办！）+在你眼中，在座的某个人是个怎么样的人？（@他并说明）+在现场所有同学中，你看哪位异性同学最舒服？+让你一直念念不忘的一位异性的名字？+你的仇人在上厕所时，没纸出不来，你怎么办？？+你前任结婚了，你愿意参加她婚礼吗？+半夜遇见劫匪，他说不唱歌不让你走，你会唱什么？+如果情敌掉水里了，你会怎么样？+你觉得你本人好看，还是照片好看？+抽烟的男人有味道，还是喝酒的男人有味道？+你的初吻是几岁在什么地方被什么人夺去的?+你的初恋对象是谁？+对梦中情人有什么要求？（至少5个）+说出3个怪癖+每天睡觉会想起的人是谁？+最害怕的事情或东西是什么？+做过最丢脸的事
大冒险 = @群内任意群友并说“我喜欢你”+评价群内任意一位群友+发语音唱歌（至少三句以上）+拍一张桌面的照片+ 在群里歌唱《姐就是女王》（四五句即可）+说一句虎哥圣经+发一个自己的黑历史+大喊三声“我卖身不卖艺啊”。+发语音大喊：“我好寂寞啊。”+@玩家中的任意一个人并说一句对他的坏话+对qq好友说“窝稀饭你!”然后截图到群里+别人空间留言我爱你然后截图+拍一张你鞋子的照片发到群里+去在坐某个异性人的空间里留言10条“我爱你”并截屏。+回答在座的人的任意2个问题！+对列表的一个异性发“一夜10元来不来？”并截图。+选一个女 生说 ：我将把你紧紧 地搂在怀中，吻你亿万次，像在赤道上面那样炽烈的吻！截图发在群里。+发表动态“我要给你暖被窝@列表好友”20赞后可删除！+和某人换情侣头像一天+对一个好友发送：但愿陪在你身边的人是我
最小奖励值 = 10
最大奖励值 = 50
最小惩罚值 = 10
最大惩罚值 = 50
    
[功能开关]
真心话大冒险 = 开启'''
                f.write(config)
                config=ConfigParser()
        config.read('./plugins/Truth_OR_Dare/settings.ini', encoding='utf-8')
        if not exists(f'plugins/Truth_OR_Dare/{gid}/data.json'):
            reset(gid)
        data = loaddata(gid)
        if config['功能开关']['真心话大冒险']=='开启':
            if msg==config['真心话大冒险命令设置']['重置游戏'] and uid in admin:
                reset(gid)
                platform.sendmsg('group', gid, '重置真心话大冒险成功')
            if msg==config['真心话大冒险命令设置']['加入游戏']:
                join(gid,uid,data)
            if msg==config['真心话大冒险命令设置']['退出游戏']:
                quit(gid,uid,data)
            if msg==config['真心话大冒险命令设置']['开始游戏']:
                start(gid,uid,data,config['真心话大冒险命令设置']['抽点数'])
            if msg==config['真心话大冒险命令设置']['抽点数']:
                points(gid,uid,data)
            if (msg==config['真心话大冒险命令设置']['选真心话'] or msg==config['真心话大冒险命令设置']['选大冒险']) and uid==data["cf"] and data["cfxz"]=='':
                punish(msg,gid,uid,data,config['真心话大冒险设置'],config['真心话大冒险命令设置'])
            if msg==config['真心话大冒险命令设置']['完成之后'] and uid==data["cf"] and data["cfxz"]!='':
                punishdone(gid,uid,data,config['真心话大冒险命令设置'])
            if (msg==config['真心话大冒险命令设置']['肯定态度'] or msg==config['真心话大冒险命令设置']['否定态度']) and data['cfdone'] and uid!=data["cf"]:
                judge(msg,gid,uid,data,config['真心话大冒险设置'],config['真心话大冒险命令设置'])
            if msg == config['真心话大冒险命令设置']['查没抽点']:
                smpd(gid,data)
            if msg == config['真心话大冒险命令设置']['拼点结果']:
                jgpd(uid,gid,data)
            if msg == config['真心话大冒险命令设置']['查没投票']:
                smzj(gid,data)
            if msg == config['真心话大冒险命令设置']['意见结果']:
                jgzj(uid,gid,data,config['真心话大冒险设置'])
            if msg[0:len(config['真心话大冒险命令设置']['加真心话'])] == config['真心话大冒险命令设置']['加真心话'] and uid in admin:
                addzxh(msg,uid, gid)
            if msg[0:len(config['真心话大冒险命令设置']['加大冒险'])] == config['真心话大冒险命令设置']['加大冒险'] and uid in admin:
                adddmx(msg, uid, gid)
            if msg == config['真心话大冒险命令设置']['查真心话']:
                zxh=config['真心话大冒险设置']['真心话'].split('+')
                cont, page = 0, 1
                reply=f'真心话题库(共{len(zxh)}个)：\n----------第{page}页----------'
                for i in zxh:
                    cont+=1
                    reply+=f'\n{cont}. {i}'
                    if cont%10 == 0:
                        page+=1
                        platform.sendmsg('group', gid, reply)
                        reply = f'----------第{page}页----------'
                        from time import sleep
                        sleep(1)
                if cont%10!=0:
                    platform.sendmsg('group', gid, reply)
            if msg == config['真心话大冒险命令设置']['查大冒险']:
                dmx=config['真心话大冒险设置']['大冒险'].split('+')
                cont, page = 0, 1
                reply = f'大冒险题库(共{len(dmx)}个)：\n----------第{page}页----------'
                for i in dmx:
                    cont += 1
                    reply += f'\n{cont}. {i}'
                    if cont % 10 == 0:
                        page += 1
                        platform.sendmsg('group', gid, reply)
                        reply = f'----------第{page}页----------'
                        from time import sleep
                        sleep(1)
                if cont % 10 != 0:
                    platform.sendmsg('group', gid, reply)
            if msg[0:len(config['真心话大冒险命令设置']['删大冒险'])] == config['真心话大冒险命令设置']['删大冒险'] and uid in admin:
                deldmx(msg, uid, gid)
            if msg[0:len(config['真心话大冒险命令设置']['删真心话'])] == config['真心话大冒险命令设置']['删真心话'] and uid in admin:
                delzxh(msg, uid, gid)

def get_group(sendip,sendprot,id):
    import requests
    response = requests.post(f'http://{sendip}:{sendprot}/get_group_info?group_id='+str(id)).json()
    return response['data']["group_name"]

def send_msg(resp_dict):
    import socket
    import time
    import yaml
    with open('../go-cqhttp/config.yml', 'r',encoding='utf-8') as f: #获取接收和发送的ip和端口
        cqconfig=yaml.load(f.read(),Loader=yaml.FullLoader)
        sendprot=cqconfig['servers'][0]['http']['port']
        sendip=cqconfig['servers'][0]['http']['host']
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
