
from ..base import Investor
import pandas as pd

class NPCInvestor(Investor):
    """

    Hyper Parameters:
        buffer_buy {float} -- Percentage of change required for buying (Should be positive)
        buffer_sell {float} -- Percentage of change required for selling (Should be negative)
        perceived_prices {pd.Series} -- Seen intrinsic, fair price of an asset by the investor

    Notes:
        - Use differences in buffer_buy and buffer_sell to reflect the loss aversion bias
            - For example if buffer_sell > -buffer_buy, the investor is more willing to buy
              an asset that has return potential of x% than selling an asset that has loss
              potential of x%
        - Use perceived_prices
    

    Flow of decision:
        - Filter buyable and sellable
            Goals:
                - Determine assets with 
                  negative and positive
                  trend
        - Determine value to buy and sell
            Goals:
                - Reflect portfolio allocation
                - Reflect risk taking
        - Determine price to buy and sell
            Goals:
                - Reflect supply and demand

    Arguments:
        Investor {[type]} -- [description]
    
    Raises:
        NotImplementedError -- [description]
        NotImplementedError -- [description]
    """

    def place_trades(self):
        sell_assets, sell_prices, sell_quantity = self.decide_asks()
        buy_assets, buy_prices, buy_quantity = self.decide_bids()

        concat_kwds = dict(axis=1, sort=False, keys=["asset", "price", "quantity"], join="inner")
        asks = pd.concat([sell_assets, sell_prices, sell_quantity], **concat_kwds).to_dict('records')
        bids = pd.concat([buy_assets, buy_prices, buy_quantity], **concat_kwds).to_dict('records')

        for trade in bids:
             self.place_bid(**trade)

        for trade in asks:
            self.place_ask(**trade)


    def decide_asks(self):
        "Decide on what price and quantity will be asked"
        assets = self.filter_sellable()
        values = self.decide_sell_values(assets=assets)
        prices = self.decide_sell_prices(assets=assets, asset_values=values)
        quantities = self.decide_sell_quantities(assets=assets, asset_values=values, asset_prices=prices)
        return assets, prices, quantities
    
    def decide_bids(self):
        "Decide on what price and quantity will be bid"
        assets = self.filter_buyable()
        values = self.decide_buy_values(assets=assets)
        prices = self.decide_buy_prices(assets=assets, asset_values=values)
        quantities = self.decide_sell_quantities(assets=assets, asset_values=values, asset_prices=prices)
        return assets, prices, quantities


    def filter_sellable(self):
        perceived_changes = self.perceived_changes
        return perceived_changes[perceived_changes < 0 & perceived_changes.isin(self.account.assets)].index

    def filter_buyable(self):
        perceived_changes = self.perceived_changes
        return perceived_changes[perceived_changes > 0].index
        

    def decide_sell_values(self, assets=None, **kwargs):
        pass

    def decide_buy_values(self, assets=None, **kwargs):
        pass


    def decide_sell_prices(self, asset_values=None, **kwargs):
        pass

    def decide_buy_prices(self, asset_values=None, **kwargs):
        pass


    def decide_sell_quantities(self, asset_values=None, asset_prices=None, **kwargs):
        return asset_values / asset_prices

    def decide_buy_quantities(self, asset_values=None, asset_prices=None, **kwargs):
        return asset_values / asset_prices


    @property
    def perceived_changes(self):
        current_prices = self.perceived_values.index.map(lambda asset: asset.price)
        return (self.perceived_values - current_prices) / current_prices

    @property
    def perceived_values(self):
        return pd.Series({asset: 5 for asset in self.markets})