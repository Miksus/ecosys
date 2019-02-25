

from collections import Counter
from ..investments.asset import Asset
from .account import Account

class Investor:

    """


    Attributes:
        cash {float} -- Cash available for the investor
        portfolio {} -- asd


    """


    def __init__(self, name, market, account=None):
        """[summary]
        
        Keyword Arguments:
            portfolio {[type]} -- [description] (default: {None})
            cash {int} -- [description] (default: {0})
        """

        self.market = market
        self.account = Account() if account is None else account
        self.name = name

    def place_bid(self, asset:Asset, price:float, quantity:float, **kwargs):
        self.account.reserve(cash=price*quantity)
        (
            self.market[asset]
            .place_bid(party=self, price=price, quantity=quantity, **kwargs)
        )

    def place_ask(self, asset:Asset, price:float, quantity:float, **kwargs):
        self.account.reserve(asset=asset, price=price, quantity=quantity)
        (
            self.market[asset]
            .place_ask(party=self, price=price, quantity=quantity, **kwargs)
        )


    def _buy(self, asset:Asset, price:float, quantity:float, **kwargs):
        "Should be called by the market after trade completition"
        self.account.buy(asset=asset, quantity=quantity, price=price)

    def _sell(self, asset:Asset, price:float, quantity:float, **kwargs):
        "Should be called by the market after trade completition"
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
