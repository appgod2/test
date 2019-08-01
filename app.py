import random
import lottery
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
    if not getId:
       myId=event.source.user_id
       getId=True
    
    text = event.message.text
    if "1"==text:
        text = "我是彭千玉"
    elif "2"==text:
        text = "廖韋佑"
    elif "威力彩"==text:
        num = " ".join(str(x) for x in random.sample(range(1,38),6))
        num2 = " ".join(str(x) for x in random.sample(range(1,8),1))
        text = num + " 特別號:" + num2
    elif "開獎號碼"==text:
        text = lottery.wei_li()
    else:
        return

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=text))


@app.route('/sendmsg')
def push_message():
    line_bot_api.push_message(
        myId,
        TextSendMessage(text="我是機器人"))


if __name__=="__main__":
    app.run()

