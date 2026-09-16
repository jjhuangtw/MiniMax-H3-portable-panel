"""Download Comfy-Org's official Krea2 style LoRAs into models/loras/krea2 and verify their SHA-256."""
import hashlib
import os
from pathlib import Path
import time

import requests

ROOT = Path(__file__).resolve().parent / "ComfyUI/models/loras/krea2"
REPO = "Comfy-Org/Krea-2"
REVISION = "e5ea8b4dd7f38f348b138eb0fe29f92c0e367e96"
SIZE = 469291992
LORAS = {
    "krea2_darkbrush.safetensors": "f47c4316dd93af66e0518c93b582f459571d4925b519133770c73a52cd5db7c6",
    "krea2_dotmatrix.safetensors": "805aa30d863347222485b9d3ce81642dbc70a73cebc95ab57219d98b878fceec",
    "krea2_kidsdrawing.safetensors": "8c1d45d204aeb4e34a7d9e16a7d473917592ba0048b03f4e03e037e3578ca500",
    "krea2_neondrip.safetensors": "a779c14435949eabae9ce0bface4320cad6672ef3547e8489107e3498d65e871",
    "krea2_rainywindow.safetensors": "7063a6f15ec6112ad3c06d79097b2a30a3ea7d9072821cb36021010d55989fe5",
    "krea2_retroanime.safetensors": "ca42107783d9e517c5d62cb9a9db9ab2ba4887d90e9dad97a9d1a7fe6ff14c56",
    "krea2_softwatercolor.safetensors": "3805e8655f19fbcac116542685e3f78f3a642e8fbfb857b5352bb32a4b3d445a",
    "krea2_sunsetblur.safetensors": "194abdd531ca190d32799f26ab5bab634aa5ba3f07b7a60ffb282657db8bf3a0",
    "krea2_vintagetarot.safetensors": "8cca96c56658fb3ac5269f9ef2245bd07cbf1b7a189f517c8763470bb1385f9f",
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
    temporary = ROOT / (name + ".part")
    url = f"https://huggingface.co/{REPO}/resolve/{REVISION}/loras/{name}"
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
    if temporary.stat().st_size != SIZE or digest(temporary) != expected:
        raise RuntimeError(f"SHA-256 mismatch: {name}")
    os.replace(temporary, target)
    print(name, "SHA-256 VERIFIED", flush=True)


if __name__ == "__main__":
    ROOT.mkdir(parents=True, exist_ok=True)
    for name, expected in LORAS.items():
        download(name, expected)
