"""Structured prompt forms that follow MiniMax's official H3 prompt-writing guide.

Source: https://github.com/MiniMax-AI/MiniMax-H3/tree/main/.claude/skills/h3-prompt-writing
"""
import os
import re

import gradio as gr
from zhconv import convert

DIALOGUE_LANGUAGES = ["Chinese", "English", "Japanese", "Korean", "Cantonese"]
SPEAKER_IDS = ["S1", "S2", "S3", "S4", "S1,S2"]
CAMERA_MOTIONS = {
    "靜止 Static Shot": "The camera holds a static shot",
    "推近 Push In": "The camera pushes in",
    "拉遠 Pull Out": "The camera pulls out",
    "變焦推 Zoom In": "The camera zooms in",
    "變焦拉 Zoom Out": "The camera zooms out",
    "左搖 Pan Left": "The camera pans left",
    "右搖 Pan Right": "The camera pans right",
    "左移 Truck Left": "The camera trucks left",
    "右移 Truck Right": "The camera trucks right",
    "上仰 Tilt Up": "The camera tilts up",
    "下俯 Tilt Down": "The camera tilts down",
    "升 Pedestal Up": "The camera pedestals up",
    "降 Pedestal Down": "The camera pedestals down",
    "環繞 Arc Shot": "The camera arcs around the subject",
    "跟拍 Tracking Shot": "The camera tracks the moving subject",
    "輕晃 Shake Slightly": "The camera shakes slightly",
    "主觀 POV": "The shot is a POV from the subject",
}
AMPLITUDES = {"一般": "", "小幅度": " with small amplitude", "大幅度": " with large amplitude"}
SPEEDS = {"一般": "", "慢速": " at slow speed", "快速": " at fast speed"}

VISUAL_MARKERS = ["fully_preserved", "partially_preserved", "attribute_transfer", "weak_reference"]
AUDIO_MARKERS = ["fully_copy", "partially_copy", "reference", "weak_reference"]
TASK_TYPES = ["keyframe completion", "reference generation", "video editing", "video continuation", "audio reuse", "audio reference"]
AUDIO_MODE_REFERENCE = "只借音色／節奏（reference：說新的話）"
AUDIO_MODE_COPY = "整條照用並對嘴（fully_copy：成片換回原音）"
REF_COLUMNS =["標籤", "定義（英文：是什麼、來自哪個素材）", "出現位置", "保留方式", "保留說明（英文）"]

I2VA_INSTRUCTION = "For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced."
KEYFRAME_PREFIXES = ("For the target video, at 0.00 seconds", "How the reference pictures align")


def dialogue_text(speaker, speaker_id, language, line, to_simplified):
    line = (line or "").strip()
    if not line:
        raise gr.Error("請先輸入台詞。")
    if to_simplified and language in ("Chinese", "Cantonese"):
        # Traditional characters more often mismatch pronunciation and lip shapes on H3.
        line = convert(line, "zh-cn")
    speaker = (speaker or "The speaker").strip()
    return f"{speaker} ({speaker_id}) says: <d>[{language}] {line}</d>"


def append_sentence(text, sentence):
    text = (text or "").rstrip()
    return f"{text} {sentence}".strip() if text else sentence


def camera_sentence(motion, amplitude, speed, target):
    sentence = CAMERA_MOTIONS[motion] + AMPLITUDES[amplitude] + SPEEDS[speed]
    target = (target or "").strip()
    return sentence + (f" toward {target}." if target else ".")


def last_shot_number(prompt):
    shots = [int(n) for n in re.findall(r"\[Shot (\d+)\]", prompt or "")]
    return max(shots) if shots else 1


def keyframe_instruction(prompt, has_first, has_last, frame_count):
    """Official first-line alignment sentence for I2VA / FL2VA / L2VA; empty for T2VA."""
    seconds = f"{frame_count / 24:.2f}"
    shot = last_shot_number(prompt)
    if has_first and has_last:
        return (f"How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the "
                f"0.00-second mark of the target video; Picture 2 (from Shot {shot}) aligns with the {seconds}-second mark of the target video.")
    if has_first:
        return I2VA_INSTRUCTION
    if has_last:
        return (f"How the reference pictures align with the target video — <Picture 1> (from [Shot {shot}]) aligns with the "
                f"{seconds}-second mark of the target video.")
    return ""


def with_keyframe_instruction(prompt, has_first, has_last, frame_count):
    if prompt.lstrip().startswith(KEYFRAME_PREFIXES):
        return prompt
    instruction = keyframe_instruction(prompt, has_first, has_last, frame_count)
    return f"{instruction}\n\n{prompt.strip()}" if instruction else prompt


def compose_base_prompt(description, soundscape, music):
    description = (description or "").strip()
    if not description:
        raise gr.Error("請填寫「畫面與動作」。")
    if not description.startswith("[Shot"):
        description = "[Shot 1] " + description
    return (f"integrated_multimodal_description: {description}\n\n"
            f"overall_soundscape: {(soundscape or '').strip() or 'N/A'}\n\n"
            f"non_diegetic_music: {(music or '').strip() or 'N/A'}")


def reference_labels(image_paths, video_items, audio_paths):
    """Label order used by the core Ref2VA node: pictures, then each video's soundtrack before its video, then audio.

    video_items: [(path, soundtrack_enabled)]. Returns [(label, kind, source_name)].
    """
    labels = [(f"<Picture {i}>", "picture", os.path.basename(p)) for i, p in enumerate(image_paths, 1)]
    audio_index = 0
    for video_index, (path, soundtrack) in enumerate(video_items, 1):
        name = os.path.basename(path)
        if soundtrack:
            audio_index += 1
            labels.append((f"<Audio {audio_index}>", "video_audio", name))
        labels.append((f"<Video {video_index}>", "video", name))
    for path in audio_paths:
        audio_index += 1
        labels.append((f"<Audio {audio_index}>", "audio", os.path.basename(path)))
    return labels


def label_table(labels):
    if not labels:
        return "尚未上傳任何參考素材（沒有素材時等同文生影音）。"
    kinds = {"picture": "參考圖", "video": "參考影片（畫面）", "video_audio": "參考影片的原音軌", "audio": "獨立音檔"}
    rows = "\n".join(f"| `{label}` | {kinds[kind]} | {name} |" for label, kind, name in labels)
    return "**提示詞標籤對照**（依上傳順序編號）\n\n| 標籤 | 類型 | 檔案 |\n|---|---|---|\n" + rows


AUTO_REF_MODES = [
    "自動偵測（依上傳素材最佳化）",
    "🎭 動作/外貌轉移 (換人)",
    "👗 服裝/特徵替換 (換裝)",
    "🗣️ 口型同步對嘴",
    "🎬 畫面自然延伸"
]


def generate_auto_ref_prompt(labels, mode="自動偵測（依上傳素材最佳化）"):
    if not labels:
        return ""

    pictures = [l for l, k, n in labels if k == "picture"]
    videos = [l for l, k, n in labels if k == "video"]
    audios = [l for l, k, n in labels if k in ("audio", "video_audio")]

    audio_ref = f"Preserved from {audios[0]}." if audios else "Ambient room tone consistent with the scene."

    # 1. 動作 / 外貌轉移 (換人)
    if mode == "🎭 動作/外貌轉移 (換人)" or (mode.startswith("自動偵測") and videos and pictures):
        pic = pictures[0] if pictures else "<Picture 1>"
        vid = videos[0] if videos else "<Video 1>"
        extra_pics = f" Additional character features refer to {', '.join(pictures[1:])}." if len(pictures) > 1 else ""
        return (
            f"[Shot 1] The subject in {vid} performs the exact same actions, body motion, and camera movement, "
            f"but their appearance, facial identity, hairstyle, and clothing are transferred from {pic}.{extra_pics} "
            f"Keep the original background, environment, lighting, and camera composition from {vid}.\n\n"
            f"overall_soundscape: {audio_ref}\n\n"
            f"non_diegetic_music: N/A"
        )

    # 2. 服裝 / 特徵替換 (換裝)
    if mode == "👗 服裝/特徵替換 (換裝)" or (mode.startswith("自動偵測") and len(pictures) >= 2 and not videos):
        return (
            f"[Shot 1] Cinematic, photorealistic video. The character shown in {pictures[0]} is the main subject, "
            f"wearing the outfit and clothing style from {pictures[1]}. "
            f"The character moves naturally with smooth, subtle body motions and expressive eyes in a harmonious setting.\n\n"
            f"overall_soundscape: {audio_ref}\n\n"
            f"non_diegetic_music: N/A"
        )

    # 3. 口型同步對嘴
    if mode == "🗣️ 口型同步對嘴" or (mode.startswith("自動偵測") and pictures and any(k == "audio" for l, k, n in labels) and not videos):
        audio_name = next((l for l, k, n in labels if k == "audio"), "<Audio 1>")
        pic = pictures[0] if pictures else "<Picture 1>"
        return (
            f"[Shot 1] The person shown in {pic} looks toward the camera and speaks naturally, "
            f"with the lips, jaw, and facial expression moving in accurate sync to {audio_name}. "
            f"Keep the same face, hairstyle, clothing, background, and lighting as {pic}, "
            f"with only small natural head movement and blinking. The camera holds a static shot.\n\n"
            f"overall_soundscape: Speech synchronized with {audio_name}.\n\n"
            f"non_diegetic_music: N/A"
        )

    # 4. 畫面延伸
    if mode == "🎬 畫面自然延伸" or (mode.startswith("自動偵測") and videos and not pictures):
        vid = videos[0]
        return (
            f"[Shot 1] Continuing the movement and camera path from {vid}, the scene develops naturally "
            f"while strictly preserving the character identity, lighting, and environmental details from {vid}.\n\n"
            f"overall_soundscape: {audio_ref}\n\n"
            f"non_diegetic_music: N/A"
        )

    # 5. 單張圖片 (圖生影音) 或通用備用
    pic = pictures[0] if pictures else "<Picture 1>"
    return (
        f"[Shot 1] Starting from the exact composition in {pic}, the scene comes to life with fluid, natural motion. "
        f"The subject in {pic} moves with subtle lifelike actions and realistic lighting.\n\n"
        f"overall_soundscape: {audio_ref}\n\n"
        f"non_diegetic_music: N/A"
    )



def default_reference_rows(labels, audio_mode):
    rows = []
    subject = 0
    copy_pending = audio_mode == AUDIO_MODE_COPY
    for label, kind, name in labels:
        if kind == "picture":
            subject += 1
            rows.append([f"<Subject {subject}>", f"is the main subject in {label}, with ...", "appears in [Shot 1]", "fully_preserved", "..."])
        elif kind == "video":
            rows.append([label, "is the source video for the target video edit.", "cut and pacing structure", "fully_preserved", "..."])
        elif kind == "video_audio":
            video = next(l for l, k, n in labels if k == "video" and n == name)
            rows.append([label, f"is the synchronized audio track of {video} and is reused in the target video.", "", "fully_copy",
                         f"{label} is reused 1:1 as the target video's complete final audio track."])
        else:
            marker = "fully_copy" if copy_pending and kind == "audio" else "reference"
            copy_pending = copy_pending and marker != "fully_copy"
            meaning = ("is the complete external soundtrack copied 1:1 as the target video's final audio track." if marker == "fully_copy"
                       else "is the voice-timbre reference for <Subject 1> (S1).")
            note = (f"{label} is reused 1:1 as the target video's complete final audio track." if marker == "fully_copy"
                    else f"the speaker follows {label}'s timbre and delivery without copying the original signal.")
            rows.append([label, meaning, "", marker, note])
    return rows


def compose_ref_prompt(rows, task_types, summary, style, description, soundscape, music):
    if hasattr(rows, "values"):
        rows = rows.values.tolist()
    rows = [[str(c or "").strip() for c in row] for row in (rows or []) if row and str(row[0] or "").strip()]
    if not rows:
        raise gr.Error("請先在表格填入參考物（可按「依上傳素材產生表格」）。")
    if not (description or "").strip():
        raise gr.Error("請填寫「逐鏡描述」。")
    definitions = "\n".join(f"{label} {definition}" for label, definition, *_ in rows)
    retention = []
    for label, _, where, marker, note in rows:
        allowed = AUDIO_MARKERS if label.startswith("<Audio") else VISUAL_MARKERS
        if marker not in allowed:
            raise gr.Error(f"{label} 的保留方式必須是：{' / '.join(allowed)}")
        position = "" if label.startswith("<Audio") or not where else f" ({where})"
        retention.append(f"{label}{position}: {marker} - {note}")
    prefix = " + ".join(task_types) if task_types else "reference generation"
    body = (description or "").strip()
    if not body.startswith("[Shot"):
        body = "[Shot 1] " + body
    style = (style or "").strip()
    return (f"subject_definitions:\n{definitions}\n\n"
            f"summary:\n[{prefix}] {(summary or '').strip()}\n\n"
            f"retention_analysis:\n" + "\n".join(retention) + "\n\n"
            f"detailed_description:\n{(style + chr(10)) if style else ''}{body}\n\n"
            f"overall_soundscape:\n{(soundscape or '').strip() or 'N/A'}\n\n"
            f"non_diegetic_music:\n{(music or '').strip() or 'N/A'}")


def _dialogue_and_camera_tools(target_box):
    with gr.Row():
        speaker = gr.Textbox(label="說話者描述（英文）", placeholder="The young woman with a clear, bright voice", scale=4)
        speaker_id = gr.Dropdown(label="說話者 ID", choices=SPEAKER_IDS, value="S1", scale=1)
        language = gr.Dropdown(label="語言", choices=DIALOGUE_LANGUAGES, value="Chinese", scale=1)
    with gr.Row():
        line = gr.Textbox(label="台詞（照原文，不翻譯）", scale=5)
        simplified = gr.Checkbox(label="中文轉簡體", value=True, scale=1,
                                 info="繁體台詞較容易發音或嘴型對不上")
    insert_line = gr.Button("插入台詞 <d>…</d>")
    with gr.Row():
        motion = gr.Dropdown(label="運鏡", choices=list(CAMERA_MOTIONS), value="推近 Push In")
        amplitude = gr.Dropdown(label="幅度", choices=list(AMPLITUDES), value="小幅度")
        speed = gr.Dropdown(label="速度", choices=list(SPEEDS), value="慢速")
        target = gr.Textbox(label="朝向（英文，選填）", placeholder="her face")
    insert_camera = gr.Button("插入運鏡句")
    insert_line.click(lambda text, s, sid, lang, ln, simp: append_sentence(text, dialogue_text(s, sid, lang, ln, simp)),
                      [target_box, speaker, speaker_id, language, line, simplified], target_box, queue=False)
    insert_camera.click(lambda text, m, a, sp, t: append_sentence(text, camera_sentence(m, a, sp, t)),
                        [target_box, motion, amplitude, speed, target], target_box, queue=False)


def add_base_prompt_builder(prompt_box):
    with gr.Accordion("🧱 結構化提示詞（官方三段格式）", open=False):
        gr.Markdown("依 MiniMax 官方寫法：畫面、環境音、配樂分開寫，模型才分得清聲音屬於哪一層。欄位請用英文；台詞保留原文。"
                    "有首幀／尾幀時，生成時會自動在第一行加上官方的對齊宣告。多鏡頭時，第 2 鏡起寫 `[Shot 2] At 00:03.500, the camera cuts to ...`。")
        description = gr.Textbox(label="畫面與動作 integrated_multimodal_description", lines=5,
                                 placeholder="[Shot 1] Live-action, cinematic, a medium shot frames ...")
        _dialogue_and_camera_tools(description)
        soundscape = gr.Textbox(label="環境音 overall_soundscape", lines=2, placeholder="Rain taps against the window while ...")
        music = gr.Textbox(label="配樂 non_diegetic_music（沒有就留 N/A）", value="N/A", lines=2)
        compose = gr.Button("組合並填入提示詞", variant="secondary")
        compose.click(compose_base_prompt, [description, soundscape, music], prompt_box, queue=False)


def add_ref_prompt_builder(prompt_box, labels_state, audio_mode_box):
    with gr.Accordion("🧱 結構化提示詞（官方 Ref 六段格式）", open=False):
        gr.Markdown(
            "Ref 的關鍵是講清楚「哪個參考物負責哪件事」。同一張圖可以只借臉、只借衣服或只借場景；**沒寫到的東西，模型會保留原狀。**\n\n"
            "- 畫面類保留方式：`fully_preserved` 完全保留／`partially_preserved` 部分保留／`attribute_transfer` 只把特徵轉移到另一個對象（例如換裝）／`weak_reference` 只取風格氛圍\n"
            "- 音訊類：`fully_copy` 整條當成片音軌（對嘴）／`partially_copy` 部分沿用／`reference` 只借音色節奏（說新的話）／`weak_reference`\n"
            "- `<Subject N>` 是從素材抽出來的人、場景、服裝；只有當圖片本身就是某一格畫面（例如首幀）時，才單獨定義 `<Picture N>`。"
        )
        fill = gr.Button("依上傳素材產生表格")
        table = gr.Dataframe(headers=REF_COLUMNS, datatype=["str"] * 5, column_count=(5, "fixed"), interactive=True, wrap=True)
        task_types = gr.CheckboxGroup(label="任務類型（summary 開頭）", choices=TASK_TYPES, value=["reference generation"])
        summary = gr.Textbox(label="摘要 summary（英文一小段）", lines=2)
        style = gr.Textbox(label="風格開場句（英文，放在 [Shot 1] 之前）", placeholder="The target video is live-action and photorealistic, with soft daylight.")
        description = gr.Textbox(label="逐鏡描述 detailed_description", lines=6,
                                 placeholder="[Shot 1] The shot begins from <Picture 1>: ... <Subject 1> ...")
        _dialogue_and_camera_tools(description)
        soundscape = gr.Textbox(label="環境音 overall_soundscape", lines=2)
        music = gr.Textbox(label="配樂 non_diegetic_music", value="N/A", lines=2)
        compose = gr.Button("組合並填入提示詞", variant="secondary")
        fill.click(default_reference_rows, [labels_state, audio_mode_box], table, queue=False)
        compose.click(compose_ref_prompt, [table, task_types, summary, style, description, soundscape, music], prompt_box, queue=False)
