import discord
import ladder_dao
import utils
import datetime
import ladder_svc

class PlayerNameLookup:
    def __init__(self, ladderService, bot: discord.client):
        self.searchList = None 
        self.ladderService = ladderService
        self.bot = bot
        self.updateTime = datetime.datetime.now()
        self.updateIntervalInSeconds = 300 # 5 minutes

    def reloadSearchList(self):
        print('updating player search lookup')
        self.updateTime = datetime.datetime.now()
        newSearchList = {}
        # add active player names
        # add active player discord nicknames
        for ap in self.ladderService.list(True):
            apname = ap.name.lower()            
            print(apname)
            newSearchList[apname] = apname
            newSearchList[ap.discordNickName.lower()] = apname
        # add inactive player names
        # add inactive player discord nicknames
        for ip in self.ladderService.list(False):
            ipname = ip.name.lower()
            print(ipname)
            newSearchList[ipname] = ipname
            newSearchList[ip.discordNickName.lower()] = ipname
        # add discord names to search list
        server = utils.getServer(self.bot)
        print(server)
        for member in server.members:
            print(member)
            if None != member.nick:
                if member.nick.lower() in newSearchList:                
                    pn = newSearchList[member.nick.lower()]
                    newSearchList[member.nick.lower()] = pn
                    newSearchList[member.mention] = pn
                    newSearchList[member.name] = pn
        self.searchList = newSearchList
    
    def checkUpdate(self):
        time_since_last_update = (datetime.datetime.now() - self.updateTime).total_seconds()
        if None == self.searchList or time_since_last_update > self.updateIntervalInSeconds:            
            self.reloadSearchList()

    def findPlayerName(self, searchString: str):        
        self.checkUpdate()
        searchString = searchString.lower()
        print('searching for {} in lookup map'.format(searchString))
        if searchString in self.searchList:
            print('searched: {} found {}'.format(searchString, self.searchList[searchString]))
            return self.searchList[searchString]
        else:
            raise Exception('No known player name, discord name, or discord nickname: {}'.format(searchString))