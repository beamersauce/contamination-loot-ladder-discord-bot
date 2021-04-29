class Player:
    def __init__(self, name, discordName, discordNickName, position, raidDates):
        self.name = name
        self.discordName = discordName
        self.discordNickName = discordNickName
        self.position = position
        self.raidDates = raidDates

    def __str__(self):
        return 'Name: {}\t DiscordName: {}\t DiscordNickName: {}\t Position: {}\t RaidDates: {}'.format(self.name, self.discordName, self.discordNickName, self.position, self.raidDates)