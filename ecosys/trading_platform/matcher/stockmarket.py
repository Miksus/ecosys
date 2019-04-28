
"""
Master class for stock order matcher

"""

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

from .base import MarketMatcher
from .mixins import LimitOrderMixin, MarketOrderMixin, StopOrderMixin

# TODO:
#   1. Turn prices to integers (cents) under the hood
#       - Should not change the usage of this class

class StockMatcher(MarketMatcher, LimitOrderMixin, MarketOrderMixin, StopOrderMixin):

    _dtype_mapping = {
        "limit": {'names':('party', 'price', 'quantity'), 'formats':('U10', 'float32', 'u4')},
        "market": {'names':('party', 'quantity'), 'formats':('U10', 'u4')},
        "stop": {'names':('party', 'price', 'quantity'), 'formats':('U10', 'float32', 'u4')}
    }

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
        return self.lowest_ask_price - self.highest_bid_price

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

# Plots
    def plot_orders(self, fig=None):
        """Plot cumulative histogram of the orders
        
        Keyword Arguments:
            fig {[type]} -- [description] (default: {None})
        
        Returns:
            [type] -- [description]
        """
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
        """Plot animated orders in cumulative histogram

        Inspiration: https://en.wikipedia.org/wiki/Order_book_(trading)#/media/File:Order_book_depth_chart.gif
        """
        plt.ion()
        n_bins =50
        bids = self.order_book["limit"]["bid"]
        asks = self.order_book["limit"]["ask"]

        if hasattr(self, "_plot_state"):
            # To optimize time spent on graphing
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

    def plot_order_book(self, tick_frequency=5):
        """Plot the orders in barh plot
        x axis: sum of quantity of orders per price (negative indicate asks)
        y axis: price (integers of cents under the hood)
        
        Keyword Arguments:
            tick_frequency {int} -- Tick label frequency (default: {5})
        """
        bids = self.order_book["limit"]["bid"].copy()
        asks = self.order_book["limit"]["ask"].copy()

        bids["quantity"] = bids["quantity"]
        asks["quantity"] = - asks["quantity"]

        orders = np.append(bids, asks)

        price_ticks = (orders["price"] * 100).round(0).astype("int")
        quantity = orders["quantity"].astype("int")

        ser_plot = (
            pd.Series(quantity, index=price_ticks)
            .groupby(price_ticks).sum()
            .reindex(range(price_ticks.min(), price_ticks.max() + 1))
        )

        colors = ser_plot.apply(lambda row: "orangered" if row <0 else "green")

        ax = plt.axes()
        plt.barh(ser_plot.index, ser_plot.values, align="center", height=1, 
                color=colors,
                edgecolor="k"
                )
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x/100:.2f}"))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(tick_frequency))

        ax.axvline(0, color="k")
        if self.last_price:
            ax.axhline(self.last_price*100, color="b", linestyle='--', label="Last Price")

        prop = dict(boxstyle='round', facecolor='lightgrey', alpha=0.5)
        ax.text(0.05, 0.95, "Asks", fontsize=14,
                horizontalalignment='left', transform = ax.transAxes,
                verticalalignment='top', color="orangered",
                bbox=prop)
        ax.text(0.95, 0.05, "Bids", fontsize=14,
                horizontalalignment='right', transform = ax.transAxes,
                verticalalignment='bottom', color="green",
                bbox=prop)

        plt.title(f"Order book: {self.asset}" if self.asset else "Order book")
        plt.ylabel("Price")
        plt.xlabel("Quantity")
        
    @property
    def historical(self):
        return pd.DataFrame(self._historical_trades)

