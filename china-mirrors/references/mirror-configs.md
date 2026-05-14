# 镜像源配置命令详解

本文档包含所有包管理器的详细配置命令，Agent 根据用户选择的包管理器执行对应命令。

---

## Python pip 配置

### Windows 全局配置

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\pip"
Set-Content -Path "$env:USERPROFILE\pip\pip.ini" -Value @"
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com

[install]
trusted-host = mirrors.aliyun.com
"@ -Encoding UTF8
Write-Host "✓ pip 已配置为阿里云镜像"
```

### Linux/Mac 全局配置

```bash
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com

[install]
trusted-host = mirrors.aliyun.com
EOF
echo "✓ pip 已配置为阿里云镜像"
```

### 项目级配置

```bash
cat > pip.conf << 'EOF'
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
EOF
echo "✓ pip 项目级配置已完成"
```

### 验证

```bash
pip config list
```

---

## Node.js npm/yarn/pnpm 配置

### 全局配置

```bash
npm config set registry https://registry.npmmirror.com
yarn config set registry https://registry.npmmirror.com 2>/dev/null || true
pnpm config set registry https://registry.npmmirror.com 2>/dev/null || true
echo "✓ Node.js 包管理器已配置"
```

### 项目级配置

```bash
echo "registry=https://registry.npmmirror.com" > .npmrc
echo "✓ npm 项目级配置已完成"
```

### 验证

```bash
npm config get registry
```

---

## Rust cargo 配置

### 全局配置

```bash
mkdir -p ~/.cargo
cat > ~/.cargo/config.toml << 'EOF'
[source.crates-io]
replace-with = 'aliyun'

[source.aliyun]
registry = "https://mirrors.aliyun.com/crates.io-index/"
EOF
echo "✓ cargo 已配置为阿里云镜像"
```

### 验证

```bash
cat ~/.cargo/config.toml
```

---

## Go mod 配置

### Windows PowerShell

```powershell
[Environment]::SetEnvironmentVariable("GOPROXY", "https://mirrors.aliyun.com/goproxy/,direct", "User")
$env:GOPROXY = "https://mirrors.aliyun.com/goproxy/,direct"
Write-Host "✓ Go GOPROXY 已配置"
```

### Linux/Mac

```bash
echo 'export GOPROXY=https://mirrors.aliyun.com/goproxy/,direct' >> ~/.bashrc
export GOPROXY=https://mirrors.aliyun.com/goproxy/,direct
echo "✓ Go GOPROXY 已配置"
```

### 验证

```bash
go env GOPROXY
```

---

## NuGet (.NET) 配置

### Windows

```powershell
$nugetPath = "$env:APPDATA\NuGet"
New-Item -ItemType Directory -Force -Path $nugetPath
Set-Content -Path "$nugetPath\NuGet.Config" -Value @"
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <clear />
    <add key="huawei" value="https://repo.huaweicloud.com/repository/nuget/v3/index.json" />
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
  </packageSources>
</configuration>
"@ -Encoding UTF8
Write-Host "✓ NuGet 已配置为华为云镜像"
```

### Linux/Mac

```bash
mkdir -p ~/.nuget
cat > ~/.nuget/NuGet.Config << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <clear />
    <add key="huawei" value="https://repo.huaweicloud.com/repository/nuget/v3/index.json" />
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
  </packageSources>
</configuration>
EOF
echo "✓ NuGet 已配置为华为云镜像"
```

### 验证

```bash
dotnet nuget list source
```

---

## RubyGems 配置

### 全局配置

```bash
gem sources --remove https://rubygems.org/ 2>/dev/null || true
gem sources -a https://mirrors.tuna.tsinghua.edu.cn/rubygems/
echo "✓ RubyGems 已配置为清华镜像"
```

### Bundler 项目级配置

```bash
bundle config mirror.https://rubygems.org https://mirrors.tuna.tsinghua.edu.cn/rubygems/
echo "✓ Bundler 镜像已配置"
```

### 验证

```bash
gem sources -l
```

---

## Conda 配置

```bash
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
conda config --set show_channel_urls yes
echo "✓ Conda 已配置为清华镜像"
```

### 验证

```bash
conda config --show channels
```

---

## Maven 配置

```bash
mkdir -p ~/.m2
cat > ~/.m2/settings.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<settings>
  <mirrors>
    <mirror>
      <id>aliyun</id>
      <mirrorOf>central</mirrorOf>
      <name>Aliyun Maven</name>
      <url>https://maven.aliyun.com/repository/public</url>
    </mirror>
  </mirrors>
</settings>
EOF
echo "✓ Maven 已配置为阿里云镜像"
```

---

## Gradle 配置

### 方式一：环境变量

```bash
mkdir -p ~/.gradle/init.d
cat > ~/.gradle/init.d/mirror.init.gradle << 'EOF'
allprojects {
    repositories {
        all { ArtifactRepository repo ->
            if (repo instanceof MavenArtifactRepository) {
                def url = repo.url.toString()
                if (url.startsWith("https://repo.maven.apache.org/maven2") ||
                    url.startsWith("https://jcenter.bintray.com")) {
                    project.logger.lifecycle "Repository ${repo.url} replaced with Tencent mirror."
                    remove repo
                }
            }
        }
        maven { url 'https://mirrors.cloud.tencent.com/nexus/repository/maven-public/' }
        maven { url 'https://maven.aliyun.com/repository/public' }
        mavenCentral()
    }
}
EOF
echo "✓ Gradle 已配置"
```

### 方式二：项目级 settings.gradle

```groovy
dependencyResolutionManagement {
    repositories {
        maven { url = uri('https://mirrors.cloud.tencent.com/gradle/') }
        mavenCentral()
    }
}
```

---

## Homebrew 配置 (macOS)

```bash
export HOMEBREW_BOTTLE_DOMAIN=https://mirrors.ustc.edu.cn/homebrew-bottles
echo 'export HOMEBREW_BOTTLE_DOMAIN=https://mirrors.ustc.edu.cn/homebrew-bottles' >> ~/.zshrc
echo "✓ Homebrew 已配置为中科大镜像"
```

---

## Composer 配置 (PHP)

```bash
composer config -g repo.packagist composer https://mirrors.aliyun.com/composer/
echo "✓ Composer 已配置为阿里云镜像"
```

---

## 恢复默认配置命令

| 包管理器 | 恢复命令 |
|---------|---------|
| pip | `rm -f ~/.pip/pip.conf` 或 `del %USERPROFILE%\pip\pip.ini` |
| npm | `npm config delete registry` |
| yarn | `yarn config delete registry` |
| pnpm | `pnpm config delete registry` |
| cargo | `rm -f ~/.cargo/config.toml` |
| Go | `unset GOPROXY` 并从 shell 配置文件中删除 |
| NuGet | 删除 `%APPDATA%\NuGet\NuGet.Config` |
| RubyGems | `gem sources --remove <mirror-url>` 并添加回 `https://rubygems.org/` |
| Conda | `conda config --remove channels <mirror-url>` |
| Homebrew | `unset HOMEBREW_BOTTLE_DOMAIN` |
