
from ..base import Investor

# Ideas:
#   The percentual distance from perceived value to actual value
#   determine the ratio of the total portfolio the person is willing
#   to use for the asset

class NPCInvestor(Investor):
    def make_placements(self):
        buy_assets, sell_assets = self.analyze_portfolio()
        for asset in sell_assets:
            self.place_bid(asset, ??)
        for asset in buy:
            self.place_ask(asset, ??)

    def analyze_portfolio(self):
        pref_weights = self.get_prefered_weights()
        old_weights = portfolio.weights
        pref_values = pref_weights * 
        pref_weights - old_weights


class ActiveInvestor(NPCInvestor):
    """Investments are driven by perceived (caluclated) value
    Sell off all "sell recommendations"

    Traits:
        - Calculative
    """

    def __init__(self, **kwargs):
        self.super().__init__(**kwargs)
        self.perceived_values = {}
        self.perceived_value_buffer = 0.02

    def make_decisions(self):
        pref_weights = self.get_prefered_weights()
        pref_weights

    def get_prefered_weights(self):
        assets = ??
        scores = {asset: self.get_score(asset) for asset in assets}

        # Because Short selling is not allowed (yet)
        scores = {
            asset: score if score > 0 else 0 
            for asset, score in scores.items()
        }
        scores_sum = sum(scores.values())
        optimal_weights = {asset: score / scores_sum for asset, score in scores.items()}
        return optimal_weights

    def get_score(self, asset):
        perceived_price = self.perceived_values[asset]
        sell_buffer = self.perceived_value_buffer
        buy_buffer = self.perceived_value_buffer
        
        estimated_change = (perceived_price - asset.price) / perceived_price
        score = (
            0 if -sell_buffer < estimated_change < buy_buffer 
            else estimated_change - buy_buffer if estimated_change > 0
            else estimated_change + sell_buffer if estimated_change < 0
        )
        return score

class SheepInvestor(NPCInvestor):

    """Investments are driven by signals in market and media

    Traits:
        - Behavioral
    """

    def __init__(self, risk_avereness, **kwargs):
        super().__init__(**kwargs)
        self.risk_avereness = risk_avereness
        self.opinions = {asset: dict(perceived_value=None, riskiness=None) for asset in self.portfolio.assets}
        

    def make_decisions(self):
        for asset in assets:
            price_willing = self.opinions[asset]["perceived_value"]
            price_actual = asset.price
            diff = (price_willing - price_actual) / price_willing
