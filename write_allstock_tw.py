def run():
	import MySQLdb
	import twstock
	# import tushare as ts
	#將所有的股票名稱和股票代碼、行業、地區寫入到名爲allstock的表中，這個文件只需要執行一次

	#通過tushare庫獲取所有的A股列表
	# stock_info = ts.get_stock_basics()
	#連接數據庫
	# conn = MySQLdb.connect(host='127.0.0.1',user='root',password='acha',database='test2')
	# conn = MySQLdb.connect(host='us-cdbr-iron-east-02.cleardb.net',user='b23603b8be443b',password='10116eed',database='heroku_55f5167c61c71c0')
	# conn = MySQLdb.connect(host='db4free.net',user='appgod',password='10021002',database='appgod_test')
	conn = MySQLdb.connect(host='118.150.153.139',port=32810,user='root',password='acha',database='twstock')
	conn.set_character_set('utf8')
	cursor = conn.cursor()

	# print(twstock.codes)
	cursor.execute('create table allstock_tw (code varchar(32),name varchar(32),market varchar(32),_type varchar(32),_group varchar(32))')
	a = 0
	for code in twstock.codes.keys():
		codeinfo = twstock.codes[code]
		name = codeinfo.name
		market = codeinfo.market
		_type = codeinfo.type
		group = codeinfo.group
		if _type == '股票':
			print('insert into allstock_tw (code,name,market,_type,_group) values (%s,%s,%s,%s,%s)',(code,name,market,_type,group))
			cursor.execute('insert into allstock_tw (code,name,market,_type,_group) values (%s,%s,%s,%s,%s)',(code,name,market,_type,group))
			a += 1

	print('共獲取到%d支股票'%a)

	conn.commit()
	cursor.close()
	conn.close()

# run()