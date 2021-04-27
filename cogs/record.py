import discord
from discord.ext import commands
import ladder
import typing
from datetime import datetime

class RecordCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO allow passing in your own date
    @commands.command(name='record', pass_context=True)
    async def record(self, ctx, name: typing.Optional[str]):
        msg = "Recorded Raid attendance for:\n"
        if None == name:
            # update all members of voice channel with name 'raid'
            raid_channel = discord.utils.get(self.bot.get_all_channels(), name='raid', type=discord.ChannelType.voice)            
            for i in range(len(raid_channel.members)):  
                #TODO HANDLE PEOPLE NOT IN LADDER
                raider_name = raid_channel.members[i].display_name
                ladder.updateLastRaidDate(raider_name, self.getTodaysDate())
                msg += raider_name + "\n"               
        else:
            # update <name>
            ladder.updateLastRaidDate(name, self.getTodaysDate())
            msg += name + "\n"        
        await ctx.send(msg)   

    def getTodaysDate(self):
        return datetime.today().strftime('%m-%d-%Y')


def setup(bot):
    bot.add_cog(RecordCog(bot))