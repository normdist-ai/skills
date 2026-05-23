# 韩梅梅形象生成技能

基于 ComfyUI 的 AI 写真照片生成技能，支持 FaceID 面部一致性保持、四维环境感知自拍、多场景生活化生成。

## 仓库地址

- GitHub: [https://github.com/normdist-ai/skills/tree/main/hanmeimei-avatar](https://github.com/normdist-ai/skills.git)
- Gitee: [https://gitee.com/normdist/skills/tree/main/hanmeimei-avatar](https://gitee.com/normdist/skills.git)


## 特性

- ✅ **FaceID 面部一致性**：使用 IPAdapter FaceID 保持韩梅梅的脸型特征
- ✅ **四维环境感知**：根据季节、时段、天气自动选择场景和光线
- ✅ **多场景生活化**：7 种生活场景（卧室、咖啡厅、图书馆、林荫道、屋顶、旅行、公园）
- ✅ **智能穿搭系统**：根据场景和时段自动选择穿搭
- ✅ **种子池管理**：优质种子池，自动筛选和复现好图
- ✅ **SIPOC 优化**：统一输出目录管理（~/.avatar/）
- ✅ **远程删除**：SSH 方式清理服务器缓存
- ✅ **定时任务**：自动定时出图和清理
- ✅ **多平台发送**：支持飞书、Trae 等平台

## 工作流程

### 1. 整体架构（v5）

```
用户调用
    ↓
selfie-v5.py (v5 主入口 — 种子池版 + SIPOC)
    ↓ 读取 good-seeds.txt（优质种子池）
prompts/base.txt + prompts/{scene}.txt
    ↓ 读取
workflows/faceid.json
    ↓ 调用
comfyui_client.py
    ↓ 调用
远程服务器 (10.28.9.6:8188)
    ↓ 执行工作流
输出图片 → ~/.avatar/outputs/
    ↓ 消息格式
trae_sender.py / feishu_sender.py
```

### 2. v5 自拍工作流

**用途**：种子池版，带 SIPOC 优化，支持定时任务

```
步骤 1: 环境感知
    ├─ get_season() → 春/夏/秋/冬
    ├─ get_period() → morning/forenoon/noon/afternoon/evening/night
    └─ get_weather() → 晴天/阴天/雨天/雪天 + 温度
    ↓
步骤 2: 场景选择
    ├─ 从 ROUTINES[季节][时段] 随机选择
    └─ apply_weather_mod() 天气修正光线
    ↓
步骤 3: 种子选择
    ├─ 默认从 good-seeds.txt 随机选择
    ├─ --seed N 指定种子
    └─ --random-seed 探索新种子
    ↓
步骤 4: 参数构建
    ├─ get_outfit(场景, 时段) → 穿搭描述
    ├─ get_expression(场景) → 表情描述
    ├─ get_background(场景) → 背景描述
    └─ get_random_face_reference() → 脸部参考图片
    ↓
步骤 5: 工作流构建
    ├─ 读取 faceid.json
    ├─ update_prompt() 替换所有参数
    ├─ 设置种子
    └─ 设置脸部参考图片
    ↓
步骤 6: 执行生成
    ├─ 创建 ComfyUIClient 实例
    ├─ client.run_workflow() 执行
    └─ 重命名输出文件（HMM-YYYYMMDD-HHMMSS-种子.png）
    ↓
步骤 7: SIPOC 输出
    ├─ 图片存入 ~/.avatar/outputs/
    ├─ 30 天自动清理旧图
    └─ 消息输出（Trae/飞书格式）
```

### 3. 远程删除工作流

**用途**：SSH 方式删除 ComfyUI 服务器缓存

```
deletefile.py
    ↓
SSH 连接到 10.28.9.6
    ↓
执行 rm / find 命令
    ↓
删除指定文件 / 批量清理旧文件
```

### 4. 定时任务工作流

**用途**：定时出图和自动清理

```
scheduler.py
    ├─ 定时生成（每 30 分钟）
    │   └─ 调用 selfie-v5.py
    │       └─ feishu_sender.py（飞书三气泡发送）
    └─ 定时清理（每天凌晨）
        └─ 调用 deletefile.py
            └─ 清理 30 天以上旧图
```

## 快速开始

### 安装依赖

```bash
pip install requests pyyaml
```

### 基础使用

#### 1. v5 自拍（推荐）

```bash
# 默认生成（从种子池随机选择）
python scripts/selfie-v5.py

# 指定场景
python scripts/selfie-v5.py --scene cafe

# 指定种子
python scripts/selfie-v5.py --seed 86522080

# 完全随机种子（探索新图）
python scripts/selfie-v5.py --random-seed

# 添加当前种子到优质池
python scripts/selfie-v5.py --seed 86522080 --add-seed
```

#### 2. 种子池管理

```bash
# 查看种子池
python scripts/seed_pool.py list

# 随机选一个种子
python scripts/seed_pool.py pick

# 添加种子到池
python scripts/seed_pool.py add 86522080
```

#### 3. 远程删除

```bash
# 删除单个文件
python scripts/deletefile.py --file HMM-FaceID_00257_.png

# 批量清理（默认 30 天）
python scripts/deletefile.py --cleanup --pattern "HMM-*.png"

# 指定保留天数
python scripts/deletefile.py --cleanup --pattern "HMM-*.png" --retention-days 7
```

#### 4. 发送到平台

```bash
# Trae 平台（渲染 Markdown 格式）
cat output.txt | python scripts/trae_sender.py

# 飞书平台（三气泡发送）
cat output.txt | python scripts/feishu_sender.py
```

#### 5. 定时任务

```bash
# 启动定时任务
python scripts/scheduler.py
```

### 输出格式

#### v5 输出（Trae 格式）

```
[HMM-20260524002840-623676467.png](file:///path/to/output.png)
---
时间：2026-05-24 00:28:40
地点：卧室
种子：623676467
---
在床上看论文，看着看着就困了
```

#### v5 输出（飞书格式 - 通过 feishu_sender.py）

```
图片（上传并发送）
时间：2026-05-24 00:28:40
地点：卧室
种子：623676467
---
想法文字（单独气泡）
```

## SIPOC 目录结构

### 统一输出目录（~/.avatar/）

```
~/.avatar/                      # ~/ 代表工作区根目录
├── config.json                 # 配置文件
├── outputs/                    # 新生成图片（30 天自动清理）
│   └── HMM-*.png
└── album/                      # 精选照片
    └── HMM-*.png
```

### 技能目录

```
hanmeimei-avatar/
├── SKILL.md                    # 技能元数据
├── prompts/                    # 提示词文件
│   ├── base.txt                # 基础提示词
│   ├── message-template.txt    # 消息模板
│   ├── bedroom.txt
│   ├── cafe.txt
│   ├── library.txt
│   ├── rooftop.txt
│   ├── park.txt
│   └── travel.txt
├── workflows/                  # 工作流文件
│   ├── default.json
│   ├── faceid.json
│   └── base.json
├── scripts/                    # 脚本文件
│   ├── selfie-v5.py            # v5 主入口（推荐）
│   ├── selfie-v4.py            # v4 种子池版（备选）
│   ├── comfyui_client.py       # ComfyUI 客户端
│   ├── deletefile.py           # 远程删除工具
│   ├── scheduler.py            # 定时任务入口
│   ├── trae_sender.py          # Trae 发送器
│   ├── feishu_sender.py        # 飞书三气泡发送器
│   └── seed_pool.py            # 种子池管理
├── docs/                       # 文档目录
│   ├── BEST_PRACTICES.md
│   ├── QUICKSTART.md
│   ├── SIPOC_OPTIMIZATION.md
│   ├── SERVER_CLEANUP.md
│   └── TEST_REPORT.md
├── assets/                     # 资源目录
│   ├── faces/                  # 脸部参考图片
│   └── sample/                 # 示例图片
└── references/                 # 参考文档
    ├── good-seeds.md
    ├── prompt-guides.md
    └── workflow-guides.md
```

## 核心参数速查

| 参数 | 值 | 说明 |
|------|-----|------|
| 模型 | ChilloutMix-Ni | SD1.5 写实模型 |
| CFG | 4.0 | 表情控制最佳值 |
| 采样器 | euler + normal | 避免塑料感 |
| FaceID 权重 | 0.80 | 表情控制最佳平衡点 |
| 分辨率 | 512×768 → 1024×1536 | Hi-Res 2x |

## 参考文档

- [SIPOC 优化文档](docs/SIPOC_OPTIMIZATION.md)
- [最佳实践](docs/BEST_PRACTICES.md)
- [快速开始](docs/QUICKSTART.md)
- [服务器清理](docs/SERVER_CLEANUP.md)
- [测试报告](docs/TEST_REPORT.md)

## Gotchas

- **所有场景必须使用 FaceID** — 脸型一致性是核心要求
- **CFG 过高导致塑料感** — 建议保持 3.5-4.0
- **batch_size 必须为 1** — 多图生成会导致 FaceID 失效
- **种子池管理** — 使用 `seed_pool.py` 管理优质种子
- **SIPOC 输出目录** — 图片统一存入 `~/.avatar/outputs/`
- **30 天自动清理** — outputs 文件夹自动清理旧图
- **SSH 远程删除** — 通过 `deletefile.py` 管理服务器缓存

## 路线图

| Phase | 状态 | 内容 |
|-------|------|------|
| Phase 1 | ✅ | 图片生成、FaceID 面部一致性 |
| Phase 1.5 | ✅ | SIPOC 优化、远程删除、定时任务 |
| Phase 2 | ⏳ | LoRA 训练 |
| Phase 3 | 🔄 | 视频生成（Wan2.1 I2V） |
| Phase 4 | 📋 | 语音合成 → 数字人 |

## 版本历史

### v5.0.0 (2026-05-24)

- 重构 SIPOC 架构，统一输出目录（~/.avatar/）
- 新增 deletefile.py（SSH 远程删除）
- 新增 scheduler.py（定时任务入口）
- 新增 trae_sender.py（Trae 平台发送器）
- 新增 docs/ 目录（完整文档体系）
- 修改 comfyui_client.py（移除删除方法，职责分离）
- 修改 selfie-v5.py（输出格式适配 Trae）
- 新增种子池管理（good-seeds.txt）
- 30 天自动清理机制

### v4.0.0 (2026-05-21)

- 新增种子池版（selfie-v4.py）
- 优化提示词外置到 prompts/
- 新增场景文件系统

### v3.0.0 (2026-05-20)

- 提示词外置版
- 场景文件支持
- 时间+日期自动注入

## 许可证

MIT License