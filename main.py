import os

from flask import Flask, request, abort
from linebot import WebhookHandler, LineBotApi
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    TextMessage, MessageEvent, MemberJoinedEvent, TextSendMessage, ImageCarouselTemplate, TemplateSendMessage, ImageCarouselColumn,
    URIAction, MessageAction, QuickReply, QuickReplyButton)
from linebot.models.template import ButtonsTemplate

app = Flask(__name__)

# access env params
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# PARAMS
WELCOME_MESSAGE = """歡迎加入群組！群組無任何版主，由熱心的球友們共同維護，要拉人請隨意，無需告知。\n\n請遵守板規如下⬇️\n\n1. 不做任何營銷及商業行為，若需生意交流，請私下與球友討論，不要構成其他人壓力。\n\n2. 不傳遞賣場連結或其他群組連結（預防球友遭受詐騙或其他不預期事件）\n\n3. 球隊要拉人也請在球敘後與球友討論，切勿在版內公開拉人，不造成其他人壓力。\n\n❤️目前記事本有最新球敘相關訊息，可以先去看看喔！如果要報名的話，直接在底下喊+1，然後再@主揪喔。\n\n另外有一些小提醒也是要看一下喔，個人簡介也麻煩填一下，開心擊球，無壓力唷😁😁\n\n如果要開團，可以放到記事本讓大家加入唷😁😁 \n\n球場價格: https://sites.google.com/view/tw-golf-price"""
FIG_GOLF_COURSE = 'https://raw.githubusercontent.com/ivantaiwan/LINEBOT/refs/heads/main/image/golf_course.jpg'
FIG_GOLF_GAME = 'https://raw.githubusercontent.com/ivantaiwan/LINEBOT/refs/heads/main/image/golf_game.jpg'
FIG_GOLF_ICON = 'https://raw.githubusercontent.com/ivantaiwan/LINEBOT/refs/heads/main/image/golf_icon.png'
FIG_KARINA = 'https://raw.githubusercontent.com/ivantaiwan/LINEBOT/refs/heads/main/image/karina.jpg'
FIG_WINTER = 'https://raw.githubusercontent.com/ivantaiwan/LINEBOT/refs/heads/main/image/winter.jpeg'

TABLE_TAIPEI = 'https://docs.google.com/spreadsheets/d/1urXlSqNkxKm67KwnN85HWFcxO93MX90M1WZ58Pnzqc8/edit?gid=0#gid=0'
TABLE_TAOYUAN_HSINCHU = 'https://docs.google.com/spreadsheets/d/1fEX6-BmrxsBqfrpYx58QT01eEG6k1TJgKWLEFxwJ4z4/edit?gid=0#gid=0'
TABLE_OTHER = 'https://docs.google.com/spreadsheets/d/1HEGYhE0PfVOwFqn5Avp01KSkP0UUXEUURx0MheIgJz0/edit?gid=0#gid=0'


@app.route('/')
def hello_world():
    return "Welcome to the service!"


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
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MemberJoinedEvent)
def handle_member_joined(event):
        line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text=WELCOME_MESSAGE)
        )

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # check user's message
    msg = event.message.text

    if msg == '!text':  # reply same message
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))
    
    elif msg == '!Karina':  # Display Karina
        image_carousel_template = ImageCarouselTemplate(columns=[
            ImageCarouselColumn(image_url=FIG_KARINA, action=MessageAction(label='KARINA!', text='KARINA!'))
        ])
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(alt_text='KARINA', template=image_carousel_template))
    
    elif msg == '!Winter':  # Display Winter
        image_carousel_template = ImageCarouselTemplate(columns=[
            ImageCarouselColumn(image_url=FIG_WINTER, action=MessageAction(label='Winter!', text='Winter!'))
        ])
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(alt_text='Winter', template=image_carousel_template))

    elif msg == '!球場價格':  # Display All Golf Course Pricing Information for Taiwan
        buttons_template = ButtonsTemplate(
            title='全台球場價格',
            thumbnail_image_url=FIG_GOLF_COURSE,
            text='請選擇想查詢的地區！',
            actions=[
                URIAction(label='雙北', uri=TABLE_TAIPEI),
                URIAction(label='桃竹苗', uri=TABLE_TAOYUAN_HSINCHU),
                URIAction(label='中部南部東部', uri=TABLE_OTHER)
            ]
        )

        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(alt_text='球場價格', template=buttons_template))

    elif msg == '!約下場':  # Display Dashboard for Create/Join Golf Game
        buttons_template = ButtonsTemplate(
            title='高爾夫約下場',
            thumbnail_image_url=FIG_GOLF_GAME,
            text='請選擇！',
            actions=[
                MessageAction(label='創建與編輯球局', text='Coming Soon!'),
                MessageAction(label='加入現有球局', text='Coming Soon!')
            ]
        )

        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(alt_text='高爾夫約下場', template=buttons_template))


if __name__ == "__main__":
    app.run()
