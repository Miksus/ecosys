
#! UNDER DEVELOPMENT

class Investor:


    def __init__(self, portfolio=None):
        self.opportunities = set()

        self.portfolio = Portfolio() if portfolio is None else portfolio


    def add_opportunity(self, market:StockMarket):
        self.opportunities.add(market)
    
    def make_decisions(self):
        pass

    def buy(self, asset, quantity):
        asset_market = {for opportunity in self.opportunities}