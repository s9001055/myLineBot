from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import requests
import urllib.request
import time
import json
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

@handler.add(MessageEvent, message=LocationMessage)
def handle_loction_message(event):
    taxi_latitude = "24.1436159114637277"
    taxi_longitude = "120.65892414129009"

    dest_latitude = str(event.message.latitude)
    dest_longitude = str(event.message.longitude)

    # replyMsg += "(" + latitude + ", " + longitude + ")"

    url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=" \
        + taxi_latitude + "," + taxi_longitude \
        + "&destinations=" \
        + dest_latitude + "," + dest_longitude \
        + "&key=" + str(os.environ['GOOGLE_API_KEY'])
    
    while True:
        res = requests.get(url)
        js = json.loads(res.text)

        if js["status"] != "OVER_QUERY_LIMIT":
            time.sleep(1)
            break

    travel_time = str(js["rows"][0]["elements"][0]["duration"]["text"])

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=travel_time))
    # # 註冊家長
    # if '註冊家長' in event.message.text:
    #     arr = event.message.text.split('\n')
    #     data[arr[1]] = event.source.user_id
    #     line_bot_api.reply_message(event.reply_token, TextSendMessage(text='註冊成功'))
    #     # 需要加入寫回CSV功能
    #     return
    
    # # 回傳家長 孩子到校訊息
    # # 需要加入是否由伺服器端傳送的 MSG，不然家長傳自己孩子的名字就會回傳 已到校 訊息給家長
    # replyMsg = 'no people'
    # replyId = event.reply_token
    # if event.message.text in data:
    #     replyId = data[event.message.text]
    #     replyMsg = event.message.text + '家長，您的小孩已到校'
    #     message = TextSendMessage(text=replyMsg)
    #     line_bot_api.push_message(replyId, message)
    # else:
    #     line_bot_api.reply_message(event.reply_token, TextSendMessage(text=replyMsg))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)