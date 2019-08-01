import requests
import re
from bs4 import BeautifulSoup

res  = requests.get('http://www.taiwanlottery.com.tw/index_new.aspx')
soup = BeautifulSoup(res.text,'html.parser')
'''開獎日期 期數'''
date    = []#Announced date
periods = [] #Number of periods
for span in soup.select('span'):
	match = re.search(r'^<span class="font_black15">(.*?)\s(.*?)</span>',str(span))
	if match:
		date.append(match.group(1))
		periods.append(match.group(2))

'''special_ball 特別號'''
special_ball = []
for div in soup.select('div'):
	match = re.search(r'^<div class="ball_red">(.*?)<',str(div))
	if match:
		special_ball.append(match.group(1))
'''lemon_ball 今彩五三九 三九樂合彩'''
lemon_ball = []
for div in soup.select('div'):
	match = re.search(r'^<div class="ball_tx ball_lemon">(.*?)<',str(div))
	if match:
		lemon_ball.append(match.group(1))
def wei_li():
	wei_li__order  = []
	wei_li__sorted = []
	counter = 0
	for div in soup.select('div'):
		match = re.search(r'^<div class="ball_tx ball_green">(.*?)<',str(div))
		if match:
			counter += 1
			if counter <= 6:
				wei_li__order.append(match.group(1))
			elif 6 < counter <= 12:
				wei_li__sorted.append(match.group(1))
	strarr = []
	strarr.append("******************威力彩******************")
	strarr.append("******************38樂合彩****************")
	strarr.append(date[1])
	strarr.append(periods[1])
	# strarr.append('*******開獎順序*******',''.join(wei_li__order))
	strarr.append('*******大小排序*******')
	strarr.append(''.join(wei_li__sorted))
	strarr.append('*******第二區號*******')
	strarr.append(int(special_ball[1]))

	return '\n'.join(str(x) for x in strarr)

def big_lottery():
	big_lottery__order  = []
	big_lottery__sorted = []
	counter = 0
	for div in soup.select('div'):
		match = re.search(r'^<div class="ball_tx ball_yellow">(.*?)<',str(div))
		if match:
			counter += 1
			if 21 <= counter <= 26:
				big_lottery__order.append(match.group(1))
			elif 27 <= counter <= 32:
				big_lottery__sorted.append(match.group(1))
	strarr = []

	strarr.append("******************大樂透******************")
	strarr.append("******************49樂合彩****************")
	strarr.append(date[3])
	strarr.append(periods[3])
	# print('*******開獎順序*******',''.join(big_lottery__order))
	strarr.append('*******大小排序*******')
	strarr.append(''.join(big_lottery__sorted))
	strarr.append('*******特別號碼*******')
	strarr.append(int(special_ball[2]))
	# print("******************************************")
	return '\n'.join(str(x) for x in strarr)

def colorful_539():
	colorful_539__order  = lemon_ball[0:5]
	colorful_539__sorted = lemon_ball[5:10]
	strarr = []

	strarr.append("******************今彩539*****************")
	strarr.append("******************39樂合彩****************")
	strarr.append(date[6])
	strarr.append(periods[6])
	# strarr.append('*******開獎順序*******')
	# strarr.append(''.join(colorful_539__order))
	strarr.append('*******大小排序*******')
	strarr.append(''.join(colorful_539__sorted))
	# print("******************************************")
	return '\n'.join(str(x) for x in strarr)

# def happy_39():
# 	happy_39__order  = lemon_ball[10:15]
# 	happy_39__sorted = lemon_ball[15:20]
# 	counter = 0

# 	print("******************39樂合彩*****************")
# 	print(date[7],periods[7])
# 	print('*******開獎順序*******',''.join(happy_39__order))
# 	print('*******大小排序*******',''.join(happy_39__sorted))
# 	print("******************************************")
# print("******************************************")
# print(wei_li())
# big_lottery())
# colorful_539()