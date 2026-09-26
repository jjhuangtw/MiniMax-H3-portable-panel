# MiniMax H3 Portable Panel

[繁體中文](README.md) | **English** | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

A local Gradio panel for generating videos with sound using the open [MiniMax H3](https://huggingface.co/MiniMaxAI/MiniMax-H3)
model on one NVIDIA card with **12–32 GB VRAM**. ComfyUI backend, fully local inference, no cloud API.
The panel detects your VRAM at start-up and adjusts itself — no settings to learn.

**Interface language**: follows your browser (any Chinese browser shows Traditional Chinese, everything else English).
The 🌐 button at the top switches and remembers your choice.

**Tabs**: Text to Video · Keyframes (FL2VA) · Reference (Ref2VA) · V2V · Lip-sync · SeedVR2 video upscale ·
Krea2 image generation · Qwen-Image editing · 🖍️ Brush Edit (scribble a few strokes and the AI redraws them as real
objects) · 3D camera · Storyboard · History · 🌐 Prompt site (embedded [ArchiPrompt](https://archi-prompt.com/),
AI prompts for architecture, landscape and interiors).

**📚 Prompt library**: every generation tab has a browsable library of ready-to-use prompts with **Krea2-rendered
thumbnails** — architecture, people, food, animals, nature, product, transport, sports, sci-fi, plus MiniMax's
official prompt-writing guides. The architecture / people / animation templates follow H3's **official three-field
format** (`integrated_multimodal_description` / `overall_soundscape` / `non_diegetic_music`). The Storyboard tab adds
15 ready-made stories (architecture, interiors, landscape, real-estate sales, people).

**✨ AI prompt writer**: type one line (any language), optionally add a picture, and a local Qwen3-VL model writes it
in H3's official format — three fields, camera moves, and `(S1)` + `<d>[Chinese] …</d>` dialogue. Available in the
Text to Video, Keyframes, Storyboard and Image tabs. Free and offline, a few seconds.

**🧷 LoRAs**: 🧩 Model settings has FL2VA and Ref2VA LoRA menus with strength sliders, applied to every video tab.

> This repo contains **only the panel code and download scripts**. Model weights are not included; the install
> scripts fetch them from the official sources and verify every SHA-256.

![panel](docs/panel.png)

| Text to Video (HD two-pass) | SeedVR2 upscale (before → after) |
| --- | --- |
| ![text to video](docs/example_text_to_video.png) | ![seedvr2 upscale](docs/example_seedvr2_upscale.png) |

Krea2 image style LoRAs:

![krea2 styles](docs/example_krea2_styles.png)

---

## Requirements

- **NVIDIA GPU with 12–32 GB VRAM.** The panel reads the card at start-up and switches off what it cannot run:

  | VRAM | Works well | Turned off automatically |
  | --- | --- | --- |
  | 24–32 GB (4090 / 5090 / 3090) | everything, including HD two-pass and Full HD | — |
  | 16 GB (4080 / 5080 / 4070 Ti S) | Q4 models, 864×480–960×544, 4–10 s | HD two-pass, Full HD |
  | 12 GB (4070 / 3060 12G) | Q4 models, 864×480, 4–6 s | same; SeedVR2 offloads more to the CPU |

  On smaller cards, generate at 864×480, then upscale in the 🔍 Upscale tab (SeedVR2).
- **System RAM 32 GB+** (64 GB recommended for 12–16 GB cards).
- **Windows 10 (1803+) or 11**, and **~200 GB free disk** (core set ~38 GB, plus any optional models).
  No git or Python setup needed — ComfyUI portable brings its own Python, and `install.bat` uses Windows' built-in
  `curl` / `tar`.

## Install — one click

**Easiest:** download **[`setup.bat`](../../raw/main/setup.bat)** (right-click ▸ Save link as…), put it in an
**empty folder** on a drive with ~200 GB free, and **double-click it**. It downloads ComfyUI portable (pinned v0.36.0),
the panel and the core H3 models, then launches the panel — no git, no 7-Zip needed. It's resumable: if a download
drops, run it again. Windows SmartScreen may warn about an unrecognized app — click **More info ▸ Run anyway** (it's
an unsigned `.bat` that only downloads the files below).

Prefer to do it by hand, or already have ComfyUI portable? Use the three manual steps below.

## Install — three manual steps

**1. Get ComfyUI portable.** Download `ComfyUI_windows_portable_nvidia.7z` from the
   [ComfyUI releases](https://github.com/comfyanonymous/ComfyUI/releases) (use the **latest**; the panel is tested on
   v0.36.0) and extract it with [7-Zip](https://www.7-zip.org/). You get a folder containing `python_embeded\` and
   `ComfyUI\`.

**2. Add the panel.** On this GitHub page click **Code ▸ Download ZIP**, extract it, and copy everything inside into
   the ComfyUI portable folder from step 1, so `install.bat` sits **next to** `python_embeded\`.

**3. Double-click `install.bat`.** It sets up the packages, downloads the custom nodes (no git) and the core H3 models
   with SHA-256 checks, then offers to launch. After that just double-click **`run_webui.bat`** and open
   http://127.0.0.1:7860 . `install.bat` is resumable — if a download drops, run it again.

**Optional models**: double-click **`download_extras.bat`** and type a number:
1 Krea2 image model for the 🎨 Image tab (~19 GB) · 2 Krea2 style LoRAs · 3 Qwen-Image-2.1 for the 🖌️ Image Edit tab
(~17 GB) · 4 SeedVR2 for the 🔍 Upscale tab (~7 GB) · 5 HD two-pass upscaler (24 GB cards) · 6 Heretic text encoder ·
7 the ✨ AI prompt writer (~5 GB; already included in 1 or 3).
A tab whose model is missing tells you which number to pick.

**🔞 NSFW community models (18+, download them yourself)**: the installers never fetch them. Where to download
10Eros-Max and DaSiWa, which folder to put them in, and how to pick them in the panel: **[NSFW_MODELS.md](NSFW_MODELS.md)**.

Detailed per-tab notes (Traditional Chinese): [RTX4090_LOCAL.md](RTX4090_LOCAL.md).

## Helper scripts

| File | What it does |
| --- | --- |
| `run_webui.bat` | Start or open the panel |
| `restart_webui.bat` | Restart the panel and backend (refuses while a job runs) |
| `cancel_generation.bat` | Cancel the current and queued jobs |
| `free_vram.bat` | Unload models and free VRAM |
| `download_extras.bat` | Optional models menu |

If VRAM detection misreads your card, run `set H3_VRAM_GB=16` in a command prompt before `run_webui.bat` to force a
smaller profile.

## License & responsible use

- Panel code: MIT, see `LICENSE`.
- **Models carry their own licenses** — read them before installing. MiniMax H3 uses the MiniMax H3 Community License
  (its scope excludes the EU, UK, Korea and the US); the custom nodes are mostly GPL-3.0 or Apache-2.0. This repo does
  not contain or distribute any model weights.
- This is a local, open-source tool with no content filter. Use it lawfully. **Do not make sexual, nude or fabricated
  imagery of real people's likenesses.** Adult content only with fictional characters, or with the consent of the
  person depicted. Creating or sharing non-consensual synthetic imagery of others is illegal in many places.
- Custom nodes and models are third-party; their correctness, safety and maintenance are their authors'.

## Credits

This panel only glues together other people's work. Thank you to every model and code author below — please visit
their pages, star their repos and follow their licenses.

### Models

| Model | Used for | Author · Source |
| --- | --- | --- |
| MiniMax H3 (FL2VA / Ref2VA, VAEs, Turbo LoRAs) | all video tabs | MiniMax — [MiniMaxAI/MiniMax-H3](https://huggingface.co/MiniMaxAI/MiniMax-H3) · ComfyUI packaging by Comfy-Org [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3) |
| MiniMax H3 Q4_K_M GGUF | default diffusion models | leejet — [leejet/MiniMax-H3-GGUF](https://huggingface.co/leejet/MiniMax-H3-GGUF) |
| Qwen3-VL-32B NVFP4 text encoder / INT8 video VAE | text encoding, lower-VRAM decode | Qwen team (Alibaba) · Comfy-Org — [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3) |
| Qwen3-VL-32B Heretic (uncensored) encoder | optional | sakamakismile — [Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4](https://huggingface.co/sakamakismile/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4) |
| H3 latent upscaler 3D | HD two-pass | LBH-123-AI — [Minimax_h3_latent_Upscaler](https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler) |
| SeedVR2 3B + EMA VAE | 🔍 video upscale | ByteDance Seed — [ByteDance-Seed/SeedVR](https://github.com/ByteDance-Seed/SeedVR) · ComfyUI weights by numz [numz/SeedVR2_comfyUI](https://huggingface.co/numz/SeedVR2_comfyUI) |
| Krea 2 Turbo + style LoRAs | 🎨 Image tab, template thumbnails | Krea — ComfyUI packaging by Comfy-Org [Comfy-Org/Krea-2](https://huggingface.co/Comfy-Org/Krea-2) |
| Qwen-Image-2.1 + Qwen3-VL 8B | 🖌️ image editing | Qwen team — [Qwen/Qwen-Image-2.1](https://huggingface.co/Qwen/Qwen-Image-2.1) · [Comfy-Org/Qwen-Image-2.1](https://huggingface.co/Comfy-Org/Qwen-Image-2.1) · optional GGUF by [AlperKTS](https://huggingface.co/AlperKTS/Qwen-Image-2.1-GGUF) and [abenzerps](https://huggingface.co/abenzerps/Qwen-Image-2.1-GGUF) |
| Qwen3-VL 4B / 8B | ✨ AI prompt writer | Qwen team — via [Comfy-Org/Krea-2](https://huggingface.co/Comfy-Org/Krea-2) and [Comfy-Org/Qwen-Image-2.1](https://huggingface.co/Comfy-Org/Qwen-Image-2.1) |

### Code & tools

| Project | Used for | Author · Source |
| --- | --- | --- |
| ComfyUI (incl. native MiniMax H3, Qwen-Image and TextGenerate nodes) | backend | comfyanonymous & Comfy-Org — [comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI) |
| ComfyUI-GGUF-Loader | loads the Q4 GGUF models | ChrisColeTech — [ChrisColeTech/ComfyUI-GGUF-Loader](https://github.com/ChrisColeTech/ComfyUI-GGUF-Loader) |
| ComfyUI-MiniMaxH3-TimelineDirector | audio lock for lip-sync | Songssx — [Songssx/ComfyUI-MiniMaxH3-TimelineDirector](https://github.com/Songssx/ComfyUI-MiniMaxH3-TimelineDirector) |
| Comfyui_Minimax_h3_latent_Upscaler | HD two-pass node | LBH-123-AI — [LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler](https://github.com/LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler) |
| 3D Camera Control for H3 | 🎥 Camera tab | NyckM — [NyckM/3d-Camera-control-H3-Minimax](https://github.com/NyckM/3d-Camera-control-H3-Minimax) |
| ComfyUI-MiniMax-H3-Edit | camera prompt encoding | ethanfel — [ethanfel/ComfyUI-MiniMax-H3-Edit](https://github.com/ethanfel/ComfyUI-MiniMax-H3-Edit) |
| ComfyUI-SeedVR2_VideoUpscaler | 🔍 upscale node | numz — [numz/ComfyUI-SeedVR2_VideoUpscaler](https://github.com/numz/ComfyUI-SeedVR2_VideoUpscaler) |
| h3-prompt-writing skill | official prompt format, guides in the library | MiniMax — [MiniMax-AI/MiniMax-H3](https://github.com/MiniMax-AI/MiniMax-H3) |
| Gradio | the web interface | Hugging Face — [gradio-app/gradio](https://github.com/gradio-app/gradio) |
| FFmpeg (via imageio-ffmpeg) | video cutting and joining | [FFmpeg](https://ffmpeg.org/) · [imageio/imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg) |
| 7-Zip (7zr.exe) | `setup.bat` unpacks ComfyUI portable | Igor Pavlov — [7-zip.org](https://www.7-zip.org/) |

The idea for the ✨ AI prompt writer comes from 青橙Lab's tutorial
[MiniMax H3 专业自动提示词](https://www.youtube.com/watch?v=Crp5GtXdqEA).
