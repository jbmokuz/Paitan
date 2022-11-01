import copy
import os
import time
import urllib

import requests
import sys
from discord.ext import commands
#import discord

from database import *
from parsers.parse import getLogId, intToYaku, parseTenhou, scorePayout, CARD
from parsers.parse import TENSAN, TENGO, TENPIN, STANDARD, BINGHOU

if len(sys.argv) > 1:
    TOKEN = os.environ["DISCORD_DEV_TOKEN"]
else:
    TOKEN = os.environ["DISCORD_BOT_TOKEN"]

bot = commands.Bot(command_prefix='$')

EMOJI_WARNING = "⚠️"
EMOJI_ERROR = "🚫"
EMOJI_OK = "👍"

async def get_vars(ctx):
    player = ctx.author
    chan = ctx.channel
    club = getClub(chan.guild.id)
    if club == None:
        createClub(chan.guild.id, chan.guild.name)
    club = getClub(chan.guild.id)
    if not getUser(player.id):
        await createSiteAccount(player, chan)
    return player, chan, club


# id=119046709983707136 name='moku' discriminator='9015'

@bot.command()
async def roll(ctx, dice=2):
    """
    roll dice
    """
    player, chan, club = await get_vars(ctx)
    rolls = []
    for i in range(dice):
        rolls.append(random.randint(1,6))
    await chan.send(f"{rolls}\n{sum(rolls)}")


#################

@bot.command()
async def change_pass(ctx):
    """
    Get a new password for your account
    """
    player, chan, club = await get_vars(ctx)

    passwd = changePassword(player.id)
    if passwd == None:
        await player.send(getError())
        return

    username = player.name + "#" + player.discriminator
    await player.send(f"Username: {username} Pass: {passwd}")


# @bot.command()
# async def createAccount(ctx):
#    """
#    Create an account for this guild
#    """
#    player, chan, club = await get_vars(ctx)
#    await createSiteAccount(player, chan)


async def createSiteAccount(player, chan):
    username = player.name + "#" + player.discriminator

    # This is the only time we have the password for a user
    # The password hash is stored
    passwd = createUser(player.id, username)
    if passwd == None:
        await player.send(getError())
        return
    else:
        ret = f"Username: {username} Pass: {passwd}"
        await player.send(ret)

    # Can they manage this chan?
    if player.guild_permissions.administrator:
        ret = addUserToClubManage(chan.guild.id, player.id)
        if ret != None:
            await player.send(f"Now managing {chan.guild.name}")
        else:
            await player.send(getError())

    # Add user to chan
    ret = addUserToClub(chan.guild.id, player.id)
    if ret != None:
        await player.send(f"You are now a member of {chan.guild.name} \n Manage account @ https://yakuhai.com")
    else:
        await player.send(getError())


@bot.command()
async def join(ctx):
    """
    Join current tourney
    """
    player, chan, club = await get_vars(ctx)
    ret = addUserToTourney(club.tourney_id, player.id)

    if str(player.id) == "225048943350775808":
        await chan.send("A Desperate Woman has joined...")
    
    if ret == None:
        await chan.send(getError())
        return

    await chan.send("Added! That makes "+str(len(getUsersForTourney(club.tourney_id))))

@bot.command()
async def leave(ctx):
    """
    Join current tourney
    """
    player, chan, club = await get_vars(ctx)
    ret = removeUserFromTourney(club.tourney_id, player.id)
    
    if str(player.id) == "225048943350775808":
        await chan.send("It is safe to play mahjong again!")
    
    if ret == None:
        await chan.send(getError())
        return
    await chan.send("Removed! That makes "+str(len(getUsersForTourney(club.tourney_id))))

@bot.command()
async def kick(ctx, userName):
    """
    kick a player from a tourney
    """
    player, chan, club = await get_vars(ctx)
        
    user = getUserFromUserName(userName)
    if user == None:
        await chan.send("Chii-tan is confused... :<")
        return

    ret = removeUserFromTourney(club.tourney_id, user.user_id)
    if ret == None:
        await chan.send(getError())
        return
    await chan.send("Removed "+userName)


    
@bot.command()
async def list(ctx):
    """
    Join current tourney
    """
    player, chan, club = await get_vars(ctx)
    if club.tourney_id == None:
        await chan.send("No tourney is currently running")
        return

    ret = requests.post("https://tenhou.net/cs/edit/cmd_get_players.cgi",data = {"L":club.tenhou_room})

    if ret.status_code != 200:
        await chan.send("Could not get list :<")

    ret = ret.text
    idle = urllib.parse.unquote(ret.split("&")[0][5:]).split(",")
    play = urllib.parse.unquote(ret.split("&")[1][5:]).split(",")
        
    print(idle, play)
    

    tourney = getTourney(club.tourney_id)

    ret = "```In Queue:\n\n"
    # Havent shuffled for tables yet
    if 1==1: #tourney.current_round == 0:
        users = getUsersForTourney(club.tourney_id)
        if users == []:
            await chan.send("No users have joined")
            return
        for u in users:
            ret += u.user_name
            if u.tenhou_name != None:
                ret += " (" + u.tenhou_name + ")"
            ret += "\n"

    else:
        pass
    
    #if tourney.current_round != 0:
    #    ret += "```\n\n```TABLES:"
    #    ret += printTables(tourney)

    ret += "```"
    await chan.send(ret)



#@commands.has_permissions(administrator=True)
@bot.command()
async def shuffle(ctx):
    """
    Shuffle for list for tables
    """
    player, chan, club = await get_vars(ctx)

    if club.tourney_id == None:
        await chan.send("No tourney is currently running")
        return

    tourney = getTourney(club.tourney_id)
    users = getUsersForTourney(club.tourney_id)

    # We are starting the next round now!
    startNextRound(club.tourney_id)

    ret = "```"

    tables = getTablesForRoundTourney(tourney.tourney_id, tourney.current_round - 1)
    
    # First round is just random
    if 1==1: #tourney.current_round == 1 or tables == [] or len(users) < len(tables):

        random.shuffle(users)
        tables = [[u.user_id for u in users[i:i + 4]] for i in range(0, len(users), 4)]


    # We want to ensure no one plays anyone they played the first round
    # Need at least 16 people, but should still get you the least overlap?
    else:

        byes = []

        print(tables)
        userIds = [u.user_id for u in users]
        
        # This is a bye table as there is not 4 players
        # @NOTE always assuming 4 player mahjong for now
        if tables[-1].pei == None:
            byes = tables[-1]
            byes = [byes.ton, byes.nan, byes.xia, byes.pei]
            tables = tables[:-1]

        # remove people not in the list
        for userId in byes:
            if not userId in userIds:
                byes.remove(userId)

        tables = [[i.ton, i.nan, i.xia, i.pei] for i in tables]
        flatTables = [a for l in tables for a in l]
        random.shuffle(flatTables)

        """
        def replaceLeavers(newUserId):
            for table in tables:
                for uid in tables:
                    if not uid in userIds:
                        table[table.get(uid)] = newUserId
                        return True
            return False

        [a,b,c,d][e,f,g,h][i]

        [a,c,d,e,f,g,h]
        [i,j,k,l,m,n]
        """
        
        # Shuffle the order of all the tables 
        random.shuffle(tables)

        # Shuffle all the tables players orders
        for t in tables:
            random.shuffle(t)

        # Make it so the tables have no repeating players
        for off in range(1, 4):
            tmp = [[] for i in tables]
            for i, t in enumerate(tables):
                tmp[i] += tables[i][:off]
                tmp[i] += tables[(i + 1) % len(tables)][off:]
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


# @bot.command()
# @commands.has_permissions(administrator=True)
async def topCut(ctx, numberOfTables):
    """
    Cut the top number of tables
    """
    player, chan, club = await get_vars(ctx)

    try:
        numberOfTables = int(numberOfTables)
    except:
        await chan.send("ERROR: Number of tables must be a number")
        return

    player, chan, club = await get_vars(ctx)

    if club.tourney_id == None:
        await chan.send("No tourney is currently running")
        return

    tourney = getTourney(club.tourney_id)
    users = getUsersForTourney(club.tourney_id)

    # We are starting the next round now!
    # startNextRound(club.tourney_id)
    standings = getStandings(club.tourney_id)
    standings = standings[:4 * numberOfTables]

    if len(standings) == 0:
        await chan.send("No scores are in to do a top cut")
        return

    startNextRound(club.tourney_id)

    print(standings)
    for pos in range(numberOfTables):
        players = []
        for player in standings[pos * 4:pos * 4 + 4]:
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

    tables = getTablesForRoundTourney(tourney.tourney_id, tourney.current_round)

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
                    print(f"ERROR: Could not find user {uId}")
                else:
                    ret += user.user_name
                    if user.tenhou_name != None:
                        ret += " " + user.tenhou_name
            ret += "\n"

    return ret


@bot.command()
async def set_name(ctx, tenhouName):
    """
    Set your tenhou name!
    """
    player, chan, club = await get_vars(ctx)

    ret = updateUserTenhouName(player.id, tenhouName)
    if ret == None:
        await chan.send(getError())
        return

    await chan.send(f"Updated tenhou name to {tenhouName}!")


@bot.command()
async def my_info(ctx):
    """
    get info about you!
    """
    player, chan, club = await get_vars(ctx)

    ret = "```"
    user = getUser(player.id)
    if user == None:
        await chan.send(getError())
        return
    await chan.send(f"Name: {user.user_name}\nTenhou: {user.tenhou_name}\nJade: {user.jade}")


@bot.command()
async def info(ctx):
    """
    get info about rooms and bot
    """
    ret = "```"
    player, chan, club = await get_vars(ctx)

    tourney = getTourney(club.tourney_id)

    if tourney != None:
        ret += f"Current Tourney: {tourney.tourney_name} {tourney.tourney_id} Round: {tourney.current_round}\n\n"

    if not club.tenhou_room == None:
        ret += f"Tenhou: https://tenhou.net/0/?{club.tenhou_room[0:9]}\n\n"

    ret += "Add Chii-tan to your server: https://discord.com/api/oauth2/authorize?client_id=732219732547076126&permissions=268957760&scope=bot\n\n"
    ret += "Website: http://yakuhai.com\n\n"
    ret += "Source: https://github.com/jbmokuz/Paitan\n\n```"

    await chan.send(ret)


def formatScores(players, tableRate):
    #table = [["Score", "", "Pay", "Name"]]
    table = [["Score", "   ", "Pay", "Name"]]    

    for row in players:
        score = str(row.score)
        shugi = str(row.shugi)
        #shugi = str(row.kans)
        payout = str(row.payout)
        #payout = ", ".join(intToYaku(row.binghou))
        #payout = str(row.score//100 - 300)
        
        #if int(payout) < 0:
        #    payout = str(0)
        if not "-" in shugi:
            shugi = "+" + shugi
        if not "-" in payout:
            payout = "+" + payout

        table.append([str(score), str(shugi), '{0:.2f}'.format(float(payout)), str(row.name)])

    colMax = [max([len(i) for i in c]) for c in zip(*table)]
    colMax[-1] = 0

    ret = f"```{tableRate}\n"
    for row in table:
        for i, col in enumerate(colMax):
            ret += row[i].ljust(col + 1)
        ret += "\n"
    ret += "```"

    return ret


@bot.command()
async def score(ctx, log=None, rate=None, shugi=None):
    """
    Score a tenhou log!
    Args:
        log:
            A full url or just the log id
        rate (optional):
            standard(default), tensan, tengo, tenpin, or binghou
        shugi (optional):
            defaults to the rate shugi
    """
    player, chan, club = await get_vars(ctx)

    if rate == None:
        rate = club.tenhou_rate

    if log == None or rate == None:
        await ctx.message.add_reaction(EMOJI_ERROR)
        message = "usage: $score [tenhou_log] [rate]\nEx: $score https://tenhou.net/0/?log=2020051313gm-0209-19713-10df4ad2&tw=1 tengo"
        if rate == None:
            message = "No default rate set\n" + message
        await chan.send(message)
        return

    if rate != None:
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
    elif rate == "binghou":
        tableRate = copy.deepcopy(BINGHOU)
    else:
        await ctx.message.add_reaction(EMOJI_ERROR)
        await chan.send(f"{rate} is not a valid rate (try $help score)")
        return

    if (shugi != None):
        try:
            tableRate.shugi = round(float(shugi), 3)
        except:
            await ctx.message.add_reaction(EMOJI_ERROR)
            await chan.send(f"{shugi} is not a valid shugi")
            return

    # This gets the players and stuff
    players = parseTenhou(log)

    if players == None:
        await ctx.message.add_reaction(EMOJI_ERROR)
        await chan.send(getError())
        return

    # This is part of a hack to keep seat order
    seatOrder = [i.name for i in players]
    # Calculates the score and also the explination of how the score was calculated
    scores, explain = scorePayout(players, tableRate)
    # Gets the unique id for the log
    logId = getLogId(log)

    # @TODO this is really hacky
    scoresOrdered = []
    for i, p in enumerate(players):
        scoresOrdered.append([x for x in scores if x.name == seatOrder[i]][0])

    # Add scores to db
    if club.tourney_id != None:
        tourney = getTourney(club.tourney_id)
        game = createTenhouGame(logId, scoresOrdered, tableRate.name, tourney.current_round)
    else:
        for p in scoresOrdered:
            p.binghou = p.binghou & (1 << CARD.index("Kan!"))
        game = createTenhouGame(logId, scoresOrdered, tableRate.name)
        
    if game == None:
        # await chan.send(getError())
        await ctx.message.add_reaction(EMOJI_WARNING)
        await chan.send("WARNING: Already scored that game! Will not be added\nHere are results anyways")
    else:                        
        ret = addGameToClub(club.club_id, game.tenhou_game_id)        
        if club.tourney_id != None:
            addGameToTourney(club.tourney_id, game.tenhou_game_id)
        if ret == None:
            await ctx.message.add_reaction(EMOJI_ERROR)
            await chan.send(getError())
            return

    scoreRet = ""
        
    # Add jade for kans
    if rate == "binghou":
        for row in scores:
            test = getUserFromTenhouName(row.name)
            if test:
                updateJade = row.score//100 - 300
                if updateJade > 0:
                    updateUserJade(test.user_id, test.jade + updateJade)
            #scoreRet += row.name + " Jade: " +str(row.score//100 - 350 + row.kans*100)+ ": Kans " + str(row.kans) + " Yaku: " + ", ".join(intToYaku(row.binghou))
            #scoreRet += formatScores(scores, tableRate)
            #scoreRet += "\n"                                    
    #else:
    scoreRet += formatScores(scores, tableRate)

        
    # print(explain)
    # if
    # await chan.send(formatScores(scores, tableRate))

    await ctx.message.add_reaction(EMOJI_OK)
    await chan.send(scoreRet)

    """
    for guild in bot.guilds:
        for log_chan in guild.text_channels:
            if str(log_chan) == "daily-log":
                print("found")
                await log_chan.send(log)
                await log_chan.send(ret)
    """


@bot.command()
async def start(ctx, p1=None, p2=None, p3=None, p4=None, tableName="general", randomSeat="true"):
    """
    Start Tenhou Game
    Args:
        player1 player2 player3 player4 randomSeating=[true/false]
    """

    player, chan, club = await get_vars(ctx)

    player_names = []
    
    if (p1 == None or p2 == None or p3 == None or p4 == None):
        if club.tourney_id != None:
            
            user = getUser(player.id)
            tourney = getTourney(club.tourney_id)
            tables = getTablesForRoundTourney(tourney.tourney_id, tourney.current_round)
            
            count = 0
            # If we have started... lets get the players table!
            if tourney.current_round != 0:
                for table in tables:
                    count += 1
                    currentTable = [table.ton, table.nan, table.xia, table.pei]
                    if user.user_id in currentTable:
                        tableName = f"table{count}"
                        for uid in currentTable:
                            u = getUser(uid)
                            print(u)
                            if u == None:
                                await chan.send(f"ERROR: Could not find user {uid}\nI think you have a bye")
                                #await chan.send(getError())
                                return
                            if u.tenhou_name == None:
                                await chan.send(f"No tenhou name for user {u.user_name}")
                            else:
                                print("COW")
                                player_names.append(u.tenhou_name)
    else:
        player_names = [p1, p2, p3, p4]

    print(player_names)
    print(tableName)
    
    if len(player_names) < 4:
        await chan.send(f"Please specify 4 players space separated")
        return


    users = [getUserFromTenhouName(u) for u in player_names]
    for u in users:
        if u:
            updateUserTable(u.user_id, tableName)

    
    print(f"Starting, Admin:{club.tenhou_room} Rules:{club.tenhou_rules}")

    rules = []

    rulez = int(club.tenhou_rules,16)
    
    if rulez % 2:
        rules.append("Aka Ari")
    else:
        rules.append("Aka Nashi")

    if rulez % 4:
        rules.append("Kuitan Ari")
    else:
        rule.append("Kuitan Nashi")

    if rulez % 8:
        rules.append("Hanchan")
    else:
        rules.append("Tonpu")

    if rulez & 0x200 or rulez & 0x400:
        rules.append("Shugi Ari")
    else:
        rules.append("Shugi Nashi")
            
    await chan.send("```Starting: " + " | ".join(rules)+"```")
        
    data = {
        "L": club.tenhou_room,
        "R2": club.tenhou_rules,
        "RND": "default",
        "WG": "1"
    }

    if randomSeat.lower() != "false" and randomSeat.lower() != "no":
        random.shuffle(player_names)
        # data["RANDOMSTART"] = "on"

    data["M"] = "\r\n".join(player_names)

    print("sending")
    resp = requests.post('https://tenhou.net/cs/edit/cmd_start.cgi', data=data)
    print(resp)
    if resp.status_code != 200:
        await chan.send(f"http error {resp.status_code} :<")
        return

    await chan.send(urllib.parse.unquote(resp.text))




#@commands.has_permissions(administrator=True)
@bot.command()
async def start_tourney(ctx, *args):
    """
    Start a Tourney on the server!
    Args:
        Tournament_Name (max 128 chars)
    """
    player, chan, club = await get_vars(ctx)

    if len(args) < 1:
        await chan.send("Please specify a tourney name!")
        return

    if club.tourney_id != None:
        await chan.send("Already have a tournament started!")
        return

    tourney = createTourney(" ".join(args), club.tenhou_rate)
    if tourney == None:
        await chan.send(getError())
        return

    
    if updateClubTourney(club.club_id, tourney.tourney_id) == None:
        await chan.send(getError())
        return

    if tourney == None:
        await chan.send("Already have a tournament by that name!")
        return

    await chan.send(f"Started Tourney '{getTourney(club.tourney_id).tourney_name}'")



#@commands.has_permissions(administrator=True)
@bot.command()
async def end_tourney(ctx):
    """
    End a Tourney on the server!
    """
    player, chan, club = await get_vars(ctx)

    if club.tourney_id == None:
        await chan.send("No tournament started!")
        return

    tmp = ""

    try:
        tmp = getTourney(club.tourney_id).tourney_name
    except:
        pass

    # await chan.send("Tourney Ended!")
    # await chan.send(formatStandings(getStandings(club.tourney_id)))

    # This really cant return -1 after calling get_vars?
    if updateClubTourney(club.club_id, None) == None:
        await chan.send("No club created yet!")
        return

    await chan.send(f"Ended Toruney '{tmp}'")


@bot.command()
@commands.has_permissions(administrator=True)
async def next_round(ctx):
    """
    Go to next round for tourney
    """
    player, chan, club = await get_vars(ctx)

    if club.tourney_id == None:
        await chan.send("No tourney is currently running")
        return

    tourney = getTourney(club.tourney_id)
    users = getUsersForTourney(club.tourney_id)

    # We are starting the next round now!
    ret = startNextRound(club.tourney_id)

    await chan.send(f"Starting Round {ret}")


@bot.command(aliases=['standings',"scores"])
async def rankings(ctx):
    """
    Get the standings of a current tourney!
    """
    player, chan, club = await get_vars(ctx)
    tourney = getTourney(club.tourney_id)
    
    if tourney == None:
        await chan.send(getError())
        return

    await chan.send(formatStandings(getStandings(club.tourney_id,False)))


def formatStandings(ordered):

    ret = "```"
    ret += " Score  |  Name\n"
    ret += "------------------\n"
    for score, name in ordered:
        score = str(round(score,2))
        if not "-" in score:
            score = " " + score
        score = score.ljust(7)

        # See if there is a user with this tenhou name
        check = getUserFromTenhouName(name)
        if check:
            ret += f"{str(score)} |  {name} ({check.user_name})\n"
        else:
            ret += f"{str(score)} |  {name}\n"

    ret += "```"

    return ret


"""
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
"""


@bot.command(aliases=['p'])
async def ping(ctx):
    """
    Ping!
    """
    player, chan, club = await get_vars(ctx)

    player = ctx.author
    chan = ctx.channel

    print("Chan id", str(chan.id))
    await chan.send(f"pong")


@bot.command()
async def role(ctx, newRole=None):
    """
    Add or remove a role (will remove if you already have the role)!
    Args:
        role: the role you want to be added to or removed from
    """
    
    player, chan, gi =  await get_vars(ctx)
    validRoles = ["san","pin","go"]

    newRole = newRole.lower()

    if newRole == None or not newRole in validRoles:
        await chan.send("Usage: role <role>\nTry san, pin, or go")
        return 

    newRole = newRole[0].upper() + newRole[1:]
    
    roles = await chan.guild.fetch_roles()
    if not newRole in [i.name for i in roles]:
        await chan.guild.create_role(name=newRole)

    removed = False
    for r in player.roles:
        if r.guild == chan.guild:
            if r.name == newRole:
                role = discord.utils.get(chan.guild.roles, name=newRole)
                await player.remove_roles(role)
                await chan.send(f"Removed from {newRole}")
                removed = True

    if (removed):
        return
                
    role = discord.utils.get(chan.guild.roles, name=newRole)
    await player.add_roles(role)
    await chan.send(f"Added to {newRole}")

    
"""
@bot.command()
async def role(ctx, role):

    
    player, chan, gi =  await get_vars(ctx)
    roles = await chan.guild.fetch_roles()

    ROLES = ["san","go","pin"]

    role = role.lower()
    
    if not role in ROLES:
        await chan.send(f"{role} is not a role!\nValid roles {ROLES}")
        return 

    role = role[0].upper() + role[1:]
                        
    if not role in [i.name for i in roles]:
        await chan.guild.create_role(name=role)

    role = discord.utils.get(chan.guild.roles, name=role)
    await player.add_roles(role)
    await chan.send("Added")
"""

"""
@bot.command()
async def role(ctx):
    player, chan, gi =  await get_vars(ctx)
    roles = await chan.guild.fetch_roles()
    if not "Ping for Games" in [i.name for i in roles]:
        await chan.guild.create_role(name="Ping for Games")

    role = discord.utils.get(chan.guild.roles, name="Ping for Games")
    await player.add_roles(role)
    await chan.send("Added")
"""
    
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

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    
    
bot.run(TOKEN)
