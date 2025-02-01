import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

async def load_cogs():
    cogs = [
        'cogs.moderation',
        'cogs.automod',
        'cogs.invites',
        'cogs.utilities',
        'cogs.settings',
        'cogs.chatbot'
    ]
    
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f'Loaded cog: {cog}')
        except Exception as e:
            print(f'Failed to load cog {cog}: {e}')

@bot.event
async def on_ready():
    await load_cogs()
    await bot.tree.sync()
    print(f'Bot {bot.user.name} is ready!')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="/help"
    ))

bot.run(os.getenv('DISCORD_TOKEN'))
