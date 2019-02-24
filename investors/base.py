

from collections import Counter



class Investor:

    """


    Attributes:
        cash {float} -- Cash available for the investor
        portfolio {} -- asd


    """


    def __init__(self, portfolio=None, cash=0, stockexchange):
        """[summary]
        
        Keyword Arguments:
            portfolio {[type]} -- [description] (default: {None})
            cash {int} -- [description] (default: {0})
        """

        self.stockexchange = stockexchange

        self.portfolio = Portfolio() if portfolio is None else portfolio
        self.cash = cash
        self.cash_reserved = 0
        self.asset_reserved = Counter()    

    def place_bid(self, asset:Asset, price:float, quantity:float, **kwargs):
        market = self.stockexchange[asset]
        market.place_bid(party=self, price=price, quantity=quantity, **kwargs)
        self.cash_reserved += price*quantity

    def place_ask(self, asset:Asset, price:float, quantity:float, **kwargs):
        market = self.stockexchange[asset]
        market.place_ask(party=self, price=price, quantity=quantity, **kwargs)
        self.asset_reserved[asset] += quantity


    def _receive_bid(self, asset:Asset, price:float, quantity:float, **kwargs):
        self.cash -= price*quantity
        self.cash_reserved -= price*quantity
        self.portfolio.append(asset, quantity=quantity)

    def _receive_ask(self, asset:Asset, price:float, quantity:float, **kwargs):
        self.cash += price*quantity
        self.asset_reserved[asset] -= quantity
        self.portfolio.remove(asset, quantity=quantity)

        



"""
Desired

myself = Investor()
inv_a = Investor()
inv_b = Investor()

myself.place_bid(nokia, 5.1, "limit")

"""
