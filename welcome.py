from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, JoinEvent, MemberJoinedEvent

import os
import sqlite3

app = FastAPI()

# LINE channel access token and secret
LINE_CHANNEL_ACCESS_TOKEN = 'YJDVGFZYnOTlub34o5TU+3cAuKEL6abW2gDPNYZGfYRuQSZAwuVGXWQLDw6kTMJCtRgLWuzPYRKRVewsJWnZKTpMQ/uboboyQt7MEOMX3Dy8shcMLOHlLSh9rTn+zfn/hGrus6UzNMMEQDnVFLvcvAdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = 'a9fd611e22ddc6b40418b2aec4c8bc8a'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Connect to SQLite database
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (id INTEGER PRIMARY KEY, user_id TEXT, display_name TEXT)''')
conn.commit()

@app.post("/callback")
async def callback(request: Request):
    signature = request.headers['x-line-signature']
    body = await request.body()
    
    try:
        handler.handle(body.decode('utf-8'), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    return JSONResponse(content={"message": "OK"})

@handler.add(MemberJoinedEvent)
def handle_member_join(event):
    new_members = event.joined.members
    for member in new_members:
        user_id = member.user_id
        profile = line_bot_api.get_profile(user_id)
        user_name = profile.display_name
        
        # Save new user to database
        cursor.execute('INSERT INTO users (user_id, display_name) VALUES (?, ?)', (user_id, user_name))
        conn.commit()
        
        welcome_message = f"歡迎{user_name}加入 記事本有多場球敘 歡迎+1 一同擊球。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=welcome_message))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 8000)))
