
import numpy as np

class Auction:
    #! UNDER DEVELOPMENT

    _dtype_mapping = {
        "offer": {'names':('party', 'price'), 'formats':('U10', 'float32', 'u4')},
        "consignor": {'names':('party', 'quantity'), 'formats':('U10', 'u4')}
    }
    #* Consignor is the seller (or buyer in reverse)

    def __init__(self, consignor, asset=None, reverse=False, sealed=False):
        """Initialize auction for asset 
        where consignor is seller (or buyer if reverse)
        
        Arguments:
            consignor {dict} -- Consignor
        
        Keyword Arguments:
            asset {[type]} -- [description] (default: {None})
            reverse {bool} -- [description] (default: {False})
            sealed {bool} -- [description] (default: {False})
        """
        self.consignor_position = "ask" if not reverse else "bid"
        self.participant_position = "bid" if not reverse else "ask"
        self.sealed = sealed

        self.order_book = {}
        self._setup_books()
        self._place_order("consignor", **consignor)
        self.order_book["consignor"] = np.append(self.order_book["consignor"], new_order)
        self.asset = asset

    def _setup_books(self):
        def make_array(dtype):
            return np.empty(shape=(0,), dtype=dtype)

        for order_type, dtype in self._dtype_mapping.items():
            # Differs from MarketPlace:
            # No specification of bids and asks
            # as only one of them is possible per order_type
            self.order_book[order_type] = make_array(dtype=dtype)

    def _place_order(self, book_type, **params):
        """Put an order to order book

        NOTE: in Auction, position is not defined
              as it is defined by attr "reverse"
              
        Arguments:
            book_type {str} -- [description]
            position {str} -- [description]
        
        """

        book = self.order_book[book_type]
        dtype = self._dtype_mapping[book_type]

        def form_order(dtype, **params):
            row_values = tuple(params[column] for column in dtype["names"])
            return np.array([row_values], dtype=dtype)

        new_order = form_order(dtype, **params)
        self.order_book[book_type] = np.append(book, new_order)
    

    def clear(self):
        best_offer = self.best_offer
        price = self.best_offer["price"]
        consignor = self.order_book["consignor"]
        quantity = consignor["quantiy"]

        self.consigor_position
        if self.consigor_position == "bid":
            self.trade_orders(
                bid=self.consigor, ask=best_offer, 
                price=price, quantity=quantity,
                asset=self.asset)
    @property
    def best_offer(self):
        offers = self.order_book["offer"]
        if self.reverse:
            # Consignor
            return offers[np.argmax(offers["price"], axis=0)]
            offers["price"].max

