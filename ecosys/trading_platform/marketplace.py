from typing import List, AnyStr

from .market.stockmarket import StockMarket
from ..investments.share import ShareClass

class StockExchange:
    """Collection of markets
    """
    # TODO: This should be done by asset object!
    def __init__(self, *assets:List[AnyStr], name=None):
        
        self.name = name
        self._markets = {}
        for asset in assets:
            if not isinstance(asset, ShareClass):
                asset = ShareClass(asset)
            self._markets[asset] = StockMarket(asset)

    def __getitem__(self, asset):
        if isinstance(asset, str):
            asset_name = asset
            return [market for asset, market in self._markets.items() if asset.name == asset_name][0]
        else:
            return self._markets[asset]

    def __setitem__(self, asset):
        self._markets[asset] = StockMarket(asset)

    @property
    def securities(self):
        return set(self._markets.keys())