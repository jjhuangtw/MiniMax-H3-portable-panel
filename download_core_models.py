"""Download the shared MiniMax H3 base assets (text encoder, VAEs, Turbo LoRAs) and verify SHA-256.

Run download_q4_models.py for the two diffusion models; this covers everything else the panel needs
by default. Optional extras (Heretic encoder, HD upscaler, SeedVR2, Krea2 styles) have their own scripts.
"""
import concurrent.futures
import hashlib
import os
from pathlib import Path
import time

import requests

BASE = Path(__file__).resolve().parent / "ComfyUI/models"
REPO = "Comfy-Org/MiniMax-H3"
REVISION = "7e75982b97cd5a41d2dcfa1904ee88d0686d6fd1"
CHUNK = 64 * 1024 * 1024
# (remote path within repo, local folder, size, sha256)
FILES = [
    ("text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "text_encoders",
     15687142551, "35a88d51044231fe332301d7a62aa81e3f2cba62febeb446e2c1e3e0ef76f2c6"),
    ("vae/minimax_h3_video_vae_fp16.safetensors", "vae",
     5207808496, "7c1f131492e7eddacaac9069a61b81bdd39de5cc96561e677c5eab1cdce5e522"),
    ("vae/minimax_h3_audio_vae_fp32.safetensors", "vae",
     605254808, "8e505d95dd1561d47abd43d4238fd40d9bb1ae9e147ed0a4cba778d76ae4db48"),
    ("loras/minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors", "loras",
     1956193000, "2339acdf19bfe123f46b971ea35d367a84adb85de43627e1eceafa5a5b2b111e"),
    ("loras/minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors", "loras",
     1956193000, "5b9ab5ade15d0775676d01a907268a69a1468dc6033b3b0d3ded5502f3ebb84c"),
]


def digest(path):
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def download(remote, folder, size, expected):
    name = os.path.basename(remote)
    root = BASE / folder
    root.mkdir(parents=True, exist_ok=True)
    target = root / name
    if target.exists():
        if target.stat().st_size == size and digest(target) == expected:
            print(name, "already verified", flush=True)
            return
        raise RuntimeError(f"Existing file failed verification: {target}")
    url = f"https://huggingface.co/{REPO}/resolve/{REVISION}/{remote}"
    parts = root / (name + ".parts")
    parts.mkdir(exist_ok=True)

    def fetch(start):
        end = min(start + CHUNK, size) - 1
        part = parts / str(start)
        if part.exists() and part.stat().st_size == end - start + 1:
            return part.stat().st_size
        for attempt in range(5):
            try:
                with requests.get(url, headers={"Range": f"bytes={start}-{end}"}, stream=True, timeout=(20, 60)) as response:
                    response.raise_for_status()
                    if response.status_code != 206:
                        raise RuntimeError("Server ignored the range request")
                    with part.open("wb") as stream:
                        for block in response.iter_content(8 * 1024 * 1024):
                            stream.write(block)
                if part.stat().st_size != end - start + 1:
                    raise RuntimeError("Incomplete range")
                return part.stat().st_size
            except (requests.RequestException, RuntimeError) as error:
                if attempt == 4:
                    raise
                print("retrying:", error, flush=True)
                time.sleep(3)

    downloaded, last_report = 0, 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(fetch, start) for start in range(0, size, CHUNK)]
        for future in concurrent.futures.as_completed(futures):
            downloaded += future.result()
            if time.monotonic() - last_report > 15 or downloaded == size:
                print(f"{name}: {downloaded / size:.1%} ({downloaded / 1e9:.2f} GB)", flush=True)
                last_report = time.monotonic()
    temporary = root / (name + ".part")
    with temporary.open("wb") as output:
        for start in range(0, size, CHUNK):
            with (parts / str(start)).open("rb") as stream:
                for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
                    output.write(block)
    if digest(temporary) != expected:
        raise RuntimeError(f"SHA-256 mismatch: {name}")
    os.replace(temporary, target)
    for start in range(0, size, CHUNK):
        (parts / str(start)).unlink()
    parts.rmdir()
    print(name, "SHA-256 VERIFIED", flush=True)


if __name__ == "__main__":
    for entry in FILES:
        download(*entry)
