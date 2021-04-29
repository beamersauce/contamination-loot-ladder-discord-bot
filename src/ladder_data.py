# util class for manipulating ladder
# EXPECTED SHEET FORMAT IS
# DISCORD NICKNAME | DISCORD NAME | MOST RECENT RAID | 2ND MOST RECENT RAID | 3RD MOST RECENT RAID


from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account 
import player
import utils
import metadata

SHEET_ID = '1bw7PFkwSm4b9T57217PtKqk34zC43ZXKlZQrfDEYRvE'
LADDER_SHEET_ID = '0'
# UPCOMING_SHEET_ID = '1957720808'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
credentials = service_account.Credentials.from_service_account_file('service.json', scopes=SCOPES)
service = build('sheets', 'v4' , credentials=credentials)
sheet = service.spreadsheets() 


def get():
    ladder = []
    result = sheet.values().get(spreadsheetId=SHEET_ID, range='Loot Ladder!A:F').execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
    else:
        for i in range(len(values)):        
            ladder.append(createPerson(i, values[i]))

    return ladder

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
        raid_dates.append(row[3])
    if (len(row) > 4):
        raid_dates.append(row[4])
    if (len(row) > 5):
        raid_dates.append(row[5])
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
    #force 3 raid dates just in case, this is lazy/bad
    player.raidDates.append('')
    player.raidDates.append('')
    player.raidDates.append('')
    player.raidDates.sort(reverse=True)
    print('Updating: {}'.format(player))
    body = {
        "values": [
            [player.name, player.discordName, player.discordNickName, player.raidDates[0], player.raidDates[1], player.raidDates[2]]
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