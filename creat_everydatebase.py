import MySQLdb
import twstock
import re,time
import pandas as pd
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

def everdate(starttime,endtime):
    everdate2(starttime,endtime,'','')

#創建所有股票的表格以及插入每支股票的近段時間的行情，這個文件只需要執行一次！！！
#想要寫入哪一段時間的數據只需要修改starttime,endtime的時間就可以了
def everdate2(starttime,endtime,line_bot_api,event):
    text =""
    #連接數據庫
    # conn = MySQLdb.connect(host='127.0.0.1',user='root',password='acha',database='test2')
    # conn = MySQLdb.connect(host='us-cdbr-iron-east-02.cleardb.net',user='b23603b8be443b',password='10116eed',database='heroku_55f5167c61c71c0')
    conn = MySQLdb.connect(host='db4free.net',user='appgod',password='10021002',database='appgod_test')
    conn.set_character_set('utf8')
    cursor = conn.cursor()

    cursor.execute("select code from allstock_tw where _type='股票' and market in ('上市','上櫃')")
    value_code = cursor.fetchall()
    sql = "show tables;"
    cursor.execute(sql)
    tables = [cursor.fetchall()]
    table_list = re.findall('(\'.*?\')',str(tables))
    table_list = [re.sub("'",'',each) for each in table_list]
    #遍歷所有股票
    for i in value_code:
        code = i[0]
        table_name = 'stock_' + code
        if table_name in table_list:
            print("pass")
        else:
            #以stock_加股票代碼爲表名稱創建表格
            cursor.execute('create table ' + table_name + ' (date varchar(32),open varchar(32),close varchar(32),high varchar(32),low varchar(32),capacity varchar(32),p_change varchar(32),unique(date))')
        
        # stock_6207_2018_pd = pd.DataFrame(stock)
        #這裏使用try，except的目的是爲了防止一些停牌的股票，獲取數據爲空，插入數據庫的時候失敗而報錯
        #再使用for循環遍歷單隻股票每一天的行情
        # try:
        time.sleep(10)
        stock = twstock.Stock(code)
        stock.fetch_from(2019, 7)  # 獲取 2000 年 10 月至今日之股票資料
        print(i[0])
        for _data in stock.data:
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
    
    # except:
        # text = '%s這股票目前停牌'%(code)
        # print('%s這股票目前停牌'%(code))

    cursor.close()
    conn.close()
    if event != '':
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="完成"))

# everdate('','')