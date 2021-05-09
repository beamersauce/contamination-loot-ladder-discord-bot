How to connect bot to discord server:
1. nav to https://discord.com/developers/applications > go to LootLadder app
2. go to OAuth2 tab > 
    Scopes: [bot]
    Bot Permissions: [View Channels, Send Messages, Mention Everyone, Add Reactions, Connect]
3. Copy url in scopes box, give to server admin
4. click link > add to server > authorize

How to connect bot to google sheet:
    TODO (service.json crap)

commands:
# NORMAL
* help - show all commands
* move <name> <position> - move name to ladder position <pos>
* drop <name> - move name to last ladder position
* list - send list in PM to requestor
* show ?<name> - send ladder position of name (or self) to requestor
* record ?<name> - read current attendee list of raid, default to current user
        

# AUTO- BID
* auction "<item name>" <seconds> - start an auction for 'item name' for seconds duration
* bid "<item name>" ?<name> - bid on <item name> with ladder position with option <name> or person bidding

TODO:
logging
error handling/messaging
allow changing metadata
allow using playername or @discord_nickname_
customize bidding to potentially not autodrop winner? let ladder admin verify
allow bidding by adding reaction to auction?
should we show who has bid in live updates?
is there a way to map from input -> playername without me maintaining the list in excel
    input can be: playername, @discord_nickname, or @discord_name (dm's)
upgrade to slash commands instead of !