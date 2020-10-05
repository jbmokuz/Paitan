from objects import GameInstance
from glob import glob
from os import path
import requests
import pickle

DB_PATH="./databases"

GAME_INSTANACE_D = {}

def writeGameInstance(guildId, gi):
    filePath = f"{DB_PATH}/{guildId}"    
    with open(filePath,'wb') as f:
        pickle.dump(gi,f)

def saveInstance(fun):
    def wrapper(guildId,*args):
        gi = getGameInstance(guildId)
        ret = fun(gi,*args)
        if ret != None:
            writeGameInstance(guildId,ret)
            return ret
        return gi
    return wrapper

def getGameInstance(guildId):
    global GAME_INSTANACE_D
    if guildId in GAME_INSTANACE_D:
        return GAME_INSTANACE_D[guildId]
    
    filePath = f"{DB_PATH}/{guildId}"
    if not path.exists(filePath):
        gi = GameInstance()
        writeGameInstance(guildId,gi)
    with open(filePath,'rb') as f:
        gi = pickle.load(f)
    GAME_INSTANACE_D[guildId] = gi
    return gi
    
@saveInstance
def setAdminPage(gi,adminPage):

    if len(adminPage) < 12:
        return None
    if adminPage[0] != "C":
        return None
    
    gi.adminPage = adminPage
    return gi

@saveInstance
def setRules(gi,rule):
    
    try:
        rule = int(rule,16)
    except:
        return None
    if rule > 0xFFFF:
        return None
    
    gi.rule = rule
    return gi
