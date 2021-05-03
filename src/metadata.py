class Metadata:
    def __init__(self, spreadsheetmetadata, serverName, textChannel, attendanceChannel, adminRole):
        self.spreadsheetmetadata = spreadsheetmetadata
        self.serverName = serverName
        self.textChannel = textChannel
        self.attendanceChannel = attendanceChannel
        self.adminRole = adminRole

    def __str__(self):
        return 'Server Name: {}\nText Channel: {}\nAttendance Channel: {}\nAdmin Role: {}'.format(self.serverName, self.textChannel, self.attendanceChannel, self.adminRole)