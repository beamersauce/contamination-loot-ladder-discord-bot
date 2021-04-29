from discord.ext import commands

class DMOnlyFailure(commands.CheckFailure):
    pass

class OfficerOnlyFailure(commands.CheckFailure):
    pass