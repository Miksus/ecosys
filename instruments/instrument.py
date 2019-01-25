class Instrument:

    _map_positions = {
        "short":"short", "write":"short", "sell":"short", 
        "long":"long", "buy":"long"
    }
    
    def __init__(self, position="long", contract_date=None):
        if contract_date is None:
            self.contract_date = datetime.datetime.now()
        else:
            self.contract_date = contract_date
        self.position = self._map_positions[position]
    
    @property
    def is_short(self):
        return self.position == "short"
    
    @property
    def is_long(self):
        return self.position == "long"