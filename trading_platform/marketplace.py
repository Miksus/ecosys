
from .market.stockmarket import StockMarket

class StockExchange:
    """Collection of markets
    """

    def __init__(self, assets:List[Asset], name=None):
        
        self.name = name
        self._markets = {}
        for asset in assets:
            self._markets[asset] = StockMarket(asset)

    def __getitem__(self, asset):
        return self._markets[asset]

    def __setitem__(self, asset):
        self._markets[asset] = StockMarket(asset)

    @property
    def securities(self):
        return set(self._markets.keys())