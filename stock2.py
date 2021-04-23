# !/usr/bin/python 
# coding:utf-8 

import requests
from io import StringIO
import pandas as pd
import numpy as np
# from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import talib as ta
from tqdm import tqdm
from numba import njit
from concurrent.futures import ProcessPoolExecutor,as_completed,wait, ALL_COMPLETED
from multiprocessing import cpu_count
import concurrent.futures
from datetime import datetime
import dask.dataframe as dd
import time
# import StockPredictor

# _host='118.150.153.139'
# _port=32773
_host='127.0.0.1'
_port=3306
# _user='root'
# _password='acha'

# _host='127.0.0.1'
# _port=3306
_user='root'
_password='acha'
_database='twstock'

def initMySQL(__host,__port,__user,__password,__database):
    global _host
    global _port
    global _user
    global _password
    global _database
    _host=__host
    _port=__port
    _user=__user
    _password=__password
    _database=__database

def getDBconnect():
    import pymysql
    conn = pymysql.connect(host=_host,port=_port,user=_user,password=_password,database=_database, charset='utf8')
    return conn

def getMyStockData_mysql():
    conn = getDBconnect()
    df = pd.read_sql("select * from myStockData ORDER BY CODE ASC", con=conn)
    return df

def getMyStockDataToStockBeanList():
    import StockBean
    data = {}
    df = getMyStockData_mysql()
    for item in df.items():
        _StockBean = StockBean.StockBean
        _StockBean.code = item["code"]
        _StockBean.codeNM = item["codeNM"]
        _StockBean.quantity =  item["quantity"]
        _StockBean.cost = item["cost"]
        _StockBean.nowprice = item["nowprice"]
        data[item["CODE"]] = _StockBean
    return data

def addMysql(data_list):
    import MySQLdb

    conn = MySQLdb.connect(host=_host,port=_port,user=_user,password=_password,database=_database)
    conn.set_character_set('utf8')
    cursor = conn.cursor()
    sql = "insert into stockall(DATE,CODE,NAME,成交股數,成交筆數,成交金額,open_price,最高價,最低價,close_price,漲跌,漲跌價差,最後揭示買價,最後揭示買量,最後揭示賣價,最後揭示賣量,本益比,Unnamed) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    content = cursor.executemany(sql, data_list)
    if content:
        print('成功')
    conn.commit()
    cursor.close
    conn.close
    
def ret2list(date):
    ret = crawl_price(date)
    data_list = []
    for item in ret.values:
        _date = date.strftime("%Y%m%d")
        result = (_date, isNaN(item[0]), isNaN(item[1]), isNaN(item[2]), isNaN(item[3])
        , isNaN(item[4]), isNaN(item[5]), isNaN(item[6]), isNaN(item[7]), isNaN(item[8]), isNaN(item[9])
        , isNaN(item[10]), isNaN(item[11]), isNaN(item[12]), isNaN(item[13]), isNaN(item[14]), isNaN(item[15])
        , isNaN(item[16]))
        data_list.append(result)
        # print(result)
    return data_list
def isNaN(num):
    if num != num:
        return 'NULL'
    else:
        return num
        
def crawl_price(date):
    r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + str(date).split(' ')[0].replace('-','') + '&type=ALL')
    ret = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '}) 
                                        for i in r.text.split('\n') 
                                        if len(i.split('",')) == 17 and i[0] != '='])), header=0)
    return ret

def initRet(ret):
    ret = ret.set_index('證券代號')
    # ret['成交金額'] = ret['成交金額'].str.replace(',','')
    ret['成交股數'] = ret['成交股數'].str.replace(',','')
    ret['開盤價'] = ret['開盤價'].str.replace(',','')
    ret['最高價'] = ret['最高價'].str.replace(',','')
    ret['最低價'] = ret['最低價'].str.replace(',','')
    ret['收盤價'] = ret['收盤價'].str.replace(',','')
    return ret

def initRet2(ret,data=None,date=0):
    # global aaa
    ret = ret.set_index('CODE')
    # ret['成交金額'] = ret['成交金額'].str.replace(',','')
    ret['成交股數'] = ret['成交股數'].str.replace(',','')
    ret['成交股數'].replace('--', np.nan, method = 'pad', inplace = True)
    ret['成交股數'].replace('--', np.nan, method = 'bfill', inplace = True)
    ret['成交股數'] = ret['成交股數'].astype(float)
    ret['open_price'] = ret['open_price'].str.replace(',','')
    ret['open_price'].replace('--', np.nan, method = 'pad', inplace = True)
    ret['open_price'].replace('--', np.nan, method = 'bfill', inplace = True)
    ret['open_price'] = ret['open_price'].astype(float)
    ret['最高價'] = ret['最高價'].str.replace(',','')
    ret['最高價'].replace('--', np.nan, method = 'pad', inplace = True)
    ret['最高價'].replace('--', np.nan, method = 'bfill', inplace = True)
    ret['最高價'] = ret['最高價'].astype(float)
    ret['最低價'] = ret['最低價'].str.replace(',','')
    ret['最低價'].replace('--', np.nan, method = 'pad', inplace = True)
    ret['最低價'].replace('--', np.nan, method = 'bfill', inplace = True)
    ret['最低價'] = ret['最低價'].astype(float)
    ret['close_price'] = ret['close_price'].str.replace(',','')
    ret['close_price'].replace('--', np.nan, method = 'pad', inplace = True)
    ret['close_price'].replace('--', np.nan, method = 'bfill', inplace = True)
    ret['close_price'] = ret['close_price'].astype(float)

    if data is not None:
        data[date] = ret
    return ret

# def initRet4(key):
#     ret = _sector.get_group(int(key))
#     ret = ret.set_index('CODE')
#     # ret['成交金額'] = ret['成交金額'].str.replace(',','')
#     ret['成交股數'] = ret['成交股數'].str.replace(',','')
#     ret['open_price'] = ret['open_price'].str.replace(',','')
#     ret['最高價'] = ret['最高價'].str.replace(',','')
#     ret['最低價'] = ret['最低價'].str.replace(',','')
#     ret['close_price'] = ret['close_price'].str.replace(',','')
#     global aaa
#     aaa[key] = ret
#     return ret

def initRet3(ret):
    ret = ret.set_index('CODE')
    # ret['成交金額'] = ret['成交金額'].str.replace(',','')
    # ret['成交股數'] = ret['成交股數'].str.replace(',','')
    # ret['open_price'] = ret['open_price'].str.replace(',','')
    # ret['最高價'] = ret['最高價'].str.replace(',','')
    # ret['最低價'] = ret['最低價'].str.replace(',','')
    ret['close_price'] = ret['close_price'].str.replace(',','')
    return ret

def downloadStockData():
    import pymysql
    from tqdm import tqdm 
    # tqdm.pandas()
    conn = pymysql.connect(host=_host,port=_port,user=_user,password=_password,database=_database, charset='utf8')
    df = pd.read_sql("select * from stockall ORDER BY DATE ASC", con=conn)
    # df.progress_apply(lambda x: x, axis=1)
    df.info(memory_usage="deep")
    df.to_csv('stockall.csv', index=False)

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
            data[date] = initRet(crawl_price(date))
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
    close = pd.DataFrame({k:d['close_price'] for k,d in data.items()}).transpose()
    close.index = pd.to_datetime(close.index)
    for column in close:
        close[column].replace('--', np.nan, method = 'pad', inplace = True)
        close[column].replace('--', np.nan, method = 'bfill', inplace = True)
    close = close.astype(float)
    close.head()
    GoldX = rising_curve(close)
    #選出來的清單
    sid_list = GoldX[GoldX==True].index
    return sid_list

def getData_mysql_bak(data_start,test_sdate,MYUSER):
    import MySQLdb
    data = {}
    conn = MySQLdb.connect(host='118.150.153.139',port=32769,user='root',password='acha',database='twstock')
    conn.set_character_set('utf8')
    cursor = conn.cursor()
    cursor.execute("select DISTINCT DATE from stockall where DATE >= %s and DATE <= %s"%(data_start,test_sdate))
    tmp = cursor.fetchall()
    for _DATE in tmp:
        df = pd.read_sql('SELECT * FROM stockall WHERE DATE = %s'%(_DATE[0]), con=conn)
        data[_DATE[0]] = initRet2(df)
    # sector = df.groupby("DATE")
    close = pd.DataFrame({k:d['close_price'] for k,d in data.items()}).transpose()
    close.index = pd.to_datetime(close.index)
    for column in close:
        close[column].replace('--', np.nan, method = 'pad', inplace = True)
        close[column].replace('--', np.nan, method = 'bfill', inplace = True)
    close = close.astype(float)
    close.head()
    # print(close)
    GoldX = rising_curve(close)
    #選出來的清單
    sid_list = GoldX[GoldX==True].index
    # print(sid_list)
    return sid_list

def getStockallDataByCODE_mysql_step1(data_start,test_sdate):
    import pymysql
    import StockBean
    data = {}

    conn = pymysql.connect(host=_host,port=_port,user=_user,password=_password,database=_database, charset='utf8')
#     conn.set_charset_collation('utf8')

    df = pd.read_sql("select DATE,CODE,open_price,最高價,最低價,close_price from stockall where DATE between %s and %s ORDER BY DATE ASC"%(data_start,test_sdate), con=conn)
    for column in df:
        if column == 'NAME':
            df.pop(column)
        elif column != 'CODE' :
            df[column].replace('--', np.nan, method = 'pad', inplace = True)
            df[column].replace('--', np.nan, method = 'bfill', inplace = True)
    sector = df.groupby("CODE")
    for code in sector.groups.keys():
        data[code] = initRet3(sector.get_group(code))
    return data

def getStockallData_mysql_step1(data_start,test_sdate):
    import pymysql
    import StockBean
    data = {}

    conn = pymysql.connect(host=_host,port=_port,user=_user,password=_password,database=_database, charset='utf8')
#     conn.set_charset_collation('utf8')

    df = pd.read_sql("select * from stockall where DATE between %s and %s ORDER BY DATE ASC"%(data_start,test_sdate), con=conn)
    sector = df.groupby("DATE")
    for date in sector.groups.keys():
        data[date] = initRet2(sector.get_group(date))
    return data

def getStockallData_mysql_step1_1(data,data_start):
    import pymysql
    import StockBean
    import datetime
    newData = {}
    for key in data.keys():
        newData[key] = data[key]
    conn = pymysql.connect(host=_host,port=_port,user=_user,password=_password,database=_database, charset='utf8')
    # data_start = datetime.datetime.now().strftime("%Y%m%d")
    df = pd.read_sql("select * from stockall where DATE > %s ORDER BY DATE ASC"%(data_start), con=conn)
    sector = df.groupby("DATE")
    for add_date in sector.groups.keys():
        newData[add_date] = initRet2(sector.get_group(add_date))
    return newData

def getStockallData_mysql_step2(data_start,test_sdate,_MYUSER,data):
    import pymysql
    import StockBean
    conn = pymysql.connect(host='118.150.153.139',port=32769,user='root',password='acha',database='twstock', charset='utf8')

    GoldX = rising_curve(data)
    #選出來的清單
    sid_list = GoldX[GoldX==True].index
    
    df2 = pd.read_sql("select * from stockall where DATE > %s ORDER BY DATE ASC"%(test_sdate), con=conn)
    sector2 = df2.groupby("DATE")
    stockall_testRunLog_list = []
    for date in sector2.groups.keys():
        newData = initRet2(sector2.get_group(date))
        # 日均量
        # volume = getDF(data,'成交股數')
        # volume5 = volume.rolling(5,min_periods=5).mean()
        # 日均線
        close = getDF(data,'close_price')

        openPrice = getDF(data,'open_price')

        high = getDF(data,'最高價')

        low = getDF(data,'最低價')
        close10 = close.rolling(10,min_periods=10).mean()
        close5 = close.rolling(5,min_periods=5).mean()
        #賣股
        if len(_MYUSER._myStockData) > 0:
            mystockdata = _MYUSER._myStockData
            for mystockbeanCode in list(mystockdata):
                mystockbean = mystockdata[mystockbeanCode]
                if mystockbeanCode in newData.open_price and '--' != newData.open_price[mystockbeanCode]:
                    nowprice = float(newData.open_price[str(mystockbean._code)])
                    mycost = float(mystockbean._cost)
                    #以均線賣
                    if nowprice < close5[mystockbean._code].iloc[-1] and nowprice < close10[mystockbean._code].iloc[-1] and mystockbean._code not in sid_list:
                        _StockBean = StockBean.StockBean(mystockbean._code,newData.NAME[mystockbean._code],1000,nowprice,nowprice)
                        _MYUSER.sellStock(_StockBean,date)
                    #停損
                    elif (nowprice-mycost)/mycost <= -0.05 and mystockbean._code not in sid_list:
                        _StockBean = StockBean.StockBean(mystockbean._code,newData.NAME[mystockbean._code],1000,nowprice,nowprice)
                        _MYUSER.sellStock(_StockBean,date)
                    #以%賣
                    # #獲利賣出
                    # if (nowprice-mycost)/mycost >= 0.1 and mystockbean._code not in sid_list:
                    #     _StockBean = StockBean.StockBean(mystockbean._code,newData.NAME[mystockbean._code],1000,nowprice,nowprice)
                    #     _MYUSER.sellStock(_StockBean,date)
                    # #停損
                    # elif (nowprice-mycost)/mycost <= -0.05 and mystockbean._code not in sid_list:
                    #     _StockBean = StockBean.StockBean(mystockbean._code,newData.NAME[mystockbean._code],1000,nowprice,nowprice)
                    #     _MYUSER.sellStock(_StockBean,date)
        #買股
        buyList = selectBuy(data_start,data,sid_list,close,openPrice,high,low)
        for code in buyList:
            _StockBean = StockBean.StockBean(code,newData.NAME[code],2000,newData.open_price[code],newData.open_price[code])
            _MYUSER.buyStock(_StockBean)
        #收盤 更新持股現價
        if len(_MYUSER._myStockData) > 0:
            for mystockbeanCode in list(_MYUSER._myStockData):
                if mystockbeanCode in newData.open_price and newData.open_price[mystockbeanCode] != '--':
                    _MYUSER.updateStockNowPrice(mystockbeanCode,newData.close_price[mystockbeanCode])
        
        data[date] = newData
        # print(close)
        GoldX = rising_curve(data)
        #選出來的清單
        sid_list = GoldX[GoldX==True].index
        msg = _MYUSER.allMoney(date)
        cursor = conn.cursor()
        if _MYUSER._id == None :
            cursor.execute("select MAX(DISTINCT id) from stockall_testRunLog ")
            tmp = cursor.fetchall()
            for _id in tmp:
                _MYUSER.setId(int(_id[0])+1)
        
        result = (_MYUSER._id,msg[0], _MYUSER._oldmoney,msg[1])
        stockall_testRunLog_list.append(result)
    sql = 'insert into stockall_testRunLog(id,date,momey,msg) values (%s,%s,%s,"%s")'
    cursor.executemany(sql, stockall_testRunLog_list)
    conn.commit()

def getData_mysql(data_start,test_sdate,_MYUSER,dataType):
    import pymysql
    import StockBean
    data = {}
    newDataList = {}
    if dataType == "csv":
        cols = ['DATE','CODE','NAME','成交股數','open_price','最高價','最低價','close_price', '本益比']
        df = pd.read_csv("stockall.csv", usecols=cols)
    else:
        conn = getDBconnect()
        df = pd.read_sql("select * from stockall where DATE between %s and %s ORDER BY DATE ASC"%(data_start,test_sdate), con=conn)
    
    data ,newDataList = initStockData(df,test_sdate)
    # sector = df.groupby("DATE")
    # for date in tqdm(sector.groups.keys()):
    #     _date = datetime.strptime(str(date),'%Y%m%d')
    #     if date < int(test_sdate):
    #         data[_date] = initRet2(sector.get_group(date))
    #     else:
    #         newDataList[_date] = initRet2(sector.get_group(date))
    
    # GoldX = rising_curve(data)
    # #選出來的清單
    # sid_list = GoldX[GoldX==True].index
    
    dateList = []
    if dataType == "csv":
        for date in newDataList.keys():
            dateList.append(date)
        dateList.sort()
    else:
        conn = getDBconnect()
        df2 = pd.read_sql("select * from stockall where DATE > %s ORDER BY DATE ASC"%(test_sdate), con=conn)
        sector2 = df2.groupby("DATE")
        dateList = sector2.groups.keys()

    stockall_testRunLog_list = []
    for date in dateList:
        _date = date.strftime('%Y-%m-%d')
        # _date = date
        if _MYUSER._stop:
            _MYUSER.addMsg("終止程式")
            break
        if dataType == "csv":
            newData = newDataList[date]
        else:
            newData = initRet2(sector2.get_group(date))
    # cursor.execute("select DISTINCT DATE from stockall where DATE > %s ORDER BY DATE ASC"%(test_sdate))
    # tmp = cursor.fetchall()
    # cursor.close()
    # for _DATE in tmp:
    #     df = pd.read_sql('SELECT * FROM stockall WHERE DATE = %s'%(_DATE[0]), con=conn)
    #     newData = initRet2(df)
        _newData = {}
        colnms = ['open_price','最高價','最低價','close_price']
        # with concurrent.futures.ProcessPoolExecutor (max_workers=cpu_count()) as executor:
        #     futures = [executor.submit(getDF,data,colnm) for colnm in tqdm(colnms)]
        #     waitData = wait(futures, return_when=ALL_COMPLETED)
        #     for d in tqdm(waitData.done):
        #         _newData[d.result()[0]] = d.result()[1]
        # close = _newData['close_price']
        # openPrice = _newData['open_price']
        # high = _newData['最高價']
        # low = _newData['最低價']
        for colnm in colnms:
            t1 = time.time()
            _newData[colnm] = getDF(data,colnm)[1]
            _colnm = colnm
            if _colnm is '最高價':
                _colnm = 'high'
            elif _colnm is '最低價':
                _colnm = 'low'
            # tqdm.pandas(desc="%s bar!"%(_colnm))
            # _newData[colnm].progress_apply(lambda x: x, axis=1)
            t2 = time.time()
            print('%s: '%(_colnm) + str(round(t2-t1, 2)) + ' seconds')
        close = _newData['close_price']
        openPrice = _newData['open_price']
        high = _newData['最高價']
        low = _newData['最低價']

        GoldX = rising_curve(data,close,openPrice)
        #選出來的清單
        sid_list = GoldX[GoldX==True].index
        #選出要買的股
        buyList = selectBuy(data_start,data,sid_list,close,openPrice,high,low)
        #賣股
        if len(_MYUSER._myStockData) > 0:
            mystockdata = _MYUSER._myStockData
            sellList = selectSell(_MYUSER,sid_list,mystockdata,close,openPrice,high,low)
            for mystockbeanCode in sellList:
                if mystockbeanCode not in buyList:#在買股清單不要賣
                    if mystockbeanCode in newData.open_price and '--' != newData.open_price[mystockbeanCode]:
                        nowprice = float(newData.open_price[mystockbeanCode])
                        sellQ = 1000
                        if _MYUSER._isAftetDaySell:
                            sellQ = mystockdata[mystockbeanCode]._quantity
                        _StockBean = StockBean.StockBean(mystockbeanCode,newData.NAME[mystockbeanCode],sellQ,nowprice,nowprice)
                        _MYUSER.sellStock(_StockBean,_date)
        #買股
        for code in buyList:
            if code in newData.open_price and '--' != newData.open_price[code]:
                _StockBean = StockBean.StockBean(code,newData.NAME[code],1000,newData.open_price[code],newData.open_price[code])
                _MYUSER.buyStock(_StockBean)
        #收盤 更新持股現價
        if len(_MYUSER._myStockData) > 0:
            for mystockbeanCode in list(_MYUSER._myStockData):
                if mystockbeanCode in newData.open_price and newData.open_price[mystockbeanCode] != '--':
                    _MYUSER.updateStockNowPrice(mystockbeanCode,newData.close_price[mystockbeanCode])
        
        data[date] = newData
        # print(close)
        # GoldX = rising_curve(data)
        # #選出來的清單
        # sid_list = GoldX[GoldX==True].index
        _MYUSER.printAllStocksData(_date)
        msg = _MYUSER.allMoney(_date)
        if _MYUSER._id == None :
            try:
                conn = getDBconnect()
                cursor = conn.cursor()
                cursor.execute("select MAX(DISTINCT id) from stockall_testRunLog ")
                tmp = cursor.fetchall()
                for _id in tmp:
                    _MYUSER.setId(int(_id[0])+1)
                sql = 'insert into stockall_testRunLog(id,date,momey,msg) values (%s,%s,%s,"%s")'%(_MYUSER._id,_date,_MYUSER._money,'開始')
                cursor.execute(sql)
                conn.commit()
            except:
                _MYUSER.setId(99999)
        result = (_MYUSER._id,msg[0], _MYUSER._oldmoney,msg[1])
        stockall_testRunLog_list.append(result)
    sql = 'insert into stockall_testRunLog(id,date,momey,msg) values (%s,%s,%s,"%s")'
    if len(stockall_testRunLog_list) > 0: 
        conn = getDBconnect()
        conn.ping(True)
        cursor = conn.cursor()
        cursor.executemany(sql, stockall_testRunLog_list)
        conn.commit()
    _MYUSER.setIsStopOk(True)
    # return sid_list

#處理選出來的股票
def selectBuy(data_start,data,sid_list,close,openPrice,high,low):
    # import twstock
    sid_list = macd(data,sid_list,close,openPrice,high,low)
    # close20 = close.rolling(20,min_periods=20).mean()
    # close10 = close.rolling(10,min_periods=10).mean()
    # close5 = close.rolling(5,min_periods=5).mean()
    newSid_list = []
    for code in tqdm(sid_list):
        # codeinfo = twstock.codes[code]
        # if codeinfo is None and codeinfo.group == "金融保險業":
        #     continue

        close240 = close[code].rolling(240,min_periods=240).mean()
        close60 = close[code].rolling(60,min_periods=60).mean()
        close20 = close[code].rolling(20,min_periods=20).mean()
        close10 = close[code].rolling(10,min_periods=10).mean()
        close5 = close[code].rolling(5,min_periods=5).mean()

        beforeClosePrice = close[code].iloc[-1]
        a1 = close5.iloc[-2] - close10.iloc[-2]
        a2 = close5.iloc[-2] - close20.iloc[-2]
        a3 = close10.iloc[-2] - close20.iloc[-2]
        a4 = close20.iloc[-2] > close60.iloc[-2]
        a5 = close60.iloc[-2] > close240.iloc[-2]
        # if a5 and a4 and (a1 < 0.3 or a1 > 0) and (a2 < 0.3 or a2 > 0) and (a3 < 0.3 or a3 > 0) and beforeClosePrice > close5.iloc[-1] and beforeClosePrice > 10:
        #     newSid_list.append(code)
        if (a1 < 0.35 or a1 > 0) and (a2 < 0.35 or a2 > 0) and (a3 < 0.35 or a3 > 0) and beforeClosePrice > close5.iloc[-1] and beforeClosePrice > 10:
            newSid_list.append(code)
        # if nowprice > close5[code].iloc[-1] and nowprice > close10[code].iloc[-1] and nowprice > close20[code].iloc[-1]:
        #     newSid_list.append(code)
    if len(newSid_list) <= 0:
        print('無選出股票')
    return newSid_list

#處理選出來賣的股票
def selectSell(_MYUSER,sid_list,mystockdata,close,openPrice,high,low):
    sellList = []
    for mystockbeanCode in list(mystockdata):
        if _MYUSER._isAftetDaySell: #隔日沖
            sellList.append(mystockbeanCode)
        else :
            dif,dea,macd = ta.MACD(close[mystockbeanCode].values, fastperiod=12, slowperiod=26, signalperiod=9)
            mystockbean = mystockdata[mystockbeanCode]
            close20 = close[mystockbeanCode].rolling(20,min_periods=20).mean()
            close10 = close[mystockbeanCode].rolling(10,min_periods=10).mean()
            close5 = close[mystockbeanCode].rolling(5,min_periods=5).mean()
            # nowprice = float(newData.open_price[str(mystockbean._code)])
            closePrice = close[mystockbeanCode].iloc[-1]
            mycost = float(mystockbean._cost)
            # #以均線賣
            # if closePrice < close5.iloc[-1] and closePrice < close10.iloc[-1] and mystockbean._code not in sid_list and closePrice < close20.iloc[-1]:
            #     sellList.append(mystockbeanCode)
            #以均線賣
            if closePrice < close5.iloc[-1] and closePrice < close10.iloc[-1] and mystockbean._code not in sid_list:
                sellList.append(mystockbeanCode)
            #macd死叉
            elif macd[-2] > 0 and macd[-1] < 0:
                sellList.append(mystockbeanCode)
            elif dif[-1] >2:
                sellList.append(mystockbeanCode)
            #停損
            elif (closePrice-mycost)/mycost <= -0.05 and mystockbean._code not in sid_list:
                sellList.append(mystockbeanCode)
            # elif ta.CDLLADDERBOTTOM(openPrice[mystockbeanCode],high[mystockbeanCode],low[mystockbeanCode],close[mystockbeanCode])[-1]!=0:
            #     sellList.append(mystockbeanCode)
            # elif ta.CDLIDENTICAL3CROWS(openPrice[mystockbeanCode],high[mystockbeanCode],low[mystockbeanCode],close[mystockbeanCode])[-1]!=0:
            #     sellList.append(mystockbeanCode)
            # # 名稱：Hanging Man 上吊線
            # # 簡介：一日K線模式，形狀與錘子類似，處於上升趨勢的頂部，預示著趨勢反轉。
            elif ta.CDLHANGINGMAN(openPrice[mystockbeanCode],high[mystockbeanCode],low[mystockbeanCode],close[mystockbeanCode])[-1]!=0:
                sellList.append(mystockbeanCode)
            # # 名稱：Evening Star 暮星
            # # 簡介：三日K線模式，與晨星相反，上升趨勢中，第一日陽線，第二日價格振幅較小，第三日陰線，預示頂部反轉。
            # elif ta.CDLEVENINGSTAR(openPrice[mystockbeanCode],high[mystockbeanCode],low[mystockbeanCode],close[mystockbeanCode])[-1]!=0:
            #     sellList.append(mystockbeanCode)
            # # 名稱：Evening Doji Star 十字暮星
            # # 簡介：三日K線模式，基本模式為暮星，第二日收盤價和開盤價相同，預示頂部反轉。
            # elif ta.CDLEVENINGDOJISTAR(openPrice[mystockbeanCode],high[mystockbeanCode],low[mystockbeanCode],close[mystockbeanCode])[-1]!=0:
            #     sellList.append(mystockbeanCode)
            # # 名稱：Dark Cloud Cover 烏雲壓頂
            # # 簡介：二日K線模式，第一日長陽，第二日開盤價高於前一日最高價，收盤價處於前一日實體中部以下，預示著股價下跌。
            elif ta.CDLDARKCLOUDCOVER(openPrice[mystockbeanCode],high[mystockbeanCode],low[mystockbeanCode],close[mystockbeanCode])[-1]!=0:
                sellList.append(mystockbeanCode)
            # # 名稱：Three-Line Strike 三線打擊
            # # 簡介：四日K線模式，前三根陽線，每日收盤價都比前一日高，開盤價在前一日實體內，第四日市場高開，收盤價低於第一日開盤價，預示股價下跌。
            elif ta.CDLDARKCLOUDCOVER(openPrice[mystockbeanCode],high[mystockbeanCode],low[mystockbeanCode],close[mystockbeanCode])[-1]!=0:
                sellList.append(mystockbeanCode)
            # # 名稱：Three Black Crows 三隻烏鴉
            # # 簡介：三日K線模式，連續三根陰線，每日收盤價都下跌且接近最低價，每日開盤價都在上根K線實體內，預示股價下跌。
            elif ta.CDLDARKCLOUDCOVER(openPrice[mystockbeanCode],high[mystockbeanCode],low[mystockbeanCode],close[mystockbeanCode])[-1]!=0:
                sellList.append(mystockbeanCode)
            # # 名稱：Two Crows 兩隻烏鴉
            # # 簡介：三日K線模式，第一天長陽，第二天高開收陰，第三天再次高開繼續收陰，收盤比前一日收盤價低，預示股價下跌。
            elif ta.CDLDARKCLOUDCOVER(openPrice[mystockbeanCode],high[mystockbeanCode],low[mystockbeanCode],close[mystockbeanCode])[-1]!=0:
                sellList.append(mystockbeanCode)
    return sellList

def runTEST():
    import StockBean
    import MYUSER

    _MYUSER = MYUSER.MYUSER(300000,{},True)
    # _StockBean = StockBean.StockBean("3645","達賣",2,40000,40000)
    # _MYUSER.buyStock(_StockBean)
    # _StockBean = StockBean.StockBean("3645","達賣",2,45000,45000)
    # _MYUSER.buyStock(_StockBean)
    # _StockBean = StockBean.StockBean("3645","達賣",2,50000,50000)
    # _MYUSER.sellStock(_StockBean)
    # _StockBean = StockBean.StockBean("3645","達賣",2,50000,50000)
    # _MYUSER.sellStock(_StockBean)
    getData_mysql(20150101,20190101,_MYUSER,"csv")
    print(_MYUSER._money)

def dfReplace(column,dfColumnData):
    dfColumnData.replace('--', np.nan, method = 'pad', inplace = True)
    dfColumnData.replace('--', np.nan, method = 'bfill', inplace = True)
    return [column,dfColumnData]

def dfloop(newDF):
    # with concurrent.futures.ProcessPoolExecutor (max_workers=cpu_count()) as executor:
    #     # for column in newDF:
    #     #     executor.submit(dfReplace(newDF[column]))
    #     futures = [executor.submit(dfReplace,column,newDF[column]) for column in tqdm(newDF)]
    #     waitData = wait(futures, return_when=ALL_COMPLETED)
    #     for d in waitData.done:
    #         newDF[d.result()[0]] = d.result()[1]
    # t1 = time.time()
    for column in newDF:
        dfReplace(column,newDF[column])
    # t2 = time.time()
    # print('dfloop dfReplace time elapsed: ' + str(round(t2-t1, 2)) + ' seconds')

    # t1 = time.time()
    newDF = newDF.astype(float)
    # t2 = time.time()
    # print('dfloop astype(float) time elapsed: ' + str(round(t2-t1, 2)) + ' seconds')
    # newDF.head()
    # newDF.info(memory_usage="deep")
    return newDF

def getDF(data,columnName,newData=None):
    # t1 = time.time()
    newDF = pd.DataFrame({k:d[columnName] for k,d in data.items()})
    # tqdm.pandas(desc="%s bar!"%(columnName))
    # newDF.progress_apply(lambda x: x, axis=1)
    # t2 = time.time()
    # print('pd.DataFram time elapsed: ' + str(round(t2-t1, 2)) + ' seconds')
    # t1 = time.time()
    newDF = newDF.transpose()
    # t2 = time.time()
    # print('transpose time elapsed: ' + str(round(t2-t1, 2)) + ' seconds')
    # t1 = time.time()
    newDF.index = pd.to_datetime(newDF.index)
    # t2 = time.time()
    # print('to_datetime time elapsed: ' + str(round(t2-t1, 2)) + ' seconds')
    # t1 = time.time()
    # newDF = dfloop(newDF)
    # t2 = time.time()
    # print('dfloop time elapsed: ' + str(round(t2-t1, 2)) + ' seconds')
    if newData is not None:
        newData[columnName] = newDF
    return [columnName,newDF]

def getDF_ALL(data):
    newDF = pd.DataFrame(data.items()).transpose()
    newDF.index = pd.to_datetime(newDF.index)
    for column in newDF:
        newDF[column].replace('--', np.nan, method = 'pad', inplace = True)
        newDF[column].replace('--', np.nan, method = 'bfill', inplace = True)
    newDF = newDF.astype(float)
    newDF.head()
    return newDF

def getDF_notFloat(data,columnName):
    newDF = pd.DataFrame({k:d[columnName] for k,d in data.items()}).transpose()
    newDF.index = pd.to_datetime(newDF.index)
    for column in newDF:
        newDF[column].replace('--', np.nan, method = 'pad', inplace = True)
        newDF[column].replace('--', np.nan, method = 'bfill', inplace = True)
    newDF.head()
    return newDF

def macd(data,sid_list,close,openPrice,high,low):
    t1 = time.time()
    # import test
    if close is None:
        close = getDF(data,'close_price')

    if openPrice is None:
        openPrice = getDF(data,'open_price')

    if high is None:
        high = getDF(data,'最高價')

    if low is None:
        low = getDF(data,'最低價')

    # volume = getDF(data,'成交股數')

    # priceChange = getDF(data,'漲跌價差')

    # aaaa = getDF_notFloat(data,'漲跌')
    newSid_list = []
    for code in sid_list:
        selectCode = {
            'close':close[code],
            # 'open':openPrice[code],
            'high':high[code],
            'low':low[code],
            # 'volume': volume[code],
            # 'priceChange': priceChange[code],
            # 'aaaa': aaaa[code],
        }
        dif,dea,macd = ta.MACD(close[code].values, fastperiod=12, slowperiod=26, signalperiod=9)
        # DIF、DEA均为正，DIF向上突破DEA，发出买入信号
        # if dif[-1] > 0 and dea[-1] > 0 and macd[-2] < 0 and macd[-1] > 0:
        # if macd[-2] < 0 and macd[-1] > 0 and dif[-1] < 2:
        #     newSid_list.append(code)
        # DIF、DEA均为负，DIF向下突破DEA，发出卖出信号
        # if dif[-1] < 0 and dea[-1] < 0 and macd[-2] > 0 and macd[-1] < 0:
        #     short_bucket.append(stk)
        OSC1 = dif[-1] - macd[-1]
        OSC2 = dif[-2] - macd[-2]
        OSCOK = OSC1 > OSC2

        # SMA = ta.MA(close[code], timeperiod=10, matype=0)

        low_list = selectCode['low'].rolling(9,min_periods=1).min()
        high_list = selectCode['high'].rolling(9,min_periods=1).max()
        rsv = (selectCode['close'] - low_list) / \
              (high_list - low_list)*100
        selectCode['K'] = rsv.ewm(com=3).mean()
        selectCode['D'] = selectCode['K'].ewm(com=3).mean()
        selectCode['J'] = 3*selectCode['K']-2*selectCode['D']
        KDOK = selectCode['K'][-1] > selectCode['D'][-1] and selectCode['K'][-1] >= 20 and selectCode['K'][-1] < 80

        # k,d = ta.STOCH(high=high_list, low=low_list, close=close[code],
        #         fastk_period=9,
        #        slowk_period=3,
        #        slowk_matype=0,
        #        slowd_period=3,
        #        slowd_matype=0)
        # sig_k = k
        # sig_d = d
        # sig_j = k*3 - d*2

        # if KDOK and OSCOK and macd[-3] < macd[-2] and macd[-2] < macd[-1] and dif[-1] < 2 and dif[-1] > 0 and dea[-1] > 0 :
        #     newSid_list.append(code)
        if (OSCOK and KDOK) | (macd[-3] < macd[-2] and macd[-2] < macd[-1]) :
            newSid_list.append(code)




        # test.train_model(selectCode)
        # stock_predictor = StockPredictor.StockPredictor(selectCode)
        # stock_predictor.fit()
        # stock_predictor.predict_close_prices_for_days(500, with_plot=True)
        # print('')
        # talib2df(ta.MACD(selectCode)).plot()
        # selectCode['close'].plot(secondary_y=True)
    t2 = time.time()
    print('macd 耗時: ' + str(round(t2-t1, 2)) + ' seconds')
    return newSid_list

def talib2df(talib_output):
    if type(talib_output) == list:
        ret = pd.DataFrame(talib_output).transpose()
    else:
        ret = pd.Series(talib_output)
    return ret

def rising_curve(data,close=None,openPrice=None):
    t1 = time.time()
    if close is None:
        close = getDF(data,'close_price')[1]
    if openPrice is None:
        openPrice = getDF(data,'open_price')[1]
    

    # 5,10,20均線
    # close5 = ta.SMA(close,timeperiod = 5)
    # close10 = ta.SMA(close,timeperiod = 10)
    # close20 = ta.SMA(close,timeperiod = 20)
    close5 = close.rolling(5,min_periods=5).mean()
    close10 = close.rolling(10,min_periods=10).mean()
    close20 = close.rolling(20,min_periods=20).mean()

    A = close5.iloc[-1] > close10.iloc[-1]
    B = close10.iloc[-1] > close20.iloc[-1]
    # C = close5.iloc[-5] < close10.iloc[-5]
    D = close10.iloc[-5] < close20.iloc[-5]

    E = close5.iloc[-1] > close5.iloc[-2]
    F = close10.iloc[-1] > close10.iloc[-2]

    K1_ = (close.iloc[-1] - openPrice.iloc[-1]) / openPrice.iloc[-1] > 0.05
    K2_ = (close.iloc[-1] - openPrice.iloc[-1]) < 0
    #三紅K
    # K1 = close.iloc[-1] > openPrice.iloc[-1]
    # K2 = close.iloc[-2] > openPrice.iloc[-2]
    # K3 = close.iloc[-3] > openPrice.iloc[-3]
    # red3K = K1 & K2 & K3

    # 日均量
    volume = getDF(data,'成交股數')[1]
    # volume1 = volume.rolling(1,min_periods=1).mean()
    # volume5 = ta.SMA(volume,timeperiod = 5)
    volume5 = volume.rolling(5,min_periods=5).mean()
    v = volume5.iloc[-6]
    for i in range(-5,-1):
        v += volume5.iloc[i]
    G = (volume.iloc[-1] > (v/5)*1.3) & (volume.iloc[-1] > volume.iloc[-2]) & (volume.iloc[-2] > volume.iloc[-3])
    # volume120 = ta.SMA(volume,timeperiod = 120)
    volume120 = volume.rolling(120,min_periods=120).mean()
    VOL = volume120.iloc[-1] > 1000000

    # resultData = (A&B&D&E&F|K1_)&VOL&G
    resultData = (A&B&E&F&K2_)&VOL
    
    t2 = time.time()
    print('rising_curve 耗時: ' + str(round(t2-t1, 2)) + ' seconds')
    return resultData

def getSid_list_mqsql():
    data = getData()
    # close = pd.DataFrame({k:d['close_price'] for k,d in data.items()}).transpose()
    # close.index = pd.to_datetime(close.index)
    # for column in close:
    #     close[column].replace('--', np.nan, method = 'pad', inplace = True)
    #     close[column].replace('--', np.nan, method = 'bfill', inplace = True)
    # close = close.astype(float)
    # close.head()
    GoldX = rising_curve(data)
    #選出來的清單
    sid_list = GoldX[GoldX==True].index
    return sid_list

def runAdd2mysql(_day):
    import datetime
    import re,time,random
    import MySQLdb
    
    data = {}
    count = 0
    n_days = _day
    date = datetime.datetime.now()
    fail_count = 0
    allow_continuous_fail_count = 5
    while count < n_days:

        print('parsing', date)
        # 使用 crawPrice 爬資料
        try:
            _date = date.strftime("%Y%m%d")
            conn = MySQLdb.connect(host=_host,port=_port,user=_user,password=_password,database=_database)
            conn.set_character_set('utf8')
            cursor = conn.cursor()
            cursor.execute("select count(*) from stockall where DATE = '%s'"%(_date))
            tmp = [cursor.fetchall()]
            cursor.close
            conn.close
            if tmp[0][0][0] > 0:
                print('%s 這有資料'%(date))
            else:
                # 抓資料
                data_list = ret2list(date)
                addMysql(data_list)
                print('success!')
                fail_count = 0
            # count += 1
        except:
            fail_count += 1
            if date.weekday() == 5 or date.weekday() == 6:
                if fail_count == allow_continuous_fail_count:
                    # 假日爬不到
                    print('fail! 假日爬不到')
                    raise
                    break
        
        # 減一天
        date -= datetime.timedelta(days=1)
        i = random.randint(5,10)
        time.sleep(i)

def runAdd2mysql_ByFail():
    import datetime
    import re,time,random
    import pymysql
    
    conn = pymysql.connect(host=_host,port=_port,user=_user,password=_password,database=_database, charset='utf8')
#     conn.set_charset_collation('utf8')
    cursor = conn.cursor()

    cursor.execute("SELECT DATE FROM stockall_fail WHERE (week BETWEEN 0 and 4) and DATE BETWEEN (select min(DISTINCT DATE) from stockall) AND (select MAX(DISTINCT DATE) from stockall)")
    tmp_fail = cursor.fetchall()
    for _date in tmp_fail:
        cursor.execute("select count(*) from stockall where DATE = '%s'"%(_date))
        tmp = [cursor.fetchall()]
        if tmp[0][0][0] > 0:
            msg = ('%s 這有資料'%(_date))
            print(msg)
            # logging.debug(msg)
        else:
            # 使用 crawPrice 爬資料
            try:
                # 抓資料
                data_list = ret2list(datetime.datetime.strptime(_date[0], "%Y%m%d"))
                addMysql(data_list)
                print(_date[0],'success!')
                # logging.debug(_date,'success!')
                cursor.execute("delete from stockall_fail where DATE = %s"%(_date))
                conn.commit()
            except:
                msg = (_date[0],'fail! 爬不到')
                print(msg)
                # logging.debug(msg)

            i = random.randint(5,10)
            time.sleep(i)
    cursor.close
    conn.close

def runAddToDay2mysql():
    import datetime
    import re,time,random
    import MySQLdb
    
    data = {}
    count = 0
    n_days = 1
    date = datetime.datetime.now()
    fail_count = 0
    allow_continuous_fail_count = 5
    while count < n_days:

        print('parsing', date)
        # 使用 crawPrice 爬資料
        _date = date.strftime("%Y%m%d")
        conn = MySQLdb.connect(host='118.150.153.139',port=32769,user='root',password='acha',database='twstock')
        conn.set_character_set('utf8')
        cursor = conn.cursor()
        cursor.execute("select count(*) from stockall where DATE = '%s'"%(_date))
        tmp = [cursor.fetchall()]
        cursor.close
        conn.close
        if tmp[0][0][0] > 0:
            print('%s 這有資料'%(date))
            break
        else:
            try:
                # 抓資料
                data_list = ret2list(date)
                addMysql(data_list)
                print('success!')
                fail_count = 0
                count += 1
            except:
                fail_count += 1
                if date.weekday() == 5 or date.weekday() == 6:
                    if fail_count == allow_continuous_fail_count:
                        # 假日爬不到
                        print('fail! 假日爬不到')
                        raise
                        break
        
        # 減一天
        # date -= datetime.timedelta(days=1)
        i = random.randint(5,10)
        time.sleep(i)

def getData_mysql2(data_start,test_sdate):
    import MySQLdb
    import StockBean
    data = {}
    conn = MySQLdb.connect(host='118.150.153.139',port=32769,user='root',password='acha',database='twstock')
    conn.set_character_set('utf8')

    df = pd.read_sql("select * from stockall where DATE between %s and %s ORDER BY DATE ASC"%(data_start,test_sdate), con=conn)
    sector = df.groupby("DATE")
    for date in sector.groups.keys():
        data[date] = initRet2(sector.get_group(date))
    
    GoldX = rising_curve(data)
    #選出來的清單
    sid_list = GoldX[GoldX==True].index
    # 日均線
    close = getDF(data,'close_price')

    openPrice = getDF(data,'open_price')

    high = getDF(data,'最高價')

    low = getDF(data,'最低價')
    buyList = selectBuy(data_start,data,sid_list,close,openPrice,high,low)
    for code in buyList:
        print(code)

# aaa = {}
# _sector = None
def initStockData(df,test_sdate=None):
    # global _sector
    # global aaa
    # aaa = {}
    data = {}
    newDataList = {}
    df.info(memory_usage="deep")
    _sector = df.groupby("DATE")
    # keys = []
    # for date in _sector.groups.keys():
    #     keys.append(date)
    # with concurrent.futures.ProcessPoolExecutor (max_workers=cpu_count()) as executor:
    #     # for date in tqdm(_sector.groups.keys()):
    # # [initRet2(_sector.get_group(date),data,date) for date in tqdm(_sector.groups.keys())]
    #     futures = [executor.submit(initRet2,_sector.get_group(key),data,key) for key in tqdm(_sector.groups.keys())]
    # # executor = ProcessPoolExecutor(max_workers=cpu_count())
    # # for date in sector.groups.keys():
    # #     executor.submit(initRet2(sector.get_group(date),data,date))
    # # for number, fib_value in zip(sector.groups.keys(),executor.map(initRet2,sector.groups.items())):
    # #     data[number] = fib_value
    #     # process_results = [task.result() for task in as_completed(futures)]
    #     waitData = wait(futures, return_when=ALL_COMPLETED)
    #     for d in waitData.done:
    #         date = d.result().DATE[0]
    #         # _date = datetime.strptime(str(date),'%Y%m%d')
    #         if test_sdate is None:
    #             data[date] = d.result()
    #         elif date < int(test_sdate):
    #             data[date] = d.result()
    #         else:
    #             newDataList[date] = initRet2(_sector.get_group(date))
    for date in tqdm(_sector.groups.keys()):
        _date = datetime.strptime(str(date),'%Y%m%d')
        dfData = initRet2(_sector.get_group(date))
        # dfData = dfData.astype(float)
        if test_sdate is None:
            data[_date] = dfData
        elif date < int(test_sdate):
            data[_date] = dfData
        else:
            newDataList[_date] = dfData
    # data.items().sort
    # data = aaa
    # [(k,data[k]) for k in sorted(data.keys())]
    # [(k,newDataList[k]) for k in sorted(newDataList.keys())]
    return [data,newDataList]


def getData_csv(_MyFrame):
    # data = {}
    # tqdm.pandas()
    # dtypes = {"DATE": "uint8"}
    t1 = time.time()
    cols = ['DATE','CODE','NAME','成交股數','open_price','最高價','最低價','close_price', '本益比']
    df = pd.read_csv("stockall.csv",usecols=cols)
    t2 = time.time()
    print('read_csv elapsed: ' + str(round(t2-t1, 2)) + ' seconds')
    # tqdm.pandas()
    # df.progress_apply(lambda x: x, axis=1)
    # df = dd.read_csv("stockall.csv")
    # data_chunk = pd.concat(df)
    data = initStockData(df)[0]
    
    _newData = {}
    colnms = ['open_price','最高價','最低價','close_price']
    # with concurrent.futures.ProcessPoolExecutor (max_workers=cpu_count()) as executor:
    #     # for colnm in tqdm(colnms):
    #     #     executor.submit(getDF(data,colnm,_newData))
    #     futures = [executor.submit(getDF,data,colnm) for colnm in tqdm(colnms)]
    #     waitData = wait(futures, return_when=ALL_COMPLETED)
    #     for d in tqdm(waitData.done):
    #         _newData[d.result()[0]] = d.result()[1]
    # close = _newData['close_price']
    # openPrice = _newData['open_price']
    # high = _newData['最高價']
    # low = _newData['最低價']
    for colnm in colnms:
        t1 = time.time()
        _newData[colnm] = getDF(data,colnm)[1]
        _colnm = colnm
        if _colnm is '最高價':
            _colnm = 'high'
        elif _colnm is '最低價':
            _colnm = 'low'
        # tqdm.pandas(desc="%s bar!"%(_colnm))
        # _newData[colnm].progress_apply(lambda x: x, axis=1)
        t2 = time.time()
        print('%s: '%(_colnm) + str(round(t2-t1, 2)) + ' seconds')
    close = _newData['close_price']
    openPrice = _newData['open_price']
    high = _newData['最高價']
    low = _newData['最低價']
    # close = getDF(data,'close_price')[1]
    # tqdm.pandas(desc="%s bar!"%('close_price'))
    # close.progress_apply(lambda x: x, axis=1)

    # openPrice = getDF(data,'open_price')[1]
    # tqdm.pandas(desc="%s bar!"%('open_price'))
    # openPrice.progress_apply(lambda x: x, axis=1)

    # high = getDF(data,'最高價')[1]
    # tqdm.pandas(desc="%s bar!"%('最高價'))
    # high.progress_apply(lambda x: x, axis=1)

    # low = getDF(data,'最低價')[1]
    # tqdm.pandas(desc="%s bar!"%('最低價'))
    # low.progress_apply(lambda x: x, axis=1)

    GoldX = rising_curve(data,close,openPrice)
    #選出來的清單
    sid_list = GoldX[GoldX==True].index

    buyList = selectBuy(0,data,sid_list,close,openPrice,high,low)

    for code in buyList:
        print(code)
    if _MyFrame is not None:
        _MyFrame.contents.AppendText("程式選出的股票代號:%s"%(str(buyList)))
        _MyFrame.contents.AppendText('\n')
    return str(buyList)

def getStockall_testRunLog():
    import MySQLdb
    import StockBean
    data = {}
    conn = MySQLdb.connect(host='118.150.153.139',port=32769,user='root',password='acha',database='twstock')
    conn.set_character_set('utf8')

    df = pd.read_sql("select * from stockall_testRunLog WHERE id = (SELECT max(DISTINCT id) from stockall_testRunLog) ORDER BY DATE ASC", con=conn)
    df.head()
    for item in df.items():
        print(item)
    return df

def ShowRateData(_MYUSER):
    import datetime
    rateData = _MYUSER._rateData
    # rateData['date'].append(20100101)
    # rateData['rate'].append(2)
    # rateData['date'].append(20100102)
    # rateData['rate'].append(2)
    # rateData['date'].append(20100103)
    # rateData['rate'].append(4)
    # _X = pd.DataFrame({k:d['date'] for k,d in rateData.items()}).transpose()
    # _Y = pd.DataFrame({k:d['rate'] for k,d in rateData.items()}).transpose()
    # _Y.index = pd.to_datetime(rateData['date'])
    # _Y = _Y.astype(float)
    # _X = list(map(lambda x:datetime.datetime.strptime(str(x)), rateData['date']))
    # _Y = list(map(lambda x:float(x), rateData['rate']))
    # for item in rateData:
    #     X_train.append(item['rate']), "%Y%m%d"))
    #     y_train.append(datetime.datetime.strptime(str(item['date'])
    # plt.ion() #开启interactive mode 成功的关键函数
    # plt.figure(1)
    plt.plot(rateData['date'],rateData['rate'],'-r')
    # plt.draw()#注意此函数需要调用
    plt.show()

# runTEST()
# runAdd2mysql_ByFail()
# getData_mysql()
# runAddToDay2mysql()
# getSid_list(2)
# getData_mysql2(20150101,20190904)

runAdd2mysql(1)

# import test

def mytest():
    data = getStockallDataByCODE_mysql_step1(20150101,20190921)
    sector = data['3645']
    sector = sector.set_index('DATE')
    sector.index = pd.to_datetime(sector.index)
    sector = sector.astype(float)
    # sector = getDF(data['3645'],'close_price')
    sector= sector.dropna()
    # sector = data.get_group('3645')
    # sector = sector.set_index('DATE')
    # sector = sector.astype(float)
    # close = sector.close_price
    # sector= sector.dropna()
    # sector.head()
    # test.initData(sector.close_price.values)
    # test.start()
    dif,dea,macd = ta.MACD(sector.close_price.values, fastperiod=12, slowperiod=26, signalperiod=9)
    sector['dif'] = dif
    sector['dea'] = dea
    sector['macd'] = macd 
    sector.tail()
    sector['close_price'].plot(figsize=(12,4))
    sector[['dif','dea']].plot(figsize=(12,4))
    sector[['macd']].plot(figsize=(12,4), kind='bar', xticks=[], color='b')
    plt.show()

    sector.close_price.plot(figsize=(10,5)) 
    plt.ylabel("Gold ETF Prices") 
    # plt.show()

    sector['S_3'] = sector['close_price'].shift(1).rolling(window=3).mean() 
    sector['S_9']= sector['close_price'].shift(1).rolling(window=9).mean() 
    sector= sector.dropna() 
    X = sector[['S_3','S_9']] 
    X.head()
    y = sector['close_price'] 
    y.head()

    t=.8 
    t = int(t*len(sector)) 
    # Train dataset 
    X_train = X[:t] 
    y_train = y[:t] 
    # Test dataset 
    X_test = X[t:] 
    y_test = y[t:]
    #
    y_test2 = ['20190904']


    linear = LinearRegression().fit(X_train,y_train) 
    print("Gold ETF Price =", round(linear.coef_[0],2), "* 3 Days Moving Average", round(linear.coef_[1],2), "* 9 Days Moving Average +", round(linear.intercept_,2))

    predicted_price = linear.predict(X_test) 
    predicted_price = pd.DataFrame(predicted_price,index=y_test.index,columns = ['close_price']) 
    predicted_price.plot(figsize=(10,5)) 
    y_test.plot() 
    plt.legend(['predicted_price','actual_price']) 
    plt.ylabel("Gold ETF Price") 
    plt.show()
    r2_score = linear.score(X[t:],y[t:])*100 
    r_squared = float("{0:.2f}".format(r2_score))
    print(r_squared)