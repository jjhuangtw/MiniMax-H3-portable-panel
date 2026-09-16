import os
import sys
import time

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"

from huggingface_hub import hf_hub_download

REPO_ID = "Comfy-Org/MiniMax-H3"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "ComfyUI", "models")

FILES_TO_DOWNLOAD = [
    ("diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors", "diffusion_models", "minimax_h3_ref2va_pruned_int8_convrot.safetensors"),
    ("loras/minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors", "loras", "minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors"),
]

def main():
    print("=== Starting MiniMax H3 V2V (Reference-to-Video) Download for RTX 4090 ===")
    print(f"Target Models Directory: {MODELS_DIR}")
    
    for repo_file, subfolder, target_name in FILES_TO_DOWNLOAD:
        target_folder = os.path.join(MODELS_DIR, subfolder)
        os.makedirs(target_folder, exist_ok=True)
        target_path = os.path.join(target_folder, target_name)
        
        if os.path.exists(target_path) and os.path.getsize(target_path) > 1024*1024*100:
            print(f"\n[OK] Already downloaded: {target_path} ({os.path.getsize(target_path)/(1024**3):.2f} GB)")
            continue

        print(f"\n[+] Downloading: {repo_file}")
        print(f"    Target path: {target_path}")
        
        success = False
        for attempt in range(1, 20):
            try:
                downloaded = hf_hub_download(
                    repo_id=REPO_ID,
                    filename=repo_file,
                    local_dir=MODELS_DIR,
                    local_dir_use_symlinks=False,
                    resume_download=True
                )
                print(f"    [OK] Finished: {downloaded}")
                success = True
                break
            except Exception as e:
                print(f"    [Attempt {attempt}/20 failed: {e}. Retrying in 5 seconds...]")
                time.sleep(5)

        if not success:
            print(f"    [ERROR] Failed to download {repo_file} after multiple attempts.", file=sys.stderr)
            sys.exit(1)

    print("\n=== MiniMax H3 V2V Reference Model Downloaded Successfully! ===")

if __name__ == "__main__":
    main()
