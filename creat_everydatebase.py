# !/usr/bin/python 
# coding:utf-8 

import sys
import traceback
import requests
import MySQLdb
sys.setrecursionlimit(10000000)


conn = MySQLdb.connect(host='127.0.0.1',port=3306,user='root',password='acha',database='twstock')
conn.set_character_set('utf8')
cursor = conn.cursor()

def everdate(starttime,endtime):
    everdate2(starttime,endtime,'','')

#創建所有股票的表格以及插入每支股票的近段時間的行情，這個文件只需要執行一次！！！
#想要寫入哪一段時間的數據只需要修改starttime,endtime的時間就可以了
def everdate2(year,month,line_bot_api,event):
#     import twstock
    import re,time
    import pandas as pd
    import threading
    from linebot import (
        LineBotApi, WebhookHandler
    )
    from linebot.exceptions import (
        InvalidSignatureError
    )
    from linebot.models import (
        MessageEvent, TextMessage, TextSendMessage,
    )
    
    text =""
    #連接數據庫
    # conn = MySQLdb.connect(host='127.0.0.1',user='root',password='acha',database='test2')
    # conn = MySQLdb.connect(host='us-cdbr-iron-east-02.cleardb.net',user='b23603b8be443b',password='10116eed',database='heroku_55f5167c61c71c0')
#     conn = mysql.connector.connect(host='db4free.net',user='appgod',password='10021002',database='appgod_test')
    print("mysql")
#     conn = mysql.connector.connect(host='mysql',port=3306,user='root',password='acha',database='twstock')
#     conn = mysql.connector.connect(host='172.17.0.1',port=32769,user='root',password='acha',database='twstock')
#     conn.set_charset_collation('utf8')
#     cursor = conn.cursor()
#     print(month)
    cursor.execute("select code from allstock_tw where _type='股票' and market in ('上市','上櫃') and code not in (select code from getstocks_status where yy = '%s' and mm = '%s')"%(year,month))
    value_code = cursor.fetchall()
    sql = "show tables;"
    cursor.execute(sql)
    tables = [cursor.fetchall()]
    table_list = re.findall('(\'.*?\')',str(tables))
    table_list = [re.sub("'",'',each) for each in table_list]
#     cursor.close()
#     conn.close()
    
    #遍歷所有股票
#     for i in value_code:
#         conn.reconnect()
#         cursor = conn.cursor()
#         code = i[0]
#         table_name = 'stock_' + code
#         if table_name in table_list:
#             a = 0
#         else:
#             cursor.execute('create table ' + table_name + ' (date varchar(32),open varchar(32),close varchar(32),high varchar(32),low varchar(32),capacity varchar(32),p_change varchar(32),unique(date))')
#             conn.commit()
            
#     cursor.close()
#     conn.close()
       
    #遍歷所有股票
    for i in value_code:
#         t = threading.Thread(target = getstock, args = (i[0],year, month))
#         t.start()
        connturlnum = 0
        getstock(i[0],year, month, connturlnum)
    
    print('%s,%s完成'%(year,month))
    cursor.close()
    conn.close()
    if event != '':
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="完成"))

def getstock(code,year, month, connturlnum):
    import re,time
    import threading
#     import mysql.connector
    
    thread_max = threading.BoundedSemaphore(100)
    time.sleep(10)
    try:
        stock = getstockdata(code,year, month)
        run(code,stock.data,year, month)
        s = requests.session()
        s.keep_alive = False
    except Exception as e:
#         print(e)
        error_class = e.__class__.__name__ #取得錯誤類型
        detail = e.args[0] #取得詳細內容
        cl, exc, tb = sys.exc_info() #取得Call Stack
        lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
        fileName = lastCallStack[0] #取得發生的檔案名稱
        lineNum = lastCallStack[1] #取得發生的行號
        funcName = lastCallStack[2] #取得發生的函數名稱
        errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
        print(errMsg)
        if "KeyError" == error_class:
#             conn = mysql.connector.connect(host='172.17.0.1',port=32769,user='root',password='acha',database='twstock')
#             conn.set_charset_collation('utf8')
#             cursor = conn.cursor()
            print("insert into getstocks_status (code,yy,mm,msg) values (%s,%s,%s,0)" % (code,year,month))
            cursor.execute("insert into getstocks_status (code,yy,mm,msg) values (%s,%s,%s,'0')" % (code,year,month))
            conn.commit
            print("換下一個")
        else:
            s = requests.session()
            s.keep_alive = False
            if connturlnum < 11:
                print("%s,%s,%s重連線"%(code,year,month))
                connturlnum += 1
                getstock(code,year, month, connturlnum)
    
#     t = threading.Thread(target = run, args = (code,stock.data))
#     t.start()

def getstockdata(code,year, month):
    import twstock
    
    stock = twstock.Stock(code)
    stock.fetch(year, month)  # 獲取 2000 年 10 月至今日之股票資料
    
    return stock


def run(code,stockdata,year, month):
#     import mysql.connector
    import re,time
    
    print(code)
#     conn = mysql.connector.connect(host='mysql',port=3306,user='root',password='acha',database='twstock')
#     conn = mysql.connector.connect(host='172.17.0.1',port=32769,user='root',password='acha',database='twstock')
#     conn.set_charset_collation('utf8')
#     cursor = conn.cursor()
    
    table_name = 'stock_' + code
    for _data in stockdata:
        #獲取股票日期，並轉格式（這裏爲什麼要轉格式，是因爲之前我2018-03-15這樣的格式寫入數據庫的時候，通過通配符%之後他居然給我把-符號當做減號給算出來了查看數據庫日期就是2000百思不得其解想了很久最後決定轉換格式）
        date = _data.date.strftime("%Y%m%d")
        _open = _data.open
        close = _data.close
        high = _data.high
        low = _data.low
        capacity = _data.capacity
        change = _data.change
        cursor.execute("select date from " + table_name)
        tmp = [cursor.fetchall()]
        tmp_list = re.findall('(\'.*?\')',str(tmp))
        tmp_list = [re.sub("'",'',each) for each in tmp_list]
        if date in tmp_list:
            text = '%s %s這股票有資料'%(code,date)
            print('%s %s這股票有資料'%(code,date))
        else:
            if date != None and _open != None and close != None and high != None and low != None and capacity != None and change != None :
                #插入每一天的行情
                text = '%s插入%s的行情'%(code,date)
                print('insert into '+table_name+ ' (date,open,close,high,low,capacity,p_change) values (%s,%s,%s,%s,%s,%s,%s)' % (date,_open,close,high,low,capacity,change))
                cursor.execute('insert into '+table_name+ ' (date,open,close,high,low,capacity,p_change) values (%s,%s,%s,%s,%s,%s,%s)' % (date,_open,close,high,low,capacity,change))
                conn.commit
    
    cursor.execute('insert into getstocks_status (code,yy,mm) values (%s,%s,%s)' % (code,year,month))
    conn.commit()

# everdate('','')

# y = 2019
# for y in range(2018,2020):
#     print(y)
#     mm = 12
#     #if y == 2019:
#     #    mm = 7
    
#     for m in range(1,mm):
#         print(m)
#         everdate2(y,m,'','')