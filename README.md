commands:
help - show all commands
    set_channel <channel> - set channel to output to
move <name> <position> - move name to ladder position <pos>
drop <name> - move name to last ladder position
    export - dump list to gsheet
    import - read lsit to memory from gsheet
list - send list in PM to requestor
show ?<name> - send ladder position of name (or self) to requestor
    record ?<name> - read current attendee list of raid, default to current user
        TODO handle non-raiders


# AUTO- BID
auction "<item name>" <seconds> - start an auction for 'item name' for seconds duration
bid "<item name>" ?<name> - bid on <item name> with ladder position with option <name> or person bidding


