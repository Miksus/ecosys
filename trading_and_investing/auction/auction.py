



class EnglishAuction(Auction):


    """


    """


    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
        



    def clear(self):
        self._set_order()
        self._settle_market_orders()



    def __getattribute__(self, name):
        if name in self._exclude_from_parents:
            raise AttributeError(name)
        else: return super().__getattribute__(name)

    def __dir__(self):
        return sorted((set(dir( self.__class__ )) | set(self.__dict__.keys())) - set(self._exclude_from_parents))