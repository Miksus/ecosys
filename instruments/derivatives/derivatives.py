
from ..instrument import Instrument

class Derivative(Instrument):
    
    def __init__(self, underlying_asset=None, **kwargs):
        self.underlying_asset = underlying_asset
        super().__init__(**kwargs)