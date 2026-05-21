---
name: hanmeimei-avatar
description: |
  韩梅梅形象生成技能 — 用 ComfyUI 生成韩梅梅的 AI 写真照片和未来的语音视频。
  保持面部一致性、写实风格、超白皙肌肤。
  当用户说"给我发张照片"、"出张图"、"看看你"、"你的照片"、"勾搭我"时触发。
  当用户说"涩图"、"nude"、"裸"时使用 --nude 模式。
  调用 comfyui 技能执行实际生成。
metadata:
  author: 韩梅梅
  version: "4.5.0"
  version_date: "2026-05-21"
  repo: "https://github.com/normdist-ai/skills/tree/main/hanmeimei-avatar"
  version_changelog: "v4.5: 远程仓库迁移到 normdist-ai/skills 子目录（原独立仓库已删除）；v4+随机种子连续出图45张全成功用户确认质量OK；good-seeds.txt扩充至4颗（+356807174）；ComfyUI队列机制确认无OOM风险"
  roadmap: "图片✅ → LoRA训练(暂缓) → 视频生成(当前目标) → 语音合成 → 数字人"
  architecture: "分层架构：selfie-v4.py → good-seeds.txt（种子池）+ prompts/*.txt + comfyui_client.py → run_workflow.py → 远程ComfyUI"
---

# 韩梅梅形象生成

## 架构说明

```
# v4 架构（当前）
scripts/selfie-v4.py (主入口 — 种子池版)
    ↓ 读取 good-seeds.txt（优质种子池，默认从中随机选种子）
prompts/base.txt + prompts/{scene}.txt (提示词文件)
    ↓ 读取
workflows/faceid.json (工作流模板)
    ↓ 调用
scripts/comfyui_client.py (客户端)
    ↓ 调用
comfyui/run_workflow.py (执行)
    ↓ 连接
远程服务器 (10.28.9.6:8188)
```

## 目录结构

```
hanmeimei-avatar/
├── SKILL.md                    # 技能元数据
├── prompts/                    # ✅ v3 提示词文件（外置，用户可直接编辑）
│   ├── base.txt                # 正向+负向基础提示词（全局共用）
│   ├── boulevard.txt           # 林荫道（4季×6时段）
│   ├── cafe.txt                # 咖啡馆
│   ├── library.txt             # 图书馆
│   ├── rooftop.txt             # 天台
│   └── bedroom.txt             # 卧室
├── workflows/                  # 工作流文件
│   ├── default.json            # 默认工作流（含 FaceID）
│   ├── faceid.json             # FaceID 工作流模板
│   └── base.json               # 基础工作流（无 FaceID）
│   ├── seed_pool.py            # ✅ 种子池管理工具（list/add/pick）
│   ├── selfie-v3.py            # v3 主入口（提示词外置版）
│   ├── selfie-v4.py            # ✅ v4 种子池版（当前推荐，支持 good-seeds.txt）
│   ├── selfie.py               # v2 自拍入口（= selfie-v2.py，提示词硬编码版）
│   ├── selfie-v2.py            # 同 selfie.py（开发源文件）
│   ├── photo.py                # 默认入口
│   ├── generate.py             # 支持 --composition 构图控制
│   └── comfyui_client.py       # comfyui 技能客户端
├── assets/faces/               # 脸部参考图片
└── outputs/                    # 输出目录
```

## 快速开始

```bash
# v4 自拍（推荐 — 种子池版，默认从 good-seeds.txt 随机选优质种子）
python scripts/selfie-v4.py

# 指定场景
python scripts/selfie-v4.py --scene cafe

# 指定种子 / 完全随机 / 追加当前种子到池
python scripts/selfie-v4.py --seed 86522080
python scripts/selfie-v4.py --random-seed
python scripts/selfie-v4.py --add-seed          # 需配合 --seed

# 用自定义提示词文件（网上复制的直接粘贴到文件里）
python scripts/selfie-v4.py -p prompts/my_style.txt

# 笑容等级 / 表情控制
python scripts/selfie-v4.py --smile-level 4
python scripts/selfie-v4.py -e "big grin, wide toothy smile, laughing joyfully"

# nude 模式
python scripts/selfie-v4.py --nude
python scripts/selfie-v4.py --nude --smile-level 5

# v3 自拍（旧版，提示词外置但无种子池）
python scripts/selfie-v3.py

# v2 自拍（旧版，提示词硬编码版）
python scripts/selfie.py --smile-level 4

# 默认生成
python scripts/photo.py
```

## 提示词文件架构（v3）

selfie-v3.py 从 `prompts/` 目录读取提示词，不硬编码在脚本中。

**分层逻辑：** base.txt（全局基础） → 场景文件（差异覆盖）

```
prompts/
├── base.txt          # [positive] 正向基础 + [negative] 负向基础（画质/肤色/手部/多人脸/nsfw约束）
├── boulevard.txt     # 林荫道 — [spring.morning] / [summer.night] ... 各段
├── cafe.txt          # 咖啡馆
├── library.txt       # 图书馆
├── rooftop.txt       # 天台
└── bedroom.txt       # 卧室
```

**场景文件格式：**
```
# 注释行
[spring.morning]
outfit: light spring dress, pastel cardigan
expression: peaceful smile
lighting: fresh spring morning sunlight through cherry blossom branches
background: outdoor street with trees and buildings
```

**覆盖规则：** 场景文件中 `outfit`/`expression`/`lighting`/`background` 覆盖 base.txt 的默认值。场景文件也可以包含 `[positive]`/`[negative]` 段来完全替换基础提示词。

**用户工作流：** 在 Civitai/LibLib 看到好的提示词 → 复制到 txt 文件 → `python selfie-v3.py -p prompts/xxx.txt` 直接出图。文件格式参考 [references/a1111-metadata-format.md](references/a1111-metadata-format.md)

**外部提示词适配规则（Flux/SDXL → SD1.5+FaceID）：**
- 模型：换成 ChilloutMix-Ni（SD1.5 写实）
- CFG：Flux 用 CFG=1 → SD1.5 改为 **4.0**（CFG=1 出来是噪点）
- 尺寸：SDXL/Flux 用 1024×1536 → SD1.5 改为 **512×768**（原生分辨率）
- 采样器：Euler 保持不变
- 加入 FaceID 保持韩梅梅的脸（工作流自动处理）
- 提示词：保留原意翻译，加入手部优化词（`perfect hands, five fingers per hand`）和负面手部词
- 输出 txt 文件放 `prompts/` 目录，用 `-p` 参数指定

## 核心参数速查

| 参数 | 值 | 说明 |
|------|-----|------|
| 模型 | ChilloutMix-Ni | SD1.5 写实模型 |
| CFG | **4.0** | 表情控制最佳值 |
| 采样器 | **euler** + normal | 避免塑料感 |
| FaceID 权重 | weight_faceidv2 = **0.80** | 表情控制最佳平衡点 |

## 参考文档

- [references/skill-details.md](references/skill-details.md) — 详细参数说明、环境感知逻辑
- [references/a1111-metadata-format.md](references/a1111-metadata-format.md) — A1111/Civitai/LibLib 参数格式规范（SD 社区事实标准）

## 笑容等级（--smile-level 参数）

| 等级 | 表情 | 权重 |
|------|------|------|
| 1 😊 | gentle smile, soft smile | 1.0 |
| 2 😁 | happy smile, cheerful expression | 1.15 |
| 3 😃 | smiling, showing teeth | 1.3 |
| 4 😄 | big grin, wide smile, laughing | 1.4 |
| 5 🤣 | big grin, wide toothy smile, laughing joyfully, showing teeth | 1.5 |

## Gotchas

- **所有场景必须使用 FaceID** — 这是韩梅梅个人照片技能，脸型一致性是核心要求
- **CFG 过高导致塑料感** — FaceID 模式下 CFG 建议保持 3.5-4.0
- **euler + normal 采样器** — 配合低 CFG 才能获得自然皮肤质感
- **weight_faceidv2 = 0.80** — 表情控制最佳平衡点（经过测试验证）
- **默认笑容等级 3（露齿微笑，权重1.3）** — v3 默认使用等级3，不指定 --smile-level 时自动生效。表情权重 1.3 配合 weight_faceidv2=0.80 使用，保持面部特征同时产生明显笑容
- **batch_size 必须为 1** — 多图生成会导致 FaceID 失效
- **nude 模式下穿搭词必须清除** — `selfie-v2.py --nude` 在正向提示词加 `nude` 的同时不能保留任何 `wearing xxx` 穿搭词，否则模型指令冲突导致出图异常。必须在拼接提示词前统一 `re.sub(r',?\s*wearing [^,]+', '', text)` 清掉所有 wearing 词汇
- **nude 模式用 selfie.py --nude** — 已从 selfie-nude.py 合并到 selfie.py（= selfie-v2.py），通过 `--nude` / `-n` 参数切换。nude 模式：clothing=None、正向加 `nude` 关键词、反向去掉 `(nsfw:1.8)` 约束
- **避免紧身服装词** — `zentai`、`bodysuit`、`full body suit` 等词在模型中被理解为类似裸体效果
- **反向提示词开头不能有排除关键词** — 排除词应加在中间并提高权重（如 `(nude:1.5)`）
- **手部提示词策略（4维度版）** — 正向加 `perfect hands, five fingers per hand` 引导好手；反向保留4个不同维度的词：`(mutated hands:1.3)` 变异 / `(extra fingers:1.3)` 多指 / `(missing fingers:1.2)` 少指 / `(poorly drawn hands:1.2)` 整体差。这4个不属同类重复，砍任何一个都会导致对应维度退步。仅靠提示词不能100%消灭手部畸形，waist up 构图仍是最稳妥方案
- **selfie.py（v0）是稳定生产版，v2-v4 是开发版** — cron 的 selfie.sh 调用 selfie.py（v0），提示词在工作流模板 faceid.json 里硬编码。v4 提示词外置到 prompts/base.txt。不混用
- **v4 负面词已对齐 v0（2026-05-21 修复）** — 之前 v4 base.txt 负面词比 v0 faceid.json 少了一大截（"同类负面词只保留一个"过度精简），导致皮肤质感退步。已补回所有 v0 有效约束：`tanned/dark/yellow skin`（防偏色）；`freckles/moles/spots/blemishes/skin imperfection/acne/scars/skin spots`（防瑕疵）；`airbrushed/oversmoothed`（防塑料感）；`bad proportions:1.331/disfigured:1.331/extra limbs/missing arms:1.331/extra legs:1.331`（防变形）；`fused fingers:1.61051/too many fingers:1.61051`（原权重）；`unclear eyes:1.331`（防眼部模糊）。正向皮肤词 v0/v4 完全一致，差异全在负面词，现已修复
- **ComfyUI 不接受 seed=-1（单条记录）** — `--random-seed` 不能传 -1 给 KSampler，会立即返回空错误。必须用 `random.randint(1, 999999999)` 生成实际种子值。ComfyUI 自带 FIFO 队列串行执行，不会 OOM，但 cron v0 和手动 v4 同时提交时排队可能导致 HTTP 轮询超时被误判为"生成失败"
- **ComfyUI 内置 FIFO 队列，串行执行** — 不会 OOM（一次只跑一个工作流）。cron v0 和手动 v4 同时提交时，后来的排队等前面的完成。不会并行占显存，但排队可能导致 HTTP 轮询超时被误判为"生成失败"
- **selfie.py 默认构图看不到手** — faceid.json 模板用 `85mm portrait lens` 生成近身特写，手不在画面内，无法验证手部优化效果。验证手部需要临时改模板为 `cowboy shot, from thighs up, hands visible` + `35mm lens`（广角拉远），或用 generate.py 的 `--composition mid-thigh up`。验证完记得改回 85mm portrait
- **种子管理策略（v4 种子池版，学术+社区验证）** — arXiv 2405.14828（46M图实验）证明"黄金种子"跨提示词泛化性好；Reddit wonderflex 教程证明每个种子有内在"主题"（色温/构图/默认服装）。管理方式：`good-seeds.txt` 保存验证好种子 → selfie-v4.py 默认从中随机选取 → `--seed N` 手动覆盖 → `--random-seed` 探索新种子。筛选流程：跑20张随机种子 → 用户挑好的 → 追加到 good-seeds.txt（用 `--add-seed` 或手动）。当前池：86522080（默认）、258102719、98994781（白瓷肌标杆）、356807174（用户 05-21 挑选）。详见 [references/good-seeds.md](references/good-seeds.md)
- **arXiv 黄金种子不可直接迁移** — arXiv 2405.14828 论文未公开具体种子列表，且其 golden seeds（~65 for SD2.0, ~67 for SDXL Turbo）是针对 MS-COCO prompts + SD 2.0/SDXL Turbo 找到的，跟我们的模型和人像场景完全不同。不能直接套用。详见 [references/good-seeds.md](references/good-seeds.md)
- **v4 selfie-v4.py 是推荐入口** — 支持 good-seeds.txt 种子池，默认从中随机选优质种子。三个参数：`--seed N`（指定）、`--random-seed`（完全随机）、`--add-seed`（追加当前种子到池）
- **默认种子 86522080** — v3 不指定 `--seed` 时使用固定默认种子 86522080（来源：selfie-nude.py 的验证好种子）。所有场景共用同一种子，不同场景因提示词不同仍有差异，同场景同种子出图完全相同。指定 `--seed` 可覆盖
- **种子可复现性** — 相同种子 + 相同参数会生成完全相同的图片
- **使用 selfie-v3.py（推荐）或 selfie.py 进行自拍** — v3 提示词外置版支持 `--scene`/`--prompt-file`；v2 提示词硬编码版支持笑容等级控制、表情自定义和 --nude 模式
- **v3 --scene 指定场景时光线必须为空** — selfie-v3.py 中 `--scene` 指定场景时，lighting 应设为空字符串让场景文件填充，不能沿用 ROUTINES 随机选的其他场景的 lighting。否则会出现卧室场景用图书馆光线的 bug
- **v3 直接写提示词文本到工作流** — 不像 v2 用正则替换工作流模板中的提示词，v3 用 `update_workflow_prompts()` 直接将拼装好的正/负向文本覆盖到 CLIPTextEncode 节点。工作流模板中的提示词文本只是占位符
- **定时自拍禁止涩图** — 半点自拍 cron 任务（no_agent 模式直接跑脚本）只出生活照。`--nude` 只在张阳明确要求时才能使用，绝不在定时任务、主动推送、或未被要求的情况下出涩图
- **Cron 部署方式** — 定时自拍用 wrapper 脚本 `~/.hermes/profiles/hanmeimei/scripts/selfie.sh`（cd 到 skill scripts 目录后 exec selfie.py），因为 selfie.py 依赖同目录的 `comfyui_client.py`，不能直接 cp 到 profile scripts 目录。cron 配置：`script: "selfie.sh"`, `no_agent: true`, `schedule: "*/30 6-23 * * *"`
- **反向提示词需检查负面嵌入** — `EasyNegative` 和 `bad_prompt_version2` 在工作流模板中可能缺失，脚本需主动检查并补上
- **selfie.py 无构图参数** — selfie.py 不支持 `--composition` 或 `--background` 参数（只有 generate.py 支持）。需要 cowboy shot / full body 等非默认构图时，需临时修改 `workflows/faceid.json` 模板提示词（加 `cowboy shot, from thighs up, hands visible` + 换 `35mm lens`），用完改回 `85mm portrait lens`。selfie-v3.py 通过 prompt-file 机制可更灵活处理构图
- **selfie-v3.py 构图灵活性** — v3 直接写入提示词文本到工作流，不依赖正则替换。修改构图只需编辑提示词文件（如加 `cowboy shot` 关键词），不需要改工作流模板
- **图片编号规则** — 文件名格式：`HMM-v4-YYYYMMDDHHMMSS-{种子号}.png`（时间戳+种子号，无连字符分隔日期和时间）。
- **出图发送格式：种子号和图连着发** — 批量出图时，每张图必须紧跟对应的种子号一起发送，方便用户识别和挑选优质种子。格式示例：`种子 98994781\nMEDIA:xxx-98994781.png`。不要把所有图堆在一起最后才列种子号
- **图片元数据格式** — ComfyUI 输出的是 JSON 工作流格式，不是 A1111 的 `parameters` 文本格式。上传 Civitai 需要额外转换。详见 [references/a1111-metadata-format.md](references/a1111-metadata-format.md)
- **DOE 实验验证提示词变量影响** — 要验证某个提示词变量（如光线时间词）是否影响出图，用 DOE 方法：固定种子 + 固定表情 + 固定所有参数，只变目标变量。创建多个 doe-*.txt 文件（对照组无变量 + 各实验组），用 `python selfie-v3.py -p prompts/doe-xxx.txt -e "gentle smile" -s 123456789` 逐组跑。注意文件名带种子，同名种子会覆盖，所以 DOE 输出文件名可能重复（需要手动区分或改时间戳）
- **DOE 已验证：时间/光线提示词对出图有显著影响** — 对照组（无时间词）vs morning/evening/midnight 实验组对比，光线氛围明显不同。这验证了 v3 场景文件中按时段配置光线描述的设计是有意义的，不是摆设
- **v3 时间+日期自动注入（2026-05-21 新增）** — `get_time_description()` 自动根据当前月份生成季节感（如 `late spring season`）+ 根据小时生成精确时间词（如 `bright late morning light, early summer morning at 11am`），注入正向提示词。效果：同一天不同时段出图光线氛围自动不同，不需要手动配。位置在表情之后、场景光线之前
- **提示词精简原则：正面和负面规则不同！** — 负面提示词适用"同类只保留一个"：用户说"太多了也会导致图片怪异"，负面从 40+ 精简到 18 个。但**正面带权重的皮肤词不可合并**：`(very pale porcelain white skin:1.3)` + `(fair snow white body:1.2)` 各自带独立权重引导模型，合并成 `(pale porcelain skin with rosy undertone:1.3)` 实测导致皮肤不够真实。皮肤正向必须保持工作流原始配方：8个词（2个带权重白肤词 + rosy undertone + pores + details + lip color + flawless + perfect skin），这是经过验证的最佳组合，不要试图"优化"
- **负面手部词保留4个维度** — `(mutated hands:1.3)` 管变异、`(extra fingers:1.3)` 管多指、`(missing fingers:1.2)` 管少指、`(poorly drawn hands:1.2)` 管整体画得差。这4个是不同维度的约束，不属同类重复，不能砍。砍掉 poorly drawn → 手指变形明显回升
- **基础服装词必须在 wearing 子句里，且需要权重** — `bra` 和 `(round neck t-shirt:1.3)` 必须写在 `build_final_positive` 的 wearing 拼接中，不能放在 base.txt 正向提示词里。放 base.txt 里会被场景 outfit 的 `wearing xxx` 覆盖掉，模型看不到。**round neck t-shirt 不加权时只有约1/3概率出现，加到1.3后稳定出现在每张图**
- **负面词不能过度精简** — v4 曾"同类负面词只保留一个"砍掉大量负面词，导致皮肤质感下降（对比 v0 回退验证）。v0 的完整负面词列表（tanned/dark/yellow skin, freckles/moles/blemishes, airbrushed/oversmoothed, bad proportions/disfigured 等）对皮肤质感至关重要，已全部补回 base.txt。**教训：精简负面词前必须 A/B 对比测试，不能凭直觉砍**
- **版本管理：v0=生产，v4=开发** — selfie.py (v0) 是定时任务用的稳定版，selfie-v4.py 是开发实验版。不混用。v0 确认效果好的提示词变更才合并到 v4。v4+随机种子连续出图45张全成功，用户确认质量OK
- **批量出图反馈** — 种子号和图要一起发，便于用户识别和挑选好种子加入 good-seeds.txt。
- **防裸体配方（v3.3 验证通过）** — 三层防御：
  1. base.txt 正向：`fully clothed`（通用约束）
  2. build_final_positive wearing 子句：`wearing bra, round neck t-shirt, {场景outfit}`（基础内衣+T恤必须在 wearing 里，不能放 base.txt 前面，否则被场景 outfit 覆盖无效）
  3. base.txt 负向：`(nsfw:2.0), (nude:1.8), (naked:1.5), (nipples:1.5)` 四维度
  **肩部和乳沟可以露**，不加 `(bare shoulders)` 和 `(cleavage)` 负面词。场景 outfit 必须具体（如 `white blouse, long skirt, bra`），不能只写 `casual outfit`，太模糊容易跑偏出裸体
  **bra 提示词对防裸体非常有效**（用户原话），实测30张稳定性测试验证
- **精简后必须多图验证** — 单张看不出退化，至少出 3-4 张图才能发现稳定性问题
- **多图发送飞书限制** — 飞书消息中嵌入多个 MEDIA: 标签时，用户可能只收到第一张。应逐张发送，或用 separate messages
- **用户说"图片没收到"时直接重发** — 这是投递失败，不是歧义。不要去翻 session history 询问"哪张图"。直接找到最近生成的图（`ls -t outputs/*.png | head -1`），重新带上 MEDIA: 标签发送即可。用户说"不对"说明你在浪费时间猜而不是行动

## 参考文档

| 文档 | 内容 | 路径 |
|------|------|------|
| 技能详细文档 | 参数配置、脚本说明、安全规则 | [references/skill-details.md](references/skill-details.md) |
| 提示词指南 | 正向/反向提示词、穿搭参考 | [references/prompt-guides.md](references/prompt-guides.md) |
| 工作流指南 | 两步法、Seed模板、参数配置 | [references/workflow-guides.md](references/workflow-guides.md) |
| 季节衣橱 | 四季穿搭、天气修正 | [references/seasonal-wardrobe.md](references/seasonal-wardrobe.md) |
| FaceID 一致性研究 | 脸型一致性控制方法 | [references/face-consistency-research.md](references/face-consistency-research.md) |
| 种子管理策略 | 种子主题理论、黄金种子学术验证（arXiv 2405.14828，46M图实验）、golden seeds 不可迁移说明、good-seeds.txt 池设计、v4 使用方式、筛选流程 | [references/good-seeds.md](references/good-seeds.md) |
| seed_pool.py | 种子池管理工具：list/add/pick 子命令，按场景分组显示 | [scripts/seed_pool.py](scripts/seed_pool.py) |
| A1111 参数格式 | Civitai/LibLib 复制参数的格式规范 | [references/a1111-metadata-format.md](references/a1111-metadata-format.md) |
| arXiv 种子研究 | Secret Seeds 论文核心发现（46M图验证黄金种子） | [references/arxiv-secret-seeds.md](references/arxiv-secret-seeds.md) |

## 已知限制

- **手部变形**：AI绘画通病。纯提示词层面已到天花板（正向 `perfect hands, five fingers per hand` + 反向 4 维度手部词：mutated/extra/missing/poorly drawn），畸形率从约 80% 降至约 40-50%，但仍非100%稳定。**下一步方案已确认可行**：Impact-Pack 的 YOLOv8n Hand Detector（hand_yolov8n.pt ✅）+ BboxDetectorSEGS + DetailerForEachAutoRetry + GoodHands-vanilla LoRA（✅），全部组件已在服务器上就位。正在实施手部检测+局部重绘流程改造 faceid.json。详见 [references/hand-fix-research.md](references/hand-fix-research.md)
- **SD1.5 服装控制力**：FaceID模式下CFG建议 3.5-4.0
- **SDXL 不兼容 FaceID**：仅支持 SD1.5 模型
- **表情控制需要平衡**：需要明显笑容时，使用 selfie.py/v3.py 并调整 FaceID 参数

## 远程仓库同步

技能源码在 GitHub 仓库 **normdist-ai/skills** 的 `hanmeimei-avatar/` 子目录（public 仓库）。

```bash
# 同步到 skills 仓库
cd /tmp && git clone https://github.com/normdist-ai/skills.git
rm -rf /tmp/skills/hanmeimei-avatar
cp -r ~/.hermes/profiles/hanmeimei/skills/creative/hanmeimei-avatar /tmp/skills/hanmeimei-avatar
rm -rf /tmp/skills/hanmeimei-avatar/.git
cd /tmp/skills && git add -A && git commit -m "feat: hanmeimei-avatar 变更描述" && git push

# ⚠️ 本地技能目录不是 git repo，不要在本地 git init
```

**gh CLI 认证**：`echo "TOKEN" | gh auth login --with-token`（PAT 已存储在 memory 中）

## 路线图

| Phase | 状态 | 内容 |
|-------|------|------|
| Phase 1 | ✅ | 图片生成、FaceID面部一致性 |
| Phase 2 | ⏳ | LoRA训练 |
| Phase 3 | 🔄 | 视频生成（Wan2.1 I2V） |
| Phase 4 | 📋 | 语音合成 → 数字人 |
