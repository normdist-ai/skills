# China Mirrors - Agent Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Skill Type](https://img.shields.io/badge/Type-SKILL-blue.svg)](https://agentskills.io)
[![Version](https://img.shields.io/badge/Version-2.2.0-green.svg)](https://github.com/normdist-ai/china-mirrors)

[中文文档](README.zh.md)

An Agent Skill that automatically configures domestic mirror sources for various package managers in China, solving dependency download speed issues for developers.

## Overview

This skill follows the [Agent Skills open standard](https://agentskills.io), fully supports OpenClaw platform, and is compatible with mainstream IDEs like Trae, Cursor, VS Code, Claude Code, etc. When triggered, the Agent reads the skill instructions and **directly executes configuration commands** on your system — no pre-packaged scripts required.

> **🎯 Special Note**: This skill is optimized for OpenClaw with progressive disclosure support, significantly reducing token consumption and improving execution efficiency.

## Compatibility

### Supported IDEs

This skill is fully compatible with the following IDEs:

| IDE | Support Status | Skills Directory |
|-----|---------------|-----------------|
| **Trae** | ✅ Fully Supported | `.trae/skills/` |
| **Cursor** | ✅ Fully Supported | `.cursor/skills/` |
| **VS Code** | ✅ Fully Supported | `.vscode/skills/` |
| **OpenCode** | ✅ Fully Supported | `~/.config/opencode/skills/` |
| **Lingma** | ✅ Fully Supported | `.lingma/skills/` |
| **Windsurf** | ✅ Fully Supported | `.windsurf/skills/` |
| **Claude Code** | ✅ Fully Supported | `~/.config/claude-code/skills/` |

### Supported Agent Platforms

This skill runs on the following Agent platforms:

| Platform | Support Status | Description |
|----------|---------------|-------------|
| **OpenClaw** | ✅ **Fully Supported** | 🎯 **Recommended Platform** - Open-source self-hosted Agent platform with perfect progressive disclosure support and optimized token consumption |
| **Claude Code** | ✅ Fully Supported | Anthropic's official CLI tool |
| **Other Agent Frameworks** | ✅ Compatible | Any framework supporting SKILL.md specification |

#### OpenClaw Integration Details

This skill is deeply optimized for OpenClaw:

- **Progressive Disclosure**: Three-layer loading mechanism (Metadata → Instructions → Commands) significantly reduces token consumption
- **Seamless Integration**: Simply copy to `~/.openclaw/skills/` directory to use
- **Secure & Reliable**: All commands are auditable, compliant with OpenClaw security best practices
- **Production Ready**: Tested and validated in OpenClaw production environments

### Technical Features

- ✅ **SKILL.md v3.0 Specification**: Fully compliant with the latest standard
- ✅ **Progressive Disclosure**: Metadata → Instructions → Commands, reducing token consumption
- ✅ **Cross-Platform**: Windows (PowerShell) + Linux/macOS (Bash)
- ✅ **No Scripts Design**: Agent executes commands directly, no pre-packaged script files
- ✅ **Secure & Reliable**: All commands are auditable, no hidden execution logic

## Supported Package Managers

| Package Manager | Config File | Recommended Mirror |
|----------------|-------------|-------------------|
| **pip** (Python) | `requirements.txt`, `pyproject.toml` | Aliyun |
| **npm/yarn/pnpm** (Node.js) | `package.json` | Huawei Cloud |
| **cargo** (Rust) | `Cargo.toml` | Aliyun |
| **go mod** (Go) | `go.mod` | Aliyun |
| **NuGet** (.NET) | `.csproj`, `packages.config` | Huawei Cloud |
| **RubyGems** (Ruby) | `Gemfile` | Tsinghua |
| **Conda** (Python) | `environment.yml` | Tsinghua |
| **Gradle** (Java/Kotlin) | `build.gradle` | Tencent Cloud |
| **Maven** (Java) | `pom.xml` | Aliyun |
| **Homebrew** (macOS) | - | USTC |
| **Composer** (PHP) | `composer.json` | Aliyun |

## Installation

### Option 1: OpenClaw Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/normdist-ai/china-mirrors.git

# Copy to OpenClaw skills directory
cp -r china-mirrors ~/.openclaw/skills/

# Verify installation
openclaw skill list | grep china-mirrors
```

### Option 2: IDE Installation

```bash
# Clone the repository
git clone https://github.com/normdist-ai/china-mirrors.git

# Copy to your IDE's skills directory
cp -r china-mirrors ~/.config/opencode/skills/
```

### Option 3: IDE-Specific Paths

| IDE | Skills Directory |
|-----|-----------------|
| **OpenClaw** | `~/.openclaw/skills/china-mirrors` |
| **Trae** | `.trae/skills/china-mirrors` |
| **Cursor** | `.cursor/skills/china-mirrors` |
| **OpenCode** | `~/.config/opencode/skills/china-mirrors` |
| **Lingma** | `.lingma/skills/china-mirrors` |

## Usage

### Trigger Phrases

The skill is automatically triggered when you mention:
- "下载慢" (download slow)
- "安装依赖" (install dependencies)
- "配置镜像" (configure mirror)
- "加速下载" (accelerate download)
- "设置国内源" (set domestic source)

Or when your project contains dependency files like `package.json`, `requirements.txt`, `Cargo.toml`, etc.

### Example Interaction

```
User: pip install 太慢了，帮我配置一下

Agent: 我来帮您配置 pip 使用国内镜像源。
       检测到您的系统是 Windows，我将配置阿里云镜像...

       [Executes configuration commands]

       ✓ pip 已配置为阿里云镜像
       现在您可以运行 pip install 测试速度
```

## Project Structure

```
china-mirrors/
├── SKILL.md                  # Skill definition (Agent instructions)
├── LICENSE                   # MIT License
├── README.md                 # English documentation
└── README.zh.md              # Chinese documentation
```

## How It Works

1. **Trigger**: Agent detects the need for mirror configuration
2. **Load**: Agent reads `SKILL.md` for detailed instructions
3. **Execute**: Agent runs shell commands directly on your system
4. **Verify**: Agent confirms the configuration is successful

## Supported Mirrors

| Provider | Speed | Services |
|----------|-------|----------|
| **Aliyun** | ⚡ Fast | pip, npm, cargo, go, maven, composer |
| **Huawei Cloud** | ⚡ Fast | npm, nuget |
| **Tsinghua University** | 🚀 Stable | pip, cargo, rubygems, conda, homebrew |
| **USTC** | 🚀 Stable | cargo, rubygems, conda, homebrew |
| **Tencent Cloud** | 🚀 Good | pip, npm, gradle |

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [SKILL.md Specification](https://github.com/402md/skillmd)
- [Microsoft Agent Skills](https://learn.microsoft.com/en-us/agent-framework/agents/skills)
- [GitHub Repository](https://github.com/normdist-ai/china-mirrors)

---

If this project helps you, please give it a ⭐ star!
