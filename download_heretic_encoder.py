"""Download the pinned Heretic (uncensored) H3 NVFP4 text encoder and verify its SHA-256."""
import concurrent.futures
import hashlib
import os
from pathlib import Path
import time

import requests

ROOT = Path(__file__).resolve().parent / "ComfyUI/models/text_encoders"
REPO = "sakamakismile/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4"
REVISION = "2814607c9e6034e2cf2c76da82f996d179567551"
NAME = "qwen3vl_32b_heretic_minimax_h3_nvfp4.safetensors"
SIZE = 15683129587
EXPECTED = "a166c7bbbe66a22065159e478335fee4a633c4a3e3bb34c8e8ac4cc91bf4996f"
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
    parts.mkdir(exist_ok=True)
    url = f"https://huggingface.co/{REPO}/resolve/{REVISION}/{NAME}"

    def fetch(start):
        end = min(start + CHUNK, SIZE) - 1
        part = parts / str(start)
        if part.exists() and part.stat().st_size == end - start + 1:
            return part.stat().st_size
        for attempt in range(4):
            try:
                with requests.get(url + f"?chunk={start}", headers={"Range": f"bytes={start}-{end}"}, stream=True, timeout=(20, 60)) as response:
                    response.raise_for_status()
                    if response.status_code != 206 or response.headers.get("Content-Range") != f"bytes {start}-{end}/{SIZE}":
                        raise RuntimeError("Unexpected download range")
                    with part.open("wb") as stream:
                        for block in response.iter_content(1024 * 1024):
                            stream.write(block)
                if part.stat().st_size != end - start + 1:
                    raise RuntimeError("Incomplete download range")
                return part.stat().st_size
            except (requests.RequestException, RuntimeError):
                if attempt == 3:
                    raise
                time.sleep(2)

    downloaded = 0
    last_report = 0
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
