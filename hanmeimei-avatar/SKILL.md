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
  version: "5.0.0"
  version_date: "2026-05-24"
  version_changelog: "v5.14: 远程仓库同步改用 gh api（git clone 超时）；凭证管理规范（.env + fact_store）；PDCA/SIPOC/风险思维方法论"
  roadmap: "图片✅(v5手部优化版已验证优于v4) → LoRA训练(暂缓) → 视频生成(当前目标) → 语音合成 → 数字人"
  architecture: "分层架构：selfie.sh（管道，版本无关入口，改一行切版本）→ selfie-v5.py（当前 cron 生产版）→ feishu_sender.py（三气泡发送：①图片→②信息（纯文本，无引用标记无emoji）→③想法）；good-seeds.txt（种子池）+ prompts/*.txt + message-template.txt（消息格式）+ comfyui_client.py → run_workflow.py → 远程ComfyUI"
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
├── prompts/                    # 提示词文件
│   ├── base.txt                # 正向+负向基础提示词（仅画质/人设，不含穿搭约束）
│   ├── message-template.txt    # ✅ 消息格式模板（变量：{image}/{time_full}/{scene_cn}/{seed}/{thought}）
│   ├── boulevard.txt           # 林荫道（4季×6时段）
│   ├── cafe.txt                # 咖啡馆
│   ├── library.txt             # 图书馆
│   ├── rooftop.txt             # 天台
│   ├── bedroom.txt             # 卧室
│   ├── park.txt                # ✅ 公园（2026-05-23 新增）
│   └── travel.txt              # ✅ 旅行途中（2026-05-23 新增）
├── workflows/                  # 工作流文件
│   ├── default.json            # 默认工作流（含 FaceID）
│   ├── faceid.json             # FaceID 工作流模板
│   └── base.json               # 基础工作流（无 FaceID）
├── scripts/                    # 脚本文件
│   ├── selfie-v5.py            # ✅ v5 手部优化版（当前 cron 生产版，推荐）
│   ├── feishu_sender.py        # ✅ 飞书三气泡发送器（独立于生图，cron 用）
│   ├── selfie-v4.py            # v4 种子池版（备选）
│   ├── selfie-v3.py            # v3 主入口（提示词外置版）
│   ├── selfie.py               # v2 自拍入口（= selfie-v2.py，提示词硬编码版）
│   ├── selfie-v2.py            # 同 selfie.py（开发源文件）
│   ├── photo.py                # 默认入口
│   ├── generate.py             # 支持 --composition 构图控制
│   ├── seed_pool.py            # ✅ 种子池管理工具（list/add/pick）
│   └── comfyui_client.py       # comfyui 技能客户端
├── assets/faces/               # 脸部参考图片
└── outputs/                    # 输出目录
```

## 快速开始

```bash
# v5 自拍（推荐 — 手部优化版，效果优于 v4）
python scripts/selfie-v5.py

# 指定场景
python scripts/selfie-v5.py --scene cafe

# v4 自拍（备选 — 种子池版）
python scripts/selfie-v4.py

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
│   ├── base.txt                # 正向+负向基础提示词（全局共用，不含穿搭约束）
│   ├── message-template.txt    # ✅ 消息格式模板（变量：{image}/{time_full}/{scene_cn}/{seed}/{thought}）
│   ├── boulevard.txt           # 林荫道（4季×6时段）
│   ├── cafe.txt                # 咖啡馆
│   ├── library.txt             # 图书馆
│   ├── rooftop.txt             # 天台
│   ├── bedroom.txt             # 卧室
│   ├── park.txt                # ✅ 公园（2026-05-23 新增）
│   └── travel.txt              # ✅ 旅行途中（2026-05-23 新增）
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
- **selfie.py（v0）是旧生产版，v5 已接管** — cron 的 selfie.sh 现在调用 selfie-v5.py（手部优化版）。v0 保留但不再使用。v4/v5 提示词外置到 prompts/base.txt。不混用
- **v4 负面词已对齐 v0（2026-05-21 修复）** — 之前 v4 base.txt 负面词比 v0 faceid.json 少了一大截（"同类负面词只保留一个"过度精简），导致皮肤质感退步。已补回所有 v0 有效约束：`tanned/dark/yellow skin`（防偏色）；`freckles/moles/spots/blemishes/skin imperfection/acne/scars/skin spots`（防瑕疵）；`airbrushed/oversmoothed`（防塑料感）；`bad proportions:1.331/disfigured:1.331/extra limbs/missing arms:1.331/extra legs:1.331`（防变形）；`fused fingers:1.61051/too many fingers:1.61051`（原权重）；`unclear eyes:1.331`（防眼部模糊）。正向皮肤词 v0/v4 完全一致，差异全在负面词，现已修复
- **提示词设计原则：base.txt 只管画质，不碰穿搭/安全** — base.txt 是通用质量基线（皮肤、镜头、画质），不含 `fully clothed` 等穿搭约束。穿搭由场景文件 outfit 字段定义，防裸体靠场景 outfit（bra+具体衣物）+ 负面词 `(nsfw:1.8)` 兜底。**修改提示词前必须全链路思考**：对所有场景（bedroom/cafe/boulevard/library/rooftop/park/travel）+ 所有模式（日常/nude/未来泳装等）的影响。不能只解决眼前问题而引入新冲突
- **场景文件必须覆盖 ROUTINES 所有引用** — ROUTINES 里引用了 park 和 travel 场景，如果对应 `prompts/*.txt` 不存在，outfit/lighting/background 全部为空，防裸体第二层防御失效。已补齐 `park.txt`（公园，四季24时段）和 `travel.txt`（旅行途中，四季24时段）** — `--random-seed` 不能传 -1 给 KSampler，会立即返回空错误。必须用 `random.randint(1, 999999999)` 生成实际种子值。ComfyUI 自带 FIFO 队列串行执行，不会 OOM，但 cron v0 和手动 v4 同时提交时排队可能导致 HTTP 轮询超时被误判为"生成失败"
- **ComfyUI 内置 FIFO 队列，串行执行** — 不会 OOM（一次只跑一个工作流）。cron v0 和手动 v4 同时提交时，后来的排队等前面的完成。不会并行占显存，但排队可能导致 HTTP 轮询超时被误判为"生成失败"
- **selfie.py 默认构图看不到手** — faceid.json 模板用 `85mm portrait lens` 生成近身特写，手不在画面内，无法验证手部优化效果。验证手部需要临时改模板为 `cowboy shot, from thighs up, hands visible` + `35mm lens`（广角拉远），或用 generate.py 的 `--composition mid-thigh up`。验证完记得改回 85mm portrait
- **种子管理策略（v4 种子池版，学术+社区验证）** — arXiv 2405.14828（46M图实验）证明"黄金种子"跨提示词泛化性好；Reddit wonderflex 教程证明每个种子有内在"主题"（色温/构图/默认服装）。管理方式：`good-seeds.txt` 保存验证好种子 → selfie-v4.py 默认从中随机选取 → `--seed N` 手动覆盖 → `--random-seed` 探索新种子。筛选流程：跑20张随机种子 → 用户挑好的 → 追加到 good-seeds.txt（用 `--add-seed` 或手动）。当前池：86522080（默认）、258102719、98994781（白瓷肌标杆）、356807174（用户 05-21 挑选）。详见 [references/good-seeds.md](references/good-seeds.md)
- **arXiv 黄金种子不可直接迁移** — arXiv 2405.14828 论文未公开具体种子列表，且其 golden seeds（~65 for SD2.0, ~67 for SDXL Turbo）是针对 MS-COCO prompts + SD 2.0/SDXL Turbo 找到的，跟我们的模型和人像场景完全不同。不能直接套用。详见 [references/good-seeds.md](references/good-seeds.md)
- **v5 selfie-v5.py 是推荐入口（当前 cron 使用）** — 手部优化版，效果优于v4（张阳2026-05-23确认）。支持 good-seeds.txt 种子池、`--nude` 模式。参数同v4：`--seed N`、`--random-seed`、`--add-seed`
- **v6 场景选择架构已删除（2026-05-23）** — `selfie-v6.py` 因路径计算 bug（SKILL_DIR/WORKFLOWS_DIR 推导错误）和工作流文件名不匹配反复出错，用户决定暂停并删除 v6 代码。场景选择的概念（LIFE_STATES 分层：生活状态→场景，工作日/周末/时段分类）保留在 `references/v6-scene-selection.md` 供未来重写参考。当前 cron 只用 v5
- **默认种子 86522080** — v3 不指定 `--seed` 时使用固定默认种子 86522080（来源：selfie-nude.py 的验证好种子）。所有场景共用同一种子，不同场景因提示词不同仍有差异，同场景同种子出图完全相同。指定 `--seed` 可覆盖
- **种子可复现性** — 相同种子 + 相同参数会生成完全相同的图片
- **使用 selfie-v3.py（推荐）或 selfie.py 进行自拍** — v3 提示词外置版支持 `--scene`/`--prompt-file`；v2 提示词硬编码版支持笑容等级控制、表情自定义和 --nude 模式
- **v3 --scene 指定场景时光线必须为空** — selfie-v3.py 中 `--scene` 指定场景时，lighting 应设为空字符串让场景文件填充，不能沿用 ROUTINES 随机选的其他场景的 lighting。否则会出现卧室场景用图书馆光线的 bug
- **v3 直接写提示词文本到工作流** — 不像 v2 用正则替换工作流模板中的提示词，v3 用 `update_workflow_prompts()` 直接将拼装好的正/负向文本覆盖到 CLIPTextEncode 节点。工作流模板中的提示词文本只是占位符
- **定时自拍禁止涩图** — 半点自拍 cron 任务（no_agent 模式直接跑脚本）只出生活照。`--nude` 只在张阳明确要求时才能使用，绝不在定时任务、主动推送、或未被要求的情况下出涩图
- **Cron agent 模式配置完成但模型 tool-calling 不稳定** — qwen3.6-35b 能跑通生图但不会用 send_message 工具（用 terminal 绕路调 lark_oapi SDK，导致图片发送走弯路且暴露凭证）。**Cron prompt 必须明确写死工具名**：告诉模型「必须使用 send_message 工具发送，不要用 terminal 或 hermes send 命令」，否则小模型会自己瞎绕路。当前状态：正式 cron 已回退 no_agent=true（稳定），调试 cron 8b2309ac039d 用 agent 模式待验证
- **反向提示词需检查负面嵌入** — `EasyNegative` 和 `bad_prompt_version2` 在工作流模板中可能缺失，脚本需主动检查并补上
- **selfie.py 无构图参数** — selfie.py 不支持 `--composition` 或 `--background` 参数（只有 generate.py 支持）。需要 cowboy shot / full body 等非默认构图时，需临时修改 `workflows/faceid.json` 模板提示词（加 `cowboy shot, from thighs up, hands visible` + 换 `35mm lens`），用完改回 `85mm portrait lens`。selfie-v3.py 通过 prompt-file 机制可更灵活处理构图
- **selfie-v3.py 构图灵活性** — v3 直接写入提示词文本到工作流，不依赖正则替换。修改构图只需编辑提示词文件（如加 `cowboy shot` 关键词），不需要改工作流模板
- **图片编号规则** — 文件名格式：`HMM-v4-YYYYMMDDHHMMSS-{种子号}.png`（时间戳+种子号，无连字符分隔日期和时间）。
| **发送格式**：三气泡 cron（①图片→②信息→③想法），通过 `feishu_sender.py` 独立发送层实现。信息行无引用标记（`>`）无 emoji，纯文本格式：`时间：… / 地点：… / 种子：…`。`selfie-v5.py` 纯生图输出到 stdout → `selfie.sh`（统一入口，改一行切版本）管道转 `feishu_sender.py` 分三气泡发飞书 → stdout 为空（cron 不再投递）。手动出图时用 `send_message` 工具连发三个气泡
|- **cron.wrap_response=false 去掉管理提示** — 在韩梅梅 profile 的 config.yaml 中设置 `cron.wrap_response: false`，cron 不再追加 "To stop or manage this job..." 管理提示和 "Cronjob Response:" header。输出为纯脚本内容（`hermes config set cron.wrap_response false --profile hanmeimei`）
|- **selfie-v5.py 职责边界：纯生图，不含发送逻辑** — 脚本只管生成图片 + stdout 输出结构化数据。飞书 API 调用由独立的 `feishu_sender.py` 处理，通过 `selfie.sh` 管道连接。改格式只改模板文件或 sender，不动生图脚本
|- **模板解析正则必须是 `.+` 不能是 `\w+`** — `selfie-v5.py` 解析 message-template.txt 的 section 名时，之前用 `^\[(\w+)\]$`，只匹配纯字母数字。section 名含冒号/空格（如 `[BUBBLE1: image]`）会被跳过，导致模板不生效，走硬编码回退格式。已改为 `^\[(.+)\]$`
|- **hermes venv 里 `$HOME` 被覆写** — 在 hermes-agent venv 下 `os.path.expanduser("~")` 返回 `/home/jarvis/.hermes/profiles/hanmeimei/home` 而非 `/home/jarvis`。所有 Python 脚本和 shell 脚本中的路径必须硬编码绝对路径，不能用 `~`、`expanduser`、或相对路径计算（`dirname $0` 往上推导也会出错）。影响 `feishu_sender.py`、`selfie-v5.py`、`selfie.sh`
|- **飞书凭证在 `platforms.feishu` 下** — config.yaml 里飞书 app_id/app_secret 不是顶层 `feishu`，而是 `platforms.feishu.app_id` 和 `platforms.feishu.app_secret`
|- **残留 selfie 进程会阻塞 ComfyUI 队列** — 如果 cron 触发的生图脚本没正常退出（路径错误、v6 bug 等），旧进程占住 ComfyUI 后续所有任务排队超时。排查：`ps aux | grep selfie`，杀掉残留再重试。selfie.sh 在执行前应检查残留进程避免排队
- **selfie.sh 必须用 venv python** — 系统 python3 和 hermes venv 的 cffi 版本冲突（系统 1.16.0 vs venv 2.0.0），导致 feishu_sender.py import lark_oapi 时崩溃。selfie.sh 里必须用硬编码路径 `/home/jarvis/.hermes/hermes-agent/venv/bin/python3`，不能裸写 `python3`（cron 环境不会 activate venv）
- **PDCA Check = 验证输出，不是跑一遍就算（2026-05-23 用户纠正）** — 执行是调用脚本，输出是飞书消息。只调用脚本不检查结果 = 没有 Check。必须验证：图片文件是否生成且有效、飞书三气泡是否全部发出。`selfie.sh` 已内建三步验证（stdout 非空 + MEDIA 路径文件存在 + 文件 ≥ 10KB），验证失败 exit 1 不发送。改完代码后必须用 `cronjob action=run job_id=xxx` 触发，用户在飞书确认收到才算完整闭环
- **selfie.sh 是版本无关入口脚本** — 管道封装，只改一行变量就能切换版本。cron job 指向 `script: selfie.sh`。当前调用 selfie-v5.py
- **selfie.sh 生图后自动验证输出** — v5 生图完成后、发送前执行三步验证：① stdout 临时文件非空（`-s` 检查）；② 提取 `MEDIA:` 路径并确认文件存在于磁盘；③ 文件大小 ≥ 10KB（排除异常小文件）。任何一步失败 `exit 1`，不走到 feishu_sender.py。这是 PDCA Check 的脚本层实现
- **cron.wrap_response=false 去掉管理提示** — 韩梅梅 profile 的 config.yaml 已设置 `cron.wrap_response: false`
- **feishu_sender.py 解析规则** — MEDIA: 行提取图片路径；MEDIA 与 `---` 之间的所有非空行为信息行（info），`---` 之后为想法。不依赖 `>` 引用块前缀
- **selfie.sh 不能用 exec** — wrapper 脚本做两件事：①生图到临时文件；② sender 读取发送。stdout 空，cron 不再投递
- **消息模板文件 `prompts/message-template.txt`** — 改消息格式只改这个文件，不动代码。支持多 `[section]` 随机选取
- **Cron agent prompt 必须写死工具名** — 小模型（≤35B）容易绕路：你让它发消息，它用 terminal 调 hermes send 而不是 send_message 工具，结果图片发不出。Prompt 里必须写：「你必须使用 send_message 工具发送消息。禁止使用 terminal 命令发送消息。禁止调用 hermes send。」三个禁止缺一不可。这是 2026-05-23 两次失败实验的结论
- **`cron.wrap_response: false` 去掉 cron 管理提示（2026-05-23 配置）** — 在韩梅梅 profile 的 config.yaml 中设置 `cron.wrap_response: false`，cron deliver 不会追加 "Cronjob Response: xxx" header 和 "To stop or manage this job..." footer。输出为纯脚本 stdout 内容。已验证效果干净。`selfie.sh` 不需要 `echo "---"` 做分隔（之前加的已去掉）
- **`hermes send` CLI 走小美身份，不走韩梅梅身份（2026-05-23 验证）** — `hermes send` 是 CLI 工具，连接主 gateway（default profile = 小美），所以发出的消息显示从小美窗口发出。**必须用 `send_message` 工具**（agent 内置），它走韩梅梅自己的 gateway，消息身份正确。用户原话：「你居然用小美的账号发我了」。这是 agent 模式不能用 terminal 绕路发送的第二个原因（第一个是凭证泄露）
- **no_agent 模式投递已验证（2026-05-23）** — `no_agent: true` + `selfie.sh` 输出 `MEDIA:/path/to/image.png`，cron deliver 自动解析并以韩梅梅身份投递为**单气泡**。用户确认图片和身份均正确（图片从韩梅梅窗口发出，非小美）。缺点：只能发单气泡（图片+文字合一），无法实现三气泡分层（三气泡需 agent 模式 + send_message 工具，但当前小模型 tool-calling 不稳定）
- **飞书排版限制** — 飞书 post 消息不支持字号（font_size / text_size），只有卡片（interactive）的富文本组件支持 `text_size`。可用 `>` 引用块做视觉层级，`---` 做分隔线
- **hermes venv 里 `$HOME` 被覆写** — `os.path.expanduser("~")` 返回 `/home/jarvis/.hermes/profiles/hanmeimei/home` 而非 `/home/jarvis`。所有 Python/Shell 脚本中的路径必须硬编码绝对路径，不能用 `~`、`expanduser`、或相对路径计算。影响 `feishu_sender.py`、`selfie-v5.py`、`selfie.sh`
- **飞书凭证在 `platforms.feishu` 下** — config.yaml 里飞书 app_id/app_secret 在 `platforms.feishu.app_id` 和 `platforms.feishu.app_secret`，不是顶层 `feishu`
- **飞书 lark_oapi 图片上传 image_type 必须用 'message'** — `CreateImageRequestBody.builder().image_type('message')`，不能用 `'image'`（会报 code=234001 Invalid request param）。这是 2026-05-23 cron agent 调试时发现的 SDK 坑。如果未来需要在脚本中直接调 lark_oapi 上传图片，记住这一点
- **Cron agent 模式安全：不要让模型在 terminal 命令中拼接 API 凭证** — qwen3.6-35b 在调试图片发送时把飞书 `app_id`/`app_secret` 明文写进 terminal 命令，永久留存在 session DB 中。Cron prompt 应避免让模型直接操作需要凭证的 API，改用 Hermes 内置的 `send_message` 工具（自动处理认证）
- **Session 日志可验证投递结果** — 用户问"图发了吗"时，用 `session_search(query="写真 MEDIA selfie", sort="newest")` 找到对应 cron session，然后 scroll 进去查看完整工具调用链（terminal/send_message 的参数和返回值），可以精确判断图片是否成功发出。比翻飞书聊天记录更可靠
- **三气泡发送（cron no_agent 模式）** — `feishu_sender.py` 读取 selfie-v5.py 的 stdout，解析后分三气泡发送到飞书。**顺序：①图片 → ②描述（时间/地点/种子，纯文本无emoji无引用标记）→ ③想法**。`selfie-v5.py` 保持纯净不碰平台 API
- **图片元数据格式** — ComfyUI 输出的是 JSON 工作流格式，不是 A1111 的 `parameters` 文本格式。上传 Civitai 需要额外转换。详见 [references/a1111-metadata-format.md](references/a1111-metadata-format.md)
- **DOE 实验验证提示词变量影响** — 要验证某个提示词变量（如光线时间词）是否影响出图，用 DOE 方法：固定种子 + 固定表情 + 固定所有参数，只变目标变量。创建多个 doe-*.txt 文件（对照组无变量 + 各实验组），用 `python selfie-v3.py -p prompts/doe-xxx.txt -e "gentle smile" -s 123456789` 逐组跑。注意文件名带种子，同名种子会覆盖，所以 DOE 输出文件名可能重复（需要手动区分或改时间戳）
- **DOE 已验证：时间/光线提示词对出图有显著影响** — 对照组（无时间词）vs morning/evening/midnight 实验组对比，光线氛围明显不同。这验证了 v3 场景文件中按时段配置光线描述的设计是有意义的，不是摆设
- **v3 时间+日期自动注入（2026-05-21 新增）** — `get_time_description()` 自动根据当前月份生成季节感（如 `late spring season`）+ 根据小时生成精确时间词（如 `bright late morning light, early summer morning at 11am`），注入正向提示词。效果：同一天不同时段出图光线氛围自动不同，不需要手动配。位置在表情之后、场景光线之前
- **提示词精简原则：正面和负面规则不同！** — 负面提示词适用"同类只保留一个"：用户说"太多了也会导致图片怪异"，负面从 40+ 精简到 18 个。但**正面带权重的皮肤词不可合并**：`(very pale porcelain white skin:1.3)` + `(fair snow white body:1.2)` 各自带独立权重引导模型，合并成 `(pale porcelain skin with rosy undertone:1.3)` 实测导致皮肤不够真实。皮肤正向必须保持工作流原始配方：8个词（2个带权重白肤词 + rosy undertone + pores + details + lip color + flawless + perfect skin），这是经过验证的最佳组合，不要试图"优化"
- **负面手部词保留4个维度** — `(mutated hands:1.3)` 管变异、`(extra fingers:1.3)` 管多指、`(missing fingers:1.2)` 管少指、`(poorly drawn hands:1.2)` 管整体画得差。这4个是不同维度的约束，不属同类重复，不能砍。砍掉 poorly drawn → 手指变形明显回升
- **基础服装词必须在 wearing 子句里，且需要权重** — `bra` 和 `(round neck t-shirt:1.3)` 必须写在 `build_final_positive` 的 wearing 拼接中，不能放在 base.txt 正向提示词里。放 base.txt 里会被场景 outfit 的 `wearing xxx` 覆盖掉，模型看不到。**round neck t-shirt 不加权时只有约1/3概率出现，加到1.3后稳定出现在每张图**
- **负面词不能过度精简** — v4 曾"同类负面词只保留一个"砍掉大量负面词，导致皮肤质感下降（对比 v0 回退验证）。v0 的完整负面词列表（tanned/dark/yellow skin, freckles/moles/blemishes, airbrushed/oversmoothed, bad proportions/disfigured 等）对皮肤质感至关重要，已全部补回 base.txt。**教训：精简负面词前必须 A/B 对比测试，不能凭直觉砍**
- **场景文件添加 [negative] section 覆盖 base** — v5.8 起每个场景文件（bedroom/boulevard/cafe/library/rooftop/park/travel）末尾添加了 `[negative]` section，包含 `(nsfw:1.8),(nude:1.5)`。base.txt 已移除 nsfw/nude，由场景级 negative 接管。这样 nude 模式可以单独控制自己的负面词（去掉 nsfw/nude），非 nude 场景统一有防裸体兜底
- **所有场景 outfit 行追加通用配饰** — necklace、earrings、bracelet 作为基础配饰添加到每个 outfit 行，保持角色装饰一致性
- **消息格式规范** — 信息行纯文本，无引用标记（`>`）无 emoji。每行一个要素：时间、地点、种子。改格式只改 `message-template.txt`，不动代码
- **park.txt 和 travel.txt 已补齐（2026-05-24）** — 之前 ROUTINES 引用了 park/travel 场景但没有对应提示词文件，导致无 outfit → 裸体风险。已创建完整的 4季×6时段 场景文件。新增场景时必须同步创建 prompts/{scene}.txt，不能只在 ROUTINES 里加条目（HandRefiner+control_sd15_inpaint_depth_hand，**张阳 2026-05-23 确认效果比 v4 好**），cron 和手动出图统一使用 v5。selfie-v4.py 是种子池版（备选）。selfie.py（v0）是旧生产版，已退役。
- **批量出图反馈** — 种子号和图要一起发，便于用户识别和挑选好种子加入 good-seeds.txt。
- **防裸体配方（v3.3 验证通过）** — 三层防御：
  1. base.txt 正向：`fully clothed`（通用约束）
  2. build_final_positive wearing 子句：`wearing bra, round neck t-shirt, {场景outfit}`（基础内衣+T恤必须在 wearing 里，不能放 base.txt 前面，否则被场景 outfit 覆盖无效）
  3. base.txt 负向：`(nsfw:2.0), (nude:1.8), (naked:1.5), (nipples:1.5)` 四维度
  **肩部和乳沟可以露**，不加 `(bare shoulders)` 和 `(cleavage)` 负面词。场景 outfit 必须具体（如 `white blouse, long skirt, bra`），不能只写 `casual outfit`，太模糊容易跑偏出裸体
  **bra 提示词对防裸体非常有效**（用户原话），实测30张稳定性测试验证
- **精简后必须多图验证** — 单张看不出退化，至少出 3-4 张图才能发现稳定性问题
- **多图发送飞书限制** — 飞书消息中嵌入多个 MEDIA: 标签时，用户可能只收到第一张。必须用 `send_message` 逐张发送（一条消息一张图）
- **出图后直接发给用户，不做视觉审查** — 用户明确要求"不要审查，直接发"。不要对生成的图片做 vision_analyze 然后转述文字描述，直接 MEDIA: 发送。用户自己判断效果
- **技能调试验证流程** — 改完技能后，必须触发 cron（`cronjob action=run job_id=xxx`）让用户在飞书看到实际效果，用户确认才算成功。不要自己判断"应该没问题"
- **技能调试时保持聚焦** — 用户提醒："我们要知道我们在调试技能。我们的目的是优化技能。"改文件后要系统更新 SKILL.md，不要零散操作后忘了更新文档
- **用户说"图片没收到"时直接重发** — 这是投递失败，不是歧义。不要去翻 session history 询问"哪张图"。直接找到最近生成的图（`ls -t outputs/*.png | head -1`），重新带上 MEDIA: 标签发送即可。用户说"不对"说明你在浪费时间猜而不是行动
- **工作方法论（张阳教导）** — 三大思维方法：① PDCA — Check = 验证实际输出不是假设成功，Act = 根据结果改进；② SIPOC — 分析流程看全链路（Suppliers→Inputs→Process→Outputs→Customers），任何一环断了后面全白费；③ 风险思维 — 执行前先想会出什么问题提前设防，踩过的坑用自动化设防

## 消息格式

发送图片时的消息从模板文件 `prompts/message-template.txt` 读取，脚本随机选一个 `[section]`。

**模板变量**：`{greeting}`, `{scene_cn}`, `{season_cn}`, `{time}`, `{weather_emoji}`, `{thought}`, `{seed}`

**修改消息格式**：只改 `message-template.txt`，不碰代码。加新 `[section]` 或改现有段落即可。

**数据来源**：
- greeting → GREETINGS 字典（按时段分组）
- scene_cn → SCENE_NAMES 字典（bedroom→卧室 等）
- thought → THOUGHTS 字典（按场景分组，每个场景5条）
- weather_emoji → WEATHER_EMOJI 字典
- seed → 实际使用的种子值

## 消息发送系统

### 架构（三气泡）

```
selfie-v5.py (生图, stdout) → selfie.sh (管道) → feishu_sender.py (三气泡发送)
```

- `selfie-v5.py`：纯生图，stdout 输出结构化文本（MEDIA: + 引用块 + 想法）
- `selfie.sh`：捕获 stdout 到临时文件，传给 `feishu_sender.py`
- `feishu_sender.py`：解析输入，分三个气泡调 lark_oapi 发飞书（①图片→②引用块→③想法）

**单气泡模板（no_agent cron 回退模式）：**
```
[default]
{image}
时间：{time_full}
地点：{scene_cn}
种子：{seed}
---
{thought}
```

**三气泡 cron 发送（当前使用，feishu_sender.py）：**
`selfie.sh` → `selfie-v5.py`（生图，输出到临时文件）→ `feishu_sender.py`（读临时文件，调 lark_oapi 分三气泡发送）→ stdout 空。
1. 气泡1（图片）：上传到飞书并发送
2. 气泡2（描述）：时间/地点/种子（纯文本，无 emoji 和引用标记）
3. 气泡3（想法）：想法文字

**feishu_sender.py 解析规则：** MEDIA: 行提取图片路径；MEDIA 与 `---` 之间的所有非空行为信息行（info），`---` 之后为想法。不再依赖 `>` 引用块前缀。

**三气泡手动发送（agent 交互模式，用 send_message 工具）：**

**可用变量：**
| 变量 | 内容 | 示例 |
|------|------|------|
| `{image}` | MEDIA:路径 | `MEDIA:/path/to/output.png` |
| `{time_full}` | 完整时间戳 | `2026-05-24 09:23:33` |
| `{scene_cn}` | 场景中文名 | `咖啡馆` |
| `{seed}` | 种子号 | `86522080` |
| `{thought}` | 随机想法 | `窗边的位置刚好有空位` |

**场景中文名映射（SCENE_NAMES）：** bedroom=卧室, boulevard=林荫道, cafe=咖啡馆, library=图书馆, rooftop=天台, park=公园, travel=旅行途中

**场景想法池（THOUGHTS）：** 每个场景 5 条想法，随机选一条。见代码中的 THOUGHTS 字典。

**改格式只改模板文件，不改代码。**

## 参考文档索引

| 主题 | 内容 | 路径 |
|------|------|------|
| v6 场景选择（已删除，概念保留） | LIFE_STATES 分层路由表：生活状态→场景，时段匹配逻辑，跨午夜处理 | [references/v6-scene-selection.md](references/v6-scene-selection.md) |
| 定时任务配置 | cron 架构、依赖、调试流程、常见问题 | [references/cron-setup.md](references/cron-setup.md) |
| 飞书三气泡发送器 | feishu_sender.py 独立发送层，直接调 lark_oapi | [scripts/feishu_sender.py](scripts/feishu_sender.py) |
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

**⚠️ `git clone` 直连超时**（2026-05-23 验证）— 服务器无法直连 GitHub，`git clone` 必然超时。必须用 `gh api` 推送。

**推送方法（gh api）：**
```bash
# 用 Python + gh api 推送（排除 outputs/ 目录）
# 1. gh api repos/normdist-ai/skills/git/ref/heads/main → 获取 base SHA
# 2. 遍历本地文件（排除 .git/__pycache__/outputs），base64 编码
# 3. gh api repos/normdist-ai/skills/git/blobs --input - → 创建 blob（stdin 传 JSON，避免 arg 长度限制）
# 4. gh api repos/normdist-ai/skills/git/trees → 创建 tree
# 5. gh api repos/normdist-ai/skills/git/commits → 创建 commit
# 6. gh api -X PATCH repos/normdist-ai/skills/git/refs/heads/main → 更新 ref
```

**关键坑：**
- `gh api ... -f content=<base64>` 会超 arg 长度限制（图片文件 > 2MB）。必须用 `--input -` + stdin 传 JSON
- 排除 `outputs/` 目录（460+ 图片文件，~900MB）
- gh CLI 认证：`gh auth status` 确认已登录（normdist-ai 账号）
- GITHUB_TOKEN 存在 `profiles/hanmeimei/.env`

**凭证管理规范：**
- Token/API Key → `profiles/hanmeimei/.env`（600 权限，不入 git）
- 账号元信息（用户名、仓库 URL）→ fact_store（只记"有什么账号"，不存密钥）
- 平台配置（飞书等）→ config.yaml

# ⚠️ 本地技能目录不是 git repo，不要在本地 git init

## 路线图

| Phase | 状态 | 内容 |
|-------|------|------|
| Phase 1 | ✅ | 图片生成、FaceID面部一致性 |
| Phase 1.5 | ✅ | 三气泡 cron 方案定稿：`selfie-v5.py`（纯生图）→ `selfie.sh`（统一入口，改一行切版本）→ `feishu_sender.py`（三气泡发送：①图片→②信息→③想法，纯文本无引用标记无emoji）；cron no_agent + wrap_response=false；hermes venv 里 $HOME 被覆写已规避；手动出图用 send_message 工具 |
| Phase 1.6 | 🗑️已删除 | v6 场景选择架构（LIFE_STATES 分层）。因路径计算 bug 和工作流文件名不匹配反复出错，2026-05-23 用户决定删除。概念保留在 `references/v6-scene-selection.md` 供未来重写 |
| Phase 2 | ⏳ | LoRA训练 |
| Phase 3 | 🔄 | 视频生成（Wan2.1 I2V） |
| Phase 4 | 📋 | 语音合成 → 数字人 |
