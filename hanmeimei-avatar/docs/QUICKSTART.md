# 韩梅梅技能 - 快速使用指南

## 前置条件

1. 确保 ComfyUI 服务器正在运行（默认地址：http://10.28.9.6:8188）
2. 确保 Python 3.7+ 已安装

## 快速开始

### 1. 首次运行（自动创建配置）

```bash
cd scripts
python selfie-v5.py
```

第一次运行时，系统会自动：
- 创建 `~/.avatar/config.json` 配置文件
- 创建 `~/.avatar/outputs/` 输出目录
- 生成一张默认图片

### 2. 基本使用

#### 随机生成（默认行为）
```bash
python selfie-v5.py
```

#### 指定场景
```bash
python selfie-v5.py --scene cafe
python selfie-v5.py --scene bedroom
python selfie-v5.py --scene library
python selfie-v5.py --scene boulevard
python selfie-v5.py --scene rooftop
python selfie-v5.py --scene park
python selfie-v5.py --scene travel
```

#### 指定种子
```bash
python selfie-v5.py --seed 86522080
```

#### 控制表情
```bash
python selfie-v5.py --smile-level 1    # 😊 温柔微笑
python selfie-v5.py --smile-level 2    # 😁 开心笑容
python selfie-v5.py --smile-level 3    # 😃 露齿微笑
python selfie-v5.py --smile-level 4    # 😄 开怀大笑
python selfie-v5.py --smile-level 5    # 🤣 爆笑
```

## 配置文件

### 编辑配置

编辑 `~/.avatar/config.json` 文件来自定义行为：

```json
{
  "comfyui": {
    "host": "http://10.28.9.6:8188",
    "client_id": "hanmeimei-avatar",
    "timeout": 600
  },
  "output": {
    "dir": "~/.avatar/outputs",
    "filename_prefix": "HMM",
    "version": "v5"
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

#### ComfyUI 配置
- `host`: ComfyUI 服务器地址（包含端口）
- `client_id`: 客户端 ID（一般不需要修改）
- `timeout`: 超时时间（秒）

#### 输出配置
- `dir`: 输出目录路径（`~` 表示工作区根目录）
- `filename_prefix`: 文件名前缀
- `version`: 版本号

#### 默认参数
- `faceid_weight`: FaceID v2 权重
- `faceid_weight_0`: FaceID 基础权重
- `cfg`: CFG 参数
- `seed`: 默认种子（null 表示随机）
- `scene`: 默认场景（null 表示随机）
- `smile_level`: 默认表情等级

## 完整参数列表

| 参数 | 说明 | 示例 |
|------|------|------|
| `--scene` | 指定场景 | `--scene cafe` |
| `--seed` | 指定种子 | `--seed 86522080` |
| `--smile-level` | 表情等级 (1-5) | `--smile-level 3` |
| `--faceid-weight` | FaceID 权重 | `--faceid-weight 0.8` |
| `--cfg` | CFG 参数 | `--cfg 4.0` |
| `--nude` | 裸体模式（⚠️ 仅用于测试） | `--nude` |
| `--add-seed` | 追加种子到好种子列表 | `--add-seed` |
| `--prompt-file` | 使用自定义提示词文件 | `--prompt-file custom.txt` |

## 输出位置

所有生成的图片统一保存在：

```
~/.avatar/outputs/
```

> **注意**：本文档中所有 `~` 均代表**工作区根目录**（如 `d:\TRAE\workspace-skills`），而非用户主目录。

文件命名规则：
```
{prefix}-{version}-{timestamp}-{seed}.png
```

示例：
```
HMM-v5-20260523123456-86522080.png
```

## 常见问题

### Q: 如何更改 ComfyUI 服务器地址？

A: 编辑 `~/.avatar/config.json`，修改 `"comfyui"."host"` 配置项。

### Q: 如何更改输出目录？

A: 编辑 `~/.avatar/config.json`，修改 `"output"."dir"` 配置项。

### Q: 连接超时怎么办？

A: 1. 检查 ComfyUI 服务器是否正常运行；2. 检查网络连接；3. 增加配置文件中的 timeout。

### Q: 提示词还会继续优化吗？

A: 是的！本次优化主要是架构层面，提示词优化会继续。

## 更新日志

### v5 (SIPOC 优化)
- ✅ 新增配置文件支持
- ✅ 统一输出目录到 `~/.avatar/outputs/`
- ✅ 保留原有手部优化（移除过度约束）
- ✅ 改进配置管理
- ✅ 向后兼容
