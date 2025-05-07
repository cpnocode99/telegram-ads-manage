import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
import requests

# 🔐 Biến môi trường
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

# 🚀 Khởi tạo Flask app và Telegram bot
app = Flask(__name__)
bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

# 🔧 Gọi Facebook API để bật/tắt
def change_status(obj_id, status):
    url = f"https://graph.facebook.com/v21.0/{obj_id}"
    headers = {"Authorization": f"Bearer {FB_ACCESS_TOKEN}"}
    data = {"status": status}
    return requests.post(url, headers=headers, data=data)

# 📍 /off ad/campaign/adset ID
def off(update, context):
    if len(context.args) != 2:
        return
    _, obj_id = context.args
    res = change_status(obj_id, "PAUSED")
    if res.status_code == 200:
        update.message.reply_text("✅ Đã tắt thành công.")
    else:
        update.message.reply_text(f"❌ Lỗi: {res.text}")

# 📍 /on ad/campaign/adset ID
def on(update, context):
    if len(context.args) != 2:
        return
    _, obj_id = context.args
    res = change_status(obj_id, "ACTIVE")
    if res.status_code == 200:
        update.message.reply_text("✅ Đã bật thành công.")
    else:
        update.message.reply_text(f"❌ Lỗi: {res.text}")

# 🔌 Gắn handler
dispatcher.add_handler(CommandHandler("off", off))
dispatcher.add_handler(CommandHandler("on", on))

# 📡 Webhook nhận từ Telegram
@app.route(f"/webhook/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

# 🔍 Kiểm tra bot
@app.route("/")
def home():
    return "✅ Facebook Ads Bot is running", 200

# 🚀 Chạy app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
