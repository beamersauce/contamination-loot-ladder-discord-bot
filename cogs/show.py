# import discord
from discord.ext import commands
import ladder
import typing

class ShowCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='show', pass_context=True)
    async def run(self, ctx, name: typing.Optional[str]):
        if None == name:
            #get current user
            name = ctx.author.display_name
        print(name)
        index = ladder.getPosition(name)
        await ctx.send("{}'s position on the loot ladder is: {}".format(name, index))
    
    # def getName(self, ctx):
    #     print(ctx.author)
    #     if None != ctx.author.nickname:
    #         return ctx.author.nick
    #     return ctx.author.name      

def setup(bot):
    bot.add_cog(ShowCog(bot))