"""Install the panel's custom nodes into ComfyUI/custom_nodes without git.

Downloads each repo as a pinned GitHub archive .zip and extracts it with Python's
zipfile (which handles non-ASCII filenames that the Windows shell's tar cannot).
Idempotent and resumable: a node whose folder already has __init__.py is skipped.
"""
import io
import os
import shutil
import zipfile
from pathlib import Path

import requests

CUSTOM_NODES = Path(__file__).resolve().parent / "ComfyUI" / "custom_nodes"

# (target folder name, repo, git ref) — pinned to the revisions the panel is built against.
NODES = [
    ("ComfyUI-MiniMaxH3-TimelineDirector", "Songssx/ComfyUI-MiniMaxH3-TimelineDirector",
     "53f7211e53385cfe80a9094bc31768f505e05a7c"),
    ("Comfyui_Minimax_h3_latent_Upscaler", "LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler",
     "d7c01b9011f2e8439493f6c02c29995a27df276f"),
    ("3d-Camera-control-H3-Minimax", "NyckM/3d-Camera-control-H3-Minimax",
     "846880de859959e801b2c506dc424bd5c8b5c6c4"),
    ("ComfyUI-MiniMax-H3-Edit", "ethanfel/ComfyUI-MiniMax-H3-Edit",
     "92ff5b926945e21d843fa618ba440ad2f96048e6"),
    ("ComfyUI-SeedVR2_VideoUpscaler", "numz/ComfyUI-SeedVR2_VideoUpscaler", "main"),
]


def install(target, repo, ref):
    dest = CUSTOM_NODES / target
    if (dest / "__init__.py").exists() or (dest / ".git").exists():
        print(f"  - {target} already present, skipping", flush=True)
        return
    url = f"https://github.com/{repo}/archive/{ref}.zip"
    print(f"  - downloading {target} ...", flush=True)
    response = requests.get(url, timeout=(20, 120))
    response.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        top = archive.namelist()[0].split("/")[0]  # "<repo>-<ref>/"
        staging = CUSTOM_NODES / (target + ".tmp")
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        archive.extractall(staging)
    extracted = staging / top
    if dest.exists():
        shutil.rmtree(dest, ignore_errors=True)
    shutil.move(str(extracted), str(dest))
    shutil.rmtree(staging, ignore_errors=True)
    print(f"    done: {target}", flush=True)


def main():
    CUSTOM_NODES.mkdir(parents=True, exist_ok=True)
    for target, repo, ref in NODES:
        try:
            install(target, repo, ref)
        except Exception as error:
            print(f"    [!] {target} failed: {error}. Re-run to try again.", flush=True)


if __name__ == "__main__":
    main()
