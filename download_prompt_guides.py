"""Fetch MiniMax's official h3-prompt-writing reference guides into prompt_references/
and verify their SHA-256. The panel loads them as the "📖 官方指南" prompt-library
categories; they are read-only reference text, not model weights.

These files are NOT redistributed by this repo (they are git-ignored); each user
downloads them from the official source, the same way the model scripts do.

Source: https://github.com/MiniMax-AI/MiniMax-H3/tree/main/.claude/skills/h3-prompt-writing/references
"""
import hashlib
import os
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent / "prompt_references"
REPO = "MiniMax-AI/MiniMax-H3"
REVISION = "1ce88e916de7c15b63cbaf347642503f9bc21d3d"
SUBDIR = ".claude/skills/h3-prompt-writing/references"
FILES = {
    "base-en.txt": (15773, "2cfebc096a6e08370f288d468d90b60f7f9bcb938f94bf090816e910e48e75fc"),
    "ref-en.txt": (23553, "1e574f356716ad55612247ffb7bbccbcdb484ad96599d63c7dca1af186b1fab7"),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def download():
    ROOT.mkdir(parents=True, exist_ok=True)
    for name, (size, expected) in FILES.items():
        target = ROOT / name
        if target.exists() and target.stat().st_size == size and digest(target.read_bytes()) == expected:
            print(name, "already verified", flush=True)
            continue
        url = f"https://raw.githubusercontent.com/{REPO}/{REVISION}/{SUBDIR}/{name}"
        response = requests.get(url, timeout=(20, 60))
        response.raise_for_status()
        data = response.content
        if len(data) != size or digest(data) != expected:
            raise RuntimeError(f"SHA-256/size mismatch: {name}")
        target.write_bytes(data)
        print(name, "SHA-256 VERIFIED", flush=True)


if __name__ == "__main__":
    download()
