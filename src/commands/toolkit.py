import discord
from discord import app_commands
from discord.ext import commands
import io

class Toolkit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 共通設定（ユーザーインストール対応）
    config = {
        "installs": app_commands.allowed_installs(guilds=True, users=True),
        "contexts": app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    }

    # 1. サーバーのビジュアル素材（アイコン・バナー・招待背景）をまとめて取得
    @app_commands.command(name="get_assets", description="サーバーのアイコン、バナー、スプラッシュ画像等のURLを取得します")
    @config["installs"]
    @config["contexts"]
    async def get_assets(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            return await interaction.response.send_message("サーバー内で実行してください。", ephemeral=True)

        embed = discord.Embed(title=f"Assets: {guild.name}", color=discord.Color.gold())
        
        assets = {
            "Icon": guild.icon.url if guild.icon else "None",
            "Banner": guild.banner.url if guild.banner else "None",
            "Splash": guild.splash.url if guild.splash else "None",
            "Discovery": guild.discovery_splash.url if guild.discovery_splash else "None"
        }

        for name, url in assets.items():
            embed.add_field(name=name, value=url if url != "None" else "未設定", inline=False)
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # 2. セキュリティ診断：Botや特定のロールが「全チャンネル」で持つ権限をスキャン
    @app_commands.command(name="audit_access", description="特定のロールが全チャンネルで持っている閲覧権限をスキャンします")
    @app_commands.describe(role="調査したいロール（未指定ならBot自身）")
    @config["installs"]
    @config["contexts"]
    async def audit_access(self, interaction: discord.Interaction, role: discord.Role = None):
        if not interaction.guild:
            return await interaction.response.send_message("サーバー内で実行してください。", ephemeral=True)

        target = role or interaction.guild.me
        lines = [f"Audit Report for: {target.name}", "="*30]
        
        for channel in interaction.guild.text_channels:
            perms = channel.permissions_for(target)
            status = "✅ 閲覧可能" if perms.view_channel else "❌ 閲覧不可"
            send_status = "✍️ 発言可能" if perms.send_messages else "🚫 発言不可"
            lines.append(f"#{channel.name}: {status} / {send_status}")

        content = "\n".join(lines)
        file = discord.File(io.StringIO(content), filename=f"audit_{target.id}.txt")
        await interaction.response.send_message(f"{target.name} のアクセス権限診断結果です。", file=file, ephemeral=True)

    # 3. シンプルなEmbed作成（メッセージ送信ツール）
    @app_commands.command(name="echo_embed", description="綺麗な枠付きメッセージをボットに代筆させます")
    @app_commands.describe(title="タイトル", description="本文", color="色（16進数 例: ffb6c1）")
    @config["installs"]
    @config["contexts"]
    async def echo_embed(self, interaction: discord.Interaction, title: str, description: str, color: str = "3498db"):
        try:
            # 16進数カラーコードを整数に変換
            hex_color = int(color.replace("#", ""), 16)
            embed = discord.Embed(title=title, description=description, color=hex_color)
            embed.set_footer(text=f"Sent by {interaction.user.display_name}")
            
            # User Installボットの場合、ボットがいないサーバーでは送信できないためエラーハンドリング
            await interaction.response.send_message(embed=embed)
        except ValueError:
            await interaction.response.send_message("カラーコードが正しくありません（例: ff0000）", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Toolkit(bot))
