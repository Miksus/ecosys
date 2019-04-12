

from collections import Counter
from ..investments.asset import Asset
from .account import Account

class Investor:

    """


    Attributes:
        cash {float} -- Cash available for the investor
        portfolio {} -- asd


    """


    def __init__(self, name, cash=None):
        """[summary]
        
        Keyword Arguments:
            portfolio {[type]} -- [description] (default: {None})
            cash {int} -- [description] (default: {0})
        """

        self.account = Account(cash=cash)
        self.name = name

    def place_bid(self, asset:Asset, quantity:float, price:float=None, **kwargs):
        self.account.reserve(cash=asset.price*quantity if price is None else price*quantity)
        (
            self.market[asset]
            .place_bid(party=self, price=price, quantity=quantity, **kwargs)
        )

    def place_ask(self, asset:Asset, quantity:float, price:float=None, **kwargs):
        self.account.reserve(asset=asset, quantity=quantity)
        (
            self.market[asset]
            .place_ask(party=self, price=price, quantity=quantity, **kwargs)
        )


    def buy(self, asset:Asset, price:float, quantity:float, **kwargs):
        "Should be called by the market after trade completition by a matcher!"
        self.account.buy(asset=asset, quantity=quantity, price=price)

    def sell(self, asset:Asset, price:float, quantity:float, **kwargs):
        "Should be called by the market after trade completition by a matcher!"
        self.account.sell(asset=asset, quantity=quantity, price=price)

    @property
    def portfolio(self):
        return self.account.portfolio


"""
Desired syntax

myself = Investor()
inv_a = Investor()
inv_b = Investor()

myself.place_bid(nokia, 5.1, "limit")

"""
