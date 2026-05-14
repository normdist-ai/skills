---
name: devlog
description: Use this skill when the user needs to record, generate, or update a development work log. Trigger on keywords like '写日报', '工作日志', '记录工作', '生成日志', '今日总结', 'devlog'. Apply even when users say '帮我记录一下今天做了什么' or '生成周报' without explicitly mentioning 'devlog'.
---

# DevLog - 开发工作日志

## 何时使用此技能

当用户需要:
- 记录每日工作内容
- 生成工作日报/周报
- 追踪问题和解决方案
- 统计工作量指标

## 工作流程

**在执行过程中,始终维护并更新以下 TodoList 以跟踪进度**:

```
任务进度跟踪:
- [ ] 步骤1: 多数据源信息收集
  - [ ] 1.1 分析对话上下文
  - [ ] 1.2 提取Git提交历史
  - [ ] 1.3 扫描文件系统活动
  - [ ] 1.4 检查终端命令历史(可选)
- [ ] 步骤2: 确定输出格式
- [ ] 步骤3: 智能信息提取和分类
- [ ] 步骤4: 生成日志内容
- [ ] 步骤5: 保存日志文件
- [ ] 步骤6: 确认和反馈
```

**使用说明**:
1. **开始时**: 复制上面的 TodoList 到回复中
2. **执行中**: 每完成一个子任务,将 `[ ]` 改为 `[x]`
3. **跳过项**: 如果某个数据源不可用,标记为 `[-]` 并说明原因

---

### 步骤1: 多数据源信息收集

按优先级从以下来源获取工作信息:

#### 1.1 对话上下文分析 (最高优先级)

分析当前对话历史(最近5-10轮),提取:
- **任务完成**: "完成了"、"修复了"、"实现了"、"提交了"
- **问题追踪**: "遇到了"、"卡在"、"报错"、"调试"
- **时间信息**: "花了X小时"、"从X点到Y点"、"上午/下午"
- **明日计划**: "明天要"、"计划做"、"待办"

#### 1.2 Git提交历史 (高价值)

检查是否为Git仓库,如果是则获取今日提交:

```bash
# 提交列表
git log --since="today" --pretty=format:"%h|%s|%an|%ar" --stat

# 代码变更统计
git diff --shortstat HEAD@{"today 00:00"} HEAD@{"today 23:59"}

# 修改文件列表
git diff --name-only HEAD@{"today 00:00"} HEAD@{"today 23:59"}
```

**Windows PowerShell 替代**:
```powershell
New-Item -ItemType Directory -Force -Path ".devlog/YYYY-MM-DD"
```

**Commit类型映射**: `feat:` → 新功能, `fix:` → Bug修复, `refactor:` → 重构, `docs:` → 文档, `test:` → 测试, `chore:` → 构建/工具

> 详细的数据源使用方法请参考 `references/data-sources.md`

#### 1.3 文件系统活动 (补充)

查找今日修改的关键文件:

```powershell
Get-ChildItem -Recurse -Include *.py,*.js,*.ts,*.java,*.go |
  Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-1) } |
  Select-Object -First 20 FullName, LastWriteTime
```

#### 1.4 终端命令历史 (可选)

提取今日执行的命令,过滤有意义的操作(构建/测试/部署/依赖管理)。

#### 1.5 主动询问策略

当数据源信息不足时,主动询问:
- "今天主要做了哪些工作?"
- "有没有遇到什么技术问题?"
- "明天的计划是什么?"

**优先级判断**: Git有提交 → 优先使用Git数据; 文件有修改 → 结合文件变化询问; 完全无数据 → 全面询问

---

### 步骤2: 确定输出格式

询问用户偏好或使用默认:
- **标准模板** (推荐): 结构化字段,适合正式汇报 → 读取 `templates/standard.md`
- **时间线**: 简洁时序记录,适合快速回顾 → 读取 `templates/timeline.md`

如果用户未指定,默认使用标准模板格式。

---

### 步骤3: 智能信息提取和分类

从收集的信息中提取并分类:

**完成事项**: 关键词匹配("完成了"、"实现了"、"修复了") + Git commit解析 + 文件修改推断
**问题追踪**: 识别问题→根因→解决方案的完整链路,结构化为: 标题/详情/原因/方案/耗时/状态
**时间信息**: 解析明确时间段("9:00-12:00")、模糊时间("上午")、相对时间("花了2小时")
**明日计划**: 识别"明天要"、"计划做"、"继续"等表达
**工作量统计**: 工作时长、任务数、提交数、代码行数变化

**信息冲突处理**: 用户明确提供 > Git数据 > 文件推断; 合并去重,标注来源

> 详细的提取规则和示例请参考 `references/best-practices.md`

---

### 步骤4: 生成日志内容

根据选择的格式,读取对应的模板文件并填充内容:
- 标准模板: 读取 `templates/standard.md`
- 时间线模板: 读取 `templates/timeline.md`

**默认生成文件**:
- `log.md` — 主要工作日志
- `stats.json` — 统计数据
- `stats.md` — 可视化报表 (自动生成)

**可选文件**:
- `issues.md` — 问题追踪 (仅当有问题时)
- `timeline.md` — 时间线格式 (用户要求时)

---

### 步骤5: 保存日志文件

1. **创建目录**: `.devlog/YYYY-MM-DD/`
   ```powershell
   New-Item -ItemType Directory -Force -Path ".devlog/YYYY-MM-DD"
   ```

2. **文件命名** (核心分离方案):

   | 文件 | 内容 | 生成规则 |
   |------|------|---------|
   | `log.md` | 主要工作日志 | 默认生成 |
   | `stats.json` | 统计数据 | 默认生成 |
   | `stats.md` | 可视化报表 | 默认生成 |
   | `issues.md` | 问题追踪 | 有问题时生成 |
   | `timeline.md` | 时间线格式 | 用户要求时生成 |

3. **处理文件冲突**: 如果文件已存在,询问用户: 覆盖/追加/创建备份

4. **更新总索引**: 在 `.devlog/index.md` 中添加或更新当日条目

---

### 步骤6: 确认和反馈

1. 展示完整的 TodoList(所有项为 `[x]` 或 `[-]`)
2. 总结生成的内容(日期/格式/数据源/生成内容/保存位置)
3. 提供后续操作建议

---

## Gotchas and Common Mistakes

- **Windows兼容性**: 使用 `New-Item -ItemType Directory -Force` 而非 `mkdir -p`; Git命令中避免 `wc -l` 等Unix-only工具
- **文件名一致性**: 主日志文件统一为 `log.md`,不要使用 `standard.md`
- **SKILL.md行数**: 本技能因功能复杂适度超出500行建议,但核心流程保持精简,详细内容外移至 references/
- **Mermaid兼容性**: `xychart-beta` 是实验性语法,在部分渲染器中不支持,优先使用 `pie` 图表
- **断链风险**: 生成 stats.md 时,仅链接实际存在的文件,issues.md 和 timeline.md 为可选

## References

- `references/data-sources.md` — 数据源详细文档(Git/文件系统/终端/IDE等)
- `references/best-practices.md` — 编写规范、提取规则、案例分析
- `references/stats-format.md` — stats.json 格式规范
- `references/todolist-guide.md` — TodoList 跟踪使用指南
- `templates/standard.md` — 标准模板输出格式
- `templates/timeline.md` — 时间线模板输出格式
- `templates/stats-report.md` — 可视化报表模板
- `scripts/stats.py` — 工作量统计脚本(支持日报/周报/月报)
