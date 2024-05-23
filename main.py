from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent, JoinEvent, UserSource, Mention, Mentionee
from linebot.v3.webhooks import MemberJoinedEvent

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = 'YJDVGFZYnOTlub34o5TU+3cAuKEL6abW2gDPNYZGfYRuQSZAwuVGXWQLDw6kTMJCtRgLWuzPYRKRVewsJWnZKTpMQ/uboboyQt7MEOMX3Dy8shcMLOHlLSh9rTn+zfn/hGrus6UzNMMEQDnVFLvcvAdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = 'a9fd611e22ddc6b40418b2aec4c8bc8a'

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
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


# @handler.add(MessageEvent, message=TextMessageContent)
# def handle_message(event):
#     with ApiClient(configuration) as api_client:
#         line_bot_api = MessagingApi(api_client)
#         line_bot_api.reply_message_with_http_info(ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=event.message.text)]))


@handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        user_id = event.joined.members[0].user_id  # Assuming one user joined
        try:
            profile = line_bot_api.get_profile(user_id)
            display_name = profile.display_name
        except LineBotApiError:
            display_name = "未知用戶"
            app.logger.error(f"Failed to get profile for user {user_id}")

        # welcome_message = f"""歡迎 {display_name} 加入群組！目前記事本有最新球敘相關訊息，可以先去看看喔，如果要報名的話，直接在底下喊+1，然後再@主揪喔。\n另外有一些小提醒也是要看一下喔，個人簡介也麻煩填一下，開心擊球，無壓力唷😁😁\n如果要開團，可以放到記事本讓大家加入唷😁😁"""
        welcome_message = f"""歡迎 {display_name} 加入群組！群組無任何版主，由熱心的球友們共同維護，要拉人請隨意，無需告知。\n\n請遵守板規如下⬇️\n\n1. 不做任何營銷及商業行為，若需生意交流，請私下與球友討論，不要構成其他人壓力。\n\n2. 不傳遞賣場連結或其他群組連結（預防球友遭受詐騙或其他不預期事件）\n\n3. 球隊要拉人也請在球敘後與球友討論，切勿在版內公開拉人，不造成其他人壓力。\n\n❤️目前記事本有最新球敘相關訊息，可以先去看看喔！如果要報名的話，直接在底下喊+1，然後再@主揪喔。\n\n另外有一些小提醒也是要看一下喔，個人簡介也麻煩填一下，開心擊球，無壓力唷😁😁\n\n如果要開團，可以放到記事本讓大家加入唷😁😁"""
        line_bot_api.reply_message_with_http_info(ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=welcome_message)]
        ))


if __name__ == "__main__":
    app.run()
