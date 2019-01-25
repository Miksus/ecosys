


class Bond(Instrument):
    _map_payment_periods = {
        "p.a":"Y"
    }
    _days_in_year = 360
    
    def __init__(self, face_value, cupon_rate, maturity=None, n_payments=None, payment_period="6M", **kwargs):
        self.face_value = face_value
        self.maturity = maturity
        
        self.cupon_rate = cupon_rate
        
        super().__init__(**kwargs)
        
        # self.payment_periods: pd.DatetimeIndex
        self.payment_periods = to_payment_periods(
            start=self.contract_date,
            maturity=maturity,
            n_payments=n_payments,
            payment_period=payment_period
        )
    
    def payoff(self):
        pass
    
    @property
    def payments(self):
        ser = self.interest_payments
        ser[ser.index.max()] += self.face_value
        return ser
    
    @property
    def interest_payments(self):
        return pd.Series([self.cupon_rate*self.face_value for _ in self.payment_periods], index=self.payment_periods)
        
        
    def calc_npv(self, risk_free_rate):
        pass