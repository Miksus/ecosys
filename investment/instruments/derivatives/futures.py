from derivatives impor Derivative



class Futures(Derivative):
    # https://www.investopedia.com/university/futures/futures4.asp
    def __init__(self, quantity, delivery_date, rate, **kwargs):
        self.quantity = quantity
        self.delivery_date = delivery_date
        self.rate = rate # Future rate
        
        super().__init__(**kwargs)