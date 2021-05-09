class PlayerNameLookup:
    def __init__():
        self.playerNames = []
        self.discordNameLookup = {}
        self.discordNicknameLookup = {}

    def findPlayerName(searchString: str):
        searchString = searchString.lower()
        # TODO i can just merge all the dictionaries together 
        # so i only have to perform 1 search
        #search by player name
        if searchString in self.playerNames:
            return searchString
        #search by discord name
        if searchString in self.discordNameLookup:
            return self.discordNameLookup[searchString]
        #search by discord nickname
        if searchString in self.discordNicknameLookup:
            return self.discordNicknameLookup[searchString]