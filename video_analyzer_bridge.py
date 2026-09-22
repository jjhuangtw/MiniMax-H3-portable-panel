"""Bridge module connecting webui.py with knishika62/video-analyzer.

Supports both:
- h3_video2prompt_frames.py (frame sampling via ffmpeg, universal vision LLM compatible)
- h3_video2prompt.py (full mp4 video_url pass-through)
"""
import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ANALYZER_DIR = BASE_DIR / "video-analyzer"
PYTHON_EXE = str(BASE_DIR / "python_embeded" / "python.exe")
if not os.path.isfile(PYTHON_EXE):
    PYTHON_EXE = sys.executable

PROVIDER_PRESETS = {
    "Google Gemini (推薦 · 雲端極速)": {
        "api_base": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model": "gemini-2.5-flash",
    },
    "OpenAI (GPT-4o)": {
        "api_base": "https://api.openai.com/v1",
        "model": "gpt-4o",
    },
    "本地 Ollama (Qwen2.5-VL)": {
        "api_base": "http://localhost:11434/v1",
        "model": "qwen2.5-vl:7b",
    },
    "本地 LM Studio": {
        "api_base": "http://localhost:1234/v1",
        "model": "qwen2.5-vl-7b-instruct",
    },
    "自訂端點 (Custom)": {
        "api_base": "",
        "model": "",
    },
}

MODE_ARG_MAP = {
    "T2VA (MiniMax H3 文生影音)": "T2VA",
    "I2VA (MiniMax H3 首幀生影音)": "I2VA",
    "FL2VA (MiniMax H3 首尾幀影音)": "FL2VA",
    "L2VA (MiniMax H3 末幀生影音)": "L2VA",
    "LTX (LTX-2.5 自然語言段落)": "LTX",
    "僅分析不生提示詞 (Analysis Only)": "ANALYSIS_ONLY",
}


def run_video_analysis(
    video_path: str,
    mode_label: str,
    method_label: str,
    api_base: str,
    model: str,
    api_key: str = "",
    enable_asr: bool = True,
    enable_audio_tags: bool = True,
    progress=None,
):
    """Execute video-analyzer pipeline and return (prompt, first_frame, last_frame, transcript, audio_tags, analysis_json)."""
    if not video_path or not os.path.isfile(video_path):
        raise ValueError("請先上傳要分析的影片檔案！")

    video = Path(video_path)
    stem = video.stem
    mode_arg = MODE_ARG_MAP.get(mode_label, "T2VA")
    is_frames_method = "frames" in method_label or "抽圖" in method_label

    script_name = "h3_video2prompt_frames.py" if is_frames_method else "h3_video2prompt.py"
    script_path = ANALYZER_DIR / script_name

    if not script_path.is_file():
        raise FileNotFoundError(f"找不到分析指令碼：{script_path}")

    out_dir = ANALYZER_DIR / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        PYTHON_EXE,
        str(script_path),
        str(video),
        "--out", str(out_dir),
    ]

    if mode_arg == "ANALYSIS_ONLY":
        cmd.append("--analysis-only")
    else:
        cmd.extend(["--mode", mode_arg])

    if api_base:
        cmd.extend(["--api-base", api_base.strip()])
    if model:
        cmd.extend(["--model", model.strip()])
    if api_key:
        cmd.extend(["--api-key", api_key.strip()])

    if not enable_asr:
        cmd.append("--no-asr")
    if not enable_audio_tags:
        cmd.append("--no-audio-tags")

    # Set up environment with tools in PATH
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    scripts_dir = str(Path(PYTHON_EXE).parent / "Scripts")
    if scripts_dir not in env.get("PATH", ""):
        env["PATH"] = scripts_dir + os.pathsep + env.get("PATH", "")

    if progress:
        progress(0.1, desc="正在啟動 Video Analyzer 進行音影解析與特徵探測...")

    # Execute subprocess with streaming logs
    process = subprocess.Popen(
        cmd,
        cwd=str(ANALYZER_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )

    full_output = []
    for line in process.stdout:
        line_clean = line.strip()
        full_output.append(line_clean)
        if progress and line_clean:
            if "ASR" in line_clean:
                progress(0.3, desc=f"Video Analyzer: {line_clean}")
            elif "音声タグ" in line_clean or "Audio tag" in line_clean or "PANNs" in line_clean:
                progress(0.5, desc=f"Video Analyzer: {line_clean}")
            elif "LLM" in line_clean:
                progress(0.7, desc=f"Video Analyzer: {line_clean}")
            elif "プロンプト" in line_clean or "Prompt" in line_clean or "完了" in line_clean:
                progress(0.9, desc=f"Video Analyzer: {line_clean}")

    retcode = process.wait()
    if retcode != 0:
        err_snippet = "\n".join(full_output[-25:])
        raise RuntimeError(f"影片分析執行失敗 (Exit Code {retcode})：\n{err_snippet}")

    if progress:
        progress(0.95, desc="正在整理分析成果與關鍵幀...")

    video_out = out_dir / stem
    prompt_path = video_out / "prompt.txt"
    json_path = video_out / "analysis.json"
    first_path = video_out / "keyframes" / "first.jpg"
    last_path = video_out / "keyframes" / "last.jpg"
    transcript_path = video_out / "transcript.txt"
    tags_path = video_out / "audio_tags.txt"

    prompt_text = prompt_path.read_text(encoding="utf-8") if prompt_path.is_file() else ""
    json_text = json_path.read_text(encoding="utf-8") if json_path.is_file() else ""
    transcript_text = transcript_path.read_text(encoding="utf-8") if transcript_path.is_file() else "（無偵測到語音或已停用 ASR）"
    tags_text = tags_path.read_text(encoding="utf-8") if tags_path.is_file() else "（無偵測到聲音標籤或已停用音訊辨識）"

    first_frame = str(first_path) if first_path.is_file() else None
    last_frame = str(last_path) if last_path.is_file() else None

    # If in analysis-only mode, synthesize a brief summary for the prompt box
    if not prompt_text and json_text:
        try:
            parsed = json.loads(json_text)
            shots_num = len(parsed.get("shots", []))
            style = parsed.get("style", "live-action")
            prompt_text = f"[Analysis Only 模式]\n風格：{style}\n鏡頭總數：{shots_num} 鏡\n聲音：{parsed.get('sounds', 'N/A')}"
        except Exception:
            prompt_text = "分析完成（未指定生成提示詞模式）。請查看下方的 Analysis JSON。"

    if progress:
        progress(1.0, desc="影片分析與提示詞反推完成！")

    return (
        prompt_text,
        first_frame,
        last_frame,
        transcript_text,
        tags_text,
        json_text,
    )
