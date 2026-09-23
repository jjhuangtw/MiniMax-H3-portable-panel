"""Download the official Krea2 Turbo image stack from Comfy-Org/Krea-2 and verify every SHA-256:
the diffusion model plus the Qwen3-VL 4B text encoder, Qwen image VAE and Turbo LoRA it needs."""
import concurrent.futures
import hashlib
import os
from pathlib import Path
import time
import requests

BASE = Path(__file__).resolve().parent / "ComfyUI/models"
CHUNK = 64 * 1024 * 1024

REPO = "Comfy-Org/Krea-2"
# (revision, remote path, local folder, size, sha256). The diffusion model's hash is the one on main;
# the three companions are pinned to the revision whose hashes were verified.
PINNED = "e5ea8b4dd7f38f348b138eb0fe29f92c0e367e96"
FILES = [
    ("main", "diffusion_models/krea2_turbo_fp8_scaled.safetensors", "diffusion_models",
     13141730784, "eb4dd8c612cfd10f64f25b057e6e6bbcb5737c94a7372177e456dbf7579502f1"),
    (PINNED, "text_encoders/qwen3vl_4b_fp8_scaled.safetensors", "text_encoders",
     5242467968, "54bd5144df0bbc25dd6ccadfcb826b521445a1b06ae5a42570bdd2974ca87094"),
    (PINNED, "vae/qwen_image_vae.safetensors", "vae",
     253806246, "a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f"),
    (PINNED, "loras/krea2_turbo_lora_rank_64_bf16.safetensors", "loras",
     469423778, "db8c5bae0a415d448da9d842111d6e51f7d32e47143a3118eb267e5c4773de87"),
]


def digest(path):
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def download(revision, REMOTE_PATH, LOCAL_FOLDER, SIZE, EXPECTED_SHA256):
    LOCAL_NAME = REMOTE_PATH.rsplit("/", 1)[1]
    root = BASE / LOCAL_FOLDER
    root.mkdir(parents=True, exist_ok=True)
    target = root / LOCAL_NAME
    if target.exists():
        if target.stat().st_size == SIZE:
            print("Verifying existing file SHA-256...", flush=True)
            if digest(target) == EXPECTED_SHA256:
                print(f"{LOCAL_NAME} already exists and is fully verified!", flush=True)
                return
        print(f"Existing file incomplete or invalid ({target.stat().st_size} vs {SIZE}), re-downloading...", flush=True)

    url = f"https://huggingface.co/{REPO}/resolve/{revision}/{requests.utils.quote(REMOTE_PATH)}"
    parts = root / (LOCAL_NAME + ".parts")
    parts.mkdir(exist_ok=True)

    def fetch(start):
        end = min(start + CHUNK, SIZE) - 1
        part = parts / str(start)
        expected_len = end - start + 1
        if part.exists() and part.stat().st_size == expected_len:
            return part.stat().st_size
        for attempt in range(8):
            try:
                headers = {"Range": f"bytes={start}-{end}", "User-Agent": "Mozilla/5.0"}
                with requests.get(url, headers=headers, stream=True, timeout=(20, 90)) as response:
                    response.raise_for_status()
                    if response.status_code != 206:
                        raise RuntimeError("Server did not return HTTP 206 Partial Content")
                    with part.open("wb") as stream:
                        for block in response.iter_content(8 * 1024 * 1024):
                            stream.write(block)
                if part.stat().st_size != expected_len:
                    raise RuntimeError("Incomplete range written")
                return part.stat().st_size
            except Exception as error:
                if attempt == 7:
                    raise
                time.sleep(2 + attempt)

    ranges = list(range(0, SIZE, CHUNK))
    total_parts = len(ranges)
    done_count = sum(1 for s in ranges if (parts / str(s)).exists() and (parts / str(s)).stat().st_size == (min(s + CHUNK, SIZE) - s))
    downloaded = sum((parts / str(s)).stat().st_size for s in ranges if (parts / str(s)).exists())
    print(f"Resuming download: {done_count}/{total_parts} chunks already downloaded ({downloaded / 1e9:.2f} GB / {SIZE / 1e9:.2f} GB)...", flush=True)

    last_report = time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(fetch, s): s for s in ranges}
        for future in concurrent.futures.as_completed(futures):
            part_len = future.result()
            now = time.monotonic()
            if now - last_report > 5 or done_count >= total_parts:
                cur_downloaded = sum((parts / str(s)).stat().st_size for s in ranges if (parts / str(s)).exists())
                pct = cur_downloaded / SIZE * 100
                print(f"Progress: {pct:.1f}% ({cur_downloaded / 1e9:.2f} / {SIZE / 1e9:.2f} GB)", flush=True)
                last_report = now

    print("All chunks downloaded! Merging into target file...", flush=True)
    temporary = root / (LOCAL_NAME + ".part")
    with temporary.open("wb") as output:
        for start in ranges:
            with (parts / str(start)).open("rb") as stream:
                for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
                    output.write(block)

    print("Verifying merged file SHA-256...", flush=True)
    if digest(temporary) != EXPECTED_SHA256:
        raise RuntimeError(f"SHA-256 mismatch for {LOCAL_NAME}")
    os.replace(temporary, target)

    print("Cleaning up chunk files...", flush=True)
    for start in ranges:
        try:
            (parts / str(start)).unlink()
        except OSError:
            pass
    try:
        parts.rmdir()
    except OSError:
        pass
    print(f"Successfully installed official model: {LOCAL_NAME} (100% SHA-256 verified)!", flush=True)


if __name__ == "__main__":
    for entry in FILES:
        download(*entry)
