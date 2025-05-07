from flask import Flask, request
import os, requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.ext import AIORateLimiter

BOT_TOKEN = os.environ["BOT_TOKEN"]
FB_ACCESS_TOKEN = os.environ["FB_ACCESS_TOKEN"]

app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).rate_limiter(AIORateLimiter()).build()

# Gọi API Facebook
def change_status(obj_id, status):
    url = f"https://graph.facebook.com/v21.0/{obj_id}"
    headers = {"Authorization": f"Bearer {FB_ACCESS_TOKEN}"}
    data = {"status": status}
    return requests.post(url, headers=headers, data=data)

# /off command
async def off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        return  # Không phản hồi gì cả nếu sai cú pháp
    _, obj_id = context.args
    res = change_status(obj_id, "PAUSED")
    if res.status_code == 200:
        await update.message.reply_text("✅ Đã tắt thành công.")
    else:
        await update.message.reply_text(f"❌ Lỗi: {res.text}")

# /on command
async def on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        return
    _, obj_id = context.args
    res = change_status(obj_id, "ACTIVE")
    if res.status_code == 200:
        await update.message.reply_text("✅ Đã bật thành công.")
    else:
        await update.message.reply_text(f"❌ Lỗi: {res.text}")

# Đăng ký command
application.add_handler(CommandHandler("off", off))
application.add_handler(CommandHandler("on", on))

# Webhook entrypoint
@app.post("/webhook")
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.update_queue.put(update)
    return "ok"
