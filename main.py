from flask import Flask, request
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.ext import AIORateLimiter, Dispatcher

BOT_TOKEN = 'TELEGRAM_BOT_TOKEN'
FB_ACCESS_TOKEN = 'FACEBOOK_ACCESS_TOKEN'

app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).rate_limiter(AIORateLimiter()).build()

# Hàm gọi Facebook API
def change_status(obj_id, status):
    url = f"https://graph.facebook.com/v19.0/{obj_id}"
    headers = {
        "Authorization": f"Bearer {FB_ACCESS_TOKEN}"
    }
    data = { "status": status }
    return requests.post(url, headers=headers, data=data)

# Handler /off
async def off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text('Cú pháp: /off {campaign|adset|ad} {id}')
        return
    obj_type, obj_id = context.args
    res = change_status(obj_id, "PAUSED")
    await update.message.reply_text("✅ Tắt thành công." if res.status_code == 200 else f"❌ Lỗi: {res.text}")

# Handler /on
async def on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text('Cú pháp: /on {campaign|adset|ad} {id}')
        return
    obj_type, obj_id = context.args
    res = change_status(obj_id, "ACTIVE")
    await update.message.reply_text("✅ Bật thành công." if res.status_code == 200 else f"❌ Lỗi: {res.text}")

application.add_handler(CommandHandler("off", off))
application.add_handler(CommandHandler("on", on))

@app.post(f"/webhook")
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.update_queue.put(update)
    return "ok"
