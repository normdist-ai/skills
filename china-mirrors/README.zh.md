# China Mirrors - Agent 技能

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Skill Type](https://img.shields.io/badge/Type-SKILL-blue.svg)](https://agentskills.io)
[![Version](https://img.shields.io/badge/Version-2.2.0-green.svg)](https://github.com/normdist-ai/china-mirrors)

[English Documentation](README.md)

一个 Agent 技能，自动配置各种包管理器的国内镜像源，解决中国大陆开发者依赖下载缓慢的问题。

## 概述

本技能遵循 [Agent Skills 开放标准](https://agentskills.io)，完全支持 OpenClaw 平台，同时兼容 Trae、Cursor、VS Code、Claude Code 等主流 IDE。当触发时，Agent 会读取技能指令并**直接在您的系统上执行配置命令**——无需预置脚本。

> **🎯 特别说明**：本技能已针对 OpenClaw 进行优化，支持渐进式披露机制，可显著降低 Token 消耗，提升执行效率。

## 兼容性

### 支持的 IDE

本技能完全兼容以下 IDE：

| IDE | 支持状态 | 技能目录 |
|-----|---------|---------|
| **Trae** | ✅ 完全支持 | `.trae/skills/` |
| **Cursor** | ✅ 完全支持 | `.cursor/skills/` |
| **VS Code** | ✅ 完全支持 | `.vscode/skills/` |
| **OpenCode** | ✅ 完全支持 | `~/.config/opencode/skills/` |
| **Lingma** | ✅ 完全支持 | `.lingma/skills/` |
| **Windsurf** | ✅ 完全支持 | `.windsurf/skills/` |
| **Claude Code** | ✅ 完全支持 | `~/.config/claude-code/skills/` |

### 支持的 Agent 平台

本技能可在以下 Agent 平台上运行：

| 平台 | 支持状态 | 说明 |
|------|---------|------|
| **OpenClaw** | ✅ **完全支持** | 🎯 **推荐平台** - 开源自托管 Agent 平台，完美支持渐进式披露机制，优化 Token 消耗 |
| **Claude Code** | ✅ 完全支持 | Anthropic 官方 CLI 工具 |
| **其他 Agent 框架** | ✅ 兼容 | 支持 SKILL.md 规范的框架均可使用 |

#### OpenClaw 集成说明

本技能已针对 OpenClaw 进行深度优化：

- **渐进式披露**：采用三层加载机制（元数据 → 正文 → 命令），大幅降低 Token 消耗
- **无缝集成**：只需复制到 `~/.openclaw/skills/` 目录即可使用
- **安全可靠**：所有命令可审计，符合 OpenClaw 安全最佳实践
- **生产就绪**：已在 OpenClaw 生产环境中测试验证

### 技术特性

- ✅ **SKILL.md v3.0 规范**：完全符合最新规范
- ✅ **渐进式披露**：元数据 → 正文 → 执行命令，降低 Token 消耗
- ✅ **跨平台支持**：Windows (PowerShell) + Linux/macOS (Bash)
- ✅ **无脚本设计**：Agent 直接执行命令，无需预置脚本文件
- ✅ **安全可靠**：所有命令可审计，无隐藏执行逻辑

## 支持的包管理器

| 包管理器 | 配置文件 | 推荐镜像 |
|---------|---------|---------|
| **pip** (Python) | `requirements.txt`, `pyproject.toml` | 阿里云 |
| **npm/yarn/pnpm** (Node.js) | `package.json` | 华为云 |
| **cargo** (Rust) | `Cargo.toml` | 阿里云 |
| **go mod** (Go) | `go.mod` | 阿里云 |
| **NuGet** (.NET) | `.csproj`, `packages.config` | 华为云 |
| **RubyGems** (Ruby) | `Gemfile` | 清华大学 |
| **Conda** (Python) | `environment.yml` | 清华大学 |
| **Gradle** (Java/Kotlin) | `build.gradle` | 腾讯云 |
| **Maven** (Java) | `pom.xml` | 阿里云 |
| **Homebrew** (macOS) | - | 中科大 |
| **Composer** (PHP) | `composer.json` | 阿里云 |

## 安装

### 方式一：OpenClaw 安装（推荐）

```bash
# 克隆仓库
git clone https://github.com/normdist-ai/china-mirrors.git

# 复制到 OpenClaw 技能目录
cp -r china-mirrors ~/.openclaw/skills/

# 验证安装
openclaw skill list | grep china-mirrors
```

### 方式二：IDE 安装

```bash
# 克隆仓库
git clone https://github.com/normdist-ai/china-mirrors.git

# 复制到您的 IDE 技能目录
cp -r china-mirrors ~/.config/opencode/skills/
```

### 方式三：IDE 特定路径

| IDE | 技能目录 |
|-----|---------|
| **OpenClaw** | `~/.openclaw/skills/china-mirrors` |
| **Trae** | `.trae/skills/china-mirrors` |
| **Cursor** | `.cursor/skills/china-mirrors` |
| **OpenCode** | `~/.config/opencode/skills/china-mirrors` |
| **Lingma** | `.lingma/skills/china-mirrors` |

## 使用方法

### 触发短语

当您提及以下内容时，技能会自动触发：
- "下载慢"
- "安装依赖"
- "配置镜像"
- "加速下载"
- "设置国内源"

或当您的项目包含依赖文件如 `package.json`、`requirements.txt`、`Cargo.toml` 等。

### 交互示例

```
用户: pip install 太慢了，帮我配置一下

Agent: 我来帮您配置 pip 使用国内镜像源。
       检测到您的系统是 Windows，我将配置阿里云镜像...

       [执行配置命令]

       ✓ pip 已配置为阿里云镜像
       现在您可以运行 pip install 测试速度
```

## 项目结构

```
china-mirrors/
├── SKILL.md                  # 技能定义（Agent 指令）
├── LICENSE                   # MIT 许可证
├── README.md                 # 英文文档
└── README.zh.md              # 中文文档
```

## 工作原理

1. **触发**：Agent 检测到需要配置镜像
2. **加载**：Agent 读取 `SKILL.md` 获取详细指令
3. **执行**：Agent 直接在您的系统上运行 Shell 命令
4. **验证**：Agent 确认配置成功

## 支持的镜像源

| 提供商 | 速度 | 服务 |
|-------|------|------|
| **阿里云** | ⚡ 快速 | pip, npm, cargo, go, maven, composer |
| **华为云** | ⚡ 快速 | npm, nuget |
| **清华大学** | 🚀 稳定 | pip, cargo, rubygems, conda, homebrew |
| **中科大** | 🚀 稳定 | cargo, rubygems, conda, homebrew |
| **腾讯云** | 🚀 良好 | pip, npm, gradle |

## 贡献

欢迎贡献！请随时提交 Issue 或 Pull Request。

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

## 许可证

本项目基于 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 相关链接

- [SKILL.md 规范](https://github.com/402md/skillmd)
- [Microsoft Agent Skills](https://learn.microsoft.com/en-us/agent-framework/agents/skills)
- [GitHub 仓库](https://github.com/normdist-ai/china-mirrors)

---

如果这个项目对您有帮助，请给一个 ⭐ star！
