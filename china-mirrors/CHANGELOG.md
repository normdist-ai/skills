# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2026-04-11

### Changed

- **Project Structure**: Removed redundant `release/` directory to simplify project structure
- **Version Control**: Added `.gitignore` file to exclude unnecessary files

### Added

- **Documentation**: Added `CHANGELOG.md` to track project changes
- **Version Control**: `.gitignore` now excludes `.pdca/` directory and common IDE files

## [2.1.1] - 2026-04-09

### Changed

- **Documentation**: Optimized SKILL.md description field for better clarity and natural expression
  - Before: "自动配置 Python pip、npm...等包管理器的国内镜像源。使用当用户提到..."
  - After: "使用中国国内镜像自动配置 Python pip、npm...等包管理器的镜像源。当用户提到...时使用。"

## [2.1.0] - 2026-04-09

### Added

- **Metadata Fields**: Enhanced SKILL.md with comprehensive metadata
  - Added `compatibility` field: Specifies environment requirements (Python, Node.js, Rust, Go, .NET, Ruby, Conda, Homebrew)
  - Added `metadata` field: Includes author, version, repository, homepage, and keywords
- **Configuration Validation**: Added commands to verify mirror configuration for each package manager
- **Rollback Instructions**: Added complete instructions to restore default configuration
- **Troubleshooting Guide**: Added troubleshooting section for common issues

### Changed

- **Specification Compliance**: Achieved 100% compliance with Agent Skills open standard (https://agentskills.io)
- **Documentation**: Updated README files to reference authoritative Agent Skills specification

## [2.0.0] - 2026-04-08

### Changed

- **Architecture**: Transformed from script-based to Agent-executable instructions
  - Removed all pre-packaged script files
  - Agent now reads SKILL.md and executes commands directly on user's system
- **Project Structure**: Optimized project structure
  - Moved SKILL.md to root directory for single-skill project
  - Deleted `skills/` directory
  - Simplified installation instructions

### Removed

- **Scripts**: Removed all pre-packaged script files (no longer needed)
- **Redundant Directories**: Removed `skills/` directory structure

### Added

- **Progressive Disclosure**: Implemented three-layer loading mechanism (Metadata → Instructions → Commands)
- **Cross-Platform Support**: Added both Windows (PowerShell) and Linux/macOS (Bash) commands
- **Security**: All commands are now auditable with no hidden execution logic

## [1.0.0] - Initial Release

### Added

- Initial release with script-based mirror configuration
- Support for multiple package managers: pip, npm, yarn, pnpm, cargo, go mod, NuGet, RubyGems, Conda, Homebrew, Gradle, Maven, Composer
- Pre-packaged configuration scripts
- Basic documentation in Chinese and English

---

## Version History Summary

| Version | Release Date | Key Changes |
|---------|-------------|-------------|
| **2.2.0** | 2026-04-11 | Project structure optimization, added CHANGELOG.md and .gitignore |
| **2.1.1** | 2026-04-09 | Optimized description text |
| **2.1.0** | 2026-04-09 | Enhanced specification compliance and functionality |
| **2.0.0** | 2026-04-08 | Agent self-executing version, removed scripts |
| **1.0.0** | - | Initial release |

---

## Upgrade Guide

### From v2.1.x to v2.2.0

No breaking changes. Simply update to the new version:

```bash
git pull origin master
```

### From v1.x to v2.0.0

**Breaking Change**: v2.0.0 removed all pre-packaged scripts. The Agent now executes commands directly based on SKILL.md instructions.

**Migration Steps**:
1. Update to v2.0.0 or later
2. No manual configuration needed - the Agent will handle everything
3. Enjoy simplified project structure and better security

---

## Roadmap

### Planned for v2.3.0

- [ ] Add automated testing for SKILL.md format validation
- [ ] Add mirror availability detection
- [ ] Add automatic fastest mirror selection
- [ ] Add configuration progress visualization

### Long-term Goals

- [ ] Support more package managers
- [ ] Add configuration history tracking
- [ ] Add one-click restore functionality
- [ ] Community-contributed mirror sources

---

[2.2.0]: https://github.com/normdist-ai/china-mirrors/compare/v2.1.1...v2.2.0
[2.1.1]: https://github.com/normdist-ai/china-mirrors/compare/v2.1.0...v2.1.1
[2.1.0]: https://github.com/normdist-ai/china-mirrors/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/normdist-ai/china-mirrors/compare/v1.0.0...v2.0.0
