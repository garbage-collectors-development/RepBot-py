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
max_given_rep = 4
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
        message_str = '\n'.join(tuple("gave +1 rep to **{0}**".format(member.name, member.discriminator) for index, member in enumerate(message.mentions)
                    if index < max_given_rep))
        await message.channel.send(message_str)

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
    """Get rep for all users containing rep and paginate it in the chat
    A maximum of 25 users will be displayed on each page"""

    def get_split_members(members:dict)->[dict]:
        """Splits the members dict into a list of dicts with a maximum of 25
        Member objects in each dict"""
        member_array = []
        for index, member in members.items():
            if (index-1) % 25 == 0:
                member_array.append(dict())
            member_array[-1][index] = member

        return member_array

    def get_embeds(member_array:[dict])->(str,):
        """Turns the member_array into a list of embed objects for the 
        pagination tool to use"""

        description = '#{0:0>3}:{1:>7} - {2}#{3}'

        embed_strings = []
        for dictionary in member_array:
            temp_str='```{0}```'.format(
                '\n'.join(
                    [description.format(rank,member.rep,member.member.name, member.member.discriminator)
                        for rank, member in dictionary.items()]
                )
            )
            embed_strings.append(temp_str)

        embeds=tuple(discord.Embed(title="Reputation Leaderboard", description=string) for string in embed_strings)
        
        return embeds
    
    ordered_members = sql.get_users_by_rep()
    member_array = get_split_members(ordered_members)
    embeds = get_embeds(member_array)
    paginator = BotEmbedPaginator(ctx, embeds)
    await paginator.run()


if __name__ == '__main__':
    logger = logging.basicConfig(level='DEBUG')
    bot.run(TOKEN)