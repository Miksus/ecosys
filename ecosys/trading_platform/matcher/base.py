
from abc import ABC, abstractmethod
import numpy as np
"""

https://docs.scipy.org/doc/numpy-1.15.1/reference/arrays.dtypes.html
https://www.investopedia.com/terms/o/order-book.asp

"""


class MarketMatcher(ABC):
    """Abstract class for markets

    Market is defined as place where participants
    trade assets/goods/et cetera.
    In this context, markets are (somewhat) perfect:
        - Bidders and askers can leave at will
        
    Use Auctions for imperfect markets
    
    Attributes:
        _dtype_mapping {Dict[Dict[Tuple]]} -- dict of numpy dtype 

    """



    _dtype_mapping = {
        "limit": {'names':('party', 'price', 'quantity'), 'formats':('U10', 'float32', 'u4')}
    }
    # Numpy takes as dtype to structured array in form of 
    # dict(names=..., formats=...) 
    # and therefore _dtype_mapping is 
    # dict(key=np.dtype)
    

    def __init__(self, asset=None):

        #Order book contain only limit orders
        self.order_book = {}
        self._setup_books()
        self._last_trade_ticks = None
        self.asset = asset

        self._historical_trades = []

    def _setup_books(self):
        "Setup the books for __init__"

        def make_array(dtype):
            return np.empty(shape=(0,), dtype=dtype)

        for order_type, dtype in self._dtype_mapping.items():
            self.order_book[order_type] = {
                "bid": make_array(dtype=dtype), "ask": make_array(dtype=dtype)
            }

    @abstractmethod
    def clear(self):
        self._settle_limit_orders()
    
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
        
        """
        # TODO: Remove unused bits (bids, asks)

        # For convenience
        bids = self.order_book[bid_origin]["bid"]
        asks = self.order_book[ask_origin]["ask"]

        disclosed_quantity = self._get_disclosed_trade_quantity(bid_order, ask_order)
        disclosed_ticks = self._get_disclosed_trade_ticks(bid_order, ask_order)

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
            ticks=disclosed_ticks, quantity=disclosed_quantity
        )

        # Delete completely fulfilled orders (if any)
        self._delete_fulfilled_orders()

    def _fulfill_orders(self, bid_order, ask_order, 
                        ticks, quantity, 
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
            ticks=ticks, quantity=quantity,
        )
        self.trade_orders(asset=self.asset, **trade_kwds)

        self._last_trade_ticks = ticks
        self.last_quantity = quantity

        self._historical_trades.append(trade_kwds)

    def _delete_fulfilled_orders(self):
        "Delete orders with quantity of zero"

        for book_type in self._dtype_mapping:
            bids = self.order_book[book_type]["bid"]
            asks = self.order_book[book_type]["ask"]

            bids = np.delete(bids, np.where(bids["quantity"] == 0), axis=0)
            asks = np.delete(asks, np.where(asks["quantity"] == 0), axis=0)

            self.order_book[book_type]["bid"] = bids
            self.order_book[book_type]["ask"] = asks

    def place_order(self, book_type, position, **params):
        """Put an order to order book
        
        Arguments:
            book_type {str} -- [description]
            position {str} -- [description]
        
        """

        book = self.order_book[book_type][position]
        dtype = self._dtype_mapping[book_type]

        def form_order(dtype, **params):
            row_values = tuple(params[column] for column in dtype["names"])
            return np.array([row_values], dtype=dtype)

        new_order = form_order(dtype, **params)
        self.order_book[book_type][position] = np.append(book, new_order)

    @staticmethod
    def trade_orders(bid, ask, ticks, quantity, asset):
        """All the fulfilled trades go here!
        This method should (in future):
            - Signal asker's account to remove {asset} by amount of {quantity} 
              and add {quantity * price} amount of cash
            - Signal bidder's account to remove {quantity * price} amount of cash
              and add {asset} by amount of {quantity}
        
        Arguments:
            bid {[type]} -- [description]
            ask {[type]} -- [description]
            price {[type]} -- [description]
            quantity {[type]} -- [description]
            asset {[type]} -- [description]
        """
        # currency = '€'
        # print("")
        # print("TRADING")
        # print(f"Ask <{'-'*(len(ask['party']) + len(bid['party']))}> Bid")
        # print(f'{ask["party"]} <{"-"*(len(ask["party"]) + len(bid["party"]))}> {bid["party"]}')
        # print(f"{quantity} x {asset}")
        # print(f"{ticks}{currency} x {quantity} = {quantity*ticks}{currency}")
        # print("-------")
        # print("") 


