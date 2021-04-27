# import discord
from discord.ext import commands
import ladder


class MoveCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='drop', pass_context=True)
    async def drop(self, ctx, name: str):
        await self.move(ctx, name, ladder.length()+1)        

    @commands.command(name='move', pass_context=True)
    async def move(self, ctx, name: str, position: int):
        ladder.move(name, position)
        await ctx.send('Moved {0} to ladder position {1}'.format(name, position))

def setup(bot):
    bot.add_cog(MoveCog(bot))