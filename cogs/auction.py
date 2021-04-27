# import discord
import discord
from discord.ext import commands
import ladder
import random
import datetime
import threading

class AuctionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auctions = {}

    @commands.command(name='auction', pass_context=True)
    async def auction(self, ctx, item_name: str, seconds: int):
        #create an auction id
        id = random.randint(10000,99999)        

        #output to main channel the auction
        auction_channel = discord.utils.get(self.bot.get_all_channels(), name='ladder', type=discord.ChannelType.text)  
        self.auctions[item_name] = {"id": id, "name": item_name, "start_time": datetime.datetime.today(), "bids": []}
        await auction_channel.send('Starting auction {} for "{}" lasting {} seconds'.format(id, item_name, seconds))
        await auction_channel.send('`$bid "{}"`'.format(item_name))
        print(self.auctions)

        #start auction timer
        threading.Timer(seconds, self.endAuction, [item_name]).start()

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

    async def endAuction(self, item_name: str):
        auction_channel = discord.utils.get(self.bot.get_all_channels(), name='ladder', type=discord.ChannelType.text)  
        await auction_channel.send('auction ended for {}'.format(item_name))


def setup(bot):
    bot.add_cog(AuctionCog(bot))