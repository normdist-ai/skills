# 评测基准详细说明

本文档详细定义 LLM Benchmark 技能使用的评测维度和基准测试。

## 评测维度总览

| 维度 | 说明 | 代表性基准测试 |
|------|------|----------------|
| Coding Agent | 代码生成与软件工程 | SWE-bench, Terminal-Bench, LiveCodeBench |
| Knowledge | 多领域知识问答 | MMLU-Pro, C-Eval, SuperGPQA |
| STEM & Reasoning | 高阶逻辑推理 | GPQA Diamond, HLE |
| Math | 数学推理与计算 | AIME, HMMT |
| Agentic | 自主任务执行与环境交互 | BrowseComp, MCP-Atlas |
| Long Context | 长上下文检索与理解 | MRCR, LongBench, RULER |
| Function Calling | 工具/API调用与编排 | BFCL, τ²-Bench |
| Safety & Trust | 安全合规与对抗鲁棒性 | HarmBench, CyberGym |
| Hallucination | 事实准确性与幻觉检测 | HaluEval, FActScore |
| Instruction Following | 指令理解与执行 | IFEval, IFBench |
| Multilingual | 跨语言能力 | MMLU-ProX, MGSM |
| Vision Language | 视觉理解能力 | MMMU, MathVista, MMStar |
| RAG | 检索增强与信息整合 | RAGAS, CRUD |

---

## 详细基准测试说明

### Coding Agent (代码能力)

| 基准测试 | 说明 | 注意事项 |
|---------|------|---------|
| SWE-bench Verified | 软件工程基准验证集 | 得分依赖 agent scaffold 配置 |
| SWE-bench Pro | 软件工程基准专业版 | 得分依赖 agent scaffold 配置 |
| SWE-bench Multilingual | 多语言软件工程基准 | 不同语言版本不可直接对比 |
| Terminal-Bench 2.0 | 终端命令执行基准 | 需标注 harness 配置 |
| LiveCodeBench | 实时代码评测 | 题目持续更新，需标注评测时间 |
| HumanEval | 代码生成基准 | 经典基准，已被更全面基准取代 |
| SkillsBench Avg5 | 技能评测平均分 | 5项技能综合评估 |
| Claw-Eval Avg | Claw 评测平均分 | 综合代码能力评估 |
| NL2Repo | 自然语言到代码仓库 | 代码生成与项目构建能力 |
| QwenWebBench | Qwen 网页评测基准 | 阿里自研基准 |
| PinchBench | Pinch 评测基准 | 代码能力专项评测 |

### Knowledge (知识理解)

| 基准测试 | 说明 | 注意事项 |
|---------|------|---------|
| MMLU-Pro | 多任务语言理解专业版 | 57个学科领域 |
| MMLU-Redux | MMLU 改进版 | 修正了原版数据质量问题 |
| SuperGPQA | 研究生级别问答 | 高难度专业知识 |
| C-Eval | 中文综合评测 | 中文知识能力 |
| CMMLU | 中文多任务语言理解 | 中文领域覆盖 |

### STEM & Reasoning (推理能力)

| 基准测试 | 说明 | 注意事项 |
|---------|------|---------|
| GPQA Diamond | 研究生级别科学问答 | 高难度推理 |
| HLE | 人类最后考试 | 极高难度基准 |
| BBH | Big-Bench Hard | 高难度推理任务 |

### Math (数学能力)

| 基准测试 | 说明 | 注意事项 |
|---------|------|---------|
| AIME26 | 美国数学邀请赛 | 高难度数学竞赛题 |
| HMMT Feb 25 | 哈佛麻省理工数学锦标赛 | 高难度数学竞赛题 |
| GSM8K | 小学数学应用题 | 基础数学推理 |
| MATH | 高中数学竞赛题 | 高难度数学推理 |

### Agentic (智能体能力)

| 基准测试 | 说明 | 注意事项 |
|---------|------|---------|
| BrowseComp | 浏览器任务评测 | 网页交互与信息检索 |
| MCPMark | MCP 协议评测 | 工具调用与协议理解 |
| MCP-Atlas | MCP 工具图谱 | 需标注工具数量 |
| WideSearch | 广域搜索评测 | 信息检索与整合 |
| OSWorld | 操作系统交互 | 桌面环境任务执行 |

### Long Context (长文本理解)

| 基准测试 | 说明 | 注意事项 |
|---------|------|---------|
| MRCR | 多轮对话检索 | 需标注上下文长度 (如 128K/1M) |
| LongBench | 长文本基准 | 多任务长文本评测 |
| RULER | 长上下文检索 | 检索准确率评测 |
| InfiniteBench | 无限上下文基准 | 极长文本评测 |

### Function Calling (函数调用)

| 基准测试 | 说明 | 注意事项 |
|---------|------|---------|
| BFCL Multi-Turn | 多轮函数调用 | 有 v1/v2/v3 版本，需标注版本 |
| τ²-Bench Telecom | 电信领域函数调用 | 特定领域评测 |
| Nexus | 函数调用基准 | 工具编排能力 |

### Safety & Trust (安全对齐)

| 基准测试 | 说明 | 注意事项 |
|---------|------|---------|
| HarmBench | 有害行为评测 | 需标注攻击类型和阈值 |
| CyberGym | 网络安全评测 | 安全漏洞检测 |
| TruthfulQA | 真实性问答 | 事实准确性 |
| SafetyBench | 安全基准 | 多维度安全评测 |

### Hallucination (幻觉评估)

| 基准测试 | 说明 | 注意事项 |
|---------|------|---------|
| HaluEval | 幻觉评测基准 | 事实准确性检测 |
| FActScore | 事实评分 | 细粒度事实评估 |

### Vision Language (多模态)

| 基准测试 | 说明 | 注意事项 |
|---------|------|---------|
| MMMU | 多模态多任务理解 | 综合多模态能力 |
| MMMU-Pro | MMMU 专业版 | 高难度多模态任务 |
| MathVista | 数学视觉推理 | 图表与数学结合 |
| MMStar | 多模态星形评测 | 细粒度视觉理解 |
| RealWorldQA | 真实世界问答 | 现实场景理解 |
| RefCOCO avg | 指代表达理解平均分 | 图像区域定位 |

---

## 维度分类原则 (MECE)

| 维度 | 侧重点 | 与其他维度区别 |
|------|--------|----------------|
| Agentic | 自主任务执行与环境交互 | 侧重完整任务流程，非单一能力 |
| Function Calling | 工具/API编排 | 侧重接口调用，非自主决策 |
| Safety & Trust | 对抗性安全 | 侧重恶意输入防御，非事实准确 |
| Hallucination | 事实准确性 | 侧重输出真实性，非安全性 |
| RAG | 检索增强生成 | 侧重外部知识整合，非内部知识 |

---

## 数据置信度标注

| 标识 | 含义 | 适用场景 |
|------|------|---------|
| ✅ | 官方发布/已独立验证 | 官方技术报告、HuggingFace Model Card、OpenCompass评测 |
| ⚠️ | 官方声称/未独立验证 | 厂商博客、发布会、未标注评测条件的得分 |
| 🔲 | 未披露/无数据 | 闭源模型未公开、新发布模型尚无评测 |

**标注规则**:
- 每个基准测试得分必须标注置信度
- 对比表中置信度低的得分用斜体标注
- 优胜者判定: 仅当两个模型置信度相同时才判定；置信度不同时标注"待验证"

---

## 评测条件注意事项

| 基准测试 | 条件依赖 | 说明 |
|---------|---------|------|
| SWE-bench | agent scaffold 配置 | 不同配置不可直接对比 |
| Terminal-Bench | harness 配置 | 需标注运行环境 |
| MRCR | 上下文长度 | 不同长度 (128K/1M) 不可直接对比 |
| BFCL | 版本号 | v1/v2/v3 不可直接对比 |
| MCP-Atlas | 工具数量 | 不同工具集不可直接对比 |
| HarmBench | 攻击类型和阈值 | 不同设置不可直接对比 |
| RAGAS | 检索器配置 | 得分依赖检索器质量 |
