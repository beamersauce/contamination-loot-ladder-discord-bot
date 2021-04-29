import discord
from discord.ext import commands
import ladder_service
import typing
import error_types
import utils
from datetime import datetime

class LadderInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def isDM(ctx):
        if type(ctx.channel) is discord.DMChannel:
            return True
        raise error_types.DMOnlyFailure(ctx.channel.name)

    async def isOfficer(ctx):
        if await utils.isOfficer(ctx.bot, ctx.author.name):
            return True
        raise error_types.OfficerOnlyFailure(ctx.author.name)

    @commands.command(name='list', pass_context=True)
    @commands.check(isDM)
    async def list(self, ctx):
        players = ladder_service.listLadder()
        await ctx.send(self.prettyPrint(players))

    def prettyPrint(self, players):        
        message = "Current Loot Ladder:\n"
        for i in range(len(players)):
            message += str(players[i].position) + ' : ' + players[i].name + '\n'
        return message

    @commands.command(name='show', pass_context=True)
    @commands.check(isDM)
    async def show(self, ctx, name: typing.Optional[str]):
        if None == name:
            #get current user
            name = ctx.author.display_name
        print('finding player position for: ' + name)
        player = ladder_service.getByName(name)
        await ctx.send("{}'s position on the loot ladder is: {}".format(player.name, player.position))

    @commands.command(name='info', pass_context=True)
    @commands.check(isDM)
    @commands.check(isOfficer)
    async def info(self, ctx, name: typing.Optional[str]):
        metadata = utils.getMetadata()
        await ctx.send(str(metadata))

    @commands.command(name='drop', pass_context=True)
    @commands.check(isOfficer)
    async def drop(self, ctx, name: str):
        await self.move(ctx, name, len(ladder_service.listLadder()))        

    @commands.command(name='move', pass_context=True)
    @commands.check(isOfficer)
    async def move(self, ctx, name: str, position: int):
        requestor = ladder_service.getByName(ctx.author.name)
        player = ladder_service.move(name, position)
        await utils.sendToChannel(self.bot, '{} moved {} to ladder position {}'.format(requestor.name, player.name, player.position))        

    @commands.command(name='record', pass_context=True)
    @commands.check(isOfficer)
    async def record(self, ctx, name: typing.Optional[str], date: typing.Optional[str]):
        if None == date:
            date = utils.getTodaysDate()
        requestor = ladder_service.getByName(ctx.author.name)
        msg = requestor.name + " recorded Raid attendance on " + date + " for:\n"
        players = [];
        if None == name:            
            # update all members of voice channel
            players = ladder_service.recordAttendance(self.bot, date)        
        else:
            # update single player <name>
            player = ladder_service.getByName(name)
            player.raidDates.append(date)
            ladder_service.update(player)
            players.append(player)  

        for player in players:
            msg += player.name + "\n"

        await utils.sendToChannel(self.bot, msg) 

def setup(bot):
    bot.add_cog(LadderInfoCog(bot))