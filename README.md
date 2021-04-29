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
admins - allow some commands to be admin only 
logging
error handling/messaging
record - if people aren't found put them on an 'upcoming list'
list rules
    drop users to 'upcoming' if they haven't raided in X days
    move users to ladder if they have 3 raids
set_channel <channel> - set channel for raid attendance and ladder/auction messages
handle nickname "* playername"