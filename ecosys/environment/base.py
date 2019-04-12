

class Environment:

    def __init__(self, investors, stock_market):
        for investor in investors:
            investor.markets = stock_market
        self.investors = investors
        self.stock_market = stock_market


    def simulate(self, steps):
        
        for _ in range(steps):
            for investor in self.investors:
                investor.place_trades()
            self.stock_market.clear_all()
        

