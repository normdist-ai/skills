# DevLog 数据源文档

## 数据源优先级

1. **对话上下文** — 最高优先级,用户直接提供的信息最准确
2. **Git提交历史** — 高价值,客观记录代码变更
3. **文件系统活动** — 补充,推断工作内容
4. **终端命令历史** — 可选,辅助了解操作

## Git 数据源

### 基础命令

```bash
# 今日提交列表
git log --since="today" --pretty=format:"%h|%s|%an|%ar" --stat

# 代码变更统计
git diff --shortstat HEAD@{"today 00:00"} HEAD@{"today 23:59"}

# 修改文件列表
git diff --name-only HEAD@{"today 00:00"} HEAD@{"today 23:59"}

# 指定日期
git log --since="2026-04-30 00:00" --until="2026-04-30 23:59" --oneline
```

### Commit 类型映射

| 前缀 | 类型 | 日志分类 |
|------|------|---------|
| `feat:` | 新功能 | 完成事项 |
| `fix:` | Bug修复 | 完成事项+问题 |
| `refactor:` | 重构 | 完成事项 |
| `docs:` | 文档 | 完成事项 |
| `test:` | 测试 | 完成事项 |
| `chore:` | 构建/工具 | 完成事项 |

### 文件类型推断

| 扩展名 | 推断活动 |
|--------|---------|
| `.py .js .ts .java .go` | 代码开发 |
| `.md .rst .txt` | 文档编写 |
| `.yml .yaml .json .toml` | 配置修改 |
| `test_* *_test.* *.spec.*` | 测试编写 |
| `.css .scss .less` | 样式开发 |

## 文件系统数据源

### Windows PowerShell

```powershell
# 查找今日修改的源代码文件
Get-ChildItem -Recurse -Include *.py,*.js,*.ts,*.java,*.go |
  Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-1) } |
  Select-Object -First 20 FullName, LastWriteTime

# 查找今日新建的文件
Get-ChildItem -Recurse |
  Where-Object { $_.CreationTime -gt (Get-Date).Date } |
  Select-Object FullName
```

## 终端命令数据源

提取有意义的操作:
- 构建: `npm run build`, `mvn package`, `cargo build`
- 测试: `npm test`, `pytest`, `go test`
- 部署: `kubectl apply`, `docker push`
- 依赖: `npm install`, `pip install`, `cargo add`

## 数据源组合策略

| 场景 | 策略 |
|------|------|
| Git有提交 | 优先使用Git数据,对话补充细节 |
| 文件有修改 | 结合文件变化询问用户 |
| 完全无数据 | 全面询问用户 |
| 信息冲突 | 用户明确提供 > Git数据 > 文件推断 |
