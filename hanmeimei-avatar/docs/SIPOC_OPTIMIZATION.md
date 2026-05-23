# SIPOC 优化说明

## 概述

本次优化基于 SIPOC（Supplier-Input-Process-Output-Customer）方法论，对韩梅梅技能进行了系统性重构，主要解决了以下问题：

1. 输入配置分散且不够灵活
2. 输出位置不统一
3. 缺少标准化的配置管理

## SIPOC 映射

| 组件 | 描述 |
|------|------|
| **Supplier** | 用户、配置文件 |
| **Input** | 配置、场景、种子等参数 |
| **Process** | 提示词构建 → 工作流执行 → 图片生成 |
| **Output** | 生成的图片到统一位置 |
| **Customer** | 用户、下游系统 |

## 文件结构变更

```
~/.avatar/              # ~/ 代表工作区根目录
├── config.json          # 配置文件
├── outputs/             # 统一输出目录（新生成的图片，保留30天）
│   └── HMM-v5-*.png
├── album/               # 精选照片（手动挑选的优质输出，永久保存）
│   ├── photo_*.png
│   └── photo_*.json
└── profile/             # 角色配置
    └── wardrobe.md      # 衣橱配置
```

> **注意**：本文档中所有 `~` 均代表**工作区根目录**（如 `d:\TRAE\workspace-skills`），而非用户主目录。

## 自动化功能

### 1. 首次运行自动创建目录

脚本首次运行时，会自动创建以下目录结构：
- `~/.avatar/`
- `~/.avatar/outputs/`
- `~/.avatar/album/`
- `~/.avatar/profile/`

### 2. 自动清理旧图片

每次运行时，自动清理 `outputs/` 目录中超过 30 天的图片文件。
- **保留期限**：30 天
- **清理范围**：仅清理 `outputs/` 目录
- **不受影响**：`album/` 目录中的精选照片永久保存

### 3. ComfyUI 服务器缓存自动删除

**需要安装 ComfyUI-api-tools 扩展**。

安装方法：
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/brantje/ComfyUI-api-tools
# 重启 ComfyUI 服务器
```

功能特性：
- **自动删除**：下载图片后自动删除服务器缓存（默认开启）
- **手动清理**：使用定时任务脚本批量清理服务器缓存
- **可配置**：在 `config.json` 中设置 `comfyui.auto_delete: false` 关闭自动删除

配置项：
```json
{
  "comfyui": {
    "auto_delete": true  // 下载后自动删除服务器缓存
  }
}
```

手动清理命令：
```bash
py scripts\scheduler.py --cleanup-comfyui
```

### 4. 收藏照片到相册

使用 `--save-to-album` 参数，将当前生成的照片保存到精选相册：

```bash
python selfie-v5.py --save-to-album --album-notes "用户喜欢的照片"
```

保存时会同时生成：
- 图片文件：与 outputs 一致的命名 `{prefix}-{timestamp}-{seed}.png`
- 元数据文件：`{prefix}-{timestamp}-{seed}.json`（包含种子、提示词、参数等信息）

## 配置文件

`~/.avatar/config.json` 格式：

```json
{
  "comfyui": {
    "host": "http://10.28.9.6:8188",
    "client_id": "hanmeimei-avatar",
    "timeout": 600,
    "auto_delete": true
  },
  "output": {
    "dir": "~/.avatar/outputs",
    "filename_prefix": "HMM",
    "version": "v5",
    "retention_days": 30
  },
  "defaults": {
    "faceid_weight": 0.80,
    "faceid_weight_0": 1.0,
    "cfg": 4.0,
    "seed": null,
    "scene": null,
    "smile_level": null
  }
}
```

### 配置项说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `comfyui.auto_delete` | 下载后自动删除服务器缓存（需 ComfyUI-api-tools） | true |
| `output.retention_days` | outputs 文件夹中图片保留天数 | 30 |

## 改动内容

### 1. 新增配置文件加载

- 脚本自动从 `~/.avatar/config.json` 读取配置
- 如果配置文件不存在，使用默认值
- 支持配置文件中的默认值覆盖命令行参数

### 2. 统一输出目录

- 所有生成的图片统一输出到 `~/.avatar/outputs/`
- 文件命名规则：`{prefix}-{timestamp}-{seed}.png`
- 自动创建输出目录（如果不存在）

### 3. 保持原有功能

- 手部优化（移除过度约束，让模型自己发挥）
- 多场景支持
- 种子管理
- FaceID 支持
- 表情等级

## 使用方法

### 基本使用

```bash
python selfie-v5.py
```

### 指定场景

```bash
python selfie-v5.py --scene cafe
python selfie-v5.py --scene bedroom
python selfie-v5.py --scene library
```

### 指定种子

```bash
python selfie-v5.py --seed 86522080
```

### 收藏到相册

```bash
python selfie-v5.py --save-to-album --album-notes "用户喜欢的照片"
```

### 配置文件定制

编辑 `~/.avatar/config.json` 来自定义：

1. 修改 ComfyUI 服务器地址
2. 更改默认参数
3. 调整输出位置

## 对比说明

| 项目 | 之前 | 现在 |
|------|------|------|
| **输出位置** | 技能目录下的 outputs | `~/.avatar/outputs/` |
| **配置方式** | 代码硬编码 | 配置文件 |
| **ComfyUI 地址** | 固定 | 可配置 |
| **默认参数** | 脚本内定义 | 配置文件 |
| **精选照片** | 无 | `~/.avatar/album/` |
| **自动清理** | 无 | 30天滚动删除 |
| **衣橱配置** | 无 | `~/.avatar/profile/wardrobe.md` |

## 注意事项

1. 配置文件路径：`~/.avatar/config.json`
2. 输出目录：`~/.avatar/outputs/`（自动创建，30天后自动清理）
3. 精选相册：`~/.avatar/album/`（永久保存）
4. 保持与原脚本的向后兼容
5. 如果配置文件不存在，使用默认值

## 下一步优化

1. 集成手部 LoRA（待 LoRA 文件准备好）
2. 性能优化（可选）
3. 更丰富的配置选项
