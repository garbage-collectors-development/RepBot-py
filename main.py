import os

import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
# print(TOKEN)
GUILD = os.getenv('GUILD')
GUILD_ID = os.getenv('GUILD_ID')
# print(GUILD)

# bot = commands.Bot(command_prefix='!')
bot = commands.Bot(command_prefix='!')

@bot.listen()
async def on_ready():

    global GUILD_ID

    for guild in bot.guilds:
        if guild.name == GUILD:
            GUILD_ID = guild.id
            print(GUILD_ID)
            break
    
    print("{0} is connected to the following guild".format(bot.user))
    print("{0}(id: {1})".format(guild.name, guild.id))

@bot.listen()
async def on_message(message:discord.Message):
    if message.author == bot.user:
        return
        
        # if message.content.startswith('-rep'):
        #     if len(message.mentions)==0:
        #         await message.channel.send("get rep for {0}".format(message.author.mention))
        #     elif len(message.mentions)==1:
        #         await message.channel.send("get rep for {0}".format(message.mentions[0].mention))
        #     else:
        #         await message.channel.send("You can only get rep for 1 user at a time")
        
    if len(message.mentions)>0 and find_thanks(message):
        if message.author in message.mentions:
            print (message.author)
            await message.channel.send("{0}, you cannot give yourself rep".format(message.author.mention))
            return
        for member in message.mentions:
            await message.channel.send("{0} you got some rep".format(member.mention))

def find_thanks(message:discord.Message)->bool:
    THANKS = ['thank', 'thanks', 'ty']
    matches = [w for w in THANKS if message.content.find(w)>-1]
    if len(matches)>0:
        return True
    else:
        return False

@bot.command(name='rep')
async def display_rep(ctx:commands.Context):
    if len(ctx.message.mentions)>1:
        await ctx.send("{0}, you can only get rep for one user at a time".format(ctx.author.mention))
    elif len(ctx.message.mentions)==1:
        await ctx.send("Get rep for {0}".format(ctx.message.mentions[0].mention))
    else:
        await ctx.send("get rep for {0}".format(ctx.author.mention))
    # await ctx.send("I got your message")



logger = logging.basicConfig(level='DEBUG')

bot.run(TOKEN)