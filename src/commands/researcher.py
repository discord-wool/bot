import discord
from discord import app_commands
from discord.ext import commands
import io
import re

class Researcher(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 共通設定（ユーザーインストール対応）
    config = {
        "installs": app_commands.allowed_installs(guilds=True, users=True),
        "contexts": app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    }

    # 1. ロール一覧と所属人数、権限の要約
    @app_commands.command(name="list_roles", description="サーバーのロール構成と権限の詳細を書き出します")
    @config["installs"]
    @config["contexts"]
    async def list_roles(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("サーバー内で実行してください。", ephemeral=True)

        lines = []
        # 役職をポジション順（上から下）にソート
        roles = sorted(interaction.guild.roles, key=lambda r: r.position, reverse=True)
        
        for r in roles:
            # 主要な権限があるかチェック
            admin = " [ADMIN]" if r.permissions.administrator else ""
            lines.append(f"Rank: {r.position} | Name: {r.name} | ID: {r.id} | Members: {len(r.members)}{admin}")

        content = f"--- {interaction.guild.name} ロールリスト ---\n\n" + "\n".join(lines)
        file = discord.File(io.StringIO(content), filename="roles_report.txt")
        await interaction.response.send_message("ロール一覧を生成しました。", file=file, ephemeral=True)

    # 2. 特定の単語を含むメッセージを検索して抽出 (直近500件から)
    @app_commands.command(name="search_word", description="チャンネル内を検索し、特定の単語を含む発言を抽出します")
    @app_commands.describe(word="検索したい単語", limit="遡るメッセージ数（最大1000）")
    @config["installs"]
    @config["contexts"]
    async def search_word(self, interaction: discord.Interaction, word: str, limit: int = 500):
        await interaction.response.defer(ephemeral=True)
        
        limit = min(limit, 1000) # 最大1000件に制限
        found_messages = []
        
        async for msg in interaction.channel.history(limit=limit):
            if word.lower() in msg.content.lower():
                ts = msg.created_at.strftime('%Y-%m-%d %H:%M')
                found_messages.append(f"[{ts}] {msg.author}: {msg.content}")

        if not found_messages:
            return await interaction.followup.send(f"「{word}」を含むメッセージは見つかりませんでした。", ephemeral=True)

        content = f"Search Result for: {word}\n" + "-"*30 + "\n" + "\n".join(found_messages)
        file = discord.File(io.StringIO(content), filename=f"search_{word}.txt")
        await interaction.followup.send(f"「{word}」の検索結果（{len(found_messages)}件）です。", file=file)

    # 3. サーバーの有効な招待リンク一覧の取得
    @app_commands.command(name="list_invites", description="サーバー内の有効な招待リンクと使用回数を確認します")
    @config["installs"]
    @config["contexts"]
    async def list_invites(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("サーバー内で実行してください。", ephemeral=True)
        
        # ボットに招待管理権限があるか確認
        if not interaction.guild.me.guild_permissions.manage_guild:
            return await interaction.response.send_message("招待リンクを取得するには、ボットに『サーバー管理』権限が必要です。", ephemeral=True)

        invites = await interaction.guild.invites()
        if not invites:
            return await interaction.response.send_message("有効な招待リンクはありません。", ephemeral=True)

        lines = []
        for inv in invites:
            uses = inv.uses if inv.uses else 0
            max_uses = inv.max_uses if inv.max_uses else "∞"
            lines.append(f"Code: {inv.code} | Created by: {inv.inviter} | Uses: {uses}/{max_uses} | Channel: #{inv.channel.name}")

        content = f"--- {interaction.guild.name} 招待リンク一覧 ---\n\n" + "\n".join(lines)
        file = discord.File(io.StringIO(content), filename="invites.txt")
        await interaction.response.send_message("招待リンク情報を取得しました。", file=file, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Researcher(bot))
