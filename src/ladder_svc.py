import ladder_dao
import player
import utils
import discord
import auction
import datetime

class LadderService:
    def __init__(self):
        self.activeLadder = ladder_dao.LadderDAO('1bw7PFkwSm4b9T57217PtKqk34zC43ZXKlZQrfDEYRvE', '0', 'Loot Ladder')
        self.inactiveLadder = ladder_dao.LadderDAO('1bw7PFkwSm4b9T57217PtKqk34zC43ZXKlZQrfDEYRvE', '1957720808', 'Upcoming Ladder')
        self.metadata = ladder_dao.LadderMetadataDAO('1bw7PFkwSm4b9T57217PtKqk34zC43ZXKlZQrfDEYRvE', '2023502702', 'BOT')
        self.auctions = {}

    def list(self):
        return self.activeLadder.get()

    def getPlayer(self, name: str):
        player = self.activeLadder.getByName(name)
        if None == player:
            raise Exception("No user found on ladder with name or discordName: {}".format(name))
        return player

    def getMetadata(self):
        return self.metadata.get()

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

    def recordAttendance(self, bot: discord.client, date: str):
        members = utils.getMembers(bot, self.getMetadata())
        players = []
        for name in members:
            try:
                player = self.getPlayer(name)
                player.raidDates.append(date)            
                players.append(player)            
                self.update(player)
            except Exception as err:            
                print('skipping recording {} error was: {}'.format(name, err))

        return players   

    def createAuction(self, item_name: str, seconds: int):
        if item_name in self.auctions:
            raise Exception('An auction already exists for {}'.format(item_name))
        auc = auction.Auction(item_name, datetime.datetime.today(), seconds, [])
        self.auctions[item_name] = auc
        return auc

    def bidOnAuction(self, item_name: str, name: str):
        player = self.getPlayer(name)
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
            await utils.sendToChannel(bot, self.getMetadata(), 'Auction ended for "{}" -- nobody bid'.format(item_name))            
        else:
            fullBids = self.getBids(auction.bids)
            winner = fullBids[0]   
            self.move(winner.name, len(self.list()))
            await utils.sendToChannel(bot, self.getMetadata(), 'Auction ended for "{}"'.format(item_name))
            await self.sendWinningMessage(bot, fullBids, winner)  

    def getBids(self, bids):
        fullBids = []
        for bid in bids:
            fullBids.append(self.activeLadder.getByName(bid))
        fullBids.sort(key=lambda player: player.position)
        return fullBids

    async def sendWinningMessage(self, bot, fullBids, winner):    
        bidString = ''
        for bid in fullBids:
            bidString += '\n{} - {}'.format(bid.name, bid.position)
        await utils.sendToChannel(bot, self.getMetadata(), '-- bids: --{}\n--------\nThe winner was {}, congratulations!\nSuicided {} to bottom of loot ladder (position {})'.format(bidString, winner.name, winner.name, bid.position))
    
    def getAuctions(self):
        return self.auctions

    #TODO
    def demote(self, name: str):
        print(self.activeLadder.get())
        print(self.inactiveLadder.get())