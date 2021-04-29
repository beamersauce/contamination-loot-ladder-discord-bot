import discord
import metadata
import ladder_data
import datetime

metadata = None

async def sendToChannel(bot, text: str):
    channel = discord.utils.get(bot.get_all_channels(), name=getMetadata().textChannel, type=discord.ChannelType.text)
    await channel.send(text)

async def isOfficer(bot, name: str):
    #find server
    server = None
    for guild in bot.guilds:
        if guild.name == getMetadata().serverName:
            server = guild
            break
    if None == server:
        raise Exception('No discord server found with name: {}'.format(getMetadata().serverName))
    
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
        if role.name == getMetadata().adminRole:
            return True

    #member does not have role, fail
    return False
            
def testName(nameToTest, playerName, discordName, discordNickName):
    nameToTest = nameToTest.lower()
    return (playerName.lower() == nameToTest or 
        (None != discordName and discordName.lower() == nameToTest) or
        (None != discordNickName and discordNickName.lower() == nameToTest))

def getMembers(bot):
    raid_channel = discord.utils.get(bot.get_all_channels(), name=getMetadata().attendanceChannel, type=discord.ChannelType.voice)  
    members = []
    for member in raid_channel.members:         
        members.append(member.display_name) 
    return members

#grab all the metadata needed to run this app and store it
def getMetadata():
    global metadata
    if None == metadata:
        metadata = ladder_data.readMetadata()
    return metadata

def getTodaysDate():
    return datetime.datetime.today().strftime('%m-%d-%Y')