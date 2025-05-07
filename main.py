import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
import requests

# 🔐 Lấy biến môi trường
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

# 🚨 Kiểm tra token có tồn tại không
if TELEGRAM_TOKEN is None:
    raise ValueError("❌ TELEGRAM_TOKEN chưa được thiết lập.")
if FB_ACCESS_TOKEN is None:
    raise ValueError("❌ FB_ACCESS_TOKEN chưa được thiết lập.")

# 🚀 Tạo Flask app & Telegram bot
app = Flask(__name__)
bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

# 📡 Gọi Facebook API để thay đổi trạng thái quảng cáo
def change_status(obj_id, status):
    url = f"https://graph.facebook.com/v21.0/{obj_id}"
    headers = {"Authorization": f"Bearer {FB_ACCESS_TOKEN}"}
    data = {"status": status}
    return requests.post(url, headers=headers, data=data)

# 📍 Lệnh /off
def off(update, context):
    if len(context.args) != 2:
        update.message.reply_text("❌ Cú pháp đúng: /off {loại} {id}")
        return
    _, obj_id = context.args
    res = change_status(obj_id, "PAUSED")
    if res.status_code == 200:
        update.message.reply_text("✅ Đã tắt thành công.")
    else:
        update.message.reply_text(f"❌ Lỗi: {res.text}")

# 📍 Lệnh /on
def on(update, context):
    if len(context.args) != 2:
        update.message.reply_text("❌ Cú pháp đúng: /on {loại} {id}")
        return
    _, obj_id = context.args
    res = change_status(obj_id, "ACTIVE")
    if res.status_code == 200:
        update.message.reply_text("✅ Đã bật thành công.")
    else:
        update.message.reply_text(f"❌ Lỗi: {res.text}")

# 🧩 Gắn handler
dispatcher.add_handler(CommandHandler("off", off))
dispatcher.add_handler(CommandHandler("on", on))

# ✅ Route nhận Webhook Telegram
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

# 📄 Trang kiểm tra bot hoạt động
@app.route("/")
def home():
    return "✅ Facebook Ads Bot đang chạy!", 200

# 🚀 Chạy Flask app (chỉ dùng khi local test)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
