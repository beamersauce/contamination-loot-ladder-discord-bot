# util class for manipulating ladder
# EXPECTED SHEET FORMAT IS
# PLAYER NAME | DISCORD NAME | DISCORD NICKNAME | RAID DATES

from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account 
import player
import utils
import metadata
import spreadsheetmetadata

SHEET_ID = '1bw7PFkwSm4b9T57217PtKqk34zC43ZXKlZQrfDEYRvE'
LADDER_SHEET_ID = '0'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
credentials = service_account.Credentials.from_service_account_file('service.json', scopes=SCOPES)
service = build('sheets', 'v4' , credentials=credentials)
sheet = service.spreadsheets() 
ladder_sheet_name = 'Loot Ladder'
upcoming_sheet_name = 'Upcoming Ladder'
metadata_sheet_name = 'BOT'


def createPerson(row_number, row):    
    name = row[0]    
    discordName = name
    discordNickName = name
    raid_dates = []
    if len(row) > 1:
        discordName = row[1]
    if (len(row) > 2):
        discordNickName = row[2]
    if (len(row) > 3):
        raid_dates = [x.strip() for x in row[3].split(',')]    
    return player.Player(name, discordName, discordNickName, row_number+1, raid_dates)    

def getByName(name: str):
    players = get()
    for player in players:
        if utils.testName(name, player.name, player.discordName, player.discordNickName):
            return player
    return None

def move(originalPosition: int, newPosition: int):
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
                        "sheetId": LADDER_SHEET_ID,
                        "dimension": "ROWS",
                        "startIndex": originalPosition-1,
                        "endIndex": originalPosition
                    },
                    "destinationIndex": newPosition-1
                }
            }
        ]
    }
    response = sheet.batchUpdate(spreadsheetId=SHEET_ID, body=body).execute()        

def overwrite(player: player.Player):
    player.raidDates.sort(reverse=True)
    print('Updating: {}'.format(player))
    body = {
        "values": [
            [player.name, player.discordName, player.discordNickName, ', '.join(player.raidDates)]
        ]
    }
    range = '{}:{}'.format(player.position,player.position)
    response = sheet.values().update(spreadsheetId=SHEET_ID, range=range, valueInputOption='USER_ENTERED', body=body).execute()

def readMetadata():    
    result = sheet.values().get(spreadsheetId=SHEET_ID, range='BOT!1:4').execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
    else:
        return metadata.Metadata(values[0][1],values[1][1],values[2][1],values[3][1])

def getSheetName(ladder):
    sheet = ladder_sheet_name
    if not ladder:
        sheet = upcoming_sheet_name
    return sheet

def get(ladder=True):
    sheetName = getSheetName(ladder)
    ladder = []
    result = sheet.values().get(spreadsheetId=SHEET_ID, range="'{}'!A:D".format(sheetName)).execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
    else:
        for i in range(len(values)):   
            ladder.append(createPerson(i, values[i]))

    return ladder

def getByName(name: str, ladder=True):
    players = get(ladder)
    for player in players:
        if utils.testName(name, player.name, player.discordName, player.discordNickName):
            return player
    return None

def switchSheets(name, position, moveToLadder=True):    
    sheetNameToMoveTo = getSheetName(moveToLadder)
    print('moving {} to {} in position {}'.format(name, sheetNameToMoveTo, position))
    # sheetNameToMoveFrom = getSheetName(not sheetToMoveTo)
    player = getByName(name, not moveToLadder)
    print(player)
    remove(position, moveToLadder)

def remove(position: int, ladder: bool):
    sheetMetadata = getSheetMetdata()
    print(sheetMetadata)
    sheetToRemoveFrom = getSheetName(ladder)
    #TODO need to get sheet ids by name
    # body = {
    #     "requests": [
    #         {
    #             "deleteDimension": {
    #                 "source": {
    #                     "sheetId": LADDER_SHEET_ID,
    #                     "dimension": "ROWS",
    #                     "startIndex": position-1,
    #                     "endIndex": position
    #                 }
    #             }
    #         }
    #     ]
    # }
    # response = sheet.batchUpdate(spreadsheetId=SHEET_ID, body=body).execute()    

def getSheetMetdata():
    response = sheet.get(spreadsheetId=SHEET_ID).execute()
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
    return spreadsheetmetadata.SpreadsheetMetadata(ladder_id, upcoming_id, metadata_id)