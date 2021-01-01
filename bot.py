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
    gi = getClub(chan.guild.id)
    if gi == None:
        createClub(chan.guild.id,chan.guild.name)
    gi = getClub(chan.guild.id)
    return player,chan, gi

#id=119046709983707136 name='moku' discriminator='9015'
@bot.command()
async def createAccount(ctx):
    """
    Create an account for this guild
    """
    player, chan, gi = get_vars(ctx)
    username = player.name+"#"+player.discriminator
    passwd = createUser(player.id,username)
    if type(passwd) == type(0):
        passwd = changePassword(player.id)
        await player.send(f"Password changed to: {passwd}")
    else:
        ret = f"Username:{username} Pass:{passwd}"
        await player.send(ret)

    # Can they manage this chan?
    if player.guild_permissions.administrator:
        ret = addUserToClubManage(chan.guild.id,player.id)
        if ret == 0:
            await player.send(f"Now managing {chan.guild.name}")
        else:
            print(f"ERR: {ret}")

    # Add user to chan
    ret = addUserToClub(chan.guild.id,player.id)
    if ret == 0:
        await player.send(f"You are now a member of {chan.guild.name}")
    else:
        print(f"ERR: {ret}")

    await player.send("Manage account @ http://yakuhai.com (Currently only for guild admins)")


@bot.command()
async def join(ctx):
    """
    Join current tourney
    """
    player, chan, gi = get_vars(ctx)
    ret = addUserToTourney(gi.tourney_id,player.id)
    if ret == -1:
        await chan.send("Please register with $createAccount")
        return
    if ret == -2:
        await chan.send("No tourney is currently running")
        return
    if ret == -3:
        await chan.send("You have already joined")
        return
    await chan.send("Added!")

@bot.command()
async def leave(ctx):
    """
    Join current tourney
    """
    player, chan, gi = get_vars(ctx)
    ret = removeUserFromTourney(gi.tourney_id,player.id)
    if ret == -1:
        await chan.send("You are not part of the tourney")
        return
    await chan.send("Removed")
    
@bot.command()
async def list(ctx):
    """
    Join current tourney
    """
    player, chan, gi = get_vars(ctx)
    if gi.tourney_id == None:
        await chan.send("No tourney is currently running")
        return

    tourney = getTourney(gi.tourney_id)

    ret = "```"

    if tourney.current_round == 1:    
        users = getUsersForTourney(gi.tourney_id)
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
    player, chan, gi = get_vars(ctx)
    
    if gi.tourney_id == None:
        await chan.send("No tourney is currently running")
        return

    tourney = getTourney(gi.tourney_id)
    users = getUsersForTourney(gi.tourney_id)

    ret = "```"

    # First round is just random
    if tourney.current_round == 1:

        #random.shuffle(users)        
        tables = [[u.user_id for u in users[i:i+4]] for i in range(0,len(users),4)]

        
    # We want to ensure no one plays anyone they played the first round
    # Need at least 16 people, but should still get you the least overlap?
    else:
        
        tables = getTablesForRoundTourney(tourney.tourney_id,tourney.current_round-1)
        
        byes = []
        
        if tables[-1].pei == None:
            byes = tables[-1]
            byes = [byes.ton, byes.nan, byes.xia, byes.pei]
            tables = tables[:-1]

        tables = [[i.ton, i.nan, i.xia, i.pei] for i in tables]

        random.shuffle(tables)
        
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

    print("COW",tables)
        
    for t in tables:
        if len(t) < 4:
            t += [None for i in range(4 - len(t))]
        createTable(tourney.tourney_id, tourney.current_round, t[0], t[1], t[2], t[3])


    
    # Now we print the stuff out

    startNextRound(gi.tourney_id)
    
    ret += printTables(tourney)
    ret += "```"


    await chan.send(ret)


def printTables(tourney):

    count = 1

    ret = ""

    ret += f"\n\nRound: {tourney.current_round-1}\n"
    
    tables = getTablesForRoundTourney(tourney.tourney_id,tourney.current_round-1)

    count += 1
    
    for table in tables:

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
                if user == None and type(user) == type(int):
                    print (f"Error getting user {uId} {user}")
                ret += user.user_name
                if user.tenhou_name != None:
                    ret += " "+user.tenhou_name
            ret += "\n"

    print(ret)

    return ret
    
@bot.command()
async def setTenhouName(ctx, tenhouName):
    """
    Set your tenhou name!
    """
    player, chan, gi = get_vars(ctx)
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
    player, chan, gi = get_vars(ctx)

    ret = "```"
    user = getUser(player.id)
    if user == None:
        await chan.send("Please register with $createAccount")
        return
    await chan.send(f"Name: {user.user_name}\nTenhou: {user.tenhou_name}")
    
@bot.command()
async def info(ctx):
    """
    get info about rooms and bot
    """
    ret = "```"
    player, chan, gi = get_vars(ctx)

    test = getTourney(gi.tourney_id)

    if test != None and type(test) != type(1):
        ret += f"Current Tourney: {test.tourney_name}\n\n"
    
    if not gi.tenhou_room == None:
        ret += f"Tenhou: https://tenhou.net/0/?{gi.tenhou_room[0:9]}\n\n"
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
    player, chan, gi = get_vars(ctx)

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
    gameId = createTenhouGame(logId,scoresOrdered,tableRate.name)
    if gameId == -1:
        await chan.send("WARNING: Already scored that game! Will not be added!")
        await chan.send("Here are results anyways")
    else:
        tourney = getTourney(gi.tourney_id)

        # Do we currently have a tourney?
        if tourney != None and type(tourney) != type(1):
            # Add the game to the tourney
            addGameToTourney(gi.tourney_id, gameId)

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

    player, chan, gi = get_vars(ctx)
    
    if (p1 == None or p2 == None or p3 == None or p4 == None):
        await chan.send(f"Please specify 4 players space separated")
        return

    player_names = [p1,p2,p3,p4]

    print(f"Starting, Admin:{gi.tenhou_room} Rules:{gi.tenhou_rules}")
    
    data = {
        "L":gi.tenhou_room,
        "R2":gi.tenhou_rules,
        "RND":"default",
        "WG":"1"
        }
    
    if randomSeat.lower() != "false" and randomSeat.lower() != "no":
        random.shuffle(player_names)
        #data["RANDOMSTART"] = "on"
        
    data["M"] = "\r\n".join(player_names)

    #import pdb
    #pdb.set_trace()
    
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
    player, chan, gi = get_vars(ctx)

    if len(args) < 1:
        await chan.send("Please specify a tourney name!")
        return 
    
    if gi.tourney_id != None:
        await chan.send("Already have a tournament started!")
        return        

    tourneyId = createTourney( " ".join(args))

    if updateClubTourney(gi.club_id, tourneyId) == -1:
        await chan.send("No club created yet!")
        return        
    
    if tourneyId < 0:
        await chan.send("Already have a tournament by that name!")
        return

    await chan.send(f"Started Tourney '{getTourney(tourneyId).tourney_name}'")

    
@bot.command()
@commands.has_permissions(administrator=True)
async def endTourney(ctx):
    """
    End a Tourney on the server!
    """
    player, chan, gi = get_vars(ctx)

    if  gi.tourney_id == None:
        await chan.send("No tournament started!")
        return

    tmp = ""
    
    try:
        tmp = getTourney(gi.tourney_id).tourney_name
    except:
        pass


    await chan.send("Final standings")

    await chan.send(getStandings(gi.tourney_id))    
    
    
    # This really cant return -1 after calling get_vars?
    if updateClubTourney(gi.club_id, None) == -1:
        await chan.send("No club created yet!")
        return

    await chan.send(f"Ended Toruney '{tmp}'")

@bot.command()
async def standings(ctx):
    """
    Get the standings of a current tourney!
    """
    player, chan, gi = get_vars(ctx)    
    test = getTourney(gi.tourney_id)

    if test == None and type(test) == type(1):
        await chan.send("There is currently no Tourney running!")
        return
    
    await chan.send(getStandings(gi.tourney_id))

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
            
    
@bot.command(aliases=['p'])
async def ping(ctx):
    """
    Ping!
    """
    player, chan, gi = get_vars(ctx)

    
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
