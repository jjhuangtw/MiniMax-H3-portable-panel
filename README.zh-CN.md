# MiniMax H3 Portable 影音创作面板

[繁體中文](README.md) | [English](README.en.md) | **简体中文** | [日本語](README.ja.md)

在一张 **12～32 GB 显存**的 NVIDIA 显卡上，用 [MiniMax H3](https://huggingface.co/MiniMaxAI/MiniMax-H3) 开源模型生成带声音视频的本地 Gradio 面板。
后端是 ComfyUI，全程在自己的电脑上推理，不使用云端 API。启动时会自动检测显存并调整设置，不用自己记参数。

**界面语言**：自动跟随浏览器。中文浏览器（包括简体中文）显示**繁体中文**界面，其他语言显示英文；也可以点上方 🌐 按钮切换，
会记住你的选择。面板目前没有简体中文界面，本页提到的按钮与分页名称以繁体中文界面为准。

**分页**：文生影音 · 首尾帧（FL2VA）· 参考影音（Ref2VA）· V2V · 对口型 · SeedVR2 视频放大 · Krea2 图片生成 ·
Qwen-Image 修图 · 🖍️ 笔刷修图（画几笔，AI 把笔画变成真实物体）· 3D 摄像机 · 编剧分镜 · 记录 ·
🌐 提示词网站（内嵌 [ArchiPrompt](https://archi-prompt.com/)，建筑／景观／室内设计 AI 提示词）。

**📚 提示词模板库**：每个生成分页都有可浏览的现成提示词，附 **Krea2 生成的缩略图**，分类有建筑、人物、美食、动物、自然、产品、交通、
运动、科幻，以及 MiniMax 官方提示词指南。建筑／人物／动画模板按 H3 **官方三段格式**编写（`integrated_multimodal_description` /
`overall_soundscape` / `non_diegetic_music`）。编剧分页另有 15 个故事模板（建筑、室内设计、景观、房产销售、人物）。

**✨ AI 专业提示词**：输入一句话（中文即可），可以附一张图，本地的 Qwen3-VL 会把它写成 H3 官方格式，包含三段字段、运镜，以及
`(S1)` + `<d>[Chinese] …</d>` 台词格式。文生、首尾帧、编剧、图片分页都有，免费、离线，几秒完成。

**🧷 LoRA**：「🧩 模型設定」里有 FL2VA 与 Ref2VA 两个 LoRA 下拉菜单和强度滑块，作用于所有影音分页。

> 本仓库**只包含面板代码与下载脚本**，不含模型权重；安装时由脚本从官方来源下载，并逐一校验 SHA-256。

![面板](docs/panel.png)

| 文生影音（高清二次采样） | SeedVR2 放大（前 → 后） |
| --- | --- |
| ![文生影音](docs/example_text_to_video.png) | ![SeedVR2 放大](docs/example_seedvr2_upscale.png) |

Krea2 图片风格 LoRA：

![Krea2 风格](docs/example_krea2_styles.png)

---

## 需要准备

- **NVIDIA 显卡，12～32 GB 显存。** 启动时自动检测显存，跑不动的选项会自动关闭：

  | 显存 | 建议用法 | 自动关闭 |
  | --- | --- | --- |
  | 24～32 GB（4090 / 5090 / 3090） | 全部功能，包括高清二次采样与 Full HD | — |
  | 16 GB（4080 / 5080 / 4070 Ti S） | Q4 模型，864×480～960×544，4～10 秒 | 高清二次采样、Full HD |
  | 12 GB（4070 / 3060 12G） | Q4 模型，864×480，4～6 秒 | 同上；SeedVR2 会更多地卸载到 CPU |

  显存较小时，先用 864×480 生成，再到「🔍 放大」分页用 SeedVR2 提升分辨率。
- **内存 32 GB 以上**（12～16 GB 显卡建议 64 GB）。
- **Windows 10（1803 及以上）或 11**，硬盘约 **200 GB 可用空间**（核心模型约 38 GB，另加可选模型）。
  不需要安装 git 或 Python：ComfyUI portable 自带 Python，`install.bat` 使用 Windows 自带的 `curl`／`tar`。

## 安装：一键

**最省事**：下载 **[`setup.bat`](../../raw/main/setup.bat)**（右键 ▸ 链接另存为），放进一个**空文件夹**（所在硬盘需约 200 GB），
**双击**运行。它会下载 ComfyUI portable（固定 v0.36.0）、面板与核心 H3 模型，最后打开面板，全程无需 git、无需 7-Zip。
中断了再运行一次即可续传。Windows SmartScreen 若提示“无法识别的应用”，点 **“更多信息 ▸ 仍要运行”**
（这是未签名的 `.bat`，只会下载下列文件）。

想自己动手，或已经有 ComfyUI portable，就用下面三个步骤。

## 安装：手动三步

**1. 获取 ComfyUI portable。** 从 [ComfyUI releases](https://github.com/comfyanonymous/ComfyUI/releases) 下载
   `ComfyUI_windows_portable_nvidia.7z`（用**最新版**即可，面板在 v0.36.0 上测试），用 [7-Zip](https://www.7-zip.org/) 解压，
   会得到一个包含 `python_embeded\` 与 `ComfyUI\` 的文件夹。

**2. 加入面板。** 在本页点 **Code ▸ Download ZIP**，解压后把里面**所有文件**复制进第 1 步的文件夹，让 `install.bat` 和
   `python_embeded\` **位于同一层**。

**3. 双击 `install.bat`。** 它会安装依赖、无需 git 下载 custom node 与核心 H3 模型（校验 SHA-256），完成后询问是否打开面板。
   之后平时双击 **`run_webui.bat`**，打开 http://127.0.0.1:7860 即可。`install.bat` 支持续传，中断了再运行一次。

**可选模型**：双击 **`download_extras.bat`**，输入数字：
1 Krea2 图片模型（🎨 分页，约 19 GB）· 2 Krea2 风格 LoRA · 3 Qwen-Image-2.1（🖌️ 修图分页，约 17 GB）·
4 SeedVR2（🔍 放大分页，约 7 GB）· 5 高清二次采样放大模型（24 GB 显卡）· 6 Heretic 文本编码器 ·
7 ✨ AI 专业提示词（约 5 GB；选 1 或 3 时已包含）。
缺少模型的分页会直接告诉你要选哪个数字。

**🔞 成人向社区模型（18 岁以上，自行下载）**：安装程序不会下载。10Eros-Max 与 DaSiWa 去哪里下载、放在哪个文件夹、
怎么在面板中选用，请看 **[NSFW_MODELS.md](NSFW_MODELS.md)**（繁体中文／英文）。

各分页的详细说明（繁体中文）：[RTX4090_LOCAL.md](RTX4090_LOCAL.md)。

## 常用批处理文件

| 文件 | 作用 |
| --- | --- |
| `run_webui.bat` | 启动或打开面板 |
| `restart_webui.bat` | 重启面板与后端（有任务运行时会拒绝） |
| `cancel_generation.bat` | 取消当前与排队中的生成 |
| `free_vram.bat` | 卸载模型、释放显存 |
| `download_extras.bat` | 可选模型下载菜单 |

显存检测有误时，可以先在命令提示符执行 `set H3_VRAM_GB=16`，再运行 `run_webui.bat`，强制使用较小的配置。

## 许可与使用须知

- 面板代码：MIT，见 `LICENSE`。
- **模型各有自己的许可**，安装前请自行阅读。MiniMax H3 采用 MiniMax H3 Community License（适用范围不含欧盟、英国、韩国与美国）；
  custom node 大多是 GPL-3.0 或 Apache-2.0。本仓库不包含也不分发任何模型权重。
- 这是本地、开源、未加内容过滤的工具，请合法使用。**请勿用真人肖像制作色情、裸露或虚假影像。** 成人内容只用虚构角色，
  或取得当事人同意的素材。未经同意制作或传播他人的合成影像，在许多地方是违法的。
- custom node 与模型均为第三方作品，其正确性、安全性与维护由原作者负责。

## 致谢

这个面板只是把以下作者的成果串在一起，衷心感谢每一位模型与代码的提供者。请到原始页面支持他们、给仓库点星，并遵守各自的许可。

### 模型提供者

| 模型 | 用途 | 作者 · 出处 |
| --- | --- | --- |
| MiniMax H3（FL2VA / Ref2VA、VAE、Turbo LoRA） | 所有影音分页 | MiniMax — [MiniMaxAI/MiniMax-H3](https://huggingface.co/MiniMaxAI/MiniMax-H3) · ComfyUI 打包：Comfy-Org [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3) |
| MiniMax H3 Q4_K_M GGUF | 默认扩散模型 | leejet — [leejet/MiniMax-H3-GGUF](https://huggingface.co/leejet/MiniMax-H3-GGUF) |
| Qwen3-VL-32B NVFP4 文本编码器 / INT8 视频 VAE | 文本编码、省显存解码 | Qwen 团队（阿里巴巴）· Comfy-Org — [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3) |
| Qwen3-VL-32B Heretic（无审查）编码器 | 可选 | sakamakismile — [Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4](https://huggingface.co/sakamakismile/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4) |
| H3 latent upscaler 3D | 高清二次采样 | LBH-123-AI — [Minimax_h3_latent_Upscaler](https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler) |
| SeedVR2 3B + EMA VAE | 🔍 视频放大 | ByteDance Seed — [ByteDance-Seed/SeedVR](https://github.com/ByteDance-Seed/SeedVR) · ComfyUI 权重：numz [numz/SeedVR2_comfyUI](https://huggingface.co/numz/SeedVR2_comfyUI) |
| Krea 2 Turbo + 风格 LoRA | 🎨 图片分页、模板缩略图 | Krea — ComfyUI 打包：Comfy-Org [Comfy-Org/Krea-2](https://huggingface.co/Comfy-Org/Krea-2) |
| Qwen-Image-2.1 + Qwen3-VL 8B | 🖌️ 修图 | Qwen 团队 — [Qwen/Qwen-Image-2.1](https://huggingface.co/Qwen/Qwen-Image-2.1) · [Comfy-Org/Qwen-Image-2.1](https://huggingface.co/Comfy-Org/Qwen-Image-2.1) · 可选 GGUF：[AlperKTS](https://huggingface.co/AlperKTS/Qwen-Image-2.1-GGUF)、[abenzerps](https://huggingface.co/abenzerps/Qwen-Image-2.1-GGUF) |
| Qwen3-VL 4B / 8B | ✨ AI 专业提示词 | Qwen 团队 — 经由 [Comfy-Org/Krea-2](https://huggingface.co/Comfy-Org/Krea-2) 与 [Comfy-Org/Qwen-Image-2.1](https://huggingface.co/Comfy-Org/Qwen-Image-2.1) |

### 代码提供者

| 项目 | 用途 | 作者 · 出处 |
| --- | --- | --- |
| ComfyUI（含原生 MiniMax H3、Qwen-Image 与 TextGenerate 节点） | 后端引擎 | comfyanonymous & Comfy-Org — [comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI) |
| ComfyUI-GGUF-Loader | 加载 Q4 GGUF 模型 | ChrisColeTech — [ChrisColeTech/ComfyUI-GGUF-Loader](https://github.com/ChrisColeTech/ComfyUI-GGUF-Loader) |
| ComfyUI-MiniMaxH3-TimelineDirector | 对口型音轨锁定 | Songssx — [Songssx/ComfyUI-MiniMaxH3-TimelineDirector](https://github.com/Songssx/ComfyUI-MiniMaxH3-TimelineDirector) |
| Comfyui_Minimax_h3_latent_Upscaler | 高清二次采样节点 | LBH-123-AI — [LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler](https://github.com/LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler) |
| 3D Camera Control for H3 | 🎥 摄像机分页 | NyckM — [NyckM/3d-Camera-control-H3-Minimax](https://github.com/NyckM/3d-Camera-control-H3-Minimax) |
| ComfyUI-MiniMax-H3-Edit | 摄像机提示词编码 | ethanfel — [ethanfel/ComfyUI-MiniMax-H3-Edit](https://github.com/ethanfel/ComfyUI-MiniMax-H3-Edit) |
| ComfyUI-SeedVR2_VideoUpscaler | 🔍 放大节点 | numz — [numz/ComfyUI-SeedVR2_VideoUpscaler](https://github.com/numz/ComfyUI-SeedVR2_VideoUpscaler) |
| h3-prompt-writing skill | 官方提示词格式、模板库中的指南 | MiniMax — [MiniMax-AI/MiniMax-H3](https://github.com/MiniMax-AI/MiniMax-H3) |
| Gradio | 网页界面 | Hugging Face — [gradio-app/gradio](https://github.com/gradio-app/gradio) |
| FFmpeg（经由 imageio-ffmpeg） | 视频剪辑拼接 | [FFmpeg](https://ffmpeg.org/) · [imageio/imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg) |
| 7-Zip（7zr.exe） | `setup.bat` 解压 ComfyUI portable | Igor Pavlov — [7-zip.org](https://www.7-zip.org/) |

✨ AI 专业提示词的构想来自青橙Lab 的教程视频
[MiniMax H3 专业自动提示词](https://www.youtube.com/watch?v=Crp5GtXdqEA)。
