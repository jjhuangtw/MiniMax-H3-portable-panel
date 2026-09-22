"""Download Qwen-Image-2.1 models for image editing into ComfyUI models directories.

Supports official ComfyUI model weights from Comfy-Org/Qwen-Image-2.1.
- Diffusion Model: qwen_image_2.1_int8_convrot.safetensors (7.25 GB, fits RTX 4090 24GB) or bf16
- Text Encoder: qwen3vl_8b_int8_convrot.safetensors (9.35 GB) or w4a8 (5.88 GB) or bf16
- VAE: qwen_image_2.1_vae_bf16.safetensors (675 MB)
"""
import argparse
import os
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
from pathlib import Path
from huggingface_hub import hf_hub_download

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "ComfyUI" / "models"
REPO_ID = "Comfy-Org/Qwen-Image-2.1"

FILES = {
    "vae": {
        "remote": "vae/qwen_image_2.1_vae_bf16.safetensors",
        "local": "vae/qwen_image_2.1_vae_bf16.safetensors",
        "size": 675509688,
        "desc": "Qwen-Image-2.1 BF16 VAE (~675 MB)",
    },
    "diffusion_int8": {
        "remote": "diffusion_models/qwen_image_2.1_int8_convrot.safetensors",
        "local": "diffusion_models/qwen_image_2.1_int8_convrot.safetensors",
        "size": 7256783064,
        "desc": "Qwen-Image-2.1 DiT Int8 ConvRot (~7.25 GB, RTX 4090 推薦)",
    },
    "diffusion_bf16": {
        "remote": "diffusion_models/qwen_image_2.1_bf16.safetensors",
        "local": "diffusion_models/qwen_image_2.1_bf16.safetensors",
        "size": 14230280616,
        "desc": "Qwen-Image-2.1 DiT BF16 (~14.23 GB)",
    },
    "encoder_int8": {
        "remote": "text_encoders/qwen3vl_8b_int8_convrot.safetensors",
        "local": "text_encoders/qwen3vl_8b_int8_convrot.safetensors",
        "size": 9350798360,
        "desc": "Qwen3-VL 8B Int8 ConvRot Text Encoder (~9.35 GB, RTX 4090 推薦)",
    },
    "encoder_w4a8": {
        "remote": "text_encoders/qwen3vl_8b_w4a8.safetensors",
        "local": "text_encoders/qwen3vl_8b_w4a8.safetensors",
        "size": 6312105364,
        "desc": "Qwen3-VL 8B W4A8 Text Encoder (~5.88 GB, 輕量低顯存)",
    },
    "encoder_bf16": {
        "remote": "text_encoders/qwen3vl_8b_bf16.safetensors",
        "local": "text_encoders/qwen3vl_8b_bf16.safetensors",
        "size": 17534334616,
        "desc": "Qwen3-VL 8B BF16 Text Encoder (~17.53 GB)",
    },
}

GGUF_FILES = {
    "q8_0": {
        "repo": "AlperKTS/Qwen-Image-2.1-GGUF",
        "remote": "qwen_image_2.1_Q8_0.gguf",
        "local": "diffusion_models/qwen_image_2.1_Q8_0.gguf",
        "desc": "Qwen-Image-2.1 Q8_0 GGUF (~7.10 GB, 接近無損高品質 · RTX 4090 首選)",
    },
    "q6_k": {
        "repo": "AlperKTS/Qwen-Image-2.1-GGUF",
        "remote": "qwen_image_2.1_Q6_K.gguf",
        "local": "diffusion_models/qwen_image_2.1_Q6_K.gguf",
        "desc": "Qwen-Image-2.1 Q6_K GGUF (~5.44 GB, 高畫質平衡)",
    },
    "q5_k_m": {
        "repo": "AlperKTS/Qwen-Image-2.1-GGUF",
        "remote": "qwen_image_2.1_Q5_K_M.gguf",
        "local": "diffusion_models/qwen_image_2.1_Q5_K_M.gguf",
        "desc": "Qwen-Image-2.1 Q5_K_M GGUF (~4.56 GB, 輕量低顯存極速)",
    },
    "q4_k_m": {
        "repo": "abenzerps/Qwen-Image-2.1-GGUF",
        "remote": "qwen-image-2.1-Q4_K_M.gguf",
        "local": "diffusion_models/qwen-image-2.1-Q4_K_M.gguf",
        "desc": "Qwen-Image-2.1 Q4_K_M GGUF (~4.29 GB, 8GB/12GB 顯卡首選)",
    },
}


def is_file_ready(rel_path, expected_size=None):
    p = MODELS_DIR / rel_path
    if not p.exists():
        return False
    if expected_size and p.stat().st_size != expected_size:
        return False
    return True


def download_item(item_key):
    info = FILES[item_key]
    dest = MODELS_DIR / info["local"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    if is_file_ready(info["local"], info["size"]):
        print(f"✅ {info['desc']} 已存在且完整，略過下載。")
        return dest

    print(f"\n🚀 開始下載: {info['desc']}")
    print(f"   來源: https://huggingface.co/{REPO_ID}/blob/main/{info['remote']}")
    print(f"   目標: {dest}")

    downloaded = hf_hub_download(
        repo_id=REPO_ID,
        filename=info["remote"],
        local_dir=str(MODELS_DIR),
    )
    actual_size = os.path.getsize(downloaded)
    print(f"🎉 下載完成! 大小: {actual_size / 1024**3:.2f} GB")
    return downloaded


def download_gguf(variant="q8_0"):
    variant = variant.lower().replace("-", "_")
    if variant not in GGUF_FILES:
        print(f"⚠️ 未知的 GGUF 版本: {variant}，可選: {list(GGUF_FILES.keys())}，預設使用 q8_0")
        variant = "q8_0"
    info = GGUF_FILES[variant]
    dest = MODELS_DIR / info["local"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1024 * 1024 * 1000:
        print(f"✅ {info['desc']} 已存在，大小: {dest.stat().st_size / 1024**3:.2f} GB，略過下載。")
        return dest

    print(f"\n🚀 開始下載 GGUF 擴散模型: {info['desc']}")
    print(f"   來源: https://huggingface.co/{info['repo']}/blob/main/{info['remote']}")
    print(f"   目標: {dest}")

    downloaded = hf_hub_download(
        repo_id=info["repo"],
        filename=info["remote"],
        local_dir=str(MODELS_DIR / "diffusion_models"),
    )
    actual_size = os.path.getsize(downloaded)
    print(f"🎉 GGUF 下載完成! 大小: {actual_size / 1024**3:.2f} GB")
    return downloaded


def check_qwen_image_ready():
    """Return True if at least one diffusion model, one encoder, and the VAE are present."""
    vae_ok = (MODELS_DIR / "vae" / "qwen_image_2.1_vae_bf16.safetensors").exists() or (MODELS_DIR / "vae" / "qwen_image_vae.safetensors").exists()
    diff_ok = any(
        (MODELS_DIR / "diffusion_models" / name).exists()
        for name in [
            "qwen_image_2.1_int8_convrot.safetensors",
            "qwen_image_2.1_bf16.safetensors",
            "qwen_image_2.1_Q8_0.gguf",
            "qwen_image_2.1_Q6_K.gguf",
            "qwen_image_2.1_Q5_K_M.gguf",
            "qwen-image-2.1-Q4_K_M.gguf",
        ]
    )
    enc_ok = any(
        (MODELS_DIR / "text_encoders" / name).exists()
        for name in ["qwen3vl_8b_int8_convrot.safetensors", "qwen3vl_8b_w4a8.safetensors", "qwen3vl_8b_bf16.safetensors"]
    )
    return vae_ok and diff_ok and enc_ok


def main():
    parser = argparse.ArgumentParser(description="Download Qwen-Image-2.1 models for ComfyUI.")
    parser.add_argument("--gguf", nargs="?", const="q8_0", default=None,
                        help="Download GGUF quantized model (choices: q8_0, q6_k, q5_k_m, q4_k_m; default: q8_0).")
    parser.add_argument("--bf16", action="store_true", help="Download unquantized BF16 weights instead of int8.")
    parser.add_argument("--w4a8", action="store_true", help="Download W4A8 text encoder (smaller, ~5.88 GB).")
    parser.add_argument("--vae-only", action="store_true", help="Download only the VAE.")
    parser.add_argument("--encoder-only", action="store_true", help="Download only the text encoder.")
    parser.add_argument("--diffusion-only", action="store_true", help="Download only the diffusion model.")
    args = parser.parse_args()

    # VAE
    if not (args.encoder_only or args.diffusion_only):
        download_item("vae")
        if args.vae_only:
            return

    # Text encoder
    if not args.diffusion_only:
        if args.bf16:
            enc_key = "encoder_bf16"
        elif args.w4a8:
            enc_key = "encoder_w4a8"
        else:
            enc_key = "encoder_int8"
        download_item(enc_key)
        if args.encoder_only:
            return

    # Diffusion model
    if not args.encoder_only:
        if args.gguf:
            download_gguf(args.gguf)
        elif args.bf16:
            download_item("diffusion_bf16")
        else:
            download_item("diffusion_int8")

    print("\n✨ Qwen-Image-2.1 模型配置已就緒！可在面板「🖌️ 修圖」分頁立即使用。")


if __name__ == "__main__":
    main()
