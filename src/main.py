import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む（ローカル用）
load_dotenv()

class MyBot(commands.Bot):
    def __init__(self):
        # プレフィックスと権限の設定
        intents = discord.Intents.default()
        intents.message_content = True 
        
        super().__init__(
            command_prefix=["!", ">>"], 
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        # Cog (commands と events) をロード
        for folder in ['commands', 'events']:
            folder_path = f'./src/{folder}'
            # フォルダが存在するか確認
            if not os.path.exists(folder_path):
                continue

            for filename in os.listdir(folder_path):
                if filename.endswith('.py') and not filename.startswith('__'):
                    # src.commands.filename の形式でロード
                    extension = f'src.{folder}.{filename[:-3]}'
                    try:
                        await self.load_extension(extension)
                        print(f'Loaded extension: {extension}')
                    except Exception as e:
                        print(f'Failed to load extension {extension}. Error: {e}')
        
        # スラッシュコマンド（ユーザーインストール型含む）を同期
        await self.tree.sync()
        print("Slash commands synced globally.")

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')

async def main():
    bot = MyBot()
    async with bot:
        # Renderの環境変数（Environment Variables）から取得
        token = os.getenv('DISCORD_TOKEN')
        if token:
            await bot.start(token)
        else:
            print("Error: DISCORD_TOKEN not found.")

if __name__ == "__main__":
    asyncio.run(main())
