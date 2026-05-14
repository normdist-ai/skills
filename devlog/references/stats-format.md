# 统计数据格式规范

本文档定义 `stats.json` 的标准格式,便于程序处理和可视化。

## 基础结构

```json
{
  "date": "2026-04-30",
  "generated_at": "2026-04-30T23:50:00Z",
  "format_version": "1.0",
  "metrics": {
    "work_hours": 3.5,
    "tasks_completed": 10,
    "tasks_in_progress": 2,
    "commits": 5,
    "lines_added": 6500,
    "lines_removed": 0,
    "files_changed": 12,
    "issues_found": 2,
    "issues_resolved": 2,
    "meetings": 1,
    "code_reviews": 0
  },
  "sources_used": [
    "dialogue_context",
    "git_history",
    "file_system"
  ],
  "tags": ["skill-development", "documentation", "optimization"]
}
```

## 字段说明

### 元数据

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `date` | string | ✅ | 日志日期 (YYYY-MM-DD) |
| `generated_at` | string | ✅ | 生成时间 (ISO 8601) |
| `format_version` | string | ✅ | 格式版本号 |

### 指标 (metrics)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `work_hours` | number | ✅ | 工作时长(小时) |
| `tasks_completed` | number | ✅ | 完成任务数 |
| `tasks_in_progress` | number | ❌ | 进行中任务数 |
| `commits` | number | ❌ | Git提交次数 |
| `lines_added` | number | ❌ | 新增代码行数 |
| `lines_removed` | number | ❌ | 删除代码行数 |
| `files_changed` | number | ❌ | 修改文件数 |
| `issues_found` | number | ❌ | 发现问题数 |
| `issues_resolved` | number | ❌ | 解决问题数 |
| `meetings` | number | ❌ | 会议次数 |
| `code_reviews` | number | ❌ | Code Review次数 |

### 其他字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `sources_used` | array | ❌ | 使用的数据源列表 |
| `tags` | array | ❌ | 标签列表 |
| `notes` | string | ❌ | 备注信息 |

## 扩展示例

### 包含时间分配

```json
{
  "date": "2026-04-30",
  "metrics": {
    "work_hours": 8.0,
    "time_allocation": {
      "coding": 4.5,
      "meeting": 1.5,
      "review": 1.0,
      "learning": 1.0
    }
  }
}
```

### 包含项目信息

```json
{
  "date": "2026-04-30",
  "project": "devlog-skill",
  "metrics": {
    "work_hours": 3.5,
    "tasks_completed": 10
  },
  "breakdown_by_project": {
    "devlog-skill": {
      "hours": 3.5,
      "tasks": 10,
      "commits": 0
    }
  }
}
```

## 使用场景

### 1. 周统计汇总

```python
import json
import glob

def weekly_stats(week_start, week_end):
    total = {
        'work_hours': 0,
        'tasks_completed': 0,
        'commits': 0
    }
    
    for file in glob.glob(f'.devlog/{week_start}_*/stats.json'):
        with open(file) as f:
            data = json.load(f)
            total['work_hours'] += data['metrics']['work_hours']
            total['tasks_completed'] += data['metrics']['tasks_completed']
            total['commits'] += data['metrics'].get('commits', 0)
    
    return total
```

### 2. 趋势分析

```python
import matplotlib.pyplot as plt
import json

def plot_work_hours_trend(month):
    dates = []
    hours = []
    
    for day in range(1, 31):
        file = f'.devlog/2026-{month}-{day:02d}/stats.json'
        try:
            with open(file) as f:
                data = json.load(f)
                dates.append(day)
                hours.append(data['metrics']['work_hours'])
        except FileNotFoundError:
            pass
    
    plt.plot(dates, hours)
    plt.xlabel('Day')
    plt.ylabel('Work Hours')
    plt.title(f'Work Hours Trend - 2026-{month}')
    plt.show()
```

### 3. 问题统计

```python
def monthly_issues(month):
    issues = []
    
    for day in range(1, 31):
        file = f'.devlog/2026-{month}-{day:02d}/issues.md'
        try:
            with open(file) as f:
                content = f.read()
                # 解析问题数量和类型
                issues.extend(parse_issues(content))
        except FileNotFoundError:
            pass
    
    return summarize_issues(issues)
```

## 版本历史

### v1.0 (2026-04-30)
- 初始版本
- 包含基础指标
- 支持数据源和标签

### 计划中的扩展
- v1.1: 添加时间分配细分
- v1.2: 支持多项目统计
- v1.3: 添加质量指标(测试覆盖率等)

---

**维护者**: DevLog Skill Team  
**最后更新**: 2026-04-30
