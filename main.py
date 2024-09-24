import os

from flask import Flask, request, abort
from linebot import WebhookHandler, LineBotApi
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextMessage, MessageEvent, MemberJoinedEvent, TextSendMessage, ImageCarouselTemplate, TemplateSendMessage, ImageCarouselColumn, URIAction, MessageAction

app = Flask(__name__)

# access env params
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# PARAMS
WELCOME_MESSAGE = """歡迎加入群組！群組無任何版主，由熱心的球友們共同維護，要拉人請隨意，無需告知。\n\n請遵守板規如下⬇️\n\n1. 不做任何營銷及商業行為，若需生意交流，請私下與球友討論，不要構成其他人壓力。\n\n2. 不傳遞賣場連結或其他群組連結（預防球友遭受詐騙或其他不預期事件）\n\n3. 球隊要拉人也請在球敘後與球友討論，切勿在版內公開拉人，不造成其他人壓力。\n\n❤️目前記事本有最新球敘相關訊息，可以先去看看喔！如果要報名的話，直接在底下喊+1，然後再@主揪喔。\n\n另外有一些小提醒也是要看一下喔，個人簡介也麻煩填一下，開心擊球，無壓力唷😁😁\n\n如果要開團，可以放到記事本讓大家加入唷😁😁 \n\n球場價格: https://sites.google.com/view/tw-golf-price"""
FIG_GOLF_COURSE = 'https://img.freepik.com/premium-photo/view-green-golf-course-with-beautiful-sunset-generative-ai_902639-51545.jpg'
FIG_GOLF_ICON = 'https://raw.githubusercontent.com/ivantaiwan/LINEBOT/refs/heads/main/image/golf_icon.png'
FIG_KARINA = 'https://upload.wikimedia.org/wikipedia/commons/1/12/230601_Karina_%28aespa%29.jpg'
FIG_WINTER = 'https://raw.githubusercontent.com/ivantaiwan/LINEBOT/refs/heads/main/image/winter.jpeg'

TABLE_TAIPEI = 'https://docs.google.com/spreadsheets/d/1G42feYlB0fs0Z5oEJO_ADgjjRY_NkkWF9vq3NcTCVj0/edit?gid=1565443371#gid=1565443371'
TABLE_TAOYUAN = 'https://docs.google.com/spreadsheets/d/1G42feYlB0fs0Z5oEJO_ADgjjRY_NkkWF9vq3NcTCVj0/edit?gid=577875396#gid=577875396'
TABLE_HSINCHU = 'https://docs.google.com/spreadsheets/d/1G42feYlB0fs0Z5oEJO_ADgjjRY_NkkWF9vq3NcTCVj0/edit?gid=1001817199#gid=1001817199'
TABLE_CENTRAL = 'https://docs.google.com/spreadsheets/d/1G42feYlB0fs0Z5oEJO_ADgjjRY_NkkWF9vq3NcTCVj0/edit?gid=979283829#gid=979283829'
TABLE_SOUTH = 'https://docs.google.com/spreadsheets/d/1G42feYlB0fs0Z5oEJO_ADgjjRY_NkkWF9vq3NcTCVj0/edit?gid=1309915830#gid=1309915830'
TABLE_EAST = 'https://docs.google.com/spreadsheets/d/1G42feYlB0fs0Z5oEJO_ADgjjRY_NkkWF9vq3NcTCVj0/edit?gid=1769279530#gid=1769279530'

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
        welcome_message = WELCOME_MESSAGE
        line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text=welcome_message)
        )

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    if msg == '!text':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))
    
    elif msg == '!Karina':
        image_carousel_template = ImageCarouselTemplate(columns=[
            ImageCarouselColumn(image_url=FIG_KARINA, action=MessageAction(label='KARINA!', text='KARINA!'))
        ])
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(alt_text='KARINA', template=image_carousel_template))
    
    elif msg == '!Winter':
        image_carousel_template = ImageCarouselTemplate(columns=[
            ImageCarouselColumn(image_url=FIG_WINTER, action=MessageAction(label='Winter!', text='Winter!'))
        ])
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(alt_text='Winter', template=image_carousel_template))

    elif msg == '!球場價格':
        # image_carousel_template = ImageCarouselTemplate(columns=[
        #     ImageCarouselColumn(image_url=FIG_GOLF_COURSE, action=URIAction(label='雙北地區', uri=TABLE_TAIPEI)),
        #     ImageCarouselColumn(image_url=FIG_GOLF_COURSE, action=URIAction(label='桃園地區', uri=TABLE_TAOYUAN)),
        #     ImageCarouselColumn(image_url=FIG_GOLF_COURSE, action=URIAction(label='竹苗地區', uri=TABLE_HSINCHU)),
        #     ImageCarouselColumn(image_url=FIG_GOLF_COURSE, action=URIAction(label='中部地區', uri=TABLE_CENTRAL)),
        #     ImageCarouselColumn(image_url=FIG_GOLF_COURSE, action=URIAction(label='南部地區', uri=TABLE_SOUTH)),
        #     ImageCarouselColumn(image_url=FIG_GOLF_COURSE, action=URIAction(label='東部地區', uri=TABLE_EAST))
        # ])
        # line_bot_api.reply_message(
        #     event.reply_token,
        #     TemplateSendMessage(alt_text='球場價格', template=image_carousel_template))
        GolfCoursePrice = TextSendMessage(
            text='球場價格',
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(
                        action=MessageAction(label='雙北', text='TABLE_TAIPEI'),
                        image_url=FIG_GOLF_ICON
                    ),
                    QuickReplyButton(
                        action=MessageAction(label='桃園', text='TABLE_TAOYUAN'),
                        image_url=FIG_GOLF_ICON
                    ),
                    # QuickReplyButton(
                    #     action=URIAction(label='竹苗', uri=TABLE_HSINCHU),
                    #     image_url=FIG_GOLF_ICON
                    # ),
                    # QuickReplyButton(
                    #     action=URIAction(label='中部', uri=TABLE_CENTRAL),
                    #     image_url=FIG_GOLF_ICON
                    # ),
                    # QuickReplyButton(
                    #     action=URIAction(label='南部', uri=TABLE_SOUTH),
                    #     image_url=FIG_GOLF_ICON
                    # ),
                    # QuickReplyButton(
                    #     action=URIAction(label='東部', uri=TABLE_EAST),
                    #     image_url=FIG_GOLF_ICON
                    # )
                ]
            )
        )
        line_bot_api.reply_message(
            event.reply_token,
            GolfCoursePrice)


if __name__ == "__main__":
    app.run()
