import discord, os
from discord.ext import commands
from functions import *
import requests, sys, re
import xml.etree.ElementTree as ET
import copy
import urllib


TOKEN = os.environ["DISCORD_DEV_TOKEN"]
ROOM_KEY = os.environ["TENHOU_DEV_KEY"]

bot = commands.Bot("!")
gi = GameInstance()

@bot.command()
async def start(ctx, p1=None, p2=None, p3=None, p4=None, randomSeat="true"):
    """
    Start Tenhou Game
    Args:
        player1 player2 player3 player3 randomSeating=[true/false]
    """

    player = ctx.author
    chan = ctx.channel

    if (p1 == None or p2 == None or p3 == None):
        await chan.send(f"Please specify 4 players space separated")
        return

    player_names = [p1,p2,p3]

    data = {
        "L":ROOM_KEY,
        "R2":"0011",
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
    player = ctx.author
    chan = ctx.channel
    await chan.send(f"pong")


@bot.command(aliases=['oi'])
async def join(ctx):
    """
    Join a list to wait for a game!
    """

    player = ctx.author
    chan = ctx.channel

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
    
    player = ctx.author
    chan = ctx.channel
    
    gi.reset()
    await chan.send(f"Cleared!")

@bot.command()
async def shuffle(ctx):
    """
    Assign players to tables!
    """
    player = ctx.author
    chan = ctx.channel
    
    tableD = gi.shuffle()

    
    if tableD == {}:
        await chan.send("Not tables could be made!")
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

    player = ctx.author
    chan = ctx.channel

    ret = ""

    if gi.waiting == []:
        await chan.send("Currently no one is waiting to play")
    else:
        for p in gi.waiting:
            ret += str(p) + "\n"
        await chan.send(ret)

@bot.command(aliases=["ranking"])
async def rankings(ctx,player_name=None):
    """
    Show the info for a player
    """
    
    player = ctx.author
    chan = ctx.channel
    ret = ""
    
    if player_name == None:
        for p in sorted(gi.players, key=lambda k: (len(gi.players[k].yaku), gi.players[k].kans))[::-1]:
            ret += str(gi.players[p]) + "\n"
        await chan.send(ret)
        return
    
    if not player_name in gi.players:
        await chan.send("player not found")
        return

    p = gi.players[player_name]
    ret += str(p) + "\n"
    for yaku in p.yaku:
        ret += yaku + "\n"
    #await player.send(ret)
    await chan.send(ret)    
    
@bot.command()
async def score(ctx, log=None):
    """
    Args:
        log:
            A full url or just the log id
    """

    
    player = ctx.author
    chan = ctx.channel

    if log == None:
        await chan.send("usage: !score [tenhou_log] !score https://tenhou.net/0/?log=2020051313gm-0209-19713-10df4ad2&tw=1")
        
    ret = gi.parseGame(log)
    if ret != 0:
        await chan.send(gi.lastError)
        return

    await chan.send(gi.lastError)
    
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
