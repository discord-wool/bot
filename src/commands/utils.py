import discord
from discord import app_commands
from discord.ext import commands
import io

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    config = {
        "installs": app_commands.allowed_installs(guilds=True, users=True),
        "contexts": app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    }

    # 1. メッセージ書き出し (閲覧権限があればOK)
    @app_commands.command(name="export_messages", description="閲覧可能な直近100件を書き出します")
    @config["installs"]
    @config["contexts"]
    async def export_messages(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # ボットに「メッセージ履歴を読む」権限があるか確認（なくても試行するがエラーハンドリング）
        try:
            messages = []
            async for message in interaction.channel.history(limit=100):
                ts = message.created_at.strftime('%Y-%m-%d %H:%M')
                messages.append(f"[{ts}] {message.author}: {message.content}")
            
            if not messages:
                return await interaction.followup.send("読み取れるメッセージがありませんでした。")

            content = "\n".join(reversed(messages))
            file = discord.File(io.StringIO(content), filename="history.txt")
            await interaction.followup.send("履歴を抽出しました：", file=file)
        except discord.Forbidden:
            await interaction.followup.send("このチャンネルの履歴を読む権限がボットにありません。")

    # 2. ユーザーID一覧 (ボットに見えるメンバーのみ)
    @app_commands.command(name="user_ids", description="ボットが捕捉しているメンバーID一覧を取得します")
    @config["installs"]
    @config["contexts"]
    async def user_ids(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("サーバー内で実行してください。", ephemeral=True)

        # 管理権限がない場合、キャッシュされているメンバーのみ表示
        members = [f"{m.name}: {m.id}" for m in interaction.guild.members]
        content = f"Total Captured: {len(members)}\n\n" + "\n".join(members)
        
        file = discord.File(io.StringIO(content), filename="members.txt")
        await interaction.response.send_message(f"メンバーリスト (Visible to Bot) です：", file=file, ephemeral=True)

    # 3. サーバー情報 (一般公開情報のみ)
    @app_commands.command(name="server_info", description="サーバーの基本情報を表示します")
    @config["installs"]
    @config["contexts"]
    async def server_info(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            return await interaction.response.send_message("サーバー情報が取得できません。", ephemeral=True)

        embed = discord.Embed(title=f"Server: {guild.name}", color=0x3498db)
        embed.add_field(name="人数", value=guild.member_count)
        embed.add_field(name="作成日", value=guild.created_at.strftime('%Y/%m/%d'))
        # オーナーなどは権限によって取得できない場合があるためエラー回避
        owner = guild.owner.name if guild.owner else "取得不可"
        embed.add_field(name="オーナー", value=owner)
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Utils(bot))
