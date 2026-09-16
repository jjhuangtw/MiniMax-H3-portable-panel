"""Download the pinned H3 latent upscaler used by HD two-pass generation and verify its SHA-256."""
import hashlib
import os
from pathlib import Path
import time

import requests

ROOT = Path(__file__).resolve().parent / "ComfyUI/models/latent_upscale_models"
REPO = "LBH-123-AI/Minimax_h3_latent_Upscaler"
REVISION = "13ccf95d85d120bdbc92c05b1247a6e147bf54bf"
NAME = "minimax_h3_latent_upscaler_3d_fp16.safetensors"
SIZE = 690592672
EXPECTED = "043e5a48e161610ef6c3ea974645220354d06fa618abca15f76d084812eb55c2"


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
    temporary = ROOT / (NAME + ".part")
    url = f"https://huggingface.co/{REPO}/resolve/{REVISION}/{NAME}"
    for attempt in range(6):
        start = temporary.stat().st_size if temporary.exists() else 0
        if start >= SIZE:
            break
        try:
            with requests.get(url, headers={"Range": f"bytes={start}-"}, stream=True, timeout=(20, 60)) as response:
                response.raise_for_status()
                if response.status_code != 206:
                    raise RuntimeError("Server ignored the resume range")
                with temporary.open("ab") as stream:
                    for block in response.iter_content(8 * 1024 * 1024):
                        stream.write(block)
        except (requests.RequestException, RuntimeError) as error:
            if attempt == 5:
                raise
            print("retrying:", error, flush=True)
            time.sleep(3)
    if temporary.stat().st_size != SIZE or digest(temporary) != EXPECTED:
        raise RuntimeError(f"SHA-256 mismatch: {NAME}")
    os.replace(temporary, target)
    print(NAME, "SHA-256 VERIFIED", flush=True)


if __name__ == "__main__":
    download()
