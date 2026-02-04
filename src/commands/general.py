import discord
from discord import app_commands
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # スラッシュコマンドの定義
    @app_commands.command(name="ping", description="疎通確認を行います")
    # ユーザーインストールを許可する設定
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Pong! 遅延: {round(self.bot.latency * 1000)}ms",
            ephemeral=True # 自分にだけ見えるようにする場合はTrue
        )

async def setup(bot):
    await bot.add_cog(General(bot))
