import discord
from discord import app_commands
from discord.ext import commands
import io
from collections import Counter

class Helper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 共通設定（ユーザーインストール・全コンテキスト対応）
    config = {
        "installs": app_commands.allowed_installs(guilds=True, users=True),
        "contexts": app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    }

    # 1. ユーザーの詳細情報を取得 (権限不要)
    @app_commands.command(name="user_lookup", description="指定したユーザーの公開情報を詳しく表示します")
    @app_commands.describe(user="調査したいユーザー")
    @config["installs"]
    @config["contexts"]
    async def user_lookup(self, interaction: discord.Interaction, user: discord.User = None):
        target = user or interaction.user
        
        embed = discord.Embed(title=f"User Info: {target.name}", color=target.accent_color or discord.Color.blue())
        embed.set_thumbnail(url=target.display_avatar.url)
        
        embed.add_field(name="ユーザー名", value=target.name, inline=True)
        embed.add_field(name="ID", value=target.id, inline=True)
        embed.add_field(name="アカウント作成日", value=target.created_at.strftime('%Y/%m/%d'), inline=False)
        embed.add_field(name="Botかどうか", value="はい" if target.bot else "いいえ", inline=True)
        
        if target.banner:
            embed.set_image(url=target.banner.url)
            
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # 2. チャンネル内の発言者ランキング (直近200件)
    @app_commands.command(name="chat_stats", description="直近のチャットの活発なユーザーを統計します")
    @config["installs"]
    @config["contexts"]
    async def chat_stats(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        authors = []
        try:
            async for msg in interaction.channel.history(limit=200):
                if not msg.author.bot:
                    authors.append(msg.author.display_name)
            
            if not authors:
                return await interaction.followup.send("集計できるメッセージが見つかりませんでした。")

            # 統計を作成
            counter = Counter(authors)
            ranking = counter.most_common(10)
            
            results = [f"{i+1}. {name}: {count} messages" for i, (name, count) in enumerate(ranking)]
            content = "--- 直近200件の発言者ランキング ---\n" + "\n".join(results)
            
            await interaction.followup.send(f"```\n{content}\n```")
        except discord.Forbidden:
            await interaction.followup.send("メッセージ履歴を読む権限がありません。")

    # 3. サーバーの全絵文字をURL付きでリスト化
    @app_commands.command(name="emoji_urls", description="サーバーの絵文字をすべてURL付きのリストとして書き出します")
    @config["installs"]
    @config["contexts"]
    async def emoji_urls(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("サーバー内でのみ実行可能です。", ephemeral=True)

        if not interaction.guild.emojis:
            return await interaction.response.send_message("このサーバーにカスタム絵文字はありません。", ephemeral=True)

        lines = [f"{e.name}: {e.url}" for e in interaction.guild.emojis]
        content = f"--- {interaction.guild.name} 絵文字URLリスト ---\n\n" + "\n".join(lines)
        
        file = discord.File(io.StringIO(content), filename="emojis_url.txt")
        await interaction.response.send_message("絵文字のURLリストを生成しました。", file=file, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Helper(bot))
