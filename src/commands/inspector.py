import discord
from discord import app_commands
from discord.ext import commands
import io

class Inspector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 共通設定（ユーザーインストール対応）
    config = {
        "installs": app_commands.allowed_installs(guilds=True, users=True),
        "contexts": app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    }

    # 1. 指定したユーザーの権限を確認する
    @app_commands.command(name="check_perms", description="指定したユーザーのこのチャンネルでの権限を表示します")
    @config["installs"]
    @config["contexts"]
    async def check_perms(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        perms = interaction.channel.permissions_for(target)
        
        # 許可されている権限をリストアップ
        allowed_list = [name for name, value in perms if value]
        content = f"--- {target.name} の権限一覧 ---\n" + "\n".join(allowed_list)
        
        file = discord.File(io.StringIO(content), filename=f"perms_{target.id}.txt")
        await interaction.response.send_message(f"{target.mention} の権限情報を生成しました。", file=file, ephemeral=True)

    # 2. サーバー内の絵文字一覧を書き出す
    @app_commands.command(name="export_emojis", description="サーバー内のカスタム絵文字一覧（名前とID）を取得します")
    @config["installs"]
    @config["contexts"]
    async def export_emojis(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("サーバー内でのみ実行可能です。", ephemeral=True)
        
        emojis = [f"{e.name}: <:{e.name}:{e.id}> (ID: {e.id})" for e in interaction.guild.emojis]
        if not emojis:
            return await interaction.response.send_message("このサーバーにカスタム絵文字はありません。", ephemeral=True)
            
        content = f"{interaction.guild.name} 絵文字リスト\n" + "\n".join(emojis)
        file = discord.File(io.StringIO(content), filename="emojis.txt")
        await interaction.response.send_message("絵文字一覧を書き出しました。", file=file, ephemeral=True)

    # 3. チャンネル構成とトピックの一覧
    @app_commands.command(name="list_channels", description="チャンネル名とトピックの一覧を取得します")
    @config["installs"]
    @config["contexts"]
    async def list_channels(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("サーバー内でのみ実行可能です。", ephemeral=True)

        lines = []
        for channel in interaction.guild.text_channels:
            topic = channel.topic if channel.topic else "（トピックなし）"
            lines.append(f"#{channel.name}\n  ID: {channel.id}\n  Topic: {topic}\n")
        
        content = f"--- {interaction.guild.name} チャンネルリスト ---\n\n" + "\n".join(lines)
        file = discord.File(io.StringIO(content), filename="channels.txt")
        await interaction.response.send_message("チャンネル一覧を生成しました。", file=file, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Inspector(bot))
