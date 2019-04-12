from typing import List, AnyStr

from .matcher.stockmarket import StockMatcher
from ..investments.share import ShareClass

class StockExchange:
    """Collection of markets
    """
    # TODO: This should be done by asset object!
    def __init__(self, *stocks:List[AnyStr], name=None):
        
        self.name = name
        self._stocks = {
            ShareClass(stock) if not isinstance(stock, ShareClass)
            else stock
            for stock in stocks
        }
        self.index = 0

    def __getitem__(self, stock):
        if isinstance(asset, str):
            stock_name = stock
            return [stock for stock in self._stocks if stock.name == stock_name][0]
        else:
            raise NotImplemented

    def __iter__(self):
        return self

    def __iter__(self):
        return iter(self._stocks)


    @property
    def securities(self):
        return set(self._markets.keys())