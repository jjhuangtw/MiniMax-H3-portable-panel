"""Append-only log of finished generations, so prompts and settings can be reused later."""
import json
import os
import time

HISTORY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generation_history.jsonl")
COLUMNS = ["時間", "分頁", "解析度", "秒數", "種子", "模型", "提示詞"]
MAX_ROWS = 300


def record(kind, prompt, output, **details):
    """One JSON line per generation; a corrupt or unwritable log must never fail a generation."""
    entry = {"time": time.strftime("%m-%d %H:%M"), "kind": kind, "prompt": prompt or "",
             "output": output if isinstance(output, str) else (output[0] if output else ""),
             **{k: v for k, v in details.items() if v is not None}}
    try:
        with open(HISTORY_PATH, "a", encoding="utf-8") as stream:
            stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as error:
        print(f"[History] 無法寫入紀錄: {error}")
    return entry


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
