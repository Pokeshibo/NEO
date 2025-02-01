import discord
from discord import app_commands
from discord.ext import commands
from database import db

class InviteTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invite_cache = {}

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            try:
                self.invite_cache[guild.id] = await guild.invites()
            except discord.Forbidden:
                pass

    @app_commands.command(name="invites", description="Check your invite statistics")
    async def invites(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild.id)
        
        count = db.c.execute('''SELECT COUNT(*) FROM invite_tracking 
                             WHERE invite_code IN 
                             (SELECT invite_code FROM invites WHERE inviter_id = ?)''',
                             (user_id,)).fetchone()[0]
        
        await interaction.response.send_message(
            f"You've invited {count} members to this server!",
            ephemeral=True
        )

    @app_commands.command(name="inviteinfo", description="Get invite details of a user")
    @app_commands.describe(member="Member to check")
    @commands.has_permissions(manage_guild=True)
    async def inviteinfo(self, interaction: discord.Interaction, member: discord.Member):
        user_id = str(member.id)
        guild_id = str(interaction.guild.id)
        
        result = db.c.execute('''SELECT invite_code, joined_at FROM invite_tracking 
                              WHERE member_id = ? AND guild_id = ?''',
                              (user_id, guild_id)).fetchone()
        
        if not result:
            await interaction.response.send_message("No invite data found!", ephemeral=True)
            return
            
        invite_code, joined_at = result
        inviter_id = db.c.execute('SELECT inviter_id FROM invites WHERE invite_code = ?', 
                                (invite_code,)).fetchone()[0]
        
        inviter = await self.bot.fetch_user(int(inviter_id))
        
        embed = discord.Embed(title="Invite Details", color=0x00ff00)
        embed.add_field(name="Invited By", value=inviter.mention)
        embed.add_field(name="Invite Code", value=invite_code)
        embed.add_field(name="Joined At", value=joined_at)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="inviteleaderboard", description="Show top inviters")
    async def invite_leaderboard(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        
        leaderboard = db.c.execute('''SELECT inviter_id, COUNT(*) as count 
                                   FROM invites 
                                   WHERE guild_id = ? 
                                   GROUP BY inviter_id 
                                   ORDER BY count DESC 
                                   LIMIT 10''', (guild_id,)).fetchall()
        
        embed = discord.Embed(title="Invite Leaderboard", color=0x00ff00)
        
        for index, (inviter_id, count) in enumerate(leaderboard, start=1):
            user = await self.bot.fetch_user(int(inviter_id))
            embed.add_field(
                name=f"{index}. {user.name}",
                value=f"**{count}** invites",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(InviteTracker(bot))
