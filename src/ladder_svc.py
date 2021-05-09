import ladder_dao
import player
import utils
import discord
import auction
import datetime
import utils
import playername_lookup

class LadderService:
    def __init__(self, activeLadder, inactiveLadder, metadata):
        self.activeLadder = activeLadder
        self.inactiveLadder = inactiveLadder
        self.metadata = metadata
        self.auctions = {}
        self.playerNameLookup = playername_lookup.PlayerNameLookup()

    def list(self):
        return self.activeLadder.get()

    def getPlayer(self, bot: discord.client, name: str, activeOnly:bool=True):
        #try to find server nickname from name first if one exists
        name = utils.getDiscordNicknameFromDiscordName(bot, name)
        player = self.activeLadder.getByName(name)
        if not activeOnly and None == player:
            player = self.inactiveLadder.getByName(name)
        if None == player:
            raise Exception("No user found on ladder with name or discordName: {}".format(name))
        return player

    def getMetadata(self):
        return self.metadata

    def move(self, name: str, newPosition: int):
        player = self.activeLadder.getByName(name)
        self.activeLadder.move(player.position, newPosition)
        player.position = newPosition
        return player

    def update(self, player: player.Player):
        #remove dupes
        player.raidDates = sorted(set(player.raidDates), reverse=True)
        player.raidDates = player.raidDates[0:5]
        self.activeLadder.overwrite(player)    

    def add(self, player: player.Player):
        #add player to inactive
        self.inactiveLadder.add(player)

    def recordAttendance(self, bot: discord.client, date: str, namesToRecord):   
        players = []     
        active = self.activeLadder.get()
        inactive = self.inactiveLadder.get()
        for name in namesToRecord:
            print('recording: {}'.format(name))
            #search active
            done = False
            print('searching active')
            for p in active:
                if utils.testName(name, p.name, p.discordNickName):
                    p = self.updateRaidDates(p, date)
                    self.activeLadder.overwrite(p)
                    players.append(p)
                    done = True
                    break
            if not done:            
                print('searching inactive')
                for p in inactive:                
                    if utils.testName(name, p.name, p.discordNickName):
                        p = self.updateRaidDates(p, date)
                        self.inactiveLadder.overwrite(p)
                        done = True
                        players.append(p)
                        break
                #player does not exist, need to create a new entry
                if not done:
                    position = len(inactive)+1
                    p = player.Player(name, name, position, [date], 'inactive')
                    print('new player: {}'.format(p))
                    self.add(p)
                    players.append(p)            
        return players  

    def updateRaidDates(self, player, date):
        player.raidDates.append(date)
        player.raidDates = sorted(set(player.raidDates), reverse=True)
        player.raidDates = player.raidDates[0:5]
        return player

    def createAuction(self, item_name: str, seconds: int):
        if item_name in self.auctions:
            raise Exception('An auction already exists for {}'.format(item_name))
        auc = auction.Auction(item_name, datetime.datetime.today(), seconds, [])
        self.auctions[item_name] = auc
        return auc

    def bidOnAuction(self, bot: discord.client, item_name: str, name: str):
        player = self.getPlayer(bot, name)
        print('received bid for "{}" from {}'.format(item_name, player.name))
        if item_name in self.auctions:
            self.auctions[item_name].bids.append(player.name)
            return True
        else:
            raise Exception('No auction with item name "{}" could be found, did you remember the quotes?'.format(item_name))

    async def checkForCompletedAuctions(self, bot:discord.client):
        completedAuctions = []
        #loop over auctions to check if any have ended                
        now = datetime.datetime.today()
        endingAuctions = []
        for key in self.auctions:
            auction = self.auctions[key]
            if (now - auction.startTime).total_seconds() > auction.seconds:
                endingAuctions.append(auction.itemName)
        for auction in endingAuctions:
            await self.endAuction(bot, auction)

    async def endAuction(self, bot, item_name: str):
        print('ending auction for {}'.format(item_name))
        auction = self.auctions.pop(item_name)    
        print(auction)
        # check for a winner
        if 0 == len(auction.bids):
            await utils.sendToChannel(bot, 'Auction ended for "{}" -- nobody bid'.format(item_name))            
        else:
            fullBids = self.getBids(auction.bids)
            winner = fullBids[0]
            endPosition = len(self.list())
            self.move(winner.name, endPosition)
            await utils.sendToChannel(bot, 'Auction ended for "{}"'.format(item_name))
            await self.sendWinningMessage(bot, fullBids, winner, endPosition)  

    def getBids(self, bids):
        fullBids = []
        for bid in bids:
            fullBids.append(self.activeLadder.getByName(bid))
        fullBids.sort(key=lambda player: player.position)
        return fullBids

    async def sendWinningMessage(self, bot, fullBids, winner, endPosition):    
        bidString = ''
        for bid in fullBids:
            bidString += '\n{} - {}'.format(bid.name, bid.position)
        await utils.sendToChannel(bot, '-- bids: --{}\n--------\nThe winner was {}, congratulations!\nSuicided {} to bottom of loot ladder (position {})'.format(bidString, winner.name, winner.name, endPosition))
    
    def getAuctions(self):
        return self.auctions

    #move name from active to inactive
    async def demote(self, bot: discord.client, name: str, ranByName: str):
        player = self.getPlayer(bot, name)
        if None == player:
            raise Exception('No player on active ladder named {}'.format(name))
        self.activeLadder.remove(player.position)
        self.inactiveLadder.add(player)
        await utils.sendToChannel(bot, '{} demoted {} off the loot ladder'.format(ranByName, name))

    #move name from inactive to active
    async def promote(self, bot, name: str, ranByName: str):
        player = self.inactiveLadder.getByName(name)
        if None == player:
            raise Exception('No player on inactive ladder named {}'.format(name))
        self.inactiveLadder.remove(player.position)
        self.activeLadder.add(player)
        await utils.sendToChannel(bot, '{} promoted {} onto loot ladder'.format(ranByName, name))

    async def checkEligible(self, bot, ranByName: str, auto: bool):
        max_days = 14
        participation_count = 3
        cutoff_date = datetime.datetime.today() - datetime.timedelta(days=max_days+1)
        print(cutoff_date)
        await self.checkPromotions(bot, ranByName, auto, cutoff_date, participation_count, max_days)
        await self.checkDemotions(bot, ranByName, auto, cutoff_date, participation_count, max_days)

    async def checkPromotions(self, bot, ranByName: str, auto: bool, cutoff_date: datetime.datetime, participation_count: int, max_days: int):
        upcoming_players = self.inactiveLadder.get()
        for player in upcoming_players:
            print('Testing player for promotion: {}'.format(player))
            count = 0
            for d in player.raidDates:
                dt = utils.convertStringToDate(d)
                if dt > cutoff_date:
                    count += 1
            if count >= participation_count:  
                await utils.sendToChannel(bot, 'Player {} is eligible for promotion, has attended {} raids in last {} days on dates: {}\n`!promote {}`'.format(player.name, count, max_days, player.raidDates, player.name))                    
                if auto:
                    await self.promote(bot, player.name, ranByName)                
    
    async def checkDemotions(self, bot, ranByName: str, auto: bool, cutoff_date: datetime.datetime, participation_count: int, max_days: int):
        active_players = self.activeLadder.get()
        for player in active_players:
            print('Testing player for demotion: {}'.format(player))
            count = 0
            for d in player.raidDates:
                dt = utils.convertStringToDate(d)
                if dt > cutoff_date:
                    count += 1
            if count < participation_count:  
                await utils.sendToChannel(bot, 'Player {} has not attended enough raids and should be demoted, attended {} raids in last {} days on dates: {}\n`!demote {}`'.format(player.name, count, max_days, player.raidDates, player.name))                    
                if auto:
                    await self.demote(bot, player.name, ranByName)   
    
    def test(self, bot):
        msg = 'active gsheet api calls: {}'.format(self.activeLadder.apicount)
        msg +='\ninactive gsheet api calls: {}'.format(self.inactiveLadder.apicount)
        # guild = utils.getServer(bot)
        # for member in guild.members:
        #     msg += '\nname: {} nick: {} mention: {}'.format(member.name, member.nick, member.mention)
        return msg

    