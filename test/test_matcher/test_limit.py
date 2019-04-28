
import pytest
import sys
sys.path.append('..')
from ecosys.trading_platform.matcher.stockmarket import StockMatcher


def test_fulfilling_equal():
    market = StockMatcher()

    market.place_bid(price=5.0, quantity=200, party="Bidder")
    market.place_ask(price=5.0, quantity=200, party="Asker")
    market.clear()

    bid_quantity = market.order_book["limit"]["bid"]["quantity"].sum()
    ask_quantity = market.order_book["limit"]["ask"]["quantity"].sum()

    assert (5.0 == market.last_price) and (0 == bid_quantity) and (0 == ask_quantity)

def test_fulfilling_equal_decimals():
    market = StockMatcher()

    market.place_bid(price=5.55, quantity=200, party="Bidder")
    market.place_ask(price=5.55, quantity=200, party="Asker")
    market.clear()

    bid_quantity = market.order_book["limit"]["bid"]["quantity"].sum()
    ask_quantity = market.order_book["limit"]["ask"]["quantity"].sum()

    assert (5.55 == market.last_price) and (0 == bid_quantity) and (0 == ask_quantity)

def test_fulfilling_unequal():
    market = StockMatcher()

    market.place_bid(price=6.0, quantity=200, party="Bidder")
    market.place_ask(price=4.0, quantity=200, party="Asker")
    market.clear()

    bid_quantity = market.order_book["limit"]["bid"]["quantity"].sum()
    ask_quantity = market.order_book["limit"]["ask"]["quantity"].sum()

    assert (5.0 == market.last_price) and (0 == bid_quantity) and (0 == ask_quantity)

def test_unfulfilling():
    market = StockMatcher()

    market.place_bid(price=4.0, quantity=200, party="Bidder")
    market.place_ask(price=6.0, quantity=200, party="Asker")
    market.clear()

    bid_quantity = market.order_book["limit"]["bid"]["quantity"].sum()
    ask_quantity = market.order_book["limit"]["ask"]["quantity"].sum()

    assert (market.last_price is None) and (200 == bid_quantity) and (200 == ask_quantity)

def test_oversupply():
    market = StockMatcher()

    market.place_bid(price=6.0, quantity=200, party="Bidder")
    market.place_ask(price=5.0, quantity=200, party="Asker")
    market.place_ask(price=5.0, quantity=200, party="Asker")
    market.clear()

    bid_quantity = market.order_book["limit"]["bid"]["quantity"].sum()
    ask_quantity = market.order_book["limit"]["ask"]["quantity"].sum()

    assert (5.5 == market.last_price) and (0 == bid_quantity) and (200 == ask_quantity)

def test_overdemand():
    market = StockMatcher()

    market.place_ask(price=5.0, quantity=200, party="Asker")
    market.place_bid(price=6.0, quantity=200, party="Bidder")
    market.place_bid(price=6.0, quantity=200, party="Bidder")
    market.clear()

    bid_quantity = market.order_book["limit"]["bid"]["quantity"].sum()
    ask_quantity = market.order_book["limit"]["ask"]["quantity"].sum()

    assert (5.5 == market.last_price) and (200 == bid_quantity) and (0 == ask_quantity)

def test_bid_priority():
    market = StockMatcher()

    market.place_ask(price=5.0, quantity=500, party="Asker")

    market.place_bid(price=1.0, quantity=100, party="Bidder")
    market.place_bid(price=6.0, quantity=500, party="Best Bidder")
    market.place_bid(price=1.0, quantity=100, party="Bidder")
    
    market.clear()

    bid_quantity = market.order_book["limit"]["bid"]["quantity"].sum()
    ask_quantity = market.order_book["limit"]["ask"]["quantity"].sum()

    assert (5.5 == market.last_price) and (200 == bid_quantity) and (0 == ask_quantity)

def test_partial_fill():
    market = StockMatcher()

    market.place_ask(price=2.0, quantity=300, party="Asker")

    market.place_bid(price=5.0, quantity=100, party="Bidder")
    market.place_bid(price=6.0, quantity=100, party="Bidder")
    market.place_bid(price=3.0, quantity=100, party="Last Bidder")
    market.place_bid(price=1.0, quantity=100, party="Unfilled Bidder")
    
    market.clear()

    bid_quantity = market.order_book["limit"]["bid"]["quantity"].sum()
    ask_quantity = market.order_book["limit"]["ask"]["quantity"].sum()

    assert (2.5 == market.last_price) and (100 == bid_quantity) and (0 == ask_quantity)