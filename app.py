import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageMessage, VideoMessage, TextSendMessage
from hotel_log_service import HotelLogService
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

app = Flask(__name__)

LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET", "")
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")
ADMIN_USER_IDS = set(filter(None, os.environ.get("ADMIN_USER_IDS", "").split(",")))
BOT_USER_ID = os.environ.get("BOT_USER_ID", "")
CRON_SECRET = os.environ.get("CRON_SECRET", "")
TZ = pytz.timezone("Asia/Bangkok")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
hotel_service = HotelLogService()

IMPORTANT_KEYWORDS = ["แอดมิน", "admin", "@admin", "ด่วน", "urgent", "สำคัญ"]
URL_RE = re.compile(r'https?://\S+')

HELP_TEXT = (
    "📌 คำสั่งแอดมิน:\n"
    "/สรุป — สรุปกิจกรรมวันนี้ (AI)\n"
    "/กะนี้ — รายงานกะปัจจุบัน\n"
    "/ห้องพร้อม — ห้องพร้อมกะนี้\n"
    "/ยอด — ยอดเงินกะนี้\n"
    "/ซ่อม — บันทึกซ่อมบำรุง\n"
    "/help — แสดงคำสั่งทั้งหมด"
)


def _fetch_link_title(url: str) -> str:
    try:
        resp = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
        soup = BeautifulSoup(resp.text, "html.parser")
        title = (
            (soup.find("meta", property="og:title") or {}).get("content")
            or (soup.find("title") and soup.find("title").get_text())
            or ""
        )
        title = title.strip()[:120]
        return f"🔗 {title} — {url}" if title else f"🔗 {url}"
    except Exception:
        return f"🔗 {url}"


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


def _push_to_admins(text: str):
    for admin_id in ADMIN_USER_IDS:
        try:
            line_bot_api.push_message(admin_id, TextSendMessage(text=text))
        except Exception as e:
            print(f"[ERROR] push to {admin_id}: {e}")


def _morning_report():
    """08:00 — report on กะดึก that just ended (17:00 yesterday → 08:00 now)."""
    now = datetime.now(TZ)
    end = now.replace(hour=8, minute=0, second=0, microsecond=0)
    start = (now - timedelta(days=1)).replace(hour=17, minute=0, second=0, microsecond=0)
    text = hotel_service.get_shift_summary_text(start, end, "กะดึก 🌙")
    _push_to_admins(f"🔔 รายงานอัตโนมัติ\n{text}")


def _evening_report():
    """17:00 — report on กะเช้า that just ended (08:00 → 17:00 today)."""
    now = datetime.now(TZ)
    end = now.replace(hour=17, minute=0, second=0, microsecond=0)
    start = now.replace(hour=8, minute=0, second=0, microsecond=0)
    text = hotel_service.get_shift_summary_text(start, end, "กะเช้า ☀️")
    _push_to_admins(f"🔔 รายงานอัตโนมัติ\n{text}")


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


@app.route("/dashboard")
def dashboard():
    key = request.args.get("key", "")
    if not CRON_SECRET or key != CRON_SECRET:
        abort(403)
    from dashboard_page import DASHBOARD_HTML
    return DASHBOARD_HTML


@app.route("/api/data")
def api_data():
    key = request.args.get("key", "")
    if not CRON_SECRET or key != CRON_SECRET:
        abort(403)
    start = request.args.get("start", "")
    end = request.args.get("end", "")
    if not start or not end:
        return {"error": "missing start/end"}, 400
    data = hotel_service.get_dashboard_data(start, end)
    return data


@app.route("/roommap")
def roommap():
    key = request.args.get("key", "")
    if not CRON_SECRET or key != CRON_SECRET:
        abort(403)
    from roommap_page import ROOMMAP_HTML
    return ROOMMAP_HTML


@app.route("/api/roommap")
def api_roommap():
    key = request.args.get("key", "")
    if not CRON_SECRET or key != CRON_SECRET:
        abort(403)
    start = request.args.get("start", "")
    end = request.args.get("end", "")
    if not start or not end:
        return {"error": "missing start/end"}, 400
    data = hotel_service.get_roommap_data(start, end)
    return data


@app.route("/admin/setup-richmenu/<secret>")
def setup_richmenu(secret):
    if not CRON_SECRET or secret != CRON_SECRET:
        abort(403)
    try:
        from rich_menu import create_and_set_richmenu
        result = create_and_set_richmenu(LINE_CHANNEL_ACCESS_TOKEN)
        return result
    except Exception as e:
        return f"Error: {e}", 500


@handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    user_id = event.source.user_id
    if user_id == BOT_USER_ID:
        return

    text = event.message.text.strip()
    is_admin = user_id in ADMIN_USER_IDS

    # Detect if bot was @mentioned
    bot_mentioned = False
    if hasattr(event.message, "mention") and event.message.mention:
        for m in event.message.mention.mentionees:
            if getattr(m, "type", "") == "user" and getattr(m, "user_id", "") == BOT_USER_ID:
                bot_mentioned = True
                break

    # --- Admin commands ---
    if text.startswith("/สรุป"):
        if is_admin:
            summary = hotel_service.get_today_summary()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=summary))
        return

    if text.startswith("/กะนี้"):
        if is_admin:
            start, end, name = hotel_service.get_shift_bounds()
            summary = hotel_service.get_shift_summary_text(start, end, name)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=summary))
        return

    if text.startswith("/ห้องพร้อม"):
        if is_admin:
            start, end, name = hotel_service.get_shift_bounds()
            summary = hotel_service.get_shift_summary_text(start, end, name)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=summary))
        return

    if text.startswith("/ยอด"):
        if is_admin:
            start, end, name = hotel_service.get_shift_bounds()
            summary = hotel_service.get_shift_summary_text(start, end, name)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=summary))
        return

    if text.startswith("/ซ่อม"):
        if is_admin:
            reply = (
                "🔧 บันทึกซ่อม/บำรุง\n"
                "พิมพ์รายละเอียดในกลุ่มโรงแรม\n"
                "ระบบจะบันทึกไว้ให้อัตโนมัติ\n\n"
                "ตัวอย่าง:\n"
                "ห้อง 101 เปลี่ยนหลอดไฟ\n"
                "ห้อง 203 ล้างแอร์"
            )
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    if text.startswith("/help"):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=HELP_TEXT))
        return

    # --- Log normal messages ---
    display_name = _get_display_name(event, user_id)
    urls = URL_RE.findall(text)
    if urls:
        content = _fetch_link_title(urls[0])
        msg_type = "link"
    else:
        content = text
        msg_type = "text"
    important = _is_important(text, bot_mentioned)
    category = hotel_service.classify(text, msg_type)
    hotel_service.log_message(user_id, display_name, msg_type, content, important, category=category)


@handler.add(MessageEvent, message=VideoMessage)
def handle_video(event):
    user_id = event.source.user_id
    if user_id == BOT_USER_ID:
        return
    display_name = _get_display_name(event, user_id)
    hotel_service.log_message(user_id, display_name, "video", "🎬 วิดีโอ", False, category="วิดีโอ")


@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    user_id = event.source.user_id
    if user_id == BOT_USER_ID:
        return
    display_name = _get_display_name(event, user_id)
    try:
        content_stream = line_bot_api.get_message_content(event.message.id)
        image_bytes = b"".join(chunk for chunk in content_stream.iter_content())
        description = hotel_service.ocr_image(image_bytes)
    except Exception:
        description = ""
    category = hotel_service.classify(description, "image")
    hotel_service.log_message(user_id, display_name, "image", "📷 รูปภาพ", False, description, category)


# Scheduled jobs (Bangkok timezone)
scheduler = BackgroundScheduler(timezone=TZ)
scheduler.add_job(hotel_service.purge_old_messages, "cron", hour=2, minute=0)
scheduler.add_job(_morning_report, "cron", hour=8, minute=0)
scheduler.add_job(_evening_report, "cron", hour=17, minute=0)
scheduler.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
