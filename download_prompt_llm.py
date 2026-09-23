"""Download only the Qwen3-VL 4B model (~5.2 GB) that writes prompts for the ✨ AI 專業提示詞 buttons.

It is the same verified file the Krea2 image tab uses, so a Krea2 download already includes it.
"""
import download_krea2_official as krea2

if __name__ == "__main__":
    entry = next(entry for entry in krea2.FILES if entry[1].endswith("qwen3vl_4b_fp8_scaled.safetensors"))
    krea2.download(*entry)
