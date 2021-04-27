# import discord
from discord.ext import commands
import ladder

class ListCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='list', pass_context=True)
    async def run(self, ctx):
        await ctx.send(self.get_ladder())

    def get_ladder(self):
        curr_ladder = ladder.get()
        message = "Current Loot Ladder:\n"
        for i in range(len(curr_ladder)):
            message += str(i+1) + ' : ' + curr_ladder[i]['name'] + '\n'
        return message

def setup(bot):
    bot.add_cog(ListCog(bot))