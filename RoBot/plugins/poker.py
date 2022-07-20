#斗地主插件
def loaddata(gid):
    from json import loads
    f = open(f'plugins/poker/{gid}/data.json', 'r')
    data = loads(f.read())
    f.close()
    return data

def writedata(gid,data):
    from json import dump
    f = open(f'plugins/poker/{gid}/data.json', 'w')
    dump(data,f,sort_keys=True, indent=2)
    f.close()

def reset(gid):
    from configparser import ConfigParser
    from json import dump
    from os.path import exists
    from os import mkdir
    config=ConfigParser()
    config.read('./plugins/poker/settings.ini', encoding='utf-8')
    multiple=int(config["设置"]["基本倍数"])
    if not exists(f'./plugins/poker/{gid}/data.json'):
        mkdir(f"./plugins/poker/{gid}")
    f = open(f'./plugins/poker/{gid}/data.json', 'w+')
    data= {"last_type": [],"now": -1,"restart": 0,"join": [],"start": False,"player": {},"end": [], "multiple": multiple,  "holecard": "", "landlord": -1, "grablandlord": -1,"last": "", "last_id": -1 }
    dump(data,f,sort_keys=True, indent=2)
    f.close()

def join(gid, uid, data,platform):
    if uid in data['join']:
        platform.sendmsg('group', gid, f'[CQ:at,qq={uid}] 你已经加入了斗地主')
    elif data["start"]:
        platform.sendmsg('group', gid, f'[CQ:at,qq={uid}] 斗地主已开始，请结束后再加入')
    elif len(data["join"])==3:
        platform.sendmsg('group', gid, f'[CQ:at,qq={uid}] 已有三人加入，请稍后再加入')
    else:
        data['join'].append(uid)
        writedata(gid, data)
        platform.sendmsg('group', gid, f'[CQ:at,qq={uid}] 加入斗地主成功（{len(data["join"])}）')

def quit(gid, uid, data,platform):
    if uid not in data['join']:
        platform.sendmsg('group', gid, f'[CQ:at,qq={uid}] 你尚未加入斗地主')
    elif data["start"]:
        platform.sendmsg('group', gid, f'[CQ:at,qq={uid}] 斗地主已开始，请结束后再退出')
    else:
        del data['join'][str(uid)]
        writedata(gid, data)
        platform.sendmsg('group', gid, f'[CQ:at,qq={uid}] 退出斗地主成功（{len(data["join"])}）')

def start(gid, uid, data,platform):
    data["holecard"] = ''
    data["player"] = {}
    data['start']=True
    writedata(gid,data)
    platform.sendmsg('group', gid, '斗地主开始，正在发牌中')
    from time import sleep
    sleep(1)
    cardall={'3': 4, '4': 4, '5': 4, '6': 4, '7': 4, '8': 4, '9': 4, 'A': 4, 'B': 4, 'C': 4, 'D': 4, 'E': 4, 'F': 4, 'Y': 1, 'Z': 1}
    carname=['3','4','5','6','7','8','9','A','B','C','D','E','F','Y','Z']
    card_name = {'3': "3", '4': "4", '5': "5", '6': "6", '7': "7", '8': "8", '9': "9", 'A': "10", 'B': "J", 'C': "Q",'D': "K", 'E': "A", 'F': "2", 'Y': "小王", 'Z': "大王"}
    from random import shuffle,choice
    shuffle(data['join'])
    cont=0
    for i in data['join']:
        cont+=1
        card=''
        cardrecord={'3': 4, '4': 4, '5': 4, '6': 4, '7': 4, '8': 4, '9': 4, 'A': 4, 'B': 4, 'C': 4, 'D': 4, 'E': 4,'F': 4, 'Y': 1, 'Z': 1}
        for j in range(17):
            while True:
                cardnum=choice(carname)
                if cardall[cardnum]>0:
                    card+=cardnum
                    cardall[cardnum]-=1
                    cardrecord[cardnum]-=1
                    break
        card_sort=list(card)
        card_sort.sort()
        data['player'][i]={'card':card_sort,'record':cardrecord}
        player_card =[]
        for j in card_sort:
            player_card.append(card_name[j])
        reply = f'你的牌为：\n[{"][".join(player_card)}]'
        # reply=f'你的牌为：\n[{"][".join(player_card)}]\n记牌器：\n'
        # for j in cardrecord:
        #     reply+=f'[{card_name[j]}]:{cardrecord[j]}  '
        platform.sendgroupprivate(i,gid,reply)
    for i in cardall:
        data["holecard"]+=i*cardall[i]
    data["grablandlord"]=0
    writedata(gid,data)
    platform.sendmsg('group',gid,f'发牌完成，[CQ:at,qq={data["join"][0]}] 请问是否抢地主')

def qiangdizhu(gid, uid, data, platform):
    data["grablandlord"]=-1
    data['landlord'] = uid
    data['player'][str(uid)]['card'] += data["holecard"]
    card_name = {'3': "3", '4': "4", '5': "5", '6': "6", '7': "7", '8': "8", '9': "9", 'A': "10", 'B': "J", 'C': "Q",'D': "K", 'E': "A", 'F': "2", 'Y': "小王", 'Z': "大王"}
    card = list(data['player'][str(uid)]['card'])
    card.sort()
    data['player'][str(uid)]['card'] = ''.join(card)
    for i in data["holecard"]:
        data['player'][str(uid)]["record"][i] -= 1
    data['now']=uid
    writedata(gid, data)
    player_card = []
    for j in card:
        player_card.append(card_name[j])
    dp=''
    for j in data["holecard"]:
        dp+=card_name[j]+']['
    reply = f'抢地主成功：\n[{"][".join(player_card)}]\n底牌[{dp[0:-2]}]'
    # reply = f'抢地主成功：\n[{"][".join(player_card)}]\n记牌器：\n'
    # for j in data['player'][str(uid)]["record"]:
    #     reply += f'[{card_name[j]}]:{data["player"][str(uid)]["record"][j]}  '
    platform.sendgroupprivate(uid, gid, reply)

def cardtype(gid,uid,msg,platform):
    msg = msg.upper()
    card_name = {'3': "3", '4': "4", '5': "5", '6': "6", '7': "7", '8': "8", '9': "9", '10': "A", 'J': "B", 'Q': "C",
                 'K': "D", 'A': "E", '2': "F", '小王': "Y", '大王': "Z"}
    cardcont = {'3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0,
                'Y': 0, 'Z': 0}
    i = 0
    while i < len(msg):
        if msg[i:i + 2] == '10':
            i += 1
            card = '10'
        elif msg[i:i + 2] == '小王':
            i += 1
            card = '小王'
        elif msg[i:i + 2] == '大王':
            i += 1
            card = '大王'
        else:
            card = msg[i]
        if card not in card_name:
            platform.sendmsg('group', gid, f'[CQ:at,qq={uid}] 出牌不符合规范')
            return None
        cardcont[card_name[card]] += 1
        i += 1
    cont = {1: [], 2: [], 3: [], 4: []}
    for i in cardcont:
        if cardcont[i] != 0:
            cont[cardcont[i]].append(i)
    if len(cont[1]) == 1 and cont[2] == cont[3] == cont[4] == []:
        type = ['单牌', cont[1][0], 1]
    elif len(cont[1]) >= 5 and cont[2] == cont[3] == cont[4] == []:
        c = []
        for i in cont[1]:
            temp = {'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14}
            if i in ['F', 'Y', 'Z']:
                platform.sendmsg('group', gid, f'[CQ:at,qq={uid}] 出牌不符合规范')
                return None
            elif i in temp:
                c.append(temp[i])
            else:
                c.append(int(i))
        for i in range(len(c) - 1):
            if c[i] + 1 != c[i + 1]:
                platform.sendmsg('group', gid, f'[CQ:at,qq={uid}] 出牌不符合规范')
                return None
        type = ['顺子', c[0], len(c)]
    elif len(cont[2]) == 1 and cont[1] == cont[3] == cont[4] == []:
        type = ['对子', cont[2][0], 2]
    elif len(cont[2]) >= 3 and cont[1] == cont[3] == cont[4] == []:
        c = []
        for i in cont[2]:
            temp = {'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14}
            if i in ['F', 'Y', 'Z']:
                platform.sendmsg('group', gid, f'[CQ:at,qq={uid}] 出牌不符合规范')
                return None
            elif i in temp:
                c.append(temp[i])
            else:
                c.append(int(i))
        for i in range(len(c) - 1):
            if c[i] + 1 != c[i + 1]:
                platform.sendmsg('group', gid, f'[CQ:at,qq={uid}] 出牌不符合规范')
                return None
        type = ['连对', c[0], len(c) * 2]
    elif len(cont[3]) == 1 and cont[1] == cont[2] == cont[4] == []:
        type = ['三对', cont[3][0], 3]
    elif len(cont[3]) == 1 and len(cont[1]) == 1 and cont[2] == cont[4] == []:
        type = ['三带一', cont[3][0], 4]
    elif len(cont[3]) == 1 and len(cont[2]) == 1 and cont[1] == cont[4] == []:
        type = ['三带二', cont[3][0], 4]
    elif len(cont[3]) >= 2 and cont[2] == cont[1] == cont[4] == []:
        c = []
        for i in cont[3]:
            temp = {'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14}
            if i in ['F', 'Y', 'Z']:
                platform.sendmsg('group', gid, f'[CQ:at,qq={uid}] 出牌不符合规范')
                return None
            elif i in temp:
                c.append(temp[i])
            else:
                c.append(int(i))
        for i in range(len(c) - 1):
            if c[i] + 1 != c[i + 1]:
                platform.sendmsg('group', gid, f'[CQ:at,qq={uid}] 出牌不符合规范')
                return None
        type = ['飞机-3', c[0], len(c)]
    elif len(cont[3]) > 1 and cont[1] != []:
        d = []
        for i in cont[3]:
            temp = {'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15, 'Y': 20, 'Z': 21}
            if i in ['E', 'F', 'Y', 'Z']:
                platform.sendmsg('group', gid, f'[CQ:at,qq={uid}] 出牌不符合规范')
                return None
            elif i in temp:
                d.append(temp[i])
            else:
                d.append(int(i))
        for i in range(len(d) - 1):
            if d[i] + 1 != d[i + 1]:
                platform.sendmsg('group', gid, f'[CQ:at,qq={uid}] 出牌不符合规范')
                return None
        if len(cont[1]) + len(cont[2]) * 2 + len(cont[4]) * 4 == len(cont[3]):
            type = ['飞机1', d[0], len(d)]
    elif len(cont[3]) > 1 and cont[1] == []:
        d = []
        for i in cont[3]:
            temp = {'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15, 'Y': 20, 'Z': 21}
            if i in ['E', 'F', 'Y', 'Z']:
                platform.sendmsg('group', gid, f'[CQ:at,qq={uid}] 出牌不符合规范')
                return None
            elif i in temp:
                d.append(temp[i])
            else:
                d.append(int(i))
        for i in range(len(d) - 1):
            if d[i] + 1 != d[i + 1]:
                platform.sendmsg('group', gid, f'[CQ:at,qq={uid}] 出牌不符合规范')
                return None
        if len(cont[2]) + len(cont[4]) * 2 == len(cont[3]):
            type = ['飞机2', d[0], len(d)]
    elif len(cont[4]) == 1 and cont[2] == cont[3] == cont[1] == []:
        type = ['炸弹', cont[4][0], 4]
    elif len(cont[1]) == 2 and 'Y' in cont[1] and 'Z' in cont[1]:
        type = ['王炸', "小王", 2]
    return type

def chupai(gid,uid,data,msg,platform):
    type=cardtype(gid,uid,msg,platform)
    if type==None:
        return None
    if data['last']=='':
        msg = msg.upper()
        card_name = {'3': "3", '4': "4", '5': "5", '6': "6", '7': "7", '8': "8", '9': "9", '10': "A", 'J': "B",'Q': "C",'K': "D", 'A': "E", '2': "F", '小王': "Y", '大王': "Z"}
        cardcont = {'3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0,'F': 0,'Y': 0, 'Z': 0}
        i = 0
        while i < len(msg):
            if msg[i:i + 2] == '10':
                i += 1
                card = '10'
            elif msg[i:i + 2] == '小王':
                i += 1
                card = '小王'
            elif msg[i:i + 2] == '大王':
                i += 1
                card = '大王'
            else:
                card = msg[i]
            cardcont[card_name[card]] += 1
            i += 1
        playercardcont = {'3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0,'F': 0,'Y': 0, 'Z': 0}
        for i in data['player'][str(uid)]["card"]:
            playercardcont[i]+=1
        for i in cardcont:
            if playercardcont[i]<cardcont[i]:
                platform.sendmsg(f'[CQ:at,qq={uid}] 你没有这些牌，请检查后重新出牌')
        last = ''
        playercard=[]
        for i in cardcont:
            playercardcont[i]-=cardcont[i]
            last+=i*cardcont[i]
            for j in range(playercardcont[i]):
                playercard.append(i)
        data['last']=last
        data['last_id']=uid
        data["last_type"]=type
        data['player'][str(uid)]["card"]=playercard
        for i in range(len(data['join'])):
            if uid==data['join'][i]:
                break
        data['now']=data['join'][(i+1)%3]
        writedata(gid,data)
        platform.sendmsg('group',gid,f'[CQ:at,qq={uid}] 出牌成功\n[CQ:at,qq={data["now"]}] 请出牌：')
        card_name = {'3': "3", '4': "4", '5': "5", '6': "6", '7': "7", '8': "8", '9': "9", 'A': "10", 'B': "J",'C': "Q", 'D': "K", 'E': "A", 'F': "2", 'Y': "小王", 'Z': "大王"}
        player_card = []
        for j in data['player'][str(uid)]['card']:
            player_card.append(card_name[j])
        reply = f'出牌成功：\n[{"][".join(player_card)}]'
        # reply = f'出牌成功：\n[{"][".join(player_card)}]\n记牌器：\n'
        # for j in data['player'][str(uid)]["record"]:
        #     reply += f'[{card_name[j]}]:{data["player"][str(uid)]["record"][j]}  '
        platform.sendgroupprivate(uid, gid, reply)
        # for k in data['join']:
        #     if uid==k:
        #         continue
        #     msg = msg.upper()
        #     card_name = {'3': "3", '4': "4", '5': "5", '6': "6", '7': "7", '8': "8", '9': "9", '10': "A", 'J': "B",
        #                  'Q': "C",
        #                  'K': "D", 'A': "E", '2': "F", '小王': "Y", '大王': "Z"}
        #     cardcont = {'3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0,
        #                 'F': 0,
        #                 'Y': 0, 'Z': 0}
        #     i = 0
        #     while i < len(msg):
        #         if msg[i:i + 2] == '10':
        #             i += 1
        #             card = '10'
        #         elif msg[i:i + 2] == '小王':
        #             i += 1
        #             card = '小王'
        #         elif msg[i:i + 2] == '大王':
        #             i += 1
        #             card = '大王'
        #         else:
        #             card = msg[i]
        #         cardcont[card_name[card]] += 1
        #         i += 1
        #     for j in cardcont:
        #         data['player'][str(k)]["record"][j]-=cardcont[j]
        #     writedata(gid,data)
        #     reply = f'记牌器：\n'
        #     card_name = {'3': "3", '4': "4", '5': "5", '6': "6", '7': "7", '8': "8", '9': "9", 'A': "10", 'B': "J",
        #                  'C': "Q", 'D': "K", 'E': "A", 'F': "2", 'Y': "小王", 'Z': "大王"}
        #     for j in data['player'][str(k)]["record"]:
        #         reply += f'[{card_name[j]}]:{data["player"][str(uid)]["record"][j]}  '
        #     platform.sendgroupprivate(k, gid, reply)
    else :
        flag=False
        if type[0]==data["last_type"][0] and type[1]>data["last_type"][1] and type[2]==data["last_type"][2]:
            flag=True
        elif type[0]=='王炸':
            flag=True
        elif type[0]=='炸弹' and data["last_type"][0]!='王炸':
            flag = True
        if not flag:
            lastcard=[]
            card_name = {'3': "3", '4': "4", '5': "5", '6': "6", '7': "7", '8': "8", '9': "9", 'A': "10", 'B': "J",
                         'C': "Q", 'D': "K", 'E': "A", 'F': "2", 'Y': "小王", 'Z': "大王"}
            for i in data["last"]:
                lastcard.append(card_name[i])
            platform.sendmsg('group',gid,f'[CQ:at,qq={uid}] 出牌的类型与上轮不相同或不能压住上家的牌，上轮出牌为[{"][".join(lastcard)}]')
            return None
        msg = msg.upper()
        card_name = {'3': "3", '4': "4", '5': "5", '6': "6", '7': "7", '8': "8", '9': "9", '10': "A", 'J': "B",'Q': "C", 'K': "D", 'A': "E", '2': "F", '小王': "Y", '大王': "Z"}
        cardcont = {'3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0,'F': 0, 'Y': 0, 'Z': 0}
        i = 0
        while i < len(msg):
            if msg[i:i + 2] == '10':
                i += 1
                card = '10'
            elif msg[i:i + 2] == '小王':
                i += 1
                card = '小王'
            elif msg[i:i + 2] == '大王':
                i += 1
                card = '大王'
            else:
                card = msg[i]
            cardcont[card_name[card]] += 1
            i += 1
        playercardcont = {'3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0,'E': 0, 'F': 0, 'Y': 0, 'Z': 0}
        for i in data['player'][str(uid)]["card"]:
            playercardcont[i] += 1
        for i in cardcont:
            if playercardcont[i] < cardcont[i]:
                platform.sendmsg('group',gid,f'[CQ:at,qq={uid}] 你没有这些牌，请检查后重新出牌')
                return None
        last = ''
        playercard = []
        for i in cardcont:
            playercardcont[i] -= cardcont[i]
            last += i * cardcont[i]
            for j in range(playercardcont[i]):
                playercard.append(i)
        data['last'] = last
        data['last_id']=uid
        data["last_type"] = type
        data['player'][str(uid)]["card"] = playercard
        for i in range(len(data['join'])):
            if uid == data['join'][i]:
                break
        data['now'] = data['join'][(i + 1) % 3]
        writedata(gid, data)
        platform.sendmsg('group', gid, f'[CQ:at,qq={uid}] 出牌成功\n[CQ:at,qq={data["now"]}] 请出牌：')
        card_name = {'3': "3", '4': "4", '5': "5", '6': "6", '7': "7", '8': "8", '9': "9", 'A': "10", 'B': "J",
                     'C': "Q", 'D': "K", 'E': "A", 'F': "2", 'Y': "小王", 'Z': "大王"}
        player_card = []
        for j in data['player'][str(uid)]['card']:
            player_card.append(card_name[j])
        reply = f'出牌成功：\n[{"][".join(player_card)}]'
        # reply = f'出牌成功：\n[{"][".join(player_card)}]\n记牌器：\n'
        # for j in data['player'][str(uid)]["record"]:
        #     reply += f'[{card_name[j]}]:{data["player"][str(uid)]["record"][j]}  '
        platform.sendgroupprivate(uid, gid, reply)
        # for k in data['join']:
        #     print(11)
        #     if uid == k:
        #         continue
        #     msg = msg.upper()
        #     card_name = {'3': "3", '4': "4", '5': "5", '6': "6", '7': "7", '8': "8", '9': "9", '10': "A", 'J': "B",
        #                  'Q': "C",
        #                  'K': "D", 'A': "E", '2': "F", '小王': "Y", '大王': "Z"}
        #     cardcont = {'3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0,
        #                 'F': 0,
        #                 'Y': 0, 'Z': 0}
        #     i = 0
        #     while i < len(msg):
        #         if msg[i:i + 2] == '10':
        #             i += 1
        #             card = '10'
        #         elif msg[i:i + 2] == '小王':
        #             i += 1
        #             card = '小王'
        #         elif msg[i:i + 2] == '大王':
        #             i += 1
        #             card = '大王'
        #         else:
        #             card = msg[i]
        #         cardcont[card_name[card]] += 1
        #         i += 1
        #     for j in cardcont:
        #         data['player'][str(k)]["record"][j] -= cardcont[j]
        #     writedata(gid, data)
        #     reply = f'记牌器：\n'
        #     card_name = {'3': "3", '4': "4", '5': "5", '6': "6", '7': "7", '8': "8", '9': "9", 'A': "10", 'B': "J",
        #                  'C': "Q", 'D': "K", 'E': "A", 'F': "2", 'Y': "小王", 'Z': "大王"}
        #     for j in data['player'][str(k)]["record"]:
        #         reply += f'[{card_name[j]}]:{data["player"][str(uid)]["record"][j]}  '
        #     platform.sendgroupprivate(k, gid, reply)

def end(gid,platform):
    from configparser import ConfigParser
    from json import dump
    from os.path import exists
    from os import mkdir
    config = ConfigParser()
    config.read('./plugins/poker/settings.ini', encoding='utf-8')
    multiple = int(config["设置"]["基本倍数"])
    if not exists(f'./plugins/poker/{gid}/data.json'):
        mkdir(f"./plugins/poker/{gid}")
    f = open(f'./plugins/poker/{gid}/data.json', 'w+')
    data = {"last_type": [], "now": -1, "restart": 0, "join": [], "start": False, "player": {}, "end": [],
            "multiple": multiple, "holecard": "", "landlord": -1, "grablandlord": -1, "last": "", "last_id": -1}
    dump(data, f, sort_keys=True, indent=2)
    f.close()
    platform.sendmsg('group', gid, f'斗地主已结束')

def run(platform,type,uid,gid,msg,BOTQQ):
    if type == 'group':
        from configparser import ConfigParser
        from os.path import exists
        config = admin = ConfigParser()
        admin.read('../config.ini', encoding='utf-8')
        admin = map(int, admin['管理员']['管理员'].split(','))
        if not exists('plugins/poker/'):
            from os import mkdir
            mkdir('plugins/poker/')
        if not exists('./plugins/poker/settings.ini'):
            with open('./plugins/poker/settings.ini', 'w+', encoding='utf-8') as f:
                config = '''[命令设置]
重置游戏 = 重置斗地主
加入游戏 = 上座
退出游戏 = 下座
开始游戏 = 开始斗地主
结束游戏 = 结束斗地主
抢地主 = 抢地主
不抢地主 = 不抢
出牌前缀 = 出
过牌 = 要不起

[设置]
基本倍数=2
最高倍数=512
最低入场豆=1024
低保=3000
低保每日领取次数=3
充值汇率(1金币换?欢乐豆)=1000

[功能开关]
斗地主 = 开启'''
                f.write(config)
                config=ConfigParser()
        config.read('./plugins/poker/settings.ini', encoding='utf-8')
        if not exists(f'plugins/poker/{gid}/data.json'):
            reset(gid)
        data = loaddata(gid)
        if config['功能开关']['斗地主']=='开启':
            if msg == config['命令设置']['重置游戏'] and uid in admin:
                reset(gid)
                platform.sendmsg('group', gid, '重置斗地主成功')
            if msg == config['命令设置']['加入游戏']:
                join(gid, uid, data,platform)
            if msg == config['命令设置']['退出游戏']:
                quit(gid, uid, data,platform)
            if msg == config['命令设置']['开始游戏'] and not data['start'] and len(data['join'])==3:
                start(gid, uid, data,platform)
            if msg == config['命令设置']['不抢地主'] and uid == data['join'][data["grablandlord"]]:
                last=data["grablandlord"]
                data["grablandlord"] = data["grablandlord"]+1
                writedata(gid, data)
                if data["grablandlord"]==3 and data["restart"]<2:
                    data["restart"]+=1
                    writedata(gid, data)
                    start(gid, uid, data, platform)
                elif data["grablandlord"]==3 and data["restart"]==2:
                    qiangdizhu(gid, data["join"][0], data, platform)
                    card_name = {'3': "3", '4': "4", '5': "5", '6': "6", '7': "7", '8': "8", '9': "9", 'A': "10",
                                 'B': "J",
                                 'C': "Q", 'D': "K", 'E': "A", 'F': "2", 'Y': "小王", 'Z': "大王"}
                    qiangdizhu(gid, uid, data, platform)
                    dp = ''
                    for j in data["holecard"]:
                        dp += card_name[j] + ']['
                    platform.sendmsg('group', gid, f'[CQ:at,qq={data["landlord"]}] 因三轮未产生地主，你为本轮的地主，底牌[{dp[0:-2]}]，请出牌：')
                else:
                    platform.sendmsg('group', gid, f'[CQ:at,qq={data["join"][last]}] 不抢地主\n[CQ:at,qq={data["join"][data["grablandlord"]]}]请问是否抢地主')
            if msg == config['命令设置']['抢地主'] and uid == data['join'][data["grablandlord"]]:
                card_name = {'3': "3", '4': "4", '5': "5", '6': "6", '7': "7", '8': "8", '9': "9", 'A': "10", 'B': "J",
                             'C': "Q", 'D': "K", 'E': "A", 'F': "2", 'Y': "小王", 'Z': "大王"}
                qiangdizhu(gid, uid, data, platform)
                dp = ''
                for j in data["holecard"]:
                    dp += card_name[j] + ']['
                platform.sendmsg('group', gid, f'[CQ:at,qq={uid}] 抢地主成功，底牌[{dp[0:-2]}]，请出牌：')
            if msg[0:len(config['命令设置']['出牌前缀'])] ==config['命令设置']['出牌前缀'] and uid ==data["now"]:
                chupai(gid,uid,data,msg[len(config['命令设置']['出牌前缀']):],platform)
                if data['player'][str(uid)]['card']==[]:
                    if uid==data["landlord"]:
                        identity='地主'
                    else:
                        identity='农民'
                    platform.sendmsg('group', gid, f'[CQ:at,qq={uid}] 率先打完牌，{identity}获胜')
                    from time import sleep
                    sleep(1)
                    end(gid,platform)
            if msg in config['命令设置']['过牌'].split(','):
                if data['last']=='':
                    platform.sendmsg('group', gid, f'[CQ:at,qq={uid}] 你不能过牌，请随意出牌：')
                    return None
                for i in range(len(data["join"])):
                    if uid==data['join'][i]:
                        break
                data["now"]=data['join'][(i+1)%3]
                if data["last_id"]==data["now"]:
                    data['last']=''
                    data['last_id']=-1
                writedata(gid,data)
                platform.sendmsg('group', gid, f'[CQ:at,qq={uid}] 不出牌，\n[CQ:at,qq={data["now"]}]请出牌：')
