
from ..base import Investor

# Ideas:
#   The percentual distance from perceived value to actual value
#   determine the ratio of the total portfolio the person is willing
#   to use for the asset

class NPCInvestor(Investor):

    def __init__(self, risk_avereness, **kwargs):
        super().__init__(**kwargs)
        self.risk_avereness = risk_avereness
        self.opinions = {asset: dict(perceived_value=None, riskiness=None) for asset in self.portfolio.assets}
        

    def make_decisions(self):
        for asset in assets:
            price_willing = self.opinions[asset]["perceived_value"]
            price_actual = asset.price
            diff = (price_willing - price_actual) / price_willing
