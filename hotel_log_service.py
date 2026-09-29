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
            ws = self.sheet.add_worksheet("AllMessages", rows=2000, cols=8)
            ws.append_row(["Timestamp", "UserID", "Name", "Type", "Content", "Important", "Description", "Category"])
        else:
            ws = self.sheet.worksheet("AllMessages")
            headers = ws.row_values(1)
            if len(headers) < 7:
                ws.resize(cols=8)
                ws.update_cell(1, 7, "Description")
                ws.update_cell(1, 8, "Category")
            elif len(headers) < 8:
                ws.resize(cols=8)
                ws.update_cell(1, 8, "Category")
        if "Important" not in existing:
            ws = self.sheet.add_worksheet("Important", rows=500, cols=6)
            ws.append_row(["Timestamp", "UserID", "Name", "Type", "Content", "Note"])
        self.all_ws = self.sheet.worksheet("AllMessages")
        self.important_ws = self.sheet.worksheet("Important")

    @staticmethod
    def classify(text: str, msg_type: str) -> str:
        if msg_type == "link":
            return "ลิงค์"
        if msg_type == "video":
            return "วิดีโอ"
        if msg_type == "image":
            return "รูปภาพ"
        t = text.lower()
        if "✅" in text:
            return "ห้องพร้อม"
        if any(w in t for w in ["check out", "checkout", "เช็คเอ้า", "เช็คเอาท์"]):
            return "check-out"
        if "ค้างคืน" in t:
            return "check-in ค้างคืน"
        if "ชั่วคราว" in t:
            return "check-in ชั่วคราว"
        if any(w in t for w in ["check in", "checkin", "เช็คอิน"]):
            return "check-in"
        if any(w in t for w in ["ซ่อม", "ซ่อมแซม", "บำรุง"]) or ("เปลี่ยน" in t and "ห้อง" in t):
            return "ซ่อมบำรุง"
        if "ย้ายห้อง" in t or ("ย้ายไป" in t and "ห้อง" in t) or "โอนห้อง" in t:
            return "ย้ายห้อง"
        return "ทั่วไป"

    def log_message(self, user_id: str, display_name: str, msg_type: str, content: str, important: bool, description: str = "", category: str = ""):
        if not self.all_ws:
            return
        now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
        row = [now, user_id, display_name, msg_type, content, "⭐" if important else "", description, category]
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
            import base64 as _b64
            b64 = _b64.standard_b64encode(image_bytes).decode("utf-8")
            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
            resp = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=300,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
                        {"type": "text", "text": "ถอดข้อความในภาพทุกตัวอักษร ถ้าไม่มีข้อความให้อธิบายภาพสั้นๆ 1 ประโยค ตอบเป็น plain text ห้ามใช้ markdown"},
                    ],
                }],
            )
            return resp.content[0].text.strip()
        except Exception as e:
            return f"(OCR error: {e})"

    def get_shift_bounds(self) -> tuple:
        """Returns (shift_start, shift_end, shift_name) for current Bangkok shift."""
        now = datetime.now(TZ)
        h = now.hour
        if 8 <= h < 17:
            start = now.replace(hour=8, minute=0, second=0, microsecond=0)
            end = now.replace(hour=17, minute=0, second=0, microsecond=0)
            name = "กะเช้า ☀️"
        elif h >= 17:
            start = now.replace(hour=17, minute=0, second=0, microsecond=0)
            end = (now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
            name = "กะดึก 🌙"
        else:
            start = (now - timedelta(days=1)).replace(hour=17, minute=0, second=0, microsecond=0)
            end = now.replace(hour=8, minute=0, second=0, microsecond=0)
            name = "กะดึก 🌙"
        return start, end, name

    def _count_cat(self, rows: list, category: str) -> int:
        return sum(1 for r in rows if len(r) > 7 and r[7] == category)

    def get_shift_summary_text(self, shift_start: datetime, shift_end: datetime, shift_name: str) -> str:
        if not self.all_ws:
            return "❌ เชื่อมต่อ Sheets ไม่ได้"
        try:
            all_rows = self.all_ws.get_all_values()
            shift_rows = []
            for r in all_rows[1:]:
                if not r[0]:
                    continue
                try:
                    ts = datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=TZ)
                    if shift_start <= ts < shift_end:
                        shift_rows.append(r)
                except ValueError:
                    continue

            date_str = shift_start.strftime("%d/%m/%Y")
            overnight = self._count_cat(shift_rows, "check-in ค้างคืน")
            temp = self._count_cat(shift_rows, "check-in ชั่วคราว")
            gen_ci = self._count_cat(shift_rows, "check-in")
            checkout = self._count_cat(shift_rows, "check-out")
            room_ready = self._count_cat(shift_rows, "ห้องพร้อม")

            lines = [
                f"📋 {shift_name} — {date_str}",
                f"{'━' * 16}",
                f"🏨 check-in ค้างคืน: {overnight} ห้อง",
                f"⏰ check-in ชั่วคราว: {temp} ห้อง",
            ]
            if gen_ci > 0:
                lines.append(f"🔑 check-in (อื่นๆ): {gen_ci} ห้อง")
            lines += [
                f"🚪 check-out: {checkout} ห้อง",
                f"✅ ห้องพร้อม: {room_ready} ห้อง",
                f"{'━' * 16}",
                f"📨 รวมข้อความ: {len(shift_rows)} รายการ",
            ]
            return "\n".join(lines)
        except Exception as e:
            return f"❌ สรุปกะไม่ได้: {e}"

    def get_dashboard_data(self, start_date: str, end_date: str) -> dict:
        """Aggregate data for dashboard. start/end = 'YYYY-MM-DD' Bangkok time."""
        import re as _re
        ROOM_RE = _re.compile(r'(?:ห้อง\s*)?(\b\d{3}\b)')
        if not self.all_ws:
            return {}
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=TZ)
            end = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=TZ) + timedelta(days=1)
        except ValueError:
            return {}
        try:
            all_rows = self.all_ws.get_all_values()
        except Exception:
            return {}

        daily: dict = {}
        hourly = [0] * 24
        categories: dict = {}
        rooms: dict = {}

        for r in all_rows[1:]:
            if not r[0]:
                continue
            try:
                ts = datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=TZ)
            except ValueError:
                continue
            if ts < start or ts >= end:
                continue

            date_str = ts.strftime("%Y-%m-%d")
            cat = r[7] if len(r) > 7 else ""
            content = r[4] if len(r) > 4 else ""
            desc = r[6] if len(r) > 6 else ""

            if date_str not in daily:
                daily[date_str] = {
                    "check-in ค้างคืน": 0, "check-in ชั่วคราว": 0,
                    "check-in": 0, "check-out": 0, "ห้องพร้อม": 0, "total": 0,
                }
            daily[date_str]["total"] += 1
            if cat in daily[date_str]:
                daily[date_str][cat] += 1

            hourly[ts.hour] += 1

            if cat:
                categories[cat] = categories.get(cat, 0) + 1

            m = ROOM_RE.search(f"{content} {desc}")
            if m:
                room = m.group(1)
                rooms[room] = rooms.get(room, 0) + 1

        daily_list = sorted(
            [{"date": d, **v} for d, v in daily.items()],
            key=lambda x: x["date"],
        )
        rooms_sorted = dict(sorted(rooms.items(), key=lambda x: x[1], reverse=True)[:20])
        total_checkin = (
            categories.get("check-in ค้างคืน", 0)
            + categories.get("check-in ชั่วคราว", 0)
            + categories.get("check-in", 0)
        )
        return {
            "daily": daily_list,
            "hourly": hourly,
            "categories": categories,
            "rooms": rooms_sorted,
            "summary": {
                "total_checkin": total_checkin,
                "total_checkout": categories.get("check-out", 0),
                "total_room_ready": categories.get("ห้องพร้อม", 0),
                "total_messages": sum(v["total"] for v in daily.values()),
            },
        }

    def get_roommap_data(self, start_date: str, end_date: str) -> dict:
        """Return per-room activity, maintenance, transfers, and financial estimates."""
        import re as _re
        ROOM_RE = _re.compile(r'ห้อง\s*(\d{3})')
        XFER_RE = _re.compile(r'ห้อง\s*(\d{3}).{0,20}(?:ย้ายไป|ไป|→)\s*ห้อง\s*(\d{3})')
        if not self.all_ws:
            return {}
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=TZ)
            end = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=TZ) + timedelta(days=1)
        except ValueError:
            return {}
        try:
            all_rows = self.all_ws.get_all_values()
        except Exception:
            return {}

        rooms: dict = {}
        maint: dict = {}
        xfers: list = []
        total_ov = total_tp = 0

        for r in all_rows[1:]:
            if not r[0]:
                continue
            try:
                ts = datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=TZ)
            except ValueError:
                continue
            if ts < start or ts >= end:
                continue

            cat = r[7] if len(r) > 7 else ""
            content = r[4] if len(r) > 4 else ""
            desc = r[6] if len(r) > 6 else ""
            text = f"{content} {desc}"
            date_str = ts.strftime("%d/%m")
            time_str = ts.strftime("%H:%M")

            m = ROOM_RE.search(text)
            room = m.group(1) if m else None

            if room:
                if room not in rooms:
                    rooms[room] = {"ov": 0, "tp": 0, "rd": 0, "co": 0}
                if cat == "check-in ค้างคืน":
                    rooms[room]["ov"] += 1
                    total_ov += 1
                elif cat == "check-in ชั่วคราว":
                    rooms[room]["tp"] += 1
                    total_tp += 1
                elif cat == "ห้องพร้อม":
                    rooms[room]["rd"] += 1
                elif cat == "check-out":
                    rooms[room]["co"] += 1
                elif cat == "ซ่อมบำรุง":
                    if room not in maint:
                        maint[room] = []
                    maint[room].append({"date": date_str, "note": content[:80]})

            if cat == "ย้ายห้อง":
                xm = XFER_RE.search(text)
                if xm:
                    xfers.append({
                        "date": date_str, "time": time_str,
                        "from": xm.group(1), "to": xm.group(2),
                        "note": content[:50]
                    })

        return {
            "rooms": rooms,
            "maint": maint,
            "xfers": xfers[-30:],
            "finance": {
                "calc": total_ov * 500 + total_tp * 180,
                "ocr": None,
                "shop": None,
            },
        }

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
