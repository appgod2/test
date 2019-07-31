import time
import twstock
import requests
import datetime
from IPython.display import clear_output

gf_high = 51.50
# Get price function
def subGetPrice(x):
    try:
        #註解: 透過twstock套件，取得股號對應資料
        GetStockList=twstock.realtime.get(x)
        #註解: 顯示取得的資料陣列
        #GetStockList
        #註解: 顯示陣列中[即時股價]並轉成浮點數
        if GetStockList['success'] == True:
            if GetStockList['realtime']['latest_trade_price'] != None:
                return GetStockList['realtime']['latest_trade_price']
            else:
                return None
        else:
            return None
    except:
        return '@error'
    
#Send message to Line Notifly    
def subLineNotify(msg):
    token = 'S/nkoXXKr5iMI/qWSBdoT5fgch591C3VCqpLrKRFtPAvsybTNu7GTXJAqQB0elx1T95usgs4IKt/j0i9qQQ82kjkymL4owhn1T0OMcEC1VS8DVE0XW6zZ4CP741fsCx6/KYyocCgpCp6Wb24peeblgdB04t89/1O/w1cDnyilFU='
    headers = {
         "Authorization": "Bearer " + token, 
         "Content-Type" : "application/x-www-form-urlencoded"
    }
    payload = {'message': '  ' + msg}
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    print(r.status_code)
    return r.status_code
        
# Timer function
def subTimer(n):
    #全域變數，記錄最高股價
    global gf_high
    try:
        while True:
            strPrice = str(subGetPrice('6213'))
            print(strPrice)
            if strPrice ==  '@error':
                #send error message to Line notify
                message = str(datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S')) + ': subGetPrice Try Error'
                subLineNotify(message)
                print('!!!!!!!!!!subGetPrice Error !!!!!!!!!!!!!!!')
                return
            elif  (strPrice ==  'None') or (strPrice ==  None):    
                time.sleep(n)   
            else:
                #超過最高股價0.5元，就發送line message通知
                if (float(strPrice) > gf_high) and ((float(strPrice) % 0.5) == 0):
                    gf_high = float(strPrice)
                    #send touch price message to Line notif
                    message = str(datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S')) + ' HighPrice: ' + strPrice
                    subLineNotify(message)
                    #清空printout後再顯示    
                    
                clear_output()    
                print(strPrice)
                time.sleep(n)   
    except:
        #send error message to Line notify
        message = str(datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S')) + ': subTimer Try Error'
        subLineNotify(message)
        print('!!!!!!!!!!subTimer Error !!!!!!!!!!!!!!!')
        return

#subLineNotify("HI")
#{Main function: n秒查一次股價}
#subTimer(3)