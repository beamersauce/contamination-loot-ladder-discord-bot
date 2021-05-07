import discord
from discord.ext import commands
import utils
import metadata
import ladder_svc
import ladder_dao
import cogs.auction
import cogs.ladder
import utils
import spreadsheetmetadata


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
metadata = metadata.Metadata(spreadsheetmetadata.SpreadsheetMetadata('Loot Ladder', 'Upcoming Ladder', 'BOT'), "burch's server", 'ladder', 'raid', 'ladder admin', 3, 14)
utils.setMetadata(metadata)
activeLadder = ladder_dao.LadderDAO('1bw7PFkwSm4b9T57217PtKqk34zC43ZXKlZQrfDEYRvE', '0', 'Loot Ladder', metadata, 'active')
inactiveLadder = ladder_dao.LadderDAO('1bw7PFkwSm4b9T57217PtKqk34zC43ZXKlZQrfDEYRvE', '1957720808', 'Upcoming Ladder', metadata, 'inactive')
# metadata = ladder_dao.LadderMetadataDAO('1bw7PFkwSm4b9T57217PtKqk34zC43ZXKlZQrfDEYRvE', '2023502702', 'BOT', utils)
ladder_service = ladder_svc.LadderService(activeLadder, inactiveLadder, metadata)

# bot.load_extension("cogs.ladder")
# bot.load_extension("cogs.auction")
cogs.ladder.setup(bot, ladder_service)
cogs.auction.setup(bot, ladder_service)
bot.load_extension("cogs.error")

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    # ladder_service = ladder_svc.LadderService()
    metadata = ladder_service.getMetadata()
    print(metadata)

#run the client
discord_key = open('discord.key', 'r').read()
bot.run(discord_key, bot=True, reconnect=True)