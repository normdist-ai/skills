# 韩梅梅形象生成技能

基于 ComfyUI 的 AI 写真照片生成技能，支持 FaceID 面部一致性保持、四维环境感知自拍、多场景生活化生成。

## 特性

- ✅ **FaceID 面部一致性**：使用 IPAdapter FaceID 保持韩梅梅的脸型特征
- ✅ **四维环境感知**：根据季节、时段、天气自动选择场景和光线
- ✅ **多场景生活化**：8 种生活场景（卧室、咖啡厅、图书馆、林荫道、屋顶、健身房、旅行、公园）
- ✅ **智能穿搭系统**：根据场景和时段自动选择 48 种穿搭组合
- ✅ **表情随机系统**：每场景 4 种表情，共 32 种表情选择
- ✅ **调试支持**：完整的 DEBUG 日志，便于排查问题

## 工作流程

### 1. 整体架构

```
用户调用
    ↓
photo.py / selfie.py
    ↓ 读取/修改工作流
comfyui_client.py
    ↓ 调用 comfyui 技能
comfyui/run_workflow.py
    ↓ 连接服务器
ComfyUI 服务器 (10.28.9.6:8188)
    ↓ 执行工作流
输出图片 → outputs/ 目录
```

### 2. photo.py 工作流

**用途**：单次生成，支持参数自定义

```
步骤 1: 读取工作流文件（如 default.json）
    ↓
步骤 2: update_prompt() 替换提示词（穿搭、表情、光线）
    ↓
步骤 3: update_load_image() 更新脸部参考图片
    ↓
步骤 4: 设置种子（不指定→默认值 / random→随机 / 指定值→使用）
    ↓
步骤 5: 创建 ComfyUIClient 实例
    ↓
步骤 6: client.run_workflow() 执行生成
    ↓
步骤 7: 返回结果文件路径
```

### 3. selfie.py 工作流

**用途**：四维环境感知自拍，自动选择场景

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
步骤 3: 参数构建
    ├─ get_outfit(场景, 时段) → 穿搭描述
    ├─ get_expression(场景) → 表情描述
    ├─ get_background(场景) → 背景描述
    └─ get_random_face_reference() → 脸部参考图片
    ↓
步骤 4: 工作流构建
    ├─ 读取 faceid.json
    ├─ update_prompt() 替换所有参数
    ├─ 设置随机种子
    └─ 设置脸部参考图片
    ↓
步骤 5: 执行生成
    ├─ 创建 ComfyUIClient 实例
    ├─ client.run_workflow() 执行
    └─ 重命名输出文件（HMM-YYYYMMDD-HHMMSS-种子.png）
    ↓
步骤 6: 输出结果
    └─ 消息文字 MEDIA:图片路径
```

### 4. comfyui_client.py 工作流

**用途**：封装 comfyui 技能调用

```
步骤 1: 检查输入图片
    └─ 如果有图片，上传到 ComfyUI 服务器
    ↓
步骤 2: 保存工作流为临时 JSON
    ↓
步骤 3: 调用 comfyui 技能
    └─ subprocess.run([python3, run_workflow.py, ...])
    ↓
步骤 4: 解析输出
    ├─ 读取 stdout 的 JSON 结果
    └─ 返回文件路径
```

### 5. 环境感知系统

#### ROUTINES 配置（4 季节 × 6 时段）

```python
spring.night = [
    ("bedroom", "warm desk lamp, soft fairy lights"),
    ("bedroom", "warm bedside lamp glow"),
    ("travel", "beautiful night view at travel destination"),
    ("park", "soft night lighting through cherry trees"),
]
```

每个时段有 2-4 个场景选择，确保随机性。

#### OUTFIT_MAP 配置（8 场景 × 6 时段）

```python
OUTFIT_MAP["bedroom"] = {
    "morning": "a comfortable cotton pajama set",
    "forenoon": "a casual loungewear set",
    "noon": "a comfortable home outfit",
    "afternoon": "a casual loungewear set",
    "evening": "a comfortable loungewear set",
    "night": "a comfortable cotton nightgown",
}
```

夜间外出场景自动加外套，卧室夜间穿睡裙。

#### EXPRESSION_MAP 配置（8 场景 × 4 表情）

```python
EXPRESSION_MAP["bedroom"] = [
    "gentle smile",
    "sleepy cute expression",
    "relaxed smile",
    "peaceful expression",
]
```

每个场景 4 种表情，随机选择。

#### BACKGROUND_MAP 配置（8 场景）

```python
BACKGROUND_MAP = {
    "bedroom": "cozy bedroom background",
    "cafe": "cozy cafe interior background",
    "library": "library background with bookshelves",
    # ...
}
```

固定背景描述，自动追加到提示词。

## 快速开始

### 安装依赖

```bash
pip install requests
```

### 基础使用

#### 1. 单次生成（photo.py）

```bash
# 默认工作流（default.json）
python scripts/photo.py

# 指定工作流
python scripts/photo.py --workflow default

# 指定种子
python scripts/photo.py --seed 123456
python scripts/photo.py --seed random

# 自定义参数
python scripts/photo.py \
  --workflow faceid \
  --clothing "a red dress" \
  --expression "happy smile" \
  --lighting "golden sunset" \
  --face assets/faces/face-1.png
```

#### 2. 环境感知自拍（selfie.py）

```bash
# 自动根据季节、时段、天气生成
python scripts/selfie.py

# 查看调试日志
python scripts/selfie.py 2>&1 | grep DEBUG
```

#### 3. 使用 comfyui 技能（推荐）

```bash
cd comfyui/scripts

# 基础生成
python3 run_workflow.py \
  --workflow ../hanmeimei-avatar/workflows/default.json \
  --host http://10.28.9.6:8188 \
  --output-dir ../hanmeimei-avatar/outputs

# 随机种子
python3 run_workflow.py \
  --workflow ../hanmeimei-avatar/workflows/faceid.json \
  --host http://10.28.9.6:8188 \
  --output-dir ../hanmeimei-avatar/outputs \
  --randomize-seed

# 上传输入图片
python3 run_workflow.py \
  --workflow ../hanmeimei-avatar/workflows/faceid.json \
  --host http://10.28.9.6:8188 \
  --output-dir ../hanmeimei-avatar/outputs \
  --input-image image=../hanmeimei-avatar/assets/faces/face-2.png
```

### Python 模块导入

```python
from scripts.photo import run_workflow

# 使用工作流默认种子
result = run_workflow("default", seed=None)

# 使用随机种子
result = run_workflow("default", seed="random")

# 使用指定种子
result = run_workflow("default", seed=123456)

# 自定义参数
result = run_workflow(
    workflow_name="faceid",
    seed=None,
    clothing="a blue dress",
    expression="gentle smile",
    lighting="natural window light",
    face_image="assets/faces/face-1.png",
)

if result["success"]:
    print(f"生成成功: {result['file']}")
else:
    print(f"生成失败: {result['error']}")
```

## 工作流文件

### 工作流类型

| 文件 | 用途 | FaceID | 穿搭 | 用途 |
|------|------|--------|------|------|
| default.json | 默认工作流 | ✅ | chiffon dress | 日常照片 |
| faceid.json | FaceID 模板 | ✅ | summer long skirt | 其他场景基础 |
| base.json | 基础工作流 | ❌ | - | 参考用 |
| nude.json | 敏感内容 | ✅ | nude | 私有环境 |

### 关键参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 模型 | chilloutmix-Ni.safetensors | SD1.5 写实模型 |
| CFG | 3.5 | 低 CFG 保证皮肤自然质感 |
| 采样器 | euler + normal | 避免塑料感 |
| 步数 | 30 (基础) + 20 (Hi-Res) | |
| 分辨率 | 512×768 → 1024×1536 | |
| batch_size | 1 | 多图生成会导致 FaceID 失效 |
| FaceID 权重 | weight_faceidv2 = 0.85 | 脸型一致性最佳平衡点 |

### FaceID 配置

```json
{
  "preset": "FACEID PLUS V2",
  "lora_strength": 0.6,
  "weight": 1,
  "weight_faceidv2": 0.85,
  "weight_type": "linear",
  "combine_embeds": "concat",
  "embeds_scaling": "V only"
}
```

## 输出格式

### selfie.py 输出

```
消息文字 MEDIA:图片路径

示例：
老公～忙完准备睡了，晚安 🌙 MEDIA:outputs/HMM-20260519-214229-513713504.png
```

### photo.py 输出

```json
{
  "success": true,
  "file": "outputs/HMM-20260519-223707-676999480.png",
  "seed": 676999480,
  "workflow": "default"
}
```

## 调试技巧

### 查看提示词替换过程

```bash
python scripts/selfie.py 2>&1 | grep DEBUG
```

输出示例：
```
[DEBUG] 原始提示词: best quality, masterpiece...
[DEBUG] 替换穿搭: comfortable cotton nightgown
[DEBUG] 替换表情: relaxed smile
[DEBUG] 替换光线: warm bedside lamp glow
[DEBUG] 添加背景: cozy bedroom background
[DEBUG] 最终提示词: best quality, masterpiece...
[DEBUG] 设置种子: 节点3 = 676999480
[DEBUG] 设置脸部参考: 节点8 = face-2.png
```

### 查看环境信息

```bash
python scripts/selfie.py 2>&1 | grep INFO
```

输出示例：
```
[INFO] === 韩梅梅自拍生成 2026-05-19 22:37:07 ===
[INFO] 季节=spring, 时段=night, 天气=cloudy(23°C,Cloudy)
[INFO] 场景=bedroom
[INFO] 光线=warm bedside lamp glow
[INFO] 脸部参考=assets/faces/face-2.png
[INFO] 穿搭=comfortable cotton nightgown
[INFO] 表情=relaxed smile
[INFO] 背景=cozy bedroom background
[INFO] 随机种子=676999480
```

## 已知问题

### 1. 手部变形

AI 绘画通病，优先使用 waist up 构图避开。

### 2. SD1.5 服装控制力

FaceID 模式下 CFG 限制为 3.5，服装控制力较弱。

### 3. SDXL 不兼容 FaceID

仅支持 SD1.5 模型。

### 4. 裸体生成问题

- 避免：`zentai`、`bodysuit`、`full body suit` 等紧身服装词
- 推荐：`dress`、`skirt`、`blouse` 等明确服装描述
- 反向提示词格式：`(nude:1.5),(naked:1.5),(topless:1.5)`

## 最佳实践

### 1. 脸型一致性

- 所有场景必须使用 FaceID
- FaceID 权重固定为 0.85
- 使用固定的脸部参考图片（face-2.png）

### 2. 皮肤质感

- CFG 必须保持 3.5
- 使用 euler + normal 采样器
- 避免过高的 CFG 导致塑料感

### 3. 场景选择

- 卧室夜间场景：睡裙
- 室外夜间场景：自动加外套
- 室内学习场景：学术休闲服

### 4. 种子复现

- 相同种子 + 相同参数 = 相同图片
- 这是 Stable Diffusion 的正常行为，不是 bug
- 用于调试和风格控制

## 路线图

| Phase | 状态 | 内容 |
|-------|------|------|
| Phase 1 | ✅ | 图片生成、FaceID 面部一致性 |
| Phase 2 | ⏳ | LoRA 训练 |
| Phase 3 | 🔄 | 视频生成（Wan2.1 I2V） |
| Phase 4 | 📋 | 语音合成 → 数字人 |

## 版本历史

### v2.4.0 (2026-05-19)

- 重构 selfie.py 架构，直接读取工作流
- 修复提示词替换重复 bug
- 新增 3 个场景（gym、travel、park）
- 优化穿搭/表情/背景映射系统
- 增加调试日志支持

### v2.3.0 (2026-05-19)

- 解决裸体生成问题
- default.json 集成 FaceID
- 优化种子处理逻辑
- 集成 comfyui 技能

### v2.2.3 (2026-05-19)

- selfie.py 改用 faceid.json 作为基础工作流
- 添加场景穿搭映射

## 许可证

MIT License