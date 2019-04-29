
from abc import ABC, abstractmethod
#TODO: streamline "_settle_market_orders"
import numpy as np

class LimitOrderMixin(ABC):
    n_ticks = 2
    def _settle_limit_orders(self):
        # 1. Get orders that are in the spread (between ask and bid prices)
        # 2. Fulfill the orders from lowest to highest


        def has_limit_orders(state):
            bids = state.order_book["limit"]["bid"]
            asks = state.order_book["limit"]["ask"]
            return bids.size > 0 and asks.size > 0

        while has_limit_orders(state=self) and self._highest_bid_ticks >= self._lowest_ask_ticks:
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
        "Order with maximum ticks the market is willing to buy"
        bids = self.order_book["limit"]["bid"]
        return bids[np.argmax(bids["ticks"], axis=0)]

    @property
    def lowest_ask_order(self):
        "Order with minimum ticks the market is willing to sell"
        asks = self.order_book["limit"]["ask"]
        try:
            return asks[np.argmin(asks["ticks"], axis=0)]
        except ValueError:
            return None

    @property
    def _highest_bid_ticks(self):
        "Maximum price the market is willing to buy in ticks"
        bids = self.order_book["limit"]["bid"]
        try:
            ticks = bids["ticks"].max()
            return ticks
        except ValueError:
            return None

    @property
    def _lowest_ask_ticks(self):
        "Minimum price the market is willing to sell in ticks"
        asks = self.order_book["limit"]["ask"]
        try:
            ticks = asks["ticks"].min()
            return ticks
        except ValueError:
            return None

    @property
    def highest_bid_price(self):
        "Maximum price the market is willing to buy"
        ticks = self._highest_bid_ticks
        return self._ticks_to_price(ticks)

    @property
    def lowest_ask_price(self):
        "Minimum price the market is willing to sell"
        ticks = self._lowest_ask_ticks
        return self._ticks_to_price(ticks)

    def _price_to_ticks(self, price):
        if price is None:
            return None
        price = round(price, self.n_ticks)
        multiplier = 10 ** self.n_ticks
        ticks = int(price * multiplier)
        return ticks
    
    def _ticks_to_price(self, ticks):
        if ticks is None:
            return None
        divider = 10 ** self.n_ticks
        price = ticks / divider
        return price


class MarketOrderMixin(ABC):

    def _settle_market_orders(self):
        """Settle market orders with limit orders
        1. Fetch bid market orders (if any)
        2. Match it with limit order
            - If None found, match with market order
                - Price is the last price
                    - If no last price, continue
            - If None market orders found, continue
        3. Repeat with Asks

        """
        # TODO: Streamline

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

    @property
    def oldest_bid_market_order(self):
        market_bids = self.order_book["market"]["bid"]
        return market_bids[0]

    @property
    def oldest_ask_market_order(self):
        market_asks = self.order_book["market"]["ask"]
        return market_asks[0]


class StopOrderMixin(ABC):

    def _trigger_stop_orders(self):
        """Activate stop orders that are triggered
        --> Turn these stop orders to market orders"""
        stop_bids = self.order_book["stop"]["bid"]
        stop_asks = self.order_book["stop"]["ask"]

        if self._last_trade_ticks is None:
            # Cannot trigger any stop orders,
            # no price level
            return

        mask_bids = stop_bids["ticks"] > self._last_trade_ticks
        mask_asks = stop_asks["ticks"] < self._last_trade_ticks

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
