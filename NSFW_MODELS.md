# 🔞 成人向社群模型（自行下載）

**繁體中文** | [English](NSFW_MODELS.en.md) | [简体中文](NSFW_MODELS.zh-CN.md) | [日本語](NSFW_MODELS.ja.md)

> **僅限 18 歲以上。** 以下是社群作者以 MiniMax H3 微調的第三方模型，每個約 21～23 GB。面板的安裝程式**不會**下載它們，
> 本 repo 也不包含、不散布。請自行下載、閱讀作者授權，並遵守本頁最下方的使用規範。

## 選哪一個

| 模型 | 檔案大小 | 顯存 | 可用選單 |
| --- | --- | --- | --- |
| **10Eros-Max** beta7 8-step Turbo int8HQ | 22.9 GB | 24 GB 以上（RTX 4090 實測） | FL2VA ＋ Ref2VA |
| **DaSiWa MiniMax H3** Hybrid v4 Turbo int8 | 21.0 GB | 24 GB 以上（RTX 4090 實測） | FL2VA ＋ Ref2VA |

兩個都是**混合模型**（一個檔案同時出現在 FL2VA 與 Ref2VA 兩個選單），而且**已內建 Turbo 蒸餾**，不需要 Turbo LoRA：
10Eros beta7 用 8 步，DaSiWa v4 Turbo 用 4 步（較快）。4090 實測 864×480／4 秒：DaSiWa v4 Turbo 約 29 秒、10Eros beta7 約 54 秒。擇一即可，不必兩個都裝。

12～16 GB 顯卡：有較小的版本，但**本面板都未實測**：DaSiWa 的 int4 檔（12.5／16.8 GB，見下方），以及社群的 10Eros-Max GGUF 版
（[Abiray/10Eros-Max-GGUF](https://huggingface.co/Abiray/10Eros-Max-GGUF)，Q3_K_M 8.9 GB · Q4_K_M 11.6 GB）。
GGUF 版來自較早的 **Test4 測試版**，採樣設定請依該模型頁說明。

## 放在哪裡

兩個檔案都放進**同一個資料夾**，和官方 H3 模型放一起：

```
<安裝資料夾>\ComfyUI\models\diffusion_models\
```

- 用 `setup.bat` 安裝：`setup.bat 所在資料夾\ComfyUI_windows_portable\ComfyUI\models\diffusion_models\`
- 手動安裝：`run_webui.bat` 旁邊的 `ComfyUI\models\diffusion_models\`

**保留檔名裡的關鍵字。** 面板靠檔名判斷：檔名有 `Turbo` 會自動切到「模型內建蒸餾」，同時有 `v4Turbo`／`4turbo`／`4step` 時用 4 步、否則 8 步；
有 `10Eros`／`Dasiwa` 會在選單顯示標籤。要改名的話請保留這些字（例如 `DasiwaMinimaxH3_dasiwaHybridV4Turbo_int8.safetensors` 可以）。

## 1. 10Eros-Max（TenStrip）

- 模型頁：https://huggingface.co/TenStrip/10Eros-Max（標示為 *Not-For-All-Audiences*；授權：MiniMax H3 Community License）
- 檔案：`10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors`（22,893,150,024 bytes）
- 直接下載：
  https://huggingface.co/TenStrip/10Eros-Max/resolve/682e73d12dcaf766dd31b4bb2991084119c2df8c/10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors
- SHA-256：`8a51ca3f7d290a799d89fefcde4ede60962256955a91dfe4746d3cc07814fd6e`
- 同一頁的其他檔**不用下載**：`…_8stepTURBO_beta7.safetensors`（40 GB 未壓縮原檔，24 GB 卡放不下）、`…_raw_beta7_int8`（非 Turbo，要 20 步）。
  作者建議 beta5 或 beta7，避免 beta6。
- 作者提到單次採樣時背景偶爾會閃爍；本機 4 秒測試沒有出現。

## 2. DaSiWa MiniMax H3（Civitai）

- 模型頁：https://civitai.com/models/2877206/dasiwa-minimax-h3
- 版本頁：https://civitai.com/models/2877206?modelVersionId=3392061（**DaSiWa Hybrid v4 Turbo**，4 步）
- 下載標示 **int8** 的檔案（約 21 GB）。Civitai 要登入免費帳號並開啟成人內容顯示才看得到，請自行設定。
- 檔案：`DasiwaMinimaxH3_dasiwaHybridV4Turbo_3281858.safetensors`（20,967,668,616 bytes；改名成 `DasiwaMinimaxH3_dasiwaHybridV4Turbo_int8.safetensors` 也可以）
- SHA-256：`36471AFB817747B711B9ABAD3D8E6B7C88A7C2B91B4887D040A8DCB7EE82B2D6`
- 同一版本另有兩個 **int4** 檔（約 12.5 GB 與 16.8 GB），16 GB 卡或許可用，但**本面板未實測**。
- 非 Turbo 的「Hybrid v4」也能用，但要選「非蒸餾・20 步」，速度慢很多。

## 檢查下載是否完整

下載不完整是最常見的當機原因。在檔案所在的資料夾開啟命令提示字元，把結果和上方的 SHA-256 比對（大小寫不影響）：

```bat
certutil -hashfile 10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors SHA256
```

## 在面板中使用

1. 把檔案放進上面的 `diffusion_models\`。
2. 打開面板上方的 **🧩 模型設定**，按 **🔄 重新掃描**。還是沒出現就執行 `restart_webui.bat`。
3. 在 **FL2VA 擴散模型**（文生／首尾幀／3D 攝影機／編劇）或 **Ref2VA 擴散模型**（參考影音／V2V／對嘴）選單選它。
4. 採樣模式：10Eros beta7 用 **模型內建蒸餾・8 步**，DaSiWa v4 Turbo 用 **模型內建蒸餾・4 步**。選模型時會自動切換，不要再疊 Turbo LoRA。
5. 兩個都超過 20 GB，不能搭配 **✨ 高清二次採樣**（載入後顯存不夠放大模型用），請用 864×480 或 960×544 生成，再到「🔍 放大」分頁升解析度。

選用：無審查的 **Heretic** 文字編碼器在 `download_extras.bat` 的選項 **6**。它只拿掉語言模型的拒答，畫得出什麼取決於上面的擴散模型。

## LoRA

Ref2VA 用的 LoRA，例如 [SexGod1979/AfterMidnight-MiniMax-H3-NSFW](https://huggingface.co/SexGod1979/AfterMidnight-MiniMax-H3-NSFW)
（Apache-2.0，兩個各 1.19 GB 的檔案：`…_sexytime_rank64-v1.2` 偏動作，建議強度 1.0；`…_softer_rank64_v1` 偏細節，建議 0.8～1.0）：

1. 放進 `ComfyUI\models\loras\NSFW\` 這類子資料夾。
2. 在 **🧩 模型設定** 按 **🔄 重新掃描**，在 **🧷 Ref2VA LoRA** 選它，並調整 **LoRA 強度**。
3. 只作用在 Ref2VA 分頁（參考影音、V2V、對嘴、附參考圖的編劇）。AfterMidnight 作者要求 **beta** 排程，否則音訊會壞；面板會自動改用 beta。

FL2VA 用的 LoRA（文生、首尾幀）在 **🧷 FL2VA LoRA** 選單用同樣方式選用。檔名含 `ref2v` 的只出現在 Ref2VA 選單，含 `fl2v` 的只出現在 FL2VA 選單。

## 使用規範

- **只用虛構的成年角色，或已同意被描繪的成年人。**
- **禁止**未經同意用真人製作性感、裸露或不實影像：名人、認識的人、網路上的照片都不行。這在許多國家屬於違法。
- **禁止**任何涉及未成年人，或外貌像未成年人的內容。
- 除非平台允許且當事人都同意，否則不要公開分享。請遵守當地法律與各模型授權（MiniMax H3 Community License；DaSiWa 依 Civitai 條款）。

## 致謝

- **TenStrip** — [10Eros-Max](https://huggingface.co/TenStrip/10Eros-Max) · GGUF 版：**Abiray** — [10Eros-Max-GGUF](https://huggingface.co/Abiray/10Eros-Max-GGUF)
- **DaSiWa** — [DaSiWa MiniMax H3（Civitai）](https://civitai.com/models/2877206/dasiwa-minimax-h3)
- **SexGod1979** — [AfterMidnight-MiniMax-H3-NSFW](https://huggingface.co/SexGod1979/AfterMidnight-MiniMax-H3-NSFW)
- **sakamakismile** — [Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4](https://huggingface.co/sakamakismile/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4)
- 以上都建立在 MiniMax 的 **MiniMax H3** 之上 — [MiniMaxAI/MiniMax-H3](https://huggingface.co/MiniMaxAI/MiniMax-H3)
