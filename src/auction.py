class Auction:
    def __init__(self, itemName, startTime, seconds, bids):
        self.itemName = itemName
        self.startTime = startTime
        self.seconds = seconds
        self.bids = bids

    def __str__(self):
        return 'ItemName: {}\t StartTime: {}\t Seconds: {}\t Bids: {}'.format(self.itemName, self.startTime, self.seconds, self.bids)