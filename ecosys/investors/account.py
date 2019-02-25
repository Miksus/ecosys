from collections import Counter

import numpy as np
import pandas as pd

class AccountCreationMixin:
    # TODO:
    # Add withdraw asset
    # Add deposit & withdraw (money)
    def deposit(self, cash):
        self.cash += cash
        self._create_record(
            transaction_type="deposit",
            transaction_sum=cash
        )

    def withdraw(self, cash):
        self.cash -= cash
        self._create_record(
            transaction_type="withdraw",
            transaction_sum=-cash
        )

    def deposit_asset(self, asset, purchase_price, quantity):
        self._purchases.append({"asset":asset, "price":purchase_price, "quantity":quantity, "remaining":quantity})
        self._create_record(
            transaction_type="asset deposit",
            asset=asset,
            price=purchase_price,
            quantity=quantity
        )

    def withdraw_asset(self, asset, quantity):
        self._settle_purchases(asset=asset, quantity=quantity)
        self._create_record(
            transaction_type="asset withdraw",
            asset=asset,
            quantity=quantity
        )

class AccountInterfaceMixin:

    @property
    def total_value(self):
        cash = self.cash
        investment_value = sum([values["asset"].price * values["remaining"] for index, values in self._purchases.iterrows()])
        return investment_value + cash

    @property
    def portfolio(self):
        "Return assets and count of possession"
        portf = self._purchases.groupby("asset")["remaining"].sum()
        portf.name = "portfolio"
        return portf

    @property
    def assets(self):
        portf = self.portfolio
        portf["cash"] = self.cash
        portf.name = "assets"
        return portf

    def get_mean_price(self, asset):
        df = self.history[self.history.asset == asset].copy()
        # Sell prices to negative
        df.loc[df.transaction_type == "sell", "price"] = -df.loc[df.transaction_type == "sell", "price"]
        return (df["price"] * df["quantity"] / df["quantity"].sum()).sum()


class Account(AccountCreationMixin, AccountInterfaceMixin):

    def __init__(self):
        self.cash = 0
        self._purchases = pd.DataFrame(columns=("asset", "price", "quantity"))
        self.history = pd.DataFrame(columns=("time", "transaction_type", "price", "quantity", "transaction_sum", "saldo"))

        self._reserved_cash = 0
        self._reserved_asset = Counter()
    
    def _create_record(self, **fields):
        mandatory_fields = ("transaction_sum", "transaction_type")
        fields["saldo"] = self.cash

        missing = [mandatory for mandatory in mandatory_fields if mandatory not in fields]
        if missing:
            raise ValueError(f"Missing fields {missing}")

        self.history.append(fields, ignore_index=True)

    def buy(self, asset, price, quantity):
        "Bid order fulfilled"
        if price*quantity > self.cash:
            raise ValueError("Insufficient funds!")

        self._purchases.append({"asset":asset, "price":price, "quantity":quantity, "remaining":quantity})

        self.cash -= price*quantity
        self.release(cash=asset*quantity)
        
        self._create_record(
            transaction_type="buy",
            asset=asset,
            price=price,
            quantity=quantity,
            transaction_sum=-price*quantity
        )

    def sell(self, asset, price, quantity):
        "Ask order fulfilled"
        if quantity > self.portfolio.loc[asset]:
            raise ValueError(f"Insufficient amount of asset {asset}!")

        invested = self._settle_purchases(asset=asset, quantity=quantity)

        income = price*quantity
        profit_loss = income - invested

        self.cash += income
        self.release(asset=asset, quantity=quantity)

        self._create_record(
            transaction_type="sell",
            asset=asset,
            price=price,
            quantity=quantity,
            transaction_sum=price*quantity
        )
        return profit_loss

    def _settle_purchases(self, asset, quantity, order="fifo"):
        # Settle purchases by FIFO
        if order.lower() == "fifo":
            position = 0
        elif order.lower() == "lifo":
            position = -1
        else:
            raise KeyError(f"Invalid order type: {order}")

        invested = 0
        while quantity > 0:
            index = self._purchases.index[
                (self._purchases["asset"] == asset) & (self._purchases["remaining"] > 0)
            ][position]

            next_purchase = self._purchases.loc[index, "remaining"]
            settle = min(quantity, next_purchase)

            self._purchases.loc[index, "remaining"] -= settle

            quantity -= settle
            invested += next_purchase * settle

            if self._purchases.loc[index, "remaining"] == 0:
                self._purchases = self._purchases.drop(index=index)

        return invested



    def reserve(self, asset=None, quantity=None, cash=None):
        """Reserve assets/cash for trade 
        (one cannot back down when trade is being fulfilled thus funds MUST exist)
        
        Keyword Arguments:
            asset {[type]} -- [description] (default: {None})
            quantity {[type]} -- [description] (default: {None})
            cash {[type]} -- [description] (default: {None})
        """

        
        self.has(asset=asset, quantity=quantity, cash=cash)

        if cash is not None:
            self._reserved_cash += cash

        if asset is not None:
            self._reserved_asset[asset] += quantity
    
    def release(self, asset=None, quantity=None, cash=None):
        "Release reserved assets/cash"
        if cash is not None:
            self._reserved_cash -= cash
        if asset is not None:
            self._reserved_asset[asset] += quantity


    def has(self, asset=None, quantity=None, cash=None, ignore_reserve=False):
        
        if cash is not None:
            required_cash = cash
            reserve = self._reserved_cash if not ignore_reserve else 0
            has_funds = self.cash >= required_cash + reserve
            if not has_funds:
                raise ValueError("Insufficient funds!")
        if asset is not None and quantity is not None:
            required_quantity = quantity
            reserve = self._reserved_asset if not ignore_reserve else 0
            has_assets = self.portfolio.loc[asset] >= required_quantity + reserve
            if not has_assets:
                raise ValueError(f"Insufficient amount of {asset}")

        
