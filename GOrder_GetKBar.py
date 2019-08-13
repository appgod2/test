# 匯入模組
import datetime
import numpy as np
from talib.abstract import *

# 算K棒
class KBar():
    # 設定初始化變數
    def __init__(self,date,cycle = 1):
        # K棒的頻率(分鐘)
        self.TAKBar = {}
        self.TAKBar['time'] = np.array([])
        self.TAKBar['open'] = np.array([])
        self.TAKBar['high'] = np.array([])
        self.TAKBar['low'] = np.array([])
        self.TAKBar['close'] = np.array([])
        self.TAKBar['volume'] = np.array([])
        self.current = datetime.datetime.strptime(date + ' 08:45:00','%Y/%m/%d %H:%M:%S')
        self.cycle = datetime.timedelta(minutes = cycle)
    # 更新最新報價
    def AddPrice(self,time,price,volume):
        # 同一根K棒
        if time < self.current:
            # 更新收盤價
            self.TAKBar['close'][-1] = price
            # 更新成交量
            self.TAKBar['volume'][-1] += volume  
            # 更新最高價
            self.TAKBar['high'][-1] = max(self.TAKBar['high'][-1],price)
            # 更新最低價
            self.TAKBar['low'][-1] = min(self.TAKBar['low'][-1],price)      
        # 不同根K棒
        else:
            while time >= self.current:
                self.current += self.cycle
            self.TAKBar['time'] = np.append(self.TAKBar['time'],self.current)
            self.TAKBar['open'] = np.append(self.TAKBar['open'],price)
            self.TAKBar['high'] = np.append(self.TAKBar['high'],price)
            self.TAKBar['low'] = np.append(self.TAKBar['low'],price)
            self.TAKBar['close'] = np.append(self.TAKBar['close'],price)
            self.TAKBar['volume'] = np.append(self.TAKBar['volume'],volume)

    # 取時間
    def GetTime(self):
        return self.TAKBar['time']      
    # 取開盤價
    def GetOpen(self):
        return self.TAKBar['open']
    # 取最高價
    def GetHigh(self):
        return self.TAKBar['high']
    # 取最低價
    def GetLow(self):
        return self.TAKBar['low']
    # 取收盤價
    def GetClose(self):
        return self.TAKBar['close']
    # 取成交量
    def GetVolume(self):
        return self.TAKBar['volume']
    # 取MA值(MA期數)
    def GetMA(self,n):
        return SMA(self.TAKBar,n)
    # 取KD值(RSV期數,K值期數,D值期數)
    def GetKD(self,rsv,k,d):
        return STOCH(self.TAKBar,rsv,k,d)
    # 取布林通道值(中線期數)
    def GetBBands(self,n):
        return BBANDS(self.TAKBar,n)
    # 取MACD值
    def GetMACD(self,fast_P,slow_P,MACD_P):
        return MACD(self.TAKBar,fast_P,slow_P,MACD_P)
    # 取威廉值
    def GetWMS(self,N):
        return WILLR(self.TAKBar,N)
    # 取WMA值(WMA期數)
    def GetWMA(self,n):
        return WMA(self.TAKBar,n)
	# 取EMA值(EMA期數)
    def GetEMA(self,n):
        return EMA(self.TAKBar,n)
