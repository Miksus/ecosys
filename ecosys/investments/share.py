
from .asset import Asset
from ..trading_platform.market.stockmarket import StockMarket as ShareClassMarket
class ShareClass(Asset):

    def __init__(self, name, ticker, market=None):
        self.name = name
        self.ticker = ticker
        if market is None:
            market = ShareClassMarket()
        self.market = market