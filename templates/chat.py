import discord
from discord.ext import commands
import os
import aiohttp
from langdetect import detect

class ChatBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conversation_history = {}
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
            "Content-Type": "application/json"
        }

    async def _call_api(self, user_id: int, prompt: str):
        try:
            lang = detect(prompt) if len(prompt) > 3 else "en"
            
            messages = [{
                "role": "system",
                "content": f"Respond in {lang} if appropriate. Be helpful and friendly."
            }]
            
            if user_id in self.conversation_history:
                messages.extend(self.conversation_history[user_id][-5:])
            
            messages.append({"role": "user", "content": prompt})

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json={
                        "model": "deepseek-chat",
                        "messages": messages,
                        "temperature": 0.7
                    },
                    headers=self.headers
                ) as response:
                    data = await response.json()
                    response_text = data['choices'][0]['message']['content']
                    
                    # Update history
                    if user_id not in self.conversation_history:
                        self.conversation_history[user_id] = []
                    self.conversation_history[user_id].extend([
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": response_text}
                    ])
                    
                    return response_text
                    
        except Exception as e:
            print(f"API Error: {e}")
            return "I'm having trouble responding right now. Please try again later."

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or not message.guild:
            return

        if self.bot.user.mentioned_in(message):
            async with message.channel.typing():
                response = await self._call_api(message.author.id, message.content)
                await message.reply(response, mention_author=True)

async def setup(bot):
    await bot.add_cog(ChatBot(bot))
