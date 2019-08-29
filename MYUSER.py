import StockBean
import logging
class MYUSER(object):
        
    def __init__(self, money=0, myStockData={str:StockBean}):
        self._id = None
        self._money = money
        self._oldmoney = money
        self._bank = 0
        self._myStockData = myStockData
    
    @property
    def money(self):
        return self._money
    
    @money.setter
    def money(self, new_money):
        self._money = new_money
    
    @property
    def myStockData(self):
        return self._myStockData
    
    @myStockData.setter
    def myStockData(self, new_myStockData):
        self._myStockData = new_myStockData
    
    def setId(self,id):
        self._id = id
    
    def buyStock(self,_StockBean):
        ncost = float(_StockBean._cost)
        nq = float(_StockBean._quantity)
        myAllMoney = float(self._money)
        if myAllMoney >= (ncost * nq):
            stockCost = 0
            oldmoney = float(self._oldmoney)
            if len(self._myStockData)>0:
                for _code in self._myStockData:
                    cost = float(self._myStockData[_code]._cost)
                    quantity = float(self._myStockData[_code]._quantity)
                    stockCost = stockCost + (cost * quantity)
            if oldmoney >= stockCost:
                oldMoney = float(self._money)
                buyMoney = ncost * nq
                HandlingFee = self.Handling_Fee(buyMoney)
                self._money = oldMoney - buyMoney - HandlingFee
                msg = ('買(%s)%s'%(_StockBean._code,_StockBean._codeNM),' 價位:%s ,數量:%s ,手續費:%s'%(ncost,nq,HandlingFee),'現金:%s - %s - %s = %s'%(oldMoney,buyMoney,HandlingFee,self._money))
                print(msg)
                logging.debug(msg)
                self._money = self._money - (ncost * nq)
                if _StockBean._code in self._myStockData:
                    old_StockBean = self._myStockData[_StockBean._code]
                    oq = float(old_StockBean._quantity)
                    ocost = float(old_StockBean._cost)
                    old_StockBean._cost = (ocost*oq + ncost*nq)/(oq+nq)
                    old_StockBean._quantity = oq + nq
                    old_StockBean._nowprice = float(_StockBean._nowprice)
                    self._myStockData[_StockBean._code] = old_StockBean
                else:
                    self._myStockData[_StockBean._code] = _StockBean
    
    def sellStock(self,_StockBean,text):
        if _StockBean._code in self._myStockData:
            old_StockBean = self._myStockData[_StockBean._code]
            oq = float(old_StockBean._quantity)
            nq = float(_StockBean.quantity)
            if oq >= nq:
                ncost = float(_StockBean._cost)
                ocost = float(old_StockBean._cost)
                addMoney = ncost * nq
                costMoney = round(ocost * nq ,0)
                HandlingFee = self.Handling_Fee(addMoney)
                TransactionTax = self.Transaction_Tax(addMoney)
                profit = addMoney - costMoney - HandlingFee - TransactionTax#損益
                oldMoney = float(self._money)
                self._money = oldMoney + addMoney
                newq = oq-nq
                if newq == 0:
                    self._myStockData.pop(_StockBean._code)
                else:
                    old_StockBean._cost = (ocost*newq)/newq
                    old_StockBean._quantity = newq
                    old_StockBean._nowprice = float(_StockBean._nowprice)
                    self._myStockData[_StockBean._code] = old_StockBean
                msg = (text,'賣(%s)%s'%(_StockBean._code,_StockBean._codeNM),' 價位:%s ,賣數量:%s ,成本:%s ,剩餘數量:%s ,手續費:%s ,交易稅:%s ,損益:%s'%(ncost,nq,ocost,newq,HandlingFee,TransactionTax,profit),'現金:%s + %s = %s'%(oldMoney,addMoney,self._money))
                print(msg)
                logging.debug(msg)
                stockCost = 0
                oldmoney = float(self._oldmoney)
                if len(self._myStockData)>0:
                    for _code in self._myStockData:
                        cost = float(self._myStockData[_code]._cost)
                        quantity = float(self._myStockData[_code]._quantity)
                        stockCost = stockCost + (cost * quantity)
                myMoney = float(self._money)
                allmoney = myMoney + stockCost
                if allmoney > oldmoney:
                    manyMoney = allmoney - oldmoney
                    oldBank = float(self._bank)
                    if manyMoney > myMoney:
                        self._bank = oldBank + myMoney
                        self._money = 0
                        msg = ('現金:%s => %s ,股票成本:%s'%(myMoney,self._money,stockCost),'存款:%s + %s = %s'%(oldBank,myMoney,self._bank))
                    else:
                        self._bank = oldBank + manyMoney
                        self._money = myMoney - manyMoney
                        msg = ('現金:%s => %s ,股票成本:%s'%(myMoney,self._money,stockCost),'存款:%s + %s = %s'%(oldBank,manyMoney,self._bank))
                    print(msg)
                    logging.debug(msg)

    def allMoney(self,date):
        stockMoney = 0
        stockCost = 0
        myAllMoney = float(self._money)
        if len(self._myStockData)>0:
            for _code in self._myStockData:
                nowprice = float(self._myStockData[_code]._nowprice)
                cost = float(self._myStockData[_code]._cost)
                quantity = float(self._myStockData[_code]._quantity)
                stockMoney = stockMoney + (nowprice * quantity)
                stockCost = stockCost + (cost * quantity)
        myAllMoney = myAllMoney + stockMoney + float(self._bank)
        oldmoney = float(self._oldmoney)
        p = round(((myAllMoney - oldmoney) / oldmoney) * 100 , 2)
        msg = (date,' 現金:%s ,股票總市值:%s ,股票成本:%s ,預估:%s ％ ,存款:%s'%(self._money,stockMoney,stockCost,p, self._bank))
        print(msg)
        logging.debug(msg)
        return msg

    def updateStockNowPrice(self,code,nowprice):
        if len(self._myStockData)>0:
            if code in self._myStockData:
                self._myStockData[code]._nowprice = float(nowprice)
    #手續費
    def Handling_Fee(self,money):
        a = 0.001425
        return round(money * a, 0)
    #交易稅
    def Transaction_Tax(self,money):
        a = 0.003
        return round(money * a ,0)
