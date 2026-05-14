---
name: "llm-benchmark"
description: "Use this skill when evaluating, comparing, or benchmarking LLM models across reasoning, coding, math, and agentic capabilities. Apply when users ask about model scores, rankings, or performance differences, or mention '模型评测', '基准测试', 'benchmark', '模型对比', '能力测试', 'LLM评测', '模型得分', '模型排名', '大模型排行', 'AI评测', '模型性能', '开源模型对比', '闭源模型对比', '中文模型评测', even if they don't explicitly mention 'benchmark' and just say 'which model is better' or 'compare these models'."
license: "Apache-2.0"
compatibility: "Requires Python 3.10+ and uv for running scripts"
metadata:
  author: "workspace-skills"
  version: "2.4.0"
---

# LLM Benchmark - 大模型综合能力评测

从互联网公开评测平台获取 LLM 评测数据，生成按能力类别组织的可视化对比报告。

**版本**: v2.4.0 (2026-05-01)

---

## ⚠️ 强制执行规则

在开始任何评测任务前，**必须**遵守以下规则：

### 1. TodoList 管理规则

- **必须调用 TodoWrite** 创建任务列表，包含所有 Checklist 项
- **必须按顺序执行** 每个步骤，完成后立即更新 TodoWrite 状态为 `completed`
- **必须检测最终状态** 任务完成前，检查 TodoList 中是否所有任务都为 `completed`
- **禁止标记完成** 如果 TodoList 中有任何任务未完成（状态为 `pending` 或 `in_progress`），整个评测任务不算完成

### 2. 执行流程规则

- **必须输出进度** 在每个步骤完成后输出 `[✓] 步骤 N/5 完成：{简短描述}`
- **必须验证数据** 运行 `validate_cache.py` 后才能继续下一步
- **必须写入缓存** 每个模型数据必须保存为 JSON 文件
- **禁止跳过步骤** 不允许跳过任何步骤直接输出结果

### 3. 任务完成标准

```
✅ 任务完成的条件：
  1. TodoList 中所有任务状态为 completed
  2. 所有缓存文件已写入并通过验证
  3. Markdown 表格已输出到对话框
  4. 用户确认满意

❌ 任务未完成的情况：
  1. TodoList 中有任务状态为 pending 或 in_progress
  2. 缓存文件缺失或验证失败
  3. 跳过了任何 Checklist 步骤
```

---

## Gotchas

这些是代理在没有明确告知的情况下会犯的错误：

- **IDE 内置模型列表必须实时获取** — Trae、OpenCode、Cursor 等 IDE 的内置模型会随时间变化，**禁止使用本地缓存或假设模型列表**。必须先从官方文档获取最新模型列表。
- **SWE-bench 得分不可直接对比** — 不同 agent scaffold 配置会导致得分差异 10-30%。必须检查评测条件是否一致。
- **模型名称变体指向同一模型** — `qwen3.6-27b`、`Qwen3.6-27B`、`Qwen-3.6-27B` 都是同一模型。使用标准名称 `Qwen3.6-27B`。
- **MoE 模型有两个参数量** — `Qwen3.6-35B-A3B` 总参数 35B，激活参数 3B。部署需求取决于激活参数，成本取决于总参数。
- **GLM-4 ≠ GLM-4.7 ≠ GLM-5** — 版本号差异代表不同代际，性能差距可达 20%+。必须确认用户意图。
- **MRCR 长文本评测需标注上下文长度** — 同一模型在 128K 和 1M 上下文下的得分不同，不可直接对比。
- **BFCL 有 v1/v2/v3 三个版本** — 不同版本得分不可对比，必须标注版本号。
- **闭源模型数据置信度低** — OpenAI、Anthropic 等闭源模型的评测数据多为官方声称 (⚠️)，未经独立验证。
- **缓存数据超过 30 天需重新验证** — 模型更新、评测方法变化会导致数据过时。

---

## 工作流程 Checklist

使用 `TodoWrite` 工具跟踪进度，**必须按顺序执行**：

```
Progress:
- [ ] 1. 确认需求 + 获取模型列表 (IDE 内置模型必须从官方网页获取)
- [ ] 2. 读取缓存 + 搜索数据 (识别缺失数据，从公开评测平台补充)
- [ ] 3. 验证数据完整性 (运行 scripts/validate_cache.py，必须通过)
- [ ] 4. 生成报告 + 写入缓存 (HTML 可视化 + JSON 缓存文件)
- [ ] 5. 输出结果 + 确认反馈 (Markdown 表格 + 用户确认)
```

### 检查点输出要求

每个步骤完成后，**必须**输出进度状态：

```
[✓] 步骤 1/5 完成：已确认评测需求（X 个模型）
[✓] 步骤 2/5 完成：已读取缓存，缺失 X 个模型数据，已搜索补充
[✓] 步骤 3/5 完成：数据验证通过（X 个缓存文件有效）
[✓] 步骤 4/5 完成：已生成报告，写入 X 个缓存文件
[✓] 步骤 5/5 完成：已输出 Markdown 表格，等待用户确认
```

### TodoList 状态检测

任务完成前，**必须**执行以下检测：

```python
# 检查 TodoList 最终状态
all_completed = all(task["status"] == "completed" for task in todos)

if not all_completed:
    pending_tasks = [t for t in todos if t["status"] != "completed"]
    print(f"❌ 任务未完成：还有 {len(pending_tasks)} 个任务未完成")
    for task in pending_tasks:
        print(f"   - {task['content']}")
    # 必须继续执行，不能结束
else:
    print("✅ 所有任务已完成")
```

### IDE 内置模型查询流程

当用户请求评测 **Trae、OpenCode、Cursor、Windsurf 等 IDE 内置模型** 时：

1. **必须先从官方文档获取模型列表**（禁止使用本地缓存或假设）
2. 使用 `WebSearch` 或 `WebFetch` 工具访问官方文档
3. 获取最新模型列表后再搜索各模型的评测数据

**常见 IDE 官方文档地址**：

| IDE | 官方模型列表文档 |
|-----|-----------------|
| Trae | `https://docs.trae.ai/ide/models` |
| OpenCode | `https://opencode.ai/docs/models` |
| Cursor | `https://docs.cursor.com/models` |
| Windsurf | `https://docs.codeium.com/windsurf/models` |
| JetBrains AI | `https://www.jetbrains.com/help/ai-assistant/models.html` |

---

## 输入处理

### 模型名称标准化

| 输入 | 标准名称 |
|------|---------|
| `qwen3.6-27b`, `Qwen-3.6-27B` | `Qwen3.6-27B` |
| `glm4.7`, `GLM 4.7` | `GLM-4.7` |
| `deepseek v4`, `DeepSeek-V4` | `DeepSeek-V4` |
| `gpt5`, `GPT-5` | `GPT-5` |

### 对比模式

| 模型数 | 模式 | 输出特点 |
|--------|------|---------|
| 1 | 单模型查询 | 评测概览 |
| 2 | 双模型对比 | 逐项对比 + 优胜者 |
| 3+ | 多模型对比 | 雷达图 + 排名矩阵 |

---

## 数据获取

### 优先级

```
本地缓存 → 官方评测平台 → 模型官方发布 → 第三方汇总
```

### 缓存机制

1. 读取 `.llm-benchmark/cache/{模型名}.json`
2. 缺失数据从互联网补充
3. 更新缓存并标注 `retrieved_at` 时间戳

> 📖 详细的数据来源、搜索关键词见 `references/data-sources.md`

### 数据置信度

| 标识 | 含义 | 来源 |
|------|------|------|
| ✅ | 已独立验证 | OpenCompass、BenchLM、HuggingFace |
| ⚠️ | 官方声称 | 厂商博客、技术报告 |
| 🔲 | 未披露 | 闭源模型无公开数据 |

---

## 验证循环

### 步骤 4: 验证数据完整性

```bash
uv run scripts/validate_cache.py --cache-dir .llm-benchmark/cache --verbose
```

如果验证失败：
1. 查看错误信息
2. 补充缺失字段
3. 重新运行验证
4. 只有验证通过才能继续

### 缓存文件必须包含

```json
{
  "cache_version": "1.0",
  "model": "模型名",
  "provider": "厂商",
  "benchmarks": { "coding_agent": {}, "knowledge": {} },
  "source": "数据来源URL",
  "retrieved_at": "YYYY-MM-DD"
}
```

> 📖 完整 Schema 见 `assets/cache-schema.json`

---

## 输出格式

### 对话框 (Markdown)

按此顺序输出：

1. **模型概览表** — 厂商、参数、架构、上下文长度、部署门槛
2. **分类对比表** — 每个能力类别一张表
3. **优胜者统计** — 胜出项数、显著领先项
4. **选型建议** — 场景推荐 + 硬件需求

### HTML 报告

保存到 `.llm-benchmark/YYYY-MM-DD/{模型名}_vs_{模型名}.html`

> 📖 HTML 模板见 `assets/html-template.html`

---

## 评测维度

| 类别 | 代表性基准 |
|------|-----------|
| Coding Agent | SWE-bench, Terminal-Bench, LiveCodeBench |
| Knowledge | MMLU-Pro, C-Eval, SuperGPQA |
| STEM & Reasoning | GPQA Diamond, HLE |
| Math | AIME, HMMT |
| Agentic | BrowseComp, MCP-Atlas |
| Long Context | MRCR, LongBench, RULER |
| Function Calling | BFCL, τ²-Bench |
| Safety & Trust | HarmBench, CyberGym |
| Vision Language | MMMU, MathVista, MMStar |

> 📖 完整评测维度和基准测试说明见 `references/benchmarks.md`

---

## References

| 文件 | 何时阅读 |
|------|---------|
| `references/benchmarks.md` | 需要了解评测基准详情时 |
| `references/data-sources.md` | 搜索数据时 |
| `references/model-benchmarks.md` | 需要参考模型数据时 |
| `assets/html-template.html` | 生成 HTML 时 |
| `assets/cache-schema.json` | 缓存写入时 |
