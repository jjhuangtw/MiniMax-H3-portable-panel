"""Download the SeedVR2 3B DiT weight and its EMA VAE for the video upscaler and verify their SHA-256."""
import concurrent.futures
import hashlib
import os
from pathlib import Path
import time

import requests

ROOT = Path(__file__).resolve().parent / "ComfyUI/models/SEEDVR2"
REPO = "numz/SeedVR2_comfyUI"
REVISION = "09ced71023636e9bc8cdf9cdecfb2625d1e691e8"
FILES = [
    ("seedvr2_ema_3b_fp16.safetensors", 6783018808, "2fd0e03a3dad24e07086750360727ca437de4ecd456f769856e960ae93e2b304"),
    ("ema_vae_fp16.safetensors", 501324814, "20678548f420d98d26f11442d3528f8b8c94e57ee046ef93dbb7633da8612ca1"),
]
CHUNK = 64 * 1024 * 1024


def digest(path):
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def download(NAME, SIZE, EXPECTED):
    target = ROOT / NAME
    if target.exists():
        if target.stat().st_size == SIZE and digest(target) == EXPECTED:
            print(NAME, "already verified", flush=True)
            return
        raise RuntimeError(f"Existing file failed verification: {target}")
    parts = ROOT / (NAME + ".parts")
    parts.mkdir(parents=True, exist_ok=True)
    url = f"https://huggingface.co/{REPO}/resolve/{REVISION}/{NAME}"

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
    for entry in FILES:
        download(*entry)
