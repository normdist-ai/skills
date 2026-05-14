---
name: "china-stock-analysis"
description: "中国A股价值投资分析工具。触发场景：用户请求分析A股股票、筛选股票、计算估值、对比行业、检测财务异常时调用。"
---

# China Stock Analysis Skill

基于价值投资理论的中国A股分析工具，面向低频交易的普通投资者。

## Gotchas

- **akshare 依赖必须安装** — 执行分析前必须先 `pip install akshare pandas numpy`
- **A股代码格式** — 6位数字，如 `600519`，不支持带交易所前缀格式
- **数据时效性** — 财务数据以最新季报/年报为准，价格数据为当日收盘价
- **政策敏感行业** — 房地产、新能源、医药、互联网等行业需特别关注政策影响

## 核心模块

| 模块 | 功能 | 脚本 |
|------|------|------|
| 股票筛选器 | 按PE/ROE/股息率等条件筛选 | `scripts/stock_screener.py` |
| 财务分析器 | 个股深度财务分析 | `scripts/financial_analyzer.py` |
| 行业对比器 | 同行业横向对比 | `scripts/industry_comparator.py` |
| 估值计算器 | DCF/DDM/相对估值 | `scripts/valuation_calculator.py` |
| 数据获取器 | 获取股票财务数据 | `scripts/data_fetcher.py` |

## 工作流程 Checklist

### 股票筛选
Progress:
- [ ] 1. 收集筛选条件（PE/PB/ROE/股息率/负债率等）
- [ ] 2. 执行 `scripts/stock_screener.py`
- [ ] 3. 以表格形式呈现结果

### 个股分析
Progress:
- [ ] 1. 收集股票代码和分析深度（摘要/标准/深度）
- [ ] 2. 执行 `scripts/data_fetcher.py` 获取数据
- [ ] 3. 执行 `scripts/financial_analyzer.py` 分析财务
- [ ] 4. 执行 `scripts/valuation_calculator.py` 计算估值
- [ ] 5. 生成中文分析报告

### 行业对比
Progress:
- [ ] 1. 收集对比目标（多只股票或行业分类）
- [ ] 2. 执行 `scripts/data_fetcher.py` 获取行业数据
- [ ] 3. 执行 `scripts/industry_comparator.py` 生成对比表

## 验证循环

### 步骤 1: 检查依赖

```bash
python -c "import akshare; print(akshare.__version__)"
```

如果失败，执行：
```bash
pip install akshare pandas numpy
```

### 步骤 2: 验证股票代码

```bash
python scripts/data_fetcher.py --code "600519" --data-type basic
```

只有验证通过才能继续分析。

## 财务异常检测

在分析过程中自动检测：

| 异常类型 | 触发条件 | 风险等级 |
|----------|----------|----------|
| 应收账款异常 | 应收增速 > 营收增速 × 1.5 | 🟡 中 |
| 现金流背离 | 净利增长但经营现金流下降 | 🔴 高 |
| 存货异常 | 存货增速 > 营收增速 × 2 | 🟡 中 |
| 毛利率异常 | 波动 > 行业均值波动 × 2 | 🟡 中 |
| 股东减持 | 大股东近期减持公告 | 🔴 高 |

## 输出格式

所有脚本输出 JSON 格式：

```json
{
  "code": "600519",
  "name": "贵州茅台",
  "analysis_date": "2025-01-25",
  "summary": { "score": 85, "conclusion": "低估" },
  "financials": {},
  "valuation": {},
  "risks": []
}
```

## 目录结构

```
china-stock-analysis/
├── SKILL.md              # 本文件
├── scripts/              # Python 脚本
│   ├── data_fetcher.py
│   ├── stock_screener.py
│   ├── financial_analyzer.py
│   ├── industry_comparator.py
│   └── valuation_calculator.py
├── assets/               # 模板文件
│   └── analysis_report.md
└── references/           # 参考文档
    └── financial_metrics.md
```

## 重要提示

- 所有分析基于公开财务数据，不涉及内幕信息
- 估值模型参数假设对结果影响较大，需向用户说明
- A股市场受政策影响较大，定量分析需结合定性判断
- 所有分析仅供参考，不构成投资建议
