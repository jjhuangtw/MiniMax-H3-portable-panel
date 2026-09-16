# MiniMax H3 Portable Panel · 影音創作面板

A local Gradio panel for [MiniMax H3](https://huggingface.co/MiniMaxAI/MiniMax-H3) open video+audio
generation on a single RTX 4090 (24 GB). ComfyUI backend, fully local inference, no cloud API.

在本機 RTX 4090（24 GB）上跑 MiniMax H3 開源影音生成的 Gradio 面板，後端是 ComfyUI，全程本機推論、不使用雲端 API。

Tabs / 分頁：Text-to-Video · FL2VA keyframes · Ref2VA reference · segmented long video ·
SeedVR2 video upscale · Krea2 image generation · 3D camera · storyboard · history.

> This repo contains **only the panel code and download scripts**. Model weights are not included;
> the install scripts fetch them from the official sources and verify every SHA-256.
> 本 repo 只包含面板**程式碼與下載腳本**，不含模型權重；安裝時由腳本自官方來源下載並核對 SHA-256。

| Text-to-Video (HD two-pass) | SeedVR2 upscale (before → after) |
| --- | --- |
| ![text to video](docs/example_text_to_video.png) | ![seedvr2 upscale](docs/example_seedvr2_upscale.png) |

Krea2 image styles / 圖片風格 LoRA：

![krea2 styles](docs/example_krea2_styles.png)

---

## Requirements / 需要準備

1. **NVIDIA GPU**, 24 GB VRAM recommended (RTX 4090). Smaller cards work at lower resolution / length / batch.
   建議 24 GB VRAM；較小的卡需降低解析度、片長與批次。
2. **ComfyUI Portable (Windows)** — download `ComfyUI_windows_portable` from the
   [ComfyUI releases](https://github.com/comfyanonymous/ComfyUI/releases); it unpacks to
   `python_embeded\` + `ComfyUI\`.
3. **git** and **~200 GB free disk** (core set is ~35 GB, plus optional models).

## Install / 安裝

1. Put this repo's files into the ComfyUI portable root, next to `python_embeded\` and `ComfyUI\`.
   把本 repo 檔案放進 ComfyUI portable 根目錄，和 `python_embeded\`、`ComfyUI\` 並排。
2. Double-click **`install.bat`**. It installs the Python packages, clones the required custom nodes
   (pinned revisions), and downloads the core H3 models (Q4 diffusion, text encoder, video/audio VAE,
   two Turbo LoRAs) with SHA-256 verification.
   雙擊 `install.bat`：裝套件、clone custom node（固定版本）、下載核心 H3 模型並核對雜湊。
3. Double-click **`run_webui.bat`** and open http://127.0.0.1:7860 .

Optional models — run these yourself if you want them / 可選模型自行執行：
`download_heretic_encoder.py`, `download_hd_models.py`, `download_seedvr2.py`, `download_krea2_style_loras.py`.

Full per-tab notes (Traditional Chinese): [RTX4090_LOCAL.md](RTX4090_LOCAL.md).

## Helper scripts / 常用批次檔

| File | 作用 |
| --- | --- |
| `run_webui.bat` | Start / open the panel · 啟動或開啟面板 |
| `restart_webui.bat` | Restart panel + backend (refuses while a job runs) · 重啟（有任務時拒絕） |
| `cancel_generation.bat` | Cancel current + queued jobs · 取消目前與排隊生成 |
| `free_vram.bat` | Unload models, free VRAM · 卸載模型、釋放顯存 |

## License & responsible use / 授權與使用須知

- Panel code: see `LICENSE` (MIT). / 面板程式碼採 MIT。
- **Models carry their own licenses** — read them before installing. MiniMax H3 uses the MiniMax H3
  Community License (its scope excludes the EU, UK, Korea and the US); the custom nodes are mostly
  GPL-3.0 or Apache-2.0. This repo does not contain or distribute any model weights.
  模型各有授權，安裝前請自行閱讀；本 repo 不含也不散布任何權重。
- This is a local, open-source, non-content-filtered tool. Use it lawfully. **Do not make sexual,
  nude, or fabricated imagery of real people's likenesses.** Adult content only with fictional
  characters or with the consent of the person depicted. Creating or sharing non-consensual
  synthetic imagery of others is illegal in many places.
  這是本機開源、未加內容過濾的工具。**請勿以真人肖像製作性感、裸露或不實影像**；成人內容只用虛構角色或取得本人同意的素材。
- Custom nodes and models are third-party; their correctness, safety and maintenance are their own.

## Credits / 致謝

MiniMax H3 (MiniMaxAI), Comfy-Org, ComfyUI, and the authors of TimelineDirector, H3 Latent Upscaler,
SeedVR2, 3D Camera Control and H3 Edit custom nodes.
