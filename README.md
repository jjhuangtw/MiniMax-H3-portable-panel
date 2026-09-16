# MiniMax H3 影音創作面板（Portable 版）

在本機 RTX 4090（24 GB）上跑 [MiniMax H3](https://huggingface.co/MiniMaxAI/MiniMax-H3) 開源影音生成的 Gradio 面板，
後端是 ComfyUI，全程本機推論、不使用雲端 API。

功能分頁：文生影音、FL2VA 首尾幀、Ref2VA 萬用參考、分段長片、SeedVR2 影片放大、
Krea2 圖片生成、3D 攝影機、AI 編劇、生成紀錄。

> 這個 repo 只包含面板**程式碼與下載腳本**。模型權重不在其中，安裝時由腳本從官方來源下載並核對 SHA-256。

## 需要準備

1. **NVIDIA 顯卡**，建議 24 GB VRAM（RTX 4090 等）。較小的卡可用，需降低解析度、片長與批次。
2. **ComfyUI Portable（Windows）**：從 [ComfyUI releases](https://github.com/comfyanonymous/ComfyUI/releases)
   下載 `ComfyUI_windows_portable`，解壓後會有 `python_embeded\` 與 `ComfyUI\` 兩個資料夾。
3. **git**、**約 200 GB 可用磁碟**（核心約 35 GB，加上各項可選模型）。

## 安裝

1. 把本 repo 的檔案放進 ComfyUI portable 的根目錄（和 `python_embeded\`、`ComfyUI\` 並排）。
2. 雙擊 **`install.bat`**。它會：
   - 裝 Python 套件（gradio、websocket-client、zhconv 等）
   - clone 需要的 ComfyUI custom node（固定版本）
   - 下載核心 H3 模型（Q4 擴散模型、文字編碼器、視訊／音訊 VAE、兩個 Turbo LoRA），逐一核對 SHA-256
3. 完成後雙擊 **`run_webui.bat`**，瀏覽器開 http://127.0.0.1:7860 。

可選模型自行執行對應腳本：`download_heretic_encoder.py`、`download_hd_models.py`、
`download_seedvr2.py`、`download_krea2_style_loras.py`。

面板操作與各分頁細節見 [RTX4090_LOCAL.md](RTX4090_LOCAL.md)。

## 常用批次檔

| 檔案 | 作用 |
| --- | --- |
| `run_webui.bat` | 啟動或開啟面板 |
| `restart_webui.bat` | 重啟面板與後端（有任務執行中會拒絕） |
| `cancel_generation.bat` | 取消目前與排隊中的生成 |
| `free_vram.bat` | 卸載模型、釋放顯存 |

## 授權與使用須知

- 面板程式碼：見 `LICENSE`。
- **模型各有授權**，安裝前請自行閱讀：MiniMax H3 採 MiniMax H3 Community License（其適用地區不含歐盟、英國、韓國、美國）；
  其他 custom node 多為 GPL-3.0 或 Apache-2.0。本 repo 不含也不散布任何模型權重。
- 這是本機開源、未加內容過濾的工具。請只用於合法用途：**不要以真人肖像製作性感、裸露或不實影像**；
  成人內容只使用虛構角色或取得本人同意的素材。散布或製作未經同意的他人不實影像在許多地區違法。
- custom node 與模型皆來自第三方，其正確性、安全性與維護狀態由各專案負責。

## 致謝

MiniMax H3（MiniMaxAI）、Comfy-Org、ComfyUI、以及 TimelineDirector、H3 Latent Upscaler、
SeedVR2、3D Camera Control、H3 Edit 等 custom node 作者。
