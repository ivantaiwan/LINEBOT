import os

from flask import Flask, request, abort
from linebot import WebhookHandler, LineBotApi
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    TextMessage, MessageEvent, MemberJoinedEvent, TextSendMessage, ImageCarouselTemplate, TemplateSendMessage, ImageCarouselColumn,
    URIAction, MessageAction, QuickReply, QuickReplyButton)
from linebot.models.template import ButtonsTemplate

import config  # config file for all project


app = Flask(__name__)

# access env params
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


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
            TextMessage(text=config.MESSAGE['welcome'])
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
            ImageCarouselColumn(image_url=config.FIGURE['karina'], action=MessageAction(label='KARINA!', text='KARINA!'))
        ])
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(alt_text='KARINA', template=image_carousel_template))
    
    elif msg == '!Winter':  # Display Winter
        image_carousel_template = ImageCarouselTemplate(columns=[
            ImageCarouselColumn(image_url=config.FIGURE['winter'], action=MessageAction(label='Winter!', text='Winter!'))
        ])
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(alt_text='Winter', template=image_carousel_template))

    elif msg in ['!球場價格', '球場價格!', '！球場價格', '球場價格！']:  # Display All Golf Course Pricing Information for Taiwan
        buttons_template = ButtonsTemplate(
            title='全台球場價格',
            thumbnail_image_url=config.FIGURE['golf_course'],
            text='請選擇想查詢的地區！',
            actions=[
                URIAction(label='雙北', uri=config.TABLE['taipei']),
                URIAction(label='桃竹苗', uri=config.TABLE['taoyuan_hsinchu']),
                URIAction(label='中部南部東部', uri=config.TABLE['other'])
            ]
        )

        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(alt_text='球場價格', template=buttons_template))

    elif msg in ['!約下場', '約下場!', '！約下場', '約下場！']:  # Display Dashboard for Create/Join Golf Game
        buttons_template = ButtonsTemplate(
            title='高爾夫約下場',
            thumbnail_image_url=config.FIGURE['golf_game'],
            text='請點選以下網址，可以新增或加入現有球局～',
            actions=[
                URIAction(label='揪打球！', uri=config.LINK['home'])
            ]
        )

        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(alt_text='高爾夫約下場', template=buttons_template))


if __name__ == "__main__":
    app.run()
