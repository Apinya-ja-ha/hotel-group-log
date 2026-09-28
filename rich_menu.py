import os
import io
import requests
from PIL import Image, ImageDraw, ImageFont


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    font_path = os.path.join(os.path.dirname(__file__), "fonts", "Sarabun-Bold.ttf")
    try:
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()


def create_richmenu_image() -> bytes:
    W, H = 2500, 843
    COLS, ROWS = 3, 2
    BW, BH = W // COLS, H // ROWS

    COLORS = [
        (41, 128, 185),   # สรุปวันนี้ — blue
        (39, 174, 96),    # กะนี้ — green
        (142, 68, 173),   # ห้องพร้อม — purple
        (230, 126, 34),   # ยอด — orange
        (192, 57, 43),    # ซ่อม — red
        (127, 140, 141),  # ช่วยเหลือ — gray
    ]
    BUTTONS = [
        ("สรุปวันนี้",  "/สรุป"),
        ("กะนี้",      "/กะนี้"),
        ("ห้องพร้อม",  "/ห้องพร้อม"),
        ("ยอด",       "/ยอด"),
        ("ซ่อม/บำรุง", "/ซ่อม"),
        ("ช่วยเหลือ",  "/help"),
    ]

    img = Image.new("RGB", (W, H), color=(20, 20, 20))
    draw = ImageDraw.Draw(img)
    font_main = _load_font(80)
    font_sub = _load_font(46)

    for i, ((label, cmd), color) in enumerate(zip(BUTTONS, COLORS)):
        row = i // COLS
        col = i % COLS
        x0 = col * BW + 8
        y0 = row * BH + 8
        x1 = x0 + BW - 16
        y1 = y0 + BH - 16
        draw.rounded_rectangle([x0, y0, x1, y1], radius=24, fill=color)

        cx = col * BW + BW // 2
        cy = row * BH + BH // 2
        draw.text((cx, cy - 52), cmd, font=font_sub, fill=(255, 255, 255, 160), anchor="mm")
        draw.text((cx, cy + 40), label, font=font_main, fill="white", anchor="mm")

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=93)
    return buf.getvalue()


def create_and_set_richmenu(access_token: str) -> str:
    headers_json = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    headers_auth = {"Authorization": f"Bearer {access_token}"}

    # Delete existing default rich menu
    try:
        resp = requests.get(
            "https://api.line.me/v2/bot/user/all/richmenu",
            headers=headers_auth, timeout=10,
        )
        if resp.ok:
            old_id = resp.json().get("richMenuId")
            if old_id:
                requests.delete(
                    f"https://api.line.me/v2/bot/richmenu/{old_id}",
                    headers=headers_auth, timeout=10,
                )
    except Exception:
        pass

    BW, BH = 2500 // 3, 843 // 2
    ACTIONS = [
        {"type": "message", "text": "/สรุป"},
        {"type": "message", "text": "/กะนี้"},
        {"type": "message", "text": "/ห้องพร้อม"},
        {"type": "message", "text": "/ยอด"},
        {"type": "message", "text": "/ซ่อม"},
        {"type": "message", "text": "/help"},
    ]
    areas = []
    for i, action in enumerate(ACTIONS):
        row = i // 3
        col = i % 3
        areas.append({
            "bounds": {"x": col * BW, "y": row * BH, "width": BW, "height": BH},
            "action": action,
        })

    menu_body = {
        "size": {"width": 2500, "height": 843},
        "selected": True,
        "name": "Admin Menu",
        "chatBarText": "เมนูแอดมิน",
        "areas": areas,
    }
    r = requests.post(
        "https://api.line.me/v2/bot/richmenu",
        headers=headers_json, json=menu_body, timeout=15,
    )
    if not r.ok:
        return f"Create rich menu failed: {r.status_code} {r.text}"
    rich_menu_id = r.json().get("richMenuId")

    img_bytes = create_richmenu_image()
    r2 = requests.post(
        f"https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content",
        headers={**headers_auth, "Content-Type": "image/jpeg"},
        data=img_bytes, timeout=30,
    )
    if not r2.ok:
        return f"Upload image failed: {r2.status_code} {r2.text}"

    r3 = requests.post(
        f"https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}",
        headers=headers_auth, timeout=10,
    )
    if not r3.ok:
        return f"Set default failed: {r3.status_code} {r3.text}"

    return f"OK richMenuId={rich_menu_id}"
