from parsers.TenhouDecoder import getGameObject
import re

# http://tenhou.net/0/?log=2020070913gm-0209-19691-21db0170&tw=2         


CARD = ["Honitsu"    ,">Ura2"  ,"Ikkitsuukan" ,">80fu"  ,"Haneman",
        "Riichi Nomi","Bakaze" ,"Ippatsu"     ,"Tanyao"  ,"Chinitsu",
        "Chanta"     ,"Riichi" ,"Local Yaku"  ,"Uradora" ,"Chiitoitsu",
        "2sou"       ,"Yakuhai","Menzen"      ,"Sanshoku","Sanankou",
        "Other Yaku" ,"3zou"   ,"Pinfu"       ,"Iipeikou","Toitoi"]
        
         
"""
CARD = ["Chinitsu","Ippatsu","Yakuhai","Riichi","Pinfu",
        "Uradora","Bakaze","Toitoi","Dora","Tanyao",
        "Menzen","Sanshoku","Local Yaku","Akadora","Ikkitsuukan",
        "Honitsu","Iipeikou","Kan","Riichi Nomi","3zou",
        "Chanta","Chiitoitsu","> 60fu","Ron","2sou","Yakuman"]
"""

#{'type': 'RON', 'player': 1, 'hand': ['7s0', '7s1', '7s2', '4p1', '5p1', '6p2', '7p3', '8p2', '9p2', '5m2', '6m3', '7m2', 'rd0', 'rd2'], 'fu': 40, 'points': 2600, 'limit': '', 'dora': ['8p3'], 'machi': ['6p2'], 'melds': [], 'closed': True, 'uradora': [], 'fromPlayer': 2, 'yaku': [['Riichi', 1], ['Dora', 1], ['Uradora', 0]], 'yakuman': []}

def intToYaku(i):
    ret = []
    for yaku in CARD:
        if i&1 == 1:
            ret.append(yaku)
        i = i >> 1
    return ret

def updateBinghou(bing,kans,names,game):

    global CARD
    
    for r in game.rounds:
        for agari in r.agari:
            player = names[agari.player]

            if agari.fu > 80:
                bing[agari.player] = bing[agari.player] | (1 << CARD.index(">80fu"))
                
            if agari.points == 1800 or agari.points == 18000:
                bing[agari.player] = bing[agari.player] | (1 << CARD.index("Haneman"))

            if "2s" in [i.asdata()[:2] for i in agari.hand]:
                bing[agari.player] = bing[agari.player] | (1 << CARD.index("2sou"))

            if "3s" in [i.asdata()[:2] for i in agari.hand]:
                bing[agari.player] = bing[agari.player] | (1 << CARD.index("2sou"))
                        
            for yaku, han in agari.yaku:
                if han < 0:
                    continue
                print("YAKU",yaku,player)
                if yaku.split(" ")[0] in CARD and not (yaku == "Uradora" and han == 0):
                    bing[agari.player] = bing[agari.player] | (1 << CARD.index(yaku.split(" ")[0]))
                elif yaku != "Uradora" and yaku != "Dora" and yaku != "Akadora" :
                    bing[agari.player] = bing[agari.player] | (1 << CARD.index("Other Yaku"))            
                if yaku == 'Uradora' and han > 2:
                    bing[agari.player] = bing[agari.player] | (1 << CARD.index(">Ura2"))
                if yaku == "Riichi" and sum([i[1] for i in agari.yaku]) == 1:
                    bing[agari.player] = bing[agari.player] | (1 << CARD.index("Riichi Nomi"))
                if yaku == "Chankan":
                    kans[agari.player] += 5
                    
            for yaku in agari.yakuman:
                yaku = "🌟**"+yaku+"**🌟"
                print("YAKUMAN",yaku,player)
                bing[agari.player] = bing[agari.player] | (1 << 25)                
                #if not yaku in self.players[player].yaku:
                #    self.players[player].yaku[yaku] = 0
                #self.players[player].yaku[yaku] += 1

        for event in r.events:
            if event.type == "Call":
                if event.meld.type == "chakan" and event.meld.type != "kan":
                    player = names[event.player]
                    print("KAN",player)
                    kans[event.player] += 1
                    if event.player != event.meld.fromPlayer:
                        kans[event.meld.fromPlayer] -= 1

    

def getLogId(log):
    ret = ""
    rex = re.search("log=(.*)[&]{0,1}",log)
    if rex == None:
        self.lastError = "Invalid log URL"
        return 1
    try:
        if "&" in rex.group(1):
            ret = rex.group(1).split("&")[0]
        else:
            ret = rex.group(1).split("&")[0]            
    except:
        self.lastError = "Some error parsing log URL"
        return 1
    
    return ret
    

def parseTenhou(log):

    game = getGameObject(log)
    names = [n.name for n in game.players]
    binghou = [0,0,0,0]
    kans = [0,0,0,0]

    updateBinghou(binghou,kans,names,game)
    scores = [j for i,j in  enumerate(game.owari.split(",")) if i % 2 == 0][:len(names)]

    if len(game.owari.split(",")) > 8:
        shugi = [j for i,j in  enumerate(game.owari.split(",")) if i % 2 == 0][len(names):]
    else:
        shugi = [0 for i in range(len(names))]

    ret = []

    print("BING",[intToYaku(i) for i in binghou])
    
    for i in range(len(names)):
        ret.append([names[i],int(scores[i]),int(shugi[i]),binghou[i],kans[i]])

    return ret

