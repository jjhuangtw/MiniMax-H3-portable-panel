import os
import sys

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"

from huggingface_hub import hf_hub_download

REPO_ID = "Comfy-Org/MiniMax-H3"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "ComfyUI", "models")

FILES_TO_DOWNLOAD = [
    ("diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors", "diffusion_models", "minimax_h3_fl2va_pruned_int8_convrot.safetensors"),
    ("text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "text_encoders", "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"),
    ("vae/minimax_h3_video_vae_fp16.safetensors", "vae", "minimax_h3_video_vae_fp16.safetensors"),
    ("vae/minimax_h3_audio_vae_fp32.safetensors", "vae", "minimax_h3_audio_vae_fp32.safetensors"),
    ("loras/minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors", "loras", "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors"),
]

def main():
    print("=== Starting MiniMax H3 Model Download for RTX 4090 ===")
    print(f"Target Models Directory: {MODELS_DIR}")
    
    for repo_file, subfolder, target_name in FILES_TO_DOWNLOAD:
        target_folder = os.path.join(MODELS_DIR, subfolder)
        os.makedirs(target_folder, exist_ok=True)
        target_path = os.path.join(target_folder, target_name)
        
        print(f"\n[+] Processing: {repo_file}")
        print(f"    Target path: {target_path}")
        
        try:
            downloaded = hf_hub_download(
                repo_id=REPO_ID,
                filename=repo_file,
                local_dir=MODELS_DIR,
                local_dir_use_symlinks=False,
                resume_download=True
            )
            print(f"    [OK] Finished: {downloaded}")
        except Exception as e:
            print(f"    [ERROR] Failed to download {repo_file}: {e}", file=sys.stderr)
            sys.exit(1)

    print("\n=== All MiniMax H3 weights downloaded successfully! ===")

if __name__ == "__main__":
    main()
