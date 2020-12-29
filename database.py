from objects import GameInstance
from glob import glob

from app.models import *
from app import db

import random
import string


def saveInstance(fun):
    def wrapper(*args):
        ret = fun(*args)
        db.session.commit()
        return ret
    return wrapper

## Create ###

@saveInstance
def createUser(userId,userName):

    if db.session.query(User).filter(User.user_name==userName).first():
        return -1
    
    if db.session.query(User).filter(User.user_id==userId).first():
        return -2

    
    password = ''.join([random.choice(string.printable[:62]) for i in range(16)])

    u = User(user_id=userId,user_name=userName)
    u.set_password(password)
    db.session.add(u)
    return password
    
@saveInstance
def createClub(clubId,clubName):

    if db.session.query(Club).filter(Club.club_name==clubName).first():
        return -1
    
    if db.session.query(Club).filter(Club.club_id==clubId).first():
        return -2
    
    c = Club(club_id=clubId,club_name=clubName)
    db.session.add(c)
    return c.club_id


def createTourney(tourneyName):

    if db.session.query(Tourney).filter(Tourney.tourney_name==tourneyName).first() != None:
        return -1
    
    t = Tourney(tourney_name=tourneyName)
    db.session.add(t)

    #Needed to add increment
    db.session.commit()

    return t.tourney_id


def createTenhouGame(replayUrl, ton, nan, xia, pei, tonScore, nanScore, xiaScore, peiScore):

    if db.session.query(TenhouGame).filter(TenhouGame.replay_url==replayUrl).first():
        return -1
    
    g = TenhouGame(replay_url=replayUrl, ton=ton, nan=nan, xia=xia, pei=pei, ton_score=tonScore, nan_score=nanScore, xia_score=xiaScore, pei_score=peiScore)
    
    db.session.add(g)

    #Needed to add increment
    db.session.commit()
    
    return g.tenhou_game_id
    
 
## ADD ##  

@saveInstance
def addUserToClubManage(guildId,userId):
    u = db.session.query(User).filter(User.user_id==userId).first()
    if u == None:
        return -1
    c = db.session.query(Club).filter(Club.club_id==guildId).first()
    if c == None:
        return -2
    if db.session.query(ClubManagement).filter(ClubManagement.user_id==userId,ClubManagement.club_id==guildId).first():
        return -3
    cm = ClubManagement(club_id=guildId,user_id=userId)
    db.session.add(cm)
    return 0

@saveInstance
def addUserToClub(guildId,userId):
    u = db.session.query(User).filter(User.user_id==userId).first()
    if u == None:
        return -1
    c = db.session.query(Club).filter(Club.club_id==guildId).first()
    if c == None:
        return -2
    if db.session.query(ClubList).filter(ClubList.user_id==userId,ClubList.club_id==guildId).first():
        return -3
    cl = ClubList(club_id=guildId,user_id=userId)
    db.session.add(cl)
    return 0
    
@saveInstance
def addUserToTourney(tourneyId,userId):
    u = db.session.query(User).filter(User.user_id==userId).first()
    if u == None:
        return -1
    c = db.session.query(Tourney).filter(Tourney.tourney_id==tourneyId).first()
    if c == None:
        return -2
    if db.session.query(TourneyUserList).filter(TourneyUserList.user_id==userId,TourneyUserList.tourney_id==tourneyId).first():
        return -3
    cl = TourneyUserList(tourney_id=tourneyId,user_id=userId)
    db.session.add(cl)
    return 0


@saveInstance
def addGameToTourney(tourneyId, tenhouGameId):
    c = db.session.query(Tourney).filter(Tourney.tourney_id==tourneyId).first()
    if c == None:
        return -1
    u = db.session.query(TenhouGame).filter(TenhouGame.tenhou_game_id==tenhouGameId).first()
    if u == None:
        return -2
    if db.session.query(TourneyGameList).filter(TourneyGameList.tourney_id==tourneyId,TourneyGameList.tenhou_game_id==tenhouGameId).first():
        return -3
    cl = TourneyGameList(tourney_id=tourneyId,tenhou_game_id=tenhouGameId)
    db.session.add(cl)
    return 0


## Delete ##

@saveInstance
def deleteClub(clubId):

    ret = db.session.query(Club).filter(Club.club_id==clubId).first()
    if not ret:
        return -1
    db.session.delete(ret)
    return 0
    
@saveInstance
def deleteUser(userId):

    ret = db.session.query(User).filter(User.user_id==userId).first()
    if not ret:
        return -1
    db.session.delete(ret)
    return 0


@saveInstance
def deleteTourney(tourneyId):

    ret = db.session.query(Tourney).filter(Tourney.tourney_id==tourneyId).first()
    if not ret:
        return -1
    db.session.delete(ret)
    return 0


@saveInstance
def deleteTenhouGame(tenhouGameId):

    ret = db.session.query(TenhouGame).filter(TenhouGame.tenhou_game_id==tenhouGameId).first()
    if not ret:
        return -1
    db.session.delete(ret)
    return 0

    
## Remove ##

@saveInstance
def removeUserFromClub(guildId,userId):

    member = db.session.query(ClubList).filter(ClubList.user_id==userId,ClubList.club_id==guildId).first()
    if not member:
        return -1
    return db.session.delete(member)


@saveInstance
def removeUserFromClubManage(guildId,userId):

    member = db.session.query(ClubManage).filter(ClubManage.user_id==userId,ClubManage.club_id==guildId).first()
    if not member:
        return -1
    return db.session.delete(member)
    
    
@saveInstance
def removeUserFromTourney(tourneyId,userId):

    member = db.session.query(TourneyUserList).filter(TourneyUserList.user_id==userId,TourneyUserList.tourney_id==tourneyId).first()
    if not member:
        return -1
    return db.session.delete(member)


## Get ##

def getUser(userId):

    user = db.session.query(User).filter(User.user_id==userId).first()
    return user

def getClub(guildId):

    club = db.session.query(Club).filter(Club.club_id==guildId).first()
    return club
    
def getTourney(tourneyId):

    tourney = db.session.query(Tourney).filter(Tourney.tourney_id==tourneyId).first()
    return tourney
    
def getTenhouGame(tenhouGameId):

    game = db.session.query(TenhouGame).filter(TenhouGame.tenhou_game_id==tenhouGameId).first()
    return game

## Get For ##

def getClubsForUserManage(userId):
    
    ret = []
    for cm in db.session.query(ClubManagement).filter(ClubManagement.user_id==userId):
        test = getClub(cm.club_id)
        if test != None:
            ret.append(test)
    return ret

def getClubsForUser(userId):
    
    ret = []
    for cl in db.session.query(ClubList).filter(ClubList.user_id==userId):
        test = getClub(cl.club_id)
        if test != None:
            ret.append(test)
    return ret

def getUsersForClub(clubId):

    ret = []
    for cl in db.session.query(ClubList).filter(ClubList.club_id==clubId):
        test = getUser(cl.user_id)
        if test != None:
            ret.append(test)
    return ret


def getTourneysForClub(clubId):

    ret = []
    for t in db.session.query(Tourney).filter(Tourney.club_id==clubId):
        test = getTourney(t.tourney_id)
        if test != None:
            ret.append(test)
    return ret
    
def getUsersForTourney(tourneyId):

    ret = []
    for t in db.session.query(TourneyUserList).filter(TourneyUserList.tourney_id==tourneyId):
        test = getUser(t.user_id)
        if test != None:
            ret.append(test)
    return ret
    
    
def getGamesForTourney(tourneyId):

    ret = []
    for t in db.session.query(TourneyGameList).filter(TourneyGameList.tourney_id==tourneyId):
        test = getTenhouGame(t.tenhou_game_id)
        if test != None:
            ret.append(test)
    return ret

## Update ##

@saveInstance
def updateClubTourney(clubId, tourneyId):
    club = getClub(clubId)
    if club == None:
        return -1
    club.tourney_id = tourneyId

@saveInstance
def updateUserTenhouName(userId, tenhouName):
    user = getUser(userId)
    if user == None:
        return -1
    user.tenhou_name = tenhouName
    return 0

## Other ##

@saveInstance
def changePassword(userId):
    u = db.session.query(User).filter(User.user_id==userId).first()
    if not u:
        return -1

    password = ''.join([random.choice(string.printable[:62]) for i in range(16)])
    u.set_password(password)
    return password

