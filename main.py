from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent, JoinEvent
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


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info( ReplyMessageRequest( reply_token=event.reply_token, messages=[TextMessage(text=event.message.text)]))



# @handler.add(MemberJoinedEvent)
# def handle_member_joined(event):
#     joined_user_ids = [member.user_id for member in event.joined.members]
#     welcome_message = "Hello!!!"
#     welcome_message = f"""歡迎 {', '.join(joined_user_ids)} 加入群組，目前記事本有最新球敘相關訊息，可以先去看看喔，如果要報名的話，直接在底下喊+1，然後在@主揪喔，另外有一些小提醒也是要看一下喔，個人簡介也麻煩填一下，開心擊球，無壓力唷😁😁
# 啊如果有開團，可以@Astor，我會幫您丟到記事本唷😁😁"""

#     with ApiClient(configuration) as api_client:
#         line_bot_api = MessagingApi(api_client)
#         line_bot_api.reply_message_with_http_info(ReplyMessageRequest(
#             reply_token=event.reply_token,
#             messages=[TextMessage(text=welcome_message)]
#         ))

@handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    api_client = ApiClient(configuration)
    line_bot_api = MessagingApi(api_client)
    
    joined_user_ids = [member.user_id for member in event.joined.members]
    names = []
    
    for user_id in joined_user_ids:
        try:
            profile = line_bot_api.get_profile(user_id)
            names.append(profile.display_name)  # 使用顯示名稱
        except LineBotApiError as e:
            app.logger.error(f"Failed to get profile for user {user_id}: {e}")
            names.append("未知用戶")  # 無法獲得資料的預設處理
    welcome_message = "Hello!!!"
    welcome_message = f"""歡迎 {', '.join(joined_user_ids)} 加入群組，目前記事本有最新球敘相關訊息，可以先去看看喔，如果要報名的話，直接在底下喊+1，然後在@主揪喔，另外有一些小提醒也是要看一下喔，個人簡介也麻煩填一下，開心擊球，無壓力唷😁😁
# 啊如果有開團，可以@Astor，我會幫您丟到記事本唷😁😁"""

    line_bot_api.reply_message_with_http_info(ReplyMessageRequest(
        reply_token=event.reply_token,
        messages=[TextMessage(text=welcome_message)]
    ))



if __name__ == "__main__":
    app.run()
