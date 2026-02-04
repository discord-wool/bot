import discord
from discord import app_commands
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # スラッシュコマンドの定義
    @app_commands.command(name="hey", description="どこでも使える挨拶コマンド")
    # インストール対象：ユーザー（User）を許可、サーバー（Guild）も一応許可
    @app_commands.allowed_installs(guilds=True, users=True)
    # 実行場所：ギルド、DM、プライベートチャンネル（グループDM等）すべて許可
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def hey(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"こんにちは、{interaction.user.name}さん！私はあなたのユーザーインストール型ボットです。",
            ephemeral=True # 他の人に見られたくない場合はTrue
        )

async def setup(bot):
    await bot.add_cog(General(bot))
