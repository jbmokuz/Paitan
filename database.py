from objects import GameInstance
from glob import glob

from app.models import User, Club, ClubManagement
from app import db

import random
import string

DB_PATH="./databases"

GAME_INSTANACE_D = {}

def writeGameInstance(guildId, gi):
    filePath = f"{DB_PATH}/{guildId}"    
    with open(filePath,'wb') as f:
        pickle.dump(gi,f)

def saveInstance(fun):
    def wrapper(*args):
        ret = fun(*args)
        db.session.commit()
        return ret
    return wrapper

@saveInstance
def addUserToClub(guildId,userId):
    u = db.session.query(User).filter(User.user_id==userId).first()
    if u == None:
        return 1
    c = db.session.query(Club).filter(Club.club_id==guildId).first()
    if c == None:
        return 2
    if db.session.query(ClubManagement).filter(ClubManagement.user_id==userId,ClubManagement.club_id==guildId).first():
        return 3
    cm = ClubManagement(club_id=guildId,user_id=userId)
    db.session.add(cm)
    return 0

@saveInstance
def createClub(clubId,clubName):


    if db.session.query(Club).filter(Club.club_name==clubName).first():
        return 1
    
    if db.session.query(Club).filter(Club.club_id==clubId).first():
        return 2

    
    c = Club(club_id=clubId,club_name=clubName)
    db.session.add(c)
    return 0


@saveInstance
def createUser(userId,userName):


    if db.session.query(User).filter(User.user_name==userName).first():
        return 1
    
    if db.session.query(User).filter(User.user_id==userId).first():
        return 2

    
    password = ''.join([random.choice(string.printable[:62]) for i in range(16)])

    u = User(user_id=userId,user_name=userName)
    u.set_password(password)
    db.session.add(u)
    return password


@saveInstance
def changePassword(userId):
    u = db.session.query(User).filter(User.user_id==userId).first()
    if not u:
        return 1

    password = ''.join([random.choice(string.printable[:62]) for i in range(16)])
    u.set_password(password)
    return password


def getClubsForUser(userId):
    
    ret = []
    for cm in db.session.query(ClubManagement).filter(ClubManagement.user_id==userId):
        ret.append(getClub(cm.club_id))
    return ret
    
def getClub(guildId):

    club = db.session.query(Club).filter(Club.club_id==guildId).first()
    if not club:
        return 1
    return club

def getUser(userId):

    club = db.session.query(User).filter(User.user_id==userId).first()
    if not club:
        return 1
    return club

    """
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
    """

"""

@saveInstance
def saveLog(gi, rawLog, parsedLog, logid):
    gi.rawLogs[logid] = rawLog
    gi.parsedLogs[logid] = parsedLog
    
    
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
"""
