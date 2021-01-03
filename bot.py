import discord, os, random
from discord.ext import commands
from database import *
import requests, sys, re
import xml.etree.ElementTree as ET
import copy
import urllib
from discord.ext.commands import has_permissions, MissingPermissions
from database import *
from functions import *
from parsers.parse import getLogId

if len(sys.argv) > 1:
    TOKEN = os.environ["DISCORD_DEV_TOKEN"]
else:
    TOKEN = os.environ["CHIITAN_TOKEN"]

bot = commands.Bot("$")

def get_vars(ctx):
    player = ctx.author
    chan = ctx.channel
    club = getClub(chan.guild.id)
    if club == None:
        createClub(chan.guild.id,chan.guild.name)
    club = getClub(chan.guild.id)
    return player, chan, club

#id=119046709983707136 name='moku' discriminator='9015'


@bot.command()
async def changePassword(ctx):
    """
    Get a new password for your account
    """
    player, chan, club = get_vars(ctx)

    passwd = changePassword(player.id)
    if passwd == None:
        await player.send(getError())
        return
    
    username = player.name+"#"+player.discriminator    
    await player.send(f"Username:{username} Pass:{passwd}")
    
@bot.command()
async def createAccount(ctx):
    """
    Create an account for this guild
    """
    player, chan, club = get_vars(ctx)
    username = player.name+"#"+player.discriminator

    # This is the only time we have the password for a user
    # The password hash is stored
    passwd = createUser(player.id,username)
    if passwd == None:
        await player.send(getError())
        return
    else:
        ret = f"Username:{username} Pass:{passwd}"
        await player.send(ret)

    # Can they manage this chan?
    if player.guild_permissions.administrator:
        ret = addUserToClubManage(chan.guild.id,player.id)
        if ret != None:
            await player.send(f"Now managing {chan.guild.name}")
        else:
            await player.send(getError())

    # Add user to chan
    ret = addUserToClub(chan.guild.id,player.id)
    if ret != None:
        await player.send(f"You are now a member of {chan.guild.name}")
    else:
        await player.send(getError())

    await player.send("Manage account @ http://yakuhai.com (Currently only for guild admins)")


@bot.command()
async def join(ctx):
    """
    Join current tourney
    """
    player, chan, club = get_vars(ctx)
    ret = addUserToTourney(club.tourney_id,player.id)
    if ret == None:
        await chan.send(getError())
        return
    await chan.send("Added!")

@bot.command()
async def leave(ctx):
    """
    Join current tourney
    """
    player, chan, club = get_vars(ctx)
    ret = removeUserFromTourney(club.tourney_id,player.id)
    if ret == None:
        await chan.send(getError())
        return
    await chan.send("Removed")


@bot.command()
async def kick(ctx, userName):
    """
    kick a player from a tourney
    """
    player, chan, club = get_vars(ctx)

    user = getUserFromUserName(userName)
    if user == None:
        await chan.send("Could not find user by that name")
    
    ret = removeUserFromTourney(club.tourney_id,player.id)
    if ret == None:
        await chan.send(getError())
        return
    await chan.send("Removed")
    
@bot.command()
async def list(ctx):
    """
    Join current tourney
    """
    player, chan, club = get_vars(ctx)
    if club.tourney_id == None:
        await chan.send("No tourney is currently running")
        return

    tourney = getTourney(club.tourney_id)

    ret = "```"
    # Havent shuffled for tables yet
    if tourney.current_round == 0:    
        users = getUsersForTourney(club.tourney_id)
        if users == []:
            await chan.send("No users have joined")
            return
        for u in users:
            ret += u.user_name
            if u.tenhou_name != None:
                ret += " ("+u.tenhou_name+")"
            ret += "\n"

    else:
        ret += printTables(tourney)
        
    ret += "```"
    await chan.send(ret)


    
@bot.command()
@commands.has_permissions(administrator=True)
async def shuffle(ctx):
    """
    Shuffle for list for tables
    """
    player, chan, club = get_vars(ctx)
    
    if club.tourney_id == None:
        await chan.send("No tourney is currently running")
        return

    tourney = getTourney(club.tourney_id)
    users = getUsersForTourney(club.tourney_id)

    # We are starting the next round now!
    startNextRound(club.tourney_id)
    
    ret = "```"

    # First round is just random
    if tourney.current_round == 1:

        #random.shuffle(users)        
        tables = [[u.user_id for u in users[i:i+4]] for i in range(0,len(users),4)]

        
    # We want to ensure no one plays anyone they played the first round
    # Need at least 16 people, but should still get you the least overlap?
    else:
        
        tables = getTablesForRoundTourney(tourney.tourney_id,tourney.current_round)
        
        byes = []

        # This is a bye table as there is not 4 players
        # @NOTE always assuming 4 player mahjong for now
        if tables[-1].pei == None:
            byes = tables[-1]
            byes = [byes.ton, byes.nan, byes.xia, byes.pei]
            tables = tables[:-1]

        tables = [[i.ton, i.nan, i.xia, i.pei] for i in tables]

        # Shuffle the order of all the tables 
        random.shuffle(tables)

        # Shuffle all the tables players orders
        for t in tables:
            random.shuffle(t)

        # Make it so the tables have no repeating players
        for off in range(1,4):
            tmp = [[] for i in tables]
            for i,t in enumerate(tables):
                tmp[i] += tables[i][:off]
                tmp[i] += tables[(i+1)%len(tables)][off:]
            tables = tmp

        count = 0
        newByes = []

        for i, b in enumerate(byes):
            if b == None:
                break
            tmp = tables[count][i]
            tables[count][i] = b
            newByes.append(tmp)
            count = (count + 1) % len(tables)
            
        tables += [newByes]

    for t in tables:
        if len(t) < 4:
            t += [None for i in range(4 - len(t))]
        createTable(tourney.tourney_id, tourney.current_round, t[0], t[1], t[2], t[3])
        
    # Now we print the stuff out
    
    ret += printTables(tourney)
    ret += "```"


    await chan.send(ret)

@bot.command()
@commands.has_permissions(administrator=True)
async def topCut(ctx,numberOfTables):
    """
    Cut the top number of tables
    """

    try:
        numberOfTables = int(numberOfTables)
    except:
        await chan.send("ERROR: Number of tables must be a number")
        return
    
    player, chan, club = get_vars(ctx)
    
    if club.tourney_id == None:
        await chan.send("No tourney is currently running")
        return

    tourney = getTourney(club.tourney_id)
    users = getUsersForTourney(club.tourney_id)

    # We are starting the next round now!
    # startNextRound(club.tourney_id)
    standings = getStandings(club.tourney_id)
    standings = standings[:4*numberOfTables]

    startNextRound(club.tourney_id)
    
    print(standings)
    for pos in range(numberOfTables):
        players = []
        for player in standings[pos*4:pos*4+4]:
            p = getUserFromTenhouName(player[1])
            if p == None:
                await chan.send(f"Warning: player {player} is not registered")
                players.append(None)
            else:
                players.append(p.user_id)
        createTable(tourney.tourney_id, tourney.current_round, players[0], players[1], players[2], players[3])

    ret = "```"
    ret += printTables(tourney)
    ret += "```"

    await chan.send(ret)
    
def printTables(tourney):

    ret = f"\n\nRound: {tourney.current_round}\n"
    
    tables = getTablesForRoundTourney(tourney.tourney_id,tourney.current_round)

    count = 0
    
    for table in tables:

        count += 1        

        if table.pei == None:
            ret += f"\n===   Byes  ===\n"
        else:
            if table.finished:
                ret += f"\n=== Table {count} 🌟 Finished ===\n"
            else:
                ret += f"\n=== Table {count} ===\n"


        for uId in [table.ton, table.nan, table.xia, table.pei]:
            if uId != None:
                user = getUser(uId)
                if user == None:
                    print (f"ERROR: Could not find user {uId}")
                else:
                    ret += user.user_name
                    if user.tenhou_name != None:
                        ret += " "+user.tenhou_name
            ret += "\n"

    return ret
    
@bot.command()
async def setTenhouName(ctx, tenhouName):
    """
    Set your tenhou name!
    """
    player, chan, club = get_vars(ctx)
    ret = updateUserTenhouName(player.id, tenhouName)
    if ret < 0:
        await chan.send(f"Error: Please create an account first with $createAccount")
        return
    await chan.send("Updated tenhou name!")


@bot.command()
async def myInfo(ctx):
    """
    get info about you!
    """
    player, chan, club = get_vars(ctx)

    ret = "```"
    user = getUser(player.id)
    if user == None:
        await chan.send(getError())
        return
    await chan.send(f"Name: {user.user_name}\nTenhou: {user.tenhou_name}")
    
@bot.command()
async def info(ctx):
    """
    get info about rooms and bot
    """
    ret = "```"
    player, chan, club = get_vars(ctx)

    tourney = getTourney(club.tourney_id)

    if tourney != None:
        ret += f"Current Tourney: {tourney.tourney_name}\n\n"
    
    if not club.tenhou_room == None:
        ret += f"Tenhou: https://tenhou.net/0/?{club.tenhou_room[0:9]}\n\n"
        
    ret += "Add Chii-tan to your server: https://discord.com/api/oauth2/authorize?client_id=732219732547076126&permissions=268957760&scope=bot\n\n"
    ret += "Website: http://yakuhai.com\n\n"
    ret += "Source: https://github.com/jbmokuz/Paitan\n\n```"
    
    await chan.send(ret)


def formatScores(scores,tableRate):

    table = [["Score","","Pay","Name"]]

    for row in scores:

        name, score, shugi, payout = row
        
        score = str(score)
        shugi = str(shugi)
        payout = str(payout)
        if not "-" in shugi:
            shugi = "+"+shugi
        if not "-" in payout:
            payout = "+"+payout       
        table.append([str(score),str(shugi),str(payout),str(name)])

    colMax = [max([len(i) for i in c]) for c in zip(*table)]
    colMax[-1] = 0
    
    ret = f"```{tableRate}\n"
    for row in table:
        for i,col in enumerate(colMax):
            ret += row[i].ljust(col+1)
        ret += "\n"
    ret += "```"

    return ret


@bot.command()
async def score(ctx, log=None, rate="standard", shugi=None):
    """
    Score a tenhou log!
    Args:
        log:
            A full url or just the log id
        rate (optional):
            tensan(default), tengo, or tenpin
        shugi (optional):
            defaults to the rate shugi
    """
    player, chan, club = get_vars(ctx)

    if log == None or rate == None:
        await chan.send("usage: !score [tenhou_log] [rate]\nEx: !score https://tenhou.net/0/?log=2020051313gm-0209-19713-10df4ad2&tw=1 tengo")
        
    
    rate = rate.lower()
    tableRate = None

    # Pick the proper table rate
    
    if rate == "tensan" or rate == "0.3" or rate == ".3":
        tableRate = copy.deepcopy(TENSAN)
    elif rate == "tengo" or rate == "0.5" or rate == ".5":
        tableRate = copy.deepcopy(TENGO)
    elif rate == "tenpin" or rate == "1.0":
        tableRate = copy.deepcopy(TENPIN)
    elif rate == "standard":
        tableRate = copy.deepcopy(STANDARD)
    else:
        await chan.send(f"{rate} is not a valid rate (try !help score)")
        return

    if(shugi != None):
        try:
            tableRate.shugi = round(float(shugi),3)
        except:
            await chan.send(f"{shugi} is not a valid shugi")
            return


    # This gets the players and stuff
    players = parseTenhou(log)
    # This is part of a hack to keep seat order
    seatOrder = [i[0] for i in players]
    # Calculates the score and also the explination of how the score was calculated
    scores, explain = scorePayout(players, tableRate)
    # Gets the unique id for the log
    logId = getLogId(log)
    
    # @TODO this is really hacky
    scoresOrdered = []
    for i,p in enumerate(players):
        scoresOrdered.append([x for x in scores if x[0] == seatOrder[i]][0])

    # Add scores to db
    game = createTenhouGame(logId,scoresOrdered,tableRate.name)
    tourney = getTourney(club.tourney_id)

    
    if game == None:
        await chan.send("WARNING: Already scored that game! Will not be added!")
        await chan.send("Here are results anyways")
        
    else:
        # Do we currently have a tourney?
        if tourney != None:
            # Add the game to the tourney
            addGameToTourney(club.tourney_id, game.tenhou_game_id)
            tables = getTablesFromScore(tourney,[i[0] for i in players])
            if len(tables.keys()) > 1:
                await chan.send("WARNING: Players are not all at the same table!")
            else:
                finishTable([i for i in tables.keys()][0])

    print(explain)    
    await chan.send(formatScores(scores, tableRate))
    
    """
    for guild in bot.guilds:
        for log_chan in guild.text_channels:
            if str(log_chan) == "daily-log":
                print("found")
                await log_chan.send(log)
                await log_chan.send(ret)
    """

    
@bot.command()
async def start(ctx, p1=None, p2=None, p3=None, p4=None, randomSeat="true"):
    """
    Start Tenhou Game
    Args:
        player1 player2 player3 player4 randomSeating=[true/false]
    """

    player, chan, club = get_vars(ctx)
    
    if (p1 == None or p2 == None or p3 == None or p4 == None):
        await chan.send(f"Please specify 4 players space separated")
        return

    player_names = [p1,p2,p3,p4]

    print(f"Starting, Admin:{club.tenhou_room} Rules:{club.tenhou_rules}")
    
    data = {
        "L":club.tenhou_room,
        "R2":club.tenhou_rules,
        "RND":"default",
        "WG":"1"
        }
    
    if randomSeat.lower() != "false" and randomSeat.lower() != "no":
        random.shuffle(player_names)
        #data["RANDOMSTART"] = "on"
        
    data["M"] = "\r\n".join(player_names)

    resp = requests.post('https://tenhou.net/cs/edit/start.cgi',data=data)
    if resp.status_code != 200:
        await chan.send(f"http error {resp.status_code} :<")
        return
    await chan.send(urllib.parse.unquote(resp.text))

@bot.command()
@commands.has_permissions(administrator=True)
async def startTourney(ctx, *args):
    """
    Start a Tourney on the server!
    Args:
        Tournament_Name (max 128 chars)
    """
    player, chan, club = get_vars(ctx)

    if len(args) < 1:
        await chan.send("Please specify a tourney name!")
        return 
    
    if club.tourney_id != None:
        await chan.send("Already have a tournament started!")
        return        

    tourney = createTourney( " ".join(args))

    if updateClubTourney(club.club_id, tourney.tourney_id) == None:
        await chan.send(getError())
        return        
    
    if tourney == None:
        await chan.send("Already have a tournament by that name!")
        return

    await chan.send(f"Started Tourney '{getTourney(tourneyId).tourney_name}'")

    
@bot.command()
@commands.has_permissions(administrator=True)
async def endTourney(ctx):
    """
    End a Tourney on the server!
    """
    player, chan, club = get_vars(ctx)

    if  club.tourney_id == None:
        await chan.send("No tournament started!")
        return

    tmp = ""
    
    try:
        tmp = getTourney(club.tourney_id).tourney_name
    except:
        pass

    await chan.send("Final standings")

    await chan.send(formatStandings(getStandings(club.tourney_id)))
    
    # This really cant return -1 after calling get_vars?
    if updateClubTourney(club.club_id, None) == None:
        await chan.send("No club created yet!")
        return

    await chan.send(f"Ended Toruney '{tmp}'")


@bot.command(aliases=['standings',"scores"]))
async def rankings(ctx):
    """
    Get the standings of a current tourney!
    """
    player, chan, club = get_vars(ctx)    
    tourney = getTourney(club.tourney_id)

    if tourney == None:
        await chan.send(getError())
        return
    
    await chan.send(formatStandings(getStandings(club.tourney_id)))


def formatStandings(ordered):

    ret = "```"
    ret += " Score  |  Name\n"
    ret += "------------------\n"
    for score, name in ordered:
        score = str(score)
        if not "-" in score:
            score = " "+score
        score = score.ljust(7)

        # See if there is a user with this tenhou name
        check = getUserFromTenhouName(name)
        if check:
            ret += f"{str(score)} |  {name} ({check.user_name})\n"
        else:
            ret += f"{str(score)} |  {name}\n"
            
            
    ret += "```"

    return ret
            

    
def getStandings(tourneyId): 
    games = getGamesForTourney(tourneyId)

    rank = {}
    
    for g in games:
        if g.ton != None:
            if not g.ton in rank:
                rank[g.ton] = 0
            rank[g.ton] += g.ton_payout

        if g.nan != None:
            if not g.nan in rank:
                rank[g.nan] = 0
            rank[g.nan] += g.nan_payout

        if g.xia != None:
            if not g.xia in rank:
                rank[g.xia] = 0
            rank[g.xia] += g.xia_payout

        if g.pei != None:
            if not g.pei in rank:
                rank[g.pei] = 0
            rank[g.pei] += g.pei_payout


    ordered = []

    for n in rank:
        ordered.append([rank[n],n])
    ordered.sort(key=lambda x:x[0], reverse=True)

    return ordered
    
    
@bot.command(aliases=['p'])
async def ping(ctx):
    """
    Ping!
    """
    player, chan, club = get_vars(ctx)

    
    player = ctx.author
    chan = ctx.channel
    await chan.send(f"pong {chan.guild.id}")
        
@bot.event
async def on_ready():
    print("Time to Mahjong!")
    print("Logged in as: {}".format(bot.user.name))

@bot.event
async def on_error(event, *args, **kwargs):
    print("ERROR!")
    print("Error from:", event)
    print("Error context:", args, kwargs)

    from sys import exc_info

    exc_type, value, traceback = exc_info()
    print("Exception type:", exc_type)
    print("Exception value:", value)
    print("Exception traceback object:", traceback)

    
bot.run(TOKEN)
