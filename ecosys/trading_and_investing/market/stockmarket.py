
# RAW VERSION



import numpy as np
import pandas as pd


import matplotlib.pyplot as plt
import seaborn as sns


from .base import MarketPlace 
from .mixins import LimitOrderMixin, MarketOrderMixin, StopOrderMixin

class StockMarket(MarketPlace, LimitOrderMixin, MarketOrderMixin, StopOrderMixin):

    _dtype_mapping = {
        "limit": {'names':('party', 'price', 'quantity'), 'formats':('U10', 'float32', 'u4')},
        "market": {'names':('party', 'quantity'), 'formats':('U10', 'u4')},
        "stop": {'names':('party', 'price', 'quantity'), 'formats':('U10', 'float32', 'u4')}
    }
    #//trade_func = trade_orders
# Set orders
    def place_ask(self, order_type="limit", **params):
        """Place ask (sell) order to market
        
        Keyword Arguments:
            order_type {str} -- type of the order (default: {"limit"})
            **params -- obligatory information for the order type. See self._dtype_mapping
        """
        self.place_order(book_type=order_type, position="ask", **params)

    def place_bid(self, order_type="limit", **params):
        """Place bid (buy) order to market
        
        Keyword Arguments:
            order_type {str} -- [description] (default: {"limit"})
            **params -- obligatory information for the order type. See self._dtype_mapping
        """
        self.place_order(book_type=order_type, position="bid", **params)

    def clear(self):
        self._trigger_stop_orders()
        self._settle_market_orders()
        self._settle_limit_orders()




    

# Analytical
    def __str__(self):
        return(
            f"Market for {self.asset}\n"
            f"------------------------\n"
            f"Latest price: {self.last_price}\n"
            f"Bid orders: {self.total_quantities['bid']}\n"
            f"Ask orders: {self.total_quantities['ask']}\n"
            f"Spread: {self.spread}\n"
        )

    @property
    def spread(self):
        return self.lowest_ask - self.highest_bid

    @property
    def total_quantities(self):
        bid_quantities = 0
        ask_quantities = 0
        for book_type in ("limit", "market", "stop"):
            bid_quantities += self.order_book[book_type]["bid"]["quantity"].sum()
            ask_quantities += self.order_book[book_type]["ask"]["quantity"].sum()
        return {"bid":bid_quantities, "ask":ask_quantities}

    def to_frame(self):
        # Columns ("limit", "market", "stop")
        dfs = []
        for book_type in ("limit", "market", "stop"):
            dfs_book = []
            for position in ("bid", "ask"):
                dfs_book.append(pd.DataFrame(self.order_book[book_type][position]))
            dfs.append(pd.concat(dfs_book, axis=0, keys=("bid", "ask"), sort=False))
        return pd.concat(dfs, axis=0, keys=("limit", "market", "stop"), sort=False)

    def plot_orders(self, fig=None):
        # x: price
        # y: quantity (cumulative)
        n_bins =50
        bids = self.order_book["limit"]["bid"]
        asks = self.order_book["limit"]["ask"]
        trade_prices = [trade["price"] for trade in self._historical_trades]


        ask_kwds = dict(histtype='step', density=False, cumulative=1, weights=asks["quantity"])
        bid_kwds = dict(histtype='step', density=False, cumulative=-1, weights=bids["quantity"])

        fig, (ax_box, ax_hist) = plt.subplots(2, sharex=True, gridspec_kw={"height_ratios": (.15, .85)})

        sns.distplot(asks["price"], n_bins, rug=True, rug_kws={"height":0.05}, hist_kws=ask_kwds, kde=False, norm_hist=False, ax=ax_hist, color="r", label="Asks")
        sns.distplot(bids["price"], n_bins, rug=True, rug_kws={"height":0.05}, hist_kws=bid_kwds, kde=False, norm_hist=False, ax=ax_hist, color="g", label="Bids")
        ax_hist.axvline(self.last_price, 0, 0.25, color="k", linestyle="--", label="Last price")
        
        sns.boxplot(trade_prices, ax=ax_box)
        ax_box.set(yticks=[])
        
        sns.despine(ax=ax_box, left=True)
        sns.despine(ax=ax_hist)
        ax_hist.legend()
        return fig
    


    def plot_order_animate(self):
        plt.ion()
        n_bins =50
        bids = self.order_book["limit"]["bid"]
        asks = self.order_book["limit"]["ask"]

        if hasattr(self, "_plot_state"):
            hist_ask, hist_bid, fig, ax = self._plot_state
            ax.cla()

            hist_ask = ax.hist(asks["price"], weights=asks["quantity"], cumulative=True, label='Ask cumulative')
            hist_bid = ax.hist(bids["price"], weights=bids["quantity"], cumulative=-1, label='Bid cumulative')
            fig.canvas.draw()
            fig.canvas.flush_events()
        else:

            fig, ax = plt.subplots(figsize=(8, 4))
            hist_ask = ax.hist(asks["price"], weights=asks["quantity"], cumulative=True, label='Ask cumulative')
            hist_bid = ax.hist(bids["price"], weights=bids["quantity"], cumulative=-1, label='Bid cumulative')
        self._plot_state = (hist_ask, hist_bid, fig, ax)


