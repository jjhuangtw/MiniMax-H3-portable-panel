"""Download the Qwen-Image-2.1 Fun ControlNet Union (int8) for the ↔️ outpaint tab and verify its SHA-256.

One checkpoint covers 8 structural controls plus inpainting; the panel uses the inpainting branch to
extend a picture past its borders. Source: alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union, repackaged
for ComfyUI by Comfy-Org (needs ComfyUI v0.38.0 or later). Resumable, pinned revision.
"""
import hashlib
import os
from pathlib import Path
import time

import requests

ROOT = Path(__file__).resolve().parent / "ComfyUI/models/model_patches"
REPO = "Comfy-Org/Qwen-Image-2.1"
REVISION = "cb504a4090723e43f17ad01cec0359490e2de613"
REMOTE = "model_patches/qwen_image_2.1_fun_controlnet_union_int8_convrot.safetensors"
NAME = "qwen_image_2.1_fun_controlnet_union_int8_convrot.safetensors"
SIZE = 3779298944
EXPECTED = "07aa961570ac0e03d4ca936aecd76854d077a33cde69b5092399afba01b3715d"


def digest(path):
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(16 * 1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def download():
    ROOT.mkdir(parents=True, exist_ok=True)
    target, partial = ROOT / NAME, ROOT / (NAME + ".part")
    if target.exists():
        if target.stat().st_size == SIZE and digest(target) == EXPECTED:
            print(NAME, "already verified", flush=True)
            return
        raise RuntimeError(f"Existing file failed verification: {target}")
    url = f"https://huggingface.co/{REPO}/resolve/{REVISION}/{REMOTE}"
    for attempt in range(20):
        done = partial.stat().st_size if partial.exists() else 0
        if done >= SIZE:
            break
        try:
            with requests.get(url, headers={"Range": f"bytes={done}-"}, stream=True, timeout=(20, 120)) as response:
                response.raise_for_status()
                if response.status_code != 206:
                    raise RuntimeError("Server ignored the range request")
                last = time.monotonic()
                with partial.open("ab") as stream:
                    for block in response.iter_content(8 * 1024 * 1024):
                        stream.write(block)
                        done += len(block)
                        if time.monotonic() - last > 20:
                            print(f"{NAME}: {done / SIZE:.1%} ({done / 1e9:.2f} GB)", flush=True)
                            last = time.monotonic()
        except (requests.RequestException, RuntimeError) as error:
            print("retrying:", error, flush=True)
            time.sleep(5)
    print("verifying SHA-256 ...", flush=True)
    if partial.stat().st_size != SIZE or digest(partial) != EXPECTED:
        raise RuntimeError(f"SHA-256 mismatch or incomplete: {partial}")
    os.replace(partial, target)
    print(NAME, "SHA-256 VERIFIED", flush=True)


if __name__ == "__main__":
    download()
