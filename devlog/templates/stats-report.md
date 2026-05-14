# 工作状态报告 - {{DATE}}

> **生成时间**: {{GENERATED_AT}}  
> **数据源**: {{SOURCES}}

---

## 📈 关键指标

| 指标 | 数值 | 说明 |
|------|------|------|
| 💼 工作时长 | {{WORK_HOURS}} 小时 | 实际工作时间 |
| ✅ 完成任务 | {{TASKS_COMPLETED}} 个 | 已完成的任务数 |
| 🔧 代码提交 | {{COMMITS}} 次 | Git commit 数量 |
| 📝 代码行数 | +{{LINES_ADDED}}/-{{LINES_REMOVED}} | 新增/删除行数 |
| 🐛 问题解决 | {{ISSUES_RESOLVED}}/{{ISSUES_FOUND}} | 已解决/发现问题 |

---

## 📊 工作量统计

### 任务完成情况

| 状态 | 数量 | 占比 |
|------|------|------|
| ✅ 已完成 | {{TASKS_COMPLETED}} | {{COMPLETED_PERCENT}}% |
| 🔄 进行中 | {{TASKS_IN_PROGRESS}} | {{IN_PROGRESS_PERCENT}}% |
| ⏸️ 待处理 | {{TASKS_PENDING}} | {{PENDING_PERCENT}}% |

```mermaid
pie title 任务完成分布
    "已完成" : {{TASKS_COMPLETED}}
    "进行中" : {{TASKS_IN_PROGRESS}}
    "待处理" : {{TASKS_PENDING}}
```

### 时间分配

| 活动类型 | 时长(小时) | 占比 |
|----------|-----------|------|
| 💻 编码开发 | {{CODING_HOURS}} | {{CODING_PERCENT}}% |
| 🐛 调试修复 | {{DEBUG_HOURS}} | {{DEBUG_PERCENT}}% |
| 📖 学习调研 | {{LEARNING_HOURS}} | {{LEARNING_PERCENT}}% |
| 🤝 会议沟通 | {{MEETING_HOURS}} | {{MEETING_PERCENT}}% |
| 📝 文档编写 | {{DOC_HOURS}} | {{DOC_PERCENT}}% |
| 🔍 Code Review | {{REVIEW_HOURS}} | {{REVIEW_PERCENT}}% |

```mermaid
pie title 时间分配
    "编码开发" : {{CODING_HOURS}}
    "调试修复" : {{DEBUG_HOURS}}
    "学习调研" : {{LEARNING_HOURS}}
    "会议沟通" : {{MEETING_HOURS}}
    "文档编写" : {{DOC_HOURS}}
    "Code Review" : {{REVIEW_HOURS}}
```

---

## 📉 代码变更统计

### 今日变更

| 指标 | 数量 |
|------|------|
| 修改文件数 | {{FILES_CHANGED}} |
| 新增行数 | {{LINES_ADDED}} |
| 删除行数 | {{LINES_REMOVED}} |
| 净增行数 | {{NET_LINES}} |

```mermaid
pie title 代码变更分布 (最近7天)
    "新增行数" : {{LINES_ADDED}}
    "删除行数" : {{LINES_REMOVED}}
```

### 文件类型分布

| 文件类型 | 数量 | 占比 |
|----------|------|------|
| `.py` | {{PY_FILES}} | {{PY_PERCENT}}% |
| `.js/.ts` | {{JS_FILES}} | {{JS_PERCENT}}% |
| `.md` | {{MD_FILES}} | {{MD_PERCENT}}% |
| 其他 | {{OTHER_FILES}} | {{OTHER_PERCENT}}% |

```mermaid
pie title 修改文件类型分布
    "Python (.py)" : {{PY_FILES}}
    "JavaScript/TypeScript" : {{JS_FILES}}
    "Markdown (.md)" : {{MD_FILES}}
    "其他" : {{OTHER_FILES}}
```

---

## 🐛 问题追踪统计

### 问题状态

| 状态 | 数量 |
|------|------|
| ✅ 已解决 | {{ISSUES_RESOLVED}} |
| 🔄 进行中 | {{ISSUES_IN_PROGRESS}} |
| ⏸️ 待处理 | {{ISSUES_PENDING}} |

```mermaid
pie title 问题状态分布
    "已解决" : {{ISSUES_RESOLVED}}
    "进行中" : {{ISSUES_IN_PROGRESS}}
    "待处理" : {{ISSUES_PENDING}}
```

### 问题类型分布

| 类型 | 数量 | 占比 |
|------|------|------|
| 🐛 Bug修复 | {{BUG_COUNT}} | {{BUG_PERCENT}}% |
| ⚙️ 配置问题 | {{CONFIG_COUNT}} | {{CONFIG_PERCENT}}% |
| 📊 性能优化 | {{PERF_COUNT}} | {{PERF_PERCENT}}% |
| 🔒 安全问题 | {{SECURITY_COUNT}} | {{SECURITY_PERCENT}}% |
| 📚 文档问题 | {{DOC_ISSUE_COUNT}} | {{DOC_ISSUE_PERCENT}}% |

```mermaid
pie title 问题类型分布
    "Bug修复" : {{BUG_COUNT}}
    "配置问题" : {{CONFIG_COUNT}}
    "性能优化" : {{PERF_COUNT}}
    "安全问题" : {{SECURITY_COUNT}}
    "文档问题" : {{DOC_ISSUE_COUNT}}
```

---

## 📅 本周趋势

### 工作时长趋势

| 日期 | 工作时长 | 完成任务 | 代码提交 |
|------|---------|---------|---------|
| {{WEEK_DAY1}} | {{HOURS_1}}h | {{TASKS_1}} | {{COMMITS_1}} |
| {{WEEK_DAY2}} | {{HOURS_2}}h | {{TASKS_2}} | {{COMMITS_2}} |
| {{WEEK_DAY3}} | {{HOURS_3}}h | {{TASKS_3}} | {{COMMITS_3}} |
| {{WEEK_DAY4}} | {{HOURS_4}}h | {{TASKS_4}} | {{COMMITS_4}} |
| {{WEEK_DAY5}} | {{HOURS_5}}h | {{TASKS_5}} | {{COMMITS_5}} |
| **本周总计** | **{{WEEK_TOTAL_HOURS}}h** | **{{WEEK_TOTAL_TASKS}}** | **{{WEEK_TOTAL_COMMITS}}** |

```mermaid
pie title 本周工作时长分布
    "{{WEEK_DAY1}}" : {{HOURS_1}}
    "{{WEEK_DAY2}}" : {{HOURS_2}}
    "{{WEEK_DAY3}}" : {{HOURS_3}}
    "{{WEEK_DAY4}}" : {{HOURS_4}}
    "{{WEEK_DAY5}}" : {{HOURS_5}}
```

---

## 🎯 今日亮点

### 最高效时段

| 时间段 | 完成任务 | 说明 |
|--------|---------|------|
| {{PEAK_TIME}} | {{PEAK_TASKS}} 个 | {{PEAK_DESCRIPTION}} |

### 最大成果

- 🏆 **代码贡献**: +{{MAX_LINES_ADDED}} 行 ({{MAX_FILE}})
- 🎉 **问题解决**: {{BIGGEST_ISSUE}}
- 📈 **性能提升**: {{PERFORMANCE_IMPROVEMENT}}

---

## 📋 明日计划概览

| 优先级 | 任务 | 预估时长 |
|--------|------|---------|
| 🔴 高 | {{HIGH_PRIORITY_TASK1}} | {{HOURS_1}}h |
| 🟡 中 | {{MEDIUM_PRIORITY_TASK1}} | {{HOURS_2}}h |
| 🟢 低 | {{LOW_PRIORITY_TASK1}} | {{HOURS_3}}h |

---

## 🔗 相关链接

- [详细工作日志](log.md)
- [原始统计数据](stats.json)

> 注意: 仅在对应文件存在时添加链接。issues.md 和 timeline.md 为可选文件,按需生成。

---

**报告生成工具**: DevLog Skill v1.0  
**数据版本**: {{FORMAT_VERSION}}
