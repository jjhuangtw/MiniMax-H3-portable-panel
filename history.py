"""Append-only log of finished generations, so prompts and settings can be reused later."""
import json
import os
import subprocess
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_PATH = os.path.join(BASE_DIR, "generation_history.jsonl")
THUMB_DIR = os.path.join(BASE_DIR, "history_thumbs")
COLUMNS = ["時間", "分頁", "解析度", "秒數", "種子", "模型", "提示詞"]
MAX_ROWS = 300


def _make_thumbnail(output):
    """A small poster frame for the gallery: the first frame of a video, or the image itself."""
    if not output or not os.path.exists(output):
        return ""
    if output.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        return output
    try:
        import imageio_ffmpeg
        os.makedirs(THUMB_DIR, exist_ok=True)
        thumb = os.path.join(THUMB_DIR, os.path.splitext(os.path.basename(output))[0] + ".jpg")
        if not os.path.exists(thumb):
            subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y",
                            "-i", output, "-frames:v", "1", "-vf", "scale=320:-2", thumb],
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), timeout=60)
        return thumb if os.path.exists(thumb) else ""
    except Exception as error:
        print(f"[History] 無法建立縮圖: {error}")
        return ""


def record(kind, prompt, output, **details):
    """One JSON line per generation; a corrupt or unwritable log must never fail a generation."""
    out = output if isinstance(output, str) else (output[0] if output else "")
    entry = {"time": time.strftime("%m-%d %H:%M"), "kind": kind, "prompt": prompt or "",
             "output": out, "thumb": _make_thumbnail(out),
             **{k: v for k, v in details.items() if v is not None}}
    try:
        with open(HISTORY_PATH, "a", encoding="utf-8") as stream:
            stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as error:
        print(f"[History] 無法寫入紀錄: {error}")
    return entry


def gallery(rows):
    """(thumbnail, caption) pairs for a gr.Gallery; rows without a thumbnail are skipped."""
    items = []
    for r in rows:
        thumb = r.get("thumb") or (r.get("output") if str(r.get("output", "")).lower().endswith((".png", ".jpg", ".jpeg", ".webp")) else "")
        if thumb and os.path.exists(thumb):
            caption = f"{r.get('time', '')} · {' '.join((r.get('prompt') or '').split())[:40]}"
            items.append((thumb, caption))
    return items


def rows_with_thumb(rows):
    return [r for r in rows if (r.get("thumb") or r.get("output", "")) and
            os.path.exists(r.get("thumb") or r.get("output", ""))]


def entries(limit=MAX_ROWS):
    if not os.path.exists(HISTORY_PATH):
        return []
    rows = []
    try:
        with open(HISTORY_PATH, encoding="utf-8") as stream:
            for line in stream:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except OSError as error:
        print(f"[History] 無法讀取紀錄: {error}")
        return []
    return rows[-limit:][::-1]  # newest first


def table(rows):
    # Every cell as text: the Dataframe declares str columns and silently drops non-string values.
    return [[str(r.get("time", "")), str(r.get("kind", "")), str(r.get("resolution", "")),
             str(r.get("seconds", "")), str(r.get("seed", "")), os.path.basename(str(r.get("model", ""))),
             " ".join((r.get("prompt") or "").split())[:70]] for r in rows]


def details_text(row):
    if not row:
        return ""
    keys = [("kind", "分頁"), ("resolution", "解析度"), ("seconds", "秒數"), ("seed", "種子"),
            ("mode", "採樣模式"), ("scheduler", "排程"), ("model", "擴散模型"), ("encoder", "文字編碼器"),
            ("lora", "LoRA"), ("lora_strength", "LoRA 強度"), ("hd", "高清二次採樣"), ("output", "輸出檔")]
    lines = [f"- **{label}**：{row[key]}" for key, label in keys if row.get(key) not in (None, "", False)]
    return "\n".join(lines)
