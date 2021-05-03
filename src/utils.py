import discord
import metadata
# import ladder_data
import datetime
import player
import ladder_svc

metadata = None

async def sendToChannel(bot, metadata, text: str):
    channel = discord.utils.get(bot.get_all_channels(), name=metadata.textChannel, type=discord.ChannelType.text)
    await channel.send(text)

def getServer(bot, metadata):        
    for guild in bot.guilds:
        if guild.name == metadata.serverName:
            return guild            
    raise Exception('No discord server found with name: {}'.format(getMetadata().serverName))

async def isOfficer(bot, name: str):
    ladder_service = ladder_svc.LadderService()
    guild = getServer(bot, ladder_service.getMetadata())
    
    #find requestor
    requestor = None
    for member in guild.members:
        if name.lower() == member.name.lower() or (None != member.nick and name.lower() == member.nick.lower()):
            requestor = member;
            break;
    if None == requestor:
        raise Exception('No player found with name: {}'.format(name))

    #check if requestor has role
    for role in requestor.roles:
        if role.name == ladder_service.getMetadata().adminRole:
            return True

    #member does not have role, fail
    return False
            
def testName(nameToTest, playerName, discordName, discordNickName):
    nameToTest = nameToTest.lower()
    return (playerName.lower() == nameToTest or 
        (None != discordName and discordName.lower() == nameToTest) or
        (None != discordNickName and discordNickName.lower() == nameToTest))

def getDiscordMember(bot, ladder_service, name: str):
    print('getting discord member for {}'.format(name))
    server = getServer(bot, ladder_service)
    for member in server.members:
        if name.lower() == member.name.lower():
            return member
    raise Exception('No discord member found with name: {}'.format(name))

def getMembers(bot, metadata):
    raid_channel = discord.utils.get(bot.get_all_channels(), name=metadata.attendanceChannel, type=discord.ChannelType.voice)  
    members = []
    for member in raid_channel.members:         
        members.append(member.display_name) 
    return members

#grab all the metadata needed to run this app and store it
# def getMetadata():
#     global metadata
#     if None == metadata:
#         metadata = ladder_data.readMetadata()
#     return metadata

def getTodaysDate():
    return datetime.datetime.today().strftime('%m-%d-%Y')

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