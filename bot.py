import discord, os, random
from discord.ext import commands
from database import *
from objects import TENSAN, TENGO, TENPIN
import requests, sys, re
import xml.etree.ElementTree as ET
import copy
import urllib
from discord.ext.commands import has_permissions, MissingPermissions

if len(sys.argv) > 1:
    TOKEN = os.environ["DISCORD_DEV_TOKEN"]
else:
    TOKEN = os.environ["CHIITAN_TOKEN"]

bot = commands.Bot("$")

def get_vars(ctx):
    player = ctx.author
    chan = ctx.channel
    gi = getGameInstance(chan.guild.id)
    return player,chan,gi


@bot.command()
async def scores(ctx):
    player, chan, gi = get_vars(ctx)
    order = []
    ret = "```\n"
    for i in gi.players:
        p = gi.players[i]
        order.append([p.payout,p.name])
    order.sort()
    order = order[::-1]
    for score,name in order:
        if "-" in str(p.score):
            ret += f"+{score} {name}\n"
        else:
            ret += f" {score} {name}\n"
    ret += "```"
    await chan.send(ret)
    

@bot.command()
async def shogi_puzzle(ctx):
    player, chan, gi = get_vars(ctx)
    file = discord.File("screenshot.png", filename="image.png")
    embed = discord.Embed()
    embed.set_image(url="attachment://image.png")
    await chan.send(file=file, embed=embed)


@bot.command()
async def ping_for_games(ctx):
    player, chan, gi = get_vars(ctx)
    roles = await chan.guild.fetch_roles()
    if not "Ping for Games" in [i.name for i in roles]:
        await chan.guild.create_role(name="Ping for Games")

    role = discord.utils.get(chan.guild.roles, name="Ping for Games")
    await player.add_roles(role)
    await chan.send("Added")


@bot.command()
async def remove_ping_for_games(ctx):
    player, chan, gi = get_vars(ctx)

    roles = await chan.guild.fetch_roles()
    if not "Ping for Games" in [i.name for i in roles]:
        await chan.guild.create_role(name="Ping for Games")
    
    role = discord.utils.get(chan.guild.roles, name="Ping for Games")
    await player.remove_roles(role)
    await chan.send("Removed")

@bot.command()
async def set_tenhou_page(ctx,admin_page):
    """
    Set the tenhou admin page
    Args:
        tenhou admin page
    """
    player, chan, gi = get_vars(ctx)
    setAdminPage(chan.guild.id,admin_page)

    number = 1
    async for message in chan.history(limit=100):
        if message.author.id == player.id:
            await message.delete()
            number -= 1
        if number == 0:
            break

    await chan.send("Set tenhou admin page")

@bot.command()
async def set_tenhou_rules(ctx,rules):
    """
    Set the tenhou rules
    Args:
        tenhou rules
    """
    player, chan, gi = get_vars(ctx)
    setRules(chan.guild.id,rules)
    await chan.send("Set")

@bot.command()
async def info(ctx):
    """
    get info about rooms and bot
    """
    ret = ""
    player, chan, gi = get_vars(ctx)
    ret += f"```Tenhou: https://tenhou.net/0/?{gi.adminPage[0:9]}\n\n"
    ret += "Add Chii-tan to your server: https://discord.com/api/oauth2/authorize?client_id=732219732547076126&permissions=268957760&scope=bot\n\n"
    ret += "Source: https://github.com/jbmokuz/Paitan\n\n```"
    await chan.send(ret)

    
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

    print(f"Starting, Admin:{gi.adminPage} Rules:{gi.rules}")
    
    data = {
        "L":gi.adminPage,
        "R2":gi.rules,
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
    await chan.send(urllib.parse.unquote("&".join(resp.url.split("&")[1:])))

@bot.command(aliases=['p'])
async def ping(ctx):
    """
    Ping!
    """
    player, chan, gi = get_vars(ctx)
    
    player = ctx.author
    chan = ctx.channel
    await chan.send(f"pong {chan.guild.id}")

@bot.command(aliases=['oi'])
async def join(ctx):
    """
    Join a list to wait for a game!
    """
    player, chan, gi = get_vars(ctx)

    ret = gi.addWaiting(player)
    if ret != 0:
        await chan.send(gi.lastError)
        return
    await chan.send(f"{player} joined the waiting to play list!")

@bot.command(aliases=['rm','remove','rme'])
async def leave(ctx):
    """
    Leave the waiting to play list :(
    """
    player, chan, gi = get_vars(ctx)
    player = ctx.author
    chan = ctx.channel

    ret = gi.removeWaiting(player)
    if ret != 0:
        await chan.send(gi.lastError)
        return
    await chan.send(f"{player} left the waiting to play list!")

@bot.command(aliases=['clearlist'])
async def clear(ctx):
    """
    Clear waiting to play list
    """
    player, chan, gi = get_vars(ctx)
    
    gi.reset()
    await chan.send(f"Cleared!")

@bot.command()
async def shuffle(ctx):
    """
    Assign players to tables!
    """
    player, chan, gi = get_vars(ctx)    

    tableD = gi.shuffle(4)

    if tableD == {}:
        await chan.send("No tables could be made!")
    else:
        ret = ""
        for table in tableD:
            ret += f"Table {table}:\n"
            for player in tableD[table]:
                ret += "  "+str(player)+"\n"
            ret += "\n"
        await chan.send(ret)
    
@bot.command(aliases=["showlist"])
async def list(ctx):
    """
    Show who is looking to play mahjong!
    """
    player, chan, gi = get_vars(ctx)
    player = ctx.author
    chan = ctx.channel

    ret = "==== Tables ====\n"
    if gi.tables == {}:
        ret += "Currently no one is playing a game\n"
    else:
        for t in gi.tables:
            ret += f"{t}:\n"
            for p in gi.tables[t]:
                ret += f"  {p.name}\n"
        
    ret += "\n==== Waiting ====\n"
    if gi.waiting == []:
        ret += ("Currently no one is waiting to play\n")
    else:
        for p in gi.waiting:
            ret += f"{p.name}\n"
    await chan.send(ret)

@bot.command(aliases=["table","tableglhf"])
async def glhf(ctx,room_number):
    """
    Ping everyone in a table with room number!
    """
    player, chan, gi = get_vars(ctx)

    ret = ""

    table_number = gi.isPlaying(player)

    if table_number == 0:
        await chan.send(f"{player.name} is not playing!")
        return
    else:
        for p in gi.tables[table_number]:
            ret += f"{p.mention} "
        ret += f"\nRoom number: ```{room_number}```"
    await chan.send(ret)

@bot.command(aliases=["gg"])
async def tablegg(ctx):
    """
    Ping everyone in a table!
    """
    player, chan, gi = get_vars(ctx)
    
    ret = ""

    table_number = gi.isPlaying(player)

    if table_number == 0:
        await chan.send(f"{player.name} is not playing!")
        return
    else:
        for p in gi.tables[table_number]:
            ret += f"{p.mention} "
        ret += f"\nHave finished their game!\nPlease use !join to rejoin the list"
    gi.tableGG(table_number)
    await chan.send(ret)
    
@bot.command()
async def explain(ctx):
    """
    Explain how the last scoring was calculated
    """
    player, chan, gi = get_vars(ctx)    

    if(gi.lastScore == ""):
        await chan.send("Nothing has been scored yet")
        return
    await player.send(gi.lastScore)
    
@bot.command()
async def score(ctx, log=None, rate="tensan", shugi=None):
    """
    Score a tenhou log! (Results in cm)
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
        
    table = [["Score","","Pay","Name"]]

    rate = rate.lower()
    tableRate = None
    
    if rate == "tensan" or rate == "0.3" or rate == ".3":
        tableRate = copy.deepcopy(TENSAN)
    elif rate == "tengo" or rate == "0.5" or rate == ".5":
        tableRate = copy.deepcopy(TENGO)
    elif rate == "tenpin" or rate == "1.0":
        tableRate = copy.deepcopy(TENPIN)
    else:
        await chan.send(f"{rate} is not a valid rate (try !help score)")
        return

    if(shugi != None):
        try:
            tableRate.shugi = round(float(shugi),3)
        except:
            await chan.send(f"{shugi} is not a valid shugi")
            return
        
    rawLog, logId = gi.getRawLog(log)
    if rawLog == "":
        await chan.send("Could download log")
        return
    players = gi.parseTenhouXML(rawLog, tableRate)
    if players == None:
        await chan.send("Already submitted")
        return

    for p in players:
        score = str(p.score)
        shugi = str(p.shugi)
        payout = str(p.payout)
        #if not "-" in score:
        #    score = "+"+score
        if not "-" in shugi:
            shugi = "+"+shugi
        if not "-" in payout:
            payout = "+"+payout       
        table.append([str(score),str(shugi),str(payout),str(p.name)])

    colMax = [max([len(i) for i in c]) for c in zip(*table)]
    colMax[-1] = 0
    
    ret = f"```{tableRate}\n"
    for row in table:
        for i,col in enumerate(colMax):
            ret += row[i].ljust(col+1)
        ret += "\n"
    ret += "```"
    """
    for guild in bot.guilds:
        for log_chan in guild.text_channels:
            if str(log_chan) == "daily-log":
                print("found")
                try:
                    await log_chan.send(log)
                    await log_chan.send(ret)
                except:
                    print("No permissions to post in daily-log")
    """
    saveLog(gi, rawLog, ret, logId)
    await chan.send(ret)
    
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
