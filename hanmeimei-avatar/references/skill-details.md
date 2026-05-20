# 韩梅梅形象生成技能 - 详细文档

## 核心工作流参数

### 关键参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 模型 | ChilloutMix-Ni | SD1.5 写实模型 |
| CFG | **3.5** | 低 CFG 保证皮肤自然质感 |
| 采样器 | **euler** + normal | 避免塑料感 |
| 步数 | 30 (基础) + 20 (Hi-Res) | |
| 分辨率 | 512×768 → 1024×1536 | |
| batch_size | 1 | |
| 基准 Seed | 98994781 | |

> ⚠️ **皮肤质感关键**：CFG 过高会导致塑料感，建议保持 3.5

### FaceID 参数

| 参数 | 值 | 说明 |
|------|-----|------|
| preset | FACEID PLUS V2 | IPAdapter 预设 |
| lora_strength | 0.6 | LoRA 强度 |
| weight | 1 | IPAdapter 权重 |
| weight_faceidv2 | **0.85** | FaceID v2 权重 |
| weight_type | linear | 权重类型 |
| combine_embeds | concat | 嵌入组合方式 |
| embeds_scaling | V only | 嵌入缩放方式 |

## 生成脚本详细说明

### photo.py（默认入口）

**命令行参数**：
- `--workflow, -w`: 工作流名称（默认：default）
- `--seed, -s`: 随机种子（默认：使用工作流默认值；"random"：随机生成）
- `--clothing, -c`: 穿搭描述（覆盖工作流中的默认穿搭）
- `--expression, -e`: 表情描述（覆盖工作流中的默认表情）
- `--lighting`: 光线描述（覆盖工作流中的默认光线）
- `--face`: 脸部参考图片路径（用于FaceID修正）
- `--json`: 输出 JSON 格式结果
- `--list, -l`: 列出所有可用工作流

**种子处理逻辑**：
- 不指定 `--seed`：使用工作流中的默认种子（default.json 为 98994781）
- `--seed random`：生成新的随机种子
- `--seed 123456789`：使用指定的种子值

**模块导入示例**：
```python
from photo import run_workflow
result = run_workflow("default", seed=None)  # 使用工作流默认种子
result = run_workflow("default", seed="random")  # 随机种子
result = run_workflow("default", seed=123456)  # 指定种子
```

### selfie.py（定时自拍）

**架构流程**：
```
selfie.py
    ↓ 1. 读取 faceid.json
    ↓ 2. 动态构建提示词（穿搭+表情+光线+背景）
    ↓ 3. update_prompt() 替换提示词
    ↓ 4. 设置种子和脸部参考
    ↓ 5. 调用 ComfyUIClient.run_workflow()
comfyui_client.py
    ↓ 6. 上传脸部参考图片
    ↓ 7. 调用 comfyui 技能
ComfyUI 服务器 (10.28.9.6:8188)
```

**场景类型（8种）**：
- bedroom（卧室）、cafe（咖啡厅）、library（图书馆）
- boulevard（林荫道）、rooftop（屋顶）
- gym（健身房）、travel（旅行）、park（公园）

**智能穿搭系统（OUTFIT_MAP）**：
- 根据场景 + 时段自动选择穿搭
- 夜间外出场景自动加外套
- 卧室夜间穿睡裙

**表情随机系统（EXPRESSION_MAP）**：
- 每个场景 4 种随机表情
- 与场景氛围匹配

**背景描述系统（BACKGROUND_MAP）**：
- 每个场景固定背景描述

### selfie-v2.py（表情控制测试版）

**最佳配置（经过测试验证）**：
| 参数 | 值 | 说明 |
|------|-----|------|
| expression_weight | **1.2** | 表情权重 |
| weight | **1.0** | IPAdapter 权重 |
| weight_faceidv2 | **0.80** | FaceID v2 权重 |
| end_at | **1.0** | FaceID 结束介入点 |
| CFG | **4.0** | 提示词控制力 |
| start_at | **0.0** | FaceID 开始介入点 |

**参数说明**：
- `--expression, -e`: 表情描述
- `--expression-weight, -ew`: 表情权重（默认: 1.2）
- `--faceid-weight, -fw`: FaceID weight_faceidv2 权重（默认: 0.80）
- `--faceid-weight-0, -fw0`: FaceID weight 权重（默认: 1.0）
- `--faceid-end-at, -fea`: FaceID end_at（默认: 1.0）
- `--cfg, -c`: CFG 值（默认: 4.0）
- `--start-at, -sa`: FaceID 开始介入点（默认: 0.0）
- `--seed, -s`: 指定种子
- `--verbose, -v`: 详细输出模式

**表情关键词参考**：
- `big grin, wide toothy smile, laughing joyfully, showing teeth` — 大笑露齿
- `warm smile, happy expression` — 温暖微笑
- `gentle smile, peaceful expression` — 温柔微笑

## 内容安全规则

| 客户端 | 检测条件 | 分发策略 |
|--------|---------|---------|
| Hermes Web UI | 无飞书 OU 号 | ✅ 直接发图 |
| 飞书 | 有飞书 OU 号 | ⚠️ 敏感内容需提醒审核风险 |

**规则**：
- 裸露/NSFW 照片只能本地展示，不能发飞书
- 飞书渠道发性感内容前必须提醒用户审核风险
- **服装选择建议**：
  - ✅ 推荐：`dress`、`skirt`、`blouse`、`shirt`、`jacket`、`coat` 等明确服装描述
  - ❌ 避免：`zentai`、`bodysuit`、`full body suit` 等紧身服装词（会被理解为类似裸体效果）
- **反向提示词正确格式**：
  - ❌ 错误：`nude, naked, topless, ...` （开头的排除词会被误解析）
  - ✅ 正确：`ng_deepnegative_v1_75t, (nude:1.5), (naked:1.5), (topless:1.5), ...` （排除词加在中间并提高权重）
