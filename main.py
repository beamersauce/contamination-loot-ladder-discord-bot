import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents)
#todo can we just load all cogs automatically?
bot.load_extension("cogs.list")
bot.load_extension("cogs.move")
bot.load_extension("cogs.record")
bot.load_extension("cogs.show")
bot.load_extension("cogs.auction")
bot.load_extension("cogs.error")

#run the client
bot.run('', bot=True, reconnect=True)