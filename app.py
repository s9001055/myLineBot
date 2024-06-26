from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import csv
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])


def csv_to_custom_dict(file_path):
    data = {}
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:  # 確保行不為空
                data[row[0]] = row[1]
    return data



file_path = 'student.csv'  # 請替換成你的CSV文件路徑
data = csv_to_custom_dict(file_path)

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
    # 回傳家長名
    replyMsg = 'no people'
    replyId = event.reply_token
    if event.message.text in data:
        replyId = data[event.message.text]
        replyMsg = event.message.text + '家長，您的小孩已到校'
        message = TextSendMessage(text=replyMsg)
        line_bot_api.push_message(replyId, message)
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=replyMsg))
    
    

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)