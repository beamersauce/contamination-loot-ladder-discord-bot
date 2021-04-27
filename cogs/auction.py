# import discord
import discord
from discord.ext import commands, tasks
import ladder
import random
import datetime
# import threading

class AuctionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auctions = {}
        # self.auction_channel = discord.utils.get(self.bot.get_all_channels(), name='ladder', type=discord.ChannelType.text)  
        self.auctionCheck.start()

    def cog_unload(self):
        self.auctionCheck.cancel()

    @commands.command(name='auction', pass_context=True)
    async def auction(self, ctx, item_name: str, seconds: int):
        #create an auction id
        id = random.randint(10000,99999)        

        #output to main channel the auction
        auction_channel = discord.utils.get(self.bot.get_all_channels(), name='ladder', type=discord.ChannelType.text)  
        self.auctions[item_name] = {"id": id, "name": item_name, "start_time": datetime.datetime.today(), "seconds": seconds, "bids": []}
        await auction_channel.send('Starting auction {} for "{}" lasting {} seconds'.format(id, item_name, seconds))
        await auction_channel.send('`$bid "{}"`'.format(item_name))
        print(self.auctions)

        #start auction timer
        # threading.Timer(seconds, self.endAuction, [item_name]).start()

    @commands.command(name='bid', pass_context=True)
    async def bid(self, ctx, item_name: str):
        name = ctx.author.display_name
        print('received bid for "{}" from {}'.format(item_name, name))
        if item_name in self.auctions:
            self.auctions[item_name]['bids'].append(name)
            await ctx.send('Successfully recorded bid on "{}"'.format(item_name))
        else:
            raise Exception('No auction with item name "{}" could be found, did you remember the quotes?'.format(item_name))

    @commands.command(name='print', pass_context=True)
    async def print(self, ctx):
        await ctx.send(self.auctions)

    @tasks.loop(seconds=10.0)
    async def auctionCheck(self):
        #loop over auctions to check if any have ended
        print('checking auctions {}'.format(self.auctions))
        now = datetime.datetime.today()
        #TODO need to pop auctions as i iterate
        for key in self.auctions:
            auction = self.auctions[key]
            if (now - auction['start_time']).total_seconds() > auction['seconds']:
                await self.endAuction(key)
    

    @auctionCheck.before_loop
    async def before_auctionCheck(self):
        await self.bot.wait_until_ready()

    async def endAuction(self, item_name: str):
        print('ending auction for {}'.format(item_name))
        auction_channel = discord.utils.get(self.bot.get_all_channels(), name='ladder', type=discord.ChannelType.text)          
        auction = self.auctions.pop(item_name)
        print(auction)
        # await auction_channel.send('Auction ended for "{}" the winner was {}'.format(item_name, winner))        


def setup(bot):
    bot.add_cog(AuctionCog(bot))