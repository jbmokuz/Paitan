import discord
import sys
import discord, os, random
from discord.ext import commands
import time
import glob
import socket

HOST = '127.0.0.1'
PORT = 7501

TOKEN = os.environ["DISCORD_DEV_TOKEN"]  
bot = commands.Bot("&")

guild_name = "bot_testing"
#emote_chan_name = sys.argv[1]


#if len(sys.argv) < 4:
#    sys.exit(0)



FILE_PATH = "./app/static/chars"

bamboo = set([n.split("/")[-1].split("-")[0] for n in glob.glob(f"{FILE_PATH}/bamboo/*")])
default = set([n.split("/")[-1].split("-")[0] for n in glob.glob(f"{FILE_PATH}/default/*")])
promo = set([n.split("/")[-1].split("-")[0] for n in glob.glob(f"{FILE_PATH}/promo/*")])
sakura = set([n.split("/")[-1].split("-")[0] for n in glob.glob(f"{FILE_PATH}/sakura/*")])

@bot.event
async def on_ready():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while 1:                        
            conn, addr = s.accept()
            with conn:
                while True:
                    data = conn.recv(1024)
                    print(data)
                    if len(data.decode("utf-8").split(",")) == 3:
                        emote_chan_name, char, numb = data.decode("utf-8").split(",")
                        print(char)
                        for guild in bot.guilds:
                            if guild.name == guild_name:
                                for chan in guild.text_channels:
                                    if str(chan) == emote_chan_name:
                                        #try:
                                        if 1==1:
                                                if char in bamboo:
                                                    file = discord.File(f"{FILE_PATH}/bamboo/{char}-{numb}.png", filename="image.png")
                                                elif char in default:
                                                    file = discord.File(f"{FILE_PATH}/default/{char}-{numb}.png", filename="image.png")
                                                elif char in promo:
                                                    file = discord.File(f"{FILE_PATH}/promo/{char}-{numb}.png", filename="image.png")
                                                elif char in sakura:
                                                    file = discord.File(f"{FILE_PATH}/sakura/{char}-{numb}.png", filename="image.png")
                                                else:
                                                    continue
                                                embed = discord.Embed()
                                                embed.set_thumbnail(url="attachment://image.png")
                                                await chan.send(file=file, embed=embed)
                                        #except:
                                        #    print("NOOOOO")
                                        #    sys.exit(0)
                    else:
                        break
            
bot.run(TOKEN)
