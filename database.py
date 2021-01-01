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
    
    t = Tourney(tourney_name=tourneyName, current_round=1)
    db.session.add(t)

    #Needed to add increment
    db.session.commit()

    return t.tourney_id


def createTenhouGame(replayId, scores, rate):

    if db.session.query(TenhouGame).filter(TenhouGame.replay_id==replayId).first():
        return -1
    
    name0, score0, shugi0, payout0 = scores[0]
    name1, score1, shugi1, payout1 = scores[1]
    name2, score2, shugi2, payout2 = scores[2]
    if len(scores) > 3 :
        name3, score3, shugi3, payout3 = scores[3]
    else:
        name3 = None
        score3 = None
        shugi3 = None
        payout3 = None

    g = TenhouGame(replay_id=replayId, rate=rate, ton=name0, nan=name1, xia=name2, pei=name3,
                   ton_score=score0, nan_score=score1, xia_score=score2, pei_score=score3,
                   ton_shugi=shugi0, nan_shugi=shugi1, xia_shugi=shugi2, pei_shugi=shugi3,
                   ton_payout=payout0, nan_payout=payout1, xia_payout=payout2, pei_payout=payout3)
    
    db.session.add(g)

    #Needed to add increment
    db.session.commit()
    
    return g.tenhou_game_id
    


def createTable(tourneyId, roundNumber, ton, nan, xia, pei):

    # No check for multiple tables as you could be playing more then one table at the same time
    
    table = TableList(tourney_id = tourneyId, round_number = roundNumber, ton=ton, nan=nan, xia=xia, pei=pei, finished=0)
    db.session.add(table)

    #Needed to add increment
    db.session.commit()
    
    return table.table_id


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

@saveInstance
def deleteTable(tableId):

    ret = db.session.query(TableList).filter(TableList.table_id==tableId).first()
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

def getTable(tableId):

    table = db.session.query(TableList).filter(TableList.table_id==tableId).first()
    return table

## Get From ##

def getUserFromTenhouName(tenhouName):

    user = db.session.query(User).filter(User.tenhou_name==tenhouName).first()
    return user

## Get For ##

def getTablesForRoundTourney(tourneyId, roundNumber, unFinished=False):

    ret = []

    for table in db.session.query(TableList).filter(TableList.tourney_id==tourneyId, TableList.round_number==roundNumber):
        if unFinished:
            if table.finished == 0:
                ret.append(table)
        else:    
            ret.append(table)
    return ret

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

@saveInstance
def finishTable(tableId,finished=1):
    table = getTable(tableId)
    if table == None:
        return -1
    table.finished = finished
    return 0

@saveInstance
def startNextRound(tourneyId):
    tourney = getTourney(tourneyId)
    if tourney == None:
        return -1
    tourney.current_round = tourney.current_round + 1
