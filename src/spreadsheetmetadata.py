class SpreadsheetMetadata:
    def __init__(self, ladderSheetId, upcomingSheetId, metadataSheetId):
        self.ladderSheetId = ladderSheetId
        self.upcomingSheetId = upcomingSheetId
        self.metadataSheetId = metadataSheetId
 
    def __str__(self):
        return 'Ladder Sheet Id: {}\nUpcoming Sheet Id: {}\nMetdata Sheet Id: {}'.format(self.ladderSheetId, self.upcomingSheetId, self.metadataSheetId)