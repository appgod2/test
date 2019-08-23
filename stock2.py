import requests
from io import StringIO
import pandas as pd
import numpy as np


def crawl_price(date):
    r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + str(date).split(' ')[0].replace('-','') + '&type=ALL')
    ret = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '}) 
                                        for i in r.text.split('\n') 
                                        if len(i.split('",')) == 17 and i[0] != '='])), header=0)
    ret = ret.set_index('證券代號')
    ret['成交金額'] = ret['成交金額'].str.replace(',','')
    ret['成交股數'] = ret['成交股數'].str.replace(',','')
    ret['開盤價'] = ret['開盤價'].str.replace(',','')
    ret['最高價'] = ret['最高價'].str.replace(',','')
    ret['最低價'] = ret['最低價'].str.replace(',','')
    ret['收盤價'] = ret['收盤價'].str.replace(',','')

    return ret

def getData(_day):
    import datetime
    import time,random

    data = {}
    n_days = _day
    date = datetime.datetime.now()
    fail_count = 0
    allow_continuous_fail_count = 5
    while len(data) < n_days:

        print('parsing', date)
        # 使用 crawPrice 爬資料
        try:
            # 抓資料
            data[date.date()] = crawl_price(date)
            print('success!')
            fail_count = 0
        except:
            # 假日爬不到
            print('fail! check the date is holiday')
            fail_count += 1
            if fail_count == allow_continuous_fail_count:
                raise
                break
        
        # 減一天
        date -= datetime.timedelta(days=1)
        i = random.randint(5,10)
        time.sleep(i)
    
    return data

def getSid_list(_day):
    data = getData(_day)
    close = pd.DataFrame({k:d['收盤價'] for k,d in data.items()}).transpose()
    close.index = pd.to_datetime(close.index)
    for column in close:
        close[column].replace('--', None, methon = 'pad', inplace = True)
        close[column].replace('--', None, methon = 'bfill', inplace = True)
    close = close.astype(float)
    close.head()
    GoldX = rising_curve(close)
    #選出來的清單
    sid_list = GoldX[GoldX==True].index
    return sid_list


def rising_curve(close):
    # 5,10,20均線
    close5 = close.rolling(5,min_periods=5).mean()
    close10 = close.rolling(10,min_periods=10).mean()
    close20 = close.rolling(20,min_periods=20).mean()

    A = close5.iloc[-1] > close10.iloc[-1]
    B = close10.iloc[-1] > close10.iloc[-1]
    C = close5.iloc[-5] < close10.iloc[-5]
    D = close10.iloc[-5] < close10.iloc[-5]
    return A&B&C&D
