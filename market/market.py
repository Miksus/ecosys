
# RAW VERSION

from abc import ABC, abstractmethod

import numpy as np
import pandas as pd


import matplotlib.pyplot as plt
import seaborn as sns

class AbstractMarket(ABC):


    def __init__(self, asset=None):
        """
        Different books for:
            market
            stop
            limit orders
        """
        # https://docs.scipy.org/doc/numpy-1.15.1/reference/arrays.dtypes.html

        # https://www.investopedia.com/terms/o/order-book.asp
        
        #Order book contain only limit orders
        self._setup_books()
        self.last_price = None
        self.asset = asset

        self._historical_trades = []

    @abstractmethod
    def clear(self):
        raise NotImplementedError("Set clear method to the class")

    @abstractmethod
    def set_sell_order(self, order_type="market", **params):
        raise NotImplementedError("")

    @abstractmethod
    def set_buy_order(self, order_type="market", **params):
        raise NotImplementedError("")
    
    def _clear_orders(self, bid_order, ask_order, bid_origin="limit", ask_origin="limit"):
        """Remove orders from order book and pass them to trade
        Parameters
        ----------
            bid_order: array-like
                bid order to clear (partially or completely)
            ask_order: array-like
                ask order to clear (partially or completely)
            bid_origin: {"limit", "market", "stop"}
                type of book the bid_order originates from
            ask_origin: {"limit", "market", "stop"}
                type of book the ask_order originates from

        Book must have:
            bid
            ask
            which both must have:
                quantity

        TODO:
            If both market orders, price is latest price
            Match bid_order_index & ask_order_index using 
        """
        def get_disclosed_price(bid, ask, decimals):
            prices = [
                order["price"]
                for order in (bid_order, ask_order) 
                if "price" in order.dtype.names
            ]
            if prices:
                price = np.mean(prices)
            else:
                price = self.last_price
            
            return np.round(price, decimals)

        def get_disclosed_quantity(bid, ask):
            return min(bid["quantity"], ask["quantity"])


        # For convenience
        bids = self.order_book[bid_origin]["bid"]
        asks = self.order_book[ask_origin]["ask"]


        disclosed_quantity = get_disclosed_quantity(bid_order, ask_order)
        disclosed_price = get_disclosed_price(bid_order, ask_order, decimals=4)

        # Fulfilled
        bid_order_fulfilled = bid_order.copy()
        ask_order_fulfilled = ask_order.copy()

        bid_order_fulfilled["quantity"] = disclosed_quantity
        ask_order_fulfilled["quantity"] = disclosed_quantity

        # set new quantities
        bid_order["quantity"] -= disclosed_quantity
        ask_order["quantity"] -= disclosed_quantity


        # Put back modified the order books
        self.order_book[bid_origin]["bid"] = bids
        self.order_book[ask_origin]["ask"] = asks

        # Turn fulfilled orders to dicts
        self._fulfill_orders(
            bid_order_fulfilled, ask_order_fulfilled, 
            bid_origin=bid_origin, ask_origin=ask_origin,
            price=disclosed_price, quantity=disclosed_quantity
        )

        # Delete completely fulfilled orders (if any)
        self._delete_fulfilled_orders()

    def _fulfill_orders(self, bid_order, ask_order, 
                        price, quantity, 
                        bid_origin=None, ask_origin=None):

        # Turn orders (np.void) to dict
        bid_order = {
            column: bid_order[i] 
            for i, column in enumerate(self._dtype_mapping[bid_origin]["names"])
        }
        ask_order = {
            column: ask_order[i] 
            for i, column in enumerate(self._dtype_mapping[ask_origin]["names"])
        }
        bid_order["order"] = bid_origin
        ask_order["order"] = ask_origin

        trade_kwds = dict(
            bid=bid_order, ask=ask_order, 
            price=price, quantity=quantity,
        )
        trade_orders(asset=self.asset, **trade_kwds)
        self.last_price = price
        self.last_quantity = quantity

        self._historical_trades.append(trade_kwds)

    def _delete_fulfilled_orders(self):
        "Delete orders with quantity of zero"

        for book_type in ("limit", "market", "stop"):
            bids = self.order_book[book_type]["bid"]
            asks = self.order_book[book_type]["ask"]

            bids = np.delete(bids, np.where(bids["quantity"] == 0), axis=0)
            asks = np.delete(asks, np.where(asks["quantity"] == 0), axis=0)

            self.order_book[book_type]["bid"] = bids
            self.order_book[book_type]["ask"] = asks



class LimitOrderMarket(AbstractMarket):

    _dtype_mapping = {
        "limit": {'names':('party', 'price', 'quantity'), 'formats':('U10', 'float32', 'u4')}
    }

    def _setup_books(self):
        "Setup the books for __init__"

        def make_array(dtype):
            return np.empty(shape=(0,), dtype=dtype)

        # https://www.investopedia.com/terms/o/order-book.asp
        limit_dtypes = self._dtype_mapping["limit"]

        self.order_book = {
            "limit":{"bid": make_array(limit_dtypes), "ask": make_array(limit_dtypes)}
        }

    def set_sell_order(self, **params):
        book = self.order_book["limit"]["ask"]
        dtype = self._dtype_mapping["limit"]

        row_values = tuple(params[column] for column in dtype["names"])
        order = np.array([row_values], dtype=dtype)

        self.order_book["limit"]["ask"] = np.append(book, order)


    def set_buy_order(self, **params):
        book = self.order_book["limit"]["bid"]
        dtype = self._dtype_mapping["limit"]

        row_values = tuple(params[column] for column in dtype["names"])
        order = np.array([row_values], dtype=dtype)

        self.order_book["limit"]["bid"] = np.append(book, order)

    def clear(self):
        self._settle_limit_orders()

# Limit order
    def _settle_limit_orders(self):
        # 1. Get orders that are in the spread (between ask and bid prices)
        # 2. Fulfill the orders from lowest to highest
        # TODO:
        #   If no limit orders, end

        def has_limit_orders(state):
            bids = state.order_book["limit"]["bid"]
            asks = state.order_book["limit"]["ask"]
            return bids.size > 0 and asks.size > 0

        while has_limit_orders(state=self) and self.highest_bid_price >= self.lowest_ask_price:
            # Fulfilling till the spread exists

            highest_bid_order = self.highest_bid_order
            lowest_ask_order = self.lowest_ask_order

            self._clear_orders(
                bid_order=highest_bid_order, 
                ask_order=lowest_ask_order, 
                bid_origin="limit", ask_origin="limit"
            )

    @property
    def highest_bid_order(self):
        "Order with maximum price the market is willing to buy"
        bids = self.order_book["limit"]["bid"]
        return bids[np.argmax(bids["price"], axis=0)]

    @property
    def lowest_ask_order(self):
        "Order withminimum price the market is willing to sell"
        asks = self.order_book["limit"]["ask"]
        try:
            return asks[np.argmin(asks["price"], axis=0)]
        except ValueError:
            return None

    @property
    def highest_bid_price(self):
        "Maximum price the market is willing to buy"
        bids = self.order_book["limit"]["bid"]
        try:
            return bids["price"].max()
        except ValueError:
            return None

    @property
    def lowest_ask_price(self):
        "Minimum price the market is willing to sell"
        asks = self.order_book["limit"]["ask"]
        try:
            return asks["price"].min()
        except ValueError:
            return None



class StockMarket(LimitOrderMarket):

    _dtype_mapping = {
        "limit": {'names':('party', 'price', 'quantity'), 'formats':('U10', 'float32', 'u4')},
        "market": {'names':('party', 'quantity'), 'formats':('U10', 'u4')},
        "stop": {'names':('party', 'price', 'quantity'), 'formats':('U10', 'float32', 'u4')}
    }

    def _setup_books(self):
        "Setup the books for __init__"

        def make_array(dtype):
            return np.empty(shape=(0,), dtype=dtype)

        # https://www.investopedia.com/terms/o/order-book.asp
        limit_dtypes = self._dtype_mapping["limit"]
        market_dtypes = self._dtype_mapping["market"]
        stop_dtypes = self._dtype_mapping["stop"]

        self.order_book = {
            "limit":{"bid": make_array(limit_dtypes), "ask": make_array(limit_dtypes)},
            "market":{"bid": make_array(market_dtypes), "ask": make_array(market_dtypes)},
            "stop":{"bid" :make_array(stop_dtypes), "ask": make_array(stop_dtypes)}
        }

    def set_sell_order(self, order_type="market", **params):
        book = self.order_book[order_type]["ask"]
        dtype = self._dtype_mapping[order_type]

        row_values = tuple(params[column] for column in dtype["names"])
        order = np.array([row_values], dtype=dtype)

        self.order_book[order_type]["ask"] = np.append(book, order)


    def set_buy_order(self, order_type="market", **params):
        book = self.order_book[order_type]["bid"]
        dtype = self._dtype_mapping[order_type]

        row_values = tuple(params[column] for column in dtype["names"])
        order = np.array([row_values], dtype=dtype)

        self.order_book[order_type]["bid"] = np.append(book, order)

    def clear(self):
        self._trigger_stop_orders()
        self._settle_market_orders()
        self._settle_limit_orders()

    def _settle_market_orders(self):
        "Settle market orders with limit orders"
        # TODO:
        #   Streamline

        market_as_bid = ("bid", "oldest_bid_market_order", "ask", "lowest_ask_order")
        market_as_ask = ("ask", "oldest_ask_market_order", "bid", "highest_bid_order")
        for market_position, market_attr, counter_position, counter_attr in (market_as_bid, market_as_ask):

            while self.order_book["market"][market_position].size > 0:
                # There are market bids

                market_order = getattr(self, market_attr)
                if self.order_book["limit"][counter_position].size > 0:
                    # Limit order exists
                    counter_order = getattr(self, counter_attr)
                    counter_origin = "limit"
                elif self.order_book["market"][counter_position].size > 0:
                    # No limit orders
                    # --> take market
                    counter_order = getattr(self, f'oldest_{counter_position}_market_order')
                    counter_origin = "market"
                else:
                    # No limit & market orders
                    # --> end
                    break
                
                bid_order = market_order if market_position == "bid" else counter_order
                ask_order = market_order if market_position == "ask" else counter_order
                bid_origin = "market" if market_position == "bid" else counter_origin
                ask_origin = "market" if market_position == "ask" else counter_origin

                if bid_origin == ask_origin == "market" and self.last_price is None:
                    # Cannot clear orders,
                    # need a price level
                    return 
                self._clear_orders(
                    bid_order=bid_order, 
                    ask_order=ask_order, 
                    bid_origin=bid_origin, ask_origin=ask_origin
                )

    def _trigger_stop_orders(self):
        """Activate stop orders that are triggered
        --> Turn these stop orders to market orders"""
        stop_bids = self.order_book["stop"]["bid"]
        stop_asks = self.order_book["stop"]["ask"]

        if self.last_price is None:
            # Cannot trigger any stop orders,
            # no price level
            return

        mask_bids = stop_bids["price"] > self.last_price
        mask_asks = stop_asks["price"] < self.last_price

        actived_stop_bids = stop_bids[mask_bids]
        actived_stop_asks = stop_asks[mask_asks]

        # Set as market orders and remove from stop
        fields_market_order = list(self._dtype_mapping["market"]["names"])
        if actived_stop_bids.size > 0:
            # Correct columns (remove price)
            actived_stop_bids = actived_stop_bids[fields_market_order]
            
            # Dump to market orders
            self.order_book["market"]["bid"] = np.append(self.order_book["market"]["bid"], actived_stop_bids.copy())
            
            # Remove from stop orders
            self.order_book["stop"]["bid"] = np.delete(stop_bids, np.where(mask_bids), axis=0)

        if actived_stop_asks.size > 0:
            # Correct columns (remove price)
            actived_stop_asks = actived_stop_asks[fields_market_order]
            
            # Dump to market orders
            self.order_book["market"]["ask"] = np.append(self.order_book["market"]["ask"], actived_stop_asks.copy())
            
            # Remove from stop orders
            self.order_book["stop"]["ask"] = np.delete(stop_asks, np.where(mask_asks), axis=0)

    @property
    def oldest_bid_market_order(self):
        market_bids = self.order_book["market"]["bid"]
        return market_bids[0]

    @property
    def oldest_ask_market_order(self):
        market_asks = self.order_book["market"]["ask"]
        return market_asks[0]
    

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


def trade_orders(bid, ask, price, quantity, asset) -> None:
    "All trading goes by here"

    print("")
    print("TRADING")
    print(f'{ask["party"]} --> {bid["party"]}')
    print(f'Price: {price} Quantity: {quantity}')
    print("-------")
    print("")




def generate_orders(n, mean_price):
    order_types = np.random.choice(["market", "limit", "stop"], p=[.05, .9, .05], size=n)
    prices = np.round(np.random.normal(loc=mean_price, scale=0.2, size=n), decimals=4)
    quantities = np.random.poisson(lam=1500, size=n)+500
    return list(zip(prices, quantities, order_types))


if __name__ == "__main__":
    import time



    my_market = StockMarket("Nokia")
    orders_buy = [list(elem) + ["buy"] for elem in generate_orders(30, 4.8)]
    orders_sell = [list(elem) + ["sell"] for elem in generate_orders(30, 5.2)]
    orders = orders_buy+orders_sell
    np.random.shuffle(orders)
    pass
    for i, (p, q, order, position) in enumerate(orders):
        method = getattr(my_market, f'set_{position}_order')
        method(party=str(i), price=p, quantity=q, order_type=order)
        if i % 5:
            pass
            #my_market.plot_order_animate()
        my_market.clear()
        time.sleep(0.1)

    my_market.clear()
    print(my_market.to_frame())










    #my_market.set_sell_order(party="Bearer_1", price=5, quantity=10, order_type="limit")
    #my_market.set_sell_order(party="Bearer_2", price=6, quantity=10, order_type="limit")
    #my_market.set_sell_order(party="Bearer_3", quantity=10, order_type="market")
    #my_market.set_sell_order(party="Bearer_4", price=6, quantity=7, order_type="limit")

    #my_market.set_buy_order(party="Buller_1", price=5, quantity=8, order_type="limit")
    #my_market.set_buy_order(party="Buller_2", price=4, quantity=10, order_type="limit")
    #my_market.set_buy_order(party="Buller_3", quantity=10, order_type="market")
    #my_market.set_buy_order(party="Buller_4", price=4, quantity=6, order_type="limit")

    #my_market.clear()
    my_market.plot_orders()
    plt.show()
    #my_market.set_buy_order(party="Buller_3", quantity=10, order_type="market")
    #my_market.set_buy_order(party="Buller_3", quantity=10, order_type="market")
    #print(my_market.ask)
    #print(my_market.bid)

    pass