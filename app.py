from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['mI7LIdwXSSC5Dfnh7FthtPUfGJks/9G3oP3P3nbO4l6wAv26OyiNcUSZVnDJTLp3Yso5gu2VMd7N7lZgvmr0ORKa7wohkYYTsd65Z+dG6bPDBPBgBTG7Rl4CVIue/cP2k36wcGSckaAneTp/C8xAPQdB04t89/1O/w1cDnyilFU='])
handler = WebhookHandler(os.environ['babe45eac33b7846bfec02361ce7facd'])


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)