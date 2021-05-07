class Metadata:
    def __init__(self, spreadsheetmetadata, serverName, textChannel, attendanceChannel, adminRole, raidsPerPeriod, raidPeriodDays):
        self.spreadsheetmetadata = spreadsheetmetadata
        self.serverName = serverName
        self.textChannel = textChannel
        self.attendanceChannel = attendanceChannel
        self.adminRole = adminRole
        self.raidsPerPeriod = raidsPerPeriod
        self.raidPeriodDays = raidPeriodDays

    def __str__(self):
        return 'Server Name: {}\nText Channel: {}\nAttendance Channel: {}\nAdmin Role: {}\nRaids per Period: {}\nRaids period (days): {}'.format(self.serverName, self.textChannel, self.attendanceChannel, self.adminRole, self.raidsPerPeriod, self.raidPeriodDays)