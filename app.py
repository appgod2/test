import random
import lottery
import myStockt
import write_allstock_tw
import creat_everydatebase
import threading
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('FlmQQSiEiaKaqoW1Pp3RWKa7I4Qbd39tUDBpod9v6vl6y0VkDelvqRKUFSXeO+IhT95usgs4IKt/j0i9qQQ82kjkymL4owhn1T0OMcEC1VSkO8Iuk4b7ApxFRjPC/QHskjulWjPaNWwah8JMj4GGNAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('c9bbe032d7640d2adcbb5e27cb28b012')
myId=''
getId=False

@app.route('/')
def index():

    return 'Hello World!'

# @app.route('/<name>')
# def hello(name):
#     return 'Hello ' + name + '!'

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global myId
    global getId
    # if not getId:
    myId=event.source.user_id
    #    getId=True
    action = 0
    text = event.message.text
    if "1"==text:
        text = "我是彭千玉"
    elif "creat_everydatebase_Run"==text:
        action = 2
        y = 2018
        for m in range(1,12):
            t = threading.Thread(target = creat_everydatebase.everdate2, args = (y,m,line_bot_api,event))
            # 執行該執行緒
            t.start()
    elif "2"==text:
        text = "廖韋佑"
    elif "威力彩"==text:
        num = " ".join(str(x) for x in random.sample(range(1,38),6))
        num2 = " ".join(str(x) for x in random.sample(range(1,8),1))
        text = num + " 特別號:" + num2
    elif "威力彩開獎"==text:
        text = lottery.wei_li()
    elif "大樂透開獎"==text:
        text = lottery.big_lottery()
    elif "539開獎"==text:
        text = lottery.colorful_539()
    elif "選單"==text:
        action = 1
        text = {
                    "type": "template",
                    "altText": "在不支援顯示樣板的地方顯示的文字",
                    "template": {
                        "type": "buttons",
                        "text": "標題文字",
                        "actions": [
                        {
                            "type": "message",
                            "label": "第一個按鈕",
                            "text": "1"
                        },
                        {
                            "type": "message",
                            "label": "第二個按鈕",
                            "text": "2"
                        },
                        {
                            "type": "message",
                            "label": "第三個按鈕",
                            "text": "3"
                        },
                        {
                            "type": "message",
                            "label": "第四個按鈕",
                            "text": "4"
                        }
                        ]
                    }
                }
    else:
        return

    if action==0:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text))
    elif action==1:
        line_bot_api.push_message(
            myId,
            text)


@app.route('/sendmsg')
def push_message():
    line_bot_api.push_message(
        myId,
        TextSendMessage(text="我是機器人"))

@app.route('/write_allstock_tw')
def write_allstock_tw_Run():
    write_allstock_tw.run()

@app.route('/creat_everydatebase')
def creat_everydatebase_Run():
    # y = 2018
    for y in range(2000,2019):
        mm = 12
        if y == 2019:
            mm = 7
            
        for m in range(1,mm):
            t = threading.Thread(target = creat_everydatebase.everdate2, args = (y,m,'',''))
            # 執行該執行緒
            t.start()

@app.route('/stock')
def test():
    # import matplotlib
    # matplotlib.use('Agg')  # 不出現畫圖的框
    # import matplotlib.pyplot as plt
    # from io import BytesIO
    # import base64

    # plt.axis([0, 5, 0, 20])  # [xmin,xmax,ymin,ymax]對應軸的範圍
    # plt.title('My first plot')  # 圖名
    # plt.plot([1, 2, 3, 4], [1, 4, 9, 16], 'ro')  # 圖上的點,最後一個引數為顯示的模式
    # sio = BytesIO()
    # plt.savefig(sio, format='png')
    # data = base64.encodebytes(sio.getvalue()).decode()
    data = myStockt.test()
    print(data)
    html = '''
       <html>
           <body>
               <img src="data:image/png;base64,{}" />
           </body>
        <html>
    '''
    return html.format(data)

    # headers = {
    # 'Content-Type': 'image/png',
    # 'Content-Length': len(data)
    # }
    # return HTTPResponse(body=data, headers=headers,)


if __name__=="__main__":
    app.run()

