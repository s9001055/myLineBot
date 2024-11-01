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

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)