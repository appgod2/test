import requests
from io import StringIO
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import talib as ta
# import StockPredictor

_host='118.150.153.139'
_port=32769
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


def addMysql(data_list):
    import MySQLdb

    conn = MySQLdb.connect(host='118.150.153.139',port=32769,user='root',password='acha',database='twstock')
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
    ret['成交金額'] = ret['成交金額'].str.replace(',','')
    ret['成交股數'] = ret['成交股數'].str.replace(',','')
    ret['開盤價'] = ret['開盤價'].str.replace(',','')
    ret['最高價'] = ret['最高價'].str.replace(',','')
    ret['最低價'] = ret['最低價'].str.replace(',','')
    ret['收盤價'] = ret['收盤價'].str.replace(',','')
    return ret

def initRet2(ret):
    ret = ret.set_index('CODE')
    ret['成交金額'] = ret['成交金額'].str.replace(',','')
    ret['成交股數'] = ret['成交股數'].str.replace(',','')
    ret['open_price'] = ret['open_price'].str.replace(',','')
    ret['最高價'] = ret['最高價'].str.replace(',','')
    ret['最低價'] = ret['最低價'].str.replace(',','')
    ret['close_price'] = ret['close_price'].str.replace(',','')
    return ret

def initRet3(ret):
    ret = ret.set_index('CODE')
    # ret['成交金額'] = ret['成交金額'].str.replace(',','')
    # ret['成交股數'] = ret['成交股數'].str.replace(',','')
    # ret['open_price'] = ret['open_price'].str.replace(',','')
    # ret['最高價'] = ret['最高價'].str.replace(',','')
    # ret['最低價'] = ret['最低價'].str.replace(',','')
    ret['close_price'] = ret['close_price'].str.replace(',','')
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
                        _MYUSER.sellStock(_StockBean,'')
                    #停損
                    elif (nowprice-mycost)/mycost <= -0.05 and mystockbean._code not in sid_list:
                        _StockBean = StockBean.StockBean(mystockbean._code,newData.NAME[mystockbean._code],1000,nowprice,nowprice)
                        _MYUSER.sellStock(_StockBean,'停損')
                    #以%賣
                    # #獲利賣出
                    # if (nowprice-mycost)/mycost >= 0.1 and mystockbean._code not in sid_list:
                    #     _StockBean = StockBean.StockBean(mystockbean._code,newData.NAME[mystockbean._code],1000,nowprice,nowprice)
                    #     _MYUSER.sellStock(_StockBean,'獲利賣出')
                    # #停損
                    # elif (nowprice-mycost)/mycost <= -0.05 and mystockbean._code not in sid_list:
                    #     _StockBean = StockBean.StockBean(mystockbean._code,newData.NAME[mystockbean._code],1000,nowprice,nowprice)
                    #     _MYUSER.sellStock(_StockBean,'停損')
        #買股
        buyList = selectBuy(data_start,data,sid_list,newData,close)
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

def getData_mysql(data_start,test_sdate,_MYUSER):
    import pymysql
    import StockBean
    data = {}
    conn = pymysql.connect(host='118.150.153.139',port=32769,user='root',password='acha',database='twstock', charset='utf8')

    df = pd.read_sql("select * from stockall where DATE between %s and %s ORDER BY DATE ASC"%(data_start,test_sdate), con=conn)
    sector = df.groupby("DATE")
    for date in sector.groups.keys():
        data[date] = initRet2(sector.get_group(date))
    
    # cursor = conn.cursor()
    # cursor.execute("select DISTINCT DATE from stockall where DATE between %s and %s ORDER BY DATE ASC"%(data_start,test_sdate))
    # tmp = cursor.fetchall()
    # for _DATE in tmp:
    #     df = pd.read_sql('SELECT * FROM stockall WHERE DATE = %s'%(_DATE[0]), con=conn)
    #     data[_DATE[0]] = initRet2(df)
    # sector = df.groupby("DATE")
    # close = getDF(data,'close_price')
    # print(close)
    GoldX = rising_curve(data)
    #選出來的清單
    sid_list = GoldX[GoldX==True].index
    
    df2 = pd.read_sql("select * from stockall where DATE > %s ORDER BY DATE ASC"%(test_sdate), con=conn)
    sector2 = df2.groupby("DATE")
    stockall_testRunLog_list = []
    for date in sector2.groups.keys():
        newData = initRet2(sector2.get_group(date))
    # cursor.execute("select DISTINCT DATE from stockall where DATE > %s ORDER BY DATE ASC"%(test_sdate))
    # tmp = cursor.fetchall()
    # cursor.close()
    # for _DATE in tmp:
    #     df = pd.read_sql('SELECT * FROM stockall WHERE DATE = %s'%(_DATE[0]), con=conn)
    #     newData = initRet2(df)
        # 日均量
        # volume = getDF(data,'成交股數')
        # volume5 = volume.rolling(5,min_periods=5).mean()
        # 日均線
        close = getDF(data,'close_price')
        #賣股
        if len(_MYUSER._myStockData) > 0:
            mystockdata = _MYUSER._myStockData
            sellList = selectSell(_MYUSER,sid_list,mystockdata,newData,close)
            for mystockbeanCode in sellList:
                nowprice = float(newData.open_price[mystockbeanCode])
                sellQ = 1000
                if _MYUSER._isAftetDaySell:
                    sellQ = mystockdata[mystockbeanCode]._quantity
                _StockBean = StockBean.StockBean(mystockbeanCode,newData.NAME[mystockbeanCode],sellQ,nowprice,nowprice)
                _MYUSER.sellStock(_StockBean,'')
        #買股
        buyList = selectBuy(data_start,data,sid_list,newData,close)
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
        _MYUSER.printAllStocksData(date)
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
    conn.ping(True)
    cursor.executemany(sql, stockall_testRunLog_list)
    conn.commit()
    # return sid_list

#處理選出來的股票
def selectBuy(data_start,data,sid_list,newData,close):
    sid_list = macd(data,sid_list)
    close20 = close.rolling(20,min_periods=20).mean()
    close10 = close.rolling(10,min_periods=10).mean()
    close5 = close.rolling(5,min_periods=5).mean()
    newSid_list = []
    for code in sid_list:
        if newData is None:
            newSid_list.append(code)
        else:
            if code in newData.open_price and '--' != newData.open_price[code]:
                newSid_list.append(code)
                # nowprice = float(newData.open_price[code])
                # if nowprice > close5[code].iloc[-1] and nowprice > close10[code].iloc[-1] and nowprice > close20[code].iloc[-1]:
                #     newSid_list.append(code)
    if len(newSid_list) <= 0:
        print('無選出股票')
    return newSid_list

#處理選出來賣的股票
def selectSell(_MYUSER,sid_list,mystockdata,newData,close):
    sellList = []
    for mystockbeanCode in list(mystockdata):
        if _MYUSER._isAftetDaySell: #隔日沖
            sellList.append(mystockbeanCode)
        else :
            dif,dea,macd = ta.MACD(close[mystockbeanCode].values, fastperiod=12, slowperiod=26, signalperiod=9)
            mystockbean = mystockdata[mystockbeanCode]
            if mystockbeanCode in newData.open_price and '--' != newData.open_price[mystockbeanCode]:
                close20 = close[mystockbeanCode].rolling(20,min_periods=20).mean()
                close10 = close[mystockbeanCode].rolling(10,min_periods=10).mean()
                close5 = close[mystockbeanCode].rolling(5,min_periods=5).mean()
                nowprice = float(newData.open_price[str(mystockbean._code)])
                mycost = float(mystockbean._cost)
                #以均線賣
                if nowprice < close5.iloc[-1] and nowprice < close10.iloc[-1] and mystockbean._code not in sid_list and nowprice < close20.iloc[-1]:
                    sellList.append(mystockbeanCode)
                #macd死叉
                elif macd[-2] > 0 and macd[-1] < 0:
                    sellList.append(mystockbeanCode)
                elif dif[-1] >2:
                    sellList.append(mystockbeanCode)
                #停損
                elif (nowprice-mycost)/mycost <= -0.1 and mystockbean._code not in sid_list:
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
    getData_mysql(20150101,20190101,_MYUSER)
    print(_MYUSER._money)

def getDF(data,columnName):
    newDF = pd.DataFrame({k:d[columnName] for k,d in data.items()}).transpose()
    newDF.index = pd.to_datetime(newDF.index)
    for column in newDF:
        newDF[column].replace('--', np.nan, method = 'pad', inplace = True)
        newDF[column].replace('--', np.nan, method = 'bfill', inplace = True)
    newDF = newDF.astype(float)
    newDF.head()
    return newDF

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

def macd(data,sid_list):
    # import test
    close = getDF(data,'close_price')

    # open = getDF(data,'open_price')

    # high = getDF(data,'最高價')

    # low = getDF(data,'最低價')

    # volume = getDF(data,'成交股數')

    # priceChange = getDF(data,'漲跌價差')

    # aaaa = getDF_notFloat(data,'漲跌')
    newSid_list = []
    for code in sid_list:
        selectCode = {
            'close':close[code],
            # 'open':open[code],
            # 'high':high[code],
            # 'low':low[code],
            # 'volume': volume[code],
            # 'priceChange': priceChange[code],
            # 'aaaa': aaaa[code],
        }
        dif,dea,macd = ta.MACD(close[code].values, fastperiod=12, slowperiod=26, signalperiod=9)
        # DIF、DEA均为正，DIF向上突破DEA，发出买入信号
        # if dif[-1] > 0 and dea[-1] > 0 and macd[-2] < 0 and macd[-1] > 0:
        if macd[-2] < 0 and macd[-1] > 0 and dif[-1] < 2:
            newSid_list.append(code)
        # DIF、DEA均为负，DIF向下突破DEA，发出卖出信号
        # if dif[-1] < 0 and dea[-1] < 0 and macd[-2] > 0 and macd[-1] < 0:
        #     short_bucket.append(stk)



        # low_list = selectCode['close'].rolling(9,min_periods=1).min()
        # high_list = selectCode['close'].rolling(9,min_periods=1).max()
        # rsv = (selectCode['close'] - low_list) / \
        #       (high_list - low_list)*100
        # selectCode['K'] = rsv.ewm(com=2).mean()
        # selectCode['D'] = selectCode['K'].ewm(com=2).mean()
        # selectCode['J'] = 3*selectCode['K']-2*selectCode['D']

        # test.train_model(selectCode)
        # stock_predictor = StockPredictor.StockPredictor(selectCode)
        # stock_predictor.fit()
        # stock_predictor.predict_close_prices_for_days(500, with_plot=True)
        # print('')
        # talib2df(ta.MACD(selectCode)).plot()
        # selectCode['close'].plot(secondary_y=True)
    return newSid_list

def talib2df(talib_output):
    if type(talib_output) == list:
        ret = pd.DataFrame(talib_output).transpose()
    else:
        ret = pd.Series(talib_output)
    return ret

def rising_curve(data):
    close = getDF(data,'close_price')
    # 5,10,20均線
    close5 = close.rolling(5,min_periods=5).mean()
    close10 = close.rolling(10,min_periods=10).mean()
    close20 = close.rolling(20,min_periods=20).mean()

    A = close5.iloc[-1] > close10.iloc[-1]
    B = close10.iloc[-1] > close20.iloc[-1]
    C = close5.iloc[-5] < close10.iloc[-5]
    D = close10.iloc[-5] < close20.iloc[-5]
    # 日均量
    volume = getDF(data,'成交股數')
    volume5 = volume.rolling(5,min_periods=5).mean()
    VOL = volume5.iloc[-1] > 1000000

    return A&B&C&D&VOL

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
            conn = MySQLdb.connect(host='118.150.153.139',port=32769,user='root',password='acha',database='twstock')
            conn.set_character_set('utf8')
            cursor = conn.cursor()
            cursor.execute("select count(*) from stockall where 日期 = '%s'"%(_date))
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

    cursor.execute("SELECT 日期 FROM stockall_fail WHERE (week BETWEEN 0 and 4) and 日期 BETWEEN (select min(DISTINCT DATE) from stockall) AND (select MAX(DISTINCT DATE) from stockall)")
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
                cursor.execute("delete from stockall_fail where 日期 = %s"%(_date))
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
    buyList = selectBuy(data_start,data,sid_list,None,close)
    for code in buyList:
        print(code)

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

# runTEST()
# runAdd2mysql_ByFail()
# getData_mysql()
# runAddToDay2mysql()
# getSid_list(2)
# getData_mysql2(20150101,20190904)
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