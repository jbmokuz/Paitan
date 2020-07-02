import random
import requests
import re
import xml.etree.ElementTree as ET
from TenhouDecoder import getGameObject
import hashlib

class Singleton(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Player():
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.yaku = {}
        self.kans = 0
        self.defkan = 0
        self.placements = []
        self.scores = []

    def __str__(self):
        return f"name:**{self.name}** core:{self.score} kans:{self.kans} yaku:**{len(self.yaku)}**"

class GameInstance(metaclass=Singleton):
    
    def __init__(self):
        self.MAX_PLAYERS = 4 # WARNING NEVER EVER SET TO 3!
        self.waiting = []
        self.lastError = ""
        self.players = {}
        self.logIds = set([])

    def reset(self):
        self.waiting = []
        self.lastError = ""
        self.players = {}
        self.logIds = set([])

    def parseGame(self,log):
        rex = re.search("log=(.*)[&]{0,1}",log)
        if rex == None:
            self.lastError = "Invalid log URL"
            return 1
        try:
            rex = rex.group(1).split("&")[0]
        except:
            self.lastError = "Some error parsing log URL"
            return 1
        if rex in self.logIds:
            self.lastError = "Already seen this log"
            return 1
            
        self.logIds.add(rex)
            
        game = getGameObject(log)
        names = [n.name for n in game.players]
        for n in names:
            if not n in self.players:
                self.players[n] = Player(n)
        for r in game.rounds:
            for agari in r.agari:
                
                player = names[agari.player]
                for yaku, han in agari.yaku:
                    if han < 0:
                        continue
                    if not yaku in self.players[player].yaku:
                        self.players[player].yaku[yaku] = 0
                    self.players[player].yaku[yaku] += 1
                for yaku in agari.yakuman:
                    yaku = "🌟**"+yaku+"**🌟"
                    if not yaku in self.players[player].yaku:
                        self.players[player].yaku[yaku] = 0
                    self.players[player].yaku[yaku] += 1
                    
            for event in r.events:
                if event.type == "Call":
                    if event.meld.type == "chakan" and event.meld.type != "kan":
                        player = names[event.player]
                        self.players[player].kans += 1
        owari = [j for i,j in  enumerate(game.owari.split(",")) if i % 2 == 0][:self.MAX_PLAYERS]
        for i,score in enumerate(owari):
            self.players[names[i]].score += int(score)

        ret = ""
        for p in names:
            ret += f"{self.players[p]}\n"
            ret += f"{[y for y in self.players[p].yaku]}\n"
        self.lastError = ret[:-1]
        
        return 0

    def report(self,name,score,place=-1):
        if not name in self.players:
            self.players[name] = Player(name)
        player = self.players[name]
        player.scores.append(score)
        player.placements.append(place)
        return 0
            
    def addPlayer(self,name):
        if not name in self.players:
            self.players[name] = Player(name)
            return 0
        else:
            self.lastError = f"{name} has already joined!"
            return 1

    def removePlayer(self,name):
        if name in self.players:
            self.players.pop(name)
            return 0
        else:
            self.lastError = f"{name} has not joined yet!"
            return 1        
                
    def addWaiting(self, name):
        if name in self.waiting:
            self.lastError = f"{name} is already waiting"
            return 1
        self.waiting.append(name)
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
                while(count in ret.keys()):
                    count += 1
                if not count in ret:
                    ret[count] = []
                for i in range(table_size):
                    ret[count].append(self.waiting.pop())
        return ret
