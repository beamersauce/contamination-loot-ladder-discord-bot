import discord
from discord.ext import commands
# import ladder_service
import typing
import error_types
import utils
from datetime import datetime
import ladder_svc

class LadderInfoCog(commands.Cog, name='Ladder Info'):
    def __init__(self, bot, ladder_service: ladder_svc.LadderService):
        self.bot = bot
        self.ladder_service = ladder_service

    def isDM(ctx):
        if type(ctx.channel) is discord.DMChannel:
            return True
        raise error_types.DMOnlyFailure(ctx.channel.name)

    async def isOfficer(ctx):
        if await utils.isOfficer(ctx.bot, ctx.author.name):
            return True
        raise error_types.OfficerOnlyFailure(ctx.author.name)

    @commands.command(name='list', pass_context=True, brief='display loot ladder', description='displays the current loot ladder')
    @commands.check(isDM)
    async def list(self, ctx):
        players = self.ladder_service.list()
        await ctx.send(self.prettyPrint(players))

    def prettyPrint(self, players):        
        message = "Current Loot Ladder:\n"
        for i in range(len(players)):
            message += str(players[i].position) + ' : ' + players[i].name + '\n'
        return message

    @commands.command(name='show', pass_context=True, brief='show player ladder position', description='displays the current loot ladder position of a person')
    @commands.check(isDM)
    async def show(self, ctx, name: typing.Optional[str]):
        if None == name:
            #get current user
            name = ctx.author.display_name
        print('finding player position for: ' + name)
        player = self.ladder_service.getPlayer(self.bot, name)
        print(player)
        await ctx.send("{}'s position on the loot ladder is: {}".format(player.name, player.position))

    @commands.command(name='info', pass_context=True, brief='show server info', description='displays the server metadata')
    @commands.check(isDM)
    @commands.check(isOfficer)
    async def info(self, ctx, name: typing.Optional[str]):
        metadata = self.ladder_service.getMetadata()
        await ctx.send(str(metadata))

    @commands.command(name='drop', pass_context=True, brief='move player to bottom of ladder', description='drops a player to the bottom of the loot ladder')
    @commands.check(isOfficer)
    async def drop(self, ctx, name):
        print('dropping {}'.format(name))
        await self.move(ctx, name, len(self.ladder_service.list()))        

    @commands.command(name='move', pass_context=True, brief='move player to specific ladder position', description='moves a player to a specific loot ladder position')
    @commands.check(isOfficer)
    async def move(self, ctx, name, position: int):
        maxPosition = len(self.ladder_service.list())
        if position > maxPosition:
            raise Exception('Request to move to position {} is greater than the end of the list at position {}'.format(position, maxPosition))
        requestor = self.ladder_service.getPlayer(self.bot, ctx.author.name)
        player = self.ladder_service.getPlayer(self.bot, name)
        #TODO change move to take player instead of name
        player = self.ladder_service.move(name, position)
        movedName = player.name
        try:
            movedName = utils.getDiscordMention(self.bot, player).mention
        except Exception as err:
            print(err)
            # pass
        await utils.sendToChannel(self.bot, '{} moved {} to ladder position {}'.format(ctx.author.mention, movedName, player.position))        

    @commands.command(name='record', pass_context=True, brief='record raid participation', description='records everyone in a voice channel as being a raider this day')
    @commands.check(isOfficer)
    async def record(self, ctx, name: typing.Optional[str], date: typing.Optional[str]):
        if None == date:
            date = utils.getTodaysDate()
        requestor = self.ladder_service.getPlayer(self.bot, ctx.author.name, False)
        msg = requestor.name + " recorded Raid attendance on " + date + " for:\n"
        namesToRecord = []
        if None == name:            
            # update all members of voice channel
            namesToRecord = utils.getMembers(self.bot)                
        else:
            #update only the given player
            namesToRecord.append(name)
        players = self.ladder_service.recordAttendance(self.bot, date, namesToRecord)
        for player in players:
            msg += player.name + "\n"
        await utils.sendToChannel(self.bot, msg) 
        await self.check(ctx, False)

    @commands.command(name='demote', pass_context=True, brief='remove player from loot ladder', description='remove player from loot ladder and put them on upcoming loot ladder')    
    @commands.check(isOfficer)
    async def demote(self, ctx, name: str):        
        await self.ladder_service.demote(self.bot, name, ctx.author.display_name)        

    @commands.command(name='promote', pass_context=True, brief='add player to loot ladder', description='add player to loot ladder from upcoming loot ladder')    
    @commands.check(isOfficer)
    async def promote(self, ctx, name: str):        
        await self.ladder_service.promote(self.bot, name, ctx.author.display_name)        

    @commands.command(name='check', pass_context=True, brief='checks if anybody is eligible to be promoted', description='checks the upcoming loot ladder for anybody matching loot ladder eligibility requirements')    
    @commands.check(isOfficer)
    async def check(self, ctx, auto=False):                
        await self.ladder_service.checkEligible(self.bot, ctx.author.display_name, auto)

    @commands.command(name='test', pass_context=True, brief='test', description='test')    
    @commands.check(isOfficer)
    async def test(self, ctx, auto=False):                
        msg = self.ladder_service.test(self.bot)
        await ctx.send(msg)

def setup(bot, ladder_service: ladder_svc.LadderService):
    bot.add_cog(LadderInfoCog(bot, ladder_service))