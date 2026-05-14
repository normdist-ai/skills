# 远程计算机场景配置详解

本文档详细说明在 SSH 远程服务器、Docker 容器、CI/CD 环境、云服务器等场景下的镜像源配置方法。

---

## 场景一：SSH 远程服务器

### 1.1 检测远程服务器信息

连接到远程服务器后，首先检测系统类型和已安装工具：

```bash
# 检测操作系统
cat /etc/os-release 2>/dev/null || sw_vers 2>/dev/null

# 检测已安装的包管理器
for cmd in python pip node npm yarn pnpm cargo go dotnet ruby gem conda brew; do
    command -v $cmd >/dev/null 2>&1 && echo "✓ $cmd: $($cmd --version 2>&1 | head -1)"
done
```

### 1.2 配置镜像源

**在远程服务器上执行配置命令：**

```bash
# Python pip
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
EOF

# Node.js npm
npm config set registry https://registry.npmmirror.com

# Rust cargo
mkdir -p ~/.cargo
cat > ~/.cargo/config.toml << 'EOF'
[source.crates-io]
replace-with = 'aliyun'

[source.aliyun]
registry = "https://mirrors.aliyun.com/crates.io-index/"
EOF

# Go
echo 'export GOPROXY=https://mirrors.aliyun.com/goproxy/,direct' >> ~/.bashrc
source ~/.bashrc
```

### 1.3 持久化配置

**重要**：SSH 会话中的环境变量不会持久化，需要写入配置文件：

```bash
# 写入 ~/.bashrc（或 ~/.zshrc）
echo 'export GOPROXY=https://mirrors.aliyun.com/goproxy/,direct' >> ~/.bashrc
echo 'export HOMEBREW_BOTTLE_DOMAIN=https://mirrors.ustc.edu.cn/homebrew-bottles' >> ~/.bashrc

# 立即生效
source ~/.bashrc
```

### 1.4 验证配置

```bash
pip config list
npm config get registry
go env GOPROXY
```

---

## 场景二：Docker 容器

### 2.1 在 Dockerfile 中配置镜像源

**Python 项目 Dockerfile：**

```dockerfile
FROM python:3.11-slim

# 配置 pip 镜像源
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set install.trusted-host mirrors.aliyun.com

# 或者使用环境变量
ENV PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

**Node.js 项目 Dockerfile：**

```dockerfile
FROM node:20-alpine

# 配置 npm 镜像源
RUN npm config set registry https://registry.npmmirror.com

# 或者使用环境变量
ENV NPM_CONFIG_REGISTRY=https://registry.npmmirror.com

WORKDIR /app
COPY package*.json ./
RUN npm install
```

**Rust 项目 Dockerfile：**

```dockerfile
FROM rust:1.75-slim

# 配置 cargo 镜像源
RUN mkdir -p /usr/local/cargo && \
    echo '[source.crates-io]\n\
replace-with = "aliyun"\n\
\n\
[source.aliyun]\n\
registry = "https://mirrors.aliyun.com/crates.io-index/"' > /usr/local/cargo/config.toml

# 或者使用环境变量
ENV CARGO_REGISTRIES_CRATES_IO_PROTOCOL=sparse

WORKDIR /app
COPY Cargo.toml Cargo.lock ./
RUN cargo build --release
```

**Go 项目 Dockerfile：**

```dockerfile
FROM golang:1.21-alpine

# 配置 GOPROXY
ENV GOPROXY=https://mirrors.aliyun.com/goproxy/,direct

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
```

### 2.2 在运行中的容器中配置（临时）

```bash
# 进入容器
docker exec -it <container_id> /bin/sh

# 配置镜像源（容器重启后失效）
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
npm config set registry https://registry.npmmirror.com
export GOPROXY=https://mirrors.aliyun.com/goproxy/,direct
```

### 2.3 Docker Compose 配置

```yaml
version: '3.8'
services:
  app:
    build: .
    environment:
      - PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
      - NPM_CONFIG_REGISTRY=https://registry.npmmirror.com
      - GOPROXY=https://mirrors.aliyun.com/goproxy/,direct
```

---

## 场景三：CI/CD 环境

### 3.1 GitHub Actions

**使用环境变量配置：**

```yaml
name: Build and Test

on: [push, pull_request]

env:
  PIP_INDEX_URL: https://mirrors.aliyun.com/pypi/simple/
  NPM_CONFIG_REGISTRY: https://registry.npmmirror.com
  GOPROXY: https://mirrors.aliyun.com/goproxy/,direct

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install npm dependencies
        run: npm install
```

**Python 项目完整配置：**

```yaml
- name: Configure pip mirror
  run: |
    pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
    pip config set install.trusted-host mirrors.aliyun.com

- name: Install dependencies
  run: pip install -r requirements.txt
```

**Node.js 项目完整配置：**

```yaml
- name: Configure npm mirror
  run: npm config set registry https://registry.npmmirror.com

- name: Install dependencies
  run: npm install
```

### 3.2 GitLab CI

```yaml
variables:
  PIP_INDEX_URL: "https://mirrors.aliyun.com/pypi/simple/"
  NPM_CONFIG_REGISTRY: "https://registry.npmmirror.com"
  GOPROXY: "https://mirrors.aliyun.com/goproxy/,direct"

stages:
  - build
  - test

build:
  stage: build
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - python setup.py build

test:
  stage: test
  image: node:20
  script:
    - npm install
    - npm test
```

### 3.3 Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    environment {
        PIP_INDEX_URL = 'https://mirrors.aliyun.com/pypi/simple/'
        NPM_CONFIG_REGISTRY = 'https://registry.npmmirror.com'
        GOPROXY = 'https://mirrors.aliyun.com/goproxy/,direct'
    }
    
    stages {
        stage('Build') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'npm install'
            }
        }
        
        stage('Test') {
            steps {
                sh 'pytest'
                sh 'npm test'
            }
        }
    }
}
```

### 3.4 Azure Pipelines

```yaml
trigger:
- main

variables:
  PIP_INDEX_URL: 'https://mirrors.aliyun.com/pypi/simple/'
  NPM_CONFIG_REGISTRY: 'https://registry.npmmirror.com'

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.11'

- script: pip install -r requirements.txt
  displayName: 'Install Python dependencies'

- task: NodeTool@0
  inputs:
    versionSpec: '20.x'

- script: npm install
  displayName: 'Install Node.js dependencies'
```

---

## 场景四：云服务器

### 4.1 阿里云 ECS

**优先使用阿里云镜像源：**

```bash
# Python pip
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# Node.js npm
npm config set registry https://registry.npmmirror.com

# Rust cargo
mkdir -p ~/.cargo
cat > ~/.cargo/config.toml << 'EOF'
[source.crates-io]
replace-with = 'aliyun'

[source.aliyun]
registry = "https://mirrors.aliyun.com/crates.io-index/"
EOF

# Go
export GOPROXY=https://mirrors.aliyun.com/goproxy/,direct
echo 'export GOPROXY=https://mirrors.aliyun.com/goproxy/,direct' >> ~/.bashrc

# Maven
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
```

### 4.2 腾讯云 CVM

**优先使用腾讯云镜像源：**

```bash
# Python pip
pip config set global.index-url https://mirrors.cloud.tencent.com/pypi/simple/

# Node.js npm
npm config set registry https://mirrors.cloud.tencent.com/npm/

# Go
export GOPROXY=https://mirrors.cloud.tencent.com/go/,direct

# Maven
mkdir -p ~/.m2
cat > ~/.m2/settings.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<settings>
  <mirrors>
    <mirror>
      <id>tencent</id>
      <mirrorOf>central</mirrorOf>
      <name>Tencent Maven</name>
      <url>https://mirrors.cloud.tencent.com/nexus/repository/maven-public/</url>
    </mirror>
  </mirrors>
</settings>
EOF
```

### 4.3 华为云 ECS

**优先使用华为云镜像源：**

```bash
# Python pip
pip config set global.index-url https://repo.huaweicloud.com/repository/pypi/simple/

# Node.js npm
npm config set registry https://repo.huaweicloud.com/repository/npm/

# Go
export GOPROXY=https://repo.huaweicloud.com/repository/goproxy/,direct

# NuGet
dotnet nuget add source https://repo.huaweicloud.com/repository/nuget/v3/index.json -n huawei
```

### 4.4 检测云服务器厂商

```bash
# 阿里云
curl -s http://100.100.100.200/latest/meta-data/region-id 2>/dev/null && echo "阿里云"

# 腾讯云
curl -s http://metadata.tencentyun.com/latest/meta-data/region 2>/dev/null && echo "腾讯云"

# 华为云
curl -s http://169.254.169.254/openstack/latest/meta_data.json 2>/dev/null | grep -o '"region": "[^"]*"' && echo "华为云"
```

---

## 环境变量优先级

在不同场景下，环境变量的优先级不同：

| 优先级 | 配置方式 | 适用场景 |
|-------|---------|---------|
| 1 (最高) | 命令行参数 | 临时测试 |
| 2 | 环境变量 | CI/CD、Docker |
| 3 | 项目级配置文件 | 项目开发 |
| 4 | 用户级配置文件 | 本地开发 |
| 5 (最低) | 全局配置文件 | 系统默认 |

**示例：**

```bash
# 优先级最高：命令行参数
pip install --index-url https://mirrors.aliyun.com/pypi/simple/ package_name

# 优先级次之：环境变量
export PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
pip install package_name

# 优先级再次：项目级配置
# ./pip.conf 或 ./.pip/pip.conf

# 优先级较低：用户级配置
# ~/.pip/pip.conf

# 优先级最低：全局配置
# /etc/pip.conf
```

---

## 快速配置脚本

### 一键配置脚本（Linux/Mac）

```bash
#!/bin/bash
# 一键配置中国国内镜像源

# 检测云服务器厂商
detect_cloud_provider() {
    if curl -s http://100.100.100.200/latest/meta-data/region-id 2>/dev/null | grep -q .; then
        echo "aliyun"
    elif curl -s http://metadata.tencentyun.com/latest/meta-data/region 2>/dev/null | grep -q .; then
        echo "tencent"
    elif curl -s http://169.254.169.254/openstack/latest/meta_data.json 2>/dev/null | grep -q "region"; then
        echo "huawei"
    else
        echo "default"
    fi
}

# 根据云厂商选择镜像
CLOUD_PROVIDER=$(detect_cloud_provider)

case $CLOUD_PROVIDER in
    aliyun)
        PIP_MIRROR="https://mirrors.aliyun.com/pypi/simple/"
        NPM_MIRROR="https://registry.npmmirror.com"
        GO_PROXY="https://mirrors.aliyun.com/goproxy/"
        ;;
    tencent)
        PIP_MIRROR="https://mirrors.cloud.tencent.com/pypi/simple/"
        NPM_MIRROR="https://mirrors.cloud.tencent.com/npm/"
        GO_PROXY="https://mirrors.cloud.tencent.com/go/"
        ;;
    huawei)
        PIP_MIRROR="https://repo.huaweicloud.com/repository/pypi/simple/"
        NPM_MIRROR="https://repo.huaweicloud.com/repository/npm/"
        GO_PROXY="https://repo.huaweicloud.com/repository/goproxy/"
        ;;
    *)
        PIP_MIRROR="https://mirrors.aliyun.com/pypi/simple/"
        NPM_MIRROR="https://registry.npmmirror.com"
        GO_PROXY="https://mirrors.aliyun.com/goproxy/"
        ;;
esac

# 配置 pip
if command -v pip >/dev/null 2>&1; then
    mkdir -p ~/.pip
    cat > ~/.pip/pip.conf << EOF
[global]
index-url = $PIP_MIRROR
trusted-host = $(echo $PIP_MIRROR | sed 's|https://||' | sed 's|/.*||')
EOF
    echo "✓ pip 已配置"
fi

# 配置 npm
if command -v npm >/dev/null 2>&1; then
    npm config set registry $NPM_MIRROR
    echo "✓ npm 已配置"
fi

# 配置 Go
if command -v go >/dev/null 2>&1; then
    echo "export GOPROXY=${GO_PROXY},direct" >> ~/.bashrc
    export GOPROXY=${GO_PROXY},direct
    echo "✓ Go 已配置"
fi

echo "✅ 镜像源配置完成！"
```

---

## 常见问题

### Q1: SSH 连接断开后配置失效？

**原因**：环境变量只在当前会话有效。

**解决**：将配置写入 `~/.bashrc` 或 `~/.zshrc`：
```bash
echo 'export GOPROXY=https://mirrors.aliyun.com/goproxy/,direct' >> ~/.bashrc
source ~/.bashrc
```

### Q2: Docker 容器重启后配置丢失？

**原因**：容器内的修改是临时的。

**解决**：在 Dockerfile 中固化配置，或使用 volume 挂载配置文件。

### Q3: CI/CD 环境中配置不生效？

**原因**：CI/CD 环境可能覆盖了配置。

**解决**：使用环境变量方式配置，优先级最高。

### Q4: 云服务器应该选择哪个镜像源？

**建议**：优先使用同厂商镜像源，网络延迟最低，速度最快。

| 云厂商 | 推荐镜像源 |
|-------|----------|
| 阿里云 | 阿里云镜像 |
| 腾讯云 | 腾讯云镜像 |
| 华为云 | 华为云镜像 |
| 其他 | 阿里云或清华镜像 |
