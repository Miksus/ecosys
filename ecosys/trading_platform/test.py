
from market.stockmarket import StockMarket

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#? Testing
def generate_orders(n, mean_price):
    order_types = np.random.choice(["market", "limit", "stop"], p=[.05, .9, .05], size=n)
    prices = np.round(np.random.normal(loc=mean_price, scale=0.2, size=n), decimals=4)
    quantities = np.random.poisson(lam=1500, size=n)+500
    return list(zip(prices, quantities, order_types))


if __name__ == "__main__":
    
    import time

    my_market = StockMarket("Nokia")
    # Generating data
    orders_buy = [list(elem) + ["bid"] for elem in generate_orders(30, 4.8)]
    orders_sell = [list(elem) + ["ask"] for elem in generate_orders(30, 5.2)]
    
    orders = orders_buy+orders_sell
    np.random.shuffle(orders)
    
    for i, (p, q, order, position) in enumerate(orders):
        method = getattr(my_market, f'place_{position}')
        method(party=f'Investor {i+1}', price=p, quantity=q, order_type=order)
        if i % 5:
            pass
            #! Animated Plot
            #my_market.plot_order_animate()

        my_market.clear()
        #time.sleep(0.1)

    my_market.clear()
    print(my_market.to_frame())

    my_market.plot_orders()
    plt.show()
    pass