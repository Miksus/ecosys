
class Asset:
    def __init__(self):
        

class Investment:

    def __init__(self, asset:Asset, price, quantity):
        self.asset = asset
        self.price = price
        self.quantity = quantity


class Portfolio:


    def __init__(self, cash, ):
        self.cash = cash
        self._investments = None

    def __getitem__(self, asset):
        return self._investments[asset]

    def __setitem__(self, asset):
        self._investments[asset] = StockMarket(asset)