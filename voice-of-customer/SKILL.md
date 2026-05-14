---
name: "voice-of-customer"
description: "基于客户之声(VOC)理论分析用户消息并提取需求。触发场景：用户提到客户反馈、用户需求、需求分析、VOC、功能请求、问题报告时调用。支持Kano模型分类、亲和图分析、优先级评估和需求追溯。注意：本技能仅负责需求收集和分析，不执行开发任务。"
version: "2.5"
author: "AI Assistant"
last_updated: "2026-05-04"
---

# Voice of Customer (VOC) 客户之声分析技能

> **版本**: 2.5 | **基于**: ISO 9000 + PDCA + Agent Skills 规范

## ⚠️ 重要说明

**VOC 技能的职责边界**：
- ✅ **负责**：收集、分析用户需求，生成需求文档
- ❌ **不负责**：执行代码修改、实施开发任务
- 🔄 **协作**：需求分析完成后，建议使用 `/pdca` 技能进行系统化开发

## Gotchas

- **VOC 技能不执行开发任务** — 只负责需求收集和分析，不修改代码文件
- **一次对话可能有多个需求** — 分别建立不同文件夹 `req-YYYYMMDD-HHMMSS-NNN/`
- **Kano 分类影响优先级决策** — 基本型必须满足，期望型优先满足，兴奋型选择性满足
- **保留用户原话** — 始终保留客户原话，不做修改，确保追溯性
- **最多 3 轮澄清对话** — 避免过多打扰用户，信息完整或用户停止时结束

## 工作流程 Checklist

Progress:
- [ ] 步骤 0: 多轮对话收集（最多 3 轮澄清）
- [ ] 步骤 1: 收集客户之声 → `req-XXX/uservoice.md`
- [ ] 步骤 2: 深度分析 → `req-XXX/analysis.md`
- [ ] 步骤 3: 转化为需求 → `req-XXX/requirements.md`
- [ ] 步骤 4: 更新追溯矩阵 → `.voc/TRACEABILITY.md`
- [ ] 步骤 5: 更新统计仪表板 → `.voc/SUMMARY.md`
- [ ] 步骤 6: 更新需求索引 → `.voc/RVTM.md`

## 验证循环

### 步骤 0: 多轮对话收集

**目标**: 通过主动发起 1-3 轮对话，充分获取用户需求

**信息完整性检查**:
- ✅ 需求描述是否清晰？
- ✅ 业务场景是否明确？
- ✅ 期望结果是否具体？
- ✅ 优先级是否有说明？

**结束对话条件**:
- ✅ 信息已完整（所有必需字段都有）
- ✅ 用户明确表示停止
- ✅ 已达到 3 轮上限

### 步骤 6: 验证和改进

验证需求完整性后：
1. 检查需求完整性
2. 检查追溯一致性
3. 检查验收标准可测试性
4. 更新 RVTM.md 需求索引

**⚠️ 重要提醒**: VOC 技能到此阶段**已完成职责**，不要直接执行代码修改。

## Kano 模型速查

| 分类 | 说明 | 策略 |
|------|------|------|
| **基本型** | 基本期望，缺失导致强烈不满 | 必须满足 |
| **期望型** | 越多越好，直接关联满意度 | 优先满足 |
| **兴奋型** | 意外功能，带来惊喜 | 选择性满足 |
| **无差异** | 功能对用户不重要 | 暂缓 |
| **反向** | 功能会导致不满 | 避免 |

## 文件结构

### 输入文件（过程文件）

| 目录 | 说明 |
|------|------|
| `assets/` | 模板文件（uservoice.md, analysis.md, requirement.md, traceability.md, summary.md） |
| `references/` | 参考文档（tools.md, example-export-feature.md） |

### 输出文件（结果文件）

所有输出文件位于项目根目录的 `.voc/` 文件夹：

| 文件 | 说明 |
|------|------|
| `.voc/RVTM.md` | 需求追溯总表（索引） |
| `.voc/USERVOICE.md` | 客户之声记录 |
| `.voc/ANALYSIS.md` | 分析结果 |
| `.voc/REQUIREMENTS.md` | 需求规格说明 |
| `.voc/TRACEABILITY.md` | 需求追溯矩阵 |
| `.voc/SUMMARY.md` | 统计仪表板 |
| `req-YYYYMMDD-HHMMSS-NNN/` | 每个需求的独立文件夹 |

### 需求文件夹命名规则

- **格式**: `req-YYYYMMDD-HHMMSS-NNN`
- **示例**: `req-20260504-205500-001`

## References

| 文档 | 内容 | 路径 |
|------|------|------|
| 实用工具与方法 | 5WHY、用户故事拆分、优先级评分等 | [references/tools.md](references/tools.md) |
| 完整案例 | 数据导出功能端到端演示 | [references/example-export-feature.md](references/example-export-feature.md) |
| 客户之声模板 | 记录用户原话和初步分析 | [assets/uservoice.md](assets/uservoice.md) |
| 分析结果模板 | 深度分析和优先级评估 | [assets/analysis.md](assets/analysis.md) |
| 需求规格模板 | 详细需求规格说明 | [assets/requirement.md](assets/requirement.md) |
| 追溯矩阵模板 | 维护追溯链 | [assets/traceability.md](assets/traceability.md) |
| 统计仪表板模板 | 可视化统计结果 | [assets/summary.md](assets/summary.md) |

## 最佳实践

### DO ✅

- 保留客户原话，不做修改
- 使用 5WHY 深挖真实需求
- 使用评分矩阵量化优先级
- 维护完整的追溯链
- 通过 1-3 轮对话充分获取需求
- 为每个需求建立独立文件夹

### DON'T ❌

- 不要过度解释，避免偏离客户原意
- 不要忽略情感，情感是重要的需求信号
- 不要执行开发任务，VOC 技能只负责需求分析
- 不要过多对话，最多 3 轮，避免用户反感
