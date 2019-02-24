import numpy as np
class Asset:

    def __init__(self, name, market:StockMarket):
        self.name = name
        self.market = market

    @property
    def price(self):
        market.last_price


class Account:

    def __init__(self, *assets, cash=0):
        self.cash = cash
        self._portfolio = {}
        self.history = pd.DataFrame(columns=("time", "type", "price", "quantity", "transaction_sum", "saldo"))
    
    def _create_record(self, transaction_type, asset, price, quantity, saldo, time=None):
        total = price*quantity

        transaction_sum = {
            "sell": +total 
            "buy": -total
        }[transaction_type]

        self.history.append({
            "time": time,
            "transaction_type": str(transaction_type),
            "asset": asset,
            "price": np.float64(price),
            "quantity": np.int64(quantity),
            "transaction_sum": np.float64(transaction_sum),
            "saldo": np.float64(self.cash),
        }, ignore_index=True)

    def buy(self, asset, price, quantity):
        "Bid order fulfilled"

        if asset not in self._portfolio:
            self._portfolio[asset] = quantity
        else:
            # Add to quantity
            self._portfolio[asset] += quantity

        self.cash -= price*quantity
        
        self._create_record(
            transaction_type="buy",
            asset=asset,
            price=price,
            quantity=quantity
        )

    def sell(self, asset, price, quantity):
        "Ask order fulfilled"
        if asset not in self._portfolio:
            raise ValueError(f"Cannot sell not owned asset {asset}!")
        else:
            # Add to quantity
            self._portfolio[asset] -= quantity
        income = price*quantity

        self.history[self.history["asset"] == asset]

        self.cash += income
        self._create_record(
            transaction_type="sell",
            asset=asset,
            price=price,
            quantity=quantity
        )
        


    def remove(self, **kwargs):
        row_values = tuple(kwargs[column] for column in self._dtype["names"])
        investment = np.array([row_values], dtype=self._dtype)


    def _detele_not_owned(self, **kwargs):
        ownings = self._investments
        self._investments = np.delete(ownings, np.where(ownings["quantity"] == 0), axis=0)



    def __getitem__(self, asset):
        "Get investment"
        if asset not in self._investments:
            return {"price": 0, "quantity": 0}
        return self._investments[asset]

    def __setitem__(self, asset, item):
        "Append investment"
        if isinstance(item, dict):
            self._investments[asset] = {"price": item["price"], "quantity": item["quantity"]}

    def __delitem__(cls, my_str):
        pass

    @property
    def assets(self):
        return self._investments

 

# ! OLD
class Account:

    _dtype = {'names':('asset', 'price', 'quantity'), 'formats':('O', 'float32', 'u4')}

    def __init__(self, *assets, cash=0):
        self.cash = cash
        self._investments = np.empty(shape=(0,), dtype=self._dtype["dtype"])
        self.history = []

    def append(self, **kwargs):
    
        row_values = tuple(kwargs[column] for column in self._dtype["names"])
        investment = np.array([row_values], dtype=self._dtype)

        self._investments = np.append(self._investments, investment)

    def remove(self, **kwargs):
        row_values = tuple(kwargs[column] for column in self._dtype["names"])
        investment = np.array([row_values], dtype=self._dtype)


    def _detele_not_owned(self, **kwargs):
        ownings = self._investments
        self._investments = np.delete(ownings, np.where(ownings["quantity"] == 0), axis=0)



    def __getitem__(self, asset):
        "Get investment"
        if asset not in self._investments:
            return {"price": 0, "quantity": 0}
        return self._investments[asset]

    def __setitem__(self, asset, item):
        "Append investment"
        if isinstance(item, dict):
            self._investments[asset] = {"price": item["price"], "quantity": item["quantity"]}

    def __delitem__(cls, my_str):
        pass

    @property
    def assets(self):
        return self._investments
# Syntax
# acc = Account()
# acc[Shares("Nokia")] = {"price":}