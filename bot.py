import discord, os, random
from discord.ext import commands
from database import *
from objects import TENSAN, TENGO, TENPIN
import requests, sys, re
import xml.etree.ElementTree as ET
import copy
import urllib
from discord.ext.commands import has_permissions, MissingPermissions
from database import *

if len(sys.argv) > 1:
    TOKEN = os.environ["DISCORD_DEV_TOKEN"]
else:
    TOKEN = os.environ["CHIITAN_TOKEN"]

bot = commands.Bot("$")

def get_vars(ctx):
    player = ctx.author
    chan = ctx.channel
    gi = getClub(chan.guild.id)
    if gi == 1:
        createClub(chan.guild.id,chan.guild.name)
    gi = getClub(chan.guild.id)
    return player,chan, gi



#id=119046709983707136 name='moku' discriminator='9015'
@bot.command()
@commands.has_permissions(administrator=True)
async def createAccount(ctx):
    """
    for testing
    """
    player, chan, gi = get_vars(ctx)
    username = player.name+"#"+player.discriminator
    passwd = createUser(player.id,username)
    if passwd == 1 or passwd == 2:
        await player.send("User already created")
        #return
    else:
        ret = f"Username:{username} Pass:{passwd}"
        await player.send(ret)
    ret = addUserToClub(chan.guild.id,player.id)
    if ret == 0:
        await player.send(f"Now managing {chan.guild.name}")
    else:
        print(f"ERR: {ret}")
    await player.send("Manage account @ http://yakuhai.com")


@bot.command()
async def info(ctx):
    """
    get info about rooms and bot
    """
    ret = ""
    player, chan, gi = get_vars(ctx)
    ret += f"```Tenhou: https://tenhou.net/0/?{gi.tenhou_room[0:9]}\n\n"
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
        "L":gi.tenhou_room,
        "R2":gi.tenhou_rules,
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
