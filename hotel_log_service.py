import os
import json
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
            creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "{}")
            creds_dict = json.loads(creds_json)
            creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
            client = gspread.authorize(creds)
            sheet_id = os.environ.get("HOTEL_LOG_SHEET_ID", "")
            self.sheet = client.open_by_key(sheet_id)
            self._init_worksheets()
            print("[INFO] Google Sheets connected")
        except Exception as e:
            print(f"[ERROR] Sheet connect failed: {e}")

    def _init_worksheets(self):
        existing = {ws.title for ws in self.sheet.worksheets()}

        if "AllMessages" not in existing:
            ws = self.sheet.add_worksheet("AllMessages", rows=2000, cols=6)
            ws.append_row(["Timestamp", "UserID", "Name", "Type", "Content", "Important"])
        if "Important" not in existing:
            ws = self.sheet.add_worksheet("Important", rows=500, cols=6)
            ws.append_row(["Timestamp", "UserID", "Name", "Type", "Content", "Note"])

        self.all_ws = self.sheet.worksheet("AllMessages")
        self.important_ws = self.sheet.worksheet("Important")

    def log_message(self, user_id: str, display_name: str, msg_type: str,
                    content: str, important: bool):
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
        """Delete rows in AllMessages older than 45 days."""
        if not self.all_ws:
            return
        try:
            cutoff = datetime.now(TZ) - timedelta(days=45)
            all_rows = self.all_ws.get_all_values()
            to_delete = []
            for i, row in enumerate(all_rows[1:], start=2):
                if not row or not row[0]:
                    continue
                try:
                    ts = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=TZ)
                    if ts < cutoff:
                        to_delete.append(i)
                except ValueError:
                    continue
            for idx in sorted(to_delete, reverse=True):
                self.all_ws.delete_rows(idx)
            print(f"[PURGE] Removed {len(to_delete)} rows older than 45 days")
        except Exception as e:
            print(f"[ERROR] purge_old_messages: {e}")

    def get_today_summary(self) -> str:
        """Ask Claude Haiku to summarise today's activity from AllMessages."""
        if not self.all_ws:
            return "ไม่สามารถเชื่อมต่อ Sheets ได้"
        try:
            today = datetime.now(TZ).date().isoformat()
            all_rows = self.all_ws.get_all_values()
            today_rows = [r for r in all_rows[1:] if r and r[0].startswith(today)]

            if not today_rows:
                return "ยังไม่มีข้อความในกลุ่มวันนี้ค่ะ"

            text_lines = [
                f"[{r[2]}] {r[4]}" for r in today_rows if r[3] == "text"
            ]
            image_count = sum(1 for r in today_rows if r[3] == "image")

            log_block = "\n".join(text_lines[-60:])  # last 60 messages

            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            resp = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=600,
                messages=[{
                    "role": "user",
                    "content": (
                        f"สรุปกิจกรรมโรงแรมวันนี้จากข้อความในกลุ่ม LINE:\n\n"
                        f"{log_block}\n\n"
                        f"(มีรูปภาพ {image_count} รูป)\n\n"
                        "สรุปเป็นภาษาไทยสั้นๆ: มีอะไรเกิดขึ้น ใครทำอะไร มีปัญหาไหม"
                    ),
                }],
            )
            return resp.content[0].text
        except Exception as e:
            return f"สรุปไม่ได้: {e}"
