import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account 
import player
import utils
import metadata
import spreadsheetmetadata
import datetime

ladder_sheet_name = 'Loot Ladder'
upcoming_sheet_name = 'Upcoming Ladder'
metadata_sheet_name = 'BOT'

class LadderDAO:
    def __init__(self, spreadsheetId, sheetId, sheetName, metadata, ladderName):
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = service_account.Credentials.from_service_account_file('service.json', scopes=SCOPES)
        service = build('sheets', 'v4' , credentials=credentials)
        self.sheet = service.spreadsheets() 
        self.spreadsheetId = spreadsheetId
        self.sheetId = sheetId
        self.sheetName = sheetName
        self.metadata = metadata
        self.apicount = 0
        self.ladderName = ladderName

    def get(self):
        ladder = []
        self.apicount += 1
        result = self.sheet.values().get(spreadsheetId=self.spreadsheetId, range="'{}'!A:D".format(self.sheetName)).execute()
        values = result.get('values', [])
        if not values:
            print('No data found.')
        else:
            for i in range(len(values)):                   
                ladder.append(utils.createPerson(i, values[i], self.ladderName))
        return ladder

    def getByName(self, name: str):
        name = name.lower()
        players = self.get()
        for player in players:
            if name == player.name.lower():
            # if utils.testName(name, player.name, player.discordNickName):
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
        self.apicount += 1
        response = self.sheet.batchUpdate(spreadsheetId=self.spreadsheetId, body=body).execute()

    def overwrite(self, player: player.Player):
        player.raidDates.sort(reverse=True)
        print('Updating: {}'.format(player))
        body = {
            "values": [
                [player.name, player.discordNickName, ', '.join(player.raidDates)]
            ]
        }
        range = "'{}'!{}:{}".format(self.sheetName, player.position, player.position)
        self.apicount += 1
        response = self.sheet.values().update(spreadsheetId=self.spreadsheetId, range=range, valueInputOption='USER_ENTERED', body=body).execute()
    
    def remove(self, position: int):
        print('removing row {} from {}'.format(position, self.sheetName))
        body = {
            "requests": [
                {
                    "deleteDimension": {
                        "range": {
                            "sheetId": self.sheetId,
                            "dimension": "ROWS",
                            "startIndex": position-1,
                            "endIndex": position
                        }
                    }
                }
            ]
        }
        self.apicount += 1
        response = self.sheet.batchUpdate(spreadsheetId=self.spreadsheetId, body=body).execute()

    def add(self, player: player.Player):
        position = len(self.get())+1
        print('adding player {} to {} in position {}'.format(player.name, self.sheetName, position))
        body = {
            "values": [
                [player.name, player.discordNickName, ', '.join(player.raidDates)]
            ]
        }
        range = "'{}'!{}:{}".format(self.sheetName, position, position)
        self.apicount += 1
        response = self.sheet.values().update(spreadsheetId=self.spreadsheetId, range=range, valueInputOption='USER_ENTERED', body=body).execute()


# class LadderMetadataDAO:
#     def __init__(self, spreadsheetId, sheetId, sheetName):
#         SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
#         credentials = service_account.Credentials.from_service_account_file('service.json', scopes=SCOPES)
#         service = build('sheets', 'v4' , credentials=credentials)
#         self.sheet = service.spreadsheets()
#         self.spreadsheetId = spreadsheetId
#         self.sheetId = sheetId
#         self.sheetName = sheetName
#         self.storedMetadata = None
#         self.updateTime = datetime.datetime.now()

#     def get(self):
#         time_since_last_update = (datetime.datetime.now() - self.updateTime).total_seconds()
#         if self.storedMetadata == None or time_since_last_update > 60:
#             print('retrieving updated metadata')
#             response = self.sheet.get(spreadsheetId=self.spreadsheetId).execute()
#             ladder_id = 0
#             upcoming_id = 0
#             metadata_id = 0
            
#             for s in response['sheets']:
#                 if s['properties']['title'] == ladder_sheet_name:
#                     ladder_id = s['properties']['sheetId']
#                 elif s['properties']['title'] == upcoming_sheet_name:
#                     upcoming_id = s['properties']['sheetId']
#                 elif s['properties']['title'] == metadata_sheet_name:
#                     metadata_id = s['properties']['sheetId']
                    
#             ssmeta = spreadsheetmetadata.SpreadsheetMetadata(ladder_id, upcoming_id, metadata_id)

#             result = self.sheet.values().get(spreadsheetId=self.spreadsheetId, range='BOT!1:6').execute()
#             values = result.get('values', [])
#             if not values:
#                 print('No data found.')
#             else:
#                 self.storedMetadata = metadata.Metadata(ssmeta, values[0][1],values[1][1],values[2][1],values[3][1],values[4][1],values[5][1])
#                 self.updateTime = datetime.datetime.now()
#         utils.setMetadata(self.storedMetadata)
#         return self.storedMetadata
