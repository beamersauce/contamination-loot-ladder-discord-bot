import discord
import metadata
# import ladder_data
import datetime
import player
import ladder_svc

metadata = {}

def setMetadata(metadataToSet):
    global metadata
    metadata = metadataToSet

async def sendToChannel(bot, text: str):
    channel = discord.utils.get(bot.get_all_channels(), name=metadata.textChannel, type=discord.ChannelType.text)
    await channel.send(text)

def getServer(bot):        
    for guild in bot.guilds:
        if guild.name == metadata.serverName:
            return guild            
    raise Exception('No discord server found with name: {}'.format(metadata.serverName))

async def isOfficer(bot, name: str):   
    # TODO can I just cache the officers? periodically update the list? 
    # TODO how do i get around creating a new ladder service here
    # ladder_service = ladder_svc.LadderService()
    # guild = getServer(ladder_service.getMetadata())
    guild = getServer(bot)
    
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
        # if role.name == ladder_service.getMetadata().adminRole:
        if role.name == metadata.adminRole:
            return True

    #member does not have role, fail
    return False
            
def testName(nameToTest, playerName, discordNickName):
    nameToTest = nameToTest.lower()
    return (playerName.lower() == nameToTest or 
        (None != discordNickName and discordNickName.lower() == nameToTest))

def getDiscordNicknameFromDiscordName(bot, discordName: str):
    print('getting discord nickname for {}'.format(discordName))
    server = getServer(bot)
    for member in server.members:
        if discordName.lower() == member.name.lower():
            if None != member.nick:
                return member.nick
            #has no nickname
            return discordName
    return discordName

#given a player_name, map it to their nickname and find that discord server member so we can @mention them
def getDiscordMention(bot, player: player.Player):
    print('getting discord member for {}'.format(player))   
    if None == player.discordNickName:
         raise Exception('No player nickname for: {}'.format(player.name))
    server = getServer(bot)
    for member in server.members:
        print(member.nick)
        if None != member.nick and player.discordNickName.lower() == member.nick.lower():
            print('found {}'.format(member))
            return member
    raise Exception('No discord member found with nickname: {}'.format(player.discordNickName))

def getMembers(bot):
    raid_channel = discord.utils.get(bot.get_all_channels(), name=metadata.attendanceChannel, type=discord.ChannelType.voice)  
    members = []
    for member in raid_channel.members:         
        members.append(member.display_name) 
    return members

def getTodaysDate():
    return datetime.datetime.today().strftime('%m-%d-%Y')

def convertStringToDate(datestring: str):
    return datetime.datetime.strptime(datestring, '%m-%d-%Y')

def createPerson(row_number, row, ladderList: str):
    name = row[0]    
    discordName = name
    discordNickName = name
    raid_dates = []
    if len(row) > 1:
        discordNickName = row[1]        
    if (len(row) > 2):
        raid_dates = [x.strip() for x in row[2].split(',')]      
    return player.Player(name, discordNickName, row_number+1, raid_dates, ladderList)   