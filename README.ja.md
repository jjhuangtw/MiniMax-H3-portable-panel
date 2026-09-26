# MiniMax H3 Portable パネル

[繁體中文](README.md) | [English](README.en.md) | [简体中文](README.zh-CN.md) | **日本語**

**VRAM 12～32 GB** の NVIDIA GPU 1 枚で、オープンモデル [MiniMax H3](https://huggingface.co/MiniMaxAI/MiniMax-H3) を使って
音声付き動画を生成するローカル Gradio パネルです。バックエンドは ComfyUI で、推論はすべて手元の PC で行い、クラウド API は使いません。
起動時に VRAM を自動検出して設定を調整するので、パラメータを覚える必要はありません。

**表示言語**：ブラウザの言語に合わせて自動で切り替わります（中国語のブラウザは繁体字中国語、それ以外は英語）。日本語の UI はまだないため、
日本語のブラウザでは**英語の UI** が表示されます。このページのボタン名・タブ名は英語 UI の表記です。上部の 🌐 ボタンで切り替えると、選択が記憶されます。

**タブ**：Text to Video · Keyframes（FL2VA）· Reference（Ref2VA）· V2V · Lip-sync · SeedVR2 動画アップスケール ·
Krea2 画像生成 · Qwen-Image 画像編集 · 🖍️ Brush Edit（数本の線を描くと AI が本物の物体として描き直す）· 3D カメラ · Storyboard ·
History · 🌐 Prompt site（[ArchiPrompt](https://archi-prompt.com/) を埋め込み。建築・ランドスケープ・インテリアの AI プロンプト）。

**📚 プロンプトライブラリ**：すべての生成タブに、**Krea2 で生成したサムネイル**付きのプロンプト集があります。建築、人物、料理、動物、
自然、製品、乗り物、スポーツ、SF のほか、MiniMax 公式のプロンプト作成ガイドも収録。建築・人物・アニメのテンプレートは H3 の
**公式 3 項目形式**（`integrated_multimodal_description` / `overall_soundscape` / `non_diegetic_music`）で書かれています。
Storyboard タブにはストーリーのテンプレートが 15 本あります（建築、インテリア、ランドスケープ、不動産販売、人物）。

**✨ AI プロンプトライター**：一文を入力し（日本語も可）、必要なら画像を 1 枚添えると、ローカルの Qwen3-VL が H3 公式形式
（3 項目、カメラワーク、`(S1)` + `<d>[Chinese] …</d>` のセリフ）に書き直します。Text to Video、Keyframes、Storyboard、Image タブで使えます。
無料・オフラインで、数秒で完了します。

**🧷 LoRA**：🧩 Model settings に FL2VA 用と Ref2VA 用の LoRA メニューと強度スライダーがあり、すべての動画タブに適用されます。

> このリポジトリには**パネルのコードとダウンロードスクリプトのみ**が含まれ、モデルの重みは含まれません。インストール時にスクリプトが
> 公式の配布元からダウンロードし、すべての SHA-256 を検証します。

![パネル](docs/panel.png)

| Text to Video（HD 2 パス） | SeedVR2 アップスケール（前 → 後） |
| --- | --- |
| ![text to video](docs/example_text_to_video.png) | ![seedvr2 upscale](docs/example_seedvr2_upscale.png) |

Krea2 画像スタイル LoRA：

![krea2 styles](docs/example_krea2_styles.png)

---

## 必要なもの

- **VRAM 12～32 GB の NVIDIA GPU。** 起動時に VRAM を検出し、動かせない機能は自動でオフになります：

  | VRAM | おすすめの使い方 | 自動でオフ |
  | --- | --- | --- |
  | 24～32 GB（4090 / 5090 / 3090） | すべての機能（HD 2 パス、Full HD を含む） | — |
  | 16 GB（4080 / 5080 / 4070 Ti S） | Q4 モデル、864×480～960×544、4～10 秒 | HD 2 パス、Full HD |
  | 12 GB（4070 / 3060 12G） | Q4 モデル、864×480、4～6 秒 | 同上。SeedVR2 は CPU への退避が増えます |

  VRAM が少ない場合は 864×480 で生成し、🔍 Upscale タブ（SeedVR2）で解像度を上げてください。
- **メモリ 32 GB 以上**（VRAM 12～16 GB の場合は 64 GB 推奨）。
- **Windows 10（1803 以降）または 11**、ディスクの空き容量 **約 200 GB**（コアモデル約 38 GB ＋ 追加モデル）。
  git や Python のインストールは不要です。ComfyUI portable に Python が同梱され、`install.bat` は Windows 標準の `curl`／`tar` を使います。

## インストール：ワンクリック

**いちばん簡単**：**[`setup.bat`](../../raw/main/setup.bat)** をダウンロードし（右クリック ▸ 名前を付けてリンク先を保存）、空き容量が
約 200 GB あるドライブの**空のフォルダー**に置いて**ダブルクリック**します。ComfyUI portable（v0.36.0 固定）、パネル、H3 のコアモデルを
ダウンロードし、最後にパネルを起動します。git も 7-Zip も不要です。途中で止まっても、もう一度実行すれば続きから再開します。
Windows SmartScreen が「認識されないアプリ」と警告した場合は **「詳細情報 ▸ 実行」** をクリックしてください
（署名のない `.bat` で、下記のファイルをダウンロードするだけです）。

手動で入れたい場合や、すでに ComfyUI portable がある場合は、下の 3 ステップを使ってください。

## インストール：手動 3 ステップ

**1. ComfyUI portable を入手。** [ComfyUI releases](https://github.com/comfyanonymous/ComfyUI/releases) から
   `ComfyUI_windows_portable_nvidia.7z` をダウンロードし（**最新版**で OK。パネルは v0.36.0 で検証）、[7-Zip](https://www.7-zip.org/)
   で展開します。`python_embeded\` と `ComfyUI\` を含むフォルダーができます。

**2. パネルを追加。** このページで **Code ▸ Download ZIP** をクリックして展開し、中の**すべてのファイル**をステップ 1 のフォルダーに
   コピーします。`install.bat` が `python_embeded\` と**同じ階層**に来るようにしてください。

**3. `install.bat` をダブルクリック。** パッケージのセットアップ、custom node（git 不要）と H3 コアモデルのダウンロード（SHA-256 検証）を
   行い、最後にパネルを起動するか尋ねます。以降は **`run_webui.bat`** をダブルクリックし、http://127.0.0.1:7860 を開くだけです。
   `install.bat` は途中から再開できます。止まったらもう一度実行してください。

**追加モデル**：**`download_extras.bat`** をダブルクリックし、番号を入力します：
1 Krea2 画像モデル（🎨 Image タブ、約 19 GB）· 2 Krea2 スタイル LoRA · 3 Qwen-Image-2.1（🖌️ Image Edit タブ、約 17 GB）·
4 SeedVR2（🔍 Upscale タブ、約 7 GB）· 5 HD 2 パス用アップスケーラー（24 GB GPU）· 6 Heretic テキストエンコーダー ·
7 ✨ AI プロンプトライター（約 5 GB。1 または 3 を選ぶと含まれます）。
モデルが足りないタブには、どの番号を選べばよいかが表示されます。

**🔞 成人向けコミュニティモデル（18 歳以上、各自でダウンロード）**：インストーラーはダウンロードしません。10Eros-Max と DaSiWa の
入手先、置くフォルダー、パネルでの選び方は **[NSFW_MODELS.ja.md](NSFW_MODELS.ja.md)** を参照してください。

タブごとの詳しい説明（繁体字中国語）：[RTX4090_LOCAL.md](RTX4090_LOCAL.md)。

## よく使うバッチファイル

| ファイル | 役割 |
| --- | --- |
| `run_webui.bat` | パネルを起動・表示 |
| `restart_webui.bat` | パネルとバックエンドを再起動（生成中は拒否） |
| `cancel_generation.bat` | 現在の生成と待機中の生成をキャンセル |
| `free_vram.bat` | モデルをアンロードして VRAM を解放 |
| `download_extras.bat` | 追加モデルのダウンロードメニュー |

VRAM の検出が正しくない場合は、コマンドプロンプトで `set H3_VRAM_GB=16` を実行してから `run_webui.bat` を起動すると、
小さめの設定を強制できます。

## ライセンスと利用上の注意

- パネルのコード：MIT（`LICENSE` を参照）。
- **モデルにはそれぞれのライセンスがあります。** インストール前に必ずお読みください。MiniMax H3 は MiniMax H3 Community License
  （適用範囲に EU、英国、韓国、米国は含まれません）、custom node の多くは GPL-3.0 または Apache-2.0 です。このリポジトリはモデルの重みを
  含まず、配布もしていません。
- ローカルで動くオープンソースのツールで、コンテンツフィルターはありません。法律を守って使ってください。**実在の人物の肖像で、性的・
  裸体・事実と異なる映像を作らないでください。** 成人向けの内容は、架空のキャラクターか、本人の同意を得た素材だけにしてください。
  同意のない合成映像の作成・共有は、多くの国で違法です。
- custom node とモデルは第三者の作品です。正確性・安全性・保守は各作者の責任です。

## クレジット

このパネルは、ほかの方々の成果をつなぎ合わせたものにすぎません。以下のモデルとコードの作者の皆さんに心から感謝します。
ぜひ元のページを訪れ、リポジトリにスターを付け、それぞれのライセンスを守ってください。

### モデル

| モデル | 用途 | 作者 · 出典 |
| --- | --- | --- |
| MiniMax H3（FL2VA / Ref2VA、VAE、Turbo LoRA） | すべての動画タブ | MiniMax — [MiniMaxAI/MiniMax-H3](https://huggingface.co/MiniMaxAI/MiniMax-H3) · ComfyUI 版：Comfy-Org [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3) |
| MiniMax H3 Q4_K_M GGUF | 既定の拡散モデル | leejet — [leejet/MiniMax-H3-GGUF](https://huggingface.co/leejet/MiniMax-H3-GGUF) |
| Qwen3-VL-32B NVFP4 テキストエンコーダー / INT8 動画 VAE | テキストエンコード、省 VRAM デコード | Qwen チーム（Alibaba）· Comfy-Org — [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3) |
| Qwen3-VL-32B Heretic（無検閲）エンコーダー | 任意 | sakamakismile — [Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4](https://huggingface.co/sakamakismile/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4) |
| H3 latent upscaler 3D | HD 2 パス | LBH-123-AI — [Minimax_h3_latent_Upscaler](https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler) |
| SeedVR2 3B + EMA VAE | 🔍 動画アップスケール | ByteDance Seed — [ByteDance-Seed/SeedVR](https://github.com/ByteDance-Seed/SeedVR) · ComfyUI 用重み：numz [numz/SeedVR2_comfyUI](https://huggingface.co/numz/SeedVR2_comfyUI) |
| Krea 2 Turbo + スタイル LoRA | 🎨 Image タブ、テンプレートのサムネイル | Krea — ComfyUI 版：Comfy-Org [Comfy-Org/Krea-2](https://huggingface.co/Comfy-Org/Krea-2) |
| Qwen-Image-2.1 + Qwen3-VL 8B | 🖌️ 画像編集 | Qwen チーム — [Qwen/Qwen-Image-2.1](https://huggingface.co/Qwen/Qwen-Image-2.1) · [Comfy-Org/Qwen-Image-2.1](https://huggingface.co/Comfy-Org/Qwen-Image-2.1) · 任意の GGUF：[AlperKTS](https://huggingface.co/AlperKTS/Qwen-Image-2.1-GGUF)、[abenzerps](https://huggingface.co/abenzerps/Qwen-Image-2.1-GGUF) |
| Qwen3-VL 4B / 8B | ✨ AI プロンプトライター | Qwen チーム — [Comfy-Org/Krea-2](https://huggingface.co/Comfy-Org/Krea-2) と [Comfy-Org/Qwen-Image-2.1](https://huggingface.co/Comfy-Org/Qwen-Image-2.1) 経由 |

### コード・ツール

| プロジェクト | 用途 | 作者 · 出典 |
| --- | --- | --- |
| ComfyUI（ネイティブの MiniMax H3、Qwen-Image、TextGenerate ノードを含む） | バックエンド | comfyanonymous & Comfy-Org — [comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI) |
| ComfyUI-GGUF-Loader | Q4 GGUF モデルの読み込み | ChrisColeTech — [ChrisColeTech/ComfyUI-GGUF-Loader](https://github.com/ChrisColeTech/ComfyUI-GGUF-Loader) |
| ComfyUI-MiniMaxH3-TimelineDirector | リップシンク用の音声ロック | Songssx — [Songssx/ComfyUI-MiniMaxH3-TimelineDirector](https://github.com/Songssx/ComfyUI-MiniMaxH3-TimelineDirector) |
| Comfyui_Minimax_h3_latent_Upscaler | HD 2 パス用ノード | LBH-123-AI — [LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler](https://github.com/LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler) |
| 3D Camera Control for H3 | 🎥 Camera タブ | NyckM — [NyckM/3d-Camera-control-H3-Minimax](https://github.com/NyckM/3d-Camera-control-H3-Minimax) |
| ComfyUI-MiniMax-H3-Edit | カメラ用プロンプトのエンコード | ethanfel — [ethanfel/ComfyUI-MiniMax-H3-Edit](https://github.com/ethanfel/ComfyUI-MiniMax-H3-Edit) |
| ComfyUI-SeedVR2_VideoUpscaler | 🔍 アップスケール用ノード | numz — [numz/ComfyUI-SeedVR2_VideoUpscaler](https://github.com/numz/ComfyUI-SeedVR2_VideoUpscaler) |
| h3-prompt-writing skill | 公式プロンプト形式、ライブラリ内のガイド | MiniMax — [MiniMax-AI/MiniMax-H3](https://github.com/MiniMax-AI/MiniMax-H3) |
| Gradio | Web インターフェース | Hugging Face — [gradio-app/gradio](https://github.com/gradio-app/gradio) |
| FFmpeg（imageio-ffmpeg 経由） | 動画のカット・結合 | [FFmpeg](https://ffmpeg.org/) · [imageio/imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg) |
| 7-Zip（7zr.exe） | `setup.bat` での ComfyUI portable の展開 | Igor Pavlov — [7-zip.org](https://www.7-zip.org/) |

✨ AI プロンプトライターのアイデアは、青橙Lab のチュートリアル動画
[MiniMax H3 专业自动提示词](https://www.youtube.com/watch?v=Crp5GtXdqEA) によるものです。
