
import pytest
import sys
sys.path.append('..')
from ecosys.trading_platform.matcher.stockmarket import StockMatcher


def test_last_price_only_market_orders():
    market = StockMatcher()
    market.place_ask(quantity=50, order_type="market", party="Market Asker")
    market.place_bid(quantity=100, order_type="market", party="Market Bidder")

    bid_quantity = market.order_book["market"]["bid"]["quantity"].sum()
    ask_quantity = market.order_book["market"]["ask"]["quantity"].sum()

    market.clear()
    assert (market.last_price is None) and (100 == bid_quantity) and (50 == ask_quantity)

def test_oversupply():
    market = StockMatcher()

    market.place_bid(price=4.0, quantity=100, party="Bidder")
    market.place_ask(quantity=200, order_type="market", party="Market Asker")
    market.clear()

    bid_quantity = market.order_book["limit"]["bid"]["quantity"].sum()
    ask_quantity = market.order_book["market"]["ask"]["quantity"].sum()

    assert (4.0 == market.last_price) and (0 == bid_quantity) and (100 == ask_quantity)

def test_undersupply():
    market = StockMatcher()

    market.place_bid(price=4.0, quantity=200, party="Bidder")
    market.place_ask(quantity=100, order_type="market", party="Market Asker")
    market.clear()

    bid_quantity = market.order_book["limit"]["bid"]["quantity"].sum()
    ask_quantity = market.order_book["market"]["ask"]["quantity"].sum()

    assert (4.0 == market.last_price) and (100 == bid_quantity) and (0 == ask_quantity)

def test_overdemand():
    market = StockMatcher()

    market.place_bid(quantity=200, order_type="market", party="Market Bidder")
    market.place_ask(price=4.0, quantity=100, party="Asker")
    
    market.clear()

    bid_quantity = market.order_book["market"]["bid"]["quantity"].sum()
    ask_quantity = market.order_book["limit"]["ask"]["quantity"].sum()

    assert (4.0 == market.last_price) and (100 == bid_quantity) and (0 == ask_quantity)

def test_underdemand():
    market = StockMatcher()

    market.place_bid(quantity=50, order_type="market", party="Market Bidder")
    market.place_ask(price=4.0, quantity=100, party="Asker")
    
    market.clear()

    bid_quantity = market.order_book["market"]["bid"]["quantity"].sum()
    ask_quantity = market.order_book["limit"]["ask"]["quantity"].sum()

    assert (4.0 == market.last_price) and (0 == bid_quantity) and (50 == ask_quantity)

def test_market_to_market():
    "Opposite market orders should trade with last price"
    market = StockMatcher()
    market.place_bid(quantity=1, price=5.0, order_type="limit", party="Bidder")
    market.place_ask(quantity=1, price=5.0, order_type="limit", party="Asker")
    market.clear()

    market.place_bid(quantity=200, order_type="market", party="Market Bidder")
    market.place_ask(quantity=200, order_type="market", party="Market Asker")
    market.clear()

    bid_quantity = market.order_book["market"]["bid"]["quantity"].sum()
    ask_quantity = market.order_book["market"]["ask"]["quantity"].sum()

    assert (5.0 == market.last_price) and (0 == bid_quantity) and (0 == ask_quantity)


def test_market_priority():
    "Market orders should be filled first"
    market = StockMatcher()
    
    market.place_ask(quantity=500, price=5.0, order_type="limit", party="Asker")

    market.place_bid(quantity=100, price=4.0, order_type="limit", party="Bidder")
    market.place_bid(quantity=500, order_type="market", party="Market Bidder")
    market.place_bid(quantity=100, price=4.0, order_type="limit", party="Bidder")
    market.clear()

    bid_quantity_market = market.order_book["market"]["bid"]["quantity"].sum()
    bid_quantity_limit = market.order_book["limit"]["bid"]["quantity"].sum()
    assert (5.0 == market.last_price) and (0 == bid_quantity_market) and (200 == bid_quantity_limit)
