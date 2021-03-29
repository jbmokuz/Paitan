import copy
import os
import time
import urllib

import requests
import sys
from discord.ext import commands

from database import *
from parsers.parse import getLogId, intToYaku, parseTenhou, scorePayout, CARD
from parsers.parse import TENSAN, TENGO, TENPIN, STANDARD, BINGHOU

if len(sys.argv) > 1:
    TOKEN = os.environ["DISCORD_DEV_TOKEN"]
else:
    TOKEN = os.environ["CHIITAN_TOKEN"]

bot = commands.Bot("$")

ROULETTE = []

EMOJI_WARNING = "⚠️"
EMOJI_ERROR = "🚫"
EMOJI_OK = "👍"

FILE_PATH = "./app/static/chars"
import glob

BAMBOO = []
SAKURA = []
DEFAULT = []
PROMO = []

for n in glob.glob(f"{FILE_PATH}/bamboo/*"):
    test = n.split("/")[-1].split("-")[0]
    if not test in BAMBOO:
        BAMBOO.append(test)

for n in glob.glob(f"{FILE_PATH}/sakura/*"):
    test = n.split("/")[-1].split("-")[0]
    if not test in SAKURA:
        SAKURA.append(test)

for n in glob.glob(f"{FILE_PATH}/default/*"):
    test = n.split("/")[-1].split("-")[0]
    if not test in DEFAULT:
        DEFAULT.append(test)

for n in glob.glob(f"{FILE_PATH}/sakura/*"):
    test = n.split("/")[-1].split("-")[0]
    if not test in PROMO:
        PROMO.append(test)


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

## ROULETTE ##

def show_roulette():
    global ROULETTE
    ret = ""
    for i in ROULETTE:
        if i < 2:
            ret += "🀫"
        if i == 2:
            ret += "🀆"
        if i == 3:
            ret += "🀂"
        ret += " "
    return ret


# @bot.command()
# async def roll(ctx, dice=2):
#    """
#    roll dice
#    """
#    player, chan, club = await get_vars(ctx)
#    rolls = []
#    for i in range(dice):
#        rolls.append(random.randint(1,6))
#    await chan.send(f"{rolls}\n{sum(rolls)}")


@bot.command()
@commands.has_permissions(administrator=True)
async def load_and_spin(ctx):
    global ROULETTE
    player, chan, club = await get_vars(ctx)
    ROULETTE = [0, 0, 0, 0, 0, 1]
    random.shuffle(ROULETTE)
    await chan.send(show_roulette())


@bot.command()
@commands.has_permissions(administrator=True)
async def pull_tile(ctx):
    global ROULETTE
    player, chan, club = await get_vars(ctx)
    pos = len([i for i in ROULETTE if i < 2]) - 1
    if ROULETTE[pos] == 1:
        await chan.send("BANG!")
        time.sleep(2)
        await chan.send("YOU")
        await chan.send("HAVE")
        await chan.send("BEEN")
        await chan.send("XIAT!")
    else:
        await chan.send("bang?")
        time.sleep(2)
        await chan.send("It was a blank")
    ROULETTE[pos] += 2
    await chan.send(show_roulette())


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
async def gocha_pick(ctx, name=None):
    """
    Pick your free starting character!  (cost free)
    Args:
        name: Either wanjirou or ichihime
    """
    global DEFAULT
    player, chan, club = await get_vars(ctx)

    print(name)
    if not (name in DEFAULT):
        await chan.send("Must pick either wanjirou or ichihime")
        return

    user = getUser(player.id)
    if user == None:
        await chan.send(getError())
        return

    for char in DEFAULT:
        if char in user.chars:
            await chan.send("You already have a default char!")
            return

    os.popen(f"python3 emote_client.py gocha {name} 1 BOT").read()
    updateUserJade(player.id, user.jade, name, None)
    await chan.send(f"You got {name}!")

@bot.command()
async def gocha_roll(ctx, type=None):
    """
    Roll the gacha! (cost 200 jade)
    Args:
        type: Either bamboo or sakura!
    """
    global SAKURA
    global BAMBOO
    player, chan, club = await get_vars(ctx)

    print(type)
    if not (type == "bamboo" or type == "sakura"):
        await chan.send("Must pick either bamboo or sakura")
        return

    user = getUser(player.id)
    if user == None:
        await chan.send(getError())
        return

    newChar = ""
    if user.jade >= 200:
        if type == "bamboo":
            newChar = random.choice(BAMBOO)
        if type == "sakura":
            newChar = random.choice(SAKURA)
    else:
        await chan.send(f"You only have {user.jade} jade!")
        return
    await chan.send("Rolling...")
    if random.randint(0,1) == 0 and len(user.chars.split(",")) > 2:
        await chan.send(f"Outch, you got a green item... RIP")
        updateUserJade(player.id, user.jade - 200, None, None)
        return
    os.popen(f"python3 emote_client.py gocha {newChar} 1 BOT").read()
    if newChar in user.chars:
        await chan.send(f"You got {newChar}! I hope that was not a duplicate... RIP")
    else:
        await chan.send(f"You got {newChar}!")
    updateUserJade(player.id, user.jade - 200, newChar, None)


@bot.command()
async def gocha_bond(ctx, name=None):
    """
    Get all the outfits for a char! (cost 300 jade)
    Args:
        name: Name (WARNING: mahjong soul+ don't have a bond (Washizu does though)!)
    """
    global SAKURA
    global BAMBOO
    global DEFAULT
    global PROMO
    player, chan, club = await get_vars(ctx)

    if not (name in SAKURA or name in BAMBOO or name in DEFAULT or name in PROMO):
        await chan.send("Not a real char!")
        return

    user = getUser(player.id)
    if user.jade >= 300:
        updateUserJade(player.id, user.jade - 300, None, name)
    else:
        await chan.send(f"You only have {user.jade} jade!")
        return
    if not name in user.chars:
        await chan.send(f"You got the new outfits and stuff for {name}! Sadly you don't own this char, what a shame!")
    else:
        await chan.send(f"You got the new outfits and stuff for {name}!")

@bot.command()
async def set_table(ctx, table="general"):
    """
    Set the table you are emoting at!
    Args:
        chan_name: Name of the chan (Ex:table1)!
    """
    player, chan, club = await get_vars(ctx)
    ret = updateUserTable(player.id, table)
    if ret == None:
        await chan.send(getError())
        return
    await chan.send(f"Updated to table {table}")


# @bot.command()
async def join(ctx):
    """
    Join current tourney
    """
    player, chan, club = await get_vars(ctx)
    ret = addUserToTourney(club.tourney_id, player.id)

    if ret == None:
        await chan.send(getError())
        return

    await chan.send("Added!")

# @bot.command()
async def leave(ctx):
    """
    Join current tourney
    """
    player, chan, club = await get_vars(ctx)
    ret = removeUserFromTourney(club.tourney_id, player.id)
    if ret == None:
        await chan.send(getError())
        return
    await chan.send("Removed")

# @bot.command()
async def kick(ctx, userName):
    """
    kick a player from a tourney
    """
    player, chan, club = await get_vars(ctx)

    user = getUserFromUserName(userName)
    if user == None:
        await chan.send("Could not find user by that name")

    ret = removeUserFromTourney(club.tourney_id, player.id)
    if ret == None:
        await chan.send(getError())
        return
    await chan.send("Removed")

# @bot.command()
async def list(ctx):
    """
    Join current tourney
    """
    player, chan, club = await get_vars(ctx)
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
                ret += " (" + u.tenhou_name + ")"
            ret += "\n"

    else:
        ret += printTables(tourney)

    ret += "```"
    await chan.send(ret)


# @bot.command()
# @commands.has_permissions(administrator=True)
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

    # First round is just random
    if tourney.current_round == 1:

        random.shuffle(users)
        tables = [[u.user_id for u in users[i:i + 4]] for i in range(0, len(users), 4)]


    # We want to ensure no one plays anyone they played the first round
    # Need at least 16 people, but should still get you the least overlap?
    else:

        tables = getTablesForRoundTourney(tourney.tourney_id, tourney.current_round - 1)

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


# @bot.command()
async def setTenhouName(ctx, tenhouName):
    """
    Set your tenhou name!
    """
    player, chan, club = await get_vars(ctx)

    ret = updateUserTenhouName(player.id, tenhouName)
    if ret == None:
        await chan.send(getError())
        return

    await chan.send("Updated tenhou name!")


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
    table = [["Score", "", "Pay", "Name"]]

    for row in players:
        score = str(row.score)
        shugi = str(row.shugi)
        payout = str(row.payout)
        if not "-" in shugi:
            shugi = "+" + shugi
        if not "-" in payout:
            payout = "+" + payout
        table.append([str(score), str(shugi), str(payout), str(row.name)])

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

    # Get scores to print
    scoreRet = ""
    if rate == "binghou":
        for row in scores:
            scoreRet += row.name + ": Kans " + str(row.kans) + " Yaku: " + ", ".join(intToYaku(row.binghou))
            scoreRet += "\n"
    else:
        scoreRet += formatScores(scores, tableRate)

    # Add scores to db
    if club.tourney_id != None:
        tourney = getTourney(club.tourney_id)
        game = createTenhouGame(logId, scoresOrdered, tableRate.name, tourney.current_round)
    else:
        for p in scoresOrdered:
            p.binghou = p.binghou & (1 << CARD.index("Kan!"))
            p.kans = 0
        game = createTenhouGame(logId, scoresOrdered, tableRate.name)

    if game == None:
        # await chan.send(getError())
        await ctx.message.add_reaction(EMOJI_WARNING)
        await chan.send("WARNING: Already scored that game! Will not be added\nHere are results anyways")
    else:

        # Add jade for kans
        if rate == "binghou":
            for row in scores:
                test = getUserFromTenhouName(row.name)
                if test and row.kans > 0:
                    updateUserJade(test.user_id, test.jade + row.kans * 100)

        ret = addGameToClub(club.club_id, game.tenhou_game_id)
        if club.tourney_id != None:
            addGameToTourney(club.tourney_id, game.tenhou_game_id)
        if ret == None:
            await ctx.message.add_reaction(EMOJI_ERROR)
            await chan.send(getError())
            return

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
async def start(ctx, p1=None, p2=None, p3=None, p4=None, table="general", randomSeat="true"):
    """
    Start Tenhou Game
    Args:
        player1 player2 player3 player4 randomSeating=[true/false]
    """

    player, chan, club = await get_vars(ctx)

    if (p1 == None or p2 == None or p3 == None or p4 == None):
        await chan.send(f"Please specify 4 players space separated")
        return

    player_names = [p1, p2, p3, p4]

    users = [getUserFromTenhouName(u) for u in player_names]
    for u in users:
        if u:
            updateUserTable(u.user_id, table)

    print(f"Starting, Admin:{club.tenhou_room} Rules:{club.tenhou_rules}")

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

    resp = requests.post('https://tenhou.net/cs/edit/cmd_start.cgi', data=data)
    if resp.status_code != 200:
        await chan.send(f"http error {resp.status_code} :<")
        return
    await chan.send(urllib.parse.unquote(resp.text))


@bot.command()
@commands.has_permissions(administrator=True)
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

    if updateClubTourney(club.club_id, tourney.tourney_id) == None:
        await chan.send(getError())
        return

    if tourney == None:
        await chan.send("Already have a tournament by that name!")
        return

    await chan.send(f"Started Tourney '{getTourney(club.tourney_id).tourney_name}'")


@bot.command()
@commands.has_permissions(administrator=True)
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


# @bot.command(aliases=['standings',"scores"])
async def rankings(ctx):
    """
    Get the standings of a current tourney!
    """
    player, chan, club = await get_vars(ctx)
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
