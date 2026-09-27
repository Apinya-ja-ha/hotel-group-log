import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage
from hotel_log_service import HotelLogService
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

app = Flask(__name__)

LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET", "")
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")
ADMIN_USER_IDS = set(filter(None, os.environ.get("ADMIN_USER_IDS", "").split(",")))
BOT_USER_ID = os.environ.get("BOT_USER_ID", "")
TZ = pytz.timezone("Asia/Bangkok")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
hotel_service = HotelLogService()

IMPORTANT_KEYWORDS = ["แอดมิน", "admin", "@admin", "ด่วน", "urgent", "สำคัญ"]


def _is_important(text: str, bot_mentioned: bool) -> bool:
    if bot_mentioned:
        return True
    lower = text.lower()
    return any(kw.lower() in lower for kw in IMPORTANT_KEYWORDS)


def _get_display_name(event, user_id: str) -> str:
    try:
        if hasattr(event.source, "group_id"):
            profile = line_bot_api.get_group_member_profile(event.source.group_id, user_id)
        elif hasattr(event.source, "room_id"):
            profile = line_bot_api.get_room_member_profile(event.source.room_id, user_id)
        else:
            profile = line_bot_api.get_profile(user_id)
        return profile.display_name
    except Exception:
        return f"User-{user_id[-6:]}"


@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


@app.route("/", methods=["GET"])
def health():
    return "Hotel Group Log — OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    user_id = event.source.user_id
    if user_id == BOT_USER_ID:
        return

    text = event.message.text.strip()

    # Detect if bot was @mentioned
    bot_mentioned = False
    if hasattr(event.message, "mention") and event.message.mention:
        for m in event.message.mention.mentionees:
            if getattr(m, "type", "") == "user" and getattr(m, "user_id", "") == BOT_USER_ID:
                bot_mentioned = True
                break

    # /สรุป command — admin only
    if text.startswith("/สรุป"):
        if user_id in ADMIN_USER_IDS:
            summary = hotel_service.get_today_summary()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=summary))
        return

    display_name = _get_display_name(event, user_id)
    important = _is_important(text, bot_mentioned)
    hotel_service.log_message(user_id, display_name, "text", text, important)


@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    user_id = event.source.user_id
    if user_id == BOT_USER_ID:
        return
    display_name = _get_display_name(event, user_id)
    hotel_service.log_message(user_id, display_name, "image", "📷 รูปภาพ", False)


# Auto-purge AllMessages sheet every day at 02:00
scheduler = BackgroundScheduler(timezone=TZ)
scheduler.add_job(hotel_service.purge_old_messages, "cron", hour=2, minute=0)
scheduler.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
