# 镜像源选择指南

本文档包含所有支持的镜像源及其选择建议。

---

## 推荐镜像源速查表

| 包管理器 | 推荐镜像 | URL | 备选1 | 备选2 |
|---------|---------|-----|-------|-------|
| **pip (Python)** | 阿里云 ⭐ | `https://mirrors.aliyun.com/pypi/simple/` | 清华大学 `https://pypi.tuna.tsinghua.edu.cn/simple/` | 腾讯云 `https://mirrors.cloud.tencent.com/pypi/simple/` |
| **npm/yarn/pnpm** | 华为云 ⭐ | `https://repo.huaweicloud.com/repository/npm/` | 阿里云 `https://registry.npmmirror.com` | 腾讯云 `https://mirrors.cloud.tencent.com/npm/` |
| **cargo (Rust)** | 阿里云 ⭐ | `https://mirrors.aliyun.com/crates.io-index/` | 清华大学 `https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/` | 中科大 `https://mirrors.ustc.edu.cn/crates.io-index/` |
| **go mod (Go)** | 阿里云 ⭐ | `https://mirrors.aliyun.com/goproxy/` | 七牛云 `https://goproxy.cn` | 官方中国 `https://goproxy.io` |
| **Maven (Java)** | 阿里云 ⭐ | `https://maven.aliyun.com/repository/public` | - | - |
| **Gradle (Java/Kotlin)** | 腾讯云 ⭐ | `https://mirrors.cloud.tencent.com/gradle/` | 阿里云 `https://maven.aliyun.com/repository/gradle-plugin/` | - |
| **NuGet (.NET)** | 华为云 ⭐ | `https://repo.huaweicloud.com/repository/nuget/v3/index.json` | 清华大学 `https://mirrors.tuna.tsinghua.edu.cn/nuget/v3/index.json` | - |
| **RubyGems (Ruby)** | 清华大学 ⭐ | `https://mirrors.tuna.tsinghua.edu.cn/rubygems/` | 中科大 `https://mirrors.ustc.edu.cn/rubygems/` | - |
| **Conda (Python)** | 清华大学 ⭐ | `https://mirrors.tuna.tsinghua.edu.cn/anaconda/` | 中科大 `https://mirrors.ustc.edu.cn/anaconda/` | - |
| **Homebrew (macOS)** | 中科大 ⭐ | `https://mirrors.ustc.edu.cn/homebrew-bottles/` | 清华大学 `https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles/` | - |
| **Composer (PHP)** | 阿里云 ⭐ | `https://mirrors.aliyun.com/composer/` | - | - |

---

## 镜像源提供商对比

| 提供商 | 速度 | 稳定性 | 服务范围 |
|-------|------|--------|---------|
| **阿里云** | ⚡ 快速 | 🚀 稳定 | pip, npm, cargo, go, maven, composer |
| **华为云** | ⚡ 快速 | 🚀 稳定 | npm, nuget |
| **清华大学** | 🚀 稳定 | 🏆 最稳定 | pip, cargo, rubygems, conda, homebrew |
| **中科大** | 🚀 稳定 | 🏆 最稳定 | cargo, rubygems, conda, homebrew |
| **腾讯云** | 🚀 良好 | ✅ 可靠 | pip, npm, gradle |
| **七牛云** | ⚡ 快速 | ✅ 可靠 | go |

---

## 选择建议

### 按场景选择

| 场景 | 推荐镜像源 | 原因 |
|------|-----------|------|
| **企业开发** | 阿里云 / 华为云 | 商业支持，SLA 保障 |
| **学术研究** | 清华大学 / 中科大 | 教育网直连，稳定性高 |
| **个人项目** | 阿里云 / 腾讯云 | 速度快，覆盖广 |
| **macOS 开发** | 中科大 / 清华大学 | Homebrew 镜像完善 |

### 按地区选择

| 地区 | 推荐镜像源 | 原因 |
|------|-----------|------|
| **华东** | 阿里云 | 服务器位于杭州，延迟最低 |
| **华北** | 清华大学 | 教育网骨干节点 |
| **华南** | 腾讯云 | 服务器位于广州/深圳 |
| **西南** | 华为云 | 服务器位于贵阳 |

---

## 常见问题处理

| 问题 | 解决方案 |
|------|---------|
| 配置后仍然慢 | 清除缓存：`pip cache purge` / `npm cache clean --force` |
| SSL 证书错误 | 添加 `trusted-host` 配置（已在配置命令中包含） |
| 权限不足 | 使用用户级配置（非系统级），避免 sudo |
| 想恢复默认 | 删除对应配置文件或执行恢复命令 |
| 特定项目需要不同镜像 | 使用项目级配置（`.npmrc` / `.piprc` / `.cargo/config.toml`） |
