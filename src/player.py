class Player:
    def __init__(self, name, discordNickName, position, raidDates, ladderList):
        self.name = name
        self.discordNickName = discordNickName
        self.position = position
        self.raidDates = raidDates
        self.ladderList = ladderList

    def __str__(self):
        return 'Name: {}\t DiscordNickName: {}\t Position: {}\t RaidDates: {}\t LadderList: {}'.format(self.name, self.discordNickName, self.position, self.raidDates, self.ladderList)