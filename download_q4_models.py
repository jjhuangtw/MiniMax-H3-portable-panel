"""Download the two pinned H3 Q4 models and verify publisher SHA-256 hashes."""
import concurrent.futures
import hashlib
import os
from pathlib import Path
import time

import requests

ROOT = Path(__file__).resolve().parent / "ComfyUI/models/diffusion_models"
REVISION = "d9c4c6312b4728a68a15a35626d84775a6523783"
SIZE = 11420663904
CHUNK = 64 * 1024 * 1024
MODELS = {
    "minimax_h3_fl2va_pruned-Q4_K_M.gguf": "dd948e08ad0ba3c71bd42f368e283dd82e790f5122a63b276e22a3e0283d0c10",
    "minimax_h3_ref2va_pruned-Q4_K_M.gguf": "9ca1aef9f4609a56c2c751484013e1b20fe352f892122e5ab0a428fb95a7956e",
}


def digest(path):
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def download(name, expected):
    target = ROOT / name
    if target.exists():
        if target.stat().st_size == SIZE and digest(target) == expected:
            print(name, "already verified", flush=True)
            return
        raise RuntimeError(f"Existing file failed verification: {target}")
    parts = ROOT / (name + ".parts")
    parts.mkdir(exist_ok=True)
    url = f"https://huggingface.co/leejet/MiniMax-H3-GGUF/resolve/{REVISION}/{name}"

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
                print(f"{name}: {downloaded / SIZE:.1%} ({downloaded / 1e9:.2f} GB)", flush=True)
                last_report = time.monotonic()
    temporary = ROOT / (name + ".part")
    with temporary.open("wb") as output:
        for start in range(0, SIZE, CHUNK):
            with (parts / str(start)).open("rb") as stream:
                for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
                    output.write(block)
    if digest(temporary) != expected:
        raise RuntimeError(f"SHA-256 mismatch: {name}")
    os.replace(temporary, target)
    for start in range(0, SIZE, CHUNK):
        (parts / str(start)).unlink()
    parts.rmdir()
    print(name, "SHA-256 VERIFIED", flush=True)


if __name__ == "__main__":
    for name, expected in MODELS.items():
        download(name, expected)
