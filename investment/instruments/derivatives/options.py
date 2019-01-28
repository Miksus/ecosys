
from derivatives import Derivative




class Option(Derivative):
    
    def __init__(self, premium, strike, expiration_date, type, style="european", **kwargs):
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
        
        self.type = type
        self.style = style
        
        super().__init__(**kwargs)

    def get_intrinsic(self, price_underlying):
        strike = self.strike
        if self.type == "call":
            intrinsic = price_underlying - strike
        elif self.type == "put":
            intrinsic = strike - price_underlying
        else:
            raise TypeError(f"Invalid option type: {option}")
            
        intrinsic[intrinsic < 0] = 0
        return intrinsic
        
    def payoff(self, price_underlying):
        intrinsic = self.get_intrinsic(price_underlying)
        premium = self.premium
        
        if self.position == "long":
            return intrinsic - premium
        elif self.position == "short":
            return premium - intrinsic
        else:
            raise TypeError(f"Invalid option position: {self.position}")
    
# Black and Scholes
    def calc_option_price(self, spot_price, date, interest_rate, volatility_underlying):
        switch = {
            "european":{
                "put": calculate_european_put,
                "call": calculate_european_call
            }
        }
        time_to_maturity = self.expiration_date - date
        return switch[self.style][self.type](
            S=spot_price, 
            K=self.strike, 
            sigma=volatility_underlying, 
            T=time_to_maturity, 
            r=interest_rate
        )

    def calc_d1(self, spot_price, date, volatility_underlying, interest_rate):

        time_to_maturity = self.expiration_date - date
        return calculate_d1(
            S=spot_price, 
            K=self.strike, 
            sigma=volatility_underlying, 
            T=time_to_maturity, 
            r=interest_rate
        )
    
    def calc_d2(self, spot_price, date, volatility_underlying, interest_rate):
        time_to_maturity = self.expiration_date - date 
        return calculate_d2(
            S=spot_price, 
            K=self.strike, 
            sigma=volatility_underlying, 
            T=time_to_maturity, 
            r=interest_rate
        ) 
        
        
    def implied_volatility(self):
        pass
    
# Greeks
    def calc_delta(self, current_date):
        """Price change of 
        one unit change in underlying price
        """
        switch = {
            "european":{
                "put": calculate_european_put_price,
                "call": calculate_european_call_price
            }
        }
        
        time_to_maturity = self.expiration_date - current_date
        return switch[self.style][self.type](
            S=spot_price, 
            K=self.strike, 
            sigma=volatility_underlying, 
            T=time_to_maturity, 
            r=interest_rate
        )
        
        
    def gamma(self):
        """Delta change of
        one unit change in underlying price
        """
        
    def vega(self):
        """ν=Sϕ(d1)t√
        """
        
    
# Decorators
    def __str__(self):
        return f'{self.type} {self.position} option'
