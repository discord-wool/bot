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

    async def setup_hook(self):
        # フォルダ内のファイルを読み込む
        # 読み込み時のパス指定を 'src.folder.file' の形式に合わせる
        for folder in ['commands', 'events']:
            for filename in os.listdir(f'./src/{folder}'):
                if filename.endswith('.py') and not filename.startswith('__'):
                    extension = f'src.{folder}.{filename[:-3]}'
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
