"""History manager for MiniMax H3 WebUI.

Supports separating images and videos, previewing outputs, and deleting entries from history and disk.
"""
import json
import os
import subprocess
import time

from ui_i18n import L

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_PATH = os.path.join(BASE_DIR, "generation_history.jsonl")
THUMB_DIR = os.path.join(BASE_DIR, "history_thumbs")
MAX_ROWS = 500


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


def is_image(row):
    out = str(row.get("output", "")).lower()
    kind = str(row.get("kind", ""))
    return out.endswith((".png", ".jpg", ".jpeg", ".webp")) or "圖片" in kind or "修圖" in kind


def record(kind, prompt, output, **details):
    """One JSON line per generation; a corrupt or unwritable log must never fail a generation."""
    out = output if isinstance(output, str) else (output[0] if output else "")
    entry = {
        "id": f"{int(time.time() * 1000)}_{os.getpid()}",
        "time": time.strftime("%m-%d %H:%M"),
        "kind": kind,
        "prompt": prompt or "",
        "output": out,
        "thumb": _make_thumbnail(out),
        **{k: v for k, v in details.items() if v is not None}
    }
    try:
        with open(HISTORY_PATH, "a", encoding="utf-8") as stream:
            stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as error:
        print(f"[History] 無法寫入紀錄: {error}")
    return entry


def entries(category="all", limit=MAX_ROWS):
    """Read history rows, newest first. Filter by category: 'image', 'video', or 'all'."""
    if not os.path.exists(HISTORY_PATH):
        return []
    rows = []
    try:
        with open(HISTORY_PATH, encoding="utf-8") as stream:
            for idx, line in enumerate(stream):
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                    if not r.get("id"):
                        r["id"] = f"row_{idx}"
                    rows.append(r)
                except json.JSONDecodeError:
                    continue
    except OSError as error:
        print(f"[History] 無法讀取紀錄: {error}")
        return []

    # Filter by category
    if category == "image":
        rows = [r for r in rows if is_image(r)]
    elif category == "video":
        rows = [r for r in rows if not is_image(r)]

    return rows[-limit:][::-1]  # newest first


def rows_with_thumb(rows):
    """Only rows whose output or thumbnail exists on disk, guaranteed 1:1 with gallery."""
    valid = []
    for r in rows:
        out = r.get("output", "")
        thumb = r.get("thumb")
        if thumb and os.path.exists(thumb):
            valid.append(r)
        elif out and os.path.exists(out):
            # Recreate thumbnail if missing
            new_thumb = _make_thumbnail(out)
            if new_thumb:
                r["thumb"] = new_thumb
            valid.append(r)
    return valid


def gallery(rows):
    """(thumbnail, caption) pairs for gr.Gallery; guaranteed exactly len(rows) items."""
    items = []
    for r in rows:
        thumb = r.get("thumb")
        out = r.get("output", "")
        img = thumb if (thumb and os.path.exists(thumb)) else (out if (out and os.path.exists(out)) else "")
        caption = f"{r.get('time', '')} · {' '.join((r.get('prompt') or '').split())[:40]}"
        items.append((img, caption))
    return items


def delete_entry(target_id, target_output=None, delete_file=False):
    """Delete a single history entry from JSONL, and optionally delete the file on disk."""
    if not os.path.exists(HISTORY_PATH):
        return False, L("紀錄檔不存在")
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as stream:
            lines = [l for l in stream if l.strip()]
    except Exception as e:
        return False, L("讀取紀錄失敗: {0}", e)

    kept_lines = []
    deleted_entry = None
    for idx, l in enumerate(lines):
        try:
            r = json.loads(l)
            r_id = r.get("id") or f"row_{idx}"
            r_out = r.get("output")
            if (target_id and r_id == target_id) or (target_output and r_out == target_output):
                deleted_entry = r
                continue
            kept_lines.append(l)
        except Exception:
            kept_lines.append(l)

    if not deleted_entry:
        return False, L("找不到對應的紀錄")

    try:
        with open(HISTORY_PATH, "w", encoding="utf-8") as stream:
            stream.writelines(kept_lines)
    except Exception as e:
        return False, L("寫入紀錄檔失敗: {0}", e)

    # Optionally delete file on disk
    if delete_file and deleted_entry:
        out = deleted_entry.get("output")
        if out and os.path.exists(out):
            try:
                os.remove(out)
            except Exception as e:
                print(f"[History] 刪除檔案失敗: {e}")
        thumb = deleted_entry.get("thumb")
        if thumb and os.path.exists(thumb) and thumb.startswith(THUMB_DIR):
            try:
                os.remove(thumb)
            except Exception:
                pass

    return True, L("已成功刪除紀錄")


def clean_missing(category="all"):
    """Remove entries whose output file no longer exists on disk."""
    if not os.path.exists(HISTORY_PATH):
        return 0
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as stream:
            lines = [l for l in stream if l.strip()]
    except Exception:
        return 0

    kept_lines = []
    removed_count = 0
    for l in lines:
        try:
            r = json.loads(l)
            if category == "image" and not is_image(r):
                kept_lines.append(l)
                continue
            if category == "video" and is_image(r):
                kept_lines.append(l)
                continue
            out = r.get("output")
            if out and os.path.exists(out):
                kept_lines.append(l)
            else:
                removed_count += 1
        except Exception:
            kept_lines.append(l)

    if removed_count > 0:
        try:
            with open(HISTORY_PATH, "w", encoding="utf-8") as stream:
                stream.writelines(kept_lines)
        except Exception:
            pass
    return removed_count


def details_text(row):
    if not row:
        return ""
    keys = [
        ("kind", "分頁模式"),
        ("resolution", "解析度"),
        ("seconds", "時長(秒)"),
        ("seed", "隨機種子"),
        ("mode", "採樣模式"),
        ("scheduler", "採樣排程"),
        ("model", "擴散模型"),
        ("encoder", "文字編碼器"),
        ("lora", "LoRA"),
        ("lora_strength", "LoRA 強度"),
        ("hd", "高清二次採樣"),
        ("output", "成品檔案路徑")
    ]
    lines = [
        f"- **{L(label)}**：`{row[key]}`" if key == "output" else f"- **{L(label)}**：{row[key]}"
        for key, label in keys if row.get(key) not in (None, "", False)
    ]
    return "\n".join(lines)
