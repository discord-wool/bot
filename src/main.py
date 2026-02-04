import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  # メッセージ内容を読み取るために必須
        
        # プレフィックスをリストで指定
        super().__init__(
            command_prefix=["!", ">>"], 
            intents=intents,
            help_command=None # デフォルトのhelpを無効化する場合
        )

    # src/main.py の setup_hook 内を修正
    async def setup_hook(self):
        # Cogのロード
        for folder in ['commands', 'events']:
            for filename in os.listdir(f'./src/{folder}'):
                if filename.endswith('.py'):
                    await self.load_extension(f'src.{folder}.{filename[:-3]}')
        
        # スラッシュコマンドをDiscordに送信（同期）
        # ※開発時は起動のたびに実行してOKですが、本番では回数制限に注意
        await self.tree.sync()
        print("Slash commands synced.")
                    await self.load_extension(extension)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')

async def main():
    bot = MyBot()
    async with bot:
        token = os.getenv('DISCORD_TOKEN')
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
