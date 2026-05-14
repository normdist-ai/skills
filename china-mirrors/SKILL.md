---
name: china-mirrors
description: 使用中国国内镜像自动配置 Python pip、npm、yarn、pnpm、cargo、go mod、NuGet、RubyGems、Conda、Homebrew、Gradle 等包管理器的镜像源。当用户提到下载慢、安装依赖、配置镜像、加速包下载、设置国内源，或在中国大陆开发需要加速依赖安装时使用。支持阿里云、腾讯云、清华大学、中科大、华为云等主流镜像。检测到 package.json、requirements.txt、Cargo.toml、go.mod、Gemfile、.nuspec、environment.yml 等文件时主动建议使用此技能。
license: MIT
compatibility: Requires Python, Node.js, Rust, Go, .NET, Ruby, Conda, or Homebrew. Supports Windows, Linux, and macOS. No additional dependencies required.
metadata:
  author: normdist-ai
  version: "2.3.0"
  repository: https://github.com/normdist-ai/china-mirrors
  homepage: https://github.com/normdist-ai/china-mirrors#readme
  keywords: mirror, china, pip, npm, cargo, goproxy, nuget, rubygems, conda, homebrew
---

# 中国国内镜像源配置技能

> **核心设计理念**：本技能不附带任何预置脚本。Agent 根据本文档指导，**直接在用户计算机上执行配置命令**。

---

## Gotchas

- **Windows PowerShell 与 Bash 命令不同** — 必须根据操作系统选择正确的命令格式
- **npm/yarn/pnpm 使用同一镜像源** — 配置 npm 后，yarn 和 pnpm 需要单独配置
- **Go GOPROXY 需要环境变量** — 配置后需要重启终端或重新加载配置文件
- **NuGet 配置会清空原有源** — 配置文件中使用 `<clear />` 会移除默认源
- **Conda 配置是追加模式** — 多次执行会添加多个 channel，注意去重
- **Homebrew 仅限 macOS** — Linux 用户使用 Linuxbrew，配置略有不同
- **项目级配置优先级高于全局配置** — 检测到项目级配置文件时应优先使用

---

## 工作流程 Checklist

Progress:
- [ ] 1. 需求检测与环境分析
  - [ ] 1.1 识别触发条件
  - [ ] 1.2 检测已安装工具
  - [ ] 1.3 与用户确认配置范围
- [ ] 2. 选择镜像源
- [ ] 3. 执行配置命令
- [ ] 4. 验证配置结果
- [ ] 5. 生成配置报告

---

## Phase 1: 需求检测与环境分析

### 1.1 触发条件识别

- 用户明确提及：下载慢、安装依赖慢、配置镜像、加速下载、设置国内源
- 检测到项目包含依赖文件：`package.json`、`requirements.txt`、`Cargo.toml`、`go.mod`、`Gemfile`、`.nuspec`、`environment.yml`、`build.gradle`、`pom.xml`、`composer.json`

### 1.2 环境检测命令

**Windows PowerShell:**
```powershell
python --version 2>$null; node --version 2>$null; npm --version 2>$null
cargo --version 2>$null; go version 2>$null; dotnet --version 2>$null
ruby --version 2>$null; conda --version 2>$null; gradle --version 2>$null
```

**Linux/Mac Bash:**
```bash
for cmd in python node npm cargo go dotnet ruby conda gradle brew; do
    $cmd --version 2>/dev/null && echo "✓ $cmd available"
done
```

### 1.3 与用户确认

询问内容：
1. 需要配置哪些包管理器？（如未指定，根据项目依赖文件自动判断）
2. 有偏好的镜像源吗？（默认推荐阿里云或华为云）
3. 配置范围：全局配置 or 项目级配置？

---

## Phase 2: 选择镜像源

根据下表选择最优镜像，**标记 ⭐ 的为当前推荐**：

| 包管理器 | 推荐镜像 | URL |
|---------|---------|-----|
| **pip** | 阿里云 ⭐ | `https://mirrors.aliyun.com/pypi/simple/` |
| **npm/yarn/pnpm** | 华为云 ⭐ | `https://repo.huaweicloud.com/repository/npm/` |
| **cargo** | 阿里云 ⭐ | `https://mirrors.aliyun.com/crates.io-index/` |
| **go mod** | 阿里云 ⭐ | `https://mirrors.aliyun.com/goproxy/` |
| **Maven** | 阿里云 ⭐ | `https://maven.aliyun.com/repository/public` |
| **Gradle** | 腾讯云 ⭐ | `https://mirrors.cloud.tencent.com/gradle/` |
| **NuGet** | 华为云 ⭐ | `https://repo.huaweicloud.com/repository/nuget/v3/index.json` |
| **RubyGems** | 清华大学 ⭐ | `https://mirrors.tuna.tsinghua.edu.cn/rubygems/` |
| **Conda** | 清华大学 ⭐ | `https://mirrors.tuna.tsinghua.edu.cn/anaconda/` |
| **Homebrew** | 中科大 ⭐ | `https://mirrors.ustc.edu.cn/homebrew-bottles/` |
| **Composer** | 阿里云 ⭐ | `https://mirrors.aliyun.com/composer/` |

> 📖 完整镜像源对比和选择建议见 [references/mirror-sources.md](references/mirror-sources.md)

---

## Phase 3: 执行配置命令

> **重要**：Agent 根据用户选择的包管理器和镜像，直接在终端执行对应命令。不要创建临时脚本文件。

> 📖 完整配置命令见 [references/mirror-configs.md](references/mirror-configs.md)

### 配置命令速查

| 包管理器 | 全局配置命令 | 验证命令 |
|---------|-------------|---------|
| pip | 创建 `~/.pip/pip.ini` 或 `pip.ini` | `pip config list` |
| npm | `npm config set registry <url>` | `npm config get registry` |
| cargo | 创建 `~/.cargo/config.toml` | `cat ~/.cargo/config.toml` |
| Go | 设置 `GOPROXY` 环境变量 | `go env GOPROXY` |
| NuGet | 创建 `NuGet.Config` | `dotnet nuget list source` |
| RubyGems | `gem sources -a <url>` | `gem sources -l` |
| Conda | `conda config --add channels <url>` | `conda config --show channels` |

---

## Phase 4: 验证配置结果

### 验证循环

**步骤：验证配置是否生效**

1. 执行对应的验证命令（见上表）
2. 检查输出是否包含配置的镜像源 URL
3. 如果验证失败：
   - 查看错误信息
   - 检查配置文件路径是否正确
   - 确认环境变量是否生效（可能需要重启终端）
   - 重新执行配置命令
4. 只有验证通过才能继续

---

## Phase 5: 生成配置报告

配置完成后，向用户报告：

```
─────────────────────────────────────
✅ 配置完成！已为您配置以下镜像源：

  • pip (Python)     → 阿里云 ⚡
  • npm (Node.js)    → 华为云 ⚡  
  • cargo (Rust)     → 阿里云 ⚡

📋 下次操作建议：
  • 运行 pip install / npm install 测试速度
  • 如需恢复默认配置，请告知我
─────────────────────────────────────
```

---

## 目录结构

```
china-mirrors/
├── SKILL.md                  # 技能定义（本文件）
├── references/               # 参考文档
│   ├── mirror-configs.md     # 详细配置命令
│   └── mirror-sources.md     # 镜像源选择指南
├── LICENSE                   # MIT 许可证
├── README.md                 # 英文文档
└── README.zh.md              # 中文文档
```

---

## References

| 文档 | 内容 | 路径 |
|------|------|------|
| 镜像源配置命令详解 | 所有包管理器的详细配置命令 | [references/mirror-configs.md](references/mirror-configs.md) |
| 镜像源选择指南 | 镜像源对比、选择建议、常见问题 | [references/mirror-sources.md](references/mirror-sources.md) |

---

## Agent 执行规范

1. **直接执行**：不要创建脚本文件，直接运行 Shell 命令
2. **幂等性**：配置命令可重复执行，不会产生副作用
3. **用户确认**：修改前简要告知用户将要做什么
4. **错误处理**：如果某个工具未安装，跳过并告知用户
5. **平台适配**：自动检测操作系统，选择正确的命令格式（PowerShell vs Bash）
