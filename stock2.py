import requests
from io import StringIO
import pandas as pd
import numpy as np
import talib as ta
import StockPredictor


def addMysql(data_list):
    import MySQLdb

    conn = MySQLdb.connect(host='118.150.153.139',port=32773,user='root',password='acha',database='twstock')
    conn.set_character_set('utf8')
    cursor = conn.cursor()
    sql = "insert into stockall(DATE,CODE,NAME,成交股數,成交筆數,成交金額,開盤價,最高價,最低價,收盤價,漲跌,漲跌價差,最後揭示買價,最後揭示買量,最後揭示賣價,最後揭示賣量,本益比,Unnamed) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
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
    close = pd.DataFrame({k:d['收盤價'] for k,d in data.items()}).transpose()
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
    close = pd.DataFrame({k:d['收盤價'] for k,d in data.items()}).transpose()
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

def getData_mysql(data_start,test_sdate,_MYUSER):
    import MySQLdb
    import StockBean
    data = {}
    conn = MySQLdb.connect(host='118.150.153.139',port=32773,user='root',password='acha',database='twstock')
    conn.set_character_set('utf8')

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
    # close = getDF(data,'收盤價')
    # print(close)
    GoldX = rising_curve(data)
    #選出來的清單
    sid_list = GoldX[GoldX==True].index
    
    df2 = pd.read_sql("select * from stockall where DATE > %s ORDER BY DATE ASC"%(test_sdate), con=conn)
    sector2 = df2.groupby("DATE")
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
        close = getDF(data,'收盤價')
        close10 = close.rolling(10,min_periods=10).mean()
        close5 = close.rolling(5,min_periods=5).mean()
        #賣股
        if len(_MYUSER._myStockData) > 0:
            mystockdata = _MYUSER._myStockData
            for mystockbeanCode in list(mystockdata):
                mystockbean = mystockdata[mystockbeanCode]
                if '--' != newData.開盤價[mystockbeanCode]:
                    nowprice = float(newData.開盤價[str(mystockbean._code)])
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
            _StockBean = StockBean.StockBean(code,newData.NAME[code],2000,newData.開盤價[code],newData.開盤價[code])
            _MYUSER.buyStock(_StockBean)
        #收盤 更新持股現價
        if len(_MYUSER._myStockData) > 0:
            for mystockbeanCode in list(_MYUSER._myStockData):
                if newData.開盤價[mystockbeanCode] != '--':
                    _MYUSER.updateStockNowPrice(mystockbeanCode,newData.收盤價[mystockbeanCode])
        
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
        cursor.execute('insert into stockall_testRunLog(id,date,momey,msg) values (%s,%s,%s,"%s")'%(_MYUSER._id,msg[0],_MYUSER._oldmoney,msg[1]))
        conn.commit()
    # return sid_list

#處理選出來的股票
def selectBuy(data_start,data,sid_list,newData,close):
    # macd(data_start,data,sid_list)
    close10 = close.rolling(10,min_periods=10).mean()
    close5 = close.rolling(5,min_periods=5).mean()
    newSid_list = []
    for code in sid_list:
        if newData is None:
            newSid_list.append(code)
        else:
            if '--' != newData.開盤價[code]:
                nowprice = float(newData.開盤價[code])
                if nowprice > close5[code].iloc[-1] and nowprice > close10[code].iloc[-1]:
                    newSid_list.append(code)
    return newSid_list

def runTEST():
    import StockBean
    import MYUSER

    _MYUSER = MYUSER.MYUSER(400000,{})
    # _StockBean = StockBean.StockBean("3645","達賣",2,40000,40000)
    # _MYUSER.buyStock(_StockBean)
    # _StockBean = StockBean.StockBean("3645","達賣",2,45000,45000)
    # _MYUSER.buyStock(_StockBean)
    # _StockBean = StockBean.StockBean("3645","達賣",2,50000,50000)
    # _MYUSER.sellStock(_StockBean)
    # _StockBean = StockBean.StockBean("3645","達賣",2,50000,50000)
    # _MYUSER.sellStock(_StockBean)
    getData_mysql(20190101,20190821,_MYUSER)
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

def getDF_notFloat(data,columnName):
    newDF = pd.DataFrame({k:d[columnName] for k,d in data.items()}).transpose()
    newDF.index = pd.to_datetime(newDF.index)
    for column in newDF:
        newDF[column].replace('--', np.nan, method = 'pad', inplace = True)
        newDF[column].replace('--', np.nan, method = 'bfill', inplace = True)
    newDF.head()
    return newDF

def macd(data_start,data,sid_list):
    import test
    close = getDF(data,'收盤價')

    open = getDF(data,'開盤價')

    high = getDF(data,'最高價')

    low = getDF(data,'最低價')

    volume = getDF(data,'成交股數')

    priceChange = getDF(data,'漲跌價差')

    aaaa = getDF_notFloat(data,'漲跌')

    for code in sid_list:
        selectCode = {
            'close':close[code],
            'open':open[code],
            'high':high[code],
            'low':low[code],
            'volume': volume[code],
            'priceChange': priceChange[code],
            'aaaa': aaaa[code],
        }
        low_list = selectCode['close'].rolling(9,min_periods=1).min()
        high_list = selectCode['close'].rolling(9,min_periods=1).max()
        rsv = (selectCode['close'] - low_list) / \
              (high_list - low_list)*100
        selectCode['K'] = rsv.ewm(com=2).mean()
        selectCode['D'] = selectCode['K'].ewm(com=2).mean()
        selectCode['J'] = 3*selectCode['K']-2*selectCode['D']

        # test.train_model(selectCode)
        # stock_predictor = StockPredictor.StockPredictor(selectCode)
        # stock_predictor.fit()
        # stock_predictor.predict_close_prices_for_days(500, with_plot=True)
        print('')
        # talib2df(ta.MACD(selectCode)).plot()
        # selectCode['close'].plot(secondary_y=True)

def talib2df(talib_output):
    if type(talib_output) == list:
        ret = pd.DataFrame(talib_output).transpose()
    else:
        ret = pd.Series(talib_output)
    return ret

def rising_curve(data):
    close = getDF(data,'收盤價')
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
    # close = pd.DataFrame({k:d['收盤價'] for k,d in data.items()}).transpose()
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
            conn = MySQLdb.connect(host='118.150.153.139',port=32773,user='root',password='acha',database='twstock')
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
    conn = MySQLdb.connect(host='118.150.153.139',port=32773,user='root',password='acha',database='twstock')
    conn.set_character_set('utf8')

    df = pd.read_sql("select * from stockall where DATE between %s and %s ORDER BY DATE ASC"%(data_start,test_sdate), con=conn)
    sector = df.groupby("DATE")
    for date in sector.groups.keys():
        data[date] = initRet2(sector.get_group(date))
    
    GoldX = rising_curve(data)
    #選出來的清單
    sid_list = GoldX[GoldX==True].index
    # 日均線
    close = getDF(data,'收盤價')
    buyList = selectBuy(data_start,data,sid_list,None,close)
    for code in buyList:
        print(code)

def getStockall_testRunLog():
    import MySQLdb
    import StockBean
    data = {}
    conn = MySQLdb.connect(host='118.150.153.139',port=32773,user='root',password='acha',database='twstock')
    conn.set_character_set('utf8')

    df = pd.read_sql("select * from stockall_testRunLog where id = max(id) ORDER BY DATE ASC", con=conn)
    for item in df.items():
        print(item)

runTEST()
# getData_mysql()
# runAddToDay2mysql()
# getSid_list(2)
# getData_mysql2(20150101,20190828)