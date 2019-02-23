
#! UNDER DEVELOPMENT
from collections import Counter

# TODO
# Set way to store "opinions"
# Opinion contains "persieved_value"
# 


class Investor:


    def __init__(self, portfolio=None, cash=0):
        self.opportunities = {}

        self.portfolio = Portfolio() if portfolio is None else portfolio
        self.cash = cash
        self.cash_reserved = 0
        self.asset_reserved = Counter()

    def add_opportunity(self, market:StockMarket):
        self.opportunities[market.asset] = market
    

    def place_bid(self, asset:Asset, price:float, quantity:float, **kwargs):
        market = self.opportunities[asset]
        market.place_bid(party=self, price=price, quantity=quantity, **kwargs)
        self.cash_reserved += price*quantity

    def place_ask(self, asset:Asset, price:float, quantity:float, **kwargs):
        market = self.opportunities[asset]
        market.place_ask(party=self, price=price, quantity=quantity, **kwargs)
        self.asset_reserved[asset] += quantity

    def receive_bid(self, asset:Asset, price:float, quantity:float, **kwargs):
        self.cash -= price*quantity
        self.cash_reserved -= price*quantity
        self.portfolio.append(asset, quantity=quantity)

    def receive_ask(self, asset:Asset, price:float, quantity:float, **kwargs):
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
