import discord
from discord import app_commands
from discord.ext import commands
from database import db

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.describe(member="Member to kick", reason="Reason for kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.kick(reason=reason)
        await interaction.response.send_message(
            f'{member.mention} has been kicked. Reason: {reason}',
            ephemeral=True
        )

    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.describe(member="Member to ban", reason="Reason for ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.ban(reason=reason)
        await interaction.response.send_message(
            f'{member.mention} has been banned. Reason: {reason}',
            ephemeral=True
        )

    @app_commands.command(name="warnings", description="Check a member's warnings")
    @app_commands.describe(member="Member to check")
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        guild_id = str(interaction.guild.id)
        user_id = str(member.id)
        
        count = db.c.execute('SELECT count FROM warnings WHERE user_id = ? AND guild_id = ?',
                           (user_id, guild_id)).fetchone()
        count = count[0] if count else 0
        
        await interaction.response.send_message(
            f"{member.mention} has {count} warnings",
            ephemeral=True
        )

    @app_commands.command(name="purge", description="Delete multiple messages")
    @app_commands.describe(amount="Number of messages to delete")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int):
        await interaction.channel.purge(limit=amount + 1)
        await interaction.response.send_message(
            f"Deleted {amount} messages",
            ephemeral=True,
            delete_after=3
        )

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(
            f"Pong! Latency: {latency}ms",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Moderation(bot))
