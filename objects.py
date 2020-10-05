import random
import requests
import re
import xml.etree.ElementTree as ET
from parsers.TenhouDecoder import getGameObject
import hashlib

class Player():
    def __init__(self, player):
        self.obj = player
        self.name = ""
        self.score = 0
        self.yaku = {}
        self.kans = 0
        self.defkan = 0
        self.placements = []
        self.scores = []

    def __str__(self):
        return f"name:**{self.name}** core:{self.score} kans:{self.kans} yaku:**{len(self.yaku)}**"


class TableRate():

    def __init__(self, rate=0.3, shugi=.50, target=30000, start=25000, uma=[30,10,-10,-30]):
        self.rate = rate
        self.shugi = shugi
        self.oka = (target - start) * 4
        self.target = target
        self.start = start
        self.uma = uma

    def __eq__(self, other):
        return (self.rate == other.rate and self.shugi == other.shugi and self.oka == other.oka and self.target == other.target and self.start == other.start and self.uma == other.uma)

    def __str__(self):
        return f"Rate: {self.rate}, Start: {self.start}, Target: {self.target}, Shugi: {self.shugi}, Oka: {self.oka}, Uma: {self.uma}"

# default values rate=0.3, shugi=.50, target=30000, start=25000, uma=[30,10,-10,-30]    
TENSAN = TableRate()
TENGO = TableRate(rate=0.5, shugi=1)
TENPIN = TableRate(rate=1, shugi=2)
    
class GameInstance():
    
    def __init__(self):
        self.waiting = []
        self.tables = {}
        self.lastError = ""
        self.players = {}
        self.logIds = set([])

        self.MAX_PLAYERS = 4 # WARNING NEVER EVER SET TO 3!
        self.rules = "000B"
        self.adminPage = ""

    def isPlaying(self,player):
        for t in self.tables:
            if player in self.tables[t]:
                return t
        return 0
        
    def getGameLink(self):
        if len(self.adminPage) < 12:
            return "Tenhou admin page not set up yet."
        return f"https://tenhou.net/0/?{self.adminPage[1:9]}"

    def reset(self):
        self.waiting = []
        self.lastError = ""
        self.players = {}
        self.logIds = set([])

        
    def scoreTable(self, players, tableRate):
        players.sort(key=lambda x: x.score,reverse=True)
        self.lastScore = ""
        
        self.lastScore += f"{tableRate}\n\n"
        self.lastScore += f"All players begin with **Start**[{tableRate.start}] points and pay the difference of the **Target**[{tableRate.target}] to first place\n" 
        self.lastScore += f"So first place gets an **Oka** of ({tableRate.start} - {tableRate.target}) × {self.MAX_PLAYERS} = {(tableRate.target - tableRate.start)*self.MAX_PLAYERS}\n\n"
        self.lastScore += f"A **Rate** of {tableRate.rate} means each 1000 points is ${tableRate.rate:.2f}\n\n"
        
        oka = [tableRate.oka] + [0]*self.MAX_PLAYERS # giving 1st place oka bonus
        for i, p in enumerate(players):
            self.lastScore += f"#{i+1}Place: (Score[{p.score}] + Oka[{oka[i]}] - Target[({tableRate.target}])/1000) × Rate[{tableRate.rate}] = ${((p.score + oka[i] - tableRate.target)/1000)*tableRate.rate:.2f}\n"

        self.lastScore += "\n"            
        self.lastScore += f"**Uma** of {tableRate.uma} is also applied based on position, and multiplied by the table **Rate**[{tableRate.rate}]\n"

        for i, p in enumerate(players):
            self.lastScore += f"#{i+1}Place: ${tableRate.rate*tableRate.uma[i]}\n"
        
        self.lastScore += "\n"
        self.lastScore += f"Finally the **Shugi Rate**[{tableRate.shugi}] is multiplied by the number of shugi and added to the final score\n"
        
        for i,p in enumerate(players):
            self.lastScore += f"#{i+1}Place: Shugi rate[{tableRate.shugi}] × Player Shugi[{p.shugi}] = {tableRate.shugi * p.shugi}\n"

        self.lastScore += "\n"
        self.lastScore += "Finally\n"

        
        for i, p in enumerate(players):

            shugi = tableRate.shugi * p.shugi
            calc = (((p.score + oka[i] - tableRate.target)/1000) + tableRate.uma[i]) * tableRate.rate + shugi
            p.payout = round(calc,2)
            self.lastScore += f"#{i+1}Place: (((({p.score}+{oka[i]}-{tableRate.target})/1000)+{tableRate.uma[i]})×{tableRate.rate}+{tableRate.shugi}×{p.shugi}) = ${p.payout}\n"

        return players


    def parseGame(self, log, rate=TENSAN):

        if "https://" in log.lower() or "http://" in log.lower():
            log = log.split("=")[1].split("&")[0]
        xml = requests.get("http://tenhou.net/0/log/?"+log).text
        print("Prasing http://tenhou.net/0/log/?"+log)

        def convertToName(s):
            ret = bytes()
            for c in s.split("%")[1:]:
                ret +=  int(c,16).to_bytes(1,"little")
            return ret.decode("utf-8")

        players = [Player(None) for i in range(4)]

        root = ET.fromstring(xml)

        type_tag = root.find('UN')
        players[0].name = convertToName(type_tag.get('n0'))
        players[1].name = convertToName(type_tag.get('n1'))
        players[2].name = convertToName(type_tag.get('n2'))
        players[3].name = convertToName(type_tag.get('n3'))

        owari = None
        for type_tag in root.findall('AGARI'):
            owari = type_tag.get("owari")
            if owari == None:
                continue
            break

        if owari == None:
            for type_tag in root.findall('RYUUKYOKU'):
                owari = type_tag.get("owari")
                if owari == None:
                    continue
                break

        if owari == None:
            self.lastError = f"Failed to parse :< Please complain to moku"
            return None            
                       
        owari = owari.split(",")
        # @TODO check if there is shugi

        if len(owari) >= 8:
            owari += [0,0,0,0,0,0,0,0]
        for i in range(0,4):
            players[i].score = int(owari[i*2])*100
            players[i].shugi = int(owari[i*2+8])

        return self.scoreTable(players, rate)

    def addWaiting(self, player):
        if player in self.waiting:
            self.lastError = f"{player.name} is already waiting"
            return 1
        if self.isPlaying(player) != 0:
            self.lastError = f"{player.name} is already playing"
            return 1
        self.waiting.append(player)
        return 0
        
    def removeWaiting(self, name):
        if name in self.waiting:
            self.waiting.remove(name)
            return 0
        self.lastError = f"{name} is not currently waiting"
        return 1

    def shuffle(self,table_size=4):
        ret = {}        
        if len(self.waiting) >= table_size:
            random.shuffle(self.waiting)
            while(len(self.waiting) >= table_size):
                count = 0
                while(str(count) in self.tables.keys()):
                    count += 1
                if not str(count) in self.tables:
                    ret[str(count)] = []
                for i in range(table_size):
                    ret[str(count)].append(self.waiting.pop())
                self.tables.update(ret)
        return ret

    def tableGG(self,tableNumber):
        if not tableNumber in self.tables:
            self.lastError = f"No table named {tableNumber}"
            return 1
        self.tables.pop(tableNumber)
        return 0
