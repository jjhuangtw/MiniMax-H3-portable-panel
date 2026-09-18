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
from prompt_library import PROMPT_CATEGORIES
from prompt_reference import OFFICIAL_GUIDE_CATEGORIES
from prompt_examples import OFFICIAL_FORMAT_EXAMPLES
from long_examples import LONG_VIDEO_EXAMPLES
from media_tools import AUTO_RESOLUTION_CHOICES, auto_canvas, has_audio_stream, media_duration, mux_original_audio, prepare_reference_video
import history
from prompt_builder import (AUDIO_MODE_COPY, AUDIO_MODE_REFERENCE, add_base_prompt_builder, add_ref_prompt_builder,
                            label_table, reference_labels, with_keyframe_instruction)
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
# Krea2 image stack (separate architecture from H3: Qwen3-VL 4B encoder, Qwen image VAE).
KREA2_HIGH_MODEL = "redcraft_krea2_dual_high.safetensors"
KREA2_LOW_MODEL = "redcraft_krea2_dual_low.safetensors"
KREA2_TEXT_ENCODER = "qwen3vl_4b_fp8_scaled.safetensors"
KREA2_VAE = "qwen_image_vae.safetensors"
KREA2_TURBO_LORA = "krea2_turbo_lora_rank_64_bf16.safetensors"
# RedCraft's own DUAL schedule: a short high-noise pass, then the low-noise model finishes the image.
KREA2_HIGH_SIGMAS = "1, 0.956724, 0"
KREA2_LOW_SIGMAS = "0.95, 0.904531, 0.840349, 0.759511, 0.654567, 0.512844, 0.310901, 0"
KREA2_SIZES = ["1024 × 1024 (1:1)", "1024 × 1536 (2:3 直式)", "1536 × 1024 (3:2 橫式)",
               "1152 × 896 (4:3)", "896 × 1152 (3:4)", "1344 × 768 (16:9)", "768 × 1344 (9:16)"]
KREA2_SAMPLERS = ["er_sde", "euler", "dpmpp_2m", "res_multistep"]
# Style / original-character LoRAs for Krea2 live in their own subfolder so they never mix with H3 LoRAs.
KREA2_LORA_SUBDIR = "krea2"
KREA2_LORA_SLOTS = 3
THUMB_EXTENSIONS = (".preview.png", ".png", ".jpg", ".jpeg", ".webp")
THUMB_DIR = os.path.join(BASE_DIR, "lora_thumbs")
# A neutral still life: the thumbnail shows a LoRA's rendering style without depicting anyone.
THUMB_PROMPT = "a still life of a ceramic teapot, lemons and a small vase of flowers on a wooden table beside a window, soft daylight"
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
FULL_HD_CHOICES = [
    "1920 × 1088 (16:9 Full HD · 需勾選高清二次採樣)",
    "1088 × 1920 (9:16 直式 Full HD · 需勾選高清二次採樣)",
]
BASE_RES_CHOICES = [
    "864 × 480 (16:9 標清 · 4090 推薦極速不爆顯存)",
    "960 × 544 (16:9 中清 · 4090 兼顧品質)",
    "1056 × 608 (16:9 高清)",
    "1280 × 704 (16:9 超清 · 需較多顯存)",
    "1344 × 768 (16:9 原生官方上限)",
    "480 × 864 (9:16 直式短影音 · 4090 推薦)",
    "768 × 1344 (9:16 直式短影音 · 高清)",
]
DEFAULT_RES = BASE_RES_CHOICES[0]
# Above the official 1344×768 area a single pass is untrained and too heavy for 24 GB.
SINGLE_PASS_MAX_PIXELS = 1344 * 768

comfy_process = None

def open_existing_webui():
    url = "http://127.0.0.1:7860"
    try:
        response = requests.get(f"{url}/config", timeout=3)
        response.raise_for_status()
        if response.json().get("title") != "MiniMax H3 Portable - RTX 4090":
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

def ensure_comfy_server():
    global comfy_process
    if is_comfy_running():
        return True
    
    print("[WebUI] Starting ComfyUI backend server...")
    cmd = [
        PYTHON_EXE,
        "main.py",
        "--listen", "127.0.0.1",
        "--port", "8188",
        "--fast", "fp8_matrix_mult", "fp16_accumulation",
        "--reserve-vram", "2.5",
        "--vram-headroom", "3",
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

def resolve_backend_file(node_type, input_name, name, what):
    """Map a chosen file to the backend's spelling (path separators differ on Windows)."""
    wanted = name.replace("\\", "/")
    for choice in backend_choices(node_type, input_name):
        if choice.replace("\\", "/") == wanted:
            return choice
    raise gr.Error(f"後端找不到{what}「{name}」。若剛下載完成，請執行 restart_webui.bat 後再試。")

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

def split_segment_prompts(text):
    return [part.strip() for part in re.split(r"^\s*---+\s*$", text or "", flags=re.MULTILINE) if part.strip()]

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
    mode=MODE_TURBO_LORA,
    ref_image_file=None,
    scheduler="simple",
    text_encoder=None,
    lora_name=None,
    lora_strength=1.0,
    fl2va_model=None,
    ref2va_model=None,
    progress=gr.Progress()
):
    segment_prompts = split_segment_prompts(segment_prompts_text)
    if not segment_prompts and not (global_prompt and global_prompt.strip()):
        raise gr.Error("請輸入全域提示詞，或填寫分段提示詞！")
    windows = plan_long_segments(total_seconds, segment_seconds, LONG_OVERLAP_FRAMES, len(segment_prompts))

    progress(0.05, desc="正在連線至 MiniMax H3 引擎...")
    if not ensure_comfy_server():
        raise gr.Error("無法啟動或連線至 ComfyUI 後端引擎，請檢查 8188 埠！")
    response = requests.get(f"{COMFY_URL}/object_info/MiniMaxH3FiniteSegmentSampler", timeout=10)
    if "MiniMaxH3FiniteSegmentSampler" not in response.json():
        raise gr.Error("後端尚未載入長片節點（TimelineDirector）。請執行 restart_webui.bat 後再試。")
    model_options = resolve_model_options(text_encoder, lora_name, lora_strength, fl2va_model, ref2va_model)

    width, height = parse_resolution(resolution_str)
    check_generation_limits(model_options["ref2va_model"], model_options["lora_name"], mode, False, width, height, 0, "ref2va")
    ref_image_name = upload_image(ref_image_file) if ref_image_file else None
    if ref_image_name:
        prompts = segment_prompts or [global_prompt]
        if not all("<picture" in p.lower() for p in prompts):
            raise gr.Error("已上傳角色參考圖：每段提示詞（或全域提示詞）都要用 <Picture 1> 指定該角色。")

    if seed is None or seed == -1:
        import random
        seed = random.randint(1, 1000000000000000)

    progress(0.15, desc=f"正在準備 {len(windows)} 段長片圖譜...")
    prompt_graph = build_long_video_prompt(
        global_prompt=(global_prompt or "").strip(),
        segment_prompts=segment_prompts,
        windows=windows,
        width=width,
        height=height,
        seed=int(seed),
        ref_image_name=ref_image_name,
        scheduler=scheduler,
        mode=mode,
        **model_options
    )
    output_video_path = run_comfy_workflow(prompt_graph, mode_settings(mode)[1], progress, "RTX 4090 正在載入 Ref2VA 模型...",
                                           "長片採樣", segments=len(windows))
    history.record("長片", global_prompt or "\n---\n".join(segment_prompts), output_video_path,
                   resolution=f"{width}×{height}", seconds=round(windows[-1][1] / 24, 2), seed=int(seed),
                   mode=mode if isinstance(mode, str) else None, scheduler=scheduler,
                   model=model_options["ref2va_model"], encoder=model_options["text_encoder"],
                   lora=model_options["lora_name"], lora_strength=model_options["lora_strength"] if model_options["lora_name"] else None)
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
        files = [f for f in files if "ref2va" not in f.lower() and "ref2v" not in f.lower()]
    elif trunk == "ref2va":
        files = [f for f in files if "fl2va" not in f.lower() and "fl2v" not in f.lower()]
    return files

def model_label_choices(models):
    """(display, value) pairs: append a short type hint after each option; value stays the filename."""
    def hint(name):
        low = name.lower()
        if "int8_convrot" in low:
            return "INT8・畫質較好但較慢、吃顯存"
        if "q4_k_m" in low or "-q4" in low:
            return "Q4・最省顯存、最快、推薦"
        if "dasiwa" in low or "hybrid" in low:
            return "DaSiwa 混合・內建蒸餾（採樣選 8 步）"
        return ""
    return [(f"{m}  —  {hint(m)}" if hint(m) else m, m) for m in models]


def model_file_size(model_name):
    for folder in model_dirs("diffusion_models"):
        candidate = os.path.join(folder, model_name.replace("/", os.sep))
        if os.path.exists(candidate):
            return os.path.getsize(candidate)
    return 0

def check_generation_limits(model_name, lora_name, mode, hd, width, height, duration, trunk):
    """Refuse combinations that crashed the backend before, and warn about mismatched pairings."""
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
    return [f for f in list_model_files("diffusion_models", "UNETLoader", "unet_name")
            if f.endswith(".safetensors") and is_krea2_model(f)]

def krea2_default(choices, preferred):
    return preferred if preferred in choices else (choices[0] if choices else preferred)

def krea2_style_loras():
    # Style / original-character LoRAs only. The `*_krea2.safetensors` naming is the real-person
    # celebrity set the user dropped in; this panel does not surface named real people, so it is
    # skipped here. Not a lock — a rename bypasses it; original-character LoRAs should avoid that suffix.
    prefix = KREA2_LORA_SUBDIR + "/"
    return sorted(f for f in list_model_files("loras", "LoraLoaderModelOnly", "lora_name")
                  if f.endswith(".safetensors") and f.replace("\\", "/").startswith(prefix)
                  and not os.path.basename(f).endswith("_krea2.safetensors"))

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

def build_krea2_prompt(prompt_text, width, height, batch, seed, high_model, low_model, dual,
                       lora_name, high_lora_strength, low_lora_strength, sampler,
                       high_sigmas, low_sigmas, steps, scheduler, cfg, text_encoder, vae, extra_loras=()):
    """RedCraft DUAL: the high-noise weight opens the image, the low-noise weight finishes it."""
    workflow = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": high_model, "weight_dtype": "default"}},
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": text_encoder, "type": "krea2"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": vae}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["3", 0], "text": prompt_text}},
        "8": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["7", 0]}},
        "9": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": batch}},
        "10": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": sampler}},
    }
    high_node = ["1", 0]
    if lora_name and high_lora_strength:
        workflow["5"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": lora_name, "strength_model": high_lora_strength}}
        high_node = ["5", 0]
    for index, (name, strength) in enumerate(extra_loras):
        workflow[f"3{index}"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"model": high_node, "lora_name": name, "strength_model": strength}}
        high_node = [f"3{index}", 0]

    if dual:
        workflow["2"] = {"class_type": "UNETLoader", "inputs": {"unet_name": low_model, "weight_dtype": "default"}}
        low_node = ["2", 0]
        if lora_name and low_lora_strength:
            workflow["6"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["2", 0], "lora_name": lora_name, "strength_model": low_lora_strength}}
            low_node = ["6", 0]
        for index, (name, strength) in enumerate(extra_loras):
            workflow[f"4{index}"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"model": low_node, "lora_name": name, "strength_model": strength}}
            low_node = [f"4{index}", 0]
        workflow["11"] = {"class_type": "ManualSigmas", "inputs": {"sigmas": high_sigmas}}
        workflow["12"] = {"class_type": "ManualSigmas", "inputs": {"sigmas": low_sigmas}}
        workflow["13"] = {"class_type": "SamplerCustom", "inputs": {
            "model": high_node, "add_noise": True, "noise_seed": seed, "cfg": cfg,
            "positive": ["7", 0], "negative": ["8", 0], "sampler": ["10", 0], "sigmas": ["11", 0], "latent_image": ["9", 0]}}
        workflow["14"] = {"class_type": "SamplerCustom", "inputs": {
            "model": low_node, "add_noise": True, "noise_seed": seed + 1, "cfg": cfg,
            "positive": ["7", 0], "negative": ["8", 0], "sampler": ["10", 0], "sigmas": ["12", 0], "latent_image": ["13", 0]}}
        sampled = ["14", 0]
    else:
        workflow["20"] = {"class_type": "KSampler", "inputs": {
            "model": high_node, "positive": ["7", 0], "negative": ["8", 0], "latent_image": ["9", 0],
            "seed": seed, "steps": steps, "cfg": cfg, "sampler_name": sampler, "scheduler": scheduler, "denoise": 1.0}}
        sampled = ["20", 0]

    workflow["15"] = {"class_type": "VAEDecode", "inputs": {"samples": sampled, "vae": ["4", 0]}}
    workflow["16"] = {"class_type": "SaveImage", "inputs": {"images": ["15", 0], "filename_prefix": "Krea2_RedCraft"}}
    return workflow

def resolve_extra_loras(*slots):
    extra = []
    for name, strength in zip(slots[0::2], slots[1::2]):
        if name and name != NO_LORA and float(strength or 0):
            extra.append((resolve_backend_file("LoraLoaderModelOnly", "lora_name", name, " LoRA "), float(strength)))
    return extra

def execute_krea2_generation(prompt, size_str, batch, seed, high_model, low_model, dual, lora_name,
                             high_lora_strength, low_lora_strength, sampler, high_sigmas, low_sigmas,
                             steps, scheduler, cfg, text_encoder, vae,
                             lora_1=None, strength_1=1.0, lora_2=None, strength_2=1.0, lora_3=None, strength_3=1.0,
                             progress=gr.Progress()):
    if not prompt or not prompt.strip():
        raise gr.Error("請輸入提示詞 (Prompt)！")

    progress(0.05, desc="正在連線至 ComfyUI...")
    if not ensure_comfy_server():
        raise gr.Error("無法啟動或連線至 ComfyUI 後端引擎，請檢查 8188 埠！")
    high_model = resolve_backend_file("UNETLoader", "unet_name", high_model, "高噪模型")
    if dual:
        low_model = resolve_backend_file("UNETLoader", "unet_name", low_model, "低噪模型")
    text_encoder = resolve_backend_file("CLIPLoader", "clip_name", text_encoder, " Krea2 文字編碼器")
    vae = resolve_backend_file("VAELoader", "vae_name", vae, " Krea2 VAE")
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
        high_model=high_model, low_model=low_model, dual=bool(dual), lora_name=lora_name,
        high_lora_strength=float(high_lora_strength), low_lora_strength=float(low_lora_strength),
        sampler=sampler, high_sigmas=high_sigmas, low_sigmas=low_sigmas,
        steps=int(steps), scheduler=scheduler, cfg=float(cfg), text_encoder=text_encoder, vae=vae,
        extra_loras=extra_loras)

    total = len(low_sigmas.split(",")) - 1 if dual else int(steps)
    images = run_comfy_workflow(prompt_graph, max(1, total), progress, "RTX 4090 正在載入 Krea2 模型...",
                                "Krea2 採樣", output_node="16", multiple=True)
    history.record("圖片 Krea2", prompt, images, resolution=f"{width}×{height}", seed=int(seed),
                   mode="雙權重" if dual else "單模型", model=high_model, encoder=text_encoder,
                   lora=", ".join(f"{os.path.basename(n)}×{s}" for n, s in extra_loras) or lora_name,
                   lora_strength=None if extra_loras else (high_lora_strength if lora_name else None))
    progress(1.0, desc="圖片生成完成！")
    return images

def generate_krea2_thumbnails(high_model, text_encoder, vae, turbo_lora, only_missing=True, progress=gr.Progress()):
    only_missing = bool(only_missing)
    names = [n for n in krea2_style_loras() if not (only_missing and has_real_preview(n))]
    if not names:
        gallery, _ = krea2_lora_gallery()
        gr.Info("所有 LoRA 都已經有縮圖。")
        return gallery
    if not ensure_comfy_server():
        raise gr.Error("無法啟動或連線至 ComfyUI 後端引擎，請檢查 8188 埠！")
    high_model = resolve_backend_file("UNETLoader", "unet_name", high_model, "高噪模型")
    text_encoder = resolve_backend_file("CLIPLoader", "clip_name", text_encoder, " Krea2 文字編碼器")
    vae = resolve_backend_file("VAELoader", "vae_name", vae, " Krea2 VAE")
    turbo = resolve_backend_file("LoraLoaderModelOnly", "lora_name", turbo_lora, " Turbo LoRA ") if turbo_lora and turbo_lora != NO_LORA else None
    import shutil
    for index, name in enumerate(names, 1):
        progress((index - 1) / len(names), desc=f"產生縮圖 {index}/{len(names)}：{os.path.basename(name)}")
        graph = build_krea2_prompt(
            prompt_text=with_triggers(THUMB_PROMPT, [name]), width=512, height=512, batch=1, seed=20260916,
            high_model=high_model, low_model=high_model, dual=False, lora_name=turbo,
            high_lora_strength=0.85, low_lora_strength=0.0, sampler="er_sde", high_sigmas="", low_sigmas="",
            steps=8, scheduler="simple", cfg=1.0, text_encoder=text_encoder, vae=vae,
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
    dit_model = resolve_backend_file("SeedVR2LoadDiTModel", "model", dit_model, " SeedVR2 主模型")
    vae_model = resolve_backend_file("SeedVR2LoadVAEModel", "model", vae_model, " SeedVR2 VAE")

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
    output = run_comfy_workflow(graph, 0, progress, "RTX 4090 正在以 SeedVR2 放大影片...", "SeedVR2 放大")
    history.record("SeedVR2 放大", os.path.basename(str(video_file)), output,
                   resolution=resolution_label, seed=int(seed), model=dit_model, mode=f"每批 {int(batch_size)} 幀")
    progress(1.0, desc="影片放大完成！")
    return output

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
                        progress(pct, desc=f"RTX 4090 {stage}: 第 {done + 1}/{segments} 段 · 步數 {val}/{max_val}...")
                        if val >= max_val:
                            finished_runs += 1
                    else:
                        pct = 0.2 + (val / max_val) * 0.7
                        progress(pct, desc=f"RTX 4090 {stage}中: 步數 {val}/{max_val}...")

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
        resolve_backend_file("MinimaxH3LatentUpscaler3D", "model_name", H3_LATENT_UPSCALER, "潛空間放大模型")
        # The 3-step refine schedule only works with the distilled Turbo LoRA.
        turbo = MODE_TURBO_LORA

    width, height = resolve_resolution(resolution_str, first_frame_file or last_frame_file)
    check_generation_limits(model_options["fl2va_model"], model_options["lora_name"], turbo, hd, width, height, duration, "fl2va")
    if not hd and width * height > SINGLE_PASS_MAX_PIXELS:
        if camera_state is not None:
            raise gr.Error("3D 攝影機模式不支援超過 1344×768 的解析度。")
        gr.Info("這個解析度超過官方 1344×768，已自動使用高清二次採樣（含 Turbo）。")
        hd = True
        resolve_backend_file("MinimaxH3LatentUpscaler3D", "model_name", H3_LATENT_UPSCALER, "潛空間放大模型")
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
                                           "RTX 4090 正在載入模型與運算中...", stage)
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
    if missing:
        gr.Warning("提示詞沒有提到：" + "、".join(missing) + "。沒指定用途時，模型會自己決定怎麼用這些素材。")

    frame_count = snap_h3_length(round(duration * 24))
    if copy_audio:
        seconds = media_duration(audio_files[0])
        frame_count = snap_h3_length(math.ceil(seconds * 24))
        if frame_count > 362:
            raise gr.Error(f"音檔長 {seconds:.1f} 秒，超過 H3 單段上限約 15 秒；請先切段，或改用長片分頁。")

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
                                           "RTX 4090 正在載入 Ref2VA 模型與參考素材...", "Ref2VA 採樣")
    if copy_audio:
        progress(0.97, desc="正在把成片音軌換回原始音檔...")
        output_video_path = mux_original_audio(output_video_path, audio_files[0])
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


def execute_lipsync(image, audio, prompt, resolution_str, mode, seed,
                    text_encoder=None, lora_name=None, lora_strength=1.0,
                    fl2va_model=None, ref2va_model=None, progress=gr.Progress()):
    """One portrait + one audio -> lip-synced talking video (Ref2VA with the audio locked)."""
    if not image:
        raise gr.Error("請先上傳一張人像照片（會成為 <Picture 1>）。")
    if not audio:
        raise gr.Error("請先上傳一段要對嘴的語音（會成為 <Audio 1>）。")
    if not (prompt or "").strip():
        prompt = LIPSYNC_DEFAULT_PROMPT
    return execute_ref_generation(
        prompt, resolution_str, 5, mode, seed,
        image_files=[image], video_files=[], use_video_audio=False,
        audio_files=[audio], audio_mode=AUDIO_MODE_COPY, scheduler="simple",
        text_encoder=text_encoder, lora_name=lora_name, lora_strength=lora_strength,
        fl2va_model=fl2va_model, ref2va_model=ref2va_model, progress=progress)


def preview_reference_labels(image_files, video_files, use_video_audio, audio_files):
    video_items = [(path, bool(use_video_audio and has_audio_stream(path))) for path in (video_files or [])]
    labels = reference_labels(list(image_files or []), video_items, list(audio_files or []))
    return label_table(labels), labels


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
    high = resolve_backend_file("UNETLoader", "unet_name", krea2_default(models, KREA2_HIGH_MODEL), "Krea2 高噪模型")
    encoders = sorted({v for _, v in text_encoder_choices()} | {f for f in list_model_files("text_encoders", "CLIPLoader", "clip_name") if f.endswith(".safetensors")})
    clip = resolve_backend_file("CLIPLoader", "clip_name", krea2_default(encoders, KREA2_TEXT_ENCODER), "Krea2 文字編碼器")
    vae = resolve_backend_file("VAELoader", "vae_name", KREA2_VAE, "Krea2 VAE")
    turbo = resolve_backend_file("LoraLoaderModelOnly", "lora_name", KREA2_TURBO_LORA, "Turbo LoRA")
    os.makedirs(PROMPT_THUMB_DIR, exist_ok=True)
    for index, (name, text) in enumerate(todo, 1):
        progress((index - 1) / len(todo), desc=f"產生縮圖 {index}/{len(todo)}：{name}")
        graph = build_krea2_prompt(
            prompt_text=prompt_to_image_desc(text), width=512, height=512, batch=1, seed=20260918,
            high_model=high, low_model=high, dual=False, lora_name=turbo,
            high_lora_strength=0.85, low_lora_strength=0.0, sampler="er_sde", high_sigmas="", low_sigmas="",
            steps=8, scheduler="simple", cfg=1.0, text_encoder=clip, vae=vae)
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
.header-box { text-align: center; margin-bottom: 20px; }
.gradio-container [role="tab"] { color: #cbd5e1 !important; font-size: 16px; font-weight: 600; }
.gradio-container [role="tab"][aria-selected="true"] { color: #ffffff !important; background: #25254a !important; border-bottom: 3px solid #a5b4fc !important; }
.gradio-container [role="listbox"],
.gradio-container [role="option"] { background: #181818 !important; color: #f1f5f9 !important; }
.gradio-container [role="option"]:hover,
.gradio-container [role="option"][aria-selected="true"] { background: #34345c !important; }
.gradio-container input::placeholder,
.gradio-container textarea::placeholder { color: #64748b !important; font-style: italic; opacity: 1; }
.gradio-container :focus-visible { outline: 2px solid #a5b4fc !important; outline-offset: 2px; }
.header-title { font-size: 2.2rem; font-weight: 800; color: #c4b5fd !important; }
.header-desc { font-size: 1.05rem; color: #cbd5e1 !important; margin-top: 5px; }
"""

with gr.Blocks(title="MiniMax H3 Portable - RTX 4090") as demo:
    with gr.Column(elem_classes=["header-box"]):
        gr.HTML("<h1 class='header-title'>MiniMax H3 影音創作面板 (Portable 版)</h1>")
        gr.HTML("<p class='header-desc'>專為 NVIDIA GeForce RTX 4090 最佳化 · 本地開源無審查 · 原生立體聲同步影音生成</p>")

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
                        t2v_res = gr.Dropdown(label="畫面解析度", choices=[*BASE_RES_CHOICES, *FULL_HD_CHOICES], value=DEFAULT_RES)
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
                    t2v_hd = gr.Checkbox(label=HD_LABEL, info=HD_INFO, value=False)

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
                        i2v_first = gr.Image(label="起始首幀圖片 (First Frame, 可選)", type="filepath", height=300)
                        i2v_last = gr.Image(label="結尾尾幀圖片 (Last Frame, 可選)", type="filepath", height=300)
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
                        i2v_res = gr.Dropdown(label="畫面解析度", choices=[*AUTO_RESOLUTION_CHOICES, *BASE_RES_CHOICES, *FULL_HD_CHOICES], value=DEFAULT_RES)
                        i2v_duration = gr.Slider(label="影片長度 (秒)", minimum=4, maximum=15, value=4, step=1)
                    with gr.Row():
                        i2v_turbo = gr.Dropdown(label="🚀 採樣模式", choices=SAMPLING_MODES, value=MODE_TURBO_LORA)
                        i2v_seed = gr.Number(label="隨機種子 (-1 為隨機)", value=-1, precision=0)
                    i2v_hd = gr.Checkbox(label=HD_LABEL, info=HD_INFO, value=False)

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
                    ref_images = gr.File(label="參考圖（最多 9 張，依順序為 <Picture 1>…）", file_count="multiple", file_types=["image"], type="filepath")
                    ref_videos = gr.File(label="參考影片（選填，最多 3 支，會轉成 24 fps、最長 15 秒）", file_count="multiple", file_types=["video"], type="filepath")
                    ref_video_audio = gr.Checkbox(label="把參考影片的原音軌也當作參考（<Audio N>）", value=True)
                    ref_audios = gr.File(label="音檔（選填，最多 3 個）", file_count="multiple", file_types=["audio"], type="filepath")
                    ref_audio_mode = gr.Radio(
                        label="第一個音檔的用途", choices=[AUDIO_MODE_REFERENCE, AUDIO_MODE_COPY], value=AUDIO_MODE_REFERENCE,
                        info="整條照用：片長自動等於音檔長度（上限約 15 秒），音軌鎖進生成過程讓嘴型對上，成片再換回原始音檔。")
                    ref_label_md = gr.Markdown(label_table([]))
                    ref_labels = gr.State([])
                    ref_prompt = gr.Textbox(
                        label="提示詞 (Prompt)", lines=8,
                        placeholder="建議用下方「結構化提示詞」產生官方六段格式：subject_definitions / summary / retention_analysis / detailed_description / overall_soundscape / non_diegetic_music"
                    )
                    add_ref_prompt_builder(ref_prompt, ref_labels, ref_audio_mode)
                    add_prompt_picker(ref_prompt)
                    with gr.Row():
                        ref_res = gr.Dropdown(
                            label="畫面解析度",
                            info="自動：依第一支參考影片，沒有影片時依 <Picture 1> 的比例",
                            choices=[
                                *AUTO_RESOLUTION_CHOICES,
                                "864 × 480 (16:9 標清 · 4090 推薦極速不爆顯存)",
                                "960 × 544 (16:9 中清 · 4090 兼顧品質)",
                                "1056 × 608 (16:9 高清)",
                                "1280 × 704 (16:9 超清 · 需較多顯存)",
                                "480 × 864 (9:16 直式短影音 · 4090 推薦)",
                                "768 × 1344 (9:16 直式短影音 · 高清)"
                            ],
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
                control.change(preview_reference_labels, [ref_images, ref_videos, ref_video_audio, ref_audios], [ref_label_md, ref_labels], queue=False)
            ref_btn.click(
                fn=lambda p, r, d, tb, s, imgs, vids, va, auds, mode, sch, enc, fl2, r2v: execute_ref_generation(
                    p, r, d, tb, s, imgs, vids, va, auds, mode, scheduler=sch, text_encoder=enc, fl2va_model=fl2, ref2va_model=r2v),
                inputs=[ref_prompt, ref_res, ref_duration, ref_turbo, ref_seed, ref_images, ref_videos, ref_video_audio, ref_audios, ref_audio_mode, ref_scheduler, *model_inputs],
                outputs=[ref_output]
            )

        with gr.Tab("🎤 對嘴"):
            gr.Markdown(
                "### 一張人像 + 一段語音 → 對嘴影片\n"
                "最簡單的對嘴：上傳一張人像照當 `<Picture 1>`、一段語音當 `<Audio 1>`，按生成。"
                "用的是 Ref2VA（跟「參考」分頁同一個模型），音檔會**鎖進生成過程讓嘴型對上**，成片再換回原始音檔。\n\n"
                "- **不是傳統 Wav2Lip**：H3 會整段重新生成，臉孔、背景會盡量貼近原圖但非逐像素不變；提示詞已內建「保持場景、只動嘴」。\n"
                "- 片長**自動等於語音長度**（上限約 15 秒；更長請把語音切段，或用「長片」分頁）。\n"
                "- 正面、清晰、單人、嘴部沒被遮住的人像效果最好。語音建議乾淨人聲。"
            )
            with gr.Row():
                with gr.Column(scale=5):
                    lip_image = gr.Image(label="人像照片（<Picture 1>）", type="filepath", height=320)
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
                "### 一次生成數十秒到兩分鐘的連續影音\n"
                "自動切成約 10 秒一段，後一段直接接續前一段結尾的潛空間（重疊 39 幀後去重），聲音也跨段延續，最後合成一支影片。"
                "使用 Ref2VA Q4 模型與 Turbo 4 步。\n\n"
                "- **只填全域提示詞**：每段用同一個描述，依總長度自動分段，適合同一場景持續發展。\n"
                "- **填分段提示詞**：每段之間用單獨一行 `---` 分隔，段數以此為準（總長度滑桿不作用）。每段開頭要接得上前一段的結尾。"
                "下方「📚 分段提示詞範例」有建築／室內／人物的現成分段範例，選一個按「套用」就會填進「分段提示詞」框，可直接生成或改寫學習。\n"
                "- **角色參考圖**：每段都會帶入，提示詞用 `<Picture 1>` 指定，有助於保持同一角色。"
            )
            with gr.Row():
                with gr.Column(scale=5):
                    long_prompt = gr.Textbox(label="全域提示詞", lines=4, placeholder="例如：電影級寫實畫面，<Picture 1> 在黃昏的海邊沿著浪花慢慢散步……\n聲音：海浪、海鷗、輕柔配樂。")
                    add_prompt_picker(long_prompt)
                    long_segment_prompts = gr.Textbox(
                        label="分段提示詞（選填）", lines=8,
                        placeholder="第 1 段：……\n---\n第 2 段：接續上一段結尾，……\n---\n第 3 段：……"
                    )
                    add_long_example_picker(long_segment_prompts)
                    long_ref = gr.Image(label="角色參考圖（選填，提示詞用 <Picture 1>）", type="filepath", height=300)
                    with gr.Row():
                        long_total = gr.Slider(label="總長度（秒）", minimum=10, maximum=120, value=30, step=1)
                        long_segment = gr.Slider(label="每段秒數", minimum=5, maximum=15, value=10, step=1)
                    with gr.Row():
                        long_res = gr.Dropdown(
                            label="畫面解析度",
                            choices=["864 × 480 (16:9 標清 · 推薦)", "960 × 544 (16:9 中清)", "480 × 864 (9:16 直式)"],
                            value="864 × 480 (16:9 標清 · 推薦)"
                        )
                        long_seed = gr.Number(label="隨機種子 (-1 為隨機)", value=-1, precision=0)
                        long_scheduler = gr.Dropdown(label="採樣排程", choices=SCHEDULERS, value="simple", info=SCHEDULER_INFO)
                    long_mode = gr.Dropdown(label="採樣模式", choices=SAMPLING_MODES, value=MODE_TURBO_LORA)
                    long_plan = gr.Markdown(preview_long_plan(30, 10, ""))
                    long_btn = gr.Button("📼 生成長片", variant="primary", size="lg")
                with gr.Column(scale=5):
                    long_output = gr.Video(label="長片輸出", interactive=False, height=520)
            for control in (long_total, long_segment, long_segment_prompts):
                control.change(preview_long_plan, [long_total, long_segment, long_segment_prompts], long_plan, queue=False)
            long_btn.click(
                fn=lambda p, sp, tot, seg, r, s, img, sch, md, enc, fl2, r2v: execute_long_generation(p, sp, tot, seg, r, s, img, mode=md, scheduler=sch, text_encoder=enc, fl2va_model=fl2, ref2va_model=r2v),
                inputs=[long_prompt, long_segment_prompts, long_total, long_segment, long_res, long_seed, long_ref, long_scheduler, long_mode, *model_inputs],
                outputs=[long_output]
            )
            gr.Markdown("[長片節點來源：Songssx / ComfyUI-MiniMaxH3-TimelineDirector](https://github.com/Songssx/ComfyUI-MiniMaxH3-TimelineDirector)。每段額外 LoRA 需為 Ref2VA 版本。")

        with gr.Tab("🔍 放大"):
            gr.Markdown("### 用 SeedVR2 把現成影片放大\n"
                        "上傳任何影片，SeedVR2 逐批放大並保持時序一致，原音軌會保留。"
                        "**這是修復／放大工具，不是文生影片**。字節跳動開源，Apache-2.0。\n\n"
                        "- **短邊解析度**：輸出畫面的短邊像素；4K 很吃顯存與時間。\n"
                        "- **每批幀數**：一次處理幾幀，越多時序越穩、越省時間，但越吃顯存（最少 5）。\n"
                        "- **顯存不足**時把「區塊轉 CPU」調高（0–32），用速度換顯存。")
            with gr.Row():
                with gr.Column(scale=5):
                    seedvr_video = gr.Video(label="上傳要放大的影片", interactive=True, height=360)
                    with gr.Row():
                        seedvr_res = gr.Dropdown(label="短邊解析度", choices=list(SEEDVR2_RES_CHOICES), value="1080p（短邊 1080）")
                        seedvr_batch = gr.Slider(label="每批幀數", minimum=5, maximum=33, value=9, step=1)
                    with gr.Row():
                        seedvr_swap = gr.Slider(label="區塊轉 CPU（省顯存，越高越慢）", minimum=0, maximum=32, value=0, step=1)
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
                "### 用 Krea2 產生素材圖，再拿去餵 H3\n"
                "**這個分頁跟 H3 無關**：Krea2 是圖片模型，架構與 H3 完全不同，所以用自己的模型、文字編碼器與 VAE。"
                "RedCraft 作者把它定位為「為 H3 配套製作、產生日本漫畫風格漫劇素材圖」的模型。\n\n"
                "**雙權重**：高噪模型先開場（放大隨機性），低噪模型接手收尾。作者原話是「它不是嚴格聽話的模型，抽卡、重抽才是正確用法」。"
                "預設的兩段 sigmas 取自作者自己的工作流。"
            )
            with gr.Row():
                with gr.Column(scale=5):
                    krea_prompt = gr.Textbox(label="提示詞 (Prompt)", lines=5,
                                             placeholder="作者建議使用 Danbooru 風格標籤（IL / Pony / SD1.5 那一套寫法）")
                    add_prompt_picker(krea_prompt)
                    with gr.Row():
                        krea_size = gr.Dropdown(label="尺寸", choices=KREA2_SIZES, value=KREA2_SIZES[1])
                        krea_batch = gr.Slider(label="一次張數", minimum=1, maximum=4, value=1, step=1)
                        krea_seed = gr.Number(label="隨機種子 (-1 為隨機)", value=-1, precision=0)
                    krea_dual = gr.Checkbox(label="雙權重接力（高噪 → 低噪）", value=True,
                                            info="關閉時只用高噪模型，走一般 KSampler。")
                    with gr.Accordion("🎨 風格／原創角色 LoRA（放在 ComfyUI/models/loras/krea2/）", open=True):
                        gr.Markdown("觸發詞放在 LoRA 旁的 `同名.trigger.txt`，選到的 LoRA 會自動把觸發詞接到提示詞後面（沒有觸發詞的風格 LoRA 通常不會生效）。"
                                    "點縮圖會填入第一個空的欄位；同時最多疊三個，套用在高噪與低噪兩個模型上。"
                                    "縮圖優先用 LoRA 旁的預覽圖（`同名.preview.png` 等），沒有的話可按「產生缺少的縮圖」，"
                                    "會用固定的靜物場景快速畫一張，只用來看畫風。")
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
                        krea_high = gr.Dropdown(label="高噪模型", choices=krea_models, value=krea2_default(krea_models, KREA2_HIGH_MODEL))
                        krea_low = gr.Dropdown(label="低噪模型", choices=krea_models, value=krea2_default(krea_models, KREA2_LOW_MODEL))
                        krea_encoders = [value for _, value in text_encoder_choices()] + [f for f in list_model_files("text_encoders", "CLIPLoader", "clip_name") if f.endswith(".safetensors")]
                        krea_clip = gr.Dropdown(label="文字編碼器（Qwen3-VL 4B）", choices=sorted(set(krea_encoders)),
                                                value=krea2_default(sorted(set(krea_encoders)), KREA2_TEXT_ENCODER))
                        krea_vaes = list_model_files("vae", "VAELoader", "vae_name")
                        krea_vae = gr.Dropdown(label="VAE", choices=krea_vaes, value=krea2_default(krea_vaes, KREA2_VAE))
                        krea_loras = [NO_LORA] + [f for f in list_model_files("loras", "LoraLoaderModelOnly", "lora_name") if f.endswith(".safetensors")]
                        krea_lora = gr.Dropdown(label="Turbo LoRA", choices=krea_loras, value=krea2_default(krea_loras, KREA2_TURBO_LORA))
                        with gr.Row():
                            krea_high_strength = gr.Slider(label="高噪 LoRA 強度", minimum=0, maximum=1.5, value=0.85, step=0.05)
                            krea_low_strength = gr.Slider(label="低噪 LoRA 強度", minimum=0, maximum=1.5, value=0.5, step=0.05)
                        with gr.Row():
                            krea_sampler = gr.Dropdown(label="採樣器", choices=KREA2_SAMPLERS, value="er_sde")
                            krea_cfg = gr.Number(label="CFG", value=1.0)
                        krea_high_sigmas = gr.Textbox(label="高噪段 sigmas", value=KREA2_HIGH_SIGMAS)
                        krea_low_sigmas = gr.Textbox(label="低噪段 sigmas", value=KREA2_LOW_SIGMAS)
                        with gr.Row():
                            krea_steps = gr.Slider(label="單模型模式步數", minimum=4, maximum=30, value=12, step=1)
                            krea_scheduler = gr.Dropdown(label="單模型模式排程", choices=SCHEDULERS, value="simple")
                        krea_refresh = gr.Button("🔄 重新掃描模型")
                    krea_btn = gr.Button("🖼️ 生成圖片", variant="primary", size="lg")
                with gr.Column(scale=5):
                    krea_output = gr.Gallery(label="生成結果", columns=2, height=640, preview=True)

            def refresh_krea2_choices():
                models = krea2_model_choices()
                encoders = sorted({f for f in list_model_files("text_encoders", "CLIPLoader", "clip_name") if f.endswith(".safetensors")})
                vaes = list_model_files("vae", "VAELoader", "vae_name")
                loras = [NO_LORA] + [f for f in list_model_files("loras", "LoraLoaderModelOnly", "lora_name") if f.endswith(".safetensors")]
                return (gr.Dropdown(choices=models, value=krea2_default(models, KREA2_HIGH_MODEL)),
                        gr.Dropdown(choices=models, value=krea2_default(models, KREA2_LOW_MODEL)),
                        gr.Dropdown(choices=encoders, value=krea2_default(encoders, KREA2_TEXT_ENCODER)),
                        gr.Dropdown(choices=vaes, value=krea2_default(vaes, KREA2_VAE)),
                        gr.Dropdown(choices=loras, value=krea2_default(loras, KREA2_TURBO_LORA)))

            krea_refresh.click(refresh_krea2_choices, None, [krea_high, krea_low, krea_clip, krea_vae, krea_lora], queue=False)

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
            krea_thumb_btn.click(generate_krea2_thumbnails, [krea_high, krea_clip, krea_vae, krea_lora, krea_thumb_missing], krea_lora_gallery)
            for slot in krea_slot_loras:
                slot.change(trigger_summary, krea_slot_loras, krea_trigger_md, queue=False)
            krea_btn.click(
                execute_krea2_generation,
                inputs=[krea_prompt, krea_size, krea_batch, krea_seed, krea_high, krea_low, krea_dual, krea_lora,
                        krea_high_strength, krea_low_strength, krea_sampler, krea_high_sigmas, krea_low_sigmas,
                        krea_steps, krea_scheduler, krea_cfg, krea_clip, krea_vae,
                        krea_slot_loras[0], krea_slot_strengths[0], krea_slot_loras[1], krea_slot_strengths[1],
                        krea_slot_loras[2], krea_slot_strengths[2]],
                outputs=[krea_output]
            )
            gr.Markdown("模型來源：Civitai「RedCraft | 红潮 | Hybrid H3 & Krea2 DUAL MASO ver 双权重」赤佬 4.0 K2T DUAL；"
                        "配套的 Qwen3-VL 4B 編碼器、Qwen image VAE 與 Turbo LoRA 取自 `Comfy-Org/Krea-2`。"
                        "`download_krea2_models.py` 可續傳並核對 SHA-256。")

        with gr.Tab("🎥 攝影機"):
            gr.Markdown("### 參考圖片 → 3D 軌跡 → FL2VA Q4 影音\n上傳圖片後，拖曳紫色攝影機設定環繞角度與仰角，滾輪調整距離；在時間軸選取關鍵幀後修改位置。▶ 只預覽運鏡，按下生成按鈕才會生成影片。\n\n此模式固定原始場景，讓攝影機移動。軌跡會轉為 H3 提示詞，實際角度與時間可能有偏差。")
            with gr.Row():
                with gr.Column(scale=3):
                    camera_image = gr.Image(label="參考圖片（必要）", type="filepath", height=300)
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
                story_res = gr.Dropdown(label="渲染解析度", choices=["864 × 480 (16:9 標清 · 4090 推薦極速不爆顯存)", "960 × 544 (16:9 中清 · 4090 兼顧品質)"], value="864 × 480 (16:9 標清 · 4090 推薦極速不爆顯存)")
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
            gr.Markdown("每次成功生成都會存一張封面縮圖。點縮圖即可看到完整提示詞與該次成品，再選要套用到哪個分頁。")
            with gr.Row():
                history_refresh = gr.Button("🔄 重新整理", scale=0, min_width=120)
                history_count = gr.Markdown("")
            history_rows = gr.State([])
            history_gallery = gr.Gallery(label="生成紀錄（最新在前，點縮圖看細節）", columns=6, height=420,
                                         allow_preview=False, object_fit="cover")
            with gr.Row():
                with gr.Column(scale=5):
                    history_prompt = gr.Textbox(label="提示詞（可先修改再套用）", lines=10)
                    with gr.Row():
                        apply_t2v = gr.Button("套用到 🎬 文生")
                        apply_i2v = gr.Button("套用到 🖼️ 首尾幀")
                        apply_ref = gr.Button("套用到 🎞️ 參考")
                        apply_long = gr.Button("套用到 📼 長片")
                    history_seed_note = gr.Markdown("")
                with gr.Column(scale=5):
                    history_video = gr.Video(label="這次的成品", interactive=False, height=360)
                    history_details = gr.Markdown("")

            def load_history():
                # Only rows whose output still exists on disk, so every gallery cell has a real thumbnail.
                rows = history.rows_with_thumb(history.entries())
                return rows, history.gallery(rows), f"共 {len(rows)} 筆（最新在最上面）"

            def pick_history(rows, event: gr.SelectData):
                index = event.index[0] if isinstance(event.index, (list, tuple)) else event.index
                if not rows or index is None or index >= len(rows):
                    return "", None, "", ""
                row = rows[index]
                output = row.get("output") or ""
                video = output if output.lower().endswith((".mp4", ".webm", ".mkv")) and os.path.exists(output) else None
                seed = row.get("seed")
                note = f"要重現，種子填 **{seed}**，並照下方設定調整模型與模式。" if seed else ""
                return row.get("prompt", ""), video, history.details_text(row), note

            history_refresh.click(load_history, None, [history_rows, history_gallery, history_count], queue=False)
            history_gallery.select(pick_history, [history_rows],
                                   [history_prompt, history_video, history_details, history_seed_note], queue=False)
            for button, target in ((apply_t2v, t2v_prompt), (apply_i2v, i2v_prompt),
                                   (apply_ref, ref_prompt), (apply_long, long_prompt)):
                button.click(lambda text: text, history_prompt, target, queue=False)
            demo.load(load_history, None, [history_rows, history_gallery, history_count])

        with gr.Tab("ℹ️ 系統"):
            gr.Markdown("""
            ### 🖥️ 運算硬體與環境架構
            - **硬體**：NVIDIA GeForce RTX 4090 (24GB VRAM)
            - **運算引擎**：ComfyUI v0.34.0 (高顯存異步雙流調度 + FP8 矩陣加速)
            - **支援生成模式**：
              - 🎬 **Text to Video (文生影音)**
              - 🖼️ **Image to Video (圖生影音 / 首尾幀)**
              - 🎥 **Ref2VA 萬用參考（多圖／參考影片／音色參考／外部音軌對嘴）**
            - **核心模型庫**：
              - 擴散模型：本目錄內的 FL2VA／Ref2VA Pruned Q4_K_M GGUF
              - 文字編碼：本目錄內的 Qwen3-VL 32B NVFP4 AWQ；可在「模型設定」切換 Heretic 無審查版
              - 視訊／音效解碼：本目錄內的 MiniMax H3 VAE
              - 疾速加速：`minimax_h3_fl2v_turbo_8step_v1.0` & `minimax_h3_ref2v_turbo_4step_v0.1`

            ### 🔗 原生 ComfyUI 節點介面
            若您需要使用更複雜的節點連線控制，可以隨時前往原生 ComfyUI 頁面：
            - [開啟 ComfyUI 原生畫布 (http://127.0.0.1:8188)](http://127.0.0.1:8188)
            - 預設範本位於本目錄的 `workflows/` 資料夾中，包含 `MiniMax_H3_Reference_to_Video_R2V.json` 等，可隨時拖曳至畫布使用。
            """)

    def fl2va_model_changed(model, resolution_a, resolution_b, mode_a, mode_b, mode_c, mode_d):
        """Big trunks cannot run the HD refine (the upscaler runs out of VRAM), and baked-turbo
        checkpoints must not stack the Turbo LoRA: switch those options off instead of failing later."""
        model = model or ""
        too_big = model_file_size(model) > HD_MAX_MODEL_BYTES
        baked = "turbo" in model.lower()
        note = (f"「{model}」約 {model_file_size(model) / 1000 ** 3:.0f} GB，放大階段顯存不足，已停用高清二次採樣。"
                if too_big else HD_INFO)
        hd_update = gr.Checkbox(value=False, interactive=not too_big, info=note)
        choices = [*BASE_RES_CHOICES] if too_big else [*BASE_RES_CHOICES, *FULL_HD_CHOICES]
        def keep(current, extra=()):
            allowed = [*extra, *choices]
            return gr.Dropdown(choices=allowed, value=current if current in allowed else DEFAULT_RES)
        mode = MODE_BAKED_TURBO if baked else None
        def keep_mode(current):
            return gr.Dropdown(value=mode) if mode and current == MODE_TURBO_LORA else gr.Dropdown()
        return (hd_update, hd_update, keep(resolution_a), keep(resolution_b, tuple(AUTO_RESOLUTION_CHOICES)),
                keep_mode(mode_a), keep_mode(mode_b), keep_mode(mode_c), keep_mode(mode_d))

    def ref2va_model_changed(model, mode_a, mode_b):
        baked = "turbo" in (model or "").lower()
        def keep_mode(current):
            return gr.Dropdown(value=MODE_BAKED_TURBO) if baked and current == MODE_TURBO_LORA else gr.Dropdown()
        return keep_mode(mode_a), keep_mode(mode_b)

    model_fl2va.change(fl2va_model_changed,
                       [model_fl2va, t2v_res, i2v_res, t2v_turbo, i2v_turbo, camera_turbo, story_turbo],
                       [t2v_hd, i2v_hd, t2v_res, i2v_res, t2v_turbo, i2v_turbo, camera_turbo, story_turbo],
                       queue=False)
    model_ref2va.change(ref2va_model_changed, [model_ref2va, ref_turbo, long_mode], [ref_turbo, long_mode], queue=False)
    demo.load(fl2va_model_changed,
              [model_fl2va, t2v_res, i2v_res, t2v_turbo, i2v_turbo, camera_turbo, story_turbo],
              [t2v_hd, i2v_hd, t2v_res, i2v_res, t2v_turbo, i2v_turbo, camera_turbo, story_turbo])
    demo.load(ref2va_model_changed, [model_ref2va, ref_turbo, long_mode], [ref_turbo, long_mode])

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
            inbrowser=True
        )
    except OSError:
        # Another launch may have finished starting after the initial check.
        if not open_existing_webui():
            raise
