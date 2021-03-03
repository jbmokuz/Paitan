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

LAST_ERROR = "No Error"

def getError():
    global LAST_ERROR
    tmp = "ERROR: "+LAST_ERROR
    LAST_ERROR = "No Error"
    return tmp

## Create ##

@saveInstance
def createUser(userId,userName):
    global LAST_ERROR

    if db.session.query(User).filter(User.user_name==userName).first():
        LAST_ERROR = f"User name '{userName}' already taken"
        return None
    
    if db.session.query(User).filter(User.user_id==userId).first():
        LAST_ERROR = f"User with your id '{userId}' is already registered"        
        return None

    
    password = ''.join([random.choice(string.printable[:62]) for i in range(16)])

    u = User(user_id=userId,user_name=userName)
    u.set_password(password)
    db.session.add(u)
    return password
    
@saveInstance
def createClub(clubId,clubName):
    global LAST_ERROR
    
    if db.session.query(Club).filter(Club.club_name==clubName).first():
        LAST_ERROR = f"Club with name '{clubName}', Already registered"
        return None
    
    if db.session.query(Club).filter(Club.club_id==clubId).first():
        LAST_ERROR = f"Club with id '{clubId}', Already registered"
        return None
    
    c = Club(club_id=clubId,club_name=clubName)
    db.session.add(c)
    return c.club_id


# does not work with save instance decorator
def createTourney(tourneyName):
    global LAST_ERROR
    
    if db.session.query(Tourney).filter(Tourney.tourney_name==tourneyName).first() != None:
        LAST_ERROR = "Already have a tourney by that name"
        return None
    
    t = Tourney(tourney_name=tourneyName, current_round=0)
    db.session.add(t)

    #Needed to add increment
    db.session.commit()

    return t


def createTenhouGame(replayId, scores, rate, roundNumber=0):
    global LAST_ERROR

    if replayId != None and db.session.query(TenhouGame).filter(TenhouGame.replay_id==replayId).first():
        LAST_ERROR = "Already scored that game! Will not be added!"
        return None
    
    name0, score0, shugi0, payout0, binghou0, kan0 = scores[0]
    name1, score1, shugi1, payout1, binghou1, kan1 = scores[1]
    name2, score2, shugi2, payout2, binghou2, kan2 = scores[2]
    if len(scores) > 3 :
        name3, score3, shugi3, payout3, binghou3, kan3 = scores[3]
    else:
        name3 = None
        score3 = None
        shugi3 = None
        payout3 = None
    if replayId != None:
        g = TenhouGame(replay_id=replayId, rate=rate, ton=name0, nan=name1, xia=name2, pei=name3,
                   ton_score=score0, nan_score=score1, xia_score=score2, pei_score=score3,
                   ton_shugi=shugi0, nan_shugi=shugi1, xia_shugi=shugi2, pei_shugi=shugi3,
                       ton_payout=payout0, nan_payout=payout1, xia_payout=payout2, pei_payout=payout3, round_number=roundNumber,ton_binghou=binghou0,nan_binghou=binghou1,xia_binghou=binghou2,pei_binghou=binghou3,ton_kan=kan0,nan_kan=kan1,xia_kan=kan2,pei_kan=kan3)
    else:
        g = TenhouGame(rate=rate, ton=name0, nan=name1, xia=name2, pei=name3,
                   ton_score=score0, nan_score=score1, xia_score=score2, pei_score=score3,
                   ton_shugi=shugi0, nan_shugi=shugi1, xia_shugi=shugi2, pei_shugi=shugi3,
                       ton_payout=payout0, nan_payout=payout1, xia_payout=payout2, pei_payout=payout3, round_number=roundNumber,ton_binghou=binghou0,nan_binghou=binghou1,xia_binghou=binghou2,pei_binghou=binghou3,ton_kan=kan0,nan_kan=kan1,xia_kan=kan2,pei_kan=kan3)

    db.session.add(g)

    #Needed to add increment
    db.session.commit()
    
    return g
    


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
    global LAST_ERROR
    
    u = db.session.query(User).filter(User.user_id==userId).first()
    if u == None:
        LAST_ERROR = "You are not registered! Please create an account ($createAccount)"
        return None
    c = db.session.query(Club).filter(Club.club_id==guildId).first()
    if c == None:
        LAST_ERROR = "No such club"
        return None
    if db.session.query(ClubManagement).filter(ClubManagement.user_id==userId,ClubManagement.club_id==guildId).first():
        LAST_ERROR = "You already manage this club"
        return None        
    cm = ClubManagement(club_id=guildId,user_id=userId)
    db.session.add(cm)
    return 0

@saveInstance
def addUserToClub(guildId,userId):
    global LAST_ERROR
    
    u = db.session.query(User).filter(User.user_id==userId).first()
    if u == None:
        LAST_ERROR = "You are not registered! Please create an account ($createAccount)"
        return None        
    c = db.session.query(Club).filter(Club.club_id==guildId).first()
    if c == None:
        LAST_ERROR = "No such club"
        return None        
    if db.session.query(ClubList).filter(ClubList.user_id==userId,ClubList.club_id==guildId).first():
        LAST_ERROR = "You already a member of this club"
        return None                
    cl = ClubList(club_id=guildId,user_id=userId)
    db.session.add(cl)
    return 0
    
@saveInstance
def addUserToTourney(tourneyId,userId):
    global LAST_ERROR
    
    u = db.session.query(User).filter(User.user_id==userId).first()
    if u == None:
        LAST_ERROR = "You are not registered! Please create an account ($createAccount)"
        return None                
    c = db.session.query(Tourney).filter(Tourney.tourney_id==tourneyId).first()

    if c == None:
        LAST_ERROR = "No such tourney"
        return None                
    if db.session.query(TourneyUserList).filter(TourneyUserList.user_id==userId,TourneyUserList.tourney_id==tourneyId).first():
        LAST_ERROR = "You already part of this tourney"
        return None                        
    cl = TourneyUserList(tourney_id=tourneyId,user_id=userId)
    db.session.add(cl)
    return 0

@saveInstance
def addGameToClub(clubId, tenhouGameId):
    global LAST_ERROR
    
    c = db.session.query(Club).filter(Club.club_id==clubId).first()
    if c == None:
        LAST_ERROR = "No such club"
        return None
    u = db.session.query(TenhouGame).filter(TenhouGame.tenhou_game_id==tenhouGameId).first()
    if u == None:
        LAST_ERROR = "No such game"
        return None

    if db.session.query(ClubGameList).filter(ClubGameList.club_id==clubId,ClubGameList.tenhou_game_id==tenhouGameId).first():
        LAST_ERROR = "Game already added"
        return None
    
    cl = ClubGameList(club_id=clubId,tenhou_game_id=tenhouGameId)
    db.session.add(cl)
    return 0


@saveInstance
def addGameToTourney(tourneyId, tenhouGameId):
    global LAST_ERROR
    
    c = db.session.query(Tourney).filter(Tourney.tourney_id==tourneyId).first()
    if c == None:
        LAST_ERROR = "No such tourney"
        return None
    u = db.session.query(TenhouGame).filter(TenhouGame.tenhou_game_id==tenhouGameId).first()
    if u == None:
        LAST_ERROR = "No such game"
        return None

    if db.session.query(TourneyGameList).filter(TourneyGameList.tourney_id==tourneyId,TourneyGameList.tenhou_game_id==tenhouGameId).first():
        LAST_ERROR = "Game already added"
        return None
    
    cl = TourneyGameList(tourney_id=tourneyId,tenhou_game_id=tenhouGameId)
    db.session.add(cl)
    return 0


## Delete ##

@saveInstance
def deleteClub(clubId):
    global LAST_ERROR
    
    ret = db.session.query(Club).filter(Club.club_id==clubId).first()
    if not ret:
        LAST_ERROR = "No such club"
        return None
    db.session.delete(ret)
    return 0
    
@saveInstance
def deleteUser(userId):
    global LAST_ERROR
    
    ret = db.session.query(User).filter(User.user_id==userId).first()
    if not ret:
        LAST_ERROR = "No such user"
        return None        
    db.session.delete(ret)
    return 0


@saveInstance
def deleteTourney(tourneyId):
    global LAST_ERROR
    
    ret = db.session.query(Tourney).filter(Tourney.tourney_id==tourneyId).first()
    if not ret:
        LAST_ERROR = "No such tourney"
        return None
    db.session.delete(ret)
    return 0


@saveInstance
def deleteTenhouGame(tenhouGameId):
    global LAST_ERROR
    
    ret = db.session.query(TenhouGame).filter(TenhouGame.tenhou_game_id==tenhouGameId).first()
    if not ret:
        LAST_ERROR = "No such game"
        return None
    db.session.delete(ret)
    return 0

@saveInstance
def deleteTable(tableId):
    global LAST_ERROR
    
    ret = db.session.query(TableList).filter(TableList.table_id==tableId).first()
    if not ret:
        LAST_ERROR = "No such table"
        return None
    db.session.delete(ret)
    return 0

    
## Remove ##

@saveInstance
def removeUserFromClub(guildId,userId):
    global LAST_ERROR
    
    member = db.session.query(ClubList).filter(ClubList.user_id==userId,ClubList.club_id==guildId).first()
    if not member: 
        LAST_ERROR = "No such club or user"
        return None       
    db.session.delete(member)
    return 0


@saveInstance
def removeUserFromClubManage(guildId,userId):
    global LAST_ERROR
    
    member = db.session.query(ClubManage).filter(ClubManage.user_id==userId,ClubManage.club_id==guildId).first()
    if not member:
        LAST_ERROR = "No such club or user"
        return None
    db.session.delete(member)
    return 0
    
    
@saveInstance
def removeUserFromTourney(tourneyId,userId):
    global LAST_ERROR
    
    member = db.session.query(TourneyUserList).filter(TourneyUserList.user_id==userId,TourneyUserList.tourney_id==tourneyId).first()
    if not member:
        LAST_ERROR  = "Could not remove user from tourney"
        return None
    db.session.delete(member)
    return 0


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

def getUserFromUserName(userName):

    user = db.session.query(User).filter(User.user_name==userName).first()
    return user

def getTablesFromScore(tourney, players):
    tables = {}
    print(players)
    for p in players:
        user = getUserFromTenhouName(p)
        if user:
            u = user.user_id
            table = db.session.query(TableList).filter(TableList.tourney_id==tourney.tourney_id,
                TableList.round_number==(tourney.current_round),
                (TableList.ton==u)|(TableList.nan==u)|(TableList.xia==u)|(TableList.pei==u)).first()
            if table == None:
                print(f"No such user {p}")
                continue
            tables[table.table_id] = table

    return tables


def getTourneys():
    ret = []
    for t in db.session.query(Tourney):
        ret.append(t)
    return ret

def getClubs():
    ret = []
    for c in db.session.query(Club):
        ret.append(c)
    return ret



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


def getAllClubs():
    
    ret = []
    for club in db.session.query(Club):
        ret.append(club)
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
        user = getUser(t.user_id)
        if user != None:
            ret.append(user)
    return ret
    
    
def getGamesForTourney(tourneyId):

    ret = []
    for t in db.session.query(TourneyGameList).filter(TourneyGameList.tourney_id==tourneyId):
        test = getTenhouGame(t.tenhou_game_id)
        if test != None:
            ret.append(test)
    return ret


def getGamesForClub(clubId):

    ret = []
    for t in db.session.query(ClubGameList).filter(ClubGameList.club_id==clubId):
        test = getTenhouGame(t.tenhou_game_id)
        if test != None:
            ret.append(test)
    return ret

def getGamesForUser(userName):
    ret = []
    for g in db.session.query(TenhouGame).filter((TenhouGame.ton==userName)|(TenhouGame.nan==userName)|(TenhouGame.xia==userName)|(TenhouGame.pei==userName)):
        ret.append(g)
    return ret

## Update ##

@saveInstance
def updateClubTourney(clubId, tourneyId):
    global LAST_ERROR
    
    club = getClub(clubId)
    if club == None:
        LAST_ERROR = "No such club"
        return None
    club.tourney_id = tourneyId
    return 0

@saveInstance
def updateUserTenhouName(userId, tenhouName):
    global LAST_ERROR
    
    user = getUser(userId)
    if user == None:
        LAST_ERROR = "You are not registered! Please create an account ($createAccount)"
        return None
    user.tenhou_name = tenhouName
    return 0

## Other ##

@saveInstance
def changePassword(userId):
    global LAST_ERROR
    
    u = db.session.query(User).filter(User.user_id==userId).first()
    if not u:
        LAST_ERROR = "You are not registered! Please create an account ($createAccount)"
        return None

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
def startNextRound(tourneyId, roundNumber=None):
    global LAST_ERROR

    tourney = getTourney(tourneyId)
    if tourney == None:
        LAST_ERROR = f"No such tourney!"
        return None

    tourney.current_round = tourney.current_round + 1
    return 0



def getStandings(clubId):
    
    games = getGamesForClub(clubId)

    rank = {}

    for g in games:
        if g.ton != None:
            if not g.ton in rank:
                rank[g.ton] = 0
            #rank[g.ton] += g.ton_payout
            rank[g.ton] += g.ton_kan            

        if g.nan != None:
            if not g.nan in rank:
                rank[g.nan] = 0
            #rank[g.nan] += g.nan_payout
            rank[g.nan] += g.nan_kan            

        if g.xia != None:
            if not g.xia in rank:
                rank[g.xia] = 0
            #rank[g.xia] += g.xia_payout
            rank[g.xia] += g.xia_kan            

        if g.pei != None:
            if not g.pei in rank:
                rank[g.pei] = 0
            #rank[g.pei] += g.pei_payout
            rank[g.pei] += g.pei_kan         


    ordered = []

    for n in rank:
        ordered.append([rank[n],n])
    ordered.sort(key=lambda x:x[0], reverse=True)

    return ordered


