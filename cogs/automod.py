import discord
from discord.ext import commands
from database import db

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        
        guild_id = str(message.guild.id)
        bad_words = db.c.execute('SELECT word FROM bad_words WHERE guild_id = ?', 
                               (guild_id,)).fetchall()
        bad_words = [word[0] for word in bad_words]
        
        if any(word in message.content.lower() for word in bad_words):
            await message.delete()
            await message.channel.send(
                f"{message.author.mention} Please maintain proper language!",
                delete_after=5
            )
            await self.add_warning(message.author, guild_id)

    async def add_warning(self, user, guild_id):
        user_id = str(user.id)
        db.c.execute('''INSERT OR REPLACE INTO warnings 
                     VALUES (?,?,COALESCE((SELECT count FROM warnings WHERE user_id=? AND guild_id=?),0)+1)''',
                     (user_id, guild_id, user_id, guild_id))
        db.conn.commit()
        
        warnings = db.c.execute('SELECT count FROM warnings WHERE user_id = ? AND guild_id = ?', 
                              (user_id, guild_id)).fetchone()[0]
        warn_limit = db.c.execute('SELECT warn_limit FROM guild_settings WHERE guild_id = ?', 
                                (guild_id,)).fetchone()
        warn_limit = warn_limit[0] if warn_limit else 3
        
        if warnings >= warn_limit:
            await user.ban(reason=f"Exceeded warning limit ({warnings}/{warn_limit})")

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
