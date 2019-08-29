
class StockBean(object):
    def __init__(self, code="", codeNM="", quantity=0, cost=0,nowprice=0):
        self._code = code
        self._codeNM = codeNM
        self._quantity = quantity
        self._cost = cost
        self._nowprice = nowprice
    
    @property
    def code(self):
        return self._cost
    
    @code.setter
    def code(self, new_code):
        self._code = new_code
    
    @property
    def codeNM(self):
        return self._codeNM
    
    @codeNM.setter
    def codeNM(self, new_codeNM):
        self._codeNM = new_codeNM
    
    @property
    def quantity(self):
        return self._quantity
    
    @quantity.setter
    def quantity(self, new_quantity):
        self._quantity = new_quantity
    
    @property
    def cost(self):
        return self._cost
    
    @cost.setter
    def cost(self, new_cost):
        self._cost = new_cost
    
    @property
    def nowprice(self):
        return self._nowprice
    
    @nowprice.setter
    def nowprice(self, new_nowprice):
        self._nowprice = new_nowprice