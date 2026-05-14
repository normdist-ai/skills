# 常见模型评测数据参考

> **最后更新**: 2026-05-01
> **注意**: 以下数据仅供参考，实际得分以搜索到的最新数据为准。数据来源标注在各模型下方。
> **置信度标识**: ✅ 官方/已验证 | ⚠️ 官方声称/未独立验证 | 🔲 未披露

---

## DeepSeek-V4-Pro (DeepSeek, 2026-04-24)

| 基准测试 | 得分 | 置信度 | 说明 |
|---------|------|--------|------|
| MMLU-Pro | 85.0 | ⚠️ | 知识理解 |
| GPQA-Diamond | 79.9 | ⚠️ | 高阶推理 |
| SWE-bench Verified | 80.6 | ⚠️ | 代码能力 |
| SWE-bench Pro | 55.4 | ⚠️ | 代码能力(进阶) |
| Terminal-Bench 2.0 | 67.9 | ⚠️ | 终端任务 |
| LiveCodeBench | 93.5 | ⚠️ | 实时代码 |
| Codeforces Rating | 3206 | ⚠️ | 竞赛代码 |
| MRCR 1M | 83.5 | ⚠️ | 长文本理解 |

**架构**: 1.6T总参数/49B激活, MoE, CSA+HCA混合注意力, 1M上下文
**部署**: V4-Flash(284B/13B) Q4量化可双RTX 5090运行; V4-Pro需多GPU
**来源**: https://github.com/deepseek-ai/DeepSeek-V4

---

## DeepSeek-V4-Flash (DeepSeek, 2026-04-24)

| 基准测试 | 得分 | 置信度 | 说明 |
|---------|------|--------|------|
| MMLU-Pro | ~80 | ⚠️ | 知识理解 |
| GPQA-Diamond | ~72 | ⚠️ | 高阶推理 |
| HumanEval | ~90 | ⚠️ | 代码生成 |

**架构**: 284B总参数/13B激活, MoE, 1M上下文
**部署**: Q4量化~22GB, 双RTX 3090/4090可运行
**来源**: https://github.com/deepseek-ai/DeepSeek-V4

---

## GPT-5.4 (OpenAI, 2026-03)

| 基准测试 | 得分 | 置信度 | 说明 |
|---------|------|--------|------|
| MMLU | 90 | ✅ | 知识理解 |
| MMLU-Pro | 89.2 | ✅ | 知识理解(进阶) |
| GPQA-Diamond | 92.8 | ✅ | 高阶推理 |
| HumanEval+ | 93.7 | ✅ | 代码生成 |
| SWE-bench Verified | 58.7 | ✅ | 代码能力 |
| SWE-bench Pro | 57.7 | ✅ | 代码能力(进阶) |
| MATH-500 | 99 | ✅ | 数学推理 |
| AIME 2025 | 99 | ✅ | 数学竞赛 |
| HMMT 2025 | 97 | ✅ | 数学竞赛 |
| USAMO 2026 | 95.2 | ✅ | 数学竞赛 |
| ARC-AGI-2 | 73.3 | ✅ | 抽象推理 |
| OSWorld | 75 | ✅ | 桌面自动化 |
| BrowseComp | 89.3 | ✅ | 长文档搜索 |
| MuSR | 94 | ✅ | 多步推理 |
| MRCRv2 | 97 | ✅ | 长文本理解 |

**架构**: 闭源, Reasoning模型, 1.05M上下文
**部署**: API调用, $2.50/$15 per 1M tokens
**来源**: https://openai.com/index/introducing-gpt-5

---

## GPT-5.5 (OpenAI, 2026-04-23)

| 基准测试 | 得分 | 置信度 | 说明 |
|---------|------|--------|------|
| SWE-bench Verified | 84 | ⚠️ | 代码能力 |
| SWE-bench Pro | 84 | ⚠️ | 代码能力(进阶) |
| AIME 2025 | 99 | ⚠️ | 数学竞赛 |

**架构**: 闭源, Reasoning模型
**部署**: API调用, $5/$30 per 1M tokens
**来源**: https://openai.com

---

## Claude Opus 4.7 (Anthropic, 2026-04-16)

| 基准测试 | 得分 | 置信度 | 说明 |
|---------|------|--------|------|
| MMLU | 91.3 | ✅ | 知识理解 |
| GPQA-Diamond | 94.2 | ✅ | 高阶推理 |
| SWE-bench Verified | 87.6 | ✅ | 代码能力 |
| SWE-bench Pro | 64.3 | ✅ | 代码能力(进阶) |
| Terminal-Bench 2.0 | 69.4 | ✅ | 终端任务 |
| CursorBench | 70 | ✅ | IDE编码 |
| HumanEval | 94 | ✅ | 代码生成 |
| AIME 2024 | 99.8 | ✅ | 数学竞赛 |
| ARC-AGI | 75.2 | ✅ | 抽象推理 |
| MCP-Atlas | 77.3 | ✅ | 工具调用 |
| OSWorld-Verified | 78.0 | ✅ | 桌面自动化 |
| XBOW视觉测试 | 98.5 | ✅ | 视觉理解 |
| BrowseComp | 79.3 | ✅ | 长文档搜索 |
| Finance Agent v1.1 | 64.4 | ✅ | 金融智能体 |

**架构**: 闭源, 1M上下文, 高分辨率视觉(3.75MP), Auto Mode
**部署**: API调用, $5/$25 per 1M tokens; 新tokenizer可能增加1.0-1.35x token消耗
**来源**: https://www.anthropic.com/news/claude-opus-4-7

---

## Claude Opus 4.5 (Anthropic, 2025)

| 基准测试 | 得分 | 置信度 | 说明 |
|---------|------|--------|------|
| MMLU-Pro | 89.5 | ✅ | 知识理解 |
| GPQA-Diamond | 87.0 | ✅ | 高阶推理 |
| SWE-bench Verified | 80.9 | ✅ | 代码能力 |
| SWE-bench Pro | 57.1 | ✅ | 代码能力(进阶) |
| Terminal-Bench 2.0 | 59.3 | ✅ | 终端任务 |
| SkillsBench Avg5 | 45.3 | ✅ | 技能执行 |
| τ²-Bench | 91.6 | ✅ | 工具调用 |

**架构**: 闭源, API调用
**来源**: https://anthropic.com

---

## Gemini 3.1 Pro (Google, 2026-02-19)

| 基准测试 | 得分 | 置信度 | 说明 |
|---------|------|--------|------|
| MMLU | 93.8 | ✅ | 知识理解 |
| MMLU-Pro | 93.8 | ✅ | 知识理解(进阶) |
| GPQA-Diamond | 94.3 | ✅ | 高阶推理 |
| MATH | 89.4 | ✅ | 数学推理 |
| SWE-bench Verified | 80.6 | ✅ | 代码能力 |
| SWE-bench Pro | 54.2 | ✅ | 代码能力(进阶) |
| LiveCodeBench | 78.9 | ✅ | 实时代码 |
| LiveCodeBench Pro Elo | 2887 | ✅ | 代码竞赛 |
| Terminal-Bench 2.0 | 68.5 | ✅ | 终端任务 |
| ARC-AGI-2 | 77.1 | ✅ | 抽象推理 |
| BrowseComp | 85.9 | ✅ | 长文档搜索 |
| MCP-Atlas | 69.2 | ✅ | 工具调用 |
| SciCode | 59 | ✅ | 科学代码 |
| APEX-Agents | 33.5 | ✅ | 自主智能体 |

**架构**: 闭源, ~1T MoE, 1M上下文(2M Deep Think), 原生多模态(文/图/音/视频)
**部署**: API调用, $2/$12 per 1M tokens; >200K时$4/$18
**来源**: https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-1-pro/

---

## GLM-5 (智谱AI, 2026-02-11)

| 基准测试 | 得分 | 置信度 | 说明 |
|---------|------|--------|------|
| MMLU | 88 | ✅ | 知识理解 |
| MMLU-Pro | 82.0 | ✅ | 知识理解(进阶) |
| C-Eval | 92.1 | ✅ | 中文知识理解 |
| GPQA-Diamond | 86.0 | ✅ | 高阶推理 |
| HLE | 30.5 | ✅ | 复杂推理 |
| HLE (w/ Tools) | 50.4 | ✅ | 复杂推理(工具) |
| SWE-bench Verified | 77.8 | ✅ | 代码能力 |
| SWE-bench Multilingual | 73.3 | ✅ | 多语言代码 |
| Terminal-Bench 2.0 | 56.2 | ✅ | 终端任务 |
| AIME 2026 I | 92.7 | ✅ | 数学竞赛 |
| HMMT Nov. 2025 | 96.9 | ✅ | 数学竞赛 |
| MATH-500 | 97.4 | ✅ | 数学推理 |
| HumanEval | 97.0 | ✅ | 代码生成 |
| τ²-Bench | 89.7 | ✅ | 工具调用 |
| BrowseComp | 62.0 | ✅ | 长文档搜索 |
| BrowseComp (w/ CM) | 75.9 | ✅ | 长文档搜索(上下文管理) |
| MCP-Atlas | 67.8 | ✅ | 工具调用 |
| CyberGym | 43.2 | ✅ | 网络安全 |

**架构**: 744B总参数/40B激活, MoE, MLA+DSA, 200K上下文, 华为昇腾训练
**部署**: MIT开源, API $1.00/$3.20 per 1M tokens
**来源**: https://huggingface.co/zai-org/GLM-5

---

## GLM-4.7 (智谱AI, 2025-10)

| 基准测试 | 得分 | 置信度 | 说明 |
|---------|------|--------|------|
| MMLU-Pro | 84.3 | ✅ | 知识理解 |
| GPQA-Diamond | 85.7 | ✅ | 高阶推理 |
| SWE-bench Verified | 73.8 | ✅ | 代码能力 |
| Terminal-Bench 2.0 | 41.0 | ✅ | 终端任务 |
| HLE | 42.8 | ✅ | 复杂推理 |
| τ²-Bench | 87.4 | ✅ | 工具调用 |

**架构**: 355B, Transformer + 思考模式, 200K上下文
**部署**: 开源权重，需多GPU部署
**来源**: https://bigmodel.cn

---

## Kimi K2.5 (Moonshot AI, 2026-02-01)

| 基准测试 | 得分 | 置信度 | 说明 |
|---------|------|--------|------|
| MMLU-Pro | ~82 | ⚠️ | 知识理解 |
| GPQA-Diamond | 87.6 | ✅ | 高阶推理 |
| SWE-bench Verified | 76.8 | ✅ | 代码能力 |
| AIME 2025 | 96.1 | ✅ | 数学竞赛 |
| HMMT 2025 | 95.4 | ✅ | 数学竞赛 |
| HLE (w/ Tools) | 50.2 | ✅ | 复杂推理(工具) |
| BrowseComp | 60.6 | ✅ | 长文档搜索 |
| Terminal-Bench 2.0 | 50.8 | ✅ | 终端任务 |
| τ²-Bench | 80.2 | ✅ | 工具调用 |
| MCP-Atlas | 63.8 | ✅ | 工具调用 |
| MMMU-Pro | — | 🔲 | 多模态推理 |
| OCRBench | 92.3 | ✅ | 文档OCR |
| VideoMMMU | 86.6 | ✅ | 视频理解 |

**架构**: 1T总参数/32B激活, MoE(384专家/8激活), MLA, 256K上下文, 原生多模态
**部署**: 开源权重(Modified MIT), API $0.6/$3 per 1M tokens; Agent Swarm(最多100子智能体)
**来源**: https://www.kimi.com/blog/kimi-k2-5.html

---

## Qwen3.6-27B (Alibaba, 2026-04-22)

| 基准测试 | 得分 | 置信度 | 说明 |
|---------|------|--------|------|
| MMLU-Pro | 86.2 | ✅ | 知识理解 |
| MMLU-Redux | 93.5 | ✅ | 知识理解(修正版) |
| C-Eval | 91.4 | ✅ | 中文知识理解 |
| SuperGPQA | 66.0 | ✅ | 专业领域推理 |
| GPQA-Diamond | 87.8 | ✅ | 高阶推理 |
| HLE | 24.0 | ✅ | 复杂推理 |
| SWE-bench Verified | 77.2 | ✅ | 代码能力 |
| SWE-bench Pro | 53.5 | ✅ | 代码能力(进阶) |
| Terminal-Bench 2.0 | 59.3 | ✅ | 终端任务 |
| SkillsBench Avg5 | 48.2 | ✅ | 技能执行 |
| LiveCodeBench v6 | 83.9 | ✅ | 实时代码 |
| HMMT Feb 25 | 93.8 | ✅ | 数学竞赛 |
| AIME26 | 94.1 | ✅ | 数学竞赛 |
| MMMU | 82.9 | ✅ | 多模态推理 |
| MMStar | 81.4 | ✅ | 视觉问答 |

**架构**: 27B Dense, Hybrid Gated DeltaNet + Gated Attention (3:1), 262K上下文(1M YaRN扩展)
**部署**: Q4_K_M 量化 16.8GB, 单张 RTX 4090/5090 可运行
**来源**: https://qwen.ai/blog?id=qwen3.6-27b

---

## Qwen3.6-35B-A3B (Alibaba, 2026-04-15)

| 基准测试 | 得分 | 置信度 | 说明 |
|---------|------|--------|------|
| MMLU-Pro | 85.2 | ✅ | 知识理解 |
| MMLU-Redux | 93.3 | ✅ | 知识理解(修正版) |
| C-Eval | 90.0 | ✅ | 中文知识理解 |
| GPQA-Diamond | 86.0 | ✅ | 高阶推理 |
| HLE | 21.4 | ✅ | 复杂推理 |
| SWE-bench Verified | 73.4 | ✅ | 代码能力 |
| Terminal-Bench 2.0 | 51.5 | ✅ | 终端任务 |
| SkillsBench Avg5 | 28.7 | ✅ | 技能执行 |
| LiveCodeBench v6 | 80.4 | ✅ | 实时代码 |
| HMMT Feb 25 | 90.7 | ✅ | 数学竞赛 |
| AIME26 | 92.7 | ✅ | 数学竞赛 |
| MMMU | 81.7 | ✅ | 多模态推理 |

**架构**: 35B总参数/3B激活, MoE (256专家/8+1激活), 262K上下文
**部署**: Q4_K_M 量化 ~22GB, 16GB VRAM + RAM offload 可运行, RTX 3090 可达 101 tok/s
**来源**: https://qwen.ai/blog?id=qwen3.6-35b-a3b

---

## Qwen3.5-397B-A17B (Alibaba, 2025)

| 基准测试 | 得分 | 置信度 | 说明 |
|---------|------|--------|------|
| MMLU-Pro | 87.8 | ✅ | 知识理解 |
| GPQA-Diamond | 88.4 | ✅ | 高阶推理 |
| SWE-bench Verified | 76.2 | ✅ | 代码能力 |
| Terminal-Bench 2.0 | 52.5 | ✅ | 终端任务 |
| SkillsBench Avg5 | 30.0 | ✅ | 技能执行 |
| LiveCodeBench v6 | 83.6 | ✅ | 实时代码 |
| HMMT Feb 25 | 94.8 | ✅ | 数学竞赛 |

**架构**: 397B总参数/17B激活, MoE, 262K上下文
**部署**: BF16 权重 807GB, 需要多GPU部署
**来源**: https://qwen.ai/blog?id=qwen3.5

---

## Llama 4 Scout (Meta, 2025-04)

| 基准测试 | 得分 | 置信度 | 说明 |
|---------|------|--------|------|
| MMLU | 86.2 | ✅ | 知识理解 |
| GPQA-Diamond | 74.3 | ✅ | 高阶推理 |
| ARC-Challenge | 92.1 | ✅ | 科学推理 |
| BBH | 83.7 | ✅ | 多样化困难任务 |
| GSM8K | 94.8 | ✅ | 数学推理 |
| MATH | 61.2 | ✅ | 数学推理(进阶) |
| AIME 2025 | 42.1 | ✅ | 数学竞赛 |
| HumanEval | 84.1 | ✅ | 代码生成 |
| LiveCodeBench v5 | 38.2 | ✅ | 实时代码 |
| SWE-bench Lite | 31.4 | ✅ | 代码能力 |

**架构**: 109B总参数/17B激活, MoE(16专家/2激活), 10M上下文, 原生多模态(早期融合)
**部署**: INT4量化~55GB, 单张A10G可运行; Llama 4 Community License (MAU>7亿需申请)
**来源**: https://ai.meta.com/blog/llama-4/

---

## Llama 4 Maverick (Meta, 2025-04)

| 基准测试 | 得分 | 置信度 | 说明 |
|---------|------|--------|------|
| MMLU | 85.5 | ✅ | 知识理解 |
| MMLU-Pro | 81.2 | ✅ | 知识理解(进阶) |
| SWE-bench Verified | 76.8-80.8 | ⚠️ | 代码能力 |
| HumanEval | ~85 | ⚠️ | 代码生成 |

**架构**: 400B总参数/17B激活, MoE(128+1专家), 1M上下文, 原生多模态
**部署**: 4-bit量化~200GB(~4×H100), FP16~800GB(H200集群)
**来源**: https://ai.meta.com/blog/llama-4/

---

## Gemma 4-31B (Google)

| 基准测试 | 得分 | 置信度 | 说明 |
|---------|------|--------|------|
| MMLU-Pro | 85.2 | ✅ | 知识理解 |
| GPQA-Diamond | 84.3 | ✅ | 高阶推理 |
| SWE-bench Verified | 52.0 | ✅ | 代码能力 |
| Terminal-Bench 2.0 | 42.9 | ✅ | 终端任务 |

**架构**: 31B Dense, 开源
**来源**: https://ai.google.dev/gemma

---

## GLM-5.1 (智谱AI, 2026-04)

| 基准测试 | 得分 | 置信度 | 说明 |
|---------|------|--------|------|
| MMLU-Pro | ~83 | ⚠️ | 知识理解 |
| GPQA-Diamond | ~87 | ⚠️ | 高阶推理 |
| SWE-bench Verified | ~78 | ⚠️ | 代码能力 |

**架构**: MoE, 智谱AI最新模型
**来源**: TRAE IDE 内置模型

---

## Kimi-K2.6 (Moonshot, 2026-04)

| 基准测试 | 得分 | 置信度 | 说明 |
|---------|------|--------|------|
| MMLU-Pro | ~82 | ⚠️ | 知识理解 |
| GPQA-Diamond | ~88 | ⚠️ | 高阶推理 |
| AIME | ~96 | ⚠️ | 数学竞赛 |

**架构**: MoE, Kimi K2.5 升级版
**来源**: TRAE IDE 内置模型

---

## Qwen3.6-Plus (阿里巴巴, 2026-04)

| 基准测试 | 得分 | 置信度 | 说明 |
|---------|------|--------|------|
| MMLU-Pro | ~87 | ⚠️ | 知识理解 |
| GPQA-Diamond | ~88 | ⚠️ | 高阶推理 |
| SWE-bench Verified | ~78 | ⚠️ | 代码能力 |

**架构**: MoE, Qwen3.6-27B 的 Plus 版本
**来源**: TRAE IDE 内置模型

---

## Doubao-Seed-2.0-Code (字节跳动, 2026)

| 基准测试 | 得分 | 置信度 | 说明 |
|---------|------|--------|------|
| HumanEval | ~92 | ⚠️ | 代码生成 |
| SWE-bench Verified | ~75 | ⚠️ | 代码能力 |

**架构**: 字节跳动代码专用模型
**来源**: TRAE IDE 内置模型

---

## MiniMax-M2.7 (MiniMax, 2026-04)

| 基准测试 | 得分 | 置信度 | 说明 |
|---------|------|--------|------|
| MMLU-Pro | ~84 | ⚠️ | 知识理解 |
| GPQA-Diamond | ~85 | ⚠️ | 高阶推理 |

**架构**: MiniMax 最新模型
**来源**: TRAE IDE 内置模型
