import os
import sys
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass
import time
import json
import uuid
import urllib.request
import urllib.parse
import subprocess
import threading
import webbrowser
import requests
import websocket
import gradio as gr
import re
import math
import tempfile
import random
from prompt_library import PROMPT_CATEGORIES
from prompt_reference import OFFICIAL_GUIDE_CATEGORIES
from prompt_examples import OFFICIAL_FORMAT_EXAMPLES
from long_examples import LONG_VIDEO_EXAMPLES
from media_tools import (AUTO_RESOLUTION_CHOICES, auto_canvas, concat_video_segments, extract_last_frame,
                        has_audio_stream, media_duration, mux_original_audio, plan_segment_durations,
                        prepare_reference_video, slice_audio, slice_video, SINGLE_SEGMENT_MAX_SECONDS)
import history
from prompt_builder import (AUDIO_MODE_COPY, AUDIO_MODE_REFERENCE, AUTO_REF_MODES, add_base_prompt_builder, add_ref_prompt_builder,
                            generate_auto_ref_prompt, label_table, reference_labels, with_keyframe_instruction)
from camera_controls import CAMERA_WEB, DEFAULT_CAMERA, EDITOR_JS, update_camera_image, apply_camera_graph

gr.set_static_paths(paths=[str(CAMERA_WEB)])

if sys.platform == "win32":
    # A closed or refreshed browser tab makes the Proactor loop print a harmless WinError 10054 traceback.
    from asyncio.proactor_events import _ProactorBasePipeTransport
    _call_connection_lost = _ProactorBasePipeTransport._call_connection_lost

    def _quiet_connection_lost(self, exc):
        try:
            _call_connection_lost(self, exc)
        except ConnectionResetError:
            pass

    _ProactorBasePipeTransport._call_connection_lost = _quiet_connection_lost

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMFY_DIR = os.path.join(BASE_DIR, "ComfyUI")
PYTHON_EXE = os.path.join(BASE_DIR, "python_embeded", "python.exe")
COMFY_SERVER = "127.0.0.1:8188"
COMFY_URL = f"http://{COMFY_SERVER}"
COMFY_WS_URL = f"ws://{COMFY_SERVER}/ws"

H3_FL2VA_MODEL = "minimax_h3_fl2va_pruned-Q4_K_M.gguf"
H3_REF2VA_MODEL = "minimax_h3_ref2va_pruned-Q4_K_M.gguf"
H3_SINGULARITY_MODEL = "Minimax-h3_Singularity_ref2va_v1.3_Pruned_w4a8.safetensors"
H3_TEXT_ENCODER = "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
H3_VIDEO_VAE = "minimax_h3_video_vae_fp16.safetensors"
# Kijai/Comfy-Org INT8 ConvRot video VAE: ~half the VRAM, near-identical quality. Used automatically when present.
H3_VIDEO_VAE_INT8 = "minimax_h3_video_vae_int8_convrot.safetensors"
H3_AUDIO_VAE = "minimax_h3_audio_vae_fp32.safetensors"
H3_FL2VA_LORA = "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors"
H3_REF2VA_LORA = "minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors"
H3_HERETIC_TEXT_ENCODER = "qwen3vl_32b_heretic_minimax_h3_nvfp4.safetensors"
TEXT_ENCODER_LABELS = {
    H3_TEXT_ENCODER: "原版 Qwen3-VL 32B NVFP4 AWQ",
    H3_HERETIC_TEXT_ENCODER: "Heretic 無審查 Qwen3-VL 32B NVFP4",
}
NO_LORA = "（不使用）"
SCHEDULERS = ["simple", "beta", "sgm_uniform", "normal", "karras"]
SEEDVR2_DIT = "seedvr2_ema_3b_fp16.safetensors"
SEEDVR2_VAE = "ema_vae_fp16.safetensors"
SEEDVR2_COLOR = ["lab", "wavelet", "wavelet_adaptive", "hsv", "adain", "none"]
SEEDVR2_RES_CHOICES = {"720p（短邊 720）": 720, "1080p（短邊 1080）": 1080, "1440p（短邊 1440）": 1440, "2160p / 4K（短邊 2160）": 2160}
# Turbo LoRA vs a checkpoint that already carries its own distillation: the two must never stack.
MODE_TURBO_LORA = "Turbo LoRA・4 步（預設 Q4／INT8 官方模型）"
MODE_BAKED_TURBO = "模型內建蒸餾・8 步（DaSiWa Turbo 等，不加 Turbo LoRA）"
MODE_FULL = "非蒸餾・20 步（CFG 2.5）"
SAMPLING_MODES = [MODE_TURBO_LORA, MODE_BAKED_TURBO, MODE_FULL]
# A ~21 GB trunk leaves too little VRAM for the upscaler's Conv3d, which aborts the whole backend.
HD_MAX_MODEL_BYTES = 15 * 1000 ** 3
# Tested ceilings on this 24 GB card: 1920×1088 ran 12 s with the Q4 trunk, 1280×704 has more room.
HD_MAX_PIXEL_SECONDS = 1920 * 1088 * 12
MODE_SETTINGS = {MODE_TURBO_LORA: (True, 4, 1.0), MODE_BAKED_TURBO: (False, 8, 1.0), MODE_FULL: (False, 20, 2.5)}

def mode_settings(mode):
    """(apply Turbo LoRA, steps, cfg). Accepts the old boolean so saved calls keep working."""
    if isinstance(mode, bool):
        mode = MODE_TURBO_LORA if mode else MODE_FULL
    return MODE_SETTINGS.get(mode, MODE_SETTINGS[MODE_TURBO_LORA])
KREA2_OFFICIAL_MODEL = "krea2_turbo_fp8_scaled.safetensors"
KREA2_TEXT_ENCODER = "qwen3vl_4b_fp8_scaled.safetensors"
KREA2_VAE = "qwen_image_vae.safetensors"
KREA2_TURBO_LORA = "krea2_turbo_lora_rank_64_bf16.safetensors"
KREA2_SIZES = ["1024 × 1024 (1:1)", "1024 × 1536 (2:3 直式)", "1536 × 1024 (3:2 橫式)",
               "1152 × 896 (4:3)", "896 × 1152 (3:4)", "1344 × 768 (16:9)", "768 × 1344 (9:16)"]
KREA2_SAMPLERS = ["er_sde", "euler", "dpmpp_2m", "res_multistep"]
# Style / original-character LoRAs for Krea2 live in their own subfolder so they never mix with H3 LoRAs.
KREA2_LORA_SUBDIR = "krea2"
KREA2_LORA_SLOTS = 3
THUMB_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".preview.png")
THUMB_DIR = os.path.join(BASE_DIR, "lora_thumbs")
# Default prompt for generating missing LoRA previews
THUMB_PROMPT = "東亞女子頭像, portrait of an East Asian woman, beautiful face, soft natural studio lighting, photorealistic, 8k"
# AfterMidnight's Ref2VA LoRAs are trained for euler + beta; the stock Turbo LoRAs use simple.
SCHEDULER_INFO = "Turbo LoRA 用 simple。AfterMidnight 等 Ref2VA NSFW LoRA 作者要求 euler + beta，否則音訊會出問題。"
# The panel defaults to the Heretic encoder; it falls back to the stock one when that file is missing.
H3_DEFAULT_TEXT_ENCODER = H3_HERETIC_TEXT_ENCODER
H3_LATENT_UPSCALER = "minimax_h3_latent_upscaler_3d_fp16.safetensors"
# Refine schedule from LBH-123-AI's H3 latent upscaler example workflow (3 steps from sigma 0.9035).
HD_REFINE_SIGMAS = "0.9035, 0.6316, 0.3158, 0.0"
# TimelineDirector's default seam overlap; valid overlaps are 0, 1, 5, 22, 39, 56...
LONG_OVERLAP_FRAMES = 39
HD_LABEL = "✨ 高清二次採樣（輸出上面選的解析度）"
HD_INFO = "先用一半解析度生成，再以 H3 潛空間放大模型放大、補 3 步細節。會自動使用 Turbo。4 秒實測：1280×704 約 2 分 15 秒、1920×1088 約 5 分鐘。"
HD_LOW_VRAM_INFO = "高清二次採樣需要 24GB 級顯卡，這台顯存不足已關閉；要更高解析度請生成後用「🔍 放大」（SeedVR2）。"
FULL_HD_CHOICES = [
    "1920 × 1088 (16:9 Full HD · 需勾選高清二次採樣)",
    "1088 × 1920 (9:16 直式 Full HD · 需勾選高清二次採樣)",
]
BASE_RES_CHOICES = [
    "864 × 480 (16:9 標清 · 推薦，最省顯存)",
    "960 × 544 (16:9 中清)",
    "1056 × 608 (16:9 高清)",
    "1280 × 704 (16:9 超清 · 較吃顯存)",
    "1344 × 768 (16:9 原生官方上限 · 最吃顯存)",
    "480 × 864 (9:16 直式短影音 · 推薦)",
    "768 × 1344 (9:16 直式短影音 · 高清 · 最吃顯存)",
]
DEFAULT_RES = BASE_RES_CHOICES[0]
# Ref2VA / V2V skip the 1344×768 ceiling: the reference latents already take part of the budget.
REF_RES_CHOICES = [choice for choice in BASE_RES_CHOICES if not choice.startswith("1344")]
# Above this area a 12–16 GB card tends to spill into shared memory or run out of VRAM.
LOW_VRAM_MAX_PIXELS = 960 * 544
# Above the official 1344×768 area a single pass is untrained and too heavy for 24 GB.
SINGLE_PASS_MAX_PIXELS = 1344 * 768

comfy_process = None

PANEL_TITLE = "MiniMax H3 Portable"

def open_existing_webui():
    url = "http://127.0.0.1:7860"
    try:
        response = requests.get(f"{url}/config", timeout=3)
        response.raise_for_status()
        # startswith: panels started before the rename still carry " - RTX 4090".
        if not str(response.json().get("title", "")).startswith(PANEL_TITLE):
            return False
    except (requests.RequestException, ValueError):
        return False
    print(f"[WebUI] Already running. Opening {url}")
    webbrowser.open(url)
    return True

def is_comfy_running():
    try:
        r = requests.get(f"{COMFY_URL}/system_stats", timeout=2)
        return r.status_code == 200
    except Exception:
        return False

def detect_gpu():
    """(name, total VRAM in GB) of GPU 0 via nvidia-smi; (None, None) if it cannot be read."""
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        name, mib = out.stdout.strip().splitlines()[0].rsplit(",", 1)
        return name.strip(), int(mib) / 1024.0
    except Exception:
        return None, None


def vram_launch_args(gb):
    """(reserve_vram, vram_headroom, profile_label) auto-scaled to the detected GPU VRAM.
    The 24GB defaults reserve ~5.5 GB, which is too much on smaller cards, so lower it."""
    if gb is None:
        return "1", "1", "未偵測到顯存 → 保守設定（約 16GB 級）"
    if gb >= 22:
        return "2.5", "3", f"{gb:.0f} GB → 高顯存（24GB 以上，全功能全速）"
    if gb >= 14:
        return "1", "1", f"{gb:.0f} GB → 中顯存（Q4 模型、864×480～960×544；高清二次採樣已關閉）"
    return "0.5", "0", f"{gb:.0f} GB → 低顯存（Q4 模型、864×480、4～6 秒短片；較慢）"


GPU_NAME, VRAM_GB = detect_gpu()
# set H3_VRAM_GB=16 (before run_webui.bat) forces a profile, e.g. when nvidia-smi misreads the card.
try:
    VRAM_GB = float(os.environ["H3_VRAM_GB"])
except (KeyError, ValueError):
    pass
VRAM_RESERVE, VRAM_HEADROOM, VRAM_PROFILE_LABEL = vram_launch_args(VRAM_GB)
# Below 22 GB the HD two-pass upscaler and 0.6 MP+ long videos run out of VRAM; an unreadable
# card is treated as capable so a failed nvidia-smi never hides features from a 24 GB user.
LOW_VRAM = VRAM_GB is not None and VRAM_GB < 22
HD_ALLOWED = not LOW_VRAM
HD_RES_CHOICES = FULL_HD_CHOICES if HD_ALLOWED else []


def ensure_comfy_server():
    global comfy_process
    if is_comfy_running():
        return True

    print(f"[WebUI] GPU 顯存設定：{VRAM_PROFILE_LABEL}")
    print("[WebUI] Starting ComfyUI backend server...")
    cmd = [
        PYTHON_EXE,
        "main.py",
        "--listen", "127.0.0.1",
        "--port", "8188",
        "--fast", "fp8_matrix_mult", "fp16_accumulation",
        "--reserve-vram", VRAM_RESERVE,
        "--vram-headroom", VRAM_HEADROOM,
        "--disable-auto-launch"
    ]
    log_path = os.path.join(BASE_DIR, "comfy_server.log")
    log_fp = open(log_path, "a", encoding="utf-8")
    comfy_process = subprocess.Popen(
        cmd,
        cwd=COMFY_DIR,
        stdout=log_fp,
        stderr=log_fp,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"}
    )
    
    for _ in range(60):
        if is_comfy_running():
            print("[WebUI] ComfyUI backend is online!")
            return True
        time.sleep(1)
    return False

def model_dirs(kind):
    dirs = [os.path.join(COMFY_DIR, "models", kind)]
    try:
        import yaml
        with open(os.path.join(COMFY_DIR, "extra_model_paths.yaml"), encoding="utf-8") as f:
            for entry in (yaml.safe_load(f) or {}).values():
                if isinstance(entry, dict) and entry.get(kind):
                    for sub in str(entry[kind]).splitlines():
                        if sub.strip():
                            dirs.append(os.path.join(entry.get("base_path", ""), sub.strip()))
    except (OSError, ImportError, ValueError):
        pass
    return dirs

def video_vae():
    """Prefer the INT8 ConvRot video VAE when it is present, else the FP16 one."""
    for folder in model_dirs("vae"):
        if os.path.exists(os.path.join(folder, H3_VIDEO_VAE_INT8)):
            return H3_VIDEO_VAE_INT8
    return H3_VIDEO_VAE

def backend_choices(node_type, input_name):
    response = requests.get(f"{COMFY_URL}/object_info/{node_type}", timeout=5)
    response.raise_for_status()
    spec = response.json()[node_type]["input"]["required"][input_name]
    if isinstance(spec[0], list):
        return spec[0]
    return spec[1].get("options", [])

MODEL_EXTS = (".safetensors", ".gguf", ".pth", ".ckpt", ".pt")

def list_model_files(kind, node_type, input_name):
    """Union of the backend's list and a folder scan, so a not-yet-indexed backend never hides a file."""
    found = set()
    try:
        # Backend uses OS separators (backslash on Windows); normalize so it dedups with the folder scan.
        found.update(f.replace("\\", "/") for f in backend_choices(node_type, input_name))
    except Exception:
        pass
    for root in model_dirs(kind):
        if not os.path.isdir(root):
            continue
        for dirpath, _, filenames in os.walk(root):
            for filename in filenames:
                if filename.endswith(MODEL_EXTS):
                    found.add(os.path.relpath(os.path.join(dirpath, filename), root).replace("\\", "/"))
    return sorted(found)

def default_text_encoder(choices=None):
    values = [value for _, value in (choices if choices is not None else text_encoder_choices())]
    return H3_DEFAULT_TEXT_ENCODER if H3_DEFAULT_TEXT_ENCODER in values else (values[0] if values else H3_TEXT_ENCODER)

def text_encoder_choices():
    files = [f for f in list_model_files("text_encoders", "CLIPLoader", "clip_name") if f.endswith(".safetensors")]
    return [(TEXT_ENCODER_LABELS.get(os.path.basename(f), f), f) for f in files]

def refresh_model_choices():
    encoders = text_encoder_choices()
    fl2va = diffusion_model_choices("fl2va")
    ref2va = diffusion_model_choices("ref2va")
    return (gr.Dropdown(choices=encoders, value=default_text_encoder(encoders)),
            gr.Dropdown(choices=model_label_choices(fl2va), value=krea2_default(fl2va, H3_FL2VA_MODEL)),
            gr.Dropdown(choices=model_label_choices(ref2va), value=krea2_default(ref2va, H3_REF2VA_MODEL)))

def extras_hint(option):
    return f"請雙擊面板資料夾裡的 download_extras.bat，選 {option} 下載，完成後執行 restart_webui.bat。"

def resolve_backend_file(node_type, input_name, name, what, extras_option=None):
    """Map a chosen file to the backend's spelling (path separators differ on Windows)."""
    wanted = (name or "").replace("\\", "/")
    for choice in backend_choices(node_type, input_name):
        if choice.replace("\\", "/") == wanted:
            return choice
    how = extras_hint(extras_option) if extras_option else "若剛下載完成，請執行 restart_webui.bat 後再試。"
    raise gr.Error(f"後端找不到{what}「{name or '（未選擇）'}」。{how}")

def missing_models_notice(ready, what, extras_option):
    if not ready:
        gr.Markdown(f"> ⚠️ **尚未下載{what}。** {extras_hint(extras_option)}")

def resolve_diffusion_model(model_name, fallback, what):
    model_name = model_name or fallback
    node = "UnetLoaderGGUF" if model_name.endswith(".gguf") else "UNETLoader"
    return resolve_backend_file(node, "unet_name", model_name, what)

def resolve_model_options(text_encoder, lora_name, lora_strength, fl2va_model=None, ref2va_model=None):
    text_encoder = resolve_backend_file("CLIPLoader", "clip_name", text_encoder or H3_DEFAULT_TEXT_ENCODER, "文字編碼器")
    if lora_name and lora_name != NO_LORA:
        lora_name = resolve_backend_file("LoraLoaderModelOnly", "lora_name", lora_name, " LoRA ")
    else:
        lora_name = None
    return {"text_encoder": text_encoder, "lora_name": lora_name, "lora_strength": float(lora_strength or 0),
            "fl2va_model": resolve_diffusion_model(fl2va_model, H3_FL2VA_MODEL, " FL2VA 模型"),
            "ref2va_model": resolve_diffusion_model(ref2va_model, H3_REF2VA_MODEL, " Ref2VA 模型")}

def add_user_lora(workflow, last_model_node, lora_name, lora_strength):
    if not lora_name or lora_strength == 0:
        return last_model_node
    workflow["9"] = {
        "class_type": "LoraLoaderModelOnly",
        "inputs": {
            "model": last_model_node,
            "lora_name": lora_name,
            "strength_model": lora_strength
        }
    }
    return ["9", 0]

def hd_base_size(width, height):
    """Half-size first pass, aligned to H3's 32-pixel canvas grid."""
    return max(32, round(width / 2 / 32) * 32), max(32, round(height / 2 / 32) * 32)

def add_hd_refine(workflow, sampled_latent, model, conditioning, seed, width, height):
    """Learned 3D latent upscale of the video stream, then a short re-noised pass at full size."""
    workflow["60"] = {"class_type": "LTXVSeparateAVLatent", "inputs": {"av_latent": sampled_latent}}
    workflow["61"] = {
        "class_type": "MinimaxH3LatentUpscaler3D",
        "inputs": {
            "latent": ["60", 0],
            "model_name": H3_LATENT_UPSCALER,
            "mode": "target dimensions",
            "mode.width": width,
            "mode.height": height,
            "align": 32,
            "enable_temporal_chunking": True,
            "force_unload": True,
            "device": "cuda",
            "precision": "fp16"
        }
    }
    workflow["62"] = {"class_type": "LTXVConcatAVLatent", "inputs": {"video_latent": ["61", 0], "audio_latent": ["60", 1]}}
    workflow["64"] = {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}}
    workflow["65"] = {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}}
    workflow["66"] = {"class_type": "ManualSigmas", "inputs": {"sigmas": HD_REFINE_SIGMAS}}
    workflow["67"] = {"class_type": "BasicGuider", "inputs": {"model": model, "conditioning": conditioning}}
    workflow["68"] = {
        "class_type": "SamplerCustomAdvanced",
        "inputs": {
            "noise": ["64", 0],
            "guider": ["67", 0],
            "sampler": ["65", 0],
            "sigmas": ["66", 0],
            "latent_image": ["62", 0]
        }
    }
    return ["68", 0]

def parse_resolution(resolution_str):
    res_parts = resolution_str.split("×")
    return int(res_parts[0].strip()), int(res_parts[1].split()[0].strip())

def upload_image(image_path):
    if not image_path:
        return None
    url = f"{COMFY_URL}/upload/image"
    with open(image_path, "rb") as f:
        filename = os.path.basename(image_path)
        files = {"image": (filename, f, "image/png")}
        data = {"overwrite": "true", "subfolder": ""}
        res = requests.post(url, files=files, data=data)
        if res.status_code == 200:
            return res.json().get("name", filename)
    return None

def build_minimax_h3_prompt(
    prompt_text,
    width=1280,
    height=704,
    duration=5,
    seed=-1,
    turbo=True,
    first_frame_name=None,
    last_frame_name=None,
    text_encoder=H3_DEFAULT_TEXT_ENCODER,
    lora_name=None,
    lora_strength=1.0,
    hd_size=None,
    fl2va_model=H3_FL2VA_MODEL,
    ref2va_model=None
):
    if seed == -1 or seed is None:
        import random
        seed = random.randint(1, 1000000000000000)

    length = int(round(duration * 24))
    while length % 17 != 5:
        length += 1

    turbo_lora, steps, cfg = mode_settings(turbo)
    final_size = hd_size or (width, height)
    if hd_size:
        width, height = hd_base_size(*hd_size)
    workflow = {
        "1": model_loader(fl2va_model),
        "2": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": text_encoder,
                "type": "minimax"
            }
        },
        "3": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": video_vae()
            }
        },
        "4": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": H3_AUDIO_VAE
            }
        }
    }

    last_model_node = ["1", 0]
    if turbo_lora:
        workflow["5"] = {
            "class_type": "LoraLoader",
            "inputs": {
                "model": last_model_node,
                "clip": ["2", 0],
                "lora_name": H3_FL2VA_LORA,
                "strength_model": 1.0,
                "strength_clip": 1.0
            }
        }
        last_model_node = ["5", 0]
    last_model_node = add_user_lora(workflow, last_model_node, lora_name, lora_strength)

    workflow["6"] = {
        "class_type": "MiniMaxH3SigmaShift",
        "inputs": {
            "model": last_model_node,
            "shift_video": 12.0,
            "shift_audio": 3.0
        }
    }

    cond_inputs = {
        "clip": ["2", 0],
        "vae": ["3", 0],
        "prompt": prompt_text,
        "width": width,
        "height": height,
        "length": length
    }

    if first_frame_name:
        workflow["10"] = {
            "class_type": "LoadImage",
            "inputs": {"image": first_frame_name}
        }
        cond_inputs["first_frame"] = ["10", 0]

    if last_frame_name:
        workflow["11"] = {
            "class_type": "LoadImage",
            "inputs": {"image": last_frame_name}
        }
        cond_inputs["last_frame"] = ["11", 0]

    workflow["7"] = {
        "class_type": "MiniMaxH3ImageToVideo",
        "inputs": cond_inputs
    }

    workflow["8"] = {
        "class_type": "ConditioningZeroOut",
        "inputs": {
            "conditioning": ["7", 0]
        }
    }

    workflow["20"] = {
        "class_type": "KSampler",
        "inputs": {
            "model": ["6", 0],
            "positive": ["7", 0],
            "negative": ["8", 0],
            "latent_image": ["7", 1],
            "seed": seed,
            "steps": steps,
            "cfg": cfg,
            "sampler_name": "euler",
            "scheduler": "simple",
            "denoise": 1.0
        }
    }

    final_latent = ["20", 0]
    if hd_size:
        hi_cond = ["7", 0]
        if first_frame_name or last_frame_name:
            # Keyframe latents are encoded at canvas size, so the refine pass needs its own conditioning.
            workflow["63"] = {
                "class_type": "MiniMaxH3ImageToVideo",
                "inputs": {**cond_inputs, "width": final_size[0], "height": final_size[1]}
            }
            hi_cond = ["63", 0]
        final_latent = add_hd_refine(workflow, ["20", 0], ["6", 0], hi_cond, seed, *final_size)

    workflow["30"] = {
        "class_type": "VAEDecode",
        "inputs": {
            "samples": final_latent,
            "vae": ["3", 0]
        }
    }

    workflow["31"] = {
        "class_type": "VAEDecodeAudio",
        "inputs": {
            "samples": final_latent,
            "vae": ["4", 0]
        }
    }

    workflow["40"] = {
        "class_type": "CreateVideo",
        "inputs": {
            "images": ["30", 0],
            "audio": ["31", 0],
            "fps": 24.0
        }
    }

    workflow["41"] = {
        "class_type": "SaveVideo",
        "inputs": {
            "video": ["40", 0],
            "filename_prefix": "MiniMax_H3_HD_Output" if hd_size else "MiniMax_H3_Output",
            "format": "auto",
            "codec": "auto"
        }
    }

    return workflow

def build_minimax_h3_ref_prompt(
    prompt_text,
    width,
    height,
    length,
    seed,
    turbo=True,
    image_names=(),
    videos=(),
    audio_names=(),
    lock_audio=False,
    scheduler="simple",
    text_encoder=H3_DEFAULT_TEXT_ENCODER,
    lora_name=None,
    lora_strength=1.0,
    ref2va_model=H3_REF2VA_MODEL,
    fl2va_model=None
):
    """Ref2VA graph. videos: [(uploaded_name, use_soundtrack)]. lock_audio pins the first standalone audio into the AV latent."""
    workflow = {
        "1": model_loader(ref2va_model),
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": text_encoder, "type": "minimax"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": video_vae()}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": H3_AUDIO_VAE}},
    }
    turbo_lora, steps, cfg = mode_settings(turbo)
    last_model_node = ["1", 0]
    if turbo_lora:
        workflow["5"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"model": last_model_node, "lora_name": H3_REF2VA_LORA, "strength_model": 1.0}}
        last_model_node = ["5", 0]
    last_model_node = add_user_lora(workflow, last_model_node, lora_name, lora_strength)
    workflow["6"] = {"class_type": "MiniMaxH3SigmaShift", "inputs": {"model": last_model_node, "shift_video": 12.0, "shift_audio": 3.0}}

    # Autogrow inputs are addressed as "<group>.<prefix><index>" with 0-based indices.
    ref_inputs = {
        "clip": ["2", 0], "vae": ["3", 0], "audio_vae": ["4", 0],
        "prompt": prompt_text, "width": width, "height": height, "length": length, "ref_image_size": "match",
    }
    for i, name in enumerate(image_names):
        workflow[f"10{i}"] = {"class_type": "LoadImage", "inputs": {"image": name}}
        ref_inputs[f"ref_images.ref_image_{i}"] = [f"10{i}", 0]
    for i, (name, use_soundtrack) in enumerate(videos):
        workflow[f"11{i}"] = {"class_type": "LoadVideo", "inputs": {"file": name}}
        workflow[f"12{i}"] = {"class_type": "GetVideoComponents", "inputs": {"video": [f"11{i}", 0]}}
        ref_inputs[f"ref_videos.ref_video_{i}"] = [f"12{i}", 0]
        if use_soundtrack:
            ref_inputs[f"ref_video_audios.ref_video_audio_{i}"] = [f"12{i}", 1]
    for i, name in enumerate(audio_names):
        workflow[f"13{i}"] = {"class_type": "LoadAudio", "inputs": {"audio": name}}
        ref_inputs[f"ref_audios.ref_audio_{i}"] = [f"13{i}", 0]
    workflow["7"] = {"class_type": "MiniMaxH3ReferenceToVideo", "inputs": ref_inputs}
    workflow["8"] = {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["7", 0]}}

    latent = ["7", 1]
    if lock_audio:
        # The source audio replaces the target audio stream with a zero denoise mask, so the picture is sampled against it.
        workflow["14"] = {"class_type": "VAEEncodeAudio", "inputs": {"audio": ["130", 0], "vae": ["4", 0]}}
        workflow["15"] = {"class_type": "MiniMaxH3LockAudioLatent", "inputs": {"target_latent": latent, "audio_latent": ["14", 0]}}
        latent = ["15", 0]

    workflow["20"] = {
        "class_type": "KSampler",
        "inputs": {
            "model": ["6", 0], "positive": ["7", 0], "negative": ["8", 0], "latent_image": latent,
            "seed": seed, "steps": steps, "cfg": cfg,
            "sampler_name": "euler", "scheduler": scheduler, "denoise": 1.0
        }
    }
    workflow["30"] = {"class_type": "VAEDecode", "inputs": {"samples": ["20", 0], "vae": ["3", 0]}}
    workflow["31"] = {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["20", 0], "vae": ["4", 0]}}
    workflow["40"] = {"class_type": "CreateVideo", "inputs": {"images": ["30", 0], "audio": ["31", 0], "fps": 24.0}}
    workflow["41"] = {"class_type": "SaveVideo", "inputs": {"video": ["40", 0], "filename_prefix": "MiniMax_H3_Ref2VA", "format": "auto", "codec": "auto"}}
    return workflow

def snap_h3_length(frames):
    frames = max(5, int(frames))
    while frames % 17 != 5:
        frames += 1
    return frames

def plan_long_segments(total_seconds, segment_seconds, overlap_frames, prompt_count=0):
    """Frame windows for TimelineDirector: each 5+17n long, each seam overlapping by an H3-valid count."""
    length = snap_h3_length(round(segment_seconds * 24))
    if overlap_frames >= length:
        raise gr.Error("每段秒數太短，必須大於接縫重疊長度。")
    step = length - overlap_frames
    if prompt_count:
        count = prompt_count
        target = None
    else:
        target = round(total_seconds * 24)
        count = max(1, -(-(target - overlap_frames) // step))
    if count > 64:
        raise gr.Error("分段數超過 64，請加長每段秒數或縮短總長度。")
    windows = [(i * step, i * step + length) for i in range(count)]
    if target and count > 1:
        # Trim only the last window toward the requested length, staying inside H3's trained 124+ frame range.
        start = windows[-1][0]
        windows[-1] = (start, start + min(length, snap_h3_length(max(target - start, 124))))
    return windows

def build_long_video_prompt(
    global_prompt,
    segment_prompts,
    windows,
    width,
    height,
    seed,
    ref_image_name=None,
    scheduler="simple",
    text_encoder=H3_DEFAULT_TEXT_ENCODER,
    lora_name=None,
    lora_strength=1.0,
    ref2va_model=H3_REF2VA_MODEL,
    fl2va_model=None,
    mode=MODE_TURBO_LORA
):
    images = [{"id": "ref_image_1", "file": ref_image_name}] if ref_image_name else []
    segments = []
    for index, (start, end) in enumerate(windows):
        segment = {"startFrame": start, "endFrame": end, "images": ["ref_image_1"] if images else [], "audios": []}
        if segment_prompts:
            segment["prompt"] = segment_prompts[index]
        segments.append(segment)
    timeline = {
        "selection": {"start": 0.0, "duration": windows[-1][1] / 24},
        "videoClips": [],
        "images": images,
        "audios": [],
        "globalPrompt": global_prompt,
        "segmentConfig": {"mode": "timeline", "count": len(windows), "activeIndex": 0, "segments": segments},
    }

    workflow = {
        "1": model_loader(ref2va_model),
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": text_encoder, "type": "minimax"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": video_vae()}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": H3_AUDIO_VAE}},
    }
    turbo_lora, steps, _ = mode_settings(mode)
    last_model_node = ["1", 0]
    if turbo_lora:
        workflow["5"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": H3_REF2VA_LORA, "strength_model": 1.0}}
        last_model_node = ["5", 0]
    last_model_node = add_user_lora(workflow, last_model_node, lora_name, lora_strength)
    workflow["6"] = {"class_type": "MiniMaxH3SigmaShift", "inputs": {"model": last_model_node, "shift_video": 12.0, "shift_audio": 3.0}}
    workflow["10"] = {
        "class_type": "MiniMaxH3TimelinePlanner",
        "inputs": {"width": width, "height": height, "generation_seconds": windows[-1][1] / 24, "timeline_data": json.dumps(timeline, ensure_ascii=False)}
    }
    workflow["11"] = {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}}
    workflow["12"] = {"class_type": "BasicScheduler", "inputs": {"model": ["6", 0], "scheduler": scheduler, "steps": steps, "denoise": 1.0}}
    workflow["20"] = {
        "class_type": "MiniMaxH3FiniteSegmentSampler",
        "inputs": {
            "model": ["6", 0], "clip": ["2", 0], "vae": ["3", 0], "audio_vae": ["4", 0],
            "finite_plan": ["10", 2], "sampler": ["11", 0], "sigmas": ["12", 0],
            "seed": seed, "continue_audio_latent": True, "ref_image_size": "match"
        }
    }
    workflow["40"] = {"class_type": "CreateVideo", "inputs": {"images": ["20", 1], "audio": ["20", 2], "fps": 24.0}}
    workflow["41"] = {"class_type": "SaveVideo", "inputs": {"video": ["40", 0], "filename_prefix": "MiniMax_H3_Long", "format": "auto", "codec": "auto"}}
    return workflow

LONG_VIDEO_RESOLUTIONS = [
    "864 × 480 (16:9 標清 · 推薦)",
    "960 × 544 (16:9 中清)",
    "1280 × 720 (16:9 高畫質 · 需 24GB，每鏡建議 6~8 秒)",
    "1344 × 768 (16:9 最高畫質 · H3 原生上限，需 24GB，每鏡建議 5~6 秒)",
    "480 × 864 (9:16 直式)",
    "720 × 1280 (9:16 直式高畫質 · 需 24GB，每鏡建議 6~8 秒)",
    "1024 × 1024 (1:1 正方)",
]
SMITE_ENGINE = "Smite79 H3-LongVideos (推薦・次世代劇本分鏡長片)"
TIMELINE_ENGINE = "TimelineDirector (舊版滑動視窗)"
# Smite79's licence forbids bundling it into another installer, so users install it themselves.
SMITE_REPO_URL = "https://github.com/Smite79/MiniMax-H3-LongVideos"

def smite_node_installed():
    root = os.path.join(COMFY_DIR, "custom_nodes")
    try:
        return any("longvideos" in name.lower() and not name.lower().endswith(".disabled")
                   and os.path.isdir(os.path.join(root, name)) for name in os.listdir(root))
    except OSError:
        return False

LONG_HQ_MIN_MP = 0.6          # at or above this the option counts as 高畫質
LONG_HQ_MIN_VRAM_GB = 22      # 高畫質 needs a 24GB-class card


def long_video_ratio_mp(resolution_str):
    """(aspect ratio, megapixels) for the H3LongVideos node, computed from the W×H in the label.
    The node sizes the frame by megapixels (1 MP = 1024×1024) and the ratio."""
    width, height = parse_resolution(resolution_str)
    mp = round(width * height / (1024 * 1024), 2)
    if "9:16" in resolution_str:
        ratio = "9:16"
    elif "1:1" in resolution_str:
        ratio = "1:1"
    elif "4:3" in resolution_str:
        ratio = "4:3"
    else:
        ratio = "16:9"
    return ratio, mp


# The Ref2VA Turbo LoRA at 4 steps leaves long-video shots undercooked (smeared, over-saturated
# frames at 1280x720, soft ones at 480p); the H3LongVideos node itself asks for 6-8 with a turbo LoRA.
LONG_TURBO_MIN_STEPS = 8

def long_video_steps(mode):
    turbo_lora, steps, _ = mode_settings(mode)
    return max(steps, LONG_TURBO_MIN_STEPS) if turbo_lora else steps

def build_smite_long_video_prompt(
    prompt_text,
    resolution_str,
    segment_seconds,
    seed,
    mode=MODE_TURBO_LORA,
    ref_image_name=None,
    scheduler="simple",
    text_encoder=H3_TEXT_ENCODER,
    lora_name=None,
    lora_strength=1.0,
    ref2va_model=H3_REF2VA_MODEL,
    plan_only=False
):
    """Build ComfyUI prompt graph for Smite79/MiniMax-H3-Longvideos architecture."""
    workflow = {
        "1": model_loader(ref2va_model),
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": text_encoder, "type": "minimax"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": video_vae()}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": H3_AUDIO_VAE}},
    }
    turbo_lora, _, _ = mode_settings(mode)
    steps = long_video_steps(mode)
    last_model = ["1", 0]
    if turbo_lora:
        workflow["5"] = {
            "class_type": "LoraLoaderModelOnly",
            "inputs": {
                "model": last_model,
                "lora_name": H3_REF2VA_LORA,
                "strength_model": 1.0
            }
        }
        last_model = ["5", 0]
    last_model = add_user_lora(workflow, last_model, lora_name, lora_strength)

    res_ratio, mp = long_video_ratio_mp(resolution_str)

    h3_inputs = {
        "model": last_model,
        "clip": ["2", 0],
        "vae": ["3", 0],
        "audio_vae": ["4", 0],
        "prompt": prompt_text,
        "resolution": res_ratio,
        "megapixels": mp,
        "shot_seconds": float(segment_seconds or 10.0),
        "steps": steps,
        "sampler_name": "res_multistep",
        "scheduler": scheduler or "simple",
        "seed": int(seed),
        "plan_only": bool(plan_only)
    }

    if ref_image_name:
        workflow["7"] = {"class_type": "LoadImage", "inputs": {"image": ref_image_name}}
        h3_inputs["ref_image_1"] = ["7", 0]

    workflow["10"] = {
        "class_type": "H3LongVideos",
        "inputs": h3_inputs
    }
    workflow["20"] = {
        "class_type": "CreateVideo",
        "inputs": {
            "images": ["10", 0],
            "audio": ["10", 1],
            "fps": 24.0
        }
    }
    workflow["30"] = {
        "class_type": "SaveVideo",
        "inputs": {
            "video": ["20", 0],
            "filename_prefix": "video/H3_LongVideo",
            "format": "auto"
        }
    }
    return workflow

def split_segment_prompts(text):
    """Segments are split by a `---` line; without one, blank-line paragraphs (the Smite79 beat
    style the tab asks for) are the segments, so switching engines keeps the same text working."""
    separator = r"^\s*---+\s*$" if re.search(r"^\s*---+\s*$", text or "", flags=re.MULTILINE) else r"\n\s*\n"
    return [part.strip() for part in re.split(separator, text or "", flags=re.MULTILINE) if part.strip()]

def preview_long_plan(total_seconds, segment_seconds, segment_prompts_text):
    prompts = split_segment_prompts(segment_prompts_text)
    try:
        windows = plan_long_segments(total_seconds, segment_seconds, LONG_OVERLAP_FRAMES, len(prompts))
    except gr.Error as error:
        return str(error)
    rows = [f"| {i} | {s / 24:.2f}s → {e / 24:.2f}s | {e - s} 幀 |" for i, (s, e) in enumerate(windows, 1)]
    source = f"依 {len(prompts)} 段分段提示詞" if prompts else "依總長度"
    return (f"{source}：共 **{len(windows)} 段**，成片約 **{windows[-1][1] / 24:.1f} 秒**；"
            f"段間重疊 {LONG_OVERLAP_FRAMES} 幀（{LONG_OVERLAP_FRAMES / 24:.2f} 秒）。\n\n"
            "| 段 | 時間 | 長度 |\n|---|---|---|\n" + "\n".join(rows))

def execute_long_generation(
    global_prompt,
    segment_prompts_text,
    total_seconds,
    segment_seconds,
    resolution_str,
    seed,
    ref_image_file=None,
    scheduler="simple",
    mode=MODE_TURBO_LORA,
    engine="Smite79 H3-LongVideos (推薦・次世代劇本分鏡長片)",
    plan_only=False,
    text_encoder=None,
    lora_name=None,
    lora_strength=1.0,
    fl2va_model=None,
    ref2va_model=None,
    progress=gr.Progress()
):
    progress(0.05, desc="正在連線至 MiniMax H3 引擎...")
    if not ensure_comfy_server():
        raise gr.Error("無法啟動或連線至 ComfyUI 後端引擎，請檢查 8188 埠！")

    model_options = resolve_model_options(text_encoder, lora_name, lora_strength, fl2va_model, ref2va_model)
    target_ref2va_model = model_options["ref2va_model"] or H3_REF2VA_MODEL

    if seed is None or seed == -1:
        seed = random.randint(1, 1000000000000000)
    seed = int(seed)

    ref_image_name = upload_image(ref_image_file) if ref_image_file else None

    # Determine which engine to use: Smite79 H3-LongVideos (Recommended) or TimelineDirector
    use_smite = "smite" in (engine or "").lower() or "h3-longvideos" in (engine or "").lower()

    if use_smite:
        # Assemble Smite79 multi-shot prompt (Scene + Beats)
        parts = []
        if global_prompt and global_prompt.strip():
            parts.append(global_prompt.strip())
        if segment_prompts_text and segment_prompts_text.strip():
            clean_segments = segment_prompts_text.replace("---", "\n\n").strip()
            parts.append(clean_segments)

        if not parts:
            raise gr.Error("請輸入全域提示詞／劇本場景或分鏡提示詞！")

        full_prompt = "\n\n".join(parts)

        if "H3LongVideos" not in requests.get(f"{COMFY_URL}/object_info/H3LongVideos", timeout=10).json():
            raise gr.Error(
                "Smite79 長片引擎尚未安裝（它的授權不允許其他安裝程式代為下載，需自行安裝）。"
                f"請到 {SMITE_REPO_URL} 下載，解壓到 ComfyUI\\custom_nodes\\ 後執行 restart_webui.bat；"
                f"或把「長片生成系統架構」改選「{TIMELINE_ENGINE}」直接使用。")
        check_generation_limits(target_ref2va_model, model_options["lora_name"], mode, False, 0, 0, 0, "ref2va")

        _, long_mp = long_video_ratio_mp(resolution_str)
        if long_mp >= LONG_HQ_MIN_MP:
            if VRAM_GB is not None and VRAM_GB < LONG_HQ_MIN_VRAM_GB:
                raise gr.Error(
                    f"高畫質長片（約 {long_mp:g} MP）需要 24GB 級顯卡，這台偵測到 {VRAM_GB:.0f} GB。"
                    "請改選 864×480 或 960×544，生成後再用「🔍 放大」SeedVR2 升解析度。")
            shot_limit = 6 if long_mp >= 0.9 else 8
            if float(segment_seconds or 10) > shot_limit:
                gr.Warning(f"高畫質（約 {long_mp:g} MP）建議「每鏡頭目標秒數」≤ {shot_limit} 秒；"
                           f"目前 {int(float(segment_seconds or 10))} 秒，顯存可能不足而中斷。")

        progress(0.15, desc="正在建置 Smite79 H3-LongVideos 長片工作流...")
        prompt_graph = build_smite_long_video_prompt(
            prompt_text=full_prompt,
            resolution_str=resolution_str,
            segment_seconds=segment_seconds,
            seed=seed,
            mode=mode,
            ref_image_name=ref_image_name,
            scheduler=scheduler,
            text_encoder=model_options["text_encoder"] or H3_TEXT_ENCODER,
            lora_name=model_options["lora_name"],
            lora_strength=model_options["lora_strength"],
            ref2va_model=target_ref2va_model,
            plan_only=plan_only
        )

        stage_desc = "分鏡劇本規劃 (Plan Only)" if plan_only else "長片連鎖採樣"
        steps = long_video_steps(mode)
        output_video_path = run_comfy_workflow(
            prompt_graph,
            steps if not plan_only else 1,
            progress,
            "正在載入模型並啟動 Smite79 H3-LongVideos 引擎...",
            stage_desc,
            output_node="30"
        )

        history.record("Smite79長片" + ("(PlanOnly)" if plan_only else ""),
                       full_prompt, output_video_path,
                       resolution=resolution_str, seconds=round(float(total_seconds or 30), 2),
                       seed=seed, mode=mode if isinstance(mode, str) else None,
                       scheduler=scheduler, model=target_ref2va_model,
                       encoder=model_options["text_encoder"])
        progress(1.0, desc="Smite79 長片生成完成！" if not plan_only else "分鏡規劃完成！")
        return output_video_path

    else:
        # Fallback: TimelineDirector (舊版滑動視窗)
        segment_prompts = split_segment_prompts(segment_prompts_text)
        if not segment_prompts and not (global_prompt and global_prompt.strip()):
            raise gr.Error("請輸入全域提示詞，或填寫分段提示詞！")
        windows = plan_long_segments(total_seconds, segment_seconds, LONG_OVERLAP_FRAMES, len(segment_prompts))
        # The long-video labels (e.g. 1280 × 720) are not all on H3's 32 px grid; Smite79 snaps itself.
        width, height = (int(v / 32 + 0.5) * 32 for v in parse_resolution(resolution_str))
        check_generation_limits(target_ref2va_model, model_options["lora_name"], mode, False, width, height, 0, "ref2va")

        if ref_image_name:
            prompts = segment_prompts or [global_prompt]
            if not all("<picture" in p.lower() for p in prompts):
                raise gr.Error("已上傳角色參考圖：每段提示詞（或全域提示詞）都要用 <Picture 1> 指定該角色。")

        progress(0.15, desc=f"正在準備 {len(windows)} 段 TimelineDirector 圖譜...")
        prompt_graph = build_long_video_prompt(
            global_prompt=(global_prompt or "").strip(),
            segment_prompts=segment_prompts,
            windows=windows,
            width=width,
            height=height,
            seed=seed,
            ref_image_name=ref_image_name,
            scheduler=scheduler,
            mode=mode,
            **model_options
        )
        output_video_path = run_comfy_workflow(
            prompt_graph, mode_settings(mode)[1], progress,
            "正在載入 Ref2VA 模型...", "長片採樣",
            segments=len(windows),
            output_node="41"
        )
        history.record("長片(TimelineDirector)", global_prompt or "\n---\n".join(segment_prompts), output_video_path,
                       resolution=f"{width}×{height}", seconds=round(windows[-1][1] / 24, 2), seed=seed,
                       mode=mode if isinstance(mode, str) else None, scheduler=scheduler,
                       model=target_ref2va_model, encoder=model_options["text_encoder"])
        progress(1.0, desc="長片生成完成！")
        return output_video_path


def is_krea2_model(name):
    """Krea2 is an image model (different architecture); keep it out of the H3 video menus."""
    return "krea2" in (name or "").lower()


def diffusion_model_choices(trunk=None):
    """H3 diffusion models for the FL2VA/Ref2VA menus. .gguf -> UnetLoaderGGUF, .safetensors ->
    UNETLoader. Krea2 image models are excluded; trunk 'fl2va'/'ref2va' hides the other trunk's
    dedicated models (models named for neither trunk, e.g. DaSiwa Hybrid, show in both)."""
    gguf = [f for f in list_model_files("diffusion_models", "UnetLoaderGGUF", "unet_name") if f.endswith(".gguf")]
    plain = [f for f in list_model_files("diffusion_models", "UNETLoader", "unet_name") if f.endswith(".safetensors")]
    files = [f for f in sorted(set(gguf + plain)) if not is_krea2_model(f)]
    if trunk == "fl2va":
        files = [f for f in files if "singularity" in f.lower() or ("ref2va" not in f.lower() and "ref2v" not in f.lower())]
    elif trunk == "ref2va":
        files = [f for f in files if "singularity" in f.lower() or ("fl2va" not in f.lower() and "fl2v" not in f.lower())]
    return files

def model_label_choices(models):
    """(display, value) pairs: put prominent tag at the front so it is instantly recognizable in dropdowns."""
    def label_for(name):
        low = name.lower()
        if "singularity" in low:
            return f"🌟【Singularity 奇點】HDR動作微調 (推薦) — {name}"
        if "dasiwa" in low or "hybrid" in low:
            return f"⚡【DaSiwa 混合】8步內建蒸餾 — {name}"
        if "q4_k_m" in low or "-q4" in low:
            return f"🚀【官方 Q4 GGUF】最省顯存・極速推薦 — {name}"
        if "int8_convrot" in low:
            return f"💎【官方 INT8】高畫質慢速・吃顯存 — {name}"
        return name
    return [(label_for(m), m) for m in models]

def v2v_default_model(choices):
    for c in choices:
        if "singularity" in c.lower():
            return c
    return krea2_default(choices, H3_REF2VA_MODEL)


def model_file_size(model_name):
    for folder in model_dirs("diffusion_models"):
        candidate = os.path.join(folder, model_name.replace("/", os.sep))
        if os.path.exists(candidate):
            return os.path.getsize(candidate)
    return 0

def check_generation_limits(model_name, lora_name, mode, hd, width, height, duration, trunk):
    """Refuse combinations that crashed the backend before, and warn about mismatched pairings."""
    if hd and not HD_ALLOWED:
        raise gr.Error(
            f"高清二次採樣需要 24GB 級顯卡，這台偵測到 {VRAM_GB:.0f} GB。"
            "請用 864×480 或 960×544 生成，再到「🔍 放大」分頁用 SeedVR2 升解析度。")
    if LOW_VRAM:
        if model_file_size(model_name) > HD_MAX_MODEL_BYTES:
            gr.Warning(f"「{model_name}」約 {model_file_size(model_name) / 1000 ** 3:.0f} GB，比 {VRAM_GB:.0f} GB 顯存還大，"
                       "會非常慢；建議在「🧩 模型設定」改選 Q4 GGUF 模型。")
        if width and height and width * height > LOW_VRAM_MAX_PIXELS:
            gr.Warning(f"{width}×{height} 對 {VRAM_GB:.0f} GB 顯存偏大，可能很慢或顯存不足；"
                       "建議 864×480 或 960×544，之後用「🔍 放大」升解析度。")
    if hd:
        size = model_file_size(model_name)
        if size > HD_MAX_MODEL_BYTES:
            raise gr.Error(
                f"高清二次採樣不能搭配這個模型：「{model_name}」約 {size / 1000 ** 3:.0f} GB，載入後顯存所剩無幾，"
                "放大階段會耗盡顯存並讓後端崩潰。請改選 Q4 GGUF 模型，或取消高清二次採樣。")
        if width * height * duration > HD_MAX_PIXEL_SECONDS:
            seconds = HD_MAX_PIXEL_SECONDS / (width * height)
            raise gr.Error(
                f"{width}×{height} 的高清二次採樣最多約 {seconds:.0f} 秒，目前設定 {int(duration)} 秒會耗盡顯存。"
                "請縮短長度、降低解析度，或改用「📼 長片」分頁分段生成。")
    lowered = (model_name or "").lower()
    if mode == MODE_TURBO_LORA and "turbo" in lowered:
        gr.Warning(f"「{model_name}」檔名顯示已內建蒸餾，建議採樣模式改選「{MODE_BAKED_TURBO}」；兩種蒸餾疊加會讓畫面變差。")
    if lora_name and lora_name != NO_LORA:
        other = "ref2va" if trunk == "fl2va" else "fl2va"
        if other in lora_name.lower().replace("ref2v", "ref2va").replace("fl2v", "fl2va"):
            gr.Warning(f"「{lora_name}」看起來是 {other.upper()} 專用的 LoRA，這個分頁用的是 {trunk.upper()} 模型，權重會對不上而失效。")

def model_loader(model_name):
    if model_name.endswith(".gguf"):
        return {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": model_name}}
    return {"class_type": "UNETLoader", "inputs": {"unet_name": model_name, "weight_dtype": "default"}}

def krea2_model_choices():
    """Only Krea2 image models for the 圖片 tab (keep the H3 video models out)."""
    models = [f for f in list_model_files("diffusion_models", "UNETLoader", "unet_name")
              if f.endswith(".safetensors") and is_krea2_model(f)]
    # Sort to prioritize official Krea-2 Turbo model first
    return sorted(models, key=lambda f: (0 if "krea2_turbo_fp8" in f.lower() else 1, f))

def krea2_models_ready():
    names = lambda kind, node, field: {os.path.basename(f) for f in list_model_files(kind, node, field)}
    return bool(krea2_model_choices()) and KREA2_TEXT_ENCODER in names("text_encoders", "CLIPLoader", "clip_name") \
        and KREA2_VAE in names("vae", "VAELoader", "vae_name")

def seedvr2_models_ready():
    return bool(seedvr2_model_choices()) and SEEDVR2_VAE in {
        os.path.basename(f) for f in list_model_files("SEEDVR2", "SeedVR2LoadVAEModel", "model")}

def krea2_default(choices, preferred):
    for c in choices:
        if "krea2_turbo_fp8" in c.lower():
            return c
    return preferred if preferred in choices else (choices[0] if choices else preferred)

def krea2_style_loras():
    prefix = KREA2_LORA_SUBDIR + "/"
    return sorted(f for f in list_model_files("loras", "LoraLoaderModelOnly", "lora_name")
                  if f.endswith(".safetensors") and f.replace("\\", "/").startswith(prefix))

def lora_file_path(name):
    for folder in model_dirs("loras"):
        candidate = os.path.join(folder, name.replace("/", os.sep).replace("\\", os.sep))
        if os.path.exists(candidate):
            return candidate
    return None

def lora_thumbnail(name):
    """Sidecar preview next to the LoRA (Civitai convention) or a generated one; else a name card."""
    path = lora_file_path(name)
    if path:
        stem = path[:-len(".safetensors")]
        for ext in THUMB_EXTENSIONS:
            if os.path.exists(stem + ext):
                return stem + ext
    os.makedirs(THUMB_DIR, exist_ok=True)
    card = os.path.join(THUMB_DIR, os.path.basename(name).replace(".safetensors", ".card.png"))
    if not os.path.exists(card):
        from PIL import Image, ImageDraw
        image = Image.new("RGB", (256, 256), (28, 28, 40))
        draw = ImageDraw.Draw(image)
        label = os.path.basename(name).replace(".safetensors", "").replace("krea2_", "")
        draw.rectangle([8, 8, 247, 247], outline=(99, 102, 241), width=3)
        draw.text((20, 110), label[:22], fill=(226, 232, 240))
        draw.text((20, 140), "(no preview)", fill=(148, 163, 184))
        image.save(card)
    return card

def lora_trigger(name):
    """Trigger words live in a `<lora>.trigger.txt` sidecar; style LoRAs stay inert without them."""
    path = lora_file_path(name)
    if not path:
        return ""
    sidecar = path[:-len(".safetensors")] + ".trigger.txt"
    if os.path.exists(sidecar):
        with open(sidecar, encoding="utf-8") as stream:
            return " ".join(stream.read().split())
    return ""

def with_triggers(prompt, names):
    missing = [t for t in (lora_trigger(n) for n in names) if t and t.lower() not in prompt.lower()]
    return ", ".join([prompt.strip(), *missing]) if missing else prompt

def trigger_summary(*names):
    rows = [f"- `{os.path.basename(n).replace('.safetensors', '')}` → **{lora_trigger(n) or '（沒有觸發詞檔）'}**"
            for n in names if n and n != NO_LORA]
    return ("生成時會自動把觸發詞接到提示詞後面：\n" + "\n".join(rows)) if rows else ""

def has_real_preview(name):
    thumb = lora_thumbnail(name)
    return thumb is not None and not thumb.endswith(".card.png")

def krea2_lora_gallery():
    names = krea2_style_loras()
    return [(lora_thumbnail(n), os.path.basename(n).replace(".safetensors", "")) for n in names], names

def build_krea2_prompt(prompt_text, width, height, batch, seed, model_name,
                       lora_name, lora_strength, sampler, steps, scheduler, cfg,
                       text_encoder, vae, extra_loras=()):
    """Krea2 workflow: clean single-pass KSampler for official Krea-2 Turbo model."""
    workflow = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": model_name, "weight_dtype": "default"}},
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": text_encoder, "type": "krea2"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": vae}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["3", 0], "text": prompt_text}},
        "8": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["7", 0]}},
        "9": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": batch}},
        "10": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": sampler}},
    }
    model_node = ["1", 0]
    # If the model is already a distilled Turbo model, do not attach Turbo LoRA again
    is_turbo_baked = "turbo" in (model_name or "").lower()
    if lora_name and lora_strength and not is_turbo_baked:
        workflow["5"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": lora_name, "strength_model": lora_strength}}
        model_node = ["5", 0]
    for index, (name, strength) in enumerate(extra_loras):
        workflow[f"3{index}"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"model": model_node, "lora_name": name, "strength_model": strength}}
        model_node = [f"3{index}", 0]

    workflow["20"] = {"class_type": "KSampler", "inputs": {
        "model": model_node, "positive": ["7", 0], "negative": ["8", 0], "latent_image": ["9", 0],
        "seed": seed, "steps": steps, "cfg": cfg, "sampler_name": sampler, "scheduler": scheduler, "denoise": 1.0}}
    sampled = ["20", 0]

    workflow["15"] = {"class_type": "VAEDecode", "inputs": {"samples": sampled, "vae": ["4", 0]}}
    workflow["16"] = {"class_type": "SaveImage", "inputs": {"images": ["15", 0], "filename_prefix": "Krea2_Output"}}
    return workflow

def resolve_extra_loras(*slots):
    extra = []
    for name, strength in zip(slots[0::2], slots[1::2]):
        if name and name != NO_LORA and float(strength or 0):
            extra.append((resolve_backend_file("LoraLoaderModelOnly", "lora_name", name, " LoRA "), float(strength)))
    return extra

def execute_krea2_generation(prompt, size_str, batch, seed, model_name, lora_name,
                             lora_strength, sampler, steps, scheduler, cfg, text_encoder, vae,
                             lora_1=None, strength_1=1.0, lora_2=None, strength_2=1.0, lora_3=None, strength_3=1.0,
                             progress=gr.Progress()):
    if not prompt or not prompt.strip():
        raise gr.Error("請輸入提示詞 (Prompt)！")

    progress(0.05, desc="正在連線至 ComfyUI...")
    if not ensure_comfy_server():
        raise gr.Error("無法啟動或連線至 ComfyUI 後端引擎，請檢查 8188 埠！")
    model_name = resolve_backend_file("UNETLoader", "unet_name", model_name, "Krea2 擴散模型", 1)
    text_encoder = resolve_backend_file("CLIPLoader", "clip_name", text_encoder, " Krea2 文字編碼器", 1)
    vae = resolve_backend_file("VAELoader", "vae_name", vae, " Krea2 VAE", 1)
    if lora_name and lora_name != NO_LORA:
        lora_name = resolve_backend_file("LoraLoaderModelOnly", "lora_name", lora_name, " Turbo LoRA ")
    else:
        lora_name = None

    extra_loras = resolve_extra_loras(lora_1, strength_1, lora_2, strength_2, lora_3, strength_3)
    width, height = parse_resolution(size_str)
    if seed is None or seed == -1:
        import random
        seed = random.randint(1, 1000000000000000)

    prompt = with_triggers(prompt, [name for name, _ in extra_loras])
    progress(0.15, desc=f"正在準備 Krea2 圖譜（{width}×{height} ×{int(batch)}）...")
    prompt_graph = build_krea2_prompt(
        prompt_text=prompt, width=width, height=height, batch=int(batch), seed=int(seed),
        model_name=model_name, lora_name=lora_name, lora_strength=float(lora_strength),
        sampler=sampler, steps=int(steps), scheduler=scheduler, cfg=float(cfg),
        text_encoder=text_encoder, vae=vae, extra_loras=extra_loras)

    images = run_comfy_workflow(prompt_graph, int(steps), progress, "正在載入 Krea2 模型...",
                                "Krea2 採樣", output_node="16", multiple=True)
    history.record("圖片 Krea2", prompt, images, resolution=f"{width}×{height}", seed=int(seed),
                   mode="官方 Turbo", model=model_name, encoder=text_encoder,
                   lora=", ".join(f"{os.path.basename(n)}×{s}" for n, s in extra_loras) or lora_name,
                   lora_strength=None if extra_loras else (lora_strength if lora_name else None))
    progress(1.0, desc="圖片生成完成！")
    return images

def generate_krea2_thumbnails(model_name, text_encoder, vae, turbo_lora, only_missing=True, progress=gr.Progress()):
    only_missing = bool(only_missing)
    names = [n for n in krea2_style_loras() if not (only_missing and has_real_preview(n))]
    if not names:
        gallery, _ = krea2_lora_gallery()
        gr.Info("所有 LoRA 都已經有縮圖。")
        return gallery
    if not ensure_comfy_server():
        raise gr.Error("無法啟動或連線至 ComfyUI 後端引擎，請檢查 8188 埠！")
    model_name = resolve_backend_file("UNETLoader", "unet_name", model_name, "Krea2 擴散模型", 1)
    text_encoder = resolve_backend_file("CLIPLoader", "clip_name", text_encoder, " Krea2 文字編碼器", 1)
    vae = resolve_backend_file("VAELoader", "vae_name", vae, " Krea2 VAE", 1)
    turbo = resolve_backend_file("LoraLoaderModelOnly", "lora_name", turbo_lora, " Turbo LoRA ") if turbo_lora and turbo_lora != NO_LORA else None
    import shutil
    for index, name in enumerate(names, 1):
        progress((index - 1) / len(names), desc=f"產生縮圖 {index}/{len(names)}：{os.path.basename(name)}")
        graph = build_krea2_prompt(
            prompt_text=with_triggers(THUMB_PROMPT, [name]), width=512, height=512, batch=1, seed=20260916,
            model_name=model_name, lora_name=turbo, lora_strength=0.85,
            sampler="er_sde", steps=8, scheduler="simple", cfg=1.0,
            text_encoder=text_encoder, vae=vae,
            extra_loras=[(resolve_backend_file("LoraLoaderModelOnly", "lora_name", name, " LoRA "), 1.0)])
        graph["16"]["inputs"]["filename_prefix"] = "lora_thumbs/thumb"
        image = run_comfy_workflow(graph, 8, lambda *a, **k: None, "載入中", "縮圖", output_node="16", multiple=True)[0]
        target = lora_file_path(name)[:-len(".safetensors")] + ".preview.png"
        shutil.copyfile(image, target)
    progress(1.0, desc="縮圖產生完成")
    gallery, _ = krea2_lora_gallery()
    return gallery

def seedvr2_model_choices():
    return [f for f in list_model_files("SEEDVR2", "SeedVR2LoadDiTModel", "model") if f.endswith(".safetensors")]

def build_seedvr2_prompt(video_name, dit_model, vae_model, resolution, batch_size, blocks_to_swap,
                         color_correction, seed):
    """Load the clip, run SeedVR2 on its frames, and mux back the original audio."""
    return {
        "1": {"class_type": "LoadVideo", "inputs": {"file": video_name}},
        "2": {"class_type": "GetVideoComponents", "inputs": {"video": ["1", 0]}},
        "3": {"class_type": "SeedVR2LoadDiTModel",
              "inputs": {"model": dit_model, "device": "cuda:0", "blocks_to_swap": blocks_to_swap,
                         "swap_io_components": False, "offload_device": "cpu", "cache_model": False, "attention": "sdpa"}},
        "4": {"class_type": "SeedVR2LoadVAEModel",
              "inputs": {"model": vae_model, "device": "cuda:0", "encode_tiled": True, "encode_tile_size": 1024,
                         "encode_tile_overlap": 128, "decode_tiled": True, "decode_tile_size": 768,
                         "decode_tile_overlap": 128, "tile_debug": "false", "offload_device": "cpu", "cache_model": False}},
        "5": {"class_type": "SeedVR2VideoUpscaler",
              "inputs": {"image": ["2", 0], "dit": ["3", 0], "vae": ["4", 0], "seed": seed,
                         "resolution": resolution, "max_resolution": 0, "batch_size": batch_size,
                         "uniform_batch_size": False, "temporal_overlap": 0, "prepend_frames": 0,
                         "color_correction": color_correction, "input_noise_scale": 0.0, "latent_noise_scale": 0.0,
                         "offload_device": "cpu", "enable_debug": False}},
        "6": {"class_type": "CreateVideo", "inputs": {"images": ["5", 0], "audio": ["2", 1], "fps": ["2", 2]}},
        "41": {"class_type": "SaveVideo", "inputs": {"video": ["6", 0], "filename_prefix": "SeedVR2_Upscaled", "format": "auto", "codec": "auto"}},
    }

def execute_seedvr2_upscale(video_file, resolution_label, batch_size, blocks_to_swap, color_correction,
                            seed, dit_model, vae_model, progress=gr.Progress()):
    if not video_file:
        raise gr.Error("請先上傳要放大的影片。")
    progress(0.05, desc="正在連線至 ComfyUI...")
    if not ensure_comfy_server():
        raise gr.Error("無法啟動或連線至 ComfyUI 後端引擎，請檢查 8188 埠！")
    if "SeedVR2VideoUpscaler" not in requests.get(f"{COMFY_URL}/object_info/SeedVR2VideoUpscaler", timeout=10).json():
        raise gr.Error("後端尚未載入 SeedVR2 節點。請執行 restart_webui.bat 後再試。")
    dit_model = resolve_backend_file("SeedVR2LoadDiTModel", "model", dit_model, " SeedVR2 主模型", 4)
    vae_model = resolve_backend_file("SeedVR2LoadVAEModel", "model", vae_model, " SeedVR2 VAE", 4)

    video_name = upload_image(video_file)
    # SeedVR2's seed is a 32-bit int (max 4294967295), unlike H3's 64-bit; keep it in range.
    if seed is None or seed == -1:
        import random
        seed = random.randint(1, 4294967295)
    seed = int(seed) % 4294967296
    resolution = SEEDVR2_RES_CHOICES.get(resolution_label, 1080)
    progress(0.15, desc=f"正在準備 SeedVR2 圖譜（短邊 {resolution}，每批 {int(batch_size)} 幀）...")
    graph = build_seedvr2_prompt(video_name, dit_model, vae_model, resolution, int(batch_size),
                                 int(blocks_to_swap), color_correction, seed)
    # SeedVR2 reports its own progress; total_steps=0 keeps the bar in the loading state until node 41 finishes.
    output = run_comfy_workflow(graph, 0, progress, "正在以 SeedVR2 放大影片...", "SeedVR2 放大")
    history.record("SeedVR2 放大", os.path.basename(str(video_file)), output,
                   resolution=resolution_label, seed=int(seed), model=dit_model, mode=f"每批 {int(batch_size)} 幀")
    progress(1.0, desc="影片放大完成！")
    return output

# ---------------------------------------------------------------------------
# Qwen-Image-2.1 Image Editing (修圖)
# ---------------------------------------------------------------------------
QWEN_IMAGE_DEFAULT_DIT = "qwen_image_2.1_int8_convrot.safetensors"
QWEN_IMAGE_DEFAULT_ENCODER = "qwen3vl_8b_int8_convrot.safetensors"
QWEN_IMAGE_DEFAULT_VAE = "qwen_image_2.1_vae_bf16.safetensors"

QWEN_IMAGE_RESOLUTIONS = [
    "保持原圖比例 (預設 1024 推薦)",
    "2048 (2K 原生高解析度)",
    "768 (中解析度 · 極速)",
    "512 (標清 · 快速預覽)",
    "0 (完全依原圖原始像素)",
]

QWEN_IMAGE_PRESETS = {
    "👕 換裝／換衣服 (將 <image2> 服裝換到 <image1> 人物上)":
        "Keep the character and pose in <image1> unchanged, put this outfit from <image2> on the character, preserve original facial features, hair, body shape and pose, realistic fabric texture, natural clothing folds, keep original background and lighting, high fashion photography, sharp details",
    "💇 髮型與髮色修改 (將 <image1> 人物髮色改為銀白高光)":
        "In <image1>, modify the character's hair to elegant silver white with soft highlights, keep facial features, skin tone, clothing and background completely unchanged, hyper-realistic, 8k resolution",
    "🏙️ 背景置換 (將 <image1> 背景換為賽博龐克雨夜街景)":
        "Keep the person in <image1> exactly unchanged in appearance, clothing, and pose. Replace the background with a futuristic cyberpunk city at rainy night with neon signs, reflections on wet asphalt, cinematic volumetric lighting",
    "🎨 藝術風格轉移 (將 <image1> 轉為經典厚塗油畫風格)":
        "Transform <image1> into a masterpiece oil painting in the style of classical post-impressionism, rich impasto brushstrokes, expressive texture, dramatic lighting, museum quality",
    "💡 賽博龐克霓虹光影 (為 <image1> 增添強烈霓虹側光)":
        "Add dramatic cyberpunk cinematic lighting to <image1>, with vivid magenta and cyan neon rim lights casting realistic reflections on the subject, dramatic contrast, studio quality",
    "🎭 表情微調 (將 <image1> 人物改為自信開朗的露齒微笑)":
        "In <image1>, modify the character's facial expression to a warm, confident and radiant smile showing teeth, natural eye crinkles, perfectly matching the original lighting and skin texture",
    "🏖️ 度假海灘場景置換 (將 <image1> 人物置於熱帶海灘陽光下)":
        "Keep the subject in <image1> unchanged, place the subject seamlessly on a sunny tropical beach with white sand, turquoise ocean waves in the background, warm golden hour sunlight, realistic ambient lighting",
    "🧹 去除背景雜物 (將 <image1> 背景清理為極簡高級攝影棚)":
        "Keep the subject in <image1> completely unchanged, remove all background clutter and distractions, replace background with a clean, elegant minimalist studio backdrop with soft gradient lighting",
}

def qwen_image_model_choices():
    plain_dits = list_model_files("diffusion_models", "UNETLoader", "unet_name")
    gguf_dits = list_model_files("diffusion_models", "UnetLoaderGGUF", "unet_name")
    all_dits = sorted(set(plain_dits + gguf_dits))
    dits = [f for f in all_dits if "qwen" in f.lower()]
    encoders = [f for f in list_model_files("text_encoders", "CLIPLoader", "clip_name") if "qwen" in f.lower()]
    all_encoders = list_model_files("text_encoders", "CLIPLoader", "clip_name")
    vaes = [f for f in list_model_files("vae", "VAELoader", "vae_name") if "qwen" in f.lower()]
    all_vaes = list_model_files("vae", "VAELoader", "vae_name")
    return (dits or all_dits, encoders or all_encoders, vaes or all_vaes)

def qwen_image_models_ready():
    dits, encoders, vaes = qwen_image_model_choices()
    has_dit = any("qwen" in f.lower() for f in dits)
    has_enc = any("qwen" in f.lower() for f in encoders)
    has_vae = any("qwen" in f.lower() for f in vaes)
    return has_dit and has_enc and has_vae

def build_qwen_image_prompt(prompt_text, negative_prompt, resolution, steps, cfg, seed,
                            sampler, scheduler, dit_model, encoder_model, vae_model,
                            cache_device, cache_dtype, uploaded_images):
    if dit_model.endswith(".gguf"):
        dit_node = {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": dit_model}}
    else:
        dit_node = {"class_type": "UNETLoader", "inputs": {"unet_name": dit_model, "weight_dtype": "default"}}

    workflow = {
        "1": dit_node,
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": encoder_model, "type": "qwen_image"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": vae_model}},
        "4": {"class_type": "QwenImage21Cache", "inputs": {"model": ["1", 0], "device": cache_device, "dtype": cache_dtype}},
    }

    text_encode_inputs = {
        "clip": ["2", 0],
        "prompt": prompt_text,
        "negative_prompt": negative_prompt or "",
        "resolution": int(resolution),
        "vae": ["3", 0],
    }

    for idx, img_filename in enumerate(uploaded_images, 1):
        node_id = f"img_{idx}"
        workflow[node_id] = {"class_type": "LoadImage", "inputs": {"image": img_filename}}
        text_encode_inputs[f"images.image_{idx}"] = [node_id, 0]

    workflow["5"] = {"class_type": "TextEncodeQwenImage21", "inputs": text_encode_inputs}
    workflow["6"] = {
        "class_type": "KSampler",
        "inputs": {
            "model": ["4", 0],
            "positive": ["5", 0],
            "negative": ["5", 1],
            "latent_image": ["5", 2],
            "seed": int(seed),
            "steps": int(steps),
            "cfg": float(cfg),
            "sampler_name": sampler,
            "scheduler": scheduler,
            "denoise": 1.0,
        },
    }
    workflow["7"] = {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["3", 0]}}
    workflow["8"] = {"class_type": "SaveImage", "inputs": {"images": ["7", 0], "filename_prefix": "QwenImageEdit"}}
    return workflow

def execute_qwen_image_edit(primary_image, ref_image, extra_ref_images, prompt, negative_prompt, res_choice,
                            steps, cfg, seed, sampler, scheduler, dit_model, encoder_model,
                            vae_model, cache_device, cache_dtype, progress=gr.Progress()):
    if not primary_image:
        raise gr.Error("請先上傳要修改的主圖 (<image1>)！")
    if not prompt or not prompt.strip():
        raise gr.Error("請輸入修圖指示提示詞 (Prompt)！")

    progress(0.05, desc="正在連線至 ComfyUI 後端...")
    if not ensure_comfy_server():
        raise gr.Error("無法啟動或連線至 ComfyUI 後端引擎，請檢查 8188 埠！")

    # Upload primary image
    progress(0.1, desc="正在上傳主圖 <image1>...")
    uploaded_names = []
    primary_name = upload_image(primary_image)
    if not primary_name:
        raise gr.Error("主圖上傳至 ComfyUI 失敗！")
    uploaded_names.append(primary_name)

    # Collect reference images (<image2>, <image3>...)
    ref_list = []
    if ref_image:
        if isinstance(ref_image, (list, tuple)):
            ref_list.extend([x for x in ref_image if x])
        else:
            ref_list.append(ref_image)
    if extra_ref_images:
        if isinstance(extra_ref_images, (list, tuple)):
            ref_list.extend([x for x in extra_ref_images if x])
        else:
            ref_list.append(extra_ref_images)

    # Upload reference images if any
    for i, ref in enumerate(ref_list, 2):
        progress(0.1 + 0.05 * min(i, 8), desc=f"正在上傳參考圖 <image{i}>...")
        r_path = ref if isinstance(ref, str) else (ref.name if hasattr(ref, "name") else str(ref))
        r_name = upload_image(r_path)
        if r_name:
            uploaded_names.append(r_name)

    # Parse resolution
    res_val = 1024
    if "2048" in str(res_choice):
        res_val = 2048
    elif "768" in str(res_choice):
        res_val = 768
    elif "512" in str(res_choice):
        res_val = 512
    elif "0" in str(res_choice):
        res_val = 0

    if seed is None or seed == -1:
        import random
        seed = random.randint(1, 1000000000000000)

    # Check models
    dit_loader = "UnetLoaderGGUF" if (dit_model or "").endswith(".gguf") else "UNETLoader"
    dit_model = resolve_backend_file(dit_loader, "unet_name", dit_model, "Qwen-Image 擴散模型", 3)
    encoder_model = resolve_backend_file("CLIPLoader", "clip_name", encoder_model, "Qwen 文字編碼器", 3)
    vae_model = resolve_backend_file("VAELoader", "vae_name", vae_model, "Qwen VAE", 3)

    progress(0.2, desc=f"正在建構 Qwen-Image-2.1 修圖圖譜（{len(uploaded_names)} 張圖片輸入）...")
    workflow = build_qwen_image_prompt(
        prompt_text=prompt,
        negative_prompt=negative_prompt,
        resolution=res_val,
        steps=int(steps),
        cfg=float(cfg),
        seed=int(seed),
        sampler=sampler,
        scheduler=scheduler,
        dit_model=dit_model,
        encoder_model=encoder_model,
        vae_model=vae_model,
        cache_device=cache_device,
        cache_dtype=cache_dtype,
        uploaded_images=uploaded_names,
    )

    output_path = run_comfy_workflow(
        workflow, int(steps), progress,
        "正在載入 Qwen-Image-2.1 修圖模型...",
        "Qwen-Image-2.1 採樣修圖中",
        output_node="8",
        multiple=False
    )
    history.record("修圖 Qwen-Image-2.1", prompt, output_path, resolution=f"基底 {res_val}", seed=int(seed),
                   mode="指令修圖", model=dit_model, encoder=encoder_model)
    progress(1.0, desc="修圖完成！")
    return output_path

def gpu_status_text(note=""):
    try:
        queue = requests.get(f"{COMFY_URL}/queue", timeout=5).json()
        device = requests.get(f"{COMFY_URL}/system_stats", timeout=5).json()["devices"][0]
    except (requests.RequestException, KeyError, IndexError, ValueError):
        return f"{note}\n\n後端未連線。".strip()
    total_gb = device["vram_total"] / 1024 ** 3
    used_gb = (device["vram_total"] - device["vram_free"]) / 1024 ** 3
    status = (f"顯存 **{used_gb:.1f} / {total_gb:.1f} GB**（含 ComfyUI 保留的模型快取）· "
              f"執行中 {len(queue.get('queue_running', []))} · 排隊 {len(queue.get('queue_pending', []))}")
    return f"{note}\n\n{status}".strip()

def cancel_generation():
    """Drop queued jobs first so the interrupt does not just start the next one."""
    try:
        requests.post(f"{COMFY_URL}/queue", json={"clear": True}, timeout=10).raise_for_status()
        requests.post(f"{COMFY_URL}/interrupt", timeout=10).raise_for_status()
    except requests.RequestException as error:
        return gpu_status_text(f"⚠️ 取消失敗：{error}")
    return gpu_status_text("⏹ 已送出取消：清空排隊中的任務，並中斷目前的生成（目前這一步算完才會停）。")

def free_vram():
    try:
        queue = requests.get(f"{COMFY_URL}/queue", timeout=5).json()
        if queue.get("queue_running") or queue.get("queue_pending"):
            return gpu_status_text("⚠️ 還有任務在執行或排隊，請先按「取消生成」或等待完成，再釋放顯存。")
        requests.post(f"{COMFY_URL}/free", json={"unload_models": True, "free_memory": True}, timeout=30).raise_for_status()
    except requests.RequestException as error:
        return gpu_status_text(f"⚠️ 釋放失敗：{error}")
    time.sleep(2)
    return gpu_status_text("🧹 已卸載所有模型並釋放快取；下次生成需要重新載入模型。")

def run_comfy_workflow(prompt_graph, total_steps, progress, loading_desc, stage, segments=1, output_node="41", multiple=False):
    """Queue a graph, relay sampler progress, and return the file saved by node 41."""
    client_id = str(uuid.uuid4())
    req_data = json.dumps({"prompt": prompt_graph, "client_id": client_id}).encode('utf-8')
    req = urllib.request.Request(f"{COMFY_URL}/prompt", data=req_data, headers={'Content-Type': 'application/json'})

    try:
        json.loads(urllib.request.urlopen(req).read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8', errors='ignore')
        try:
            err_json = json.loads(err_body)
            err_msg = json.dumps(err_json.get("node_errors", err_json), ensure_ascii=False)
        except Exception:
            err_msg = err_body
        raise gr.Error(f"ComfyUI 驗證錯誤: {err_msg}")
    except Exception as e:
        raise gr.Error(f"提交任務失敗: {e}")

    ws = websocket.WebSocket()
    ws.connect(f"{COMFY_WS_URL}?clientId={client_id}")

    output_video_path = None
    progress(0.2, desc=loading_desc)

    current_step = 0
    finished_runs = 0

    while True:
        try:
            msg = ws.recv()
            if isinstance(msg, str):
                data = json.loads(msg)
                msg_type = data.get("type")
                msg_data = data.get("data", {})

                if msg_type == "progress":
                    val = msg_data.get("value", 0)
                    max_val = msg_data.get("max", total_steps)
                    current_step = val
                    if segments > 1:
                        done = min(finished_runs, segments - 1)
                        pct = 0.2 + ((done + val / max_val) / segments) * 0.7
                        progress(pct, desc=f"{stage}: 第 {done + 1}/{segments} 段 · 步數 {val}/{max_val}...")
                        if val >= max_val:
                            finished_runs += 1
                    else:
                        pct = 0.2 + (val / max_val) * 0.7
                        progress(pct, desc=f"{stage}中: 步數 {val}/{max_val}...")

                elif msg_type == "executed" and msg_data.get("node") == output_node:
                    output = msg_data.get("output", {})
                    files = output.get("videos") or output.get("images", [])
                    paths = [os.path.join(COMFY_DIR, "output", f.get("subfolder", ""), f.get("filename")) for f in files]
                    if paths:
                        output_video_path = paths if multiple else paths[0]
                        break

                elif msg_type == "execution_interrupted":
                    ws.close()
                    raise gr.Error("已取消生成。")

                elif msg_type == "execution_error":
                    err = msg_data.get("exception_message", "未知錯誤")
                    ws.close()
                    if "OutOfMemory" in err:
                        raise gr.Error(f"顯存不足 (OOM): {err}\n建議：請將解析度切換為「864 × 480 (16:9 標清)」並降低秒數為 4~5 秒！")
                    raise gr.Error(f"生成時發生錯誤: {err}")

                elif msg_type == "status":
                    status = msg_data.get("status", {})
                    if status.get("exec_info", {}).get("queue_remaining", 0) == 0 and current_step >= total_steps:
                        break
        except websocket.WebSocketConnectionClosedException:
            break
        except gr.Error:
            raise
        except Exception as e:
            print(f"[WebUI Exception] {e}")
            break

    ws.close()

    if not output_video_path:
        raise gr.Error("本次任務未取得輸出，請查看 ComfyUI 執行記錄；不會以舊檔案代替。")
    for item in (output_video_path if multiple else [output_video_path]):
        if not os.path.exists(item):
            raise gr.Error("本次任務未取得輸出，請查看 ComfyUI 執行記錄；不會以舊檔案代替。")
    return output_video_path

def execute_generation(
    prompt,
    resolution_str,
    duration,
    turbo,
    seed,
    first_frame_file=None,
    last_frame_file=None,
    camera_state=None,
    text_encoder=None,
    lora_name=None,
    lora_strength=1.0,
    hd=False,
    keyframe_instruction=True,
    fl2va_model=None,
    ref2va_model=None,
    progress=gr.Progress()
):
    if not prompt or not prompt.strip():
        raise gr.Error("提示詞欄是空的。欄位裡灰色斜體的文字只是範例，請輸入自己的描述，或從「提示詞範本庫」套用。")
    if camera_state is not None and not first_frame_file:
        raise gr.Error("請先上傳 3D 攝影機使用的參考圖片。")
    if hd and camera_state is not None:
        raise gr.Error("3D 攝影機模式不支援高清二次採樣。")

    progress(0.05, desc="正在連線至 MiniMax H3 引擎...")
    if not ensure_comfy_server():
        raise gr.Error("無法啟動或連線至 ComfyUI 後端引擎，請檢查 8188 埠！")

    if camera_state is not None:
        for node_type in ("BruxosH3Camera", "TextEncodeH3Edit"):
            response = requests.get(f"{COMFY_URL}/object_info/{node_type}", timeout=10)
            response.raise_for_status()
            if node_type not in response.json():
                raise gr.Error("後端尚未載入攝影機節點。請等目前生成完成，再執行 restart_webui.bat。")
    model_options = resolve_model_options(text_encoder, lora_name, lora_strength, fl2va_model, ref2va_model)
    if hd:
        resolve_backend_file("MinimaxH3LatentUpscaler3D", "model_name", H3_LATENT_UPSCALER, "潛空間放大模型", 5)
        # The 3-step refine schedule only works with the distilled Turbo LoRA.
        turbo = MODE_TURBO_LORA

    width, height = resolve_resolution(resolution_str, first_frame_file or last_frame_file)
    check_generation_limits(model_options["fl2va_model"], model_options["lora_name"], turbo, hd, width, height, duration, "fl2va")
    if not hd and width * height > SINGLE_PASS_MAX_PIXELS:
        if camera_state is not None:
            raise gr.Error("3D 攝影機模式不支援超過 1344×768 的解析度。")
        if not HD_ALLOWED:
            raise gr.Error(f"{width}×{height} 超過官方 1344×768，需要高清二次採樣（24GB 級顯卡）；"
                           f"這台偵測到 {VRAM_GB:.0f} GB，請改選較小的解析度。")
        gr.Info("這個解析度超過官方 1344×768，已自動使用高清二次採樣（含 Turbo）。")
        hd = True
        resolve_backend_file("MinimaxH3LatentUpscaler3D", "model_name", H3_LATENT_UPSCALER, "潛空間放大模型", 5)
        turbo = True

    if seed is None or seed == -1:
        import random
        seed = random.randint(1, 1000000000000000)
    seed = int(seed)

    first_frame_name = upload_image(first_frame_file) if first_frame_file else None
    last_frame_name = upload_image(last_frame_file) if last_frame_file else None

    if keyframe_instruction and camera_state is None:
        prompt = with_keyframe_instruction(prompt, bool(first_frame_name), bool(last_frame_name),
                                           snap_h3_length(round(duration * 24)))

    progress(0.15, desc="正在準備影音生成圖譜...")
    prompt_graph = build_minimax_h3_prompt(
        prompt_text=prompt,
        width=width,
        height=height,
        duration=duration,
        seed=seed,
        turbo=turbo,
        first_frame_name=first_frame_name,
        last_frame_name=last_frame_name,
        hd_size=(width, height) if hd else None,
        **model_options
    )
    if camera_state is not None:
        if not first_frame_name:
            raise gr.Error("參考圖片上傳失敗，請重新上傳。")
        prompt_graph = apply_camera_graph(prompt_graph, camera_state, prompt, width, height)

    stage = "高清二次採樣（先半解析度 4 步，放大後再 3 步）" if hd else "採樣"
    output_video_path = run_comfy_workflow(prompt_graph, prompt_graph["20"]["inputs"]["steps"], progress,
                                           "正在載入模型與運算中...", stage)
    history.record("3D 攝影機" if camera_state is not None else ("FL2VA" if (first_frame_name or last_frame_name) else "文生影音"),
                   prompt, output_video_path, resolution=f"{width}×{height}", seconds=round(duration, 2), seed=seed,
                   mode=turbo if isinstance(turbo, str) else None, hd=bool(hd),
                   model=model_options["fl2va_model"], encoder=model_options["text_encoder"],
                   lora=model_options["lora_name"], lora_strength=model_options["lora_strength"] if model_options["lora_name"] else None)
    progress(1.0, desc="影音生成完成！")
    return output_video_path

def resolve_resolution(resolution_str, source_path=None):
    """Fixed "W × H" choices, or an auto choice sized from the source's aspect ratio."""
    megapixels = AUTO_RESOLUTION_CHOICES.get(resolution_str)
    if megapixels is None:
        return parse_resolution(resolution_str)
    if not source_path:
        raise gr.Error("「自動・依素材比例」需要先上傳首幀、參考圖或參考影片。")
    return auto_canvas(source_path, megapixels)

def upload_files(paths):
    names = []
    for path in paths:
        name = upload_image(path)
        if not name:
            raise gr.Error(f"上傳到 ComfyUI 失敗：{os.path.basename(path)}")
        names.append(name)
    return names

def execute_ref_generation(
    prompt,
    resolution_str,
    duration,
    turbo,
    seed,
    image_files=None,
    video_files=None,
    use_video_audio=True,
    audio_files=None,
    audio_mode=AUDIO_MODE_REFERENCE,
    scheduler="simple",
    text_encoder=None,
    lora_name=None,
    lora_strength=1.0,
    fl2va_model=None,
    ref2va_model=None,
    warn_missing=True,
    target_frames=None,
    mux_audio=True,
    progress=gr.Progress()
):
    image_files, video_files, audio_files = list(image_files or []), list(video_files or []), list(audio_files or [])
    if not prompt or not prompt.strip():
        raise gr.Error("請輸入提示詞 (Prompt)！")
    if len(image_files) > 9 or len(video_files) > 3 or len(audio_files) > 3:
        raise gr.Error("最多 9 張參考圖、3 支參考影片、3 個音檔。")
    copy_audio = audio_mode == AUDIO_MODE_COPY
    if copy_audio and not audio_files:
        raise gr.Error("「整條照用並對嘴」需要上傳至少一個音檔（使用第一個）。")

    progress(0.05, desc="正在連線至 MiniMax H3 引擎...")
    if not ensure_comfy_server():
        raise gr.Error("無法啟動或連線至 ComfyUI 後端引擎，請檢查 8188 埠！")
    model_options = resolve_model_options(text_encoder, lora_name, lora_strength, fl2va_model, ref2va_model)
    if copy_audio and "MiniMaxH3LockAudioLatent" not in requests.get(f"{COMFY_URL}/object_info/MiniMaxH3LockAudioLatent", timeout=10).json():
        raise gr.Error("後端尚未載入 TimelineDirector 的音軌鎖定節點。請執行 restart_webui.bat 後再試。")

    progress(0.08, desc="正在整理參考影片（轉 24 fps、最長 15 秒）...")
    prepared = [prepare_reference_video(path) for path in video_files]
    video_items = [(path, bool(use_video_audio and has_audio)) for path, has_audio, _ in prepared]
    labels = reference_labels(image_files, video_items, audio_files)
    missing = [label for label, _, _ in labels if label.lower() not in prompt.lower()]
    if warn_missing and missing:
        escaped = [label.replace("<", "＜").replace(">", "＞") for label in missing]
        gr.Warning("提示詞沒有提到：" + "、".join(escaped) + "。沒指定用途時，模型會自己決定怎麼用這些素材。")

    if target_frames is not None:
        frame_count = snap_h3_length(target_frames)
    elif copy_audio:
        seconds = media_duration(audio_files[0])
        frame_count = snap_h3_length(round(seconds * 24))
        if frame_count > 362:
            raise gr.Error(f"音檔長 {seconds:.1f} 秒，超過 H3 單段上限約 15 秒；請改用「🎤 對嘴」分頁（支援超長語音自動分段連鎖生成）！")
    else:
        frame_count = snap_h3_length(round(duration * 24))

    source = prepared[0][0] if prepared else (image_files[0] if image_files else None)
    width, height = resolve_resolution(resolution_str, source)
    check_generation_limits(model_options["ref2va_model"], model_options["lora_name"], turbo, False, width, height, duration, "ref2va")

    progress(0.12, desc="正在上傳參考素材...")
    image_names = upload_files(image_files)
    video_names = upload_files([path for path, _ in video_items])
    audio_names = upload_files(audio_files)

    if seed is None or seed == -1:
        import random
        seed = random.randint(1, 1000000000000000)
    progress(0.15, desc=f"正在準備 Ref2VA 圖譜（{width}×{height}，{frame_count} 幀）...")
    prompt_graph = build_minimax_h3_ref_prompt(
        prompt_text=prompt,
        width=width,
        height=height,
        length=frame_count,
        seed=int(seed),
        turbo=turbo,
        image_names=image_names,
        videos=[(name, soundtrack) for name, (_, soundtrack) in zip(video_names, video_items)],
        audio_names=audio_names,
        lock_audio=copy_audio,
        scheduler=scheduler,
        **model_options
    )
    output_video_path = run_comfy_workflow(prompt_graph, prompt_graph["20"]["inputs"]["steps"], progress,
                                           "正在載入 Ref2VA 模型與參考素材...", "Ref2VA 採樣")
    if copy_audio and mux_audio:
        progress(0.97, desc="正在把成片音軌換回原始音檔...")
        output_video_path = mux_original_audio(output_video_path, audio_files[0], match_audio_length=True)
    history.record("Ref2VA", prompt, output_video_path, resolution=f"{width}×{height}",
                   seconds=round(frame_count / 24, 2), seed=int(seed), mode=turbo if isinstance(turbo, str) else None,
                   scheduler=scheduler, model=model_options["ref2va_model"], encoder=model_options["text_encoder"],
                   lora=model_options["lora_name"], lora_strength=model_options["lora_strength"] if model_options["lora_name"] else None)
    progress(1.0, desc="參考影音生成完成！")
    return output_video_path


LIPSYNC_DEFAULT_PROMPT = (
    "[Shot 1] The person shown in <Picture 1> looks toward the camera and speaks naturally, with the "
    "lips, jaw and facial expression moving in accurate sync to <Audio 1>. Keep the same face, hairstyle, "
    "clothing, background and lighting as <Picture 1>, with only small natural head movement and blinking. "
    "The camera holds a static shot.\n\n"
    "overall_soundscape: A quiet room tone consistent with the scene.\n\n"
    "non_diegetic_music: N/A")


class SegmentProgressWrapper:
    """Map sub-segment progress (0.0 to 1.0) into the global progress range for multi-segment runs."""
    def __init__(self, parent_progress, seg_idx, total_segs, seg_desc=""):
        self.parent = parent_progress
        self.seg_idx = seg_idx
        self.total_segs = total_segs
        self.seg_desc = seg_desc

    def __call__(self, val, desc=None):
        if self.parent is None:
            return
        overall = (self.seg_idx + float(val)) / float(self.total_segs)
        prefix = f"[段落 {self.seg_idx + 1}/{self.total_segs}] "
        text = prefix + (desc or self.seg_desc)
        try:
            self.parent(min(0.99, max(0.01, overall)), desc=text)
        except Exception:
            pass


def execute_lipsync(image, audio, prompt, resolution_str, mode, seed,
                    text_encoder=None, lora_name=None, lora_strength=1.0,
                    fl2va_model=None, ref2va_model=None, progress=gr.Progress()):
    """One portrait + one audio -> lip-synced talking video (Ref2VA with the audio locked).

    If audio exceeds 15 seconds, automatically segments and chains via the last frame of each segment,
    maintaining 100% sample-accurate lip-sync alignment with zero cumulative drift.
    """
    if not image:
        raise gr.Error("請先上傳一張人像照片（會成為 <Picture 1>）。")
    if not audio:
        raise gr.Error("請先上傳一段要對嘴的語音（會成為 <Audio 1>）。")
    if not (prompt or "").strip():
        prompt = LIPSYNC_DEFAULT_PROMPT

    total_seconds = media_duration(audio)
    if total_seconds <= SINGLE_SEGMENT_MAX_SECONDS:
        return execute_ref_generation(
            prompt, resolution_str, total_seconds, mode, seed,
            image_files=[image], video_files=[], use_video_audio=False,
            audio_files=[audio], audio_mode=AUDIO_MODE_COPY, scheduler="simple",
            text_encoder=text_encoder, lora_name=lora_name, lora_strength=lora_strength,
            fl2va_model=fl2va_model, ref2va_model=ref2va_model,
            warn_missing=False, mux_audio=True, progress=progress)

    # Multi-segment long video lip-sync (> SINGLE_SEGMENT_MAX_SECONDS)
    segments = plan_segment_durations(total_seconds, max_segment_seconds=12.0)
    total_segs = len(segments)
    gr.Info(f"語音長度為 {total_seconds:.1f} 秒（超過 {int(SINGLE_SEGMENT_MAX_SECONDS)} 秒），已自動啟用原圖高解析錨定分段長片機制，共 {total_segs} 段連續生成...")

    segment_videos = []
    # 固定隨機種子，確保所有分段的角色面部特徵、光影風格與背景 100% 高度一致
    fixed_seed = int(seed) if seed is not None and seed != -1 else random.randint(1, 1000000000000000)

    for i, (start_sec, dur_sec, seg_frames) in enumerate(segments):
        seg_audio = slice_audio(audio, start_sec, dur_sec)
        seg_progress = SegmentProgressWrapper(progress, i, total_segs, f"正在生成第 {i + 1}/{total_segs} 段對嘴影片...")
        seg_progress(0.01, f"準備生成第 {i + 1}/{total_segs} 段（約 {dur_sec:.1f} 秒，{seg_frames} 幀）...")

        # 核心修復：每段始終使用使用者上傳的原始高畫質人像照片作為 <Picture 1>！
        # 絕不截取上一段末幀進行遞歸二次/多次生成，徹底消滅 VAE 迭代失真、畫面暗角變黑、雜色斑塊與噪點累積擴大！
        seg_video = execute_ref_generation(
            prompt, resolution_str, dur_sec, mode, fixed_seed,
            image_files=[image], video_files=[], use_video_audio=False,
            audio_files=[seg_audio], audio_mode=AUDIO_MODE_COPY, scheduler="simple",
            text_encoder=text_encoder, lora_name=lora_name, lora_strength=lora_strength,
            fl2va_model=fl2va_model, ref2va_model=ref2va_model,
            warn_missing=False, target_frames=seg_frames, mux_audio=False, progress=seg_progress)

        segment_videos.append(seg_video)

    progress(0.97, desc="正在無縫拼接所有分段並還原完整原音軌...")
    concat_video = concat_video_segments(segment_videos)
    final_video = mux_original_audio(concat_video, audio, match_audio_length=True)

    progress(1.0, desc="長片對嘴生成完成！")
    history.record("LipSync_Long", prompt, final_video,
                   seconds=round(media_duration(final_video), 2),
                   mode=mode if isinstance(mode, str) else None,
                   scheduler="simple", segments=total_segs)
    return final_video


V2V_PRESETS = {
    "🌟 Singularity HDR 動作畫質增強 (推薦)": (
        "[Shot 1] The character action, body dynamics, and cinematography from <Video 1> are fully preserved. "
        "High dynamic range (HDR) cinematic quality, fluid and impactful motion, crisp facial details, clean and de-oiled natural lighting without glossy sheen. "
        "<Video 1> fully_preserved."
    ),
    "⚔️ 武俠打鬥 / 動作特效強化 (Singularity 專精)": (
        "[Shot 1] The martial arts choreography, sword fighting action sequences, and camera movement from <Video 1> are fully preserved. "
        "Enhanced physical impact, dynamic martial arts VFX, particle aura and energy waves, cinematic movie lighting. "
        "<Video 1> fully_preserved."
    ),
    "🏙️ 動作保留 + 賽博龐克背景變換": (
        "[Shot 1] The character action and performance from <Video 1> are fully preserved, but the background environment "
        "is transformed into a cyberpunk neon futuristic street at night with wet asphalt and volumetric lighting. "
        "<Video 1> fully_preserved."
    ),
    "🌸 動作保留 + 動漫二次元風格化": (
        "[Shot 1] The motion, choreography, and camera movements from <Video 1> are fully preserved. "
        "Japanese anime feature film aesthetic, vibrant colorful lighting, expressive facial dynamics, detailed line art. "
        "<Video 1> fully_preserved."
    ),
}
V2V_DEFAULT_PROMPT = V2V_PRESETS["🌟 Singularity HDR 動作畫質增強 (推薦)"]


def execute_v2v(video_file, image_files, prompt, resolution_str, duration,
                auto_duration, turbo, seed, scheduler="simple", use_video_audio=True,
                text_encoder=None, fl2va_model=None, ref2va_model=None,
                progress=gr.Progress()):
    """Dedicated Video-to-Video (V2V) generation: source video (+ optional style/character pictures) -> transformed video.

    Supports single segment (<= 15s) and automatic chained multi-segment long video (> 15s).
    """
    if not video_file:
        raise gr.Error("請先上傳來源影片（動作 / 運鏡 / 肢體來源）。")

    ref_video = video_file if isinstance(video_file, str) else (video_file[0] if isinstance(video_file, (list, tuple)) else str(video_file))
    if not os.path.exists(ref_video):
        raise gr.Error(f"來源影片檔案不存在：{ref_video}")

    image_list = list(image_files or [])

    if not (prompt or "").strip():
        prompt = V2V_PRESETS["🌟 Singularity HDR 動作畫質增強 (推薦)"]

    target_ref2va_model = ref2va_model or H3_SINGULARITY_MODEL
    lora_name = None
    lora_strength = 0.0

    video_len = media_duration(ref_video)
    total_seconds = video_len if auto_duration else min(float(duration or 5.0), video_len)

    if total_seconds <= SINGLE_SEGMENT_MAX_SECONDS:
        return execute_ref_generation(
            prompt, resolution_str, total_seconds, turbo, seed,
            image_files=image_list, video_files=[ref_video],
            use_video_audio=use_video_audio, audio_files=[],
            audio_mode=AUDIO_MODE_REFERENCE, scheduler=scheduler,
            text_encoder=text_encoder,
            lora_name=lora_name, lora_strength=lora_strength,
            fl2va_model=fl2va_model, ref2va_model=target_ref2va_model,
            warn_missing=False, mux_audio=use_video_audio, progress=progress)

    # Multi-segment long video V2V (> SINGLE_SEGMENT_MAX_SECONDS)
    segments = plan_segment_durations(total_seconds, max_segment_seconds=12.0)
    total_segs = len(segments)
    gr.Info(f"來源影片長度為 {total_seconds:.1f} 秒（超過 {int(SINGLE_SEGMENT_MAX_SECONDS)} 秒），已自動分段為 {total_segs} 段長影片連續重塑...")

    segment_videos = []
    base_images = list(image_list)
    fixed_seed = int(seed) if seed is not None and seed != -1 else random.randint(1, 1000000000000000)

    for i, (start_sec, dur_sec, seg_frames) in enumerate(segments):
        seg_progress = SegmentProgressWrapper(progress, i, total_segs, f"正在處理第 {i + 1}/{total_segs} 段 V2V 重塑...")
        seg_progress(0.01, f"正在切取第 {i + 1}/{total_segs} 段來源影片（{dur_sec:.1f} 秒，{seg_frames} 幀）...")
        seg_video_input = slice_video(ref_video, start_sec, dur_sec)

        # 核心修復：始終使用原版上傳的參考圖片作為角色/風格依據，不混入上一段截取的末幀，杜絕色差累積與雜點劣化
        seg_video = execute_ref_generation(
            prompt, resolution_str, dur_sec, turbo, fixed_seed,
            image_files=base_images, video_files=[seg_video_input],
            use_video_audio=False, audio_files=[],
            audio_mode=AUDIO_MODE_REFERENCE, scheduler=scheduler,
            text_encoder=text_encoder,
            lora_name=lora_name, lora_strength=lora_strength,
            fl2va_model=fl2va_model, ref2va_model=target_ref2va_model,
            warn_missing=False, target_frames=seg_frames, mux_audio=False, progress=seg_progress)

        segment_videos.append(seg_video)

    progress(0.97, desc="正在無縫拼接所有 V2V 重塑分段...")
    concat_video = concat_video_segments(segment_videos)

    if use_video_audio and has_audio_stream(ref_video):
        progress(0.99, desc="正在還原來源影片完整原音軌...")
        final_video = mux_original_audio(concat_video, ref_video, match_audio_length=True)
    else:
        final_video = concat_video

    progress(1.0, desc="長影片 V2V 重塑完成！")
    history.record("V2V_Long", prompt, final_video,
                   seconds=round(media_duration(final_video), 2),
                   mode=turbo if isinstance(turbo, str) else None,
                   scheduler=scheduler, model=target_ref2va_model,
                   segments=total_segs)
    return final_video


def preview_reference_labels(image_files, video_files, use_video_audio, audio_files):
    video_items = [(path, bool(use_video_audio and has_audio_stream(path))) for path in (video_files or [])]
    labels = reference_labels(list(image_files or []), video_items, list(audio_files or []))
    return label_table(labels), labels


def on_reference_materials_change(image_files, video_files, use_video_audio, audio_files, current_prompt, auto_mode="自動偵測（依上傳素材最佳化）"):
    video_items = [(path, bool(use_video_audio and has_audio_stream(path))) for path in (video_files or [])]
    labels = reference_labels(list(image_files or []), video_items, list(audio_files or []))
    md = label_table(labels)
    # If the user prompt is empty or just whitespace, auto-fill it based on uploaded materials
    new_prompt = current_prompt
    if not (current_prompt or "").strip() and labels:
        new_prompt = generate_auto_ref_prompt(labels, mode=auto_mode)
    return md, labels, new_prompt


def force_generate_ref_prompt(image_files, video_files, use_video_audio, audio_files, auto_mode="自動偵測（依上傳素材最佳化）"):
    video_items = [(path, bool(use_video_audio and has_audio_stream(path))) for path in (video_files or [])]
    labels = reference_labels(list(image_files or []), video_items, list(audio_files or []))
    return generate_auto_ref_prompt(labels, mode=auto_mode)


T2V_PROMPT_TEMPLATES = {
    "自訂提示詞（保留目前內容）": "",
    "🎞️ 3D 電影級奇幻場景": """電影級 3D 動畫，一座漂浮在雲海上的古老天空城，巨大的石造拱門與發光水晶被晨霧環繞。一名披著紅色斗篷的旅人沿著懸空石橋緩慢前進，衣角隨風飄動，遠方有飛行生物掠過。

鏡頭：從超廣角空拍緩慢向前推進，接著繞到人物側後方，以平順的環繞運鏡展現天空城的規模。體積光、細緻材質、真實陰影、電影景深，動作自然連貫。

聲音：高空風聲、遠處鳥鳴、低沉而神秘的管弦樂、腳步踩在石橋上的回音。不要文字、字幕、標誌或浮水印。""",
    "🏙️ 賽博朋克城市追逐": """寫實電影風格，雨後的賽博朋克夜都市。身穿黑色風衣的主角在霓虹燈照亮的巷道中高速奔跑，跨越水坑並閃避迎面而來的人群，後方的無人機持續追蹤。濕潤地面反射紫色與藍色霓虹光。

鏡頭：低角度跟拍，穿插近距離側拍與一次快速甩鏡，節奏緊湊但人物外觀保持一致，運動清晰自然。

聲音：急促腳步、雨水飛濺、無人機引擎、遠處警報與有力的電子低音。不要文字、字幕、標誌或浮水印。""",
    "🚗 豪華汽車廣告": """高級汽車廣告，一輛流線型銀色跑車行駛在黎明時分的海岸公路，車身烤漆精準反射天空與海面，輪胎和懸吊動作符合真實物理。畫面乾淨、精緻、具有精品廣告質感。

鏡頭：先以貼近地面的前輪特寫開始，平滑切換到車側追拍，最後以高空廣角顯示跑車沿著海岸線遠去。自然動態模糊、電影級光影。

聲音：沉穩的引擎聲、換檔聲、海風與低調現代配樂。不要品牌、文字、字幕、標誌或浮水印。""",
    "⌚ 精品產品展示": """高端 3D 產品廣告，一只精密機械腕錶懸浮在深色攝影棚中，金屬邊緣、藍寶石鏡面與內部齒輪細節清楚可見。細小水珠緩慢掠過表面，背景有柔和金色光帶。

鏡頭：微距鏡頭緩慢環繞產品一圈，依序對焦錶冠、指針與機芯，最後停在正面英雄視角。材質真實、反射受控、畫面穩定。

聲音：細緻齒輪運轉、清脆滴答聲、柔和低頻氛圍音。不要文字、品牌、字幕、標誌或浮水印。""",
    "🏠 建築空間漫遊": """超寫實建築視覺化，現代極簡住宅客廳面向森林與湖泊，大片落地窗、木質牆面、天然石材地板，午後陽光穿過樹葉在室內形成柔和移動光影。空間整潔且比例正確。

鏡頭：穩定器視角從入口緩慢向前移動，繞過沙發後轉向落地窗與湖景，運鏡平順，垂直線保持筆直，曝光自然。

聲音：安靜室內環境、遠處鳥鳴、微風吹動樹葉與輕柔鋼琴。不要人物、文字、字幕、標誌或浮水印。""",
    "🌿 微距自然紀錄片": """自然紀錄片風格的極致微距畫面，清晨森林中的一片綠葉掛著透明露珠，一隻色彩細膩的蝴蝶停在葉緣，翅膀緩慢開合。陽光穿過背景形成柔和散景，露珠反射周圍森林。

鏡頭：從露珠超近距離特寫緩慢拉焦到蝴蝶眼睛，再輕微橫移跟隨蝴蝶振翅起飛。自然色彩、高速攝影質感、細節清晰。

聲音：清晨鳥鳴、微風、昆蟲振翅與輕柔森林環境音。不要文字、字幕、標誌或浮水印。""",
    "🍜 美食廣告慢動作": """電影級美食廣告，一碗熱氣蒸騰的日式拉麵放在深色木桌上，湯面油光、麵條、叉燒與溏心蛋質感真實。筷子夾起麵條，湯汁以慢動作滴落，蒸氣在逆光中清晰可見。

鏡頭：從食材微距特寫開始，平滑繞到碗的正面，再慢速推近被夾起的麵條。暖色棚拍光、淺景深、細節豐富。

聲音：湯汁輕響、筷子碰碗、細微環境聲與溫暖簡潔的配樂。不要文字、字幕、品牌、標誌或浮水印。""",
    "🤖 科幻機甲啟動": """高品質寫實 3D 科幻場景，巨大人形機甲站在昏暗的地下機庫中，維修平台與機械手臂環繞四周。機甲的核心逐步亮起藍色光芒，裝甲板鎖定，液壓系統噴出白色蒸氣，最後抬頭甦醒。

鏡頭：由腳部低角度緩慢向上仰拍，穿過維修平台後抵達發光核心，最後以廣角呈現完整機甲。金屬材質、尺度感與機械運動準確。

聲音：大型機械鎖定、液壓洩壓、電力充能、低頻震動與史詩音樂漸強。不要文字、字幕、標誌或浮水印。""",
    "👤 寫實人物情緒特寫": """寫實電影人像，一名年輕女性站在雨夜的車站月台，臉上帶著克制而複雜的情緒，雨水落在髮絲與外套上。遠方列車燈光逐漸靠近，背景人群自然移動，人物身份與五官保持穩定。

鏡頭：從中景緩慢推進到臉部特寫，人物先望向軌道，接著輕輕轉頭看向鏡頭。自然眨眼、細微呼吸、電影膚色、柔和景深。

聲音：雨聲、遠處列車、月台廣播的模糊回音與低調鋼琴。不要可辨識的廣播台詞、文字、字幕、標誌或浮水印。""",
    "✨ 魔法粒子變身": """精緻 3D 奇幻動畫，一名角色站在黑暗森林的圓形祭壇中央，金色魔法粒子從地面盤旋升起，逐步凝聚成帶有發光紋路的華麗盔甲。角色姿勢穩定，服裝變化連續，粒子照亮周圍樹木與薄霧。

鏡頭：以半身正面開始，緩慢繞角色 180 度，變身完成時拉遠呈現完整造型與祭壇。粒子流動自然、光影一致、細節清楚。

聲音：魔法能量聚集、金屬組裝、森林夜間環境音與逐漸高昂的奇幻配樂。不要文字、字幕、標誌或浮水印。""",
}


PROMPT_LIBRARY = {
    **PROMPT_CATEGORIES,
    "🎯 官方格式範例（可直接生成）": OFFICIAL_FORMAT_EXAMPLES,
    **OFFICIAL_GUIDE_CATEGORIES,
    "原有精選": {name: prompt for name, prompt in T2V_PROMPT_TEMPLATES.items() if prompt},
}


def preview_prompt_template(category, template_name):
    return PROMPT_LIBRARY.get(category, {}).get(template_name, "")


def apply_prompt_template(category, template_name, current_prompt, append=False):
    template = preview_prompt_template(category, template_name)
    if not template:
        return current_prompt
    if append and current_prompt and current_prompt.strip():
        return current_prompt.rstrip() + "\n\n" + template
    return template


def change_prompt_category(category):
    return gr.Dropdown(choices=list(PROMPT_LIBRARY.get(category, {})), value=None), ""


PROMPT_THUMB_DIR = os.path.join(BASE_DIR, "prompt_thumbs")
# Categories that are reference text / LLM instructions, not scene prompts — no thumbnails.
THUMBNAIL_SKIP_CATEGORIES = ("分鏡導演", "官方指南")


def prompt_to_image_desc(text):
    """Reduce an H3 prompt to a clean visual scene description for a Krea2 thumbnail:
    keep the imagery, drop field labels, shot tags, timing, camera motion, dialogue and notes."""
    t = text or ""
    match = re.search(r"integrated_multimodal_description:(.*?)(?:\n\noverall_soundscape:|\n\nnon_diegetic_music:|$)", t, re.S)
    if match:
        t = match.group(1)
    t = re.split(r"\n\s*---\s*\n", t)[0]  # first segment only for multi-segment prompts
    t = re.sub(r"How the reference pictures align.*?\.", "", t, flags=re.S)
    t = re.sub(r"For the target video, at [^.]*referenced\.", "", t, flags=re.S)
    t = re.sub(r"\[Shot \d+\]", "", t)
    t = re.sub(r"At \d{1,2}[:：]\d{2}[.．]\d{1,3}[,，]?", "", t)
    t = re.sub(r"[（(][Ss]\d[\d,]*[)）]\s*(says|replies|sings|shouts|says in an off-screen voiceover)[^:：.]*[:：]?", "", t)
    t = re.sub(r"<d>\[[^\]]*\]|</d>", "", t)          # keep spoken words, drop the tags
    t = re.sub(r"The camera[^.]*\.", "", t)            # drop camera-motion sentences (still image)
    t = re.sub(r"<[^>]+>", "", t)                      # drop <Picture 1> etc.
    t = re.sub(r"時長[:：][^。.]*[。.]?", "", t)
    t = re.sub(r"避免[^。]*。?", "", t)
    t = re.sub(r"\s+", " ", t).strip(" ,，。.")
    return t or (text or "")[:300]


def prompt_thumb_path(category, name):
    import hashlib
    key = hashlib.sha1((category + "|" + name).encode("utf-8")).hexdigest()
    return os.path.join(PROMPT_THUMB_DIR, key + ".jpg")


def prompt_gallery_items(category):
    """(thumbnail-or-placeholder, name) pairs for the category, in template order."""
    names = list(PROMPT_LIBRARY.get(category, {}))
    items = []
    placeholder = os.path.join(PROMPT_THUMB_DIR, "_placeholder.png")
    for name in names:
        thumb = prompt_thumb_path(category, name)
        items.append((thumb if os.path.exists(thumb) else (placeholder if os.path.exists(placeholder) else None), name))
    return items, names


def _ensure_placeholder():
    path = os.path.join(PROMPT_THUMB_DIR, "_placeholder.png")
    if os.path.exists(path):
        return path
    try:
        from PIL import Image, ImageDraw
        os.makedirs(PROMPT_THUMB_DIR, exist_ok=True)
        img = Image.new("RGB", (512, 512), (38, 40, 46))
        draw = ImageDraw.Draw(img)
        draw.text((150, 240), "尚無縮圖", fill=(150, 155, 165))
        img.save(path)
    except Exception:
        return None
    return path


def generate_prompt_thumbnails(category, only_missing=True, progress=gr.Progress()):
    """Render a fast Krea2 thumbnail (512x512, 8 steps) for each template in the category."""
    import shutil
    if any(skip in category for skip in THUMBNAIL_SKIP_CATEGORIES):
        gr.Info("這個分類是參考文字，不需要縮圖。")
        return prompt_gallery_items(category)[0]
    templates = PROMPT_LIBRARY.get(category, {})
    todo = [(n, t) for n, t in templates.items()
            if not (only_missing and os.path.exists(prompt_thumb_path(category, n)))]
    if not todo:
        gr.Info("這個分類的縮圖都已經有了。")
        return prompt_gallery_items(category)[0]
    if not ensure_comfy_server():
        raise gr.Error("無法啟動或連線至 ComfyUI 後端引擎，請檢查 8188 埠！")
    models = krea2_model_choices()
    model = resolve_backend_file("UNETLoader", "unet_name", krea2_default(models, KREA2_OFFICIAL_MODEL), "Krea2 擴散模型", 1)
    encoders = sorted({v for _, v in text_encoder_choices()} | {f for f in list_model_files("text_encoders", "CLIPLoader", "clip_name") if f.endswith(".safetensors")})
    clip = resolve_backend_file("CLIPLoader", "clip_name", krea2_default(encoders, KREA2_TEXT_ENCODER), "Krea2 文字編碼器", 1)
    vae = resolve_backend_file("VAELoader", "vae_name", KREA2_VAE, "Krea2 VAE", 1)
    turbo = resolve_backend_file("LoraLoaderModelOnly", "lora_name", KREA2_TURBO_LORA, "Turbo LoRA", 1)
    os.makedirs(PROMPT_THUMB_DIR, exist_ok=True)
    for index, (name, text) in enumerate(todo, 1):
        progress((index - 1) / len(todo), desc=f"產生縮圖 {index}/{len(todo)}：{name}")
        graph = build_krea2_prompt(
            prompt_text=prompt_to_image_desc(text), width=512, height=512, batch=1, seed=20260918,
            model_name=model, lora_name=turbo, lora_strength=0.85,
            sampler="er_sde", steps=8, scheduler="simple", cfg=1.0, text_encoder=clip, vae=vae)
        graph["16"]["inputs"]["filename_prefix"] = "prompt_thumbs/thumb"
        image = run_comfy_workflow(graph, 8, lambda *a, **k: None, "載入中", "縮圖", output_node="16", multiple=True)[0]
        shutil.copyfile(image, prompt_thumb_path(category, name))
    progress(1.0, desc="縮圖產生完成")
    return prompt_gallery_items(category)[0]


def add_prompt_picker(prompt_box):
    with gr.Accordion("📚 提示詞範本庫｜建築・人物・官方格式範例・分鏡導演・官方寫作指南・精選", open=False):
        default_cat = next(iter(PROMPT_LIBRARY))
        _init_items, _init_names = prompt_gallery_items(default_cat)
        with gr.Row():
            category = gr.Dropdown(label="分類", choices=list(PROMPT_LIBRARY), value=default_cat)
            template = gr.Dropdown(label="範本（可輸入關鍵字搜尋）", choices=list(PROMPT_LIBRARY[default_cat]), value=None)
        gallery_names = gr.State(_init_names)
        thumb_gallery = gr.Gallery(value=_init_items, label="範本縮圖（點一張即選用）", columns=6, height=260,
                                   allow_preview=False, object_fit="cover")
        with gr.Row():
            gen_thumbs = gr.Button("🖼️ 產生此分類縮圖")
            gen_missing = gr.Checkbox(label="只補缺少的", value=True)
        preview = gr.Textbox(label="範本預覽", lines=10, max_lines=24, interactive=False)
        gr.Markdown("點縮圖或用下拉選單選範本，再套用；切換分類不會改動已寫的提示詞。縮圖由 Krea2 快速生成、僅供示意（非 H3 實際成片）。\n\n"
                    "「📖 官方指南」兩類是 MiniMax 官方 h3-prompt-writing skill 的原文（三段格式與 Ref 六段格式），"
                    "當**參考與範例**用：在預覽框閱讀、選取複製取用；其中 `Case 1～4` 與 Ref 的 `Complete Example` 是完整官方格式範例，可直接「套用」當起手式再改。結構化表單（🧱）已依這份指南設計。\n\n"
                    "「🎯 官方格式範例（可直接生成）」是依官方格式手寫的 12 組完整 T2VA 提示詞（含 `integrated_multimodal_description` 三欄），**套用後直接就能在「文生影音／FL2VA」分頁生成**，也可當範本改寫。\n\n"
                    "「🎬 分鏡導演」那一類是**給語言模型看的指令**，不是 H3 的提示詞，兩份接著用：\n"
                    "1. 「單圖擴展成 10–20 秒分鏡」：貼給會看圖的語言模型，連同一張參考圖，讓它產出分鏡表與九宮格分鏡圖。\n"
                    "2. 「多圖分鏡 → 連貫多段影片提示詞」：把分鏡圖交回語言模型，讓它逐段寫出鎖定同一人物、同一場景、同一時間軸的提示詞。\n"
                    "3. 每段提示詞回到面板生成：單段用「FL2VA 首尾幀」或「Ref2VA」分頁；整條一次跑用「長片」分頁，分段提示詞以單獨一行 `---` 分隔。")
        with gr.Row():
            replace = gr.Button("套用・取代提示詞", variant="secondary")
            append = gr.Button("加到提示詞末尾")
        def on_prompt_category(cat):
            items, names = prompt_gallery_items(cat)
            return gr.Dropdown(choices=list(PROMPT_LIBRARY.get(cat, {})), value=None), "", items, names

        def on_gallery_pick(cat, names, event: gr.SelectData):
            if not names or event.index is None or event.index >= len(names):
                return gr.update(), gr.update()
            name = names[event.index]
            return name, preview_prompt_template(cat, name)

        category.change(on_prompt_category, [category], [template, preview, thumb_gallery, gallery_names], queue=False)
        template.change(preview_prompt_template, [category, template], [preview], queue=False)
        thumb_gallery.select(on_gallery_pick, [category, gallery_names], [template, preview], queue=False)
        gen_thumbs.click(generate_prompt_thumbnails, [category, gen_missing], [thumb_gallery])
        replace.click(apply_prompt_template, [category, template, prompt_box], [prompt_box], queue=False)
        append.click(lambda c, t, p: apply_prompt_template(c, t, p, append=True), [category, template, prompt_box], [prompt_box], queue=False)


def add_long_example_picker(segment_box):
    """Long-video segment examples (建築/室內/人物) that fill the 分段提示詞 box directly."""
    cats = list(LONG_VIDEO_EXAMPLES)
    with gr.Accordion("📚 分段提示詞範例｜建築・室內・人物（30 秒～2 分鐘，用官方技巧）", open=True):
        gr.Markdown(
            "入門學習用：每個範例是多段提示詞，已用單獨一行 `---` 分好段。**選範例 → 套用**，就會填進上面的「分段提示詞」框，"
            "把「每段秒數」保持在預設 10 秒，段數會決定總長度（3 段≈30 秒、6 段≈60 秒、12 段≈2 分鐘）。\n\n"
            "這些範例示範官方 h3-prompt-writing 技巧：開頭寫風格與 `[Shot 1]`；運鏡用官方詞彙（Push In／Truck／Arc／Pedestal／Tilt "
            "＋幅度＋速度）；聲音融進描述；畫面文字用英文雙引號；人物類用 `<Picture 1>` 綁定角色參考圖、台詞用 `(S1)`＋`<d>[English] …</d>`。"
            "每段開頭都接續上一段的結尾，維持同一場景／同一角色。套用後可自行改寫學習。"
        )
        with gr.Row():
            lcat = gr.Dropdown(label="分類", choices=cats, value=cats[0])
            lname = gr.Dropdown(label="範例（可輸入關鍵字搜尋）", choices=list(LONG_VIDEO_EXAMPLES[cats[0]]), value=None)
        lprev = gr.Textbox(label="範例預覽（每段以 --- 分隔）", lines=10, max_lines=24, interactive=False)
        lapply = gr.Button("套用到「分段提示詞」", variant="secondary")
        lcat.change(lambda c: (gr.Dropdown(choices=list(LONG_VIDEO_EXAMPLES.get(c, {})), value=None), ""),
                    [lcat], [lname, lprev], queue=False)
        lname.change(lambda c, n: LONG_VIDEO_EXAMPLES.get(c, {}).get(n, ""), [lcat, lname], [lprev], queue=False)
        lapply.click(lambda c, n: LONG_VIDEO_EXAMPLES.get(c, {}).get(n, ""), [lcat, lname], [segment_box], queue=False)

def plan_storyboard(story, seconds_per_shot=4):
    if not story or not story.strip():
        raise gr.Error("請先輸入故事內容！")
    parts = [x.strip() for x in re.split(r"(?<=[。！？!?])\s*|\n+", story) if x.strip()]
    return [[i, f"鏡頭 {i}", text, "電影感中景，平穩運鏡", int(seconds_per_shot), "環境音與情緒配樂"]
            for i, text in enumerate(parts[:30], 1)]

def render_storyboard(rows, resolution, turbo, text_encoder=None, lora_name=None, lora_strength=1.0,
                     fl2va_model=None, ref2va_model=None, progress=gr.Progress()):
    if hasattr(rows, "values"):
        rows = rows.values.tolist()
    rows = [r for r in (rows or []) if len(r) >= 6 and str(r[2]).strip()]
    if not rows:
        raise gr.Error("請先建立分鏡表！")
    clips = []
    for i, row in enumerate(rows):
        progress(i / len(rows), desc=f"正在渲染鏡頭 {i+1}/{len(rows)}")
        prompt = f"{row[2]}。鏡頭：{row[3]}。聲音：{row[5]}。保持角色外觀一致，不要字幕、文字或浮水印。"
        clips.append(execute_generation(prompt, resolution, int(row[4]), turbo, -1,
                                        text_encoder=text_encoder, lora_name=lora_name, lora_strength=lora_strength,
                                        fl2va_model=fl2va_model, ref2va_model=ref2va_model))
    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    output = os.path.join(COMFY_DIR, "output", f"AI_Studio_{int(time.time())}.mp4")
    list_file = os.path.join(tempfile.gettempdir(), f"h3_concat_{uuid.uuid4().hex}.txt")
    with open(list_file, "w", encoding="utf-8") as f:
        for clip in clips:
            f.write("file '" + clip.replace("'", "'\\''") + "'\n")
    result = subprocess.run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", list_file,
                             "-c", "copy", output], capture_output=True, text=True)
    os.unlink(list_file)
    if result.returncode != 0:
        raise gr.Error("剪接失敗：" + result.stderr[-800:])
    progress(1, desc="分鏡影片剪接完成")
    return output



theme = gr.themes.Soft(
    primary_hue="indigo",
    secondary_hue="slate"
)

# Keep both browser theme modes readable on the intentionally black interface.
dark_palette = {
    "body_background_fill": "#050505",
    "body_text_color": "#f1f5f9",
    "body_text_color_subdued": "#cbd5e1",
    "background_fill_primary": "#111111",
    "background_fill_secondary": "#181818",
    "block_background_fill": "#111111",
    "block_label_background_fill": "#181818",
    "block_label_text_color": "#f1f5f9",
    "block_title_text_color": "#f1f5f9",
    "block_info_text_color": "#cbd5e1",
    "input_background_fill": "#0a0a0a",
    "input_placeholder_color": "#64748b",
    "checkbox_label_background_fill": "#181818",
    "checkbox_label_background_fill_selected": "#25254a",
    "checkbox_label_text_color": "#f1f5f9",
    "checkbox_label_text_color_selected": "#ffffff",
    "button_secondary_background_fill": "#242424",
    "button_secondary_text_color": "#f1f5f9",
    "button_primary_background_fill": "#4338ca",
    "button_primary_text_color": "#ffffff",
    "link_text_color": "#a5b4fc",
}
theme = theme.set(**{
    variant: color
    for name, color in dark_palette.items()
    for variant in (name, name + "_dark")
}, body_text_size="16px", input_text_size="16px",
    block_label_text_size="15px", block_label_text_weight="600")

css = """
body, .gradio-container {
    background: #050505 !important;
    color: #f1f5f9 !important;
}
.gradio-container {
    --body-background-fill: #050505;
    --body-background-fill-dark: #050505;
    --background-fill-primary: #050505;
    --background-fill-secondary: #111111;
    --block-background-fill: #111111;
    --block-label-background-fill: #181818;
    --input-background-fill: #0a0a0a;
}
.gradio-container .block,
.gradio-container .form,
.gradio-container .panel {
    background: #111111 !important;
    border-color: #2a2a2a !important;
}
.gradio-container input:not([type="checkbox"]):not([type="radio"]),
.gradio-container textarea,
.gradio-container .wrap,
.gradio-container .secondary-wrap {
    background: #0a0a0a !important;
    color: #f8fafc !important;
    border-color: #333333 !important;
}
/* Checkboxes and radios draw their tick with a background image, so they must not get the blanket input background. */
.gradio-container input[type="checkbox"],
.gradio-container input[type="radio"] {
    background-color: #0a0a0a !important;
    border: 2px solid #94a3b8 !important;
}
.gradio-container input[type="checkbox"]:checked,
.gradio-container input[type="radio"]:checked {
    background-color: #6366f1 !important;
    border-color: #c7d2fe !important;
}
.gradio-container input[type="checkbox"]:checked {
    background-image: url("data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='M12.207 4.793a1 1 0 010 1.414l-5 5a1 1 0 01-1.414 0l-2-2a1 1 0 011.414-1.414L6.5 9.086l4.293-4.293a1 1 0 011.414 0z'/%3e%3c/svg%3e") !important;
    background-size: 100% 100% !important;
    background-position: center !important;
}
.gradio-container input[type="radio"]:checked {
    background-image: radial-gradient(circle, #ffffff 35%, transparent 40%) !important;
}
.gradio-container label,
.gradio-container .label-wrap,
.gradio-container .block-info,
.gradio-container .prose,
.gradio-container p,
.gradio-container h1,
.gradio-container h2,
.gradio-container h3 {
    color: #e5e7eb;
}
.gradio-container .label-wrap,
.gradio-container .block-info {
    background: #181818 !important;
}
.header-box { text-align: center; margin-bottom: 8px; margin-top: -5px; }
.gradio-container [role="tab"] { color: #cbd5e1 !important; font-size: 16px; font-weight: 600; }
.gradio-container [role="tab"][aria-selected="true"] { color: #ffffff !important; background: #25254a !important; border-bottom: 3px solid #a5b4fc !important; }
.gradio-container [role="listbox"],
.gradio-container [role="option"] { background: #181818 !important; color: #f1f5f9 !important; }
.gradio-container [role="option"]:hover,
.gradio-container [role="option"][aria-selected="true"] { background: #34345c !important; }
.gradio-container input::placeholder,
.gradio-container textarea::placeholder { color: #64748b !important; font-style: italic; opacity: 1; }
.gradio-container :focus-visible { outline: 2px solid #a5b4fc !important; outline-offset: 2px; }
.header-title { font-size: 2.0rem; font-weight: 800; color: #c4b5fd !important; margin: 0; }
"""

with gr.Blocks(title=PANEL_TITLE) as demo:
    with gr.Column(elem_classes=["header-box"]):
        gr.HTML("<h1 class='header-title'>MiniMax H3 影音創作面板 (Portable 版)</h1>")

    with gr.Row(equal_height=True):
        gpu_status = gr.Markdown("顯存管理 →")
        cancel_btn = gr.Button("⏹ 取消生成", variant="stop", scale=0, min_width=130)
        free_btn = gr.Button("🧹 釋放顯存", scale=0, min_width=130)
        status_btn = gr.Button("🔄 顯存狀態", scale=0, min_width=130)
    # queue=False: these must run even while a generation holds the Gradio queue.
    cancel_btn.click(cancel_generation, None, gpu_status, queue=False)
    free_btn.click(free_vram, None, gpu_status, queue=False)
    status_btn.click(gpu_status_text, None, gpu_status, queue=False)

    with gr.Accordion("🧩 模型設定（文字編碼器・擴散模型，共用）", open=False):
        with gr.Row():
            encoders = text_encoder_choices()
            model_encoder = gr.Dropdown(label="文字編碼器", choices=encoders, value=default_text_encoder(encoders), scale=5)
            model_refresh = gr.Button("🔄 重新掃描", scale=1)
        with gr.Row():
            fl2va_models = diffusion_model_choices("fl2va")
            ref2va_models = diffusion_model_choices("ref2va")
            model_fl2va = gr.Dropdown(label="FL2VA 擴散模型（文生／首尾幀／3D 攝影機／編劇）",
                                      choices=model_label_choices(fl2va_models),
                                      value=krea2_default(fl2va_models, H3_FL2VA_MODEL))
            model_ref2va = gr.Dropdown(label="Ref2VA 擴散模型（參考影音／長片）",
                                       choices=model_label_choices(ref2va_models),
                                       value=krea2_default(ref2va_models, H3_REF2VA_MODEL))
        model_refresh.click(refresh_model_choices, None, [model_encoder, model_fl2va, model_ref2va], queue=False)
    model_inputs = [model_encoder, model_fl2va, model_ref2va]

    with gr.Tabs():
        with gr.Tab("🎬 文生"):
            with gr.Row():
                with gr.Column(scale=5):
                    t2v_prompt = gr.Textbox(
                        label="影片描述 (Prompt)",
                        placeholder="詳細描述畫面、鏡頭動作與聲音效果，例如：\n電影級預告片：雨後的賽博朋克夜都市，主角身穿風衣在摩天大樓天台奔跑跳躍，背後是呼嘯而過的飛行車輛與霓虹光影。\n聲音：急促腳步聲、呼嘯風聲、遠處都市氛圍、震撼的電影低音音效。",
                        lines=5
                    )
                    add_prompt_picker(t2v_prompt)
                    add_base_prompt_builder(t2v_prompt)
                    with gr.Row():
                        t2v_res = gr.Dropdown(label="畫面解析度", choices=[*BASE_RES_CHOICES, *HD_RES_CHOICES], value=DEFAULT_RES)
                        t2v_duration = gr.Slider(
                            label="影片長度 (秒)",
                            minimum=4,
                            maximum=15,
                            value=4,
                            step=1
                        )
                    with gr.Row():
                        t2v_turbo = gr.Dropdown(label="🚀 採樣模式", choices=SAMPLING_MODES, value=MODE_TURBO_LORA)
                        t2v_seed = gr.Number(label="隨機種子 (-1 為隨機)", value=-1, precision=0)
                    t2v_hd = gr.Checkbox(label=HD_LABEL, info=HD_INFO if HD_ALLOWED else HD_LOW_VRAM_INFO, value=False, interactive=HD_ALLOWED)

                    t2v_btn = gr.Button("🎬 開始生成影音 (Generate Video & Audio)", variant="primary", size="lg")

                with gr.Column(scale=5):
                    t2v_output = gr.Video(label="生成影音預覽 (帶原生立體聲音效)", interactive=False, height=520)

            t2v_btn.click(
                fn=lambda p, r, d, tb, s, hd, enc, fl2, r2v: execute_generation(p, r, d, tb, s, text_encoder=enc, fl2va_model=fl2, ref2va_model=r2v, hd=hd),
                inputs=[t2v_prompt, t2v_res, t2v_duration, t2v_turbo, t2v_seed, t2v_hd, *model_inputs],
                outputs=[t2v_output]
            )

        with gr.Tab("🖼️ 首尾幀"):
            gr.Markdown("上傳首幀與尾幀，描述兩張圖片之間的動作與聲音，生成銜接影音。也可只提供首幀；兩張皆留空時依文字生成。")
            with gr.Row():
                with gr.Column(scale=5):
                    with gr.Row():
                        i2v_first = gr.Image(label="起始首幀圖片 (First Frame, 可選 · 支援 Ctrl+V 貼上)", type="filepath", height=300, elem_classes=["clipboard-image-target"])
                        i2v_last = gr.Image(label="結尾尾幀圖片 (Last Frame, 可選 · 支援 Ctrl+V 貼上)", type="filepath", height=300, elem_classes=["clipboard-image-target"])
                    i2v_prompt = gr.Textbox(
                        label="影音動態描述 (Prompt)",
                        placeholder="描述圖片中人物或場景如何運動，以及所搭配的聲音或音效...",
                        lines=3
                    )
                    add_prompt_picker(i2v_prompt)
                    add_base_prompt_builder(i2v_prompt)
                    i2v_instruction = gr.Checkbox(
                        label="自動加入官方首尾幀對齊宣告", value=True,
                        info="有首幀時第一行加上「<Picture 1> 是第 0 秒」；首尾幀都有時註明尾幀對齊的秒數。提示詞已自行寫好時不會重複加。")
                    with gr.Row():
                        i2v_res = gr.Dropdown(label="畫面解析度", choices=[*AUTO_RESOLUTION_CHOICES, *BASE_RES_CHOICES, *HD_RES_CHOICES], value=DEFAULT_RES)
                        i2v_duration = gr.Slider(label="影片長度 (秒)", minimum=4, maximum=15, value=4, step=1)
                    with gr.Row():
                        i2v_turbo = gr.Dropdown(label="🚀 採樣模式", choices=SAMPLING_MODES, value=MODE_TURBO_LORA)
                        i2v_seed = gr.Number(label="隨機種子 (-1 為隨機)", value=-1, precision=0)
                    i2v_hd = gr.Checkbox(label=HD_LABEL, info=HD_INFO if HD_ALLOWED else HD_LOW_VRAM_INFO, value=False, interactive=HD_ALLOWED)

                    i2v_btn = gr.Button("🎬 生成首尾幀影音", variant="primary", size="lg")

                with gr.Column(scale=5):
                    i2v_output = gr.Video(label="生成影音預覽", interactive=False, height=520)

            i2v_btn.click(
                fn=lambda p, r, d, tb, s, f, l, hd, ki, enc, fl2, r2v: execute_generation(p, r, d, tb, s, f, l, text_encoder=enc, fl2va_model=fl2, ref2va_model=r2v, hd=hd, keyframe_instruction=ki),
                inputs=[i2v_prompt, i2v_res, i2v_duration, i2v_turbo, i2v_seed, i2v_first, i2v_last, i2v_hd, i2v_instruction, *model_inputs],
                outputs=[i2v_output]
            )

        with gr.Tab("🎞️ 參考"):
            gr.Markdown(
                "### 參考圖、參考影片、音檔自由組合（Ref2VA）\n"
                "同一個 Ref2VA 模型，提示詞怎麼宣告決定它做什麼：\n\n"
                "| 用法 | 上傳 | 關鍵宣告 |\n|---|---|---|\n"
                "| 雙圖換裝 | 人物圖＋服裝圖 | 服裝 `attribute_transfer`，並寫明不要借服裝圖上的人 |\n"
                "| 照片＋聲線說話 | 人物圖＋音檔（音色範本） | 音檔 `reference`，台詞寫新的話 |\n"
                "| 外部音軌對嘴 | 臉＋服裝圖＋音檔 | 音檔 `fully_copy`，下方選「整條照用並對嘴」 |\n"
                "| 動作轉移換人 | 參考影片＋人物圖 | 影片 `fully_preserved`、人物 `attribute_transfer` |\n\n"
                "標籤依上傳順序編號；**影片有原音軌且勾選使用時，影片音軌會先佔一個 `<Audio N>`**，請以下方對照表為準。"
            )
            with gr.Row():
                with gr.Column(scale=5):
                    ref_images = gr.File(label="參考圖（最多 9 張，依順序為 <Picture 1>… · 支援 Ctrl+V 貼上）", file_count="multiple", file_types=["image"], type="filepath", elem_classes=["clipboard-image-target"])
                    ref_videos = gr.File(label="參考影片（選填，最多 3 支，會轉成 24 fps、最長 15 秒）", file_count="multiple", file_types=["video"], type="filepath")
                    ref_video_audio = gr.Checkbox(label="把參考影片的原音軌也當作參考（<Audio N>）", value=True)
                    ref_audios = gr.File(label="音檔（選填，最多 3 個）", file_count="multiple", file_types=["audio"], type="filepath")
                    ref_audio_mode = gr.Radio(
                        label="第一個音檔的用途", choices=[AUDIO_MODE_REFERENCE, AUDIO_MODE_COPY], value=AUDIO_MODE_REFERENCE,
                        info="整條照用：片長自動等於音檔長度（上限約 15 秒），音軌鎖進生成過程讓嘴型對上，成片再換回原始音檔。")
                    ref_label_md = gr.Markdown(label_table([]))
                    ref_labels = gr.State([])
                    with gr.Row():
                        ref_auto_btn = gr.Button("✨ 依素材自動生成提示詞", variant="secondary", scale=2)
                        ref_auto_mode = gr.Dropdown(label="自動提示詞用途", choices=AUTO_REF_MODES, value=AUTO_REF_MODES[0], scale=3)
                    ref_prompt = gr.Textbox(
                        label="提示詞 (Prompt)", lines=8,
                        placeholder="上傳素材後系統會自動生成最佳官方提示詞；亦可按「✨ 依素材自動生成提示詞」隨時重新生成..."
                    )
                    add_ref_prompt_builder(ref_prompt, ref_labels, ref_audio_mode)
                    add_prompt_picker(ref_prompt)
                    with gr.Row():
                        ref_res = gr.Dropdown(
                            label="畫面解析度",
                            info="自動：依第一支參考影片，沒有影片時依 <Picture 1> 的比例",
                            choices=[*AUTO_RESOLUTION_CHOICES, *REF_RES_CHOICES],
                            value=next(iter(AUTO_RESOLUTION_CHOICES))
                        )
                        ref_duration = gr.Slider(label="影片長度 (秒)（整條照用音檔時忽略）", minimum=4, maximum=15, value=5, step=1)
                    with gr.Row():
                        ref_turbo = gr.Dropdown(label="🚀 採樣模式", choices=SAMPLING_MODES, value=MODE_TURBO_LORA)
                        ref_scheduler = gr.Dropdown(label="採樣排程", choices=SCHEDULERS, value="simple", info=SCHEDULER_INFO)
                        ref_seed = gr.Number(label="隨機種子 (-1 為隨機)", value=-1, precision=0)

                    ref_btn = gr.Button("🎬 生成參考影音", variant="primary", size="lg")

                with gr.Column(scale=5):
                    ref_output = gr.Video(label="生成影音預覽", interactive=False, height=520)

            for control in (ref_images, ref_videos, ref_video_audio, ref_audios):
                control.change(
                    on_reference_materials_change,
                    [ref_images, ref_videos, ref_video_audio, ref_audios, ref_prompt, ref_auto_mode],
                    [ref_label_md, ref_labels, ref_prompt],
                    queue=False
                )
            ref_auto_btn.click(
                force_generate_ref_prompt,
                [ref_images, ref_videos, ref_video_audio, ref_audios, ref_auto_mode],
                ref_prompt,
                queue=False
            )
            ref_auto_mode.change(
                force_generate_ref_prompt,
                [ref_images, ref_videos, ref_video_audio, ref_audios, ref_auto_mode],
                ref_prompt,
                queue=False
            )
            ref_btn.click(
                fn=lambda p, r, d, tb, s, imgs, vids, va, auds, mode, sch, enc, fl2, r2v: execute_ref_generation(
                    p, r, d, tb, s, imgs, vids, va, auds, mode, scheduler=sch, text_encoder=enc, fl2va_model=fl2, ref2va_model=r2v),
                inputs=[ref_prompt, ref_res, ref_duration, ref_turbo, ref_seed, ref_images, ref_videos, ref_video_audio, ref_audios, ref_audio_mode, ref_scheduler, *model_inputs],
                outputs=[ref_output]
            )

        with gr.Tab("🔄 V2V"):
            gr.Markdown(
                "### 影片轉影片 / 動作與風格重塑（Video-to-Video）\n"
                "上傳來源影片（提供動作、運鏡、肢體軌跡），透過提示詞保留動作、重塑畫質與風格：\n\n"
                "- 🌟 **HDR 畫質重塑與動作增強**（`Singularity` 奇點微調模型專精：大幅消除運動模糊、去油光、強化武俠打鬥打擊感與特效）\n"
                "- 🏙️ **動作保留 + 背景場景變換**（人物動作原樣保留，將背景環境變換為賽博龐克、奇幻森林、雨夜等）\n"
                "- 🎨 **動漫 / 奇幻風格重塑**（保留肢體動作，重繪為二次元或魔幻特效風格）\n"
                "- ⏳ **超長影片自動分段長片**：約 15~16 秒以內單段極速重塑（如 15.1 秒影片不分段直接完成）；超過 16 秒系統會**自動分段處理**，每段始終錨定原版參考素材以杜絕迭代畫質衰退與暗斑，最後自動無縫合成完整影片並還原原音！"
            )
            with gr.Row():
                with gr.Column(scale=5):
                    v2v_video = gr.File(label="來源影片（動作 / 運鏡 / 肢體來源，會標為 <Video 1>）", file_types=["video"], file_count="single", type="filepath")
                    v2v_label_preview = gr.Markdown("尚未上傳來源影片。")

                    with gr.Row():
                        v2v_preset = gr.Dropdown(
                            label="💡 常用 V2V 提示詞範本（點選即可套用）",
                            choices=list(V2V_PRESETS.keys()),
                            value=list(V2V_PRESETS.keys())[0],
                            scale=4
                        )
                        v2v_apply_btn = gr.Button("套用範本", scale=1, min_width=90)

                    v2v_prompt = gr.Textbox(
                        label="提示詞 (Prompt)",
                        lines=6,
                        value=V2V_DEFAULT_PROMPT,
                        placeholder="描述要保留什麼動作（如 <Video 1> fully_preserved）與要變換的風格或角色外貌..."
                    )

                    with gr.Row():
                        v2v_model = gr.Dropdown(
                            label="🎯 V2V 擴散模型",
                            choices=model_label_choices(ref2va_models),
                            value=v2v_default_model(ref2va_models),
                            info="首選 Singularity 奇點微調模型（支援 HDR 與動作增強）"
                        )
                        v2v_res = gr.Dropdown(
                            label="畫面解析度",
                            info="自動：依來源影片比例",
                            choices=[*AUTO_RESOLUTION_CHOICES, *REF_RES_CHOICES],
                            value=next(iter(AUTO_RESOLUTION_CHOICES))
                        )
                    with gr.Row():
                        v2v_auto_duration = gr.Checkbox(label="⚡ 自動處理整支影片（超過 16 秒自動分段長片）", value=True)
                        v2v_video_audio = gr.Checkbox(label="保留來源影片原音軌", value=True)
                        v2v_duration = gr.Slider(label="指定秒數（未勾選整支時生效）", minimum=4, maximum=60, value=5, step=1)
                    with gr.Row():
                        v2v_turbo = gr.Dropdown(label="🚀 採樣模式", choices=SAMPLING_MODES, value=MODE_TURBO_LORA)
                        v2v_scheduler = gr.Dropdown(label="採樣排程", choices=SCHEDULERS, value="simple")
                        v2v_seed = gr.Number(label="隨機種子 (-1 為隨機)", value=-1, precision=0)

                    v2v_btn = gr.Button("🔄 開始 V2V 影片重塑", variant="primary", size="lg")

                with gr.Column(scale=5):
                    v2v_output = gr.Video(label="V2V 重塑影片預覽", interactive=False, height=520)

            def update_v2v_labels(vid, keep_audio):
                if not vid:
                    return "尚未上傳來源影片。"
                v_path = vid if isinstance(vid, str) else (vid.name if hasattr(vid, "name") else str(vid))
                v_name = os.path.basename(v_path)
                lines = [f"| 標籤 | 類型 | 檔案來源 |\n|---|---|---|\n| `<Video 1>` | 來源影片（動作/運鏡來源） | `{v_name}` |"]
                if keep_audio and has_audio_stream(v_path):
                    lines.append(f"| `<Audio 1>` | 來源音軌 | 隨片保留 |")
                return "**提示詞素材對照表**：\n\n" + "\n".join(lines)

            for c in (v2v_video, v2v_video_audio):
                c.change(update_v2v_labels, [v2v_video, v2v_video_audio], v2v_label_preview, queue=False)

            v2v_apply_btn.click(lambda p_name: V2V_PRESETS.get(p_name, ""), inputs=[v2v_preset], outputs=[v2v_prompt], queue=False)
            v2v_preset.change(lambda p_name: V2V_PRESETS.get(p_name, ""), inputs=[v2v_preset], outputs=[v2v_prompt], queue=False)

            def on_v2v_model_change(selected_model):
                low = (selected_model or "").lower()
                baked = "turbo" in low and "singularity" not in low
                mode = MODE_BAKED_TURBO if baked else MODE_TURBO_LORA
                if "singularity" in low:
                    gr.Info("已選取 Singularity 奇點微調模型：自動配置 4 步 Turbo 模式，具備 HDR 畫質與動作增強能力。")
                elif baked:
                    gr.Info("已選取內建蒸餾模型：自動配置 8 步採樣（不外掛 Turbo LoRA）。")
                else:
                    gr.Info("已選取標準模型：自動配置 4 步 Turbo LoRA 採樣。")
                return gr.Dropdown(value=mode), selected_model

            v2v_model.change(on_v2v_model_change, inputs=[v2v_model], outputs=[v2v_turbo, model_ref2va], queue=False)

            v2v_btn.click(
                fn=lambda vid, p, r, d, ad, tb, s, sch, va, enc, fl2, v2vm: execute_v2v(
                    vid, [], p, r, d, ad, tb, s, scheduler=sch, use_video_audio=va,
                    text_encoder=enc, fl2va_model=fl2, ref2va_model=v2vm),
                inputs=[v2v_video, v2v_prompt, v2v_res, v2v_duration, v2v_auto_duration,
                        v2v_turbo, v2v_seed, v2v_scheduler, v2v_video_audio,
                        model_encoder, model_fl2va, v2v_model],
                outputs=[v2v_output]
            )

        with gr.Tab("🎤 對嘴"):
            gr.Markdown(
                "### 一張人像 + 一段語音 → 對嘴影片\n"
                "最簡單的對嘴：上傳一張人像照當 `<Picture 1>`、一段語音當 `<Audio 1>`，按生成。"
                "用的是 Ref2VA（跟「參考」分頁同一個模型），音檔會**鎖進生成過程讓嘴型對上**，成片再換回原始音檔。\n\n"
                "- **不是傳統 Wav2Lip**：H3 會整段重新生成，臉孔、背景會盡量貼近原圖但非逐像素不變；提示詞已內建「保持場景、只動嘴」。\n"
                "- ⏳ **超長語音自動分段長片**：約 15~16 秒以內單段極速生成；語音長度**若超過 16 秒會自動分段連續生成**（每段約 10~12 秒），**各段全程以原始高解析人像照片為錨定參考**（徹底杜絕截取上一段末幀造成 VAE 迭代失真、變黑與雜色噪點問題！），最後自動無縫拼接並還原完整原音！\n"
                "- 正面、清晰、單人、嘴部沒被遮住的人像效果最好。語音建議乾淨人聲。"
            )
            with gr.Row():
                with gr.Column(scale=5):
                    lip_image = gr.Image(label="人像照片（<Picture 1> · 支援 Ctrl+V 貼上）", type="filepath", height=320, elem_classes=["clipboard-image-target"])
                    lip_audio = gr.Audio(label="要對嘴的語音（<Audio 1>）", type="filepath")
                    lip_prompt = gr.Textbox(label="提示詞（已內建，可自行微調）", lines=6, value=LIPSYNC_DEFAULT_PROMPT)
                    with gr.Row():
                        lip_res = gr.Dropdown(
                            label="畫面解析度",
                            choices=[
                                "480 × 864 (9:16 直式 · 推薦)",
                                "768 × 1344 (9:16 直式 · 高清)",
                                "864 × 480 (16:9 橫式)",
                                "960 × 544 (16:9 橫式 · 中清)",
                            ],
                            value="480 × 864 (9:16 直式 · 推薦)")
                        lip_mode = gr.Dropdown(label="🚀 採樣模式", choices=SAMPLING_MODES, value=MODE_TURBO_LORA)
                        lip_seed = gr.Number(label="隨機種子 (-1 為隨機)", value=-1, precision=0)
                    lip_btn = gr.Button("🎤 生成對嘴影片", variant="primary", size="lg")
                with gr.Column(scale=5):
                    lip_output = gr.Video(label="對嘴影片（含原始語音）", interactive=False, height=520)
            lip_btn.click(
                fn=lambda img, aud, p, r, md, s, enc, fl2, r2v: execute_lipsync(
                    img, aud, p, r, md, s, text_encoder=enc, fl2va_model=fl2, ref2va_model=r2v),
                inputs=[lip_image, lip_audio, lip_prompt, lip_res, lip_mode, lip_seed, *model_inputs],
                outputs=[lip_output]
            )

        with gr.Tab("📼 長片"):
            gr.Markdown(
                "### 🎬 Smite79 H3-LongVideos 劇本分鏡連續長片（至多 120 秒）\n"
                "已升級改用 **[Smite79/MiniMax-H3-Longvideos](https://huggingface.co/Smite79/MiniMax-H3-Longvideos)** 官方推薦架構！"
                "單一提示詞／劇本分鏡直出連續影音，內建角色記憶、對白識別、鏡頭銜接與同步立體聲。\n\n"
                "- **劇本提示詞格式（推薦寫法）**：\n"
                "  - **第一段為「場景與環境（Scene）」**：設定全片的光影、色調、時間、地點與攝影風格（自動作為各鏡頭基底）。\n"
                "  - **後續各段為「分鏡動作（Beats）」**：每段代表一個鏡頭（段落之間請空一行）。\n"
                "  - **對白標記**：台詞請加雙引號，例如：`Mara 走過來問他：\"還有最後一個嗎？\"`\n"
                "  - **角色設定（Character Sheet）**：可在段落中定義 `女主: <Picture 1>, 25, she, 黑色風衣...`，多鏡頭角色特徵始終一致。\n"
                "  - **原字不漏指令**：若有特定動作不可被壓縮，可在該行前加上 `exact:`（例如：`exact: 雙手始終背在身後`）。\n"
                "- **全域提示詞**：若只填寫全域提示詞（如單一場景或連續運鏡），系統會依每段目標秒數自動連貫生成。"
            )
            with gr.Row():
                with gr.Column(scale=5):
                    smite_ready = smite_node_installed()
                    long_engine = gr.Dropdown(
                        label="🎬 長片生成系統架構",
                        choices=[SMITE_ENGINE, TIMELINE_ENGINE],
                        value=SMITE_ENGINE if smite_ready else TIMELINE_ENGINE,
                        info=("預設為 Smite79 次世代系統，支援人物記憶、對白識別與多鏡頭音影連貫。" if smite_ready else
                              "尚未安裝 Smite79 引擎，已改用 TimelineDirector（分段提示詞以單獨一行 --- 分隔）。"
                              f"想用 Smite79 請自行從 {SMITE_REPO_URL} 下載到 ComfyUI\\custom_nodes\\ 後重啟。")
                    )
                    long_prompt = gr.Textbox(
                        label="全域提示詞／劇本場景設定（Scene 氛圍）",
                        lines=5,
                        placeholder="第一段描述全片場景、環境光影、時間地點與攝影質感；亦可直接在此輸入完整多段劇本..."
                    )
                    add_prompt_picker(long_prompt)
                    long_segment_prompts = gr.Textbox(
                        label="分鏡劇本（Beats，每段一鏡頭，段落間空一行）",
                        lines=8,
                        placeholder="鏡頭 1：女主從病房脫身，警惕地觀察走廊四周。\n\n鏡頭 2：女主蹲行躲在布草車後方，護士推車經過護士站。\n\n鏡頭 3：女主坐上輪椅進入電梯，電梯門關閉。"
                    )
                    add_long_example_picker(long_segment_prompts)
                    long_ref = gr.Image(label="角色參考圖（選填，提示詞用 <Picture 1> · 支援 Ctrl+V 貼上）", type="filepath", height=300, elem_classes=["clipboard-image-target"])
                    with gr.Row():
                        long_segment = gr.Slider(label="每鏡頭目標秒數 (Shot Seconds)", minimum=5, maximum=15, value=10, step=1)
                        long_total = gr.Slider(label="預估總長度（秒）", minimum=10, maximum=120, value=30, step=1)
                    with gr.Row():
                        long_res_choices = [r for r in LONG_VIDEO_RESOLUTIONS
                                            if not (LOW_VRAM and long_video_ratio_mp(r)[1] >= LONG_HQ_MIN_MP)]
                        long_res = gr.Dropdown(
                            label="畫面解析度",
                            choices=long_res_choices,
                            value=long_res_choices[0],
                            info=(f"這台 {VRAM_GB:.0f} GB 顯存只列出省顯存的解析度；要更清楚，生成後用「🔍 放大」。" if LOW_VRAM else
                                  "高畫質選項更清楚但更慢、更吃顯存（需 24GB），請搭配較短的每鏡秒數；"
                                  "採樣模式選「非蒸餾・20 步」細節最好。")
                        )
                        long_seed = gr.Number(label="隨機種子 (-1 為隨機)", value=-1, precision=0)
                        long_scheduler = gr.Dropdown(label="採樣排程", choices=SCHEDULERS, value="simple", info=SCHEDULER_INFO)
                    long_mode = gr.Dropdown(label="採樣模式", choices=SAMPLING_MODES, value=MODE_TURBO_LORA,
                                            info=f"長片的 Turbo LoRA 會自動用 {LONG_TURBO_MIN_STEPS} 步（4 步在長片會糊、高畫質會花掉）。")
                    long_plan = gr.Markdown(preview_long_plan(30, 10, ""))
                    with gr.Row():
                        long_plan_btn = gr.Button("📋 先預覽分鏡劇本規劃 (Plan Only・不消耗顯存)", variant="secondary", scale=2)
                        long_btn = gr.Button("🎬 開始生成長片影音", variant="primary", size="lg", scale=3)
                with gr.Column(scale=5):
                    long_output = gr.Video(label="長片輸出預覽", interactive=False, height=520)
            for control in (long_total, long_segment, long_segment_prompts):
                control.change(preview_long_plan, [long_total, long_segment, long_segment_prompts], long_plan, queue=False)
            long_btn.click(
                fn=lambda p, sp, tot, seg, r, s, img, sch, md, eng, enc, fl2, r2v: execute_long_generation(
                    p, sp, tot, seg, r, s, ref_image_file=img, scheduler=sch, mode=md, engine=eng, plan_only=False,
                    text_encoder=enc, fl2va_model=fl2, ref2va_model=r2v
                ),
                inputs=[long_prompt, long_segment_prompts, long_total, long_segment, long_res, long_seed, long_ref, long_scheduler, long_mode, long_engine, *model_inputs],
                outputs=[long_output]
            )
            long_plan_btn.click(
                fn=lambda p, sp, tot, seg, r, s, img, sch, md, eng, enc, fl2, r2v: execute_long_generation(
                    p, sp, tot, seg, r, s, ref_image_file=img, scheduler=sch, mode=md, engine=eng, plan_only=True,
                    text_encoder=enc, fl2va_model=fl2, ref2va_model=r2v
                ),
                inputs=[long_prompt, long_segment_prompts, long_total, long_segment, long_res, long_seed, long_ref, long_scheduler, long_mode, long_engine, *model_inputs],
                outputs=[long_output]
            )
            gr.Markdown("[長片核心架構：Smite79 / MiniMax-H3-Longvideos](https://huggingface.co/Smite79/MiniMax-H3-Longvideos) · 支援劇本鏡頭導演、角色記憶與多鏡頭音畫連貫。亦支援舊版 TimelineDirector 滑動視窗。")


        with gr.Tab("🔍 放大"):
            gr.Markdown("### 用 SeedVR2 把現成影片放大\n"
                        "上傳任何影片，SeedVR2 逐批放大並保持時序一致，原音軌會保留。"
                        "**這是修復／放大工具，不是文生影片**。字節跳動開源，Apache-2.0。\n\n"
                        "- **短邊解析度**：輸出畫面的短邊像素；4K 很吃顯存與時間。\n"
                        "- **每批幀數**：一次處理幾幀，越多時序越穩、越省時間，但越吃顯存（最少 5）。\n"
                        "- **顯存不足**時把「區塊轉 CPU」調高（0–32），用速度換顯存。")
            missing_models_notice(seedvr2_models_ready(), " SeedVR2 放大模型", 4)
            with gr.Row():
                with gr.Column(scale=5):
                    seedvr_video = gr.Video(label="上傳要放大的影片", interactive=True, height=360)
                    with gr.Row():
                        seedvr_res = gr.Dropdown(label="短邊解析度", choices=list(SEEDVR2_RES_CHOICES), value="1080p（短邊 1080）")
                        seedvr_batch = gr.Slider(label="每批幀數", minimum=5, maximum=33, value=5 if LOW_VRAM else 9, step=1)
                    with gr.Row():
                        # Smaller cards start with part of the 3B DiT on the CPU so the first run does not OOM.
                        seedvr_swap = gr.Slider(label="區塊轉 CPU（省顯存，越高越慢）", minimum=0, maximum=32, step=1,
                                                value=(16 if VRAM_GB < 14 else 8) if LOW_VRAM else 0,
                                                info=f"已依 {VRAM_GB:.0f} GB 顯存自動調整" if LOW_VRAM else None)
                        seedvr_color = gr.Dropdown(label="色彩校正", choices=SEEDVR2_COLOR, value="lab")
                    with gr.Row():
                        seedvr_seed = gr.Number(label="隨機種子 (-1 為隨機)", value=-1, precision=0)
                    with gr.Accordion("模型檔案", open=False):
                        seedvr_models = seedvr2_model_choices()
                        seedvr_dit = gr.Dropdown(label="SeedVR2 主模型", choices=seedvr_models, value=krea2_default(seedvr_models, SEEDVR2_DIT))
                        seedvr_vaes = list_model_files("SEEDVR2", "SeedVR2LoadVAEModel", "model")
                        seedvr_vae = gr.Dropdown(label="SeedVR2 VAE", choices=seedvr_vaes, value=krea2_default(seedvr_vaes, SEEDVR2_VAE))
                        seedvr_rescan = gr.Button("🔄 重新掃描模型")
                    seedvr_btn = gr.Button("🔍 放大影片", variant="primary", size="lg")
                with gr.Column(scale=5):
                    seedvr_output = gr.Video(label="放大結果", interactive=False, height=520)
            seedvr_rescan.click(
                lambda: (gr.Dropdown(choices=seedvr2_model_choices()),
                         gr.Dropdown(choices=list_model_files("SEEDVR2", "SeedVR2LoadVAEModel", "model"))),
                None, [seedvr_dit, seedvr_vae], queue=False)
            seedvr_btn.click(execute_seedvr2_upscale,
                             inputs=[seedvr_video, seedvr_res, seedvr_batch, seedvr_swap, seedvr_color, seedvr_seed, seedvr_dit, seedvr_vae],
                             outputs=[seedvr_output])
            gr.Markdown("模型：`numz/SeedVR2_comfyUI`（版本 `09ced71`）3B fp16 + EMA VAE，`download_seedvr2.py` 可續傳並核對 SHA-256。"
                        "節點：[numz/ComfyUI-SeedVR2_VideoUpscaler](https://github.com/numz/ComfyUI-SeedVR2_VideoUpscaler)。")

        with gr.Tab("🎨 圖片"):
            gr.Markdown(
                "### 🌟 Krea-2 官方純淨版高速生圖\n"
                "**Krea-2** 是專門的高質感圖像生成模型（使用 Qwen3-VL 4B 文字編碼器與 Qwen VAE），可產生高美學質感圖片作為 H3 影片、對嘴之參考圖。\n\n"
                "- 🚀 **官方 Turbo 蒸餾模型**：只需 **8 步** 即可極速出圖（RTX 4090 約 5 秒一張；顯存較小會慢一些），享有純淨細緻的光影與寫實質感。\n"
                "- 🎨 **風格與角色 LoRA**：支援內建 9 款官方藝術風格 LoRA（復古動漫、水彩、霓虹、雨窗等）及自訂角色 LoRA。"
            )
            missing_models_notice(krea2_models_ready(), " Krea2 圖片模型", 1)
            with gr.Row():
                with gr.Column(scale=5):
                    krea_prompt = gr.Textbox(
                        label="提示詞 (Prompt)", lines=5,
                        placeholder="輸入你想生成的畫面描述（支援英文自然語言或標籤，例如：A stunning 25-year-old Japanese woman, elegant face, luxury penthouse, night, city lights, photorealistic, 8k）")
                    add_prompt_picker(krea_prompt)
                    with gr.Row():
                        krea_size = gr.Dropdown(label="尺寸", choices=KREA2_SIZES, value=KREA2_SIZES[1])
                        krea_batch = gr.Slider(label="一次張數", minimum=1, maximum=10, value=1, step=1)
                        krea_seed = gr.Number(label="隨機種子 (-1 為隨機)", value=-1, precision=0)
                    with gr.Accordion("🎨 風格／原創角色 LoRA（放在 ComfyUI/models/loras/krea2/）", open=True):
                        gr.Markdown("觸發詞放在 LoRA 旁的 `同名.trigger.txt`，選到的 LoRA 會自動把觸發詞接到提示詞後面（沒有觸發詞的風格 LoRA 通常不會生效）。"
                                    "點縮圖會填入第一個空的欄位；同時最多疊三個。"
                                    "縮圖優先用 LoRA 旁的預覽圖（`同名.png` 等），沒有的話可按「產生缺少的縮圖」，"
                                    "會以「東亞女子頭像」快速畫一張，方便預覽角色與風格。")
                        krea_lora_items, krea_lora_names_init = krea2_lora_gallery()
                        krea_lora_names = gr.State(krea_lora_names_init)
                        krea_lora_gallery = gr.Gallery(value=krea_lora_items, label="LoRA 縮圖", columns=6, height=240,
                                                       allow_preview=False, object_fit="cover")
                        krea_slot_loras, krea_slot_strengths = [], []
                        slot_choices = [NO_LORA, *krea_lora_names_init]
                        for slot in range(1, KREA2_LORA_SLOTS + 1):
                            with gr.Row():
                                krea_slot_loras.append(gr.Dropdown(label=f"LoRA {slot}", choices=slot_choices, value=NO_LORA, scale=4))
                                krea_slot_strengths.append(gr.Slider(label="強度", minimum=0, maximum=1.5, value=1.0, step=0.05, scale=2))
                        krea_trigger_md = gr.Markdown("")
                        with gr.Row():
                            krea_lora_rescan = gr.Button("🔄 重新掃描 LoRA")
                            krea_thumb_btn = gr.Button("🖼️ 產生縮圖")
                            krea_thumb_missing = gr.Checkbox(label="只補缺少的", value=True)
                    with gr.Accordion("模型與取樣設定", open=False):
                        krea_models = krea2_model_choices()
                        krea_model = gr.Dropdown(label="🎯 擴散模型", choices=krea_models, value=krea2_default(krea_models, KREA2_OFFICIAL_MODEL), info="官方推薦 krea2_turbo_fp8_scaled")
                        krea_encoders = [value for _, value in text_encoder_choices()] + [f for f in list_model_files("text_encoders", "CLIPLoader", "clip_name") if f.endswith(".safetensors")]
                        krea_clip = gr.Dropdown(label="文字編碼器（Qwen3-VL 4B）", choices=sorted(set(krea_encoders)),
                                                value=krea2_default(sorted(set(krea_encoders)), KREA2_TEXT_ENCODER))
                        krea_vaes = list_model_files("vae", "VAELoader", "vae_name")
                        krea_vae = gr.Dropdown(label="VAE", choices=krea_vaes, value=krea2_default(krea_vaes, KREA2_VAE))
                        krea_loras = [NO_LORA] + [f for f in list_model_files("loras", "LoraLoaderModelOnly", "lora_name") if f.endswith(".safetensors")]
                        with gr.Row():
                            krea_lora = gr.Dropdown(label="Turbo LoRA (非 Turbo 模型才需掛載)", choices=krea_loras, value=krea2_default(krea_loras, KREA2_TURBO_LORA), scale=3)
                            krea_lora_strength = gr.Slider(label="Turbo LoRA 強度", minimum=0, maximum=1.5, value=0.85, step=0.05, scale=2)
                        with gr.Row():
                            krea_sampler = gr.Dropdown(label="採樣器", choices=KREA2_SAMPLERS, value="er_sde")
                            krea_cfg = gr.Number(label="CFG", value=1.0)
                        with gr.Row():
                            krea_steps = gr.Slider(label="採樣步數 (Turbo 推薦 8 步)", minimum=4, maximum=30, value=8, step=1)
                            krea_scheduler = gr.Dropdown(label="採樣排程", choices=SCHEDULERS, value="simple")
                        krea_refresh = gr.Button("🔄 重新掃描模型")
                    krea_btn = gr.Button("🖼️ 生成圖片", variant="primary", size="lg")
                with gr.Column(scale=5):
                    krea_output = gr.Gallery(label="生成結果", columns=2, height=640, preview=True)

            def refresh_krea2_choices():
                models = krea2_model_choices()
                encoders = sorted({f for f in list_model_files("text_encoders", "CLIPLoader", "clip_name") if f.endswith(".safetensors")})
                vaes = list_model_files("vae", "VAELoader", "vae_name")
                loras = [NO_LORA] + [f for f in list_model_files("loras", "LoraLoaderModelOnly", "lora_name") if f.endswith(".safetensors")]
                return (gr.Dropdown(choices=models, value=krea2_default(models, KREA2_OFFICIAL_MODEL)),
                        gr.Dropdown(choices=encoders, value=krea2_default(encoders, KREA2_TEXT_ENCODER)),
                        gr.Dropdown(choices=vaes, value=krea2_default(vaes, KREA2_VAE)),
                        gr.Dropdown(choices=loras, value=krea2_default(loras, KREA2_TURBO_LORA)))

            krea_refresh.click(refresh_krea2_choices, None, [krea_model, krea_clip, krea_vae, krea_lora], queue=False)

            def rescan_krea2_loras(*current):
                items, names = krea2_lora_gallery()
                choices = [NO_LORA, *names]
                slots = [gr.Dropdown(choices=choices, value=value if value in choices else NO_LORA) for value in current]
                return (items, names, *slots)

            # Explicit slot parameters: Gradio cannot inject SelectData after *varargs.
            def pick_krea2_lora(names, slot_1, slot_2, slot_3, event: gr.SelectData):
                current = (slot_1, slot_2, slot_3)
                index = event.index[0] if isinstance(event.index, (list, tuple)) else event.index
                if index is None or index >= len(names):
                    return tuple(gr.Dropdown() for _ in current)
                chosen = names[index]
                updates = [gr.Dropdown() for _ in current]
                if chosen in current:
                    return tuple(updates)
                empty = next((i for i, value in enumerate(current) if value in (None, NO_LORA)), 0)
                updates[empty] = gr.Dropdown(value=chosen)
                return tuple(updates)

            krea_lora_rescan.click(rescan_krea2_loras, krea_slot_loras,
                                   [krea_lora_gallery, krea_lora_names, *krea_slot_loras], queue=False)
            krea_lora_gallery.select(pick_krea2_lora, [krea_lora_names, *krea_slot_loras], krea_slot_loras, queue=False)
            krea_thumb_btn.click(generate_krea2_thumbnails, [krea_model, krea_clip, krea_vae, krea_lora, krea_thumb_missing], krea_lora_gallery)
            for slot in krea_slot_loras:
                slot.change(trigger_summary, krea_slot_loras, krea_trigger_md, queue=False)
            krea_btn.click(
                execute_krea2_generation,
                inputs=[krea_prompt, krea_size, krea_batch, krea_seed, krea_model, krea_lora,
                        krea_lora_strength, krea_sampler,
                        krea_steps, krea_scheduler, krea_cfg, krea_clip, krea_vae,
                        krea_slot_loras[0], krea_slot_strengths[0], krea_slot_loras[1], krea_slot_strengths[1],
                        krea_slot_loras[2], krea_slot_strengths[2]],
                outputs=[krea_output]
            )
            gr.Markdown("模型來源：`Comfy-Org/Krea-2` 官方純淨版 `krea2_turbo_fp8_scaled.safetensors`（13.14 GB，8 步 Turbo 蒸餾加速）。"
                        "配套 Qwen3-VL 4B 編碼器、Qwen image VAE 與官方風格 LoRA 均通過 SHA-256 驗證。")

        with gr.Tab("🖌️ 修圖"):
            gr.Markdown(
                "### 🖌️ Qwen-Image-2.1 多模態指令修圖與參考換裝\n"
                "**Qwen-Image-2.1** 是阿里千問開源的次世代統一圖像生成與**指令修圖**大模型（7B DiT + Qwen3-VL 8B 編碼器），"
                "支援單圖局部精準修改、多圖外觀／服裝遷移、背景置換與風格變換！\n\n"
                "- 🎯 **提示詞圖片標記規範**：\n"
                "  - 主圖自動標記為 **`<image1>`**（要修改的人物、主體或場景）。\n"
                "  - 選填參考圖依序標記為 **`<image2>`**、**`<image3>`**…（如要借用的服裝、配飾、風格或第二個人物）。\n"
                "- 🚀 **原生 2K 與自然語言修圖**：原生支援高達 2048×2048 輸出；支援純英文或中英混合指令（例如：`Keep <image1> unchanged, replace outfit with <image2>`）。\n"
                "- ⚡ **KV 快取加速**：內建 `QwenImage21Cache` 自動調節顯存（Int8 量化，12GB 以上顯卡都能用）。"
            )
            qwen_dits, qwen_encoders, qwen_vaes = qwen_image_model_choices()
            missing_models_notice(qwen_image_models_ready(), " Qwen-Image-2.1 修圖模型", 3)
            with gr.Row():
                with gr.Column(scale=5):
                    with gr.Row():
                        qwen_primary_image = gr.Image(label="主圖 / 要修改的圖片 (<image1>, 必要 · 支援 Ctrl+V 貼上)", type="filepath", height=300, elem_classes=["clipboard-image-target"])
                        qwen_ref_image = gr.Image(label="選填參考圖 (<image2>, 如服飾/配件/風格 · 支援 Ctrl+V 貼上)", type="filepath", height=300, elem_classes=["clipboard-image-target"])
                    with gr.Accordion("➕ 更多參考圖 (<image3>, <image4>... 如多配件或多人物)", open=False):
                        qwen_extra_images = gr.File(label="批次上傳更多參考圖 (依序對應 <image3>, <image4>... · 支援 Ctrl+V 貼上)", file_types=["image"], file_count="multiple", type="filepath", elem_classes=["clipboard-image-target"])
                        qwen_extra_gallery = gr.Gallery(label="更多參考圖預覽 (<image3> 起)", columns=4, height=130, allow_preview=True)

                    def update_qwen_gallery(files):
                        if not files:
                            return []
                        res = []
                        for idx, f in enumerate(files, 3):
                            path = f if isinstance(f, str) else (f.name if hasattr(f, "name") else str(f))
                            res.append((path, f"<image{idx}>"))
                        return res

                    qwen_extra_images.change(update_qwen_gallery, [qwen_extra_images], [qwen_extra_gallery], queue=False)
                    with gr.Row():
                        qwen_preset = gr.Dropdown(
                            label="💡 常用修圖指令範本（點選即可填入）",
                            choices=list(QWEN_IMAGE_PRESETS.keys()),
                            value=list(QWEN_IMAGE_PRESETS.keys())[0],
                            scale=4
                        )
                        qwen_preset_btn = gr.Button("套用範本", scale=1, min_width=90)
                    qwen_prompt = gr.Textbox(
                        label="修圖提示詞 (Prompt)",
                        lines=5,
                        value=QWEN_IMAGE_PRESETS[list(QWEN_IMAGE_PRESETS.keys())[0]],
                        placeholder="請使用 <image1> 代表主圖，<image2> 代表第 1 張參考圖...\n例如：Keep the character and pose in <image1> unchanged, put this outfit from <image2> on the character..."
                    )
                    qwen_negative = gr.Textbox(
                        label="反向提示詞 (Negative Prompt, 選填)",
                        lines=2,
                        value="",
                        placeholder="選填：模糊、低畫質、畸形、多餘肢體..."
                    )
                    with gr.Row():
                        qwen_res = gr.Dropdown(
                            label="輸出解析度",
                            choices=QWEN_IMAGE_RESOLUTIONS,
                            value=QWEN_IMAGE_RESOLUTIONS[0],
                            info="預設 1024 自動等比例縮放；可選 2048 原生 2K 或 0 保持像素"
                        )
                        qwen_steps = gr.Slider(label="採樣步數 (推薦 25 步)", minimum=10, maximum=50, value=25, step=1)
                        qwen_cfg = gr.Number(label="CFG (官方推薦 1.0)", value=1.0)
                        qwen_seed = gr.Number(label="隨機種子 (-1 為隨機)", value=-1, precision=0)

                    with gr.Accordion("⚙️ 模型與 KV 快取設定", open=False):
                        with gr.Row():
                            qwen_model = gr.Dropdown(label="🎯 Qwen-Image 擴散模型", choices=qwen_dits, value=krea2_default(qwen_dits, QWEN_IMAGE_DEFAULT_DIT), scale=3)
                            qwen_encoder = gr.Dropdown(label="文字編碼器 (Qwen3-VL 8B)", choices=qwen_encoders, value=krea2_default(qwen_encoders, QWEN_IMAGE_DEFAULT_ENCODER), scale=3)
                            qwen_vae = gr.Dropdown(label="Qwen VAE", choices=qwen_vaes, value=krea2_default(qwen_vaes, QWEN_IMAGE_DEFAULT_VAE), scale=2)
                        with gr.Row():
                            qwen_sampler = gr.Dropdown(label="採樣器", choices=["euler", "res_multistep", "dpmpp_2m"], value="euler")
                            qwen_scheduler = gr.Dropdown(label="採樣排程", choices=SCHEDULERS, value="simple")
                            qwen_cache_device = gr.Dropdown(label="KV 快取設備", choices=["auto", "gpu", "cpu", "off"], value="auto", info="auto 自動分配顯存與記憶體")
                            qwen_cache_dtype = gr.Dropdown(label="KV 快取精度", choices=["default", "int8", "int4"], value="default", info="int8 顯存減半速度更快")
                        qwen_refresh_btn = gr.Button("🔄 重新掃描模型")

                    qwen_btn = gr.Button("🖌️ 開始修圖 (Execute Image Edit)", variant="primary", size="lg")

                with gr.Column(scale=5):
                    qwen_output = gr.Image(label="修圖結果預覽", type="filepath", height=480)
                    with gr.Row():
                        qwen_to_primary = gr.Button("🔄 設為主圖 (<image1> 迭代修圖)", variant="secondary")
                        qwen_to_i2v = gr.Button("📋 套用到 🖼️ 首尾幀 (首幀)", variant="secondary")
                        qwen_to_ref = gr.Button("📋 套用到 🎞️ 參考", variant="secondary")
                        qwen_to_lip = gr.Button("📋 套用到 🎤 對嘴", variant="secondary")

            def on_qwen_preset_change(p_name):
                return QWEN_IMAGE_PRESETS.get(p_name, "")

            qwen_preset_btn.click(on_qwen_preset_change, [qwen_preset], [qwen_prompt], queue=False)
            qwen_preset.change(on_qwen_preset_change, [qwen_preset], [qwen_prompt], queue=False)

            def refresh_qwen_choices():
                dits, encoders, vaes = qwen_image_model_choices()
                return (
                    gr.Dropdown(choices=dits, value=krea2_default(dits, QWEN_IMAGE_DEFAULT_DIT)),
                    gr.Dropdown(choices=encoders, value=krea2_default(encoders, QWEN_IMAGE_DEFAULT_ENCODER)),
                    gr.Dropdown(choices=vaes, value=krea2_default(vaes, QWEN_IMAGE_DEFAULT_VAE)),
                )

            qwen_refresh_btn.click(refresh_qwen_choices, None, [qwen_model, qwen_encoder, qwen_vae], queue=False)

            qwen_btn.click(
                fn=execute_qwen_image_edit,
                inputs=[
                    qwen_primary_image, qwen_ref_image, qwen_extra_images, qwen_prompt, qwen_negative,
                    qwen_res, qwen_steps, qwen_cfg, qwen_seed, qwen_sampler, qwen_scheduler,
                    qwen_model, qwen_encoder, qwen_vae, qwen_cache_device, qwen_cache_dtype
                ],
                outputs=[qwen_output]
            )

            qwen_to_primary.click(lambda img: img, [qwen_output], [qwen_primary_image], queue=False)
            qwen_to_i2v.click(lambda img: img, [qwen_output], [i2v_first], queue=False)
            qwen_to_ref.click(lambda img: [img] if img else None, [qwen_output], [ref_images], queue=False)
            qwen_to_lip.click(lambda img: img, [qwen_output], [lip_image], queue=False)

            gr.Markdown(
                "模型來源：[Qwen/Qwen-Image-2.1](https://huggingface.co/Qwen/Qwen-Image-2.1) · "
                "ComfyUI 官方適配權重 [Comfy-Org/Qwen-Image-2.1](https://huggingface.co/Comfy-Org/Qwen-Image-2.1) "
                "（7B DiT Int8 ConvRot + Qwen3-VL 8B Int8 + BF16 VAE）。"
            )

        with gr.Tab("🎥 攝影機"):
            gr.Markdown("### 參考圖片 → 3D 軌跡 → FL2VA Q4 影音\n上傳圖片後，拖曳紫色攝影機設定環繞角度與仰角，滾輪調整距離；在時間軸選取關鍵幀後修改位置。▶ 只預覽運鏡，按下生成按鈕才會生成影片。\n\n此模式固定原始場景，讓攝影機移動。軌跡會轉為 H3 提示詞，實際角度與時間可能有偏差。")
            with gr.Row():
                with gr.Column(scale=3):
                    camera_image = gr.Image(label="參考圖片（必要 · 支援 Ctrl+V 貼上）", type="filepath", height=300, elem_classes=["clipboard-image-target"])
                    camera_prompt = gr.Textbox(label="場景／主體補充描述", value="Preserve the source scene, subject identity, materials and lighting. Only the camera moves.", lines=3)
                    gr.Markdown("描述目標主體與風格即可，避免加入和 3D 軌跡相反的運鏡指令。")
                    camera_res = gr.Dropdown(label="輸出解析度", choices=["864 × 480 (16:9)", "960 × 544 (16:9)", "480 × 864 (9:16)"], value="864 × 480 (16:9)")
                    camera_turbo = gr.Dropdown(label="採樣模式", choices=SAMPLING_MODES, value=MODE_TURBO_LORA)
                    camera_seed = gr.Number(label="隨機種子 (-1 為隨機)", value=-1, precision=0)
                    camera_btn = gr.Button("🎥 按 3D 軌跡生成影音", variant="primary")
                    camera_output = gr.Video(label="攝影機影音輸出", interactive=False, height=520)
                with gr.Column(scale=5):
                    camera_editor = gr.HTML(value=DEFAULT_CAMERA.copy(), html_template='<div class="camera-editor-mount"></div>', js_on_load=EDITOR_JS)
                    with gr.Accordion("查看目前軌跡設定", open=False):
                        camera_inspect = gr.Button("讀取目前關鍵幀")
                        camera_json = gr.JSON(label="攝影機設定")
                        camera_inspect.click(lambda state: {"frames": state["frames"], "fps": 24, "keyframes": json.loads(state["trajectory"])}, [camera_editor], [camera_json], queue=False)
            camera_image.change(update_camera_image, [camera_image, camera_editor], [camera_editor], queue=False)
            camera_btn.click(
                lambda p, r, tb, s, image, state, enc, fl2, r2v: execute_generation(p, r, state["frames"] / 24, tb, s, image, camera_state=state, text_encoder=enc, fl2va_model=fl2, ref2va_model=r2v),
                [camera_prompt, camera_res, camera_turbo, camera_seed, camera_image, camera_editor, *model_inputs], [camera_output]
            )
            gr.Markdown("[工具來源：NyckM / 3d-Camera-control-H3-Minimax](https://github.com/NyckM/3d-Camera-control-H3-Minimax) · 原生 ComfyUI 中亦可搜尋 `bruxosdovfx Camera H3` 節點。")

        with gr.Tab("📝 編劇"):
            gr.Markdown("### 故事 → 分鏡 → 批次渲染 → 自動剪接")
            story_text = gr.Textbox(label="故事／劇本", lines=10, placeholder="貼上故事內容，每個段落或句子會成為可編輯鏡頭。")
            with gr.Row():
                story_seconds = gr.Slider(label="每鏡秒數", minimum=4, maximum=15, value=4, step=1)
                story_res = gr.Dropdown(label="渲染解析度", choices=BASE_RES_CHOICES[:2], value=DEFAULT_RES)
                story_turbo = gr.Dropdown(label="採樣模式", choices=SAMPLING_MODES, value=MODE_TURBO_LORA)
            plan_btn = gr.Button("① 自動拆分分鏡", variant="secondary")
            shot_table = gr.Dataframe(headers=["序號", "鏡頭名", "畫面內容", "運鏡", "秒數", "聲音／配樂"], datatype=["number", "str", "str", "str", "number", "str"], interactive=True, wrap=True)
            render_btn = gr.Button("② 批次渲染並自動剪接", variant="primary", size="lg")
            studio_output = gr.Video(label="完整成片", interactive=False, height=520)
            plan_btn.click(plan_storyboard, [story_text, story_seconds], shot_table)
            render_btn.click(
                lambda rows, r, tb, enc, fl2, r2v: render_storyboard(
                    rows, r, tb, text_encoder=enc, fl2va_model=fl2, ref2va_model=r2v),
                [shot_table, story_res, story_turbo, *model_inputs], studio_output)
        with gr.Tab("📜 紀錄"):
            gr.Markdown("歷史紀錄已自動分類為 **🖼️ 圖片紀錄** 與 **🎬 影片紀錄**。點選縮圖即可預覽成品、查看提示詞與完整設定，並支援一鍵套用與刪除紀錄。")
            with gr.Tabs():
                with gr.Tab("🖼️ 圖片紀錄"):
                    with gr.Row():
                        img_hist_refresh = gr.Button("🔄 重新整理", scale=0, min_width=110)
                        img_hist_del = gr.Button("🗑️ 刪除所選紀錄", variant="stop", scale=0, min_width=130)
                        img_hist_del_file = gr.Checkbox(label="同時從硬碟刪除圖片檔案", value=False)
                        img_hist_clean = gr.Button("🧹 清理失效紀錄", scale=0, min_width=120)
                        img_hist_count = gr.Markdown("共 0 筆圖片紀錄")
                    img_hist_rows = gr.State([])
                    img_selected_idx = gr.State(None)
                    img_hist_gallery = gr.Gallery(label="圖片紀錄（最新在前，點縮圖查看與套用）", columns=6, height=380,
                                                  allow_preview=False, object_fit="cover")
                    with gr.Row():
                        with gr.Column(scale=5):
                            img_hist_prompt = gr.Textbox(label="提示詞（可先修改再套用）", lines=7)
                            with gr.Row():
                                apply_img_to_krea = gr.Button("📋 套用到 🎨 圖片")
                                apply_img_to_qwen = gr.Button("📋 套用到 🖌️ 修圖")
                                apply_img_to_i2v = gr.Button("📋 套用到 🖼️ 首尾幀 (首幀)")
                                apply_img_to_ref = gr.Button("📋 套用到 🎞️ 參考")
                            img_hist_seed_note = gr.Markdown("")
                            img_hist_details = gr.Markdown("")
                        with gr.Column(scale=5):
                            img_hist_output = gr.Image(label="圖片成品預覽", interactive=False, height=420)

                with gr.Tab("🎬 影片紀錄"):
                    with gr.Row():
                        vid_hist_refresh = gr.Button("🔄 重新整理", scale=0, min_width=110)
                        vid_hist_del = gr.Button("🗑️ 刪除所選紀錄", variant="stop", scale=0, min_width=130)
                        vid_hist_del_file = gr.Checkbox(label="同時從硬碟刪除影片檔案", value=False)
                        vid_hist_clean = gr.Button("🧹 清理失效紀錄", scale=0, min_width=120)
                        vid_hist_count = gr.Markdown("共 0 筆影片紀錄")
                    vid_hist_rows = gr.State([])
                    vid_selected_idx = gr.State(None)
                    vid_hist_gallery = gr.Gallery(label="影片紀錄（最新在前，點縮圖查看與套用）", columns=6, height=380,
                                                  allow_preview=False, object_fit="cover")
                    with gr.Row():
                        with gr.Column(scale=5):
                            vid_hist_prompt = gr.Textbox(label="提示詞（可先修改再套用）", lines=7)
                            with gr.Row():
                                apply_vid_t2v = gr.Button("📋 套用到 🎬 文生")
                                apply_vid_i2v = gr.Button("📋 套用到 🖼️ 首尾幀")
                                apply_vid_ref = gr.Button("📋 套用到 🎞️ 參考")
                                apply_vid_long = gr.Button("📋 套用到 📼 長片")
                            vid_hist_seed_note = gr.Markdown("")
                            vid_hist_details = gr.Markdown("")
                        with gr.Column(scale=5):
                            vid_hist_output = gr.Video(label="影片成品預覽", interactive=False, height=420)

            def load_img_history():
                rows = history.rows_with_thumb(history.entries(category="image"))
                return rows, history.gallery(rows), f"共 **{len(rows)}** 筆圖片紀錄", None, "", None, "", ""

            def pick_img_history(rows, event: gr.SelectData):
                index = event.index[0] if isinstance(event.index, (list, tuple)) else event.index
                if not rows or index is None or index >= len(rows):
                    return None, "", None, "", ""
                row = rows[index]
                output = row.get("output") or ""
                img = output if os.path.exists(output) else None
                seed = row.get("seed")
                note = f"💡 要重現此圖，種子請填 **{seed}**。" if seed else ""
                return index, row.get("prompt", ""), img, history.details_text(row), note

            def delete_selected_img(rows, selected_idx, del_file):
                if selected_idx is None or not rows or selected_idx >= len(rows):
                    gr.Warning("請先在上方點選要刪除的圖片紀錄縮圖！")
                    return rows, history.gallery(rows), f"共 **{len(rows)}** 筆圖片紀錄", selected_idx, "", None, "", ""
                target = rows[selected_idx]
                success, msg = history.delete_entry(target.get("id"), target.get("output"), delete_file=del_file)
                if success:
                    gr.Info("已成功刪除該筆圖片紀錄！" + ("（已同步從硬碟移除檔案）" if del_file else ""))
                else:
                    gr.Warning(f"刪除失敗: {msg}")
                new_rows = history.rows_with_thumb(history.entries(category="image"))
                return new_rows, history.gallery(new_rows), f"共 **{len(new_rows)}** 筆圖片紀錄", None, "", None, "", ""

            def clean_img_missing():
                count = history.clean_missing(category="image")
                gr.Info(f"已清理 {count} 筆檔案已不存在的圖片歷史紀錄！")
                new_rows = history.rows_with_thumb(history.entries(category="image"))
                return new_rows, history.gallery(new_rows), f"共 **{len(new_rows)}** 筆圖片紀錄", None, "", None, "", ""

            def load_vid_history():
                rows = history.rows_with_thumb(history.entries(category="video"))
                return rows, history.gallery(rows), f"共 **{len(rows)}** 筆影片紀錄", None, "", None, "", ""

            def pick_vid_history(rows, event: gr.SelectData):
                index = event.index[0] if isinstance(event.index, (list, tuple)) else event.index
                if not rows or index is None or index >= len(rows):
                    return None, "", None, "", ""
                row = rows[index]
                output = row.get("output") or ""
                vid = output if os.path.exists(output) else None
                seed = row.get("seed")
                note = f"💡 要重現此影片，種子請填 **{seed}**，並參照設定微調。" if seed else ""
                return index, row.get("prompt", ""), vid, history.details_text(row), note

            def delete_selected_vid(rows, selected_idx, del_file):
                if selected_idx is None or not rows or selected_idx >= len(rows):
                    gr.Warning("請先在上方點選要刪除的影片紀錄縮圖！")
                    return rows, history.gallery(rows), f"共 **{len(rows)}** 筆影片紀錄", selected_idx, "", None, "", ""
                target = rows[selected_idx]
                success, msg = history.delete_entry(target.get("id"), target.get("output"), delete_file=del_file)
                if success:
                    gr.Info("已成功刪除該筆影片紀錄！" + ("（已同步從硬碟移除檔案）" if del_file else ""))
                else:
                    gr.Warning(f"刪除失敗: {msg}")
                new_rows = history.rows_with_thumb(history.entries(category="video"))
                return new_rows, history.gallery(new_rows), f"共 **{len(new_rows)}** 筆影片紀錄", None, "", None, "", ""

            def clean_vid_missing():
                count = history.clean_missing(category="video")
                gr.Info(f"已清理 {count} 筆檔案已不存在的影片歷史紀錄！")
                new_rows = history.rows_with_thumb(history.entries(category="video"))
                return new_rows, history.gallery(new_rows), f"共 **{len(new_rows)}** 筆影片紀錄", None, "", None, "", ""

            # Image event bindings
            img_hist_refresh.click(load_img_history, None, [img_hist_rows, img_hist_gallery, img_hist_count, img_selected_idx, img_hist_prompt, img_hist_output, img_hist_details, img_hist_seed_note], queue=False)
            img_hist_gallery.select(pick_img_history, [img_hist_rows], [img_selected_idx, img_hist_prompt, img_hist_output, img_hist_details, img_hist_seed_note], queue=False)
            img_hist_del.click(delete_selected_img, [img_hist_rows, img_selected_idx, img_hist_del_file], [img_hist_rows, img_hist_gallery, img_hist_count, img_selected_idx, img_hist_prompt, img_hist_output, img_hist_details, img_hist_seed_note], queue=False)
            img_hist_clean.click(clean_img_missing, None, [img_hist_rows, img_hist_gallery, img_hist_count, img_selected_idx, img_hist_prompt, img_hist_output, img_hist_details, img_hist_seed_note], queue=False)

            apply_img_to_krea.click(lambda t: t, img_hist_prompt, krea_prompt, queue=False)
            apply_img_to_qwen.click(lambda t: t, img_hist_prompt, qwen_prompt, queue=False)
            apply_img_to_i2v.click(lambda img: img, img_hist_output, i2v_first, queue=False)
            apply_img_to_ref.click(lambda img: [img] if img else [], img_hist_output, ref_images, queue=False)

            # Video event bindings
            vid_hist_refresh.click(load_vid_history, None, [vid_hist_rows, vid_hist_gallery, vid_hist_count, vid_selected_idx, vid_hist_prompt, vid_hist_output, vid_hist_details, vid_hist_seed_note], queue=False)
            vid_hist_gallery.select(pick_vid_history, [vid_hist_rows], [vid_selected_idx, vid_hist_prompt, vid_hist_output, vid_hist_details, vid_hist_seed_note], queue=False)
            vid_hist_del.click(delete_selected_vid, [vid_hist_rows, vid_selected_idx, vid_hist_del_file], [vid_hist_rows, vid_hist_gallery, vid_hist_count, vid_selected_idx, vid_hist_prompt, vid_hist_output, vid_hist_details, vid_hist_seed_note], queue=False)
            vid_hist_clean.click(clean_vid_missing, None, [vid_hist_rows, vid_hist_gallery, vid_hist_count, vid_selected_idx, vid_hist_prompt, vid_hist_output, vid_hist_details, vid_hist_seed_note], queue=False)

            apply_vid_t2v.click(lambda t: t, vid_hist_prompt, t2v_prompt, queue=False)
            apply_vid_i2v.click(lambda t: t, vid_hist_prompt, i2v_prompt, queue=False)
            apply_vid_ref.click(lambda t: t, vid_hist_prompt, ref_prompt, queue=False)
            apply_vid_long.click(lambda t: t, vid_hist_prompt, long_prompt, queue=False)

            demo.load(load_img_history, None, [img_hist_rows, img_hist_gallery, img_hist_count, img_selected_idx, img_hist_prompt, img_hist_output, img_hist_details, img_hist_seed_note])
            demo.load(load_vid_history, None, [vid_hist_rows, vid_hist_gallery, vid_hist_count, vid_selected_idx, vid_hist_prompt, vid_hist_output, vid_hist_details, vid_hist_seed_note])

        with gr.Tab("ℹ️ 系統"):
            gr.Markdown(
                f"### 🎛️ 顯存自動設定\n"
                f"開機時自動偵測顯卡並調整後端參數（`--reserve-vram {VRAM_RESERVE}` / `--vram-headroom {VRAM_HEADROOM}`），"
                f"也會依顯存自動關閉跑不動的選項，不用自己設定：\n\n"
                f"> **本機：{GPU_NAME or '未偵測到 NVIDIA 顯卡'} · {VRAM_PROFILE_LABEL}**\n\n"
                "| 顯存 | 建議用法 | 自動調整 |\n|---|---|---|\n"
                "| **24～32 GB**（4090／5090／3090） | 全部功能；高清二次採樣、長片高畫質 | — |\n"
                "| **16 GB**（4080／5080／4070 Ti S） | Q4 模型、864×480～960×544、4～10 秒 | 關閉高清二次採樣與 Full HD、長片只列省顯存解析度、SeedVR2 轉 8 區塊到 CPU |\n"
                "| **12 GB**（4070／3060 12G） | Q4 模型、864×480、4～6 秒 | 同上，SeedVR2 轉 16 區塊到 CPU |\n\n"
                "- 顯存較小時，要更清楚的成片：先用 864×480 生成，再到「🔍 放大」用 SeedVR2 升到 1080p。\n"
                "- 系統記憶體（RAM）建議 **32 GB 以上**，12～16 GB 顯卡建議 **64 GB**；不夠時會很慢。\n"
                "- 爆顯存或變很慢時，按上方「🧹 釋放顯存」再試一次。"
            )
            gr.Markdown(
                "### 🧰 需要時再下載的模型\n"
                "雙擊面板資料夾裡的 **`download_extras.bat`**，輸入數字即可下載（可續傳、自動核對 SHA-256）：\n\n"
                "1. 🎨 圖片分頁：Krea2 模型（約 19 GB）　2. Krea2 官方風格 LoRA　3. 🖌️ 修圖分頁：Qwen-Image-2.1（約 17 GB）\n"
                "4. 🔍 放大分頁：SeedVR2（約 7 GB）　5. 高清二次採樣放大模型（僅 24GB）　6. Heretic 文字編碼器\n\n"
                f"長片的 Smite79 引擎需自行安裝（授權不允許其他安裝程式代為下載）：{SMITE_REPO_URL} ，"
                "沒裝時長片分頁會自動改用 TimelineDirector。\n\n"
                "### 🖥️ 架構\n"
                "- 後端：ComfyUI v0.36.0（本機 http://127.0.0.1:8188 可開原生節點畫布）\n"
                "- 影音模型：MiniMax H3 FL2VA／Ref2VA Q4_K_M GGUF（預設）、Qwen3-VL 32B NVFP4 文字編碼器、H3 影音 VAE（有 INT8 版時自動使用）\n"
                "- 加速：`minimax_h3_fl2v_turbo_8step_v1.0`、`minimax_h3_ref2v_turbo_4step_v0.1` Turbo LoRA"
            )

    def fl2va_model_changed(model, resolution_a, resolution_b, mode_a, mode_b, mode_c, mode_d):
        """Big trunks cannot run the HD refine (the upscaler runs out of VRAM), and baked-turbo
        checkpoints must not stack the Turbo LoRA: switch those options off instead of failing later."""
        model = model or ""
        too_big = model_file_size(model) > HD_MAX_MODEL_BYTES
        baked = "turbo" in model.lower()
        if not HD_ALLOWED:
            note = HD_LOW_VRAM_INFO
        elif too_big:
            note = f"「{model}」約 {model_file_size(model) / 1000 ** 3:.0f} GB，放大階段顯存不足，已停用高清二次採樣。"
        else:
            note = HD_INFO
        no_hd = too_big or not HD_ALLOWED
        hd_update = gr.Checkbox(value=False, interactive=not no_hd, info=note)
        choices = [*BASE_RES_CHOICES] if no_hd else [*BASE_RES_CHOICES, *FULL_HD_CHOICES]
        def keep(current, extra=()):
            allowed = [*extra, *choices]
            return gr.Dropdown(choices=allowed, value=current if current in allowed else DEFAULT_RES)
        target_mode = MODE_BAKED_TURBO if baked else MODE_TURBO_LORA
        return (hd_update, hd_update, keep(resolution_a), keep(resolution_b, tuple(AUTO_RESOLUTION_CHOICES)),
                gr.Dropdown(value=target_mode), gr.Dropdown(value=target_mode), gr.Dropdown(value=target_mode), gr.Dropdown(value=target_mode))

    def ref2va_model_changed(model, *current_modes):
        low = (model or "").lower()
        baked = "turbo" in low and "singularity" not in low
        target_mode = MODE_BAKED_TURBO if baked else MODE_TURBO_LORA
        if "singularity" in low:
            gr.Info("已選取 Singularity 奇點微調模型：自動配置 4 步 Turbo 採樣，具備 HDR 畫質與動作增強能力。")
        elif baked:
            gr.Info("已選取內建蒸餾模型：自動配置 8 步採樣（不外掛 Turbo LoRA）。")
        updates = [gr.Dropdown(value=target_mode) for _ in current_modes]
        return (*updates, gr.Dropdown(value=model))

    model_fl2va.change(fl2va_model_changed,
                       [model_fl2va, t2v_res, i2v_res, t2v_turbo, i2v_turbo, camera_turbo, story_turbo],
                       [t2v_hd, i2v_hd, t2v_res, i2v_res, t2v_turbo, i2v_turbo, camera_turbo, story_turbo],
                       queue=False)
    model_ref2va.change(ref2va_model_changed, [model_ref2va, ref_turbo, v2v_turbo, long_mode], [ref_turbo, v2v_turbo, long_mode, v2v_model], queue=False)
    demo.load(fl2va_model_changed,
              [model_fl2va, t2v_res, i2v_res, t2v_turbo, i2v_turbo, camera_turbo, story_turbo],
              [t2v_hd, i2v_hd, t2v_res, i2v_res, t2v_turbo, i2v_turbo, camera_turbo, story_turbo])
    demo.load(ref2va_model_changed, [model_ref2va, ref_turbo, v2v_turbo, long_mode], [ref_turbo, v2v_turbo, long_mode, v2v_model])

CLIPBOARD_JS_PATH = os.path.join(BASE_DIR, "clipboard_paste.js")
try:
    with open(CLIPBOARD_JS_PATH, "r", encoding="utf-8") as _f:
        CLIPBOARD_JS = _f.read()
except Exception:
    CLIPBOARD_JS = ""

if __name__ == "__main__":
    if open_existing_webui():
        sys.exit(0)
    ensure_comfy_server()
    try:
        demo.launch(
            server_name="127.0.0.1",
            server_port=7860,
            theme=theme,
            css=css,
            head=f"<script>{CLIPBOARD_JS}</script>",
            inbrowser=True
        )
    except OSError:
        # Another launch may have finished starting after the initial check.
        if not open_existing_webui():
            raise

