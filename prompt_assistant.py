# -*- coding: utf-8 -*-
"""✨ AI 專業提示詞: a local Qwen3-VL (run by ComfyUI's native TextGenerate node) turns a one-line
idea, optionally with a picture, into a prompt in MiniMax H3's official format.

The instructions condense MiniMax's h3-prompt-writing guide (three fields, [Shot N] with cut
times, camera motion + amplitude + speed, (S1) + <d>[Language] …</d> for speech, English quotes
for on-screen text). This module only builds the request and parses the reply; webui.py runs it.
"""
import re

KIND_T2VA = "t2va"        # 🎬 文生: three official fields
KIND_KEYFRAME = "i2va"    # 🖼️ 首尾幀: body that starts from <Picture 1> (and lands on Picture 2)
KIND_STORY = "story"      # 📝 編劇: 共同設定 + 畫面｜運鏡｜聲音 lines, in Traditional Chinese
KIND_IMAGE = "image"      # 🎨 圖片: one English paragraph for Krea2

STYLE_CHOICES = {
    "自動（依想法判斷）": "",
    "寫實電影": "Live-action, cinematic",
    "高級廣告質感": "Live-action, high-end commercial look",
    "3D 動畫": "3D CG animation",
    "2D 動畫": "2D-animated",
    "黏土動畫": "claymation",
    "水彩": "watercolor",
    "復古膠片": "vintage film",
}

_SPEECH_RULE = ("Speech only when the user asks for talking or gives lines. Put the speaker's description and a "
                "stable ID outside the tag and the exact words inside it, always starting with the language tag. "
                "Never translate spoken words: Chinese words stay Chinese, e.g. The young woman with a soft, clear "
                "voice (S1) says: <d>[Chinese] 歡迎光臨。</d> Only people who speak get an ID.")
_CAMERA_RULE = ("Write camera motion as a natural sentence using: push in / pull out, pan left / pan right, truck left / "
                "truck right, tilt up / tilt down, pedestal up / pedestal down, arc shot, tracking shot, static shot, "
                "zoom in / zoom out. Add \"with small amplitude\" or \"with large amplitude\" and \"at slow speed\" or "
                "\"at fast speed\" when they matter, e.g. \"The camera pushes in with small amplitude at slow speed "
                "toward her face.\"")
_SAFETY_RULE = ("Keep everything the user asked for and invent concrete, plausible details for anything vague. "
                "Do not add real people, brands or logos the user did not name. Use calm, precise wording.")

_THREE_FIELDS = f"""The prompt has exactly three fields, written in English, separated by one blank line:
integrated_multimodal_description: [Shot 1] ...

overall_soundscape: ...

non_diegetic_music: ...

Rules:
1. Begin [Shot 1] with the visual style and the opening composition, for example "[Shot 1] Live-action, cinematic, a medium-wide shot frames ...". Styles: Live-action, cinematic / 3D CG / 2D-animated / claymation / watercolor / vintage film. Default to live-action, cinematic.
2. Along the timeline, describe only what can be seen or heard: each subject's age, gender, hair and clothing, the setting, key props, the lighting, then the actions and reactions in order.
3. {_CAMERA_RULE}
4. Use one shot unless the idea needs more. A later shot starts with an increasing cut time inside the video length, e.g. "[Shot 2] At 00:04.000, the camera cuts to a close-up of ...". Never put a time on Shot 1.
5. {_SPEECH_RULE}
6. Text that is visible on screen goes in English double quotes, e.g. a neon sign reading "營業中".
7. overall_soundscape: 1 to 4 English sentences about ambient sound, action sounds and non-verbal human sounds. Do not repeat dialogue.
8. non_diegetic_music: 1 to 3 English sentences about instruments, tempo and volume changes, or N/A when music does not fit.
9. {_SAFETY_RULE}"""

_T2VA_EXAMPLE = """Example output:
integrated_multimodal_description: [Shot 1] Live-action, cinematic, a medium-wide shot frames a baker opening the shutters of a small street bakery before sunrise. The camera pushes in with small amplitude at slow speed as the middle-aged baker with a calm, slightly raspy voice (S1) places a fresh loaf on the wooden counter and says: <d>[English] First batch of the morning.</d> [Shot 2] At 00:05.000, the camera cuts to a close-up of steam rising from the sliced bread while the baker's final words carry over from the previous shot.

overall_soundscape: Wooden shutters scrape open over a quiet street as trays clink softly inside the bakery. The doorbell rings once, followed by light footsteps and the crisp sound of bread being sliced.

non_diegetic_music: A soft acoustic-guitar pattern at a moderate tempo, joined by sparse upright-bass notes and a gentle fade at the end."""

_I2VA_EXAMPLE = """Example output:
integrated_multimodal_description: [Shot 1] Live-action, cinematic, the young woman shown in <Picture 1> remains beside the rain-covered train window, preserving her appearance, clothing, seat position, and the carriage layout. The camera trucks right with small amplitude at slow speed as she lifts her gaze from the folded letter toward the passing city lights. Her reflection moves across the glass while she folds the letter along its existing crease.

overall_soundscape: The train wheels produce a steady metallic rhythm beneath a low ventilation hum. Rain ticks against the window while paper rustles softly in her hands.

non_diegetic_music: Sustained cello notes at a slow tempo with widely spaced piano tones, gradually decreasing in volume."""

_WRITER = ("You are a professional prompt writer for the MiniMax H3 video-and-audio generation model. Rewrite the "
           "user's idea (often short, often in Chinese) into ONE final prompt. Output ONLY the result: no explanation, "
           "no title, no Markdown, no code fences.")

SYSTEM_PROMPTS = {
    KIND_T2VA: f"""{_WRITER}

{_THREE_FIELDS}
10. If a picture is attached and the user gives no idea, only animate what is in the picture: do not add people or objects that are not in it.

{_T2VA_EXAMPLE}""",
    KIND_KEYFRAME: f"""{_WRITER}

This is an image-to-video task. The first attached picture is the exact first frame of the video, called <Picture 1>. If a second picture is attached it is the exact last frame, called Picture 2.
- [Shot 1] MUST name the picture: after the style, write "the <subject> shown in <Picture 1>" (e.g. "the young woman shown in <Picture 1>", "the house shown in <Picture 1>") and say that its appearance, clothing and layout are preserved. Do not re-describe everything visible in the picture.
- Then describe the motion that develops forward from that frame. Keep identity, clothing, colors, key objects and spatial layout consistent with the picture.
- With a last frame: use a single shot and describe the continuous path from the first frame to the last one, ending with the subject settling into the pose and composition established by Picture 2.
- Do NOT write the "How the reference pictures align..." or "For the target video..." line; the panel adds it.
- Do not add sounds or speech the user did not ask for beyond natural ambience.

{_THREE_FIELDS}

{_I2VA_EXAMPLE}""",
    KIND_STORY: f"""You are a storyboard writer for a short video. Turn the user's idea into a shot list, written in Traditional Chinese. Output ONLY the result: no explanation, no title, no Markdown.

Layout:
- Line 1 starts with 設定： and gives the shared setting in one or two sentences: visual style, place, lighting, and the look of every recurring person (age, hair, clothing). It is added in front of every shot, so it must not describe any action.
- Then exactly the requested number of lines, one per shot, each written as 畫面內容｜運鏡｜聲音 using the full-width bar ｜. Do not write a header line. 畫面內容 describes what happens; 運鏡 is one camera move such as 緩慢推近（Push In）、緩慢後拉（Pull Out）、向右橫移（Truck Right）、由下往上仰拍（Tilt Up）、環繞（Arc）、固定鏡頭; 聲音 lists the sounds and music.
- Shots follow each other in time and keep the same people and place. Dialogue, if the user wants it, goes in 畫面內容 as: 她 (S1) 說：<d>[Chinese] 台詞</d>
- {_SAFETY_RULE}""",
    KIND_IMAGE: """You write prompts for the Krea2 image model. Turn the user's idea (often short, often in Chinese) into ONE English paragraph of 60 to 120 words describing a single still image: subject, age, hair and clothing for people, pose, setting, lighting, lens and framing, colors and mood, then material and texture details. Output ONLY the paragraph: no title, no Markdown, no lists. Do not add real people, brands, logos or text the user did not ask for.""",
}


def build_user_message(kind, idea, style="", seconds=None, shots=None, shot_seconds=None, images=0):
    picture_only = ("Bring the attached picture to life as a video. Keep only the people, animals and objects that "
                    "are in the picture; the motion comes from natural movement such as light, wind, water, people "
                    "already in it, and one slow camera move.")
    parts = [(idea or "").strip() or picture_only]
    if kind == KIND_IMAGE:
        if images:
            parts.append("Use the attached picture as the visual reference for subject, setting, colors and lighting.")
    elif kind == KIND_STORY:
        parts.append(f"請寫 {int(shots)} 個鏡頭，每個鏡頭約 {int(shot_seconds)} 秒。")
    else:
        parts.append(f"Video length: {int(seconds)} seconds.")
        if kind == KIND_T2VA and images:
            parts.append("The attached picture shows the look to recreate: use its subject, setting, colors and lighting as the scene.")
    if style:
        parts.append(f"Visual style: {style}." if kind != KIND_STORY else f"畫面風格：{style}。")
    return "\n\n".join(parts)


def chat_text(system, user, images=0):
    """Qwen3-VL chat template with our own system message (the node's default template would put the
    Krea2 captioning system prompt in front); one vision block per attached picture, reasoning off."""
    vision = "<|vision_start|><|image_pad|><|vision_end|>" * images
    return (f"<|im_start|>system\n{system}<|im_end|>\n<|im_start|>user\n{vision}{user}<|im_end|>\n"
            "<|im_start|>assistant\n<think>\n\n</think>\n\n")


def tag_dialogue(text):
    """<d> blocks must open with a language tag; add [Chinese] / [English] when the model left it out."""
    def fix(match):
        words = match.group(1)
        if words.lstrip().startswith("["):
            return match.group(0)
        language = "Chinese" if re.search(r"[\u4e00-\u9fff]", words) else "English"
        return f"<d>[{language}] {words.strip()}</d>"
    return re.sub(r"<d>(.*?)</d>", fix, text, flags=re.S)


def clean_output(text):
    text = (text or "").strip()
    text = re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", text).strip()
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    return tag_dialogue(re.sub(r"^(Output|Prompt|Final prompt)\s*:\s*", "", text, flags=re.I).strip())


def split_story(text):
    """(setting, story lines) for the 編劇 boxes."""
    setting, shots = "", []
    for line in (l.strip() for l in text.splitlines()):
        if not line:
            continue
        if line.startswith(("設定：", "設定:")):
            setting = re.sub(r"^設定[：:]\s*", "", line)
        elif ("｜" in line or "|" in line) and not re.fullmatch(r"[\s｜|]*畫面(內容)?[\s｜|]*運鏡[\s｜|]*聲音[\s｜|]*", line):
            shots.append(re.sub(r"^\s*(\d+[.、)]|鏡頭\s*\d+[:：])\s*", "", line))
    return setting, "\n".join(shots)
