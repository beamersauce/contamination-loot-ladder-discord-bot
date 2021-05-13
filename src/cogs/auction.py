import discord
from discord.ext import commands, tasks
import ladder
import random
import utils
import error_types
import ladder_svc
import typing
import playername_lookup
import datetime

class AuctionCog(commands.Cog, name='Auction'):
    def __init__(self, bot, ladder_service: ladder_svc.LadderService):
        self.bot = bot
        self.auctions = {}
        self.auctionCheck.start()
        self.ladder_service = ladder_service
        self.playerlookup = playername_lookup.PlayerNameLookup(ladder_service, bot)

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

    @commands.command(name='auction', pass_context=True, brief='start an auction', description='starts an auction for an item')
    @commands.check(isOfficer)
    async def auction(self, ctx, item_name: str, seconds: int):
        auc = self.ladder_service.createAuction(item_name, seconds)
        message = await utils.sendToChannel(self.bot, 'Starting auction for "{}" lasting {} seconds\nTo bid:\n\tAdd a check reaction to this message\n\tOR send a direct message to me with the following command (with quotes and all):\n`!bid "{}"`'.format(auc.itemName, auc.seconds, auc.itemName))        
        await message.add_reaction('\U00002705')
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')        
    
    @commands.command(name='bid', pass_context=True, brief='bid on an auction', description='bids your position on an active auction')
    @commands.check(isDM)
    async def bid(self, ctx, item_name: str):
        name = ctx.author.display_name
        playername = self.playerlookup.findPlayerName(name)
        self.ladder_service.bidOnAuction(item_name, playername)
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

    @commands.command(name='abid', pass_context=True, brief='bid on an auction for someone', description='bids a players position on an active auction, this is useful when a player cant bid for themself')
    @commands.check(isOfficer)
    async def adminBid(self, ctx, item_name: str, name: str):
        playername = self.playerlookup.findPlayerName(name)
        self.ladder_service.bidOnAuction(item_name, playername)
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

    @commands.command(name='print', pass_context=True, brief='show auctions', description='shows all current auctions')
    @commands.check(isDM)
    async def print(self, ctx):
        msg = self.printRunningAuctions()
        await ctx.send(msg)

    def printRunningAuctions(self):
        auctions = self.ladder_service.getAuctions()             
        msg = 'Auctions:'
        if len(auctions) == 0:
            msg += ' no active auctions'
        else:
            for key in auctions:            
                auc = auctions[key]
                now = datetime.datetime.today()
                msg += '\nItemName: {}\t Seconds Remaining: {}\t Bids: {}'.format(auc.itemName, round(auc.seconds - (now - auc.startTime).total_seconds()), auc.bids)                
        return msg

    @tasks.loop(seconds=30.0)
    async def auctionCheck(self):
        await self.ladder_service.checkForCompletedAuctions(self.bot)  
        auctions = self.ladder_service.getAuctions() 
        if len(auctions) > 0:
            msg = self.printRunningAuctions()
            await utils.sendToChannel(self.bot, msg)

    @auctionCheck.before_loop
    async def before_auctionCheck(self):
        await self.bot.wait_until_ready()



def setup(bot, ladder_service: ladder_svc.LadderService):
    bot.add_cog(AuctionCog(bot, ladder_service))