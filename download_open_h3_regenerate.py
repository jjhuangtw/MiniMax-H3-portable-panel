"""Download NVIDIA's Open-H3-Regenerate-2K refiner (merged LoRA + Sharp curve branches) and verify SHA-256.

Source: Efficient-Large-Model/Open-H3-Regenerate-2K (MiniMax H3 Community License), pinned revision.
Used by the Songssx/ComfyUI-OpenH3-Regenerate2K nodes on the Ref2VA pruned INT8 trunk (Comfy-Org/MiniMax-H3,
fetched here too when missing); the VAEs and text encoder it also needs are the ones the panel already installs,
and the latent upscaler is extras option 5. Resumable.

The LoRA goes in loras/open_h3/ so the panel's H3 LoRA menus can leave it out: it only works together with
the curve branches and the exact refine sigmas, never as a plain LoRA.
"""
import hashlib
import os
from pathlib import Path
import time

import requests

MODELS = Path(__file__).resolve().parent / "ComfyUI/models"
REGEN = ("Efficient-Large-Model/Open-H3-Regenerate-2K", "5809c33730c18b6b1c827b40974855a4288641b3")
H3 = ("Comfy-Org/MiniMax-H3", "77aac5182eb85bb20930536bac73e498bbe2bfd7")
FILES = [
    (REGEN, "lora/open_h3_regenerate_2k_lora.safetensors", "loras/open_h3/open_h3_regenerate_2k_lora.safetensors",
     12452449080, "8e36a0912ab72f7f3b00f41e3c7c97c7dfdec21e66c88ab22f08b9b0c681bb04"),
    (REGEN, "lora/sharp_curve_branches.safetensors", "open_h3_regenerate/lora/sharp_curve_branches.safetensors",
     1238746768, "26ff1c4ea50fc5b0cea252912b67ec308a65d534cef026ef56f415ae92102e4e"),
    (H3, "diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors",
     "diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors",
     20970379616, "9255f52b6677845ad238f20dfaafa94727053694127ab7f255c048f0f9365779"),
]


def digest(path):
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(16 * 1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def download(source, remote, local, size, expected):
    target = MODELS / local
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_name(target.name + ".part")
    if target.exists():
        if target.stat().st_size == size and digest(target) == expected:
            print(target.name, "already verified", flush=True)
            return
        raise RuntimeError(f"Existing file failed verification: {target}")
    repo, revision = source
    url = f"https://huggingface.co/{repo}/resolve/{revision}/{remote}"
    for attempt in range(20):
        done = partial.stat().st_size if partial.exists() else 0
        if done >= size:
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
                            print(f"{target.name}: {done / size:.1%} ({done / 1e9:.2f} GB)", flush=True)
                            last = time.monotonic()
        except (requests.RequestException, RuntimeError) as error:
            print("retrying:", error, flush=True)
            time.sleep(5)
    print(f"verifying SHA-256 of {target.name} ...", flush=True)
    if partial.stat().st_size != size or digest(partial) != expected:
        raise RuntimeError(f"SHA-256 mismatch or incomplete: {partial}")
    os.replace(partial, target)
    print(target.name, "SHA-256 VERIFIED", flush=True)


if __name__ == "__main__":
    for item in FILES:
        download(*item)
