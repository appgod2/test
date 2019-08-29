def test00():
    import pandas as pd
    data = test0()
    close = pd.DataFrame({k:d['收盤價'] for k,d in data.items()}).transpose()
    close.index = pd.to_datetime(close.index)
    close.to_csv('all.csv', index=True)


def test0():
    import datetime
    import time

    data = {}
    n_days = 9
    date = datetime.datetime.now()
    fail_count = 0
    allow_continuous_fail_count = 5
    while len(data) < n_days:

        print('parsing', date)
        # 使用 crawPrice 爬資料
        # try:
            # 抓資料
        data[date.date()] = crawl_price(date)
        print('success!')
        fail_count = 0
        # except:
        #     # 假日爬不到
        #     print('fail! check the date is holiday')
        #     fail_count += 1
        #     if fail_count == allow_continuous_fail_count:
        #         raise
        #         break
        
        # 減一天
        date -= datetime.timedelta(days=1)
        time.sleep(10)
    
    return data

def crawl_price(date):
    import requests
    from io import StringIO
    import pandas as pd
    import numpy as np

    r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + str(date).split(' ')[0].replace('-','') + '&type=ALL')
    ret = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '}) 
                                        for i in r.text.split('\n') 
                                        if len(i.split('",')) == 17 and i[0] != '='])), header=0)
    ret = ret.set_index('證券代號')
    ret['成交金額'] = ret['成交金額'].str.replace(',','')
    ret['成交股數'] = ret['成交股數'].str.replace(',','')
    # df = pd.DataFrame(ret, ret.)
    ret.to_csv(str(date).split(' ')[0].replace('-','')+'.csv', index=True)
    return ret

def test():
    from pandas_datareader import data # pip install pandas_datareader
    import matplotlib.pyplot as plt    # pip install matplotlib
    import pandas as pd                # pip install pandas
    from io import BytesIO
    import base64

    data = data.DataReader("^TWII", "yahoo", "2000-01-01","2019-08-01")
    c = data['Close']
    c.plot()
    # plt.show()
    sio = BytesIO()
    plt.savefig(sio, format='png')
    outdata = base64.encodebytes(sio.getvalue()).decode()
    plt.close
    return outdata

def test2():
    import pandas as pd

    lookback_period = 3
    start_capital = 1
    for year in range(2010, 2018):
        
        # calculate performance of stocks
        # -------------------------------

        # 拿取近n年股票
        c = close.truncate(str(year-lookback_period), str(year))

        # 計算近n年最大下跌幅度
        dropdown = (c.cummax() - c).max()/c.max()*100

        # 計算近n年報酬率
        profit = (c.iloc[-1] / c.iloc[0] - 1) * 100

        # 計算近n年標準差(波動率)
        std = (c/c.shift()).std()

        # constraint
        # ----------
        
        constraint = (std[std < 0.02].index & 
                    profit[profit > 10].index & 
                    dropdown[dropdown < 50].index) 

        # backtest
        # --------

        # 取出今年的股價
        c2 = close.truncate(str(year), str(year + 1))

        # 依照剛剛的條件選取股票
        selected_stocks = constraint & c2.columns
        print(year, '年買了',len(selected_stocks),'支股票')

        # 回測
        equality = c2[selected_stocks].dropna(axis=1).mean(axis=1)
        total_equality = (equality / equality[0] * start_capital)
        total_equality.plot(color='blue')

        # 今年底的資產，變成明年初的資產
        start_capital = total_equality[-1]

# test00()