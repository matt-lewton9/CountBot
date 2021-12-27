import discord
from discord.ext import commands, tasks
from discord.utils import get
from datetime import date
from icecream import ic
import pandas as pd
import os
from dotenv import load_dotenv

LIMIT = 100000 #limits to 100,000 messages

load_dotenv() #load env file
TOKEN = os.getenv("TOKEN") #get token from .env file

bot = commands.Bot(command_prefix="$") #create a bot

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot)) #log in


@bot.command(brief = 'Count messages')
async def count(ctx):

    #get guild from context
    guild = ctx.guild

    #get channel ids
    channels = []
    for channel in guild.text_channels:
        channels.append(channel.id)

    #get messages/make user list
    messages = {} #dictionary of lists containing dates as keys
    users = [] #list of users for reference
    key = 0 #column key for each user
    total = 0 #total messages scraped

    for channel in channels: #gets all users in last whatever channel
        async for message in guild.get_channel(channel).history(limit=LIMIT): #get messages

            total += 1 #add 1 to total
            
            msg_author = message.author.name #get message author

            if msg_author not in users: #if user is new, add them to users list
                users.append(msg_author)

            msg_date = str(message.created_at.date()) #get date of message

            if msg_date not in messages.keys(): #if date is new, create a dictionary entry containing a list of users
                messages[msg_date] = {} #init empty dict for each date
                
                for user in users: #init every user in dict as 0
                    messages[msg_date][user] = 0
                
            if msg_author not in messages[msg_date].keys(): #if user is not in the current date, add them
                messages[msg_date][msg_author] = 0

            messages[msg_date][msg_author] += 1 #increment counter for user on date

    ### EXPORT AS CSV ###
    df = pd.DataFrame(messages).T #make into pandas dataframe
    df.fillna(0) #fill all null entries with 0
    df.to_csv(f'{guild.name}_message_counts.csv') #export as CSV
  
    await ctx.send(f'{total} Messages Counted. Data Compiled to CSV.')

bot.run(TOKEN) #run bot
