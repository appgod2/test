# import MySQLdb
# import tushare as ts
# #將所有的股票名稱和股票代碼、行業、地區寫入到名爲allstock的表中，這個文件只需要執行一次

# #通過tushare庫獲取所有的A股列表
# stock_info = ts.get_stock_basics()
# #連接數據庫
# conn = MySQLdb.connect(host='127.0.0.1',user='root',password='acha',database='test2')
# conn.set_character_set('utf8')
# cursor = conn.cursor()

# codes = stock_info.index
# names = stock_info.name
# industrys = stock_info.industry
# areas = stock_info.area
# #通過for循環遍歷所有股票，然後拆分獲取到需要的列，將數據寫入到數據庫中
# a=0
# for i in range(0,len(stock_info)):
# 	print('insert into allstock (code,name,industry,area) values (%s,%s,%s,%s)',(codes[i],names[i],industrys[i],areas[i]))
# 	cursor.execute('insert into allstock (code,name,industry,area) values (%s,%s,%s,%s)',(codes[i],names[i],industrys[i],areas[i]))
# 	a += 1
# #統計所有A股數量
# print('共獲取到%d支股票'%a)

# conn.commit()
# cursor.close()
# conn.close()