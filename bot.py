from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, MemberJoinedEvent

app = Flask(__name__)

# 設置你的Channel Access Token和Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = 'YJDVGFZYnOTlub34o5TU+3cAuKEL6abW2gDPNYZGfYRuQSZAwuVGXWQLDw6kTMJCtRgLWuzPYRKRVewsJWnZKTpMQ/uboboyQt7MEOMX3Dy8shcMLOHlLSh9rTn+zfn/hGrus6UzNMMEQDnVFLvcvAdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = 'a9fd611e22ddc6b40418b2aec4c8bc8a'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
# 存儲所有球局的列表
games = []

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
    text = event.message.text.strip().lower()
    
    if text.startswith("生成"):
        parts = text.split()
        if len(parts) == 6:
            try:
                date = datetime.datetime.strptime(parts[2], "%Y-%m-%d")
                participants = int(parts[5])
                game = {
                    'location': parts[1],
                    'date': date,
                    'time': parts[3],
                    'fee': parts[4],
                    'participants': participants,
                    'max_participants': 4,
                    'users': []  # 用於存儲加入的用戶
                }
                games.append(game)
                response = "新的球局已生成！\n地點: {}\n日期: {}\n時間: {}\n球資: {}\n目前人數: {}/{}".format(
                    game['location'], game['date'].strftime("%Y-%m-%d"), game['time'],
                    game['fee'], game['participants'], game['max_participants']
                )
            except ValueError:
                response = "日期格式錯誤！請使用 YYYY-MM-DD 格式。\n或者參與人數必須是整數。"
        else:
            response = "格式錯誤！請輸入：生成 球局地點 日期 開球時間 球資 目前人數"
    
    elif text == "查看":
        if not games:
            response = "目前沒有球局。"
        else:
            sorted_games = sorted(games, key=lambda x: x['date'])
            response = "目前球局信息："
            for game in sorted_games:
                response += "\n地點: {}\n日期: {}\n時間: {}\n球資: {}\n目前人數: {}/{}\n".format(
                    game['location'], game['date'].strftime("%Y-%m-%d"), game['time'],
                    game['fee'], game['participants'], game['max_participants']
                )

    elif text.startswith("加入"):
        parts = text.split()
        if len(parts) == 2:
            location = parts[1]
            matching_games = [game for game in games if game['location'] == location]
            if not matching_games:
                response = f"沒有找到地點為 {location} 的球局。"
            else:
                game = matching_games[0]
                game['participants'] += 1
                if game['participants'] > game['max_participants']:
                    game['max_participants'] += 4
                game['users'].append(event.source.user_id)  # 記錄用戶ID
                response = "你已加入球局！\n地點: {}\n日期: {}\n時間: {}\n球資: {}\n目前人數: {}/{}".format(
                    game['location'], game['date'].strftime("%Y-%m-%d"), game['time'],
                    game['fee'], game['participants'], game['max_participants']
                )
        else:
            response = "格式錯誤！請輸入：加入 球局地點"
    
    elif text.startswith("查詢"):
        parts = text.split()
        if len(parts) == 2:
            location = parts[1]
            matching_games = [game for game in games if game['location'] == location]
            if not matching_games:
                response = f"沒有找到地點為 {location} 的球局。"
            else:
                response = f"{location} 的球局信息："
                for game in matching_games:
                    users = "\n".join(game['users']) if game['users'] else "無加入的用戶"
                    response += "\n地點: {}\n日期: {}\n時間: {}\n球資: {}\n目前人數: {}/{}\n加入的用戶:\n{}".format(
                        game['location'], game['date'].strftime("%Y-%m-%d"), game['time'],
                        game['fee'], game['participants'], game['max_participants'], users
                    )
        else:
            response = "格式錯誤！請輸入：查詢 球局地點"
    
    else:
        response = "不支援的指令。請使用：生成、查看、加入 或 查詢。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response)
    )

@handler.add(MemberJoinedEvent)
def handle_member_join(event):
    new_members = [member.user_id for member in event.joined.members]
    for user_id in new_members:
        user_profile = line_bot_api.get_profile(user_id)
        user_name = user_profile.display_name
        welcome_message = f"{user_name}您好，歡迎加入！有開團球敘都會丟到記事本，歡迎喊加一，並@開團的人讓他知到一下，謝謝你，記事本也有些小提醒要記得看喔，靠大家一起維持了😁"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=welcome_message))


if __name__ == "__main__":
    app.run()