from fastapi import FastAPI, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, JoinEvent, MemberJoinedEvent
from database import SessionLocal, Game
import json

app = FastAPI()

# 設置你的Channel Access Token和Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = 'YJDVGFZYnOTlub34o5TU+3cAuKEL6abW2gDPNYZGfYRuQSZAwuVGXWQLDw6kTMJCtRgLWuzPYRKRVewsJWnZKTpMQ/uboboyQt7MEOMX3Dy8shcMLOHlLSh9rTn+zfn/hGrus6UzNMMEQDnVFLvcvAdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = 'a9fd611e22ddc6b40418b2aec4c8bc8a'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/callback")
async def callback(request: Request, db: Session = Depends(get_db)):
    signature = request.headers['X-Line-Signature']
    body = await request.body()
    app.logger.info("Request body: " + body.decode("utf-8"))

    try:
        handler.handle(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event: MessageEvent, db: Session = Depends(get_db)):
    user_message = event.message.text
    user_id = event.source.user_id

    if user_message.startswith("生成"):
        parts = user_message.split()
        if len(parts) == 6:
            game = Game(
                location=parts[1],
                date=parts[2],
                time=parts[3],
                fee=int(parts[4]),
                participants=int(parts[5]),
                users=""
            )
            db.add(game)
            db.commit()
            reply = f"新球局已生成: 地點:{game.location} 日期:{game.date} 開球時間:{game.time} 球資:{game.fee} 目前人數:{game.participants}/4"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="指令格式錯誤，請使用格式：生成 地點 日期 時間 球資 目前人數"))
    
    elif user_message == "查看目前球局":
        games = db.query(Game).all()
        if not games:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="目前沒有任何球局"))
        else:
            sorted_games = sorted(games, key=lambda k: k.date)
            reply = "目前球局如下：\n"
            for game in sorted_games:
                reply += f"地點:{game.location} 日期:{game.date} 開球時間:{game.time} 球資:{game.fee} 目前人數:{game.participants}/{(game.participants // 4 + 1) * 4}\n"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

    elif user_message.startswith("加入"):
        parts = user_message.split()
        if len(parts) == 2:
            game_location = parts[1]
            user_profile = line_bot_api.get_profile(user_id)
            user_name = user_profile.display_name
            game = db.query(Game).filter(Game.location == game_location).first()
            if game:
                game.participants += 1
                users = game.users.split(',') if game.users else []
                users.append(user_name)
                game.users = ','.join(users)
                if game.participants % 4 == 0:
                    game.participants += 4
                db.commit()
                reply = f"{user_name} 已加入 {game_location} 的球局！目前人數:{game.participants}/{(game.participants // 4 + 1) * 4}"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="找不到指定地點的球局"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="指令格式錯誤，請使用格式：加入 地點"))
    
    elif user_message.startswith("某某球局"):
        parts = user_message.split()
        if len(parts) == 2:
            game_location = parts[1]
            game = db.query(Game).filter(Game.location == game_location).first()
            if game:
                reply = f"{game_location} 的球局:\n日期: {game.date}\n開球時間: {game.time}\n加入人員: {game.users}"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="找不到指定地點的球局"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="指令格式錯誤，請使用格式：某某球局 地點"))

@handler.add(MemberJoinedEvent)
def handle_member_join(event: MemberJoinedEvent):
    new_members = [member.user_id for member in event.joined.members]
    for user_id in new_members:
        user_profile = line_bot_api.get_profile(user_id)
        user_name = user_profile.display_name
        welcome_message = f"{user_name}您好，歡迎加入！有開團球敘都會丟到記事本，歡迎喊加一，並@開團的人讓他知到一下，謝謝你，記事本也有些小提醒要記得看喔，靠大家一起維持了😁"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=welcome_message))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
