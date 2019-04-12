
from .asset import Asset
from ..trading_platform.matcher.stockmarket import StockMatcher as ShareClassMarket
class ShareClass(Asset):

    def __init__(self, name, ticker, market=None):
        self.name = name
        self.ticker = ticker
        if market is None:
            market = ShareClassMarket()
        self.market = market

    @property
    def price(self):
        return self.market.last_price