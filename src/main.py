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
import playername_lookup

# METADATA - burch server
google_spreadsheet_id = '1bw7PFkwSm4b9T57217PtKqk34zC43ZXKlZQrfDEYRvE'
google_ladder_sheet_id = '0'
google_upcoming_sheet_id = '1957720808'
google_metadata_sheet_id = '2023502702'
discord_server_name = "burch's server"
discord_text_channel = 'ladder'
discord_voice_channel = 'raid'
discord_role_name = 'ladder admin'
raids_per_period = 3
period_in_days = 14
# END METADATA
# METADATA - contam
# google_spreadsheet_id = '1bw7PFkwSm4b9T57217PtKqk34zC43ZXKlZQrfDEYRvE'
# google_ladder_sheet_id = '0'
# google_upcoming_sheet_id = '1957720808'
# google_metadata_sheet_id = '2023502702'
# discord_server_name = "FrozenGaming"
# discord_text_channel = 'lootladdertest'
# discord_voice_channel = 'RAID'
# discord_role_name = 'LootLadder'
# raids_per_period = 3
# period_in_days = 14
# END METADATA

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
metadata = metadata.Metadata(spreadsheetmetadata.SpreadsheetMetadata('Loot Ladder', 'Upcoming Ladder', 'BOT'), discord_server_name, discord_text_channel, discord_voice_channel, discord_role_name, raids_per_period, period_in_days)
utils.setMetadata(metadata)
activeLadder = ladder_dao.LadderDAO(google_spreadsheet_id, google_ladder_sheet_id, 'Loot Ladder', metadata, 'active')
inactiveLadder = ladder_dao.LadderDAO(google_spreadsheet_id, google_upcoming_sheet_id, 'Upcoming Ladder', metadata, 'inactive')
# metadata = ladder_dao.LadderMetadataDAO(google_spreadsheet_id, google_metadata_sheet_id, 'BOT', utils)
ladder_service = ladder_svc.LadderService(activeLadder, inactiveLadder, metadata, bot)

# bot.load_extension("cogs.ladder")
# bot.load_extension("cogs.auction")
cogs.ladder.setup(bot, ladder_service)
cogs.auction.setup(bot, ladder_service)
bot.load_extension("cogs.error")

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    metadata = ladder_service.getMetadata()
    print(metadata)

#run the client
discord_key = open('discord.key', 'r').read()
bot.run(discord_key, bot=True, reconnect=True)