from ecosys import Environment, ActiveInvestor, ShareClass, StockExchange

env = Environment(
    investors={
        ActiveInvestor(name="Jack", cash=10_000),
        ActiveInvestor(name="John", cash=10_000),
        ActiveInvestor(name="James", cash=10_000)
    },
    stock_market=StockExchange(
        ShareClass("Nokia", ticker="NOK"), 
        ShareClass("Fortum", ticker="FUM"), 
        ShareClass("Nordea", ticker="NDEA")
    )

)

env.simulate(5)