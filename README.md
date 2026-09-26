# MiniMax H3 Portable Panel · 影音創作面板

A local Gradio panel for [MiniMax H3](https://huggingface.co/MiniMaxAI/MiniMax-H3) open video+audio
generation on one NVIDIA card with **12–32 GB VRAM**. ComfyUI backend, fully local inference, no cloud API.
The panel detects your VRAM at start-up and adjusts itself — no settings to learn.

在本機 NVIDIA 顯卡（**12～32 GB 顯存**）上跑 MiniMax H3 開源影音生成的 Gradio 面板，後端是 ComfyUI，全程本機推論、不使用雲端 API。
開啟時自動偵測顯存並調整設定，不用自己記參數。

**Traditional Chinese / English**: the interface follows your browser language (any Chinese browser → 繁體中文,
everything else → English); the 🌐 button at the top switches and remembers your choice.
介面語言自動跟隨瀏覽器（中文瀏覽器顯示繁體中文，其他顯示英文），也可以按上方 🌐 按鈕切換並記住。

Tabs / 分頁：Text-to-Video · FL2VA keyframes · Ref2VA reference · V2V · lip-sync · SeedVR2 video upscale ·
Krea2 image generation · Qwen-Image editing · 🖍️ brush editing (scribble a few strokes → AI redraws them
as real objects) · 3D camera · storyboard · history · 🌐 prompt site ([ArchiPrompt](https://archi-prompt.com/),
architecture / landscape / interior AI prompts, embedded).

**Prompt library / 提示詞範本庫**: every generation tab has a browsable library of ready-to-use
prompts with **Krea2-rendered thumbnails** — architecture, people, food, animals, nature, product,
transport, sports, sci-fi, plus MiniMax's official prompt-writing guides. The 建築/人物/animation
templates are written in H3's **official three-field spec** (`integrated_multimodal_description` /
`overall_soundscape` / `non_diegetic_music`). The storyboard tab has 15 ready-made stories (architecture,
interiors, landscape, real-estate sales, people). 每個生成分頁都有帶**縮圖**的提示詞範本庫，範本依 MiniMax 官方三段格式撰寫；編劇分頁另有 15 個故事範本。

**✨ AI prompt writer / AI 專業提示詞**: type one line (Chinese is fine), optionally add a picture, and a local
Qwen3-VL model writes it in H3's official format — three fields, camera moves, `(S1)` + `<d>[Chinese] …</d>`
dialogue — for the text-to-video, keyframe, storyboard and image tabs. Free and offline, a few seconds.
輸入一句話（可附圖），本機 Qwen3-VL 自動寫成官方格式提示詞；文生／首尾幀／編劇／圖片分頁都有。

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

- **NVIDIA GPU with 12–32 GB VRAM.** The panel reads the card at start-up and switches off what it
  cannot run. 開啟時自動偵測顯存，跑不動的選項會自動關閉：

  | VRAM 顯存 | Works well 建議用法 | Turned off automatically 自動關閉 |
  | --- | --- | --- |
  | 24–32 GB (4090 / 5090 / 3090) | everything, incl. HD two-pass and Full HD 全部功能 | — |
  | 16 GB (4080 / 5080 / 4070 Ti S) | Q4 models, 864×480–960×544, 4–10 s | HD two-pass, Full HD 高清二次採樣、Full HD |
  | 12 GB (4070 / 3060 12G) | Q4 models, 864×480, 4–6 s | same; SeedVR2 offloads more to CPU 同上 |

  Smaller cards: generate at 864×480, then upscale in the 🔍 tab (SeedVR2). 小顯存先用 864×480 生成，再用「🔍 放大」升解析度。
- **System RAM 32 GB+** (64 GB recommended for 12–16 GB cards). 系統記憶體 32 GB 以上，12～16 GB 顯卡建議 64 GB。
- **Windows 10 (1803+) or 11**, and **~200 GB free disk** (core set ~38 GB, plus any optional models).
  No git or Python setup needed — the ComfyUI portable brings its own Python, and `install.bat` uses
  Windows' built-in `curl`/`tar`. 不需要安裝 git 或 Python。

## Install / 安裝 — one click / 一鍵

**Easiest:** download **[`setup.bat`](../../raw/main/setup.bat)** (right-click ▸ Save link as…), put it in an
**empty folder** on a drive with ~200 GB free, and **double-click it**. It downloads ComfyUI portable
(pinned v0.36.0), the panel and the core H3 models, then launches the WebUI — no git, no 7-Zip needed.
It's resumable: if a download drops, run it again. Windows SmartScreen may warn about an unrecognized
app — click **More info ▸ Run anyway** (it's an unsigned `.bat` that only downloads the files below).
最省事：下載 `setup.bat`，放進一顆空資料夾（磁碟需 ~200 GB），**雙擊**它，全程自動（免 git、免 7-Zip）。
SmartScreen 若跳警告，按「更多資訊 ▸ 仍要執行」。

Prefer to do it by hand, or already have ComfyUI portable? Use the three manual steps below.
想手動、或已經有 ComfyUI portable，就用下面三步。

## Install / 安裝 — three steps (manual) / 三步（手動）

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

**Optional models / 選用模型** — double-click **`download_extras.bat`** and type a number
（雙擊 `download_extras.bat`，輸入數字即可）:
1 Krea2 image model for the 🎨 tab (~19 GB) · 2 Krea2 style LoRAs · 3 Qwen-Image-2.1 for the 🖌️ edit tab (~17 GB) ·
4 SeedVR2 for the 🔍 upscale tab (~7 GB) · 5 HD two-pass upscaler (24 GB cards) · 6 Heretic text encoder ·
7 the ✨ AI prompt writer (~5 GB; already included in 1 or 3).
A tab whose model is missing says which number to pick. 缺模型的分頁會直接告訴你要選哪個數字。

**🔞 NSFW community models (18+, download yourself) / 成人向社群模型（自行下載）** — the installers never fetch
them. Where to download 10Eros-Max and DaSiWa, which folder to put them in, and how to pick them in the panel:
**[NSFW_MODELS.md](NSFW_MODELS.md)**. 安裝程式不會下載；下載位置、放哪個資料夾、怎麼在面板選用，請看 **[NSFW_MODELS.md](NSFW_MODELS.md)**。

Full per-tab notes (Traditional Chinese): [RTX4090_LOCAL.md](RTX4090_LOCAL.md).

## Helper scripts / 常用批次檔

| File | 作用 |
| --- | --- |
| `run_webui.bat` | Start / open the panel · 啟動或開啟面板 |
| `restart_webui.bat` | Restart panel + backend (refuses while a job runs) · 重啟（有任務時拒絕） |
| `cancel_generation.bat` | Cancel current + queued jobs · 取消目前與排隊生成 |
| `free_vram.bat` | Unload models, free VRAM · 卸載模型、釋放顯存 |
| `download_extras.bat` | Optional models menu · 選用模型下載選單 |

To force a smaller VRAM profile (e.g. if detection misreads the card), run `set H3_VRAM_GB=16` in a
command prompt before `run_webui.bat`. 偵測錯誤時可先 `set H3_VRAM_GB=16` 再啟動，強制使用較小的設定。

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

This panel only glues together other people's work. Thank you to every model and code author below —
please visit their pages, star their repos and follow their licences.
這個面板只是把以下作者的成果串在一起，衷心感謝每一位模型與程式的提供者；請到原始頁面支持他們，並遵守各自的授權。

### Models / 模型提供者

| Model 模型 | Used for 用途 | Author 作者 · Source 出處 |
| --- | --- | --- |
| MiniMax H3 (FL2VA / Ref2VA, VAEs, Turbo LoRAs) | all video tabs 所有影音分頁 | MiniMax — [MiniMaxAI/MiniMax-H3](https://huggingface.co/MiniMaxAI/MiniMax-H3) · ComfyUI packaging by Comfy-Org [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3) |
| MiniMax H3 Q4_K_M GGUF | default diffusion models 預設擴散模型 | leejet — [leejet/MiniMax-H3-GGUF](https://huggingface.co/leejet/MiniMax-H3-GGUF) |
| Qwen3-VL-32B NVFP4 text encoder / INT8 video VAE | text encoding, lower-VRAM decode 文字編碼、省顯存解碼 | Qwen team (Alibaba) · Comfy-Org — [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3) |
| Qwen3-VL-32B Heretic (uncensored) encoder | optional 選用 | sakamakismile — [Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4](https://huggingface.co/sakamakismile/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4) |
| H3 latent upscaler 3D | HD two-pass 高清二次採樣 | LBH-123-AI — [Minimax_h3_latent_Upscaler](https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler) |
| SeedVR2 3B + EMA VAE | 🔍 video upscale 影片放大 | ByteDance Seed — [ByteDance-Seed/SeedVR](https://github.com/ByteDance-Seed/SeedVR) · ComfyUI weights by numz [numz/SeedVR2_comfyUI](https://huggingface.co/numz/SeedVR2_comfyUI) |
| Krea 2 Turbo + style LoRAs | 🎨 image tab, template thumbnails 圖片分頁、範本縮圖 | Krea — ComfyUI packaging by Comfy-Org [Comfy-Org/Krea-2](https://huggingface.co/Comfy-Org/Krea-2) |
| Qwen-Image-2.1 + Qwen3-VL 8B | 🖌️ image editing 修圖 | Qwen team — [Qwen/Qwen-Image-2.1](https://huggingface.co/Qwen/Qwen-Image-2.1) · [Comfy-Org/Qwen-Image-2.1](https://huggingface.co/Comfy-Org/Qwen-Image-2.1) · optional GGUF by [AlperKTS](https://huggingface.co/AlperKTS/Qwen-Image-2.1-GGUF) and [abenzerps](https://huggingface.co/abenzerps/Qwen-Image-2.1-GGUF) |
| Qwen3-VL 4B / 8B | ✨ AI prompt writer AI 專業提示詞 | Qwen team — via [Comfy-Org/Krea-2](https://huggingface.co/Comfy-Org/Krea-2) and [Comfy-Org/Qwen-Image-2.1](https://huggingface.co/Comfy-Org/Qwen-Image-2.1) |

### Code & tools / 程式提供者

| Project 專案 | Used for 用途 | Author 作者 · Source 出處 |
| --- | --- | --- |
| ComfyUI (incl. native MiniMax H3, Qwen-Image and TextGenerate nodes) | backend 後端引擎 | comfyanonymous & Comfy-Org — [comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI) |
| ComfyUI-GGUF-Loader | loads the Q4 GGUF models 載入 GGUF 模型 | ChrisColeTech — [ChrisColeTech/ComfyUI-GGUF-Loader](https://github.com/ChrisColeTech/ComfyUI-GGUF-Loader) |
| ComfyUI-MiniMaxH3-TimelineDirector | audio lock for lip-sync 對嘴音軌鎖定 | Songssx — [Songssx/ComfyUI-MiniMaxH3-TimelineDirector](https://github.com/Songssx/ComfyUI-MiniMaxH3-TimelineDirector) |
| Comfyui_Minimax_h3_latent_Upscaler | HD two-pass node 高清二次採樣節點 | LBH-123-AI — [LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler](https://github.com/LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler) |
| 3D Camera Control for H3 | 🎥 camera tab 攝影機分頁 | NyckM — [NyckM/3d-Camera-control-H3-Minimax](https://github.com/NyckM/3d-Camera-control-H3-Minimax) |
| ComfyUI-MiniMax-H3-Edit | camera prompt encoding 攝影機提示詞編碼 | ethanfel — [ethanfel/ComfyUI-MiniMax-H3-Edit](https://github.com/ethanfel/ComfyUI-MiniMax-H3-Edit) |
| ComfyUI-SeedVR2_VideoUpscaler | 🔍 upscale node 放大節點 | numz — [numz/ComfyUI-SeedVR2_VideoUpscaler](https://github.com/numz/ComfyUI-SeedVR2_VideoUpscaler) |
| h3-prompt-writing skill | official prompt format, guides in the library 官方提示詞格式與指南 | MiniMax — [MiniMax-AI/MiniMax-H3](https://github.com/MiniMax-AI/MiniMax-H3) |
| Gradio | the web interface 網頁介面 | Hugging Face — [gradio-app/gradio](https://github.com/gradio-app/gradio) |
| FFmpeg (via imageio-ffmpeg) | video cutting / joining 影片剪接 | [FFmpeg](https://ffmpeg.org/) · [imageio/imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg) |
| 7-Zip (7zr.exe) | `setup.bat` unpacks ComfyUI portable 解壓縮 | Igor Pavlov — [7-zip.org](https://www.7-zip.org/) |

Idea for the ✨ AI prompt writer: 青橙Lab's tutorial
[MiniMax H3 专业自动提示词](https://www.youtube.com/watch?v=Crp5GtXdqEA). ✨ AI 專業提示詞的構想來自青橙Lab 的教學影片。
