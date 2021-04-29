# util class for manipulating ladder
# EXPECTED SHEET FORMAT IS
# DISCORD NICKNAME | DISCORD NAME | MOST RECENT RAID | 2ND MOST RECENT RAID | 3RD MOST RECENT RAID


from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account 

SHEET_ID = '1bw7PFkwSm4b9T57217PtKqk34zC43ZXKlZQrfDEYRvE'
LADDER_SHEET_ID = '0'
# UPCOMING_SHEET_ID = '1957720808'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
credentials = service_account.Credentials.from_service_account_file('service.json', scopes=SCOPES)
service = build('sheets', 'v4' , credentials=credentials)
sheet = service.spreadsheets() 


def get():
    ladder = []
    result = sheet.values().get(spreadsheetId=SHEET_ID, range='Loot Ladder!A:E').execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
    else:
        for row in values:
            ladder.append(createPerson(row))

    return ladder

# def get_upcoming():
#     ladder = []
#     result = sheet.values().get(spreadsheetId=SHEET_ID,
#                             range='Upcoming Ladder!A:E').execute()
#     values = result.get('values', [])
#     if not values:
#         print('No data found.')
#     else:
#         for row in values:
#             ladder.append(createPerson(row))

#     return ladder


#TODO i should use a class for this
#utility function to turn sheet row into person object
def createPerson(row):
    name = row[0]
    raid_date_1 = '1/1/2021'
    raid_date_2 = '1/1/2021'
    raid_date_3 = '1/1/2021'
    #default to discord username if there is no nickname
    discordName = row[0] 
    if len(row) > 1:
        discordName = row[1]
    if (len(row) > 2):
        raid_date_1 = row[2]
    if (len(row) > 3):
        raid_date_2 = row[3]
    if (len(row) > 4):
        raid_date_3 = row[4]
    return {'name': name, 'discordName': discordName, 'raid_date_1': raid_date_1, 'raid_date_2': raid_date_2, 'raid_date_3': raid_date_3}

def length():
    return len(get())

def getPosition(name: str):
    try:
        return findIndex(name, get())
    except Exception:
        raise Exception("No user found on ladder with name or discordName: {}".format(name))

def findIndex(name: str, ladder):
    for i in range(len(ladder)):
        if ladder[i]['name'].lower() == name.lower() or ladder[i]['discordName'].lower() == name.lower():
            return i+1
    raise Exception("No user found on ladder with name or discordName: {}".format(name))

def move(name: str, position: int):
    ladder = get()
    index = findIndex(name, get())
    # if we are moving to a higher position, we need to add 1 to make room for us shifting out of our current position 
    # e.g. 2->5 is actually 2->6 because we'll slide back to 5
    if position > index:
        position += 1
    print("index: {} pos: {}".format(index, position))

    body = {
        "requests": [
            {
                "moveDimension": {
                    "source": {
                        "sheetId": LADDER_SHEET_ID,
                        "dimension": "ROWS",
                        "startIndex": index-1,
                        "endIndex": index
                    },
                    "destinationIndex": position-1
                }
            }
        ]
    }
    response = sheet.batchUpdate(spreadsheetId=SHEET_ID, body=body).execute()    

# TODO - the logic on this is actually fairly complicated I want to do this:
# 1. find a the user
#   1a. user is on ladder sheet
#       store sheet=ladder   
#   1b. if user is not on upcoming sheet
#        add user to sheet
#        store sheet=upcoming
#  2.  update date
#       if 
#           date in raid_date_1 is same, do nothing
#       else 
#           move raid_date_2 to raid_date_3
#           move raid_date_1 to raid_date_2
#           insert todays date in raid_date_1
def updateLastRaidDate(name: str, date: str):    
    ladder = get()
    index = findIndex(name, ladder)        

    # Skip if most recent raid time matches
    if date == ladder[index-1]['raid_date_1']:
        raise Exception('{} already had todays raid attendence recorded'.format(name))
    else:
        print('dates did not match, sliding {}'.format(date))
        #shift all raid dates over 1
        slideRaidDates(ladder, index, date)
   
# def addUserToUpcoming(name: str, date:str):    
#     body = {
#         "values": [
#             [name, '', date, '', '']
#         ]
#     }    
#     response = sheet.values().append(spreadsheetId=SHEET_ID, range='Upcoming Ladder!A:A', valueInputOption='USER_ENTERED', insertDataOption='INSERT_ROWS', body=body).execute()

def slideRaidDates(ladder, index, date):    
    person = ladder[index-1]
    #move 2 to 3
    body = {
        "values": [
            [person['raid_date_2']]
        ]
    }
    response = sheet.values().update(spreadsheetId=SHEET_ID, range='E{}'.format(index), valueInputOption='USER_ENTERED', body=body).execute()
    #move 1 to 2
    body = {
        "values": [
            [person['raid_date_1']]
        ]
    }
    response = sheet.values().update(spreadsheetId=SHEET_ID, range='D{}'.format(index), valueInputOption='USER_ENTERED', body=body).execute()
    #replace 1
    body = {
        "values": [
            [date]
        ]
    }
    response = sheet.values().update(spreadsheetId=SHEET_ID, range='C{}'.format(index), valueInputOption='USER_ENTERED', body=body).execute()
    