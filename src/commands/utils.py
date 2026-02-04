import discord
from discord import app_commands
from discord.ext import commands
import io
import datetime

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 共通の設定：どこでも使えるようにする
    common_settings = {
        "guilds": True,
        "users": True
    }
    context_settings = {
        "guilds": True,
        "dms": True,
        "private_channels": True
    }

    # 1. チャンネルのメッセージ情報をファイルとして返す
    @app_commands.command(name="export_messages", description="直近100件のメッセージをテキストファイルで書き出します")
    @app_commands.allowed_installs(**common_settings)
    @app_commands.allowed_contexts(**context_settings)
    async def export_messages(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True) # 処理に時間がかかるため一時待機
        
        messages = []
        async for message in interaction.channel.history(limit=100):
            timestamp = message.created_at.strftime('%Y-%m-%d %H:%M:%S')
            messages.append(f"[{timestamp}] {message.author}: {message.content}")
        
        content = "\n".join(reversed(messages))
        file = discord.File(io.StringIO(content), filename="chat_history.txt")
        
        await interaction.followup.send("メッセージ履歴を書き出しました：", file=file)

    # 2. サーバーのユーザーIDなどをまとめて返す
    @app_commands.command(name="user_ids", description="サーバー内のメンバーID一覧を取得します")
    @app_commands.allowed_installs(**common_settings)
    @app_commands.allowed_contexts(**context_settings)
    async def user_ids(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("このコマンドはサーバー内でのみ有効です。", ephemeral=True)

        members = [f"{m.name}: {m.id}" for m in interaction.guild.members]
        content = "\n".join(members)
        
        # 人数が多い場合に備えてファイルで送信
        file = discord.File(io.StringIO(content), filename="user_ids.txt")
        await interaction.response.send_message(f"{interaction.guild.name} のメンバーID一覧です：", file=file, ephemeral=True)

    # 3. サーバーの情報（人数や作成日）を返す
    @app_commands.command(name="server_info", description="サーバーの詳細情報を表示します")
    @app_commands.allowed_installs(**common_settings)
    @app_commands.allowed_contexts(**context_settings)
    async def server_info(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            return await interaction.response.send_message("サーバー情報が見つかりません。", ephemeral=True)

        embed = discord.Embed(title=f"サーバー情報: {guild.name}", color=discord.Color.blue())
        embed.add_field(name="サーバーID", value=guild.id, inline=False)
        embed.add_field(name="作成日", value=guild.created_at.strftime('%Y/%m/%d'), inline=True)
        embed.add_field(name="オーナー", value=guild.owner, inline=True)
        embed.add_field(name="メンバー数", value=guild.member_count, inline=True)
        embed.add_field(name="テキストチャンネル数", value=len(guild.text_channels), inline=True)
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Utils(bot))
