import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account 
import player
import utils
import metadata
import spreadsheetmetadata
ladder_sheet_name = 'Loot Ladder'
upcoming_sheet_name = 'Upcoming Ladder'
metadata_sheet_name = 'BOT'

class LadderDAO:
    def __init__(self, spreadsheetId, sheetId, sheetName):
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = service_account.Credentials.from_service_account_file('service.json', scopes=SCOPES)
        service = build('sheets', 'v4' , credentials=credentials)
        self.sheet = service.spreadsheets() 
        self.spreadsheetId = spreadsheetId
        self.sheetId = sheetId
        self.sheetName = sheetName

    def get(self):
        ladder = []
        result = self.sheet.values().get(spreadsheetId=self.spreadsheetId, range="'{}'!A:D".format(self.sheetName)).execute()
        values = result.get('values', [])
        if not values:
            print('No data found.')
        else:
            for i in range(len(values)):   
                ladder.append(utils.createPerson(i, values[i]))
        return ladder

    def getByName(self, name: str):
        players = self.get()
        for player in players:
            if utils.testName(name, player.name, player.discordName, player.discordNickName):
                return player
        return None

    def move(self, originalPosition: int, newPosition: int):
        if newPosition == originalPosition:
            return
        # if we are moving to a higher position, we need to add 1 to make room for us shifting out of our current position 
        # e.g. 2->5 is actually 2->6 because we'll slide back to 5
        if newPosition > originalPosition:
            newPosition += 1
        print("from: {} to: {}".format(originalPosition, newPosition))

        body = {
            "requests": [
                {
                    "moveDimension": {
                        "source": {
                            "sheetId": self.sheetId,
                            "dimension": "ROWS",
                            "startIndex": originalPosition-1,
                            "endIndex": originalPosition
                        },
                        "destinationIndex": newPosition-1
                    }
                }
            ]
        }
        response = self.sheet.batchUpdate(spreadsheetId=self.spreadsheetId, body=body).execute()

    def overwrite(self, player: player.Player):
        player.raidDates.sort(reverse=True)
        print('Updating: {}'.format(player))
        body = {
            "values": [
                [player.name, player.discordName, player.discordNickName, ', '.join(player.raidDates)]
            ]
        }
        range = "'{}'!{}:{}".format(self.sheetName, player.position,player.position)
        response = self.sheet.values().update(spreadsheetId=self.spreadsheetId, range=range, valueInputOption='USER_ENTERED', body=body).execute()



class LadderMetadataDAO:
    def __init__(self, spreadsheetId, sheetId, sheetName):
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = service_account.Credentials.from_service_account_file('service.json', scopes=SCOPES)
        service = build('sheets', 'v4' , credentials=credentials)
        self.sheet = service.spreadsheets()
        self.spreadsheetId = spreadsheetId
        self.sheetId = sheetId
        self.sheetName = sheetName

    def get(self):
        response = self.sheet.get(spreadsheetId=self.spreadsheetId).execute()
        ladder_id = 0
        upcoming_id = 0
        metadata_id = 0
        
        for s in response['sheets']:
            if s['properties']['title'] == ladder_sheet_name:
                ladder_id = s['properties']['sheetId']
            elif s['properties']['title'] == upcoming_sheet_name:
                upcoming_id = s['properties']['sheetId']
            elif s['properties']['title'] == metadata_sheet_name:
                metadata_id = s['properties']['sheetId']
                
        ssmeta = spreadsheetmetadata.SpreadsheetMetadata(ladder_id, upcoming_id, metadata_id)

        result = self.sheet.values().get(spreadsheetId=self.spreadsheetId, range='BOT!1:4').execute()
        values = result.get('values', [])
        if not values:
            print('No data found.')
        else:
            return metadata.Metadata(ssmeta, values[0][1],values[1][1],values[2][1],values[3][1])
