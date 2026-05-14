# LLM Benchmark Skill

从互联网公开评测平台获取 LLM 评测数据，生成按能力类别组织的可视化对比报告。

## 功能特性

- **多模型对比**: 支持 2-7 个模型的横向对比
- **12 类评测维度**: Coding Agent, Knowledge, STEM & Reasoning, Math, Vision, Function Calling 等
- **本地缓存**: 已评测模型数据持久化存储，减少重复搜索
- **HTML 可视化报告**: 雷达图、柱形图、排名矩阵、深色模式
- **置信度标注**: 区分已验证 (✅)、官方声称 (⚠️)、未披露 (🔲) 数据

## 目录结构

```
llm-benchmark/
├── assets/                    # 静态资源 (模板、Schema、数据文件)
│   ├── html-template.html     # HTML 报告模板
│   └── cache-schema.json      # 缓存数据 JSON Schema
├── scripts/                   # 可执行脚本
│   ├── validate_cache.py      # 验证缓存数据
│   ├── clean_cache.py         # 清理过期缓存
│   └── stats_cache.py         # 缓存统计信息
├── references/                # 参考文档
│   ├── benchmarks.md          # 评测基准详细说明
│   ├── data-sources.md        # 数据来源与搜索策略
│   ├── model-benchmarks.md    # 常见模型评测数据参考
│   └── rankings.md            # 综合排名参考数据
├── SKILL.md                   # 技能定义文件
└── README.md                  # 本文件
```

## 脚本工具

| 脚本 | 用途 | 用法 |
|------|------|------|
| `validate_cache.py` | 验证缓存数据是否符合 Schema | `uv run scripts/validate_cache.py --verbose` |
| `clean_cache.py` | 清理过期或损坏的缓存 | `uv run scripts/clean_cache.py --days 30 --dry-run` |
| `stats_cache.py` | 显示缓存统计信息 | `uv run scripts/stats_cache.py` |

> 💡 使用 `uv run` 自动安装脚本依赖（PEP 723）

## 使用方法

### 触发关键词

"模型评测"、"基准测试"、"benchmark"、"模型对比"、"能力测试"、"LLM评测"、"模型得分"、"哪个模型好"、"模型排名"、"大模型排行"

### 示例

```
用户: 对比 Qwen3.6-27B 和 GLM-4.7
用户: DeepSeek-V4 和 Claude Opus 4.7 哪个代码能力强
用户: 对比 Qwen3.6-27B、GLM-5、Kimi K2.5 和 DeepSeek-V4-Pro
```

## 输出

| 输出项 | 位置 | 说明 |
|--------|------|------|
| Markdown 表格 | 对话框 | 模型概览、分类对比、选型建议 |
| HTML 报告 | `.llm-benchmark/YYYY-MM-DD/` | 可视化报告，含雷达图、柱形图 |
| 缓存数据 | `.llm-benchmark/cache/` | JSON 格式，遵循 cache-schema.json |

## 数据来源

| 平台 | 说明 |
|------|------|
| 官方技术报告 | 厂商发布的模型技术报告 |
| HuggingFace Model Card | 模型卡片的评测数据 |
| BenchLM | benchlm.ai |
| Artificial Analysis | artificialanalysis.ai |
| OpenRouter | openrouter.ai |
| OpenCompass | opencompass.org.cn |
| SuperCLUE | superclueai.com |

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v2.2.1 | 2026-05-01 | 修复脚本交互式提示问题; 添加 PEP 723 内联依赖; 补充 Frontmatter 可选字段 |
| v2.2.0 | 2026-05-01 | 按 agentskills.io 最佳实践重构: 添加 Gotchas/Checklist/Validation loops |
| v2.1.0 | 2026-05-01 | 重构目录结构符合 agentskills.io 规范; SKILL.md 精简至 131 行; 新增 scripts/ 和 benchmarks.md |
| v2.0.0 | 2026-05-01 | 评测维度扩展至12类; 新增多模型对比/本地缓存/雷达图/深色模式/置信度标注 |
| v1.0.0 | 2026-04-XX | 初始版本 |
