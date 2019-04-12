
from .base import NPCInvestor
import pandas as pd
import numpy as np
# Ideas:
#   The percentual distance from perceived value to actual value
#   determine the ratio of the total portfolio the person is willing
#   to use for the asset



class ActiveInvestor(NPCInvestor):
    """Investments are driven by perceived (caluclated) value
    Sell off all "sell recommendations"

    Traits:
        - Calculative
    """
    def decide_asks(self):
        "Decide on what price and quantity will be asked"
        assets = self.filter_sellable()
        quantities = self.decide_sell_quantities(assets=assets)
        prices = self.decide_sell_prices(assets=assets, quantities=quantities)
        return assets, prices, quantities


    def decide_buy_values(self, assets):
        perceived_changes = self.perceived_changes[assets]
        optimal_weights = perceived_changes / perceived_changes.sum()
        return optimal_weights * self.account.cash


    def decide_sell_prices(self, assets=None, asset_values=None, **kwargs):
        """[summary]
        Affecting price:
            + big demand
            - big supply
            + perceived_change
            - risks

        p = price that maximize(payoff * probability_trade)
        payoff = p - perceived_value
        probability_trade = probability of the shares of the order (X) can be executed before cancellation of the order
        probability_trade = prob(sum of bid sizes with price p - sum of ask sizes that are better than investor's + bid momentum - ask momentum >= investor's order size)
        probability_trade = prob(bids[bids >= p] - asks[asks < p] + bid_momentum - ask_momentum >= X)

        bid_momentum = investor's guess for sizes of incoming bids over price p before cancelling his/her order
        ask_momentum = investor's guess for sizes of incoming asks under price p before cancelling his/her order

        Keyword Arguments:
            assets {[type]} -- [description] (default: {None})
            asset_values {[type]} -- [description] (default: {None})
        """
        perceived_changes = self.perceived_changes
        prices = np.array([])
        for asset in assets:
            bids = asset.market.order_book["limit"]["bid"]
            asks = asset.market.order_book["limit"]["ask"]
            historical_trades = asset.market.historical
            price_per_expected_payoff = {
                p: (p - perceived_value)
                * (
                    (bids[bids["price"] >= p]["quantity"] + historical_trades[historical_trades["price"] > p]["quantity"]) 
                    / (asks[asks["price"] < p]["quantity"] + historical_trades[historical_trades["price"] < p]["quantity"])
                )
                for p in np.linspace(asset.price*0.9, asset.price*1.1, 200)
            }
            p = max(price_per_expected_payoff, key=prices.get)
            np.append(prices, p)
        return prices

    def decide_buy_prices(self, assets, asset_values=None, **kwargs):
        """[summary]
        Affecting price:
            - Big supply
            + Big demand
            + perceived_change
            - risks
        Keyword Arguments:
            assets {[type]} -- [description] (default: {None})
            asset_values {[type]} -- [description] (default: {None})
        """
        perceived_changes = self.perceived_changes
        prices = np.array([])
        for asset in assets:
            bids = asset.market.order_book["limit"]["bid"]
            asks = asset.market.order_book["limit"]["ask"]
            historical_trades = asset.market.historical
            price_per_expected_payoff = {
                p: (perceived_value - p)
                * (
                    (asks[asks["price"] < p]["quantity"] + historical_trades[historical_trades["price"] < p]["quantity"])
                    / (bids[bids["price"] >= p]["quantity"] + historical_trades[historical_trades["price"] > p]["quantity"]) 
                )
                for p in np.linspace(asset.price*0.9, asset.price*1.1, 200)
            }
            p = max(price_per_expected_payoff, key=prices.get)
            np.append(prices, p)
        return prices


    def decide_sell_quantities(self, assets, **kwargs):
        # Sell all
        return self.account.portfolio_quantities[assets]

    def decide_buy_quantities(self, asset_values=None, asset_prices=None, **kwargs):
        return asset_values / asset_prices


class RandomInvestor(NPCInvestor):

    def decide_asks(self):
        pass

    def decide_bids(self):
        pass



class SheepInvestor(NPCInvestor):

    """Investments are driven by signals in market and media

    Traits:
        - Behavioral
    """

    def __init__(self, risk_avereness, **kwargs):
        super().__init__(**kwargs)
        self.risk_avereness = risk_avereness
        self.opinions = {asset: dict(perceived_value=None, riskiness=None) for asset in self.portfolio.assets}
        

