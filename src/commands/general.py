from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        """疎通確認用のコマンド"""
        await ctx.send(f"Pong! 遅延: {round(self.bot.latency * 1000)}ms")

async def setup(bot):
    await bot.add_cog(General(bot))
