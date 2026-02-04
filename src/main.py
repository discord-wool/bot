import discord
import os
import asyncio
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# 自作のWebサーバー（Renderのポート開放用）をインポート
from src.utils.keep_alive import keep_alive

# .envファイルを読み込む
load_dotenv()

class MyBot(commands.Bot):
    def __init__(self):
        # プレフィックスコマンドの設定 (! や >>)
        intents = discord.Intents.default()
        intents.message_content = True  # メッセージ読み取り権限
        intents.members = True          # サーバーメンバー情報取得権限
        
        super().__init__(
            command_prefix=["!", ">>"], 
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        """ボット起動時に実行される初期設定"""
        
        # 1. 各カテゴリのフォルダから拡張機能（Cog）を読み込む
        folders = ['commands', 'events']
        for folder in folders:
            folder_path = f'./src/{folder}'
            if not os.path.exists(folder_path):
                continue

            for filename in os.listdir(folder_path):
                if filename.endswith('.py') and not filename.startswith('__'):
                    extension = f'src.{folder}.{filename[:-3]}'
                    try:
                        await self.load_extension(extension)
                        print(f'✅ Loaded: {extension}')
                    except Exception as e:
                        print(f'❌ Failed to load {extension}: {e}')
        
        # 2. スラッシュコマンド（User Install対応）をDiscordに同期
        try:
            # グローバル同期（反映まで最大1時間かかる場合があります）
            synced = await self.tree.sync()
            print(f"♻️ Synced {len(synced)} slash commands globally.")
        except Exception as e:
            print(f"⚠️ Failed to sync commands: {e}")

    async def on_ready(self):
        """ボットがログインした時の処理"""
        print("-" * 30)
        print(f'Logged in as: {self.user.name}')
        print(f'Bot ID: {self.user.id}')
        print("-" * 30)
        
        # ボットのステータスを設定（例：/hey をプレイ中）
        activity = discord.Game(name="/hey | !help")
        await self.change_presence(status=discord.Status.online, activity=activity)

async def main():
    # Renderのスリープ防止用Webサーバーをバックグラウンドで起動
    keep_alive()

    # ボットの初期化と実行
    bot = MyBot()
    async with bot:
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            print("❌ DISCORD_TOKEN is not set in environment variables.")
            return
        
        await bot.start(token)

if __name__ == "__main__":
    # 非同期メイン関数を実行
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot is shutting down...")
