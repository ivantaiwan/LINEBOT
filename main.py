import os

import openai
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
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# get Bot User ID
bot_info = line_bot_api.get_bot_info()
BOT_USER_ID = bot_info.user_id
BOT_DISPLAY_NAME = "群組專用 AI"

# set OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)


def ask_chatgpt(prompt: str) -> str:
    """call OpenAI ChatGPT with system prompt"""
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": "你是一位熱情但謹慎的高爾夫教練機器人，活躍於一個用來揪團打高爾夫的群組中。請全程使用繁體中文回答，必要時可搭配英文術語做簡要補充。你應保持禮貌、語氣親切但不隨便，回答要簡潔、明確，不知道的問題請直接說不知道，絕對不要胡亂猜測或瞎掰。你應避免回應任何帶有惡意、挑釁、危險、或可能對他人造成傷害的問題與請求。你特別擅長解答高爾夫相關的問題，例如：打球技巧、球具介紹、場地規則、服裝禮儀等。"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=512,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

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
    mention = None
    replied = False

    # Check if the bot was mentioned (with @) in the group
    if event.source.type in ['group', 'room']:
        mention = event.message.mention
    else:
        mention = None

    if msg == '!text':  # reply same message
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))
        replied = True
    
    elif msg == '!Karina':  # Display Karina
        image_carousel_template = ImageCarouselTemplate(columns=[
            ImageCarouselColumn(image_url=config.FIGURE['karina'], action=MessageAction(label='KARINA!', text='KARINA!'))
        ])
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(alt_text='KARINA', template=image_carousel_template))
        replied = True
    
    elif msg == '!Winter':  # Display Winter
        image_carousel_template = ImageCarouselTemplate(columns=[
            ImageCarouselColumn(image_url=config.FIGURE['winter'], action=MessageAction(label='Winter!', text='Winter!'))
        ])
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(alt_text='Winter', template=image_carousel_template))
        replied = True

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
        
        replied = True

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
        
        replied = True
    
    # ChatGPT
    # only if no explicit command was matched
    # This block will now only execute if the message didn't trigger any of the above commands.
    if event.source.type in ['group', 'room']:
        if mention or not any(m.user_id == BOT_USER_ID for m in mention.mentionees):
            cleaned_msg = msg.replace(BOT_DISPLAY_NAME, "").strip()

            try:
                answer = ask_chatgpt(cleaned_msg)
            except Exception as e:
                answer = "抱歉，AI無法回答你的問題。\nError:" + str(e)

            if not replied:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=answer))
                replied = True
            else:
                line_bot_api.push_message(event.source.user_id, TextSendMessage(text=answer))

            return # IMPORTANT: Stop processing after replying for ChatGPT


if __name__ == "__main__":
    app.run()
