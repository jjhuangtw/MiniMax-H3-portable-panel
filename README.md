# MiniMax H3 Portable Panel · 影音創作面板

A local Gradio panel for [MiniMax H3](https://huggingface.co/MiniMaxAI/MiniMax-H3) open video+audio
generation on a single RTX 4090 (24 GB). ComfyUI backend, fully local inference, no cloud API.

在本機 RTX 4090（24 GB）上跑 MiniMax H3 開源影音生成的 Gradio 面板，後端是 ComfyUI，全程本機推論、不使用雲端 API。

Tabs / 分頁：Text-to-Video · FL2VA keyframes · Ref2VA reference · segmented long video ·
SeedVR2 video upscale · Krea2 image generation · 3D camera · storyboard · history.

> This repo contains **only the panel code and download scripts**. Model weights are not included;
> the install scripts fetch them from the official sources and verify every SHA-256.
> 本 repo 只包含面板**程式碼與下載腳本**，不含模型權重；安裝時由腳本自官方來源下載並核對 SHA-256。

![panel](docs/panel.png)

| Text-to-Video (HD two-pass) | SeedVR2 upscale (before → after) |
| --- | --- |
| ![text to video](docs/example_text_to_video.png) | ![seedvr2 upscale](docs/example_seedvr2_upscale.png) |

Krea2 image styles / 圖片風格 LoRA：

![krea2 styles](docs/example_krea2_styles.png)

---

## Requirements / 需要準備

- **NVIDIA GPU**, 24 GB VRAM recommended (RTX 4090). Smaller cards work at lower resolution / length / batch.
  建議 24 GB VRAM；較小的卡需降低解析度、片長與批次。
- **Windows 10 (1803+) or 11**, and **~200 GB free disk** (core set ~35 GB, plus any optional models).
  No git or Python setup needed — the ComfyUI portable brings its own Python, and `install.bat` uses
  Windows' built-in `curl`/`tar`. 不需要安裝 git 或 Python。

## Install / 安裝 — three steps / 三步

**1. Get ComfyUI portable.** Download `ComfyUI_windows_portable_nvidia.7z` from the
   [ComfyUI releases](https://github.com/comfyanonymous/ComfyUI/releases) (use the **latest** — the panel
   is tested on v0.36.0) and extract it with [7-Zip](https://www.7-zip.org/). You get a folder containing
   `python_embeded\` and `ComfyUI\`.
   下載最新版 ComfyUI portable（`.7z`），用 7-Zip 解壓，得到含 `python_embeded\`、`ComfyUI\` 的資料夾。

**2. Add the panel.** On this GitHub page click **Code ▸ Download ZIP**, extract it, and copy everything
   inside into the ComfyUI portable folder from step 1 — so `install.bat` sits **next to** `python_embeded\`.
   在本頁按 **Code ▸ Download ZIP**，解壓後把裡面**所有檔案**複製進步驟 1 的資料夾，讓 `install.bat` 和
   `python_embeded\` 並排。

**3. Double-click `install.bat`.** It sets up the packages, downloads the custom nodes (no git) and the
   core H3 models with SHA-256 checks, then offers to launch. After that just double-click **`run_webui.bat`**
   and open http://127.0.0.1:7860 . `install.bat` is resumable — if a download drops, run it again.
   雙擊 `install.bat`：裝套件、免 git 下載 custom node 與核心模型（核對雜湊），跑完會問要不要開啟面板；
   之後平常用 `run_webui.bat`。中斷了再跑一次即可續傳。

Optional models — run these `.py` files yourself later if you want them / 之後想要再自行執行：
`download_heretic_encoder.py` (uncensored encoder, panel default), `download_int8_vae.py` (lower-VRAM
video VAE), `download_hd_models.py` (HD upscale), `download_seedvr2.py` (video upscaler),
`download_krea2_style_loras.py` (Krea2 style LoRAs).

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
