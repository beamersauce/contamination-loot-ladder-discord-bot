import discord
from discord.ext import commands
import utils
import metadata

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
#todo can we just load all cogs automatically?
bot.load_extension("cogs.ladder")
# bot.load_extension("cogs.move")
# bot.load_extension("cogs.record")
bot.load_extension("cogs.auction")
bot.load_extension("cogs.error")

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    metadata = utils.getMetadata()
    print(metadata)

#run the client
discord_key = open('discord.key', 'r').read()
bot.run(discord_key, bot=True, reconnect=True)