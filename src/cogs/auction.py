# import discord
import discord
from discord.ext import commands, tasks
import ladder
import random
import ladder_service
import utils
import error_types

class AuctionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auctions = {}
        self.auctionCheck.start()

    def cog_unload(self):
        self.auctionCheck.cancel()

    async def isOfficer(ctx):
        if await utils.isOfficer(ctx.bot, ctx.author.name):
            return True
        raise error_types.OfficerOnlyFailure(ctx.author.name)
        
    def isDM(ctx):
        if type(ctx.channel) is discord.DMChannel:
            return True
        raise error_types.DMOnlyFailure(ctx.channel.name)

    @commands.command(name='auction', pass_context=True)
    @commands.check(isOfficer)
    async def auction(self, ctx, item_name: str, seconds: int):
        auc = ladder_service.createAuction(item_name, seconds)
        await utils.sendToChannel(self.bot, 'Starting auction for "{}" lasting {} seconds\nTo bid, send a direct message to me of the following command (with quotes and all):\n`!bid "{}"`'.format(auc.itemName, auc.seconds, auc.itemName))        
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')        
    
    @commands.command(name='bid', pass_context=True)
    @commands.check(isDM)
    async def bid(self, ctx, item_name: str):
        name = ctx.author.display_name
        ladder_service.bidOnAuction(item_name, name)
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

    @commands.command(name='print', pass_context=True)
    async def print(self, ctx):
        auctions = ladder_service.getAuctions        
        await ctx.send(auctions)

    @tasks.loop(seconds=10.0)
    async def auctionCheck(self):
        await ladder_service.checkForCompletedAuctions(self.bot)            

    @auctionCheck.before_loop
    async def before_auctionCheck(self):
        await self.bot.wait_until_ready()



def setup(bot):
    bot.add_cog(AuctionCog(bot))