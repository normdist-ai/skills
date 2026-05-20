---
name: hanmeimei-avatar
description: |
  韩梅梅形象生成技能 — 用 ComfyUI 生成韩梅梅的 AI 写真照片和未来的语音视频。
  保持面部一致性、写实风格、超白皙肌肤。
  当用户说"给我发张照片"、"出张图"、"看看你"、"你的照片"、"勾搭我"时触发。
  调用 comfyui 技能执行实际生成。
metadata:
  author: 韩梅梅
  version: "2.6.0"
  version_date: "2026-05-21"
  version_changelog: "selfie-v2.py 成为默认自拍脚本；新增笑容等级控制；优化多人脸约束；添加 nsfw 反向约束"
  roadmap: "图片✅ → LoRA训练(暂缓) → 视频生成(当前目标) → 语音合成 → 数字人"
  architecture: "分层架构：photo.py → comfyui_client.py → comfyui/run_workflow.py"
---

# 韩梅梅形象生成

## 架构说明

```
scripts/photo.py (默认入口)
    ↓ 读取
workflows/*.json (工作流文件)
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
├── workflows/                  # 工作流文件
│   ├── default.json            # 默认工作流（含 FaceID）
│   ├── faceid.json             # FaceID 工作流模板
│   └── base.json               # 基础工作流（无 FaceID）
├── scripts/
│   ├── photo.py                # 默认入口
│   ├── selfie-v2.py            # ✅ 自拍入口（表情控制）
│   ├── selfie.py               # 自拍入口（旧版）
│   └── comfyui_client.py       # comfyui 技能客户端
├── assets/faces/               # 脸部参考图片
└── outputs/                    # 输出目录
```

## 快速开始

```bash
# 默认生成
python scripts/photo.py

# 指定工作流和种子
python scripts/photo.py --workflow default --seed 123456

# 自拍（四维环境感知 + 笑容等级）
python scripts/selfie-v2.py --smile-level 4

# 自定义表情
python scripts/selfie-v2.py --expression "big grin, wide toothy smile, laughing joyfully, showing teeth"
```

> 📖 详细参数说明见 [references/skill-details.md](references/skill-details.md)

## 核心参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 模型 | ChilloutMix-Ni | SD1.5 写实模型 |
| CFG | **4.0** | 表情控制最佳值 |
| 采样器 | **euler** + normal | 避免塑料感 |
| FaceID 权重 | weight_faceidv2 = **0.80** | 表情控制最佳平衡点 |
| 表情权重 | **1.2** | 配合 FaceID 权重使用 |

> 📖 完整参数配置见 [references/skill-details.md](references/skill-details.md)

## 笑容等级

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
- **表情权重 1.2** — 配合 weight_faceidv2=0.80 使用，保持面部特征同时产生明显笑容
- **batch_size 必须为 1** — 多图生成会导致 FaceID 失效
- **避免紧身服装词** — `zentai`、`bodysuit`、`full body suit` 等词在模型中被理解为类似裸体效果
- **反向提示词开头不能有排除关键词** — 排除词应加在中间并提高权重（如 `(nude:1.5)`）
- **种子可复现性** — 相同种子 + 相同参数会生成完全相同的图片
- **使用 selfie-v2.py 进行自拍** — 支持笑容等级控制和表情自定义

## 参考文档

| 文档 | 内容 | 路径 |
|------|------|------|
| 技能详细文档 | 参数配置、脚本说明、安全规则 | [references/skill-details.md](references/skill-details.md) |
| 提示词指南 | 正向/反向提示词、穿搭参考 | [references/prompt-guides.md](references/prompt-guides.md) |
| 工作流指南 | 两步法、Seed模板、参数配置 | [references/workflow-guides.md](references/workflow-guides.md) |
| 季节衣橱 | 四季穿搭、天气修正 | [references/seasonal-wardrobe.md](references/seasonal-wardrobe.md) |
| FaceID 一致性研究 | 脸型一致性控制方法 | [references/face-consistency-research.md](references/face-consistency-research.md) |
| 好种子列表 | 经过验证的种子值 | [references/good-seeds.md](references/good-seeds.md) |

## 已知限制

- **手部变形**：AI绘画通病，优先用 waist up 构图避开
- **SD1.5 服装控制力**：FaceID模式下CFG建议 3.5-4.0
- **SDXL 不兼容 FaceID**：仅支持 SD1.5 模型
- **表情控制需要平衡**：需要明显笑容时，使用 selfie-v2.py 并调整 FaceID 参数

## 路线图

| Phase | 状态 | 内容 |
|-------|------|------|
| Phase 1 | ✅ | 图片生成、FaceID面部一致性 |
| Phase 2 | ⏳ | LoRA训练 |
| Phase 3 | 🔄 | 视频生成（Wan2.1 I2V） |
| Phase 4 | 📋 | 语音合成 → 数字人 |
