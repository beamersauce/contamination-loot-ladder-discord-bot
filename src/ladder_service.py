import ladder_data
import player
import utils
import discord
import auction
import datetime

auctions = {}

def listLadder():
    return ladder_data.get()

def getByName(name: str):
    player = ladder_data.getByName(name)
    if None == player:
        raise Exception("No user found on ladder with name or discordName: {}".format(name))
    return player

def move(name: str, newPosition: int):
    player = getByName(name)
    ladder_data.move(player.position, newPosition)
    player.position = newPosition
    return player
    
def recordAttendance(bot: discord.client, date: str):
    members = utils.getMembers(bot)
    players = []
    for name in members:
        try:
            player = getByName(name)
            player.raidDates.append(date)            
            players.append(player)            
            update(player)
        except Exception as err:            
            print('skipping recording {} error was: {}'.format(name, err))

    return players          
        
def update(player: player.Player):
    #remove dupes
    player.raidDates = sorted(set(player.raidDates), reverse=True)
    ladder_data.overwrite(player)    

def createAuction(item_name: str, seconds: int):
    if item_name in auctions:
        raise Exception('An auction already exists for {}'.format(item_name))
    auc = auction.Auction(item_name, datetime.datetime.today(), seconds, [])
    auctions[item_name] = auc
    return auc

def bidOnAuction(item_name: str, name: str):
    player = getByName(name)
    print('received bid for "{}" from {}'.format(item_name, player.name))
    if item_name in auctions:
        auctions[item_name].bids.append(player.name)
        return True
    else:
        raise Exception('No auction with item name "{}" could be found, did you remember the quotes?'.format(item_name))
    
def getAuctions():
    return auctions

async def checkForCompletedAuctions(bot):
    completedAuctions = []
    #loop over auctions to check if any have ended                
    now = datetime.datetime.today()
    endingAuctions = []
    for key in auctions:
        auction = auctions[key]
        if (now - auction.startTime).total_seconds() > auction.seconds:
            endingAuctions.append(auction.itemName)
    for auction in endingAuctions:
        await endAuction(bot, auction)            

async def endAuction(bot, item_name: str):
    print('ending auction for {}'.format(item_name))
    auction = auctions.pop(item_name)    
    print(auction)
    # check for a winner
    if 0 == len(auction.bids):
        await utils.sendToChannel(bot, 'Auction ended for "{}" -- nobody bid'.format(item_name))            
    else:
        fullBids = getBids(auction.bids)
        winner = fullBids[0]   
        move(winner.name, len(listLadder()))
        await utils.sendToChannel(bot, 'Auction ended for "{}"'.format(item_name))
        await sendWinningMessage(bot, fullBids, winner)        

def getBids(bids):
    fullBids = []
    for bid in bids:
        fullBids.append(ladder_data.getByName(bid))
    fullBids.sort(key=lambda player: player.position)
    return fullBids

async def sendWinningMessage(bot, fullBids, winner):    
    bidString = ''
    for bid in fullBids:
        bidString += '\n{} - {}'.format(bid.name, bid.position)
    await utils.sendToChannel(bot, '-- bids: --{}\n--------\nThe winner was {}, congratulations!\nSuicided {} to bottom of loot ladder'.format(bidString, winner.name, winner.name))