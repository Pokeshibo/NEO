import discord
from discord import app_commands
from discord.ext import commands
from database import db
import time
import aiohttp
import datetime

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    @app_commands.command(name="healthcheck", description="Check bot's system health")
    async def healthcheck(self, interaction: discord.Interaction):
        embed = discord.Embed(title="System Health Report", color=0x00ff00)
        
        # Database Check
        try:
            db.c.execute("SELECT 1")
            embed.add_field(name="Database", value="✅ Operational", inline=False)
        except Exception as e:
            embed.add_field(name="Database", value=f"❌ Error: {str(e)}", inline=False)
        
        # API Check
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.deepseek.com/v1/ping") as resp:
                    status = "✅ Operational" if resp.status == 200 else "❌ Unavailable"
                    embed.add_field(name="AI API", value=status, inline=False)
        except Exception as e:
            embed.add_field(name="AI API", value=f"❌ Error: {str(e)}", inline=False)
        
        # Performance
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=False)
        
        # Uptime
        uptime = str(datetime.timedelta(seconds=int(time.time() - self.start_time)))
        embed.add_field(name="Uptime", value=uptime, inline=False)
        
        # Commands
        commands = len(self.bot.tree.get_commands())
        embed.add_field(name="Commands", value=f"{commands} registered", inline=False)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Utilities(bot))
