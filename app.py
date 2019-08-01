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

line_bot_api = LineBotApi('NVTR4vxLQ/zNiXQvTsgvW4gO7FbW6hIKrf7C/t7dKU1uAelrBfvxGzvskg9NHA9VT95usgs4IKt/j0i9qQQ82kjkymL4owhn1T0OMcEC1VRByaaf86UWChSW0NySEOnUqSOw9/1VRfuGsQSvurb8MQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('c9bbe032d7640d2adcbb5e27cb28b012')

app = Flask(__name__)

@app.route('/')
def index():
    
    return 'Hello World!'

@app.route('/<name>')
def hello(name):
    return 'Hello ' + name + '!'

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
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))



if __name__=="__main__":
    app.run()