# 综合排名参考数据

> **注意**: 排名数据随时间变化，仅供参考。搜索时应获取最新数据。

---

## OpenCompass 综合排名 (2026-03)

| 排名 | 模型 | 综合得分 | 类型 |
|------|------|---------|------|
| 1 | Gemini-3-Pro-Preview | 81.3 | 闭源 |
| 2 | GLM-5 | 79.0 | 开源 |
| 3 | GPT-5-2025-08-07 | 78.8 | 闭源 |
| 4 | Qwen3.5-397B-A17B | 78.4 | 开源 |
| 5 | Kimi-K2.5 | 78.2 | 开源 |
| 6 | DeepSeek-V3.2-Speciale | 78.2 | 开源 |
| 7 | GLM-4.7 | 77.6 | 开源 |
| 8 | Step-3.5-Flash | 76.9 | 开源 |
| 9 | DeepSeek-V3.2 | 75.3 | 开源 |
| 10 | Kimi-K2-Thinking | 75.3 | 开源 |

### OpenCompass 各维度 TOP 5

**IFEval (指令遵循)**:

| 排名 | 模型 | 得分 |
|------|------|------|
| 1 | GPT-5 | 94.6 |
| 2 | Kimi-K2.5 | 93.9 |
| 3 | GLM-5 | 93.2 |
| 4 | Step-3.5-Flash | 93.2 |
| 5 | Gemini-3 | 92.8 |

**MMLU-Pro (知识能力)**:

| 排名 | 模型 | 得分 |
|------|------|------|
| 1 | Gemini-3 | 89.3 |
| 2 | Qwen3.5-397B | 87.6 |
| 3 | Kimi-K2.5 | 86.2 |
| 4 | GPT-5 | 86.2 |
| 5 | GLM-5 | 85.2 |

**LiveCodeBench (代码能力)**:

| 排名 | 模型 | 得分 |
|------|------|------|
| 1 | DeepSeek-V3.2-Speciale | 96.0 |
| 2 | GLM-5 | 95.8 |
| 3 | Step-3.5-Flash | 95.7 |
| 4 | GLM-4.7 | 95.4 |
| 5 | Kimi-K2.5 | 91.9 |

---

## SuperCLUE 中文综合排名 (2025年度, 2026-02发布)

| 排名 | 模型 | 综合得分 | 类型 |
|------|------|---------|------|
| 1 | Claude-Opus-4.5-Reasoning | 68.25 | 闭源 |
| 2 | Gemini-3-Pro-Preview | 65.59 | 闭源 |
| 3 | GPT-5.2 (high) | 64.32 | 闭源 |
| 4 | Kimi-K2.5-Thinking | 61.50 | 开源 |
| 5 | Qwen3-Max-Thinking | 60.61 | 闭源 |

### SuperCLUE 各维度 TOP 3

**代码生成**:

| 排名 | 模型 | 得分 |
|------|------|------|
| 1 | Kimi-K2.5-Thinking | 53.33 |
| 2 | GPT-5.2 | — |
| 3 | Gemini-3-Pro | — |

**数学推理**:

| 排名 | 模型 | 得分 |
|------|------|------|
| 1 | Qwen3-Max-Thinking | 80.87 |
| 1 | Gemini-3-Pro-Preview | 80.87 (并列) |
| 3 | Claude-Opus-4.5-Reasoning | — |

**关键发现**:
- 国内开源模型 TOP 5 全部来自中国 (Kimi, Qwen, DeepSeek, GLM, Step)
- 推理能力 (数学/科学) 海内外整体对齐
- 国内代码生成、智能体任务更优
- 海外精确指令遵循、幻觉控制领先

---

## C-Eval 中文知识理解排名 (2026-04)

| 排名 | 模型 | 得分 | 类型 |
|------|------|------|------|
| 1 | Qwen3-Max-Thinking | 93.70 | 闭源 |
| 2 | Qwen 3.6 Plus Preview | 93.30 | 闭源 |
| 3 | Qwen3.5-397B-A17B | 93.00 | 开源 |
| 4 | Hunyuan-T1 | 91.80 | 闭源 |
| 5 | Qwen3.6-27B | 91.40 | 开源 |
| 6 | Qwen3.5-27B | 90.50 | 开源 |
| 7 | Qwen3.6-35B-A3B | 90.00 | 开源 |

---

## Chatbot Arena ELO 排名 (2026-04)

| 排名 | 模型 | ELO得分 | 投票数 |
|------|------|---------|--------|
| 1 | GPT-5 | 1350+ | 50K+ |
| 2 | Claude Opus 4.7 | 1340+ | 40K+ |
| 3 | Gemini 3 Pro | 1330+ | 30K+ |

## Artificial Analysis Intelligence Index (2026-04)

| 排名 | 模型 | 指数 | 类型 |
|------|------|------|------|
| 1 | GPT-5 | 58 | 闭源 |
| 12 | Qwen3.6-Max-Preview | 52 | 闭源 |

---

## 数据来源

| 平台 | 网址 | 说明 |
|------|------|------|
| OpenCompass | https://opencompass.readthedocs.io | 综合评测，覆盖主流模型，中文评测权威 |
| SuperCLUE | https://www.cluebenchmarks.com | 中文大模型综合性评测基准，独立第三方 |
| C-Eval | https://cevalbenchmark.com | 中文多学科知识评测 |
| DataLearner | https://datalearner.com/benchmarks | C-Eval等榜单实时排名 |
| Chatbot Arena | https://lmsys.org | 用户偏好投票排名 |
| Artificial Analysis | https://artificialanalysis.ai | 多维度对比，含速度/价格 |
| FlagEval | https://flageval.baai.ac.cn | 智源研究院评测平台，含具身智能 |
