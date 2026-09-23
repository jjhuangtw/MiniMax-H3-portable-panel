# 本機影片方案（RTX 4090 實測，12～32 GB 顯存皆可用）

啟動：雙擊 `run_webui.bat`，開啟 http://127.0.0.1:7860 。影片推論在本機執行，不使用雲端 API。

## ComfyUI 版本

本面板在 **ComfyUI v0.36.0** 上實測通過（FL2VA／Ref2VA 路徑皆正常）。升級到 v0.36.0 時，除了 `requirements.txt` 顯眼處列的套件，還要一併升級 **`comfy-aimdo` 到 0.5.3**（`pip install "comfy-aimdo==0.5.3"`）——它是 v0.36.0 新記憶體圖編譯器的原生相依，若停在 0.5.2，每次生成會在收尾階段丟 `'MallocGraph' object has no attribute 'rogue_count'` 而失敗。連同要對齊的還有 `comfyui-frontend-package==1.52.7`、`comfyui-workflow-templates==0.11.62`、`comfy-kitchen==0.2.34`。升級後重啟後端才會生效。

## H3 快速生成

- 模型庫：本 Portable 目錄的 `ComfyUI/models`，不依賴固定磁碟代號。FL2VA 與 Ref2VA 使用 Pruned Q4_K_M GGUF；文字編碼器預設 Heretic 無審查 NVFP4（可切回原版 AWQ），VAE 與 LoRA 使用既有檔案。原 INT8 權重仍保留。
- 「FL2VA 首尾幀影音」：上傳首幀／尾幀並描述動作與聲音；也可只用首幀。文生影音也使用 FL2VA。
- 「Ref2VA 萬用參考」：最多 9 張參考圖、3 支參考影片（可選是否帶原音軌）、3 個音檔，詳見下方「Ref2VA 萬用參考」。
- 兩份 Q4 模型各為 11,420,663,904 bytes。來源：`leejet/MiniMax-H3-GGUF`，版本 `d9c4c6312b4728a68a15a35626d84775a6523783`。`download_q4_models.py` 可續傳並核對 SHA-256；檔案大小不等於生成時的總顯存用量。
- 文生／圖生：勾選 Turbo，使用 FL2VA 8-step v1.0 LoRA，以作者支援的 4 步模式推論；關閉 Turbo 為 20 步。
- 初次試片：864×480、4～5 秒。降低步數可能影響細節與動作品質。
- 顯存採動態管理，保留參數**開機時依偵測到的 GPU 顯存自動調整**（`detect_gpu()` 用 nvidia-smi）：≥22GB 用 `--reserve-vram 2.5 --vram-headroom 3`；14–22GB 用 `1 / 1`；<14GB 用 `0.5 / 0`。偵測失敗時取保守的 `1 / 1`（但不關閉任何功能）。這些不是硬性上限，也不是把兩個參數相加當固定保留量。
- **顯存 < 22 GB 時面板自動調整**：關閉「高清二次採樣」與 Full HD 選項（執行時也會擋下並說明）、SeedVR2 預設「每批 5 幀」並把 8 個（<14GB 為 16 個）區塊轉到 CPU；選到比顯存還大的模型（INT8／DaSiwa 約 21 GB）或超過 960×544 的解析度時跳警告建議改用 Q4 與 864×480。目前的偵測結果與對照表在「ℹ️ 系統」分頁。
- 偵測錯誤或想強制較小的設定：在命令提示字元先 `set H3_VRAM_GB=16` 再執行 `run_webui.bat`。
- 12～16 GB 卡要高解析度：先 864×480 生成，再到「🔍 放大」用 SeedVR2 升到 1080p。系統 RAM 建議 64 GB（模型會部分卸載到 RAM）。
- 預設片長 4 秒；不使用 `--highvram` 強制常駐，也不加在動態顯存模式下無效的 `--lowvram`。仍可能需要 CPU 卸載，不能保證不使用共享記憶體；增加餘裕也可能降低速度。
- 單張 4090 不等於 fal H3 Max 雲端速度；首次讀取大型模型也會增加等待時間。
- 不同大型模型不要同時生成。先做短片確認，再提高解析度或片長。

## 文字編碼器與 LoRA

面板頂端「🧩 模型設定」對所有分頁生效。

- Heretic 無審查編碼器：`qwen3vl_32b_heretic_minimax_h3_nvfp4.safetensors`（15,683,129,587 bytes），放在 `ComfyUI/models/text_encoders`。來源：`sakamakismile/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4`，版本 `2814607c9e6034e2cf2c76da82f996d179567551`。`download_heretic_encoder.py` 可續傳並核對 SHA-256。
- 面板預設使用 Heretic 版；該檔案不存在時自動退回原版 NVFP4 AWQ。
- 它移除的是 Qwen3-VL 聊天拒答；H3 只取提示詞隱藏狀態，畫面通常只有細微差異。H3 能否畫出某類內容主要取決於擴散模型的訓練資料，這部分要靠 LoRA。
- 擴散模型可在「模型設定」挑選：FL2VA 一個選單（文生／首尾幀／3D 攝影機／編劇），Ref2VA 一個選單（參考影音／V2V／對嘴）。清單同時列出 `.gguf` 與 `.safetensors`，載入器依副檔名自動選 `UnetLoaderGGUF` 或 `UNETLoader`。預設仍是兩個 Q4_K_M GGUF；目錄內的 pruned INT8 convrot（各 20,970,379,616 bytes）可直接選用，畫質較好但較慢、顯存吃更多。
- `DasiwaMinimaxH3_dasiwaHybridTurboV2_int8.safetensors`（20,967,669,168 bytes）：Civitai「⛩️💀 DaSiWa MiniMax H3 💀⛩️」DaSiWa Hybrid **Turbo** v2，SHA-256 `37C17FD9…A2D03A6B` 與官方一致（由 civitai.red 鏡像取得，雜湊比對確認為同一檔）。混合模型，REF2VA 與 FL2VA 兩條路徑皆可用；本機以「模型內建蒸餾・8 步」實測 864×480／4 秒約 83 秒。
- 非蒸餾的 DaSiWa Hybrid v2（20,967,669,160 bytes，SHA-256 `4CB8E1EA…56D25F8`）已移出模型目錄，現放在 `_unused_models/`，可自行刪除以釋放 21 GB。其 `final_layer.video_out` 與 ref2va 距離 0.0077、與 fl2va 0.0428，基底主幹為 Ref2VA，但兩條路徑同樣都實測可用（FL2VA 20 步約 160 秒、Ref2VA 20 步約 245 秒）。
- **採樣模式**（各分頁的下拉選單，取代原本的 Turbo 勾選）：
  - `Turbo LoRA・4 步`：官方 Q4／INT8 模型用，套用 Turbo LoRA、CFG 1。
  - `模型內建蒸餾・8 步`：DaSiWa Turbo 這類已蒸餾的權重用，**不套 Turbo LoRA**、CFG 1。兩種蒸餾不可疊加。
  - `非蒸餾・20 步`：CFG 2.5，DaSiWa 非蒸餾版與原始權重用。
- 額外 LoRA 以 `LoraLoaderModelOnly` 疊在 Turbo LoRA 之後（節點 9），強度 -2～2。FL2VA 與 Ref2VA 是不同模型，LoRA 要選對應版本。新放入的檔案若後端找不到，執行 `restart_webui.bat`。

## INT8 視訊 VAE（省顯存）

- `minimax_h3_video_vae_int8_convrot.safetensors`（2,811,065,184 bytes）放進 `ComfyUI/models/vae`，面板會**自動優先使用**它取代原版 FP16（5.2 GB）；檔案不存在時自動退回 FP16。
- 來源：`Comfy-Org/MiniMax-H3`（版本 `7e75982b97cd5a41d2dcfa1904ee88d0686d6fd1`），SHA-256 `52a2c8c7…c8e60c0e`。`download_int8_vae.py` 可續傳並核對。
- Kijai 實測（RTX 5070 12GB、15 秒片）：VAE 顯存從 4,965 MB 降到 2,677 MB（約 −46%），並略快。24GB 卡不缺這點，但高解析度時多出的餘裕仍有幫助。音訊 VAE 不變。

## Ref2VA 萬用參考

- 參考素材以 ComfyUI Autogrow 名稱傳入核心節點：`ref_images.ref_image_0`、`ref_videos.ref_video_0`、`ref_video_audios.ref_video_audio_0`、`ref_audios.ref_audio_0`（0 起算）。2026-09-15 以前的面板寫成 `ref_video_1`／`ref_image_1`，後端會默默忽略，參考素材實際沒有生效；影片也未經 `GetVideoComponents` 拆出影格與音軌。
- 標籤順序與核心節點一致：先 `<Picture N>`；每支影片若帶原音軌，該音軌的 `<Audio N>` 排在它的 `<Video N>` 之前；最後才是獨立音檔。面板會即時顯示對照表。
- 參考影片上傳前以 ffmpeg 轉為 24 fps、最長 362 幀（約 15.08 秒）、短邊不超過 720。H3 按 24 fps 讀取參考影格。
- 第一個音檔選「整條照用並對嘴」：片長依音檔長度吸附到 17n+5 幀（上限 362）；音訊以 TimelineDirector 的 `MiniMaxH3LockAudioLatent` 鎖入 AV 潛空間（音訊不去噪），成片再用 ffmpeg 換回原始音檔，另存 `*_原音.mp4`。
- 解析度可選「自動・依素材比例」：依第一支參考影片，沒有影片時依 `<Picture 1>` 的比例，吸附 32 px。FL2VA 分頁的自動選項依首幀（或尾幀）。

## 結構化提示詞

「文生影音」「FL2VA」「Ref2VA」分頁都有「🧱 結構化提示詞」，格式依 MiniMax 官方 h3-prompt-writing 指南（https://github.com/MiniMax-AI/MiniMax-H3/tree/main/.claude/skills/h3-prompt-writing ）：

- Base：`integrated_multimodal_description` / `overall_soundscape` / `non_diegetic_music`。
- Ref：`subject_definitions` / `summary` / `retention_analysis` / `detailed_description` / `overall_soundscape` / `non_diegetic_music`；保留標記畫面類為 `fully_preserved`、`partially_preserved`、`attribute_transfer`、`weak_reference`，音訊類為 `fully_copy`、`partially_copy`、`reference`、`weak_reference`。
- 台詞按鈕產生 `說話者 (S1) says: <d>[Chinese] …</d>`，中文可用 zhconv 轉簡體（`python_embeded/lib/site-packages/zhconv`，1.4.3，GPLv2+，SHA-256 `ad42d9057ca0605f8e41d62b67ca797f879f58193ee6840562c51459b2698c45`）。
- FL2VA 分頁預設在第一行加入官方對齊宣告：只有首幀時用 I2VA 句，首尾幀都有時用 FL2VA 句（尾幀秒數＝幀數／24，鏡頭編號取提示詞中最大的 `[Shot N]`），只有尾幀時用 L2VA 句；提示詞已有宣告時不重複。
- 「📚 提示詞範本庫」新增兩類「📖 官方指南」：MiniMax 官方 h3-prompt-writing skill 原文（三段格式 9 條、Ref 六段格式 8 條），當參考／範例用；`Case 1～4` 與 Ref 的 `Complete Example` 是完整官方格式範例，可直接套用。原文不隨 repo 散布（`.gitignore` 排除 `prompt_references/*.txt`），由 `download_prompt_guides.py` 自官方 repo（版本 `1ce88e916de7c15b63cbaf347642503f9bc21d3d`）下載並核對 SHA-256；檔案不存在時面板不顯示這兩類，不影響其他功能。

## 提示詞範本庫

各生成分頁（含「🎨 圖片」）都有「📚 提示詞範本庫」：左選分類、右選範本，或**直接點縮圖選用**，再按「套用・取代」或「加到末尾」。

- **分類**：建築（35）、人物（53）、美食料理／動物寵物／自然風景／產品・廣告／交通載具／運動健身／科幻奇幻（各 8）、🎯 官方格式範例（12，可直接生成）、🎬 分鏡導演（給語言模型的指令，非 H3 提示詞）、📖 官方指南 ×2、原有精選。
- **官方格式**：建築／人物／成年女性動畫這三類（共 60）已依 h3-prompt-writing skill 重寫為官方英文三段格式（`integrated_multimodal_description` `[Shot 1]` + 官方運鏡詞彙／`overall_soundscape`／`non_diegetic_music`），主題類與官方格式範例亦同。名稱保留、內容合規，套用後可直接生成。原始碼分別在 `prompt_official.py`（重寫版）、`prompt_themes.py`（主題類）。
- **縮圖**：每個畫面型範本一張縮圖，快取在 `prompt_thumbs/<sha1>.jpg`（隨 repo 提供）。縮圖用 Krea2 圖片模型 512×512、8 步快速生成，**僅供示意**（Krea2 與 H3 是不同模型，非實際成片）；生成前會用 `prompt_to_image_desc()` 去掉欄位標籤、`[Shot]`、運鏡句與台詞，只留純畫面描述。新增範本或想重生成時按「🖼️ 產生此分類縮圖」（勾「只補缺少的」跳過已有）。參考文字類（官方指南、分鏡導演）不做縮圖。

## Ref2VA NSFW LoRA 與採樣排程

- 「Ref2VA 萬用參考」分頁新增「採樣排程」選單（simple／beta／sgm_uniform／normal／karras），預設 simple。
- `SexGod1979/AfterMidnight-MiniMax-H3-NSFW`（版本 `4b325f60229c136b97501f5830bb277aace738b6`，Apache-2.0）的兩個 rank64 LoRA 已放入 `ComfyUI/models/loras`，`download_ref2va_loras.py` 可續傳並核對 SHA-256：
  - `AfterMidnight_ref2va_h3_sexytime_rank64-v1.2.safetensors`（1,192,828,320 bytes，動作取向，建議強度 1.0）
  - `AfterMidnight_ref2va_h3_softer_rank64_v1.safetensors`（1,192,828,168 bytes，細節取向，0.8–1.0）
- **只適用 Ref2VA**，文生與首尾幀分頁的 FL2VA 模型不適用。
- **作者要求 euler + beta 排程**，否則音訊會出現異常；面板的採樣器固定 euler，排程請自行改成 beta。
- 這兩個 LoRA 只包含 attention（qkv、out_proj）與 MLP 共 600 個張量，不含 adaln，因此可直接套用於 pruned Q4 GGUF；含 adaln 的 LoRA 在 pruned 模型上會有部分權重被靜默丟棄。

## 高清二次採樣

「文生影音」與「FL2VA 首尾幀影音」分頁勾選「✨ 高清二次採樣」後，輸出所選解析度：先以一半解析度跑 Turbo 4 步，拆出視訊潛空間，用 3D 潛空間放大模型放大 2 倍，再以完整解析度從 sigma 0.9035 補 3 步（排程取自放大模型作者的範例工作流）。會自動使用 Turbo；3D 攝影機與 Ref2VA 分頁不支援。

- 節點：https://github.com/LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler （版本 `d7c01b9011f2e8439493f6c02c29995a27df276f`）
- 模型：`ComfyUI/models/latent_upscale_models/minimax_h3_latent_upscaler_3d_fp16.safetensors`（690,592,672 bytes），來源 `LBH-123-AI/Minimax_h3_latent_Upscaler`，版本 `13ccf95d85d120bdbc92c05b1247a6e147bf54bf`；`download_hd_models.py` 可續傳並核對 SHA-256。
- 本機實測（4 秒、Turbo、模型已快取）：1280×704 約 135 秒；1920×1088 約 291 秒。兩者 GPU 記憶體用量都接近 24 GB（DynamicVRAM 會盡量用滿）。
- 超過官方 1344×768 面積的解析度（Full HD 選項）必須勾選高清二次採樣，否則會直接提示。

## 🖍️ 筆刷修圖（畫幾筆 → AI 生成新圖）

- 上傳圖片，用筆刷（綠／紅／藍／黃／紫／白／黑，可調粗細、有橡皮擦）在想改的地方畫幾筆，選「筆畫的用途」並寫一句要變成什麼（中文可），按生成。靈感來自 YouTube Shorts「Best Rendering AI Tool」的塗鴉改圖示範。
- 四種用途：✏️ 依筆畫加入新東西（照筆畫的位置、形狀、大小生成真實物件）、🔄 把塗到的地方換成別的、🧽 移除塗到的東西（可不寫字）、🎨 自由指示（筆畫只標位置）。有「常用範例」可點選填入。
- 做法：沿用「🖌️ 修圖」的 Qwen-Image-2.1 與其模型設定，把**原圖當 `<image1>`、畫了筆畫的圖當 `<image2>`**，提示詞要求依 `<image2>` 筆畫的位置修改 `<image1>`、其餘不變、結果不得留筆畫。實測只送畫了筆畫的單張圖時，新物件會偏離筆畫位置；兩張一起送則準確落在筆畫上。
- 沒畫筆畫就按生成會提示；結果可按「🔄 用結果繼續畫」接著改下一處，或套用到首尾幀／參考分頁。RTX 4090：1024 解析度、25 步每張約 17～20 秒（第一次載入模型較久）。

## 🌐 提示詞網站

- 最後一個分頁用框架嵌入 ArchiPrompt（https://archi-prompt.com/ ，建築・景觀・室內設計 AI 提示詞分享），挑好提示詞複製後貼回各分頁即可。網站沒有禁止嵌入的標頭，可直接顯示。
- 網站在隱藏的分頁裡載入會變成空白，所以第一次點開這個分頁時才載入，之後切換分頁不會重新整理。
- Google 不允許在框架內登入；要登入或分享提示詞時，按分頁上方的連結在新視窗開啟。
- 分頁多、視窗較窄時，最後幾個分頁（系統、提示詞網站）會收在分頁列右邊的「⋯」選單裡。

## 圖片生成（Krea-2 官方純淨 Turbo 版）

「🎨 圖片」分頁使用 Krea-2 官方蒸餾模型，架構不同於 H3（使用 Qwen3-VL 4B 文字編碼器與 Qwen VAE）。用途是產生高美學質感的圖片素材，再拿去當 H3 的參考圖或對嘴主圖。

- 模型：`Comfy-Org/Krea-2` 官方純淨版 `krea2_turbo_fp8_scaled.safetensors`（13.14 GB，8 步 Turbo 蒸餾加速）。
- 配套檔取自 `Comfy-Org/Krea-2`：`qwen3vl_4b_fp8_scaled.safetensors`（文字編碼器，CLIPLoader type 填 `krea2`）、`qwen_image_vae.safetensors`、`krea2_turbo_lora_rank_64_bf16.safetensors`。
- 純淨 8 步單階段工作流：採用 `KSampler`（`steps=8`, `cfg=1.0`, `sampler_name='er_sde'`, `scheduler='simple'`），出圖迅速且細節自然，完全淘汰舊版 RedCraft 雙權重與死黑雜點。
- **風格／原創角色 LoRA**：放在 `ComfyUI/models/loras/krea2/`，分頁內最多疊三個。
  - 觸發詞放在同名 `.trigger.txt`，生成時自動接到提示詞後面；風格 LoRA 沒有觸發詞通常不會生效。
  - 縮圖優先用同名 `.preview.png`／`.png`／`.jpg`／`.webp`；按「產生縮圖」會用固定的靜物場景（茶壺、檸檬、花瓶）加觸發詞，以 512×512、8 步快速畫出。
  - 已放入 `Comfy-Org/Krea-2` 官方九個風格 LoRA，觸發詞取自 ComfyUI 內建 Krea2 範本：darkbrush、dotmatrix、kidsdrawing、neondrip、rainywindow、retroanime、softwatercolor、sunsetblur、vintagetarot。

## ✨ AI 專業提示詞（本機自動寫提示詞）

- 文生、首尾幀、編劇、圖片分頁的提示詞欄上方都有「✨ AI 專業提示詞」：輸入一句想法（中文可），選風格，可附參考圖，按下後由本機模型寫成 MiniMax 官方格式並直接填入。靈感來自青橙Lab 的「MiniMax H3 专业自动提示词」教學（https://www.youtube.com/watch?v=Crp5GtXdqEA）；本面板用 ComfyUI v0.36 原生 `TextGenerate` 節點實作，不需額外節點。
- 各分頁的輸出：
  - 文生：三段官方格式；只附圖沒寫想法時，只讓圖中既有的東西動起來。
  - 首尾幀：看首幀（與尾幀）寫動作路徑，`[Shot 1]` 以 `<Picture 1>` 錨定；對齊宣告由面板自動加。
  - 編劇：`設定：` 一行加 N 行 `畫面｜運鏡｜聲音`，填入共同設定與故事欄。
  - 圖片：一段 Krea2 用的英文畫面描述。
- 模型：優先用修圖分頁的 `qwen3vl_8b_int8_convrot`（CLIPLoader type `qwen_image`），沒有時用圖片分頁的 `qwen3vl_4b_fp8_scaled`（type `krea2`）；兩者都沒有時 `download_extras.bat` 選 7 只下載 4B（約 5 GB）。H3 自己的 32B 編碼器被截成 50 層、沒有輸出頭，不能拿來寫字。
- 寫作規則濃縮自 MiniMax 官方 h3-prompt-writing 指南（`prompt_assistant.py`）；台詞保留原文並補上 `[Chinese]`／`[English]` 語言標籤。附圖先縮到約 0.4 MP 再給模型看。RTX 4090 實測（8B）：文生約 4 秒、編劇 5 鏡約 5 秒；用 AI 寫的文生提示詞實際生成 6 秒片 83 秒，畫面與台詞都正確。

## 編劇（故事 → 分鏡 → 自動剪接）

- 「📝 編劇」分頁有 15 個範本（`story_templates.py`）：🏛️ 建築（山林清水模住宅、都會玻璃帷幕大樓、紅磚三合院老屋新生）、🛋️ 室內設計（北歐原木客廳、日式侘寂茶室、輕奢飯店套房）、🌳 景觀（私人庭院四季花園、都會口袋公園、屋頂空中花園）、🏠 房仲銷售（新成屋三房帶看、預售屋接待中心、實景照片帶看）、🌸 東方女子（茶館旗袍泡茶、雨夜老街撐紙傘、晨光書房寫書法）。選範本按「套用範本」會同時填好共同設定、故事與分鏡表（有建議的圖片用途時也會一併選好），直接按 ② 生成。房仲範本的台詞用官方 `(S1)` + `<d>[Chinese] …</d>` 寫法。
- **附加圖片**（選填）三種用途：
  - 👤 人物參考：每個鏡頭改用 Ref2VA，圖片標為 `<Picture 1>`～`<Picture 3>`，提示詞自動加上「每鏡都是圖中同一人」的宣告，臉孔一致性最好。
  - 🏠 場景參考：同樣走 Ref2VA，宣告「畫面中的建築／空間與圖片一致」。
  - 🖼️ 逐鏡開場：第 N 張圖當第 N 鏡的首幀（FL2VA，自動加官方首幀對齊宣告）；圖比鏡頭少時，其餘鏡頭只用文字生成。適合房屋實景照片做帶看影片。
  - 所有鏡頭用同一個固定解析度，才能無損直接剪接。
- 故事每行一個鏡頭：`畫面內容｜運鏡｜聲音`；沒有 `｜` 時整段依句子拆鏡、用預設運鏡與聲音。
- 「全片共同設定」會加在每個鏡頭提示詞前面。每鏡是各自獨立的文生影音，服裝、髮型、場景會跟著設定一致，但臉孔仍可能每鏡略有差異；要同一人全片一致請在「附加圖片」上傳人像並選「人物參考」。
- 實測：茶館範本前 2 鏡 × 4 秒（864×480、Turbo）共 125 秒，剪接後 8.95 秒。

## SeedVR2

`download_extras.bat` 選 4 會下載 3B DiT（`seedvr2_ema_3b_fp16.safetensors`）與 EMA VAE（`ema_vae_fp16.safetensors`），來源 `numz/SeedVR2_comfyUI` 版本 `09ced71`，皆核對 SHA-256。節點的 Python 相依由 `install.bat`（`download_nodes.py`）安裝。`.part` 是下載暫存檔，不代表可用模型。
SeedVR2 用於既有影片提升畫質，不是文生影片加速器。

## 3D 攝影機

生成結束後執行 `restart_webui.bat`，會一併重啟本 Portable 的面板與後端；有執行中／排隊中的任務時拒絕重啟。

在「3D 攝影機」分頁上傳參考圖片，拖曳紫色攝影機或輸入角度、仰角與距離，設定 2–24 個關鍵幀。片長可選約 5.17／10.13／15.08 秒；時間軸顯示最後一幀時刻，會比檔案總長少 1/24 秒。按 ▶ 預覽軌跡，再按「按 3D 軌跡生成影音」。此分頁使用 FL2VA Q4 的固定場景模式，H3 Edit 的提示詞與 options 一起接入，影片使用一般視訊 VAE 解碼。360 度閉合且起訖高度／距離一致時，工具可要求末幀錨定原圖；這不保證中途軌跡精確。

原生 ComfyUI 也已安裝 Camera H3 與 H3 Edit 節點。（本機）`workflows/H3_Camera_Q4_API.json` 是接線參考，使用前需替換其中的參考圖片名稱；此資料夾不在公開 repo。

- 攝影機：https://github.com/NyckM/3d-Camera-control-H3-Minimax （版本 `846880de859959e801b2c506dc424bd5c8b5c6c4`）
- 編碼依賴：https://github.com/ethanfel/ComfyUI-MiniMax-H3-Edit （版本 `92ff5b926945e21d843fa618ba440ad2f96048e6`）
- 工具以提示詞引導運鏡，並非幾何攝影機控制；實際角度、速度及場景一致性仍取決於 H3。

## RealRebelAI 長影片擴展（H3 Extender，僅本機）

以下是這台機器另外手動部署的節點與工作流，面板不依賴它們，`install.bat` 也不會安裝：

RealRebelAI 推薦之 MiniMax H3 / FastH3 長影片擴展架構：
- **`ComfyUI_MiniMax_H3_Extender`**：提供 `MiniMaxH3Extender` 與 `MiniMaxH3MotionContextDiskFinalDecode`。核心機制為 Latent 運動視窗滑動接力與硬碟快取釋放 VRAM。
- **`ComfyUI-KJNodes`**：提供 `ImageResizeKJv2`、`GetImageSize` 等前處理節點。
- **官方工作流檔案**：置於 `workflows/realrebelai/`：
  - `FastH3---T2V_ONLY_Extender_Nodes.json`
  - `FastH3---FL2VA.json`
  - `FastH3---T2V.json`
  可在原生 ComfyUI（http://127.0.0.1:8188）直接將 JSON 拖入使用。

來源：https://github.com/ModelTC/Minimax-H3-Turbo
