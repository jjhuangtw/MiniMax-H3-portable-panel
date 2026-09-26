# 🔞 NSFW community models / 成人向社群模型（自行下載）

> **18+ only.** These are third-party community fine-tunes of MiniMax H3. The panel's installers **do not**
> download them (they are 14–21 GB each) and this repo does not contain or distribute them. Download them
> yourself, read each author's licence, and follow the rules at the bottom of this page.
>
> **僅限 18 歲以上。** 以下是社群作者以 MiniMax H3 微調的第三方模型，每個 14～21 GB。面板的安裝程式**不會**下載它們，
> 本 repo 也不包含、不散布。請自行下載、閱讀作者授權，並遵守本頁最下方的使用規範。

## Which one? / 選哪一個

| Model 模型 | File size 檔案大小 | VRAM 顯存 | Menus 可用選單 |
| --- | --- | --- | --- |
| **10Eros-Max** beta5 Turbo hybrid w4a8 | 14.0 GB | 24 GB+ (tested on RTX 4090) | FL2VA + Ref2VA |
| **DaSiWa MiniMax H3** Hybrid Turbo v2 INT8 | 21.0 GB | 24 GB+ (tested on RTX 4090) | FL2VA + Ref2VA |

Both are **hybrids** (one file works in both model menus) with **Turbo distillation built in** — they run at
8 steps with no Turbo LoRA. Pick one; you don't need both.
兩個都是**混合模型**（一個檔案同時出現在 FL2VA 與 Ref2VA 兩個選單），且**已內建 Turbo 蒸餾**，8 步、不需 Turbo LoRA。擇一即可。

12–16 GB cards: there are smaller builds, but **none has been tested with this panel** —
DaSiWa's int4 file (below, 12.5 GB) and community GGUF builds of 10Eros-Max
([Abiray/10Eros-Max-GGUF](https://huggingface.co/Abiray/10Eros-Max-GGUF), Q3_K_M 8.9 GB · Q4_K_M 11.6 GB).
The GGUFs come from an **earlier test build (Test4)**; follow the sampling settings on their model page.
12～16 GB 顯卡：有較小的版本，但**本面板都未實測**：DaSiWa 的 int4 檔（12.5 GB，見下方），以及社群的 10Eros-Max GGUF 版（上方連結，Q4_K_M 11.6 GB）。GGUF 版來自較早的 **Test4 測試版**，採樣設定請依該模型頁說明。

## Where to put the file / 放在哪裡

Both files go in the **same folder**, next to the official H3 models:
兩個檔案都放進**同一個資料夾**（與官方 H3 模型放一起）：

```
<your install folder>\ComfyUI\models\diffusion_models\
```

- Installed with `setup.bat`: `<folder where setup.bat is>\ComfyUI_windows_portable\ComfyUI\models\diffusion_models\`
  用 `setup.bat` 安裝：`setup.bat 所在資料夾\ComfyUI_windows_portable\ComfyUI\models\diffusion_models\`
- Installed by hand: the folder next to `run_webui.bat` → `ComfyUI\models\diffusion_models\`
  手動安裝：`run_webui.bat` 旁邊的 `ComfyUI\models\diffusion_models\`

**Keep the downloaded filename.** The panel reads the name: `Turbo` in the filename switches the sampling mode
to 「模型內建蒸餾・8 步」 automatically, and `10Eros` / `Dasiwa` gives it a clear label in the menu. If you rename it,
keep those words.
**保留下載時的檔名**。面板靠檔名判斷：檔名有 `Turbo` 會自動切到「模型內建蒸餾・8 步」，有 `10Eros`／`Dasiwa` 會在選單顯示標籤。要改名的話請保留這些字。

## 1. 10Eros-Max (TenStrip)

- Page 模型頁：https://huggingface.co/TenStrip/10Eros-Max (marked *Not-For-All-Audiences*; licence: MiniMax H3 Community License)
- File 檔案：`10Eros_Max_h3_TURBO-hybrid_beta5_w4a8_14gb_optimized.safetensors` (13,997,668,774 bytes)
- Direct link 直接下載：
  https://huggingface.co/TenStrip/10Eros-Max/resolve/8a198588c8870ab0d613b3492a3150d091c8c2dd/10Eros_Max_h3_TURBO-hybrid_beta5_w4a8_14gb_optimized.safetensors
- SHA-256：`a8067999c65594b462d581c02b8a0573dd42d9812a14c586150a947c13388f2e`
- Use **beta5**. The author notes beta3 / beta4 are broken test uploads. 請用 **beta5**；作者說明 beta3／beta4 是壞掉的測試檔。

## 2. DaSiWa MiniMax H3 (Civitai)

- Page 模型頁：https://civitai.com/models/2877206/dasiwa-minimax-h3
- On the page choose the **DaSiWa Hybrid Turbo v2** version and download the file marked **int8** (about
  20.5 GB). Civitai needs a free account with mature content enabled to show this page; do that yourself.
  在模型頁選 **DaSiWa Hybrid Turbo v2** 版本，下載標示 **int8** 的檔案（約 20.5 GB）。Civitai 需登入並開啟成人內容顯示才看得到，請自行設定。
- File 檔案：`DasiwaMinimaxH3_dasiwaHybridTurboV2_3203135.safetensors` (20,967,669,168 bytes)
- SHA-256：`37C17FD91971C17E02E60798A05EEC48D881E1BB970D6309F58CF134A2D03A6B`
- The same version also has an **int4** file (`…_3203313.safetensors`, about 12.5 GB) that may suit 16 GB
  cards; it has **not been tested with this panel**. 同一版本另有 **int4** 檔（約 12.5 GB），16 GB 卡或許可用，但**本面板未實測**。
- The non-Turbo "Hybrid v2" also works but needs 「非蒸餾・20 步」 and is about 2–3× slower. 非 Turbo 的 Hybrid v2 也能用，但要選「非蒸餾・20 步」，慢 2～3 倍。

## Check the download / 檢查下載是否完整

A broken download is the most common cause of a crash. In the folder, open a command prompt and compare the
result with the SHA-256 above (upper/lower case doesn't matter):
下載不完整是最常見的當機原因。在該資料夾開啟命令提示字元，比對結果與上方 SHA-256（大小寫不影響）：

```bat
certutil -hashfile 10Eros_Max_h3_TURBO-hybrid_beta5_w4a8_14gb_optimized.safetensors SHA256
```

## Use it in the panel / 在面板中使用

1. Put the file in `diffusion_models\` (above). 把檔案放進上面的 `diffusion_models\`。
2. In the panel open **🧩 模型設定** at the top and press **🔄 重新掃描**. If it still doesn't appear, run `restart_webui.bat`.
   打開面板上方 **🧩 模型設定**，按 **🔄 重新掃描**；還是沒出現就執行 `restart_webui.bat`。
3. Pick it in the **FL2VA** menu (text-to-video, keyframes, 3D camera, storyboard) and/or the **Ref2VA** menu
   (reference, V2V, lip-sync). 在 **FL2VA**（文生／首尾幀／3D 攝影機／編劇）或 **Ref2VA**（參考影音／V2V／對嘴）選單選它。
4. Sampling mode 採樣模式：**模型內建蒸餾・8 步** (set automatically; never stack the Turbo LoRA on it 會自動切換，不要再疊 Turbo LoRA).
5. HD two-pass (✨ 高清二次採樣) is refused with the 21 GB DaSiWa file — it leaves too little VRAM for the
   upscaler. Generate at 864×480 or 960×544 and upscale in the 🔍 tab. The 14 GB 10Eros file can use HD two-pass on 24 GB cards.
   21 GB 的 DaSiWa 不能搭配高清二次採樣（顯存不夠放大模型），請用 864×480 或 960×544 生成，再用「🔍 放大」分頁升解析度；14 GB 的 10Eros 在 24 GB 卡上可以用高清二次採樣。

Optional: the uncensored **Heretic** text encoder is option **6** in `download_extras.bat`. It only removes the
language model's refusals; what H3 can draw depends on the diffusion model above.
選用：無審查的 **Heretic** 文字編碼器在 `download_extras.bat` 的選項 **6**。它只拿掉語言模型的拒答，畫得出什麼取決於上面的擴散模型。

**LoRAs:** the panel has no LoRA menu for the H3 video tabs. Ref2VA LoRAs such as
[SexGod1979/AfterMidnight-MiniMax-H3-NSFW](https://huggingface.co/SexGod1979/AfterMidnight-MiniMax-H3-NSFW)
(Apache-2.0, goes in `ComfyUI\models\loras\`) can only be used in your own workflows in ComfyUI itself
(http://127.0.0.1:8188). The author requires the euler sampler with the **beta** scheduler, or the audio breaks.
**LoRA**：面板的影音分頁沒有 LoRA 選單。上面這類 Ref2VA LoRA（放 `ComfyUI\models\loras\`）只能在 ComfyUI 本體（http://127.0.0.1:8188）自己的工作流使用；作者要求 euler + **beta** 排程，否則音訊會壞。

## Rules / 使用規範

- **Adults only, fictional or consenting.** Only fictional adult characters, or real adults who have given
  consent to be depicted. 只用虛構的成年角色，或已同意被描繪的成年人。
- **Never** make sexual, nude or fabricated imagery of a real person without consent — no celebrities, no
  people you know, no photos taken from the internet. This is illegal in many countries.
  **禁止**未經同意用真人製作性感、裸露或不實影像（名人、認識的人、網路照片都不行），許多國家屬違法。
- **Never** anything involving minors, or characters that look like minors. **禁止**任何涉及未成年人或外貌像未成年人的內容。
- Keep it private unless the platform allows it and everyone depicted agreed. Follow your local law and each
  model's licence (MiniMax H3 Community License; Civitai terms for DaSiWa).
  除非平台允許且當事人同意，否則不要公開分享。請遵守當地法律與各模型授權。

## Thanks / 致謝

- **TenStrip** — [10Eros-Max](https://huggingface.co/TenStrip/10Eros-Max) · GGUF builds by **Abiray** — [10Eros-Max-GGUF](https://huggingface.co/Abiray/10Eros-Max-GGUF)
- **DaSiWa** — [DaSiWa MiniMax H3 on Civitai](https://civitai.com/models/2877206/dasiwa-minimax-h3)
- **SexGod1979** — [AfterMidnight-MiniMax-H3-NSFW](https://huggingface.co/SexGod1979/AfterMidnight-MiniMax-H3-NSFW)
- **sakamakismile** — [Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4](https://huggingface.co/sakamakismile/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4)
- All built on **MiniMax H3** by MiniMax — [MiniMaxAI/MiniMax-H3](https://huggingface.co/MiniMaxAI/MiniMax-H3)
