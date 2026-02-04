import discord
import os
import asyncio
import sys
from discord.ext import commands
from dotenv import load_dotenv

# プロジェクトルートをパスに追加（ModuleNotFoundError対策）
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# インポート文：srcフォルダ内からの相対インポートとして扱う
try:
    from utils.keep_alive import keep_alive
except ImportError:
    # ローカル実行時などのためのフォールバック
    from src.utils.keep_alive import keep_alive

load_dotenv()

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True 
        
        super().__init__(
            command_prefix=["!", ">>"], 
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        """Cogの動的読み込み設定"""
        # main.pyがある場所（srcフォルダ）を取得
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        folders = ['commands', 'events']
        for folder in folders:
            folder_path = os.path.join(base_path, folder)
            
            if not os.path.exists(folder_path):
                continue

            for filename in os.listdir(folder_path):
                if filename.endswith('.py') and not filename.startswith('__'):
                    # インポートパスを 'commands.filename' の形式にする
                    extension = f'{folder}.{filename[:-3]}'
                    try:
                        await self.load_extension(extension)
                        print(f'✅ Loaded: {extension}')
                    except Exception as e:
                        print(f'❌ Failed to load {extension}: {e}')
        
        # スラッシュコマンド同期
        await self.tree.sync()
        print("♻️ Global Slash Commands Synced.")

    async def on_ready(self):
        print("-" * 30)
        print(f'Logged in as: {self.user.name} ({self.user.id})')
        print("-" * 30)
        await self.change_presence(activity=discord.Game(name="/hey | !help"))

async def main():
    # Renderのポート開放
    keep_alive()

    bot = MyBot()
    async with bot:
        token = os.getenv('DISCORD_TOKEN')
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
