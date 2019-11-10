import os

import discord
from disputils import BotEmbedPaginator
from discord.ext import commands
import logging
from dotenv import load_dotenv
import pathlib
import datetime

import persistance

load_dotenv()
TOKEN = os.getenv('TOKEN')
# print(TOKEN)
GUILD_NAME = os.getenv('GUILD')
GUILD_ID = os.getenv('GUILD_ID')
DB_LOCATION = os.getenv('DB_LOCATION')
current_guild = None
# print(GUILD)

# bot = commands.Bot(command_prefix='!')
bot = commands.Bot(command_prefix='!')
db_file = pathlib.Path(DB_LOCATION)
sql = persistance.Persistance(db_file)

@bot.listen()
async def on_ready():

    global current_guild

    for guild in bot.guilds:
        if guild.name == GUILD_NAME:
            sql.guild = guild
            print(GUILD_ID)
            break


    current_users = sql.users
    missing_users=tuple(member for member in bot.get_all_members() if member not in current_users)
    for member in missing_users:
        sql.add_new_user(member)
    
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
        now = datetime.datetime.now()
        hold_time = now - datetime.timedelta(minutes=12)
        if message.author in message.mentions:
            print (message.author)
            await message.channel.send("{0}, you cannot give yourself rep".format(message.author.mention))
            return
        if not datetime.datetime.now() > sql.get_last_used(message.author) > (datetime.datetime.now() - datetime.timedelta(minutes=12)):
            sql.add_rep(message.mentions)
            sql.set_last_used(message.author)
        else:
            # not allowing rep more frequent than every 12 minutes.
            return
        for member in message.mentions:
            await message.channel.send("{0} you got some rep".format(member.mention))

def find_thanks(message:discord.Message)->bool:
    THANKS = ('thank', 'thanks', 'ty')
    matches = tuple(w for w in THANKS if message.content.find(w)>-1)
    if len(matches)>0:
        return True
    else:
        return False

@bot.command(name='rep',help = "gets the rep for a specific user")
async def display_rep(ctx:commands.Context):
    if len(ctx.message.mentions)>1:
        await ctx.send("{0}, you can only get rep for one user at a time".format(ctx.author.mention))
    elif len(ctx.message.mentions)==1:
        user_rep = sql.get_rep(ctx.message.mentions[0])
        await ctx.send("{0} has {1} rep".format(ctx.message.mentions[0].mention, user_rep))
    else:
        author_rep = sql.get_rep(ctx.author)
        await ctx.send("{0} has {1} rep".format(ctx.author.mention, author_rep))
    # await ctx.send("I got your message")

@bot.command(name='setrep', help = "sets the rep for the mentioned user")
@commands.has_role('admin')
async def set_rep(ctx:commands.Context, member:discord.Member, rep:int):

    sql.set_rep(member, rep)

    await ctx.send("{0}'s rep is now {1}".format(member.mention, rep))

@bot.command(name='getrep', help = 'gets the rep for all users')
async def get_rep_for_all_users(ctx:commands.Context):
    
    ordered_members = sql.get_users_by_rep()
    # message = "\n".join([f'#{rank:0>2}:{member.rep:>7} - {member.member.name}#{member.member.discriminator}' for rank, member in ordered_members.items()])
    # message = "```\n{0}```".format(message)
    # #await ctx.send(message)

    # embed = discord.Embed(
    #     title = "Reputation Leaderboard",
    #     description = message
    # )
    embeds = [discord.Embed(title = "Reputation Leaderbpard", description=f'`#{rank:0>2}:{member.rep:>7} - {member.member.name}#{member.member.discriminator}`') for rank, member in ordered_members.items()]

    paginator = BotEmbedPaginator(ctx, embeds)
    await paginator.run()



logger = logging.basicConfig(level='DEBUG')

bot.run(TOKEN)