"""Download the INT8 ConvRot video VAE (Comfy-Org) and verify its SHA-256.

Half the VRAM of the FP16 video VAE with near-identical quality; a drop-in replacement.
"""
import concurrent.futures
import hashlib
import os
from pathlib import Path
import time

import requests

ROOT = Path(__file__).resolve().parent / "ComfyUI/models/vae"
REPO = "Comfy-Org/MiniMax-H3"
REVISION = "7e75982b97cd5a41d2dcfa1904ee88d0686d6fd1"
NAME = "minimax_h3_video_vae_int8_convrot.safetensors"
SIZE = 2811065184
EXPECTED = "52a2c8c73583c86e4f41cdcce3a6ad0ea562987bc0bf3d60a0cef5f5c8e60c0e"
CHUNK = 64 * 1024 * 1024


def digest(path):
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def download():
    target = ROOT / NAME
    if target.exists():
        if target.stat().st_size == SIZE and digest(target) == EXPECTED:
            print(NAME, "already verified", flush=True)
            return
        raise RuntimeError(f"Existing file failed verification: {target}")
    parts = ROOT / (NAME + ".parts")
    parts.mkdir(parents=True, exist_ok=True)
    url = f"https://huggingface.co/{REPO}/resolve/{REVISION}/vae/{NAME}"

    def fetch(start):
        end = min(start + CHUNK, SIZE) - 1
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
        futures = [pool.submit(fetch, start) for start in range(0, SIZE, CHUNK)]
        for future in concurrent.futures.as_completed(futures):
            downloaded += future.result()
            if time.monotonic() - last_report > 15 or downloaded == SIZE:
                print(f"{NAME}: {downloaded / SIZE:.1%} ({downloaded / 1e9:.2f} GB)", flush=True)
                last_report = time.monotonic()
    temporary = ROOT / (NAME + ".part")
    with temporary.open("wb") as output:
        for start in range(0, SIZE, CHUNK):
            with (parts / str(start)).open("rb") as stream:
                for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
                    output.write(block)
    if digest(temporary) != EXPECTED:
        raise RuntimeError(f"SHA-256 mismatch: {NAME}")
    os.replace(temporary, target)
    for start in range(0, SIZE, CHUNK):
        (parts / str(start)).unlink()
    parts.rmdir()
    print(NAME, "SHA-256 VERIFIED", flush=True)


if __name__ == "__main__":
    download()
