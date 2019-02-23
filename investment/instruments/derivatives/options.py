
from derivatives import Derivative

from calculations.option import calculate_european_call_price, calculate_european_put_price, d1 as calc_d1, d2 as calc_d2


class _Option(Derivative):

    def __init__(self, premium, strike, expiration_date, style="european", **kwargs):
        """
        premium: price of which the instrument was bought/sold
        strike
        exercise_date
        type: [call, put]
        style: [american, european]
        """
        self.premium = premium
        self.strike = strike
        
        self.expiration_date = expiration_date
        
        self.style = style
        
        super().__init__(**kwargs)

    def payoff(self, price_underlying):
        intrinsic = self.get_intrinsic(price_underlying)
        premium = self.premium
        
        if self.position == "long":
            return intrinsic - premium
        elif self.position == "short":
            return premium - intrinsic
        else:
            raise TypeError(f"Invalid option position: {self.position}")

    def calc_d1(self, spot_price, date, volatility_underlying, interest_rate):

        time_to_maturity = self.expiration_date - date
        return calc_d1(
            S=spot_price, 
            K=self.strike, 
            sigma=volatility_underlying, 
            T=time_to_maturity, 
            r=interest_rate
        )
    
    def calc_d2(self, spot_price, date, volatility_underlying, interest_rate):
        time_to_maturity = self.expiration_date - date 
        return calc_d2(
            S=spot_price, 
            K=self.strike, 
            sigma=volatility_underlying, 
            T=time_to_maturity, 
            r=interest_rate
        ) 
        
        
    def implied_volatility(self):
        pass
    
# Greeks

    def gamma(self):
        """Delta change of
        one unit change in underlying price
        """
        
    def vega(self):
        """ν=Sϕ(d1)t√
        """
        
    
# Decorators
    def __str__(self):
        return f'{self.type_} {self.position} option'


class PutOption(_Option):

    def get_intrinsic(self, price_underlying):
        strike = self.strike
        intrinsic = strike - price_underlying
        intrinsic[intrinsic < 0] = 0
        return intrinsic

    def calc_option_price(self, spot_price, date, interest_rate, volatility_underlying):

        time_to_maturity = self.expiration_date - date
        if self.style == "european":
            price = calculate_european_put(
                S=spot_price, 
                K=self.strike, 
                sigma=volatility_underlying, 
                T=time_to_maturity, 
                r=interest_rate
            )
        else:
            raise NotImplementedError
        return price
    
    @property
    def type_(self):
        return "Put"

class CallOption(_Option):

    def __init__(self, premium, strike, expiration_date, style="european", **kwargs):
        """
        premium: price of which the instrument was bought/sold
        strike
        exercise_date
        type: [call, put]
        style: [american, european]
        """
        self.premium = premium
        self.strike = strike
        
        self.expiration_date = expiration_date
        
        self.type = type_
        self.style = style
        
        super().__init__(**kwargs)

    def get_intrinsic(self, price_underlying):
        strike = self.strike
        intrinsic = price_underlying - strike

        intrinsic[intrinsic < 0] = 0
        return intrinsic

    def calc_option_price(self, spot_price, date, interest_rate, volatility_underlying):

        time_to_maturity = self.expiration_date - date
        if self.style == "european":
            price = calculate_european_call(
                S=spot_price, 
                K=self.strike, 
                sigma=volatility_underlying, 
                T=time_to_maturity, 
                r=interest_rate
            )
        else:
            raise NotImplementedError
        return price

    @property
    def type_(self):
        return "Call"