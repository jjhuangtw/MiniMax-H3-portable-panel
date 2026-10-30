# 🔞 成人向社区模型（自行下载）

[繁體中文](NSFW_MODELS.md) | [English](NSFW_MODELS.en.md) | **简体中文** | [日本語](NSFW_MODELS.ja.md)

> **仅限 18 岁以上。** 以下是社区作者基于 MiniMax H3 微调的第三方模型，每个约 21～23 GB。面板的安装程序**不会**下载它们，
> 本仓库也不包含、不分发。请自行下载、阅读作者的许可，并遵守本页最下方的使用规范。
>
> 面板在简体中文浏览器中显示繁体中文界面，因此下文的按钮与菜单名称按繁体界面书写（例如「🧩 模型設定」）。

## 选哪一个

| 模型 | 文件大小 | 显存 | 可用菜单 |
| --- | --- | --- | --- |
| **10Eros-Max** beta7 8-step Turbo int8HQ | 22.9 GB | 24 GB 以上（RTX 4090 实测） | FL2VA ＋ Ref2VA |
| **DaSiWa MiniMax H3** Hybrid v4 Turbo int8 | 21.0 GB | 24 GB 以上（RTX 4090 实测） | FL2VA ＋ Ref2VA |

两个都是**混合模型**（一个文件同时出现在 FL2VA 与 Ref2VA 两个菜单），并且**已内置 Turbo 蒸馏**，不需要 Turbo LoRA：
10Eros beta7 用 8 步，DaSiWa v4 Turbo 用 4 步（更快）。4090 实测 864×480／4 秒：DaSiWa v4 Turbo 约 29 秒、10Eros beta7 约 54 秒。选一个即可，不必两个都装。

12～16 GB 显卡：有较小的版本，但**本面板都未实测**：DaSiWa 的 int4 文件（12.5／16.8 GB，见下方），以及社区的 10Eros-Max GGUF 版
（[Abiray/10Eros-Max-GGUF](https://huggingface.co/Abiray/10Eros-Max-GGUF)，Q3_K_M 8.9 GB · Q4_K_M 11.6 GB）。
GGUF 版来自较早的 **Test4 测试版**，采样设置请按该模型页的说明。

## 放在哪里

两个文件都放进**同一个文件夹**，和官方 H3 模型放在一起：

```
<安装文件夹>\ComfyUI\models\diffusion_models\
```

- 用 `setup.bat` 安装：`setup.bat 所在文件夹\ComfyUI_windows_portable\ComfyUI\models\diffusion_models\`
- 手动安装：`run_webui.bat` 旁边的 `ComfyUI\models\diffusion_models\`

**保留文件名里的关键字。** 面板靠文件名判断：文件名含 `Turbo` 会自动切到「模型內建蒸餾」，同时含 `v4Turbo`／`4turbo`／`4step` 时用 4 步、否则 8 步；
含 `10Eros`／`Dasiwa` 会在菜单里显示标签。如果要改名，请保留这些字（例如 `DasiwaMinimaxH3_dasiwaHybridV4Turbo_int8.safetensors` 可以）。

## 1. 10Eros-Max（TenStrip）

- 模型页：https://huggingface.co/TenStrip/10Eros-Max（标记为 *Not-For-All-Audiences*；许可：MiniMax H3 Community License）
- 文件：`10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors`（22,893,150,024 bytes）
- 直接下载：
  https://huggingface.co/TenStrip/10Eros-Max/resolve/682e73d12dcaf766dd31b4bb2991084119c2df8c/10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors
- SHA-256：`8a51ca3f7d290a799d89fefcde4ede60962256955a91dfe4746d3cc07814fd6e`
- 同一页的其他文件**不用下载**：`…_8stepTURBO_beta7.safetensors`（40 GB 未压缩原文件，24 GB 显卡放不下）、`…_raw_beta7_int8`（非 Turbo，要 20 步）。
  作者建议 beta5 或 beta7，避免 beta6。
- 作者提到单次采样时背景偶尔会闪烁；本机 4 秒测试没有出现。

## 2. DaSiWa MiniMax H3（Civitai）

- 模型页：https://civitai.com/models/2877206?modelVersionId=3392061
- 这是 **DaSiWa Hybrid v4 Turbo** 版本（4 步），下载标注 **int8** 的文件（约 21 GB）。Civitai 需要登录免费账号并开启成人内容显示才能看到，请自行设置。
- 文件：`DasiwaMinimaxH3_dasiwaHybridV4Turbo_3281858.safetensors`（20,967,668,616 bytes；改名成 `DasiwaMinimaxH3_dasiwaHybridV4Turbo_int8.safetensors` 也可以）
- SHA-256：`36471AFB817747B711B9ABAD3D8E6B7C88A7C2B91B4887D040A8DCB7EE82B2D6`
- 同一版本还有两个 **int4** 文件（约 12.5 GB 与 16.8 GB），16 GB 显卡或许能用，但**本面板未实测**。
- 非 Turbo 的「Hybrid v4」也能用，但要选「非蒸餾・20 步」，速度慢很多。

## 检查下载是否完整

下载不完整是最常见的崩溃原因。在文件所在的文件夹打开命令提示符，把结果和上方的 SHA-256 对比（大小写不影响）：

```bat
certutil -hashfile 10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors SHA256
```

## 在面板中使用

1. 把文件放进上面的 `diffusion_models\`。
2. 打开面板上方的 **「🧩 模型設定」**，点 **「🔄 重新掃描」**。仍然没出现就运行 `restart_webui.bat`。
3. 在 **「FL2VA 擴散模型」**（文生／首尾帧／3D 摄像机／编剧）或 **「Ref2VA 擴散模型」**（参考影音／V2V／对口型）菜单中选择它。
4. 采样模式：10Eros beta7 用 **「模型內建蒸餾・8 步」**，DaSiWa v4 Turbo 用 **「模型內建蒸餾・4 步」**。选择模型时会自动切换，不要再叠加 Turbo LoRA。
5. 两个都超过 20 GB，不能配合 **「✨ 高清二次採樣」**（加载后显存不够放大模型使用），请用 864×480 或 960×544 生成，再到「🔍 放大」分页提升分辨率。

可选：无审查的 **Heretic** 文本编码器是 `download_extras.bat` 的选项 **6**。它只去掉语言模型的拒答，能画出什么取决于上面的扩散模型。

## LoRA

Ref2VA 用的 LoRA，例如 [SexGod1979/AfterMidnight-MiniMax-H3-NSFW](https://huggingface.co/SexGod1979/AfterMidnight-MiniMax-H3-NSFW)
（Apache-2.0，两个各 1.19 GB 的文件：`…_sexytime_rank64-v1.2` 偏动作，建议强度 1.0；`…_softer_rank64_v1` 偏细节，建议 0.8～1.0）：

1. 放进 `ComfyUI\models\loras\NSFW\` 这类子文件夹。
2. 在 **「🧩 模型設定」** 点 **「🔄 重新掃描」**，在 **「🧷 Ref2VA LoRA」** 中选择它，并调整 **「LoRA 強度」**。
3. 只作用于 Ref2VA 分页（参考影音、V2V、对口型、附参考图的编剧）。AfterMidnight 作者要求使用 **beta** 调度器，否则音频会出问题；面板会自动改用 beta。

FL2VA 用的 LoRA（文生、首尾帧）在 **「🧷 FL2VA LoRA」** 菜单中用同样的方式选择。文件名含 `ref2v` 的只出现在 Ref2VA 菜单，含 `fl2v` 的只出现在 FL2VA 菜单。

## 使用规范

- **只使用虚构的成年角色，或已同意被描绘的成年人。**
- **禁止**未经同意用真人制作色情、裸露或虚假影像：名人、认识的人、网上的照片都不行。这在许多国家属于违法。
- **禁止**任何涉及未成年人，或外貌像未成年人的内容。
- 除非平台允许且当事人都同意，否则不要公开分享。请遵守当地法律与各模型的许可（MiniMax H3 Community License；DaSiWa 遵循 Civitai 条款）。

## 致谢

- **TenStrip** — [10Eros-Max](https://huggingface.co/TenStrip/10Eros-Max) · GGUF 版：**Abiray** — [10Eros-Max-GGUF](https://huggingface.co/Abiray/10Eros-Max-GGUF)
- **DaSiWa** — [DaSiWa MiniMax H3（Civitai）](https://civitai.com/models/2877206/dasiwa-minimax-h3)
- **SexGod1979** — [AfterMidnight-MiniMax-H3-NSFW](https://huggingface.co/SexGod1979/AfterMidnight-MiniMax-H3-NSFW)
- **sakamakismile** — [Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4](https://huggingface.co/sakamakismile/Qwen3-VL-32B-Heretic-MiniMax-H3-NVFP4)
- 以上都基于 MiniMax 的 **MiniMax H3** — [MiniMaxAI/MiniMax-H3](https://huggingface.co/MiniMaxAI/MiniMax-H3)
