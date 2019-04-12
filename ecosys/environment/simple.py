from ..trading_platform.marketplace import StockExchange
from ..investors.base import Investor
from ..investments.share import ShareClass


from ..trading_platform.matcher.stockmarket import StockMatcher


Environment(
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

omxh = StockExchange(
    ShareClass("Nokia", ticker="NOK"), 
    ShareClass("Fortum", ticker="FUM"), 
    ShareClass("Nordea", ticker="NDEA")
)

inv_a = Investor(name="Jack", market=omxh)
inv_b = Investor(name="John", market=omxh)
inv_c = Investor(name="James", market=omxh)

inv_a.account.deposit(5000)
inv_a.account.deposit_asset(omxh["Nokia"], quantity=500)
inv_a.account.deposit_asset(omxh["Fortum"], quantity=200)
inv_a.account.deposit_asset(omxh["Nordea"], quantity=100)

inv_b.account.deposit(7000)
inv_b.account.deposit_asset(omxh["Nokia"], quantity=10)
inv_b.account.deposit_asset(omxh["Fortum"], quantity=500)
inv_b.account.deposit_asset(omxh["Nordea"], quantity=20)

inv_c.account.deposit(500)
inv_c.account.deposit_asset(omxh["Fortum"], quantity=2000)
inv_c.account.deposit_asset(omxh["Nordea"], quantity=30)


inv_a.place_ask(asset="Nokia", price=5.3, quantity=250, order_type="limit")
inv_b.place_bid(asset="Nokia", price=5.2, quantity=200, order_type="limit")
inv_c.place_ask(asset="Nokia", price=5.3, quantity=50, order_type="limit")