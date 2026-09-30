# -*- coding: utf-8 -*-
"""↔️ 擴圖 (outpaint): place a picture on a bigger canvas and let Qwen-Image-2.1's Fun ControlNet Union
redraw the new area through its inpainting branch.

The canvas goes to ComfyUI as one RGBA PNG: LoadImage turns transparent pixels into mask = 1, which the
ControlNet treats as "regenerate". The mask reaches a few pixels into the picture so the seam is redrawn
too, and paste_back() puts the untouched picture on top with a soft edge afterwards.
"""
import math
import os
import tempfile
import uuid

from PIL import Image, ImageDraw, ImageFilter

# Target width / height; None keeps the picture's shape and grows every side by `grow`.
SHAPES = {
    "16:9 橫幅（影片、簡報）": 16 / 9,
    "9:16 直幅（手機、短影音）": 9 / 16,
    "1:1 方形": 1.0,
    "4:3 橫式": 4 / 3,
    "3:4 直式": 3 / 4,
    "21:9 超寬電影感": 21 / 9,
    "四周各擴大一圈（保持比例）": None,
}
# Where the original sits on the new canvas, as (x, y) fractions of the free space.
ANCHORS = {
    "置中（兩邊一起擴）": (0.5, 0.5),
    "靠左（往右擴）": (0.0, 0.5),
    "靠右（往左擴）": (1.0, 0.5),
    "靠上（往下擴）": (0.5, 0.0),
    "靠下（往上擴）": (0.5, 1.0),
}
# Output size in megapixels; Qwen-Image-2.1 is trained up to 2K (about 4 MP).
SIZES = {
    "約 1 MP（快速）": 1.0,
    "約 2 MP（推薦）": 2.0,
    "約 4 MP（2K 高解析 · 較慢）": 4.0,
}
GROW = 0.25          # "四周各擴大一圈": each side grows by a quarter of the picture
SNAP = 16            # VAE downscale 8 × patch 2
OVERLAP = 0.02       # share of the short side redrawn inside the picture so the seam blends


def plan_canvas(width, height, shape, anchor, megapixels):
    """(canvas_w, canvas_h, picture_w, picture_h, x, y) snapped to SNAP, scaled to about `megapixels`."""
    ratio = SHAPES[shape]
    if ratio is None:
        canvas_w, canvas_h = width * (1 + 2 * GROW), height * (1 + 2 * GROW)
        fx, fy = 0.5, 0.5
    else:
        if abs(ratio - width / height) < 0.02:
            raise ValueError("same shape")
        canvas_w, canvas_h = (height * ratio, height) if ratio > width / height else (width, width / ratio)
        fx, fy = ANCHORS[anchor]
    scale = math.sqrt(megapixels * 1e6 / (canvas_w * canvas_h))
    canvas_w, canvas_h = (max(SNAP, round(v * scale / SNAP) * SNAP) for v in (canvas_w, canvas_h))
    picture_w = min(canvas_w, round(width * scale))
    picture_h = min(canvas_h, round(height * scale))
    return canvas_w, canvas_h, picture_w, picture_h, round((canvas_w - picture_w) * fx), round((canvas_h - picture_h) * fy)


def build_canvas(path, shape, anchor, megapixels):
    """Write the RGBA canvas for ComfyUI; returns (canvas_path, plan, resized_picture)."""
    picture = Image.open(path).convert("RGB")
    plan = plan_canvas(*picture.size, shape, anchor, megapixels)
    canvas_w, canvas_h, picture_w, picture_h, x, y = plan
    picture = picture.resize((picture_w, picture_h), Image.LANCZOS)
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (128, 128, 128, 0))
    canvas.paste(picture, (x, y))
    # Opaque = keep. Only the edges that touch new area give up a thin band to the seam.
    keep = Image.new("L", (canvas_w, canvas_h), 0)
    band = max(4, round(min(picture_w, picture_h) * OVERLAP))
    left = x + (band if x > 0 else 0)
    top = y + (band if y > 0 else 0)
    right = x + picture_w - (band if x + picture_w < canvas_w else 0)
    bottom = y + picture_h - (band if y + picture_h < canvas_h else 0)
    ImageDraw.Draw(keep).rectangle([left, top, right - 1, bottom - 1], fill=255)
    canvas.putalpha(keep)
    out = os.path.join(tempfile.gettempdir(), f"h3_outpaint_{uuid.uuid4().hex[:8]}.png")
    canvas.save(out)
    return out, plan, picture


def paste_back(result_path, picture, plan, output_path):
    """Put the original pixels back over the generated picture, fading out across the seam band."""
    canvas_w, canvas_h, picture_w, picture_h, x, y = plan
    result = Image.open(result_path).convert("RGB").resize((canvas_w, canvas_h), Image.LANCZOS)
    band = max(4, round(min(picture_w, picture_h) * OVERLAP))
    # Drawn with `band` of margin so the blur only softens edges that meet new area, never the canvas border.
    fade = Image.new("L", (picture_w + 2 * band, picture_h + 2 * band), 0)
    left = 2 * band if x > 0 else 0
    top = 2 * band if y > 0 else 0
    right = picture_w - (0 if x + picture_w < canvas_w else -2 * band)
    bottom = picture_h - (0 if y + picture_h < canvas_h else -2 * band)
    ImageDraw.Draw(fade).rectangle([left, top, right - 1, bottom - 1], fill=255)
    fade = fade.filter(ImageFilter.GaussianBlur(band / 2)).crop((band, band, band + picture_w, band + picture_h))
    result.paste(picture, (x, y), fade)
    result.save(output_path)
    return output_path


def direction_text(plan):
    """Plain-English note for the prompt writer on where the canvas grew."""
    canvas_w, canvas_h, picture_w, picture_h, x, y = plan
    sides = [name for name, grown in (("left", x > 0), ("right", x + picture_w < canvas_w),
                                      ("top", y > 0), ("bottom", y + picture_h < canvas_h)) if grown]
    return ", ".join(sides) or "all sides"
