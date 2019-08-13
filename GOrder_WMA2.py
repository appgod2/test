# 匯入模組
from haohaninfo import GOrder
import GOrder_GetKBar, datetime  

# Yuanta(元大證券)、Capital(群益證券)、Capital_Future(群益期貨)、Kgi(凱基證券)、Kgi_Future(凱基期貨)、Simulator(虛擬期貨)
Broker = 'Simulator'
# match(成交資訊)、commission(委託資訊)、updn5(上下五檔資訊)
Kind = 'match'
# 取即時報價的商品代碼(GOrder內需先訂閱該商品)
Prod = 'TXFH9'
# 取得當天日期
Date = datetime.datetime.now().strftime("%Y/%m/%d")
# 開始判斷時間
StartTime = datetime.datetime.strptime(Date + ' 09:00:00.00','%Y/%m/%d %H:%M:%S.%f')
# 定義報價指令的物件
a = GOrder.GOQuote()
# 定義下單指令的物件
b = GOrder.GOCommand()
# 定義K棒物件(1分K)
KBar = GOrder_GetKBar.KBar(Date,1)
# 固定式停損點數
StopLoss = 20
# 定義WMA快線及慢線期數、
FastN = 5
SlowN = 10
# 定義兩次交叉需間隔的時間
M = 8

# 進場判斷
CrossTime = None
Interval = datetime.timedelta(minutes = M)
for i in a.Describe(Broker,Kind,Prod):
    time = datetime.datetime.strptime(i[0],'%Y/%m/%d %H:%M:%S.%f')
    # print(time)
    price = float(i[2])
    volume = int(i[3])
    # 餵資料進K棒物件
    KBar.AddPrice(time,price,volume)
    # 取WMA值
    FastWMA = KBar.GetWMA(FastN)
    SlowWMA = KBar.GetWMA(SlowN)
    # 買賣方平均每筆成交口數
    AvgBuy = int(i[4]) / int(i[5])
    AvgSell = int(i[4]) / int(i[6])

    # K棒數量足夠計算lastMA，且超過開始判斷的時間才開始判斷
    if len(SlowWMA) > SlowN and time >= StartTime:
        # 當前快線、上一分鐘快線、當前慢線、上一分鐘慢線
        thisFastWMA = FastWMA[-1]
        lastFastWMA = FastWMA[-2]
        thisSlowWMA = SlowWMA[-1]
        lastSlowWMA = SlowWMA[-2]
        # 多單進場(趨勢偏多且WMA黃金交叉)
        if AvgBuy > AvgSell and lastFastWMA <= lastSlowWMA and thisFastWMA > thisSlowWMA:
            # 判斷是否第二次交叉，並且超過指定時間間隔
            if CrossTime is None:
                CrossTime = time + Interval
            elif time > CrossTime :
                # 送出市價單(券商名稱,商品代碼,多空方向,價格,口數,委託單類別,價格類別)
                OrderInfo = b.Order(Broker, Prod, 'B', '0', '1', 'IOC', 'MKT')
                # 印出委託單書號(GOrder內有委託單的詳細紀錄)
                print(OrderInfo)
                # 紀錄進場方向及進場價
                BS = 'B'
                OrderPrice = price
                # 跳出迴圈
                a.EndDescribe()
        # 空單進場(趨勢偏空且WMA死亡交叉)
        elif AvgBuy < AvgSell and lastFastWMA >= lastSlowWMA and thisFastWMA < thisSlowWMA:
            # 判斷是否第二次交叉，並且超過指定時間間隔
            if CrossTime is None:
                CrossTime = time + Interval
            elif time > CrossTime :    
                # 送出市價單(券商名稱,商品代碼,多空方向,價格,口數,委託單類別,價格類別)
                OrderInfo = b.Order(Broker, Prod, 'S', '0', '1', 'IOC', 'MKT')
                # 印出委託單書號(GOrder內有委託單的詳細紀錄)
                print(OrderInfo)
                # 紀錄進場方向及進場價
                BS = 'S'
                OrderPrice = price
                # 跳出迴圈
                a.EndDescribe()
	
# 出場判斷(取成交資訊)
for i in a.Describe(Broker,Kind,Prod):
    time = datetime.datetime.strptime(i[0],'%Y/%m/%d %H:%M:%S.%f')
    price = float(i[2])
    volume = int(i[3])
    # 餵資料進K棒物件
    KBar.AddPrice(time,price,volume)
    # 取WMA值
    FastWMA = KBar.GetWMA(FastN)
    SlowWMA = KBar.GetWMA(SlowN)
    # 當前快線、上一分鐘快線、當前慢線、上一分鐘慢線
    thisFastWMA = FastWMA[-1]
    lastFastWMA = FastWMA[-2]
    thisSlowWMA = SlowWMA[-1]
    lastSlowWMA = SlowWMA[-2]
    # 多單出場
    if BS == 'B':
        # WMA死亡交叉
        if lastFastWMA >= lastSlowWMA and thisFastWMA < thisSlowWMA:
            # 送出市價單(券商名稱,商品代碼,多空方向,價格,口數,委託單類別,價格類別)
            CoverInfo = b.Order(Broker, Prod, 'S', '0', '1', 'IOC', 'MKT')
            # 印出委託單書號(GOrder內有委託單的詳細紀錄)
            print(CoverInfo)
            print("多單出場WMA死亡交叉")
            # 跳出迴圈
            a.EndDescribe()
        # 固定式停損
        elif price <= OrderPrice - StopLoss:
            # 送出市價單(券商名稱,商品代碼,多空方向,價格,口數,委託單類別,價格類別)
            CoverInfo = b.Order(Broker, Prod, 'S', '0', '1', 'IOC', 'MKT')
            # 印出委託單書號(GOrder內有委託單的詳細紀錄)
            print(CoverInfo)
            print("多單出場固定式停損")
            # 跳出迴圈
            a.EndDescribe()    
    # 空單出場
    elif BS == 'S':
        # WMA黃金交叉
        if lastFastWMA <= lastSlowWMA and thisFastWMA > thisSlowWMA:
            # 送出市價單(券商名稱,商品代碼,多空方向,價格,口數,委託單類別,價格類別)
            CoverInfo = b.Order(Broker, Prod, 'B', '0', '1', 'IOC', 'MKT')
            # 印出委託單書號(GOrder內有委託單的詳細紀錄)
            print(CoverInfo)
            print("空單出場WMA黃金交叉")
            # 跳出迴圈
            a.EndDescribe()
		# 固定式停損
        elif price >= OrderPrice + StopLoss:
            # 送出市價單(券商名稱,商品代碼,多空方向,價格,口數,委託單類別,價格類別)
            CoverInfo = b.Order(Broker, Prod, 'B', '0', '1', 'IOC', 'MKT')
            # 印出委託單書號(GOrder內有委託單的詳細紀錄)
            print(CoverInfo)
            print("空單出場固定式停損")
            # 跳出迴圈
            a.EndDescribe()
        
        