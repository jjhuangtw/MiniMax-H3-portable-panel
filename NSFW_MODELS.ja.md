# 🔞 成人向けコミュニティモデル（各自でダウンロード）

[繁體中文](NSFW_MODELS.md) | [English](NSFW_MODELS.en.md) | [简体中文](NSFW_MODELS.zh-CN.md) | **日本語**

> **18 歳以上限定。** 以下は、コミュニティの作者が MiniMax H3 をファインチューニングした第三者のモデルで、それぞれ 14～21 GB あります。
> パネルのインストーラーはこれらを**ダウンロードしません**。このリポジトリにも含まれず、配布もしていません。各自でダウンロードし、
> 作者のライセンスを読み、このページ末尾の利用ルールを守ってください。
>
> 日本語のブラウザではパネルが英語 UI で表示されるため、以下のボタン名・メニュー名は英語 UI の表記です。

## どれを選ぶか

| モデル | ファイルサイズ | VRAM | 使えるメニュー |
| --- | --- | --- | --- |
| **10Eros-Max** beta5 Turbo ハイブリッド w4a8 | 14.0 GB | 24 GB 以上（RTX 4090 で検証済み） | FL2VA ＋ Ref2VA |
| **DaSiWa MiniMax H3** Hybrid Turbo v2 INT8 | 21.0 GB | 24 GB 以上（RTX 4090 で検証済み） | FL2VA ＋ Ref2VA |

どちらも**ハイブリッドモデル**（1 つのファイルが FL2VA と Ref2VA の両方のメニューに表示されます）で、**Turbo 蒸留が組み込み済み**です。
8 ステップで動き、Turbo LoRA は不要です。どちらか一方で十分です。

VRAM 12～16 GB の場合：より小さい版もありますが、**このパネルではどれも未検証**です。DaSiWa の int4 ファイル（12.5 GB、下記参照）と、
コミュニティによる 10Eros-Max の GGUF 版（[Abiray/10Eros-Max-GGUF](https://huggingface.co/Abiray/10Eros-Max-GGUF)、Q3_K_M 8.9 GB · Q4_K_M 11.6 GB）。
GGUF 版は**以前のテスト版（Test4）**をもとにしています。サンプリング設定はそのモデルページの説明に従ってください。

## ファイルの置き場所

どちらのファイルも、公式の H3 モデルと**同じフォルダー**に置きます：

```
<インストールフォルダー>\ComfyUI\models\diffusion_models\
```

- `setup.bat` でインストールした場合：`setup.bat のあるフォルダー\ComfyUI_windows_portable\ComfyUI\models\diffusion_models\`
- 手動でインストールした場合：`run_webui.bat` の隣にある `ComfyUI\models\diffusion_models\`

**ダウンロードしたときのファイル名のままにしてください。** パネルはファイル名で判断します。ファイル名に `Turbo` があるとサンプリングモードが
自動で **Built-in distill · 8 steps** に切り替わり、`10Eros`／`Dasiwa` があるとメニューにラベルが表示されます。名前を変える場合も、これらの語は残してください。

## 1. 10Eros-Max（TenStrip）

- モデルページ：https://huggingface.co/TenStrip/10Eros-Max（*Not-For-All-Audiences* 指定。ライセンス：MiniMax H3 Community License）
- ファイル：`10Eros_Max_h3_TURBO-hybrid_beta5_w4a8_14gb_optimized.safetensors`（13,997,668,774 bytes）
- 直接ダウンロード：
  https://huggingface.co/TenStrip/10Eros-Max/resolve/8a198588c8870ab0d613b3492a3150d091c8c2dd/10Eros_Max_h3_TURBO-hybrid_beta5_w4a8_14gb_optimized.safetensors
- SHA-256：`a8067999c65594b462d581c02b8a0573dd42d9812a14c586150a947c13388f2e`
- **beta5** を使ってください。作者によると beta3／beta4 は壊れたテスト版です。

## 2. DaSiWa MiniMax H3（Civitai）

- モデルページ：https://civitai.com/models/2877206/dasiwa-minimax-h3
- ページで **DaSiWa Hybrid Turbo v2** のバージョンを選び、**int8** と表示されたファイル（約 20.5 GB）をダウンロードします。このページを表示するには
  Civitai の無料アカウントにログインし、成人向けコンテンツの表示をオンにする必要があります。各自で設定してください。
- ファイル：`DasiwaMinimaxH3_dasiwaHybridTurboV2_3203135.safetensors`（20,967,669,168 bytes）
- SHA-256：`37C17FD91971C17E02E60798A05EEC48D881E1BB970D6309F58CF134A2D03A6B`
- 同じバージョンに **int4** ファイル（`…_3203313.safetensors`、約 12.5 GB）もあり、16 GB の GPU で使える可能性がありますが、**このパネルでは未検証**です。
- Turbo でない「Hybrid v2」も使えますが、**Not distilled · 20 steps** を選ぶ必要があり、速度は 2～3 倍遅くなります。

## ダウンロードが完全か確認する

ダウンロードの破損は、クラッシュのいちばん多い原因です。ファイルのあるフォルダーでコマンドプロンプトを開き、結果を上記の SHA-256 と
比べてください（大文字・小文字は区別しません）：

```bat
certutil -hashfile 10Eros_Max_h3_TURBO-hybrid_beta5_w4a8_14gb_optimized.safetensors SHA256
```

## パネルでの使い方

1. ファイルを上記の `diffusion_models\` に置きます。
2. パネル上部の **🧩 Model settings** を開き、**🔄 Rescan** を押します。それでも表示されない場合は `restart_webui.bat` を実行します。
3. **FL2VA diffusion model** メニュー（Text to Video / Keyframes / 3D Camera / Storyboard）または **Ref2VA diffusion model** メニュー
   （Reference / V2V / Lip-sync）で選びます。
4. サンプリングモード：**Built-in distill · 8 steps**。モデルを選ぶと自動で切り替わります。Turbo LoRA を重ねないでください。
5. 21 GB の DaSiWa は **✨ HD two-pass** と組み合わせられません（読み込むとアップスケーラーに使う VRAM が足りなくなるため）。864×480 か 960×544 で
   生成し、🔍 Upscale タブで解像度を上げてください。14 GB の 10Eros は、24 GB の GPU なら HD two-pass を使えます。

任意：無検閲の **Heretic** テキストエンコーダーは `download_extras.bat` の **6** 番です。言語モデルの拒否をなくすだけで、何を描けるかは上記の拡散モデル次第です。

## LoRA

Ref2VA 用の LoRA、たとえば [SexGod1979/AfterMidnight-MiniMax-H3-NSFW](https://huggingface.co/SexGod1979/AfterMidnight-MiniMax-H3-NSFW)
（Apache-2.0、各 1.19 GB のファイル 2 つ：`…_sexytime_rank64-v1.2` は動き重視で強度 1.0、`…_softer_rank64_v1` はディテール重視で 0.8～1.0）：

1. `ComfyUI\models\loras\NSFW\` のようなサブフォルダーに置きます。
2. **🧩 Model settings** で **🔄 Rescan** を押し、**🧷 Ref2VA LoRA** でファイルを選んで **LoRA strength** を調整します。
3. Ref2VA のタブ（Reference、V2V、Lip-sync、参照画像付きの Storyboard）にだけ適用されます。AfterMidnight の作者は **beta** スケジューラーを
   指定しており、そうしないと音声が崩れます。パネルは自動で beta に切り替えます。

FL2VA 用の LoRA（Text to Video、Keyframes）も、同じように **🧷 FL2VA LoRA** メニューで選びます。ファイル名に `ref2v` を含む LoRA は Ref2VA メニューにだけ、
`fl2v` を含むものは FL2VA メニューにだけ表示されます。

## 利用ルール

- **架空の成人キャラクター、または描かれることに同意した成人だけを使ってください。**
- 実在の人物の性的・裸体・事実と異なる映像を、同意なく作ることは**禁止**です。有名人、知り合い、ネット上の写真はいずれも不可です。多くの国で違法です。
- 未成年者、または未成年に見えるキャラクターに関わる内容は**一切禁止**です。
- プラットフォームが認めており、描かれた全員が同意している場合を除き、公開しないでください。お住まいの地域の法律と、各モデルのライセンス
  （MiniMax H3 Community License、DaSiWa は Civitai の規約）を守ってください。

## 謝辞

- **TenStrip** — [10Eros-Max](https://huggingface.co/TenStrip/10Eros-Max) · GGUF 版：**Abiray** — [10Eros-Max-GGUF](https://huggingface.co/Abiray/10Eros-Max-GGUF)
- **DaSiWa** — [DaSiWa MiniMax H3（Civitai）](https://civitai.com/models/2877206/dasiwa-minimax-h3)
- **SexGod1979** — [AfterMidnight-MiniMax-H3-NSFW](https://huggingface.co/SexGod1979/AfterMidnight-MiniMax-H3-NSFW)
- **sakamakismile** — [Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4](https://huggingface.co/sakamakismile/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4)
- いずれも MiniMax の **MiniMax H3** をもとにしています — [MiniMaxAI/MiniMax-H3](https://huggingface.co/MiniMaxAI/MiniMax-H3)
