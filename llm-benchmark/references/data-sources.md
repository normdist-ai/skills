# 数据源与搜索策略

## 评测平台

| 平台 | 网址 | 特点 | 优先级 |
|------|------|------|--------|
| **OpenCompass** | opencompass.readthedocs.io | 综合评测，覆盖主流模型 | ⭐⭐⭐ |
| **BenchLM** | benchlm.ai | 8维度178项基准，实时更新 | ⭐⭐⭐ |
| **HuggingFace** | huggingface.co | 模型卡片官方评测数据 | ⭐⭐⭐ |
| **SuperCLUE** | cluebenchmarks.com | 中文大模型综合性评测基准，独立第三方 | ⭐⭐⭐ |
| **DataLearner** | datalearner.com/benchmarks | MMLU/C-Eval等榜单排名 | ⭐⭐ |
| **LLMDB** | llmdb.com/benchmarks | 多维度评测榜单 | ⭐⭐ |
| **C-Eval** | cevalbenchmark.com | 中文多学科知识评测 | ⭐⭐ |
| **FlagEval** | flageval.baai.ac.cn | 智源研究院评测平台，含具身智能 | ⭐⭐ |
| **Chatbot Arena** | lmsys.org | 用户偏好投票排名 | ⭐⭐ |
| **Artificial Analysis** | artificialanalysis.ai | 多维度对比，含速度/价格 | ⭐ |

## 搜索优先级

```
1. 官方评测平台 (BenchLM, OpenCompass)     → 数据最权威
2. 模型官方发布 (HuggingFace, 技术报告, 博客) → 数据最完整
3. 第三方评测汇总 (DataLearner, LLMDB)      → 数据最全面
```

## 搜索关键词模板

### 通用搜索
```
"{模型名} benchmark MMLU GPQA SWE-bench score"
"{模型名} 评测 得分 OpenCompass"
"{模型名} vs {对比模型} benchmark comparison"
```

### 中文评测搜索
```
"{模型名} SuperCLUE 评测 排名"
"{模型名} C-Eval 得分 中文"
"{模型名} OpenCompass 中文 排行榜"
"{模型名} 国产大模型 评测 对比"
"{模型名} FlagEval 评测 得分"
```

### 官方数据搜索
```
"{模型名} model card benchmark results"
"{模型名} 官方 评测 性能 技术报告"
"{模型名} site:huggingface.co"
"{模型名} site:qwen.ai" (或其他厂商域名)
```

### 特定维度搜索
```
"{模型名} SWE-bench score coding"
"{模型名} MMLU-Pro knowledge benchmark"
"{模型名} GPQA reasoning score"
```

## 数据整理格式

将收集的数据整理为统一 JSON 格式:

```json
{
  "cache_version": "1.0",
  "model": "Qwen3.6-27B",
  "provider": "Alibaba",
  "architecture": "Dense (Hybrid DeltaNet + Attention)",
  "parameters": "27B",
  "active_parameters": "27B",
  "context_length": "262K (1M with YaRN)",
  "release_date": "2026-04-22",
  "license": "Apache 2.0",
  "multimodal": true,
  "deploy": {
    "bf16_size": "55.6 GB",
    "q4_size": "16.8 GB",
    "min_gpu": "RTX 4090 (24GB)",
    "rec_gpu": "RTX 5090 / H100",
    "frameworks": ["SGLang >=0.5.10", "vLLM >=0.19.0", "llama.cpp"],
    "quantization": ["FP8", "Q4_K_M", "78 community quants"]
  },
  "benchmarks": {
    "coding_agent": {
      "SWE-bench Verified": 77.2,
      "SWE-bench Pro": 53.5,
      "Terminal-Bench 2.0": 59.3,
      "SkillsBench Avg5": 48.2,
      "LiveCodeBench v6": 83.9
    },
    "knowledge": {
      "MMLU-Pro": 86.2,
      "MMLU-Redux": 93.5,
      "SuperGPQA": 66.0,
      "C-Eval": 91.4
    },
    "stem_reasoning": {
      "GPQA Diamond": 87.8,
      "HLE": 24.0,
      "HMMT Feb 25": 93.8,
      "AIME26": 94.1
    },
    "vision_language": {
      "MMMU": 82.9,
      "MMStar": 81.4,
      "MathVista mini": 87.4
    },
    "long_context": {
      "MRCR 1M": null,
      "LongBench": null
    },
    "function_calling": {
      "BFCL v3": null,
      "MCP-Atlas": null,
      "τ²-Bench": null
    },
    "safety_trust": {
      "TruthfulQA": null,
      "HarmBench": null
    },
    "chinese": {
      "C-Eval": 91.4,
      "CMMLU": null,
      "SuperCLUE": null
    }
  },
  "source": "https://qwen.ai/blog?id=qwen3.6-27b",
  "retrieved_at": "2026-05-01"
}
```

## JSON Schema 校验

缓存写入前必须校验 JSON 格式，必填字段:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| cache_version | string | ✅ | 缓存格式版本，当前 "1.0" |
| model | string | ✅ | 模型名称 |
| provider | string | ✅ | 厂商 |
| architecture | string | ✅ | 架构描述 |
| parameters | string | ✅ | 参数规模 |
| context_length | string | ✅ | 上下文长度 |
| benchmarks | object | ✅ | 评测数据，至少包含一个维度 |
| source | string | ✅ | 数据来源 URL |
| retrieved_at | string | ✅ | 数据获取日期 (YYYY-MM-DD) |
| active_parameters | string | 可选 | MoE模型激活参数 |
| release_date | string | 可选 | 发布日期 |
| license | string | 可选 | 许可协议 |
| multimodal | boolean | 可选 | 是否多模态 |
| deploy | object | 可选 | 部署信息 |

**校验规则**:
- `benchmarks` 下每个维度的值必须是 number 或 null
- 得分范围: 0-100 (百分比制) 或 0-4000 (Elo 评分制，如 Codeforces)
- `retrieved_at` 必须是有效日期
- 超过30天的缓存数据建议重新验证

## 条件处理

| 情况 | 处理方式 |
|------|---------|
| 搜索无结果 | 换用模型别名搜索，或直接访问 HuggingFace Model Card |
| 数据来源冲突 | 优先采用官方数据，标注来源平台 |
| 模型不存在 | 明确告知用户，建议可能的正确名称 |
| 数据缺失 | 用 `N/A` 标注，**绝不猜测或编造数据** |
| 评测条件不同 | 在脚注中标注差异 (如 SWE-bench 的 agent scaffold 配置) |

## TRAE IDE 模型参考

> 来源: https://docs.trae.cn/ide/models

### TRAE 内置模型 (2026-05)

| 模型 | 厂商 | 说明 |
|------|------|------|
| Doubao-Seed-2.0-Code | 字节跳动 | 代码专用 |
| Doubao-Seed-1.8 | 字节跳动 | 通用 |
| Doubao-Seed-Code | 字节跳动 | 代码专用 |
| MiniMax-M2.7 | MiniMax | 通用 |
| MiniMax-M2.5 | MiniMax | 通用 |
| GLM-5.1 | 智谱AI | 通用 |
| GLM-5V-Turbo | 智谱AI | 多模态 |
| GLM-5 | 智谱AI | 通用 |
| DeepSeek-V3.1-Terminus | DeepSeek | 通用 |
| Kimi-K2.6 | Moonshot | 通用 |
| Kimi-K2.5 | Moonshot | 通用 |
| Qwen3.6-Plus | 阿里巴巴 | 通用 |
| Qwen3.5-Plus | 阿里巴巴 | 通用 |

### TRAE 支持的服务商

| 服务商 | 说明 |
|--------|------|
| AWS | Amazon Bedrock |
| Anthropic | Claude 系列模型 |
| OpenAI | GPT 系列模型 |
| Gemini | Google Gemini 系列模型 |
| xAI | Grok 系列模型 |
| OpenRouter | 多模型聚合平台 |
| Vercel AI Gateway | Vercel AI 网关 |
| Ollama Cloud | 本地模型云端部署 |
| MiniMax-CN / MiniMax-Global | MiniMax 国内/国际版 |
| Bigmodel / Bigmodel-plan | 智谱AI 开放平台 |
| Z.ai / Z.ai-plan | 字节跳动模型服务 |
| Kimi-CN / Kimi-Global | Moonshot 国内/国际版 |
| DeepSeek | DeepSeek API |
| 火山引擎 / 火山引擎 Plan | 字节跳动云服务 |
| 阿里云 | 阿里云模型服务 |
| 腾讯云 | 腾讯云模型服务 |
| 模力方舟 | 模力方舟模型服务 |
| 硅基流动 | 硅基流动模型服务 |
| PPIO | PPIO 模型服务 |
| Novita | Novita 模型服务 |
| BytePlus / BytePlus Plan | 字节跳动国际版 |
| Infinigence AI CN / Global | 无问芯穹 国内/国际版 |

**用途**: 
- 识别用户可能询问的模型名称变体 (如 "Kimi-K2.6" vs "Kimi K2.6")
- 确定模型厂商和服务商对应关系
- 补充模型别名搜索关键词

---

## OpenCode Zen 模型参考

> 来源: https://opencode.ai/docs/zh-cn/zen/

### OpenCode Zen 模型列表 (2026-05)

| 模型 | 模型 ID | 输入价格 ($/1M) | 输出价格 ($/1M) |
|------|---------|-----------------|-----------------|
| GPT 5.5 | gpt-5.5 | $5.00 | $30.00 |
| GPT 5.5 Pro | gpt-5.5-pro | $30.00 | $180.00 |
| GPT 5.4 | gpt-5.4 | $2.50 | $15.00 |
| GPT 5.4 Pro | gpt-5.4-pro | $30.00 | $180.00 |
| GPT 5.4 Mini | gpt-5.4-mini | $0.75 | $4.50 |
| GPT 5.4 Nano | gpt-5.4-nano | $0.20 | $1.25 |
| Claude Opus 4.7 | claude-opus-4-7 | $5.00 | $25.00 |
| Claude Opus 4.6 | claude-opus-4-6 | $5.00 | $25.00 |
| Claude Opus 4.5 | claude-opus-4-5 | $5.00 | $25.00 |
| Claude Sonnet 4.6 | claude-sonnet-4-6 | $3.00 | $15.00 |
| Claude Sonnet 4.5 | claude-sonnet-4-5 | $3.00 | $15.00 |
| Claude Haiku 4.5 | claude-haiku-4-5 | $1.00 | $5.00 |
| Gemini 3.1 Pro | gemini-3.1-pro | $2.00 | $12.00 |
| Gemini 3 Flash | gemini-3-flash | $0.50 | $3.00 |
| Qwen3.6 Plus | qwen3.6-plus | $0.50 | $3.00 |
| Qwen3.5 Plus | qwen3.5-plus | $0.20 | $1.20 |
| MiniMax M2.7 | minimax-m2.7 | $0.30 | $1.20 |
| MiniMax M2.5 | minimax-m2.5 | $0.30 | $1.20 |
| GLM 5.1 | glm-5.1 | $1.40 | $4.40 |
| GLM 5 | glm-5 | $1.00 | $3.20 |
| Kimi K2.6 | kimi-k2.6 | $0.95 | $4.00 |
| Kimi K2.5 | kimi-k2.5 | $0.60 | $3.00 |

### 免费模型 (限时)

| 模型 | 说明 |
|------|------|
| Big Pickle | 隐身模型，免费期间数据可能用于改进 |
| MiniMax M2.5 Free | 限时免费，数据可能用于改进 |
| Ling 2.6 Flash Free | 限时免费 |
| Hy3 Preview Free | 限时免费 |
| Nemotron 3 Super Free | NVIDIA 免费端点，会记录提示词 |
| GPT 5 Nano | 免费 |

### 已弃用模型

| 模型 | 弃用日期 |
|------|----------|
| GPT 5.2 Codex | 2026-07-23 |
| GPT 5.1 Codex | 2026-07-23 |
| GPT 5 Codex | 2026-07-23 |
| Claude Sonnet 4 | 2026-06-15 |
| GLM 5 | 2026-05-14 |
| GLM 4.7 | 2026-03-15 |
| Gemini 3 Pro | 2026-03-09 |
| Kimi K2 Thinking | 2026-03-06 |
| Claude Haiku 3.5 | 2026-02-16 |

**用途**: 
- 模型 ID 与名称映射 (如 claude-opus-4-7 → Claude Opus 4.7)
- API 定价参考
- 识别已弃用模型，避免推荐过时版本
