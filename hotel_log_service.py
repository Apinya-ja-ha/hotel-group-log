import os
import json
import base64
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pytz
import anthropic

TZ = pytz.timezone("Asia/Bangkok")
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]


class HotelLogService:
    def __init__(self):
        self.sheet = None
        self.all_ws = None
        self.important_ws = None
        self._connect()

    def _connect(self):
        try:
            raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
            if not raw.startswith("{"):
                raw = base64.b64decode(raw).decode("utf-8")
            creds_dict = json.loads(raw)
            creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
            client = gspread.authorize(creds)
            self.sheet = client.open_by_key(os.environ.get("HOTEL_LOG_SHEET_ID", ""))
            self._ensure_worksheets()
            print("[OK] Google Sheets connected")
        except Exception as e:
            print(f"[ERROR] Sheet connect: {e}")

    def _ensure_worksheets(self):
        existing = [ws.title for ws in self.sheet.worksheets()]
        if "AllMessages" not in existing:
            ws = self.sheet.add_worksheet("AllMessages", rows=2000, cols=6)
            ws.append_row(["Timestamp", "UserID", "Name", "Type", "Content", "Important"])
        if "Important" not in existing:
            ws = self.sheet.add_worksheet("Important", rows=500, cols=6)
            ws.append_row(["Timestamp", "UserID", "Name", "Type", "Content", "Note"])
        self.all_ws = self.sheet.worksheet("AllMessages")
        self.important_ws = self.sheet.worksheet("Important")

    def log_message(self, user_id: str, display_name: str, msg_type: str, content: str, important: bool):
        if not self.all_ws:
            return
        now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
        row = [now, user_id, display_name, msg_type, content, "⭐" if important else ""]
        try:
            self.all_ws.append_row(row)
            if important:
                self.important_ws.append_row(row)
        except Exception as e:
            print(f"[ERROR] log_message: {e}")

    def purge_old_messages(self):
        """Delete rows older than 45 days from AllMessages sheet."""
        if not self.all_ws:
            return
        try:
            cutoff = datetime.now(TZ) - timedelta(days=45)
            all_rows = self.all_ws.get_all_values()
            to_delete = []
            for i, row in enumerate(all_rows[1:], start=2):
                if not row[0]:
                    continue
                try:
                    ts = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=TZ)
                    if ts < cutoff:
                        to_delete.append(i)
                except ValueError:
                    continue
            for idx in sorted(to_delete, reverse=True):
                self.all_ws.delete_rows(idx)
            print(f"[PURGE] Deleted {len(to_delete)} rows older than 45 days")
        except Exception as e:
            print(f"[ERROR] purge: {e}")

    def ocr_image(self, image_bytes: bytes) -> str:
        try:
            import base64
            b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
            resp = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=300,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
                        {"type": "text", "text": "ถอดข้อความในภาพ ถ้าไม่มีข้อความให้อธิบายภาพสั้นๆ 1-2 ประโยค"},
                    ],
                }],
            )
            return f"📷 {resp.content[0].text.strip()}"
        except Exception as e:
            return f"📷 รูปภาพ (OCR error: {e})"

    def get_today_summary(self) -> str:
        if not self.all_ws:
            return "❌ เชื่อมต่อ Sheets ไม่ได้"
        try:
            today = datetime.now(TZ).strftime("%Y-%m-%d")
            all_rows = self.all_ws.get_all_values()
            today_rows = [r for r in all_rows[1:] if r[0].startswith(today)]

            if not today_rows:
                return "📋 ยังไม่มีข้อความวันนี้"

            text_rows = [r for r in today_rows if r[3] == "text"]
            image_count = sum(1 for r in today_rows if r[3] == "image")

            if not text_rows:
                return f"📋 วันนี้มีรูปภาพ {image_count} รูป แต่ไม่มีข้อความ"

            log_lines = "\n".join(f"[{r[2]}] {r[4]}" for r in text_rows[-60:])

            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
            resp = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=600,
                messages=[{
                    "role": "user",
                    "content": (
                        f"สรุปกิจกรรมโรงแรมวันนี้จากข้อความในกลุ่ม LINE:\n\n"
                        f"{log_lines}\n\n"
                        f"(รูปภาพ {image_count} รูป)\n\n"
                        "สรุปสั้นๆ 5-8 บรรทัด: ใครทำอะไร มีปัญหาอะไรบ้าง "
                        "รายการสำคัญที่ต้องติดตาม"
                    ),
                }],
            )
            return f"📊 สรุปวันนี้ ({today})\n\n{resp.content[0].text}"
        except Exception as e:
            return f"❌ สรุปไม่ได้: {e}"
