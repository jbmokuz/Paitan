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


@bot.command()
async def createAccount(ctx):
   """
   Create an account for this guild
   """
   player, chan, club = await get_vars(ctx)
   await createSiteAccount(player, chan)


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

@bot.event
async def on_message(message):
    await bot.process_commands(message)
        
bot.run(TOKEN)
