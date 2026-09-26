# 🔞 NSFW community models (download them yourself)

[繁體中文](NSFW_MODELS.md) | **English** | [简体中文](NSFW_MODELS.zh-CN.md) | [日本語](NSFW_MODELS.ja.md)

> **18+ only.** These are third-party community fine-tunes of MiniMax H3, 14–21 GB each. The panel's installers
> **do not** download them, and this repo does not contain or distribute them. Download them yourself, read each
> author's license, and follow the rules at the bottom of this page.

## Which one?

| Model | File size | VRAM | Menus |
| --- | --- | --- | --- |
| **10Eros-Max** beta5 Turbo hybrid w4a8 | 14.0 GB | 24 GB+ (tested on RTX 4090) | FL2VA + Ref2VA |
| **DaSiWa MiniMax H3** Hybrid Turbo v2 INT8 | 21.0 GB | 24 GB+ (tested on RTX 4090) | FL2VA + Ref2VA |

Both are **hybrids** (one file shows in both the FL2VA and the Ref2VA menu) with **Turbo distillation built in** —
they run at 8 steps with no Turbo LoRA. Pick one; you don't need both.

12–16 GB cards: there are smaller builds, but **none has been tested with this panel** — DaSiWa's int4 file (below,
12.5 GB) and community GGUF builds of 10Eros-Max ([Abiray/10Eros-Max-GGUF](https://huggingface.co/Abiray/10Eros-Max-GGUF),
Q3_K_M 8.9 GB · Q4_K_M 11.6 GB). The GGUFs come from an **earlier test build (Test4)**; follow the sampling settings on
their model page.

## Where to put the file

Both files go in the **same folder**, next to the official H3 models:

```
<your install folder>\ComfyUI\models\diffusion_models\
```

- Installed with `setup.bat`: `<folder where setup.bat is>\ComfyUI_windows_portable\ComfyUI\models\diffusion_models\`
- Installed by hand: the folder next to `run_webui.bat` → `ComfyUI\models\diffusion_models\`

**Keep the downloaded filename.** The panel reads the name: `Turbo` in the filename switches the sampling mode to
**Built-in distill · 8 steps** automatically, and `10Eros` / `Dasiwa` gives it a clear label in the menu. If you rename
it, keep those words.

## 1. 10Eros-Max (TenStrip)

- Model page: https://huggingface.co/TenStrip/10Eros-Max (marked *Not-For-All-Audiences*; license: MiniMax H3 Community License)
- File: `10Eros_Max_h3_TURBO-hybrid_beta5_w4a8_14gb_optimized.safetensors` (13,997,668,774 bytes)
- Direct link:
  https://huggingface.co/TenStrip/10Eros-Max/resolve/8a198588c8870ab0d613b3492a3150d091c8c2dd/10Eros_Max_h3_TURBO-hybrid_beta5_w4a8_14gb_optimized.safetensors
- SHA-256: `a8067999c65594b462d581c02b8a0573dd42d9812a14c586150a947c13388f2e`
- Use **beta5**. The author notes that beta3 / beta4 are broken test uploads.

## 2. DaSiWa MiniMax H3 (Civitai)

- Model page: https://civitai.com/models/2877206/dasiwa-minimax-h3
- On the page choose the **DaSiWa Hybrid Turbo v2** version and download the file marked **int8** (about 20.5 GB).
  Civitai needs a free account with mature content enabled to show this page; set that up yourself.
- File: `DasiwaMinimaxH3_dasiwaHybridTurboV2_3203135.safetensors` (20,967,669,168 bytes)
- SHA-256: `37C17FD91971C17E02E60798A05EEC48D881E1BB970D6309F58CF134A2D03A6B`
- The same version also has an **int4** file (`…_3203313.safetensors`, about 12.5 GB) that may suit 16 GB cards; it
  has **not been tested with this panel**.
- The non-Turbo "Hybrid v2" also works, but needs **Not distilled · 20 steps** and is about 2–3× slower.

## Check the download

A broken download is the most common cause of a crash. Open a command prompt in the file's folder and compare the
result with the SHA-256 above (upper or lower case doesn't matter):

```bat
certutil -hashfile 10Eros_Max_h3_TURBO-hybrid_beta5_w4a8_14gb_optimized.safetensors SHA256
```

## Use it in the panel

1. Put the file in `diffusion_models\` (above).
2. Open **🧩 Model settings** at the top of the panel and press **🔄 Rescan**. If it still doesn't appear, run
   `restart_webui.bat`.
3. Pick it in the **FL2VA diffusion model** menu (Text to Video / Keyframes / 3D Camera / Storyboard) and/or the
   **Ref2VA diffusion model** menu (Reference / V2V / Lip-sync).
4. Sampling mode: **Built-in distill · 8 steps**. It switches automatically when you pick the model; never stack the
   Turbo LoRA on it.
5. **✨ HD two-pass** is refused with the 21 GB DaSiWa file — once it is loaded there is too little VRAM left for the
   upscaler. Generate at 864×480 or 960×544 and upscale in the 🔍 Upscale tab. The 14 GB 10Eros file can use HD
   two-pass on 24 GB cards.

Optional: the uncensored **Heretic** text encoder is option **6** in `download_extras.bat`. It only removes the
language model's refusals; what H3 can draw depends on the diffusion model above.

## LoRAs

Ref2VA LoRAs such as [SexGod1979/AfterMidnight-MiniMax-H3-NSFW](https://huggingface.co/SexGod1979/AfterMidnight-MiniMax-H3-NSFW)
(Apache-2.0, two 1.19 GB files: `…_sexytime_rank64-v1.2` for motion at strength 1.0, `…_softer_rank64_v1` for detail at
0.8–1.0):

1. Put them in a subfolder such as `ComfyUI\models\loras\NSFW\`.
2. In **🧩 Model settings** press **🔄 Rescan**, then pick the file in **🧷 Ref2VA LoRA** and set **LoRA strength**.
3. It applies to the Ref2VA tabs (Reference, V2V, Lip-sync, and Storyboard with reference pictures). AfterMidnight's
   author requires the **beta** scheduler or the audio breaks — the panel switches to beta automatically.

FL2VA LoRAs (Text to Video, Keyframes) are picked the same way in **🧷 FL2VA LoRA**. A LoRA whose name contains `ref2v`
only shows in the Ref2VA menu, and one with `fl2v` only in the FL2VA menu.

## Rules

- **Adults only, fictional or consenting.** Only fictional adult characters, or real adults who have agreed to be
  depicted.
- **Never** make sexual, nude or fabricated imagery of a real person without consent — no celebrities, no people you
  know, no photos taken from the internet. This is illegal in many countries.
- **Never** anything involving minors, or characters that look like minors.
- Keep it private unless the platform allows it and everyone depicted has agreed. Follow your local law and each
  model's license (MiniMax H3 Community License; Civitai's terms for DaSiWa).

## Thanks

- **TenStrip** — [10Eros-Max](https://huggingface.co/TenStrip/10Eros-Max) · GGUF builds by **Abiray** — [10Eros-Max-GGUF](https://huggingface.co/Abiray/10Eros-Max-GGUF)
- **DaSiWa** — [DaSiWa MiniMax H3 on Civitai](https://civitai.com/models/2877206/dasiwa-minimax-h3)
- **SexGod1979** — [AfterMidnight-MiniMax-H3-NSFW](https://huggingface.co/SexGod1979/AfterMidnight-MiniMax-H3-NSFW)
- **sakamakismile** — [Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4](https://huggingface.co/sakamakismile/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4)
- All built on **MiniMax H3** by MiniMax — [MiniMaxAI/MiniMax-H3](https://huggingface.co/MiniMaxAI/MiniMax-H3)
