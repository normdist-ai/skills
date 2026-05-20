# 工作流指南

## 两步法（解耦优化）

### 核心思想
先生成好的构图/服装，再局部重绘面部/手部，避免逆向优化。

### 工作流

```
Step 1: 基础图生成（不用 FaceID）
  → ChilloutMix Ni, CFG=5.5, DPM++ 2M Karras, 30步
  → 重点控制：穿搭、构图、姿态、光线
  → 512×832 (全身坐姿) 或 512×768 (半身照)
  → Hi-Res Fix 2x → 1024×1664 或 1024×1536

Step 2: 面部局部重绘（CLIPSeg + FaceID）
  → CLIPSeg 检测 "face" 生成面部 mask
  → mask dilation=30px, blur=7, threshold=0.4
  → FaceID PlusV2 (weight=1.2, faceidv2=0.8) + InpaintModelConditioning
  → CFG=3.5, DPM++ 2M Karras, 30步
  → 仅重绘 mask 区域，保留基础图的其他部分
```

### 关键参数

| 参数 | Step1 基础图 | Step2 面部重绘 |
|------|------------|--------------|
| FaceID | ❌ 不用 | ✅ PlusV2 |
| CFG | 5.5 | 3.5 |
| Sampler | DPM++ 2M Karras | euler / normal |
| Steps | 30 | 30 |

## Seed 模板模式

### 核心理念
不再用 FaceID 约束脸型，而是用用户满意的图片 seed + 提示词控制表情/穿搭。

### 优势
- 提示词自由控制表情
- CFG 可拉到 5.5，穿搭控制力强
- 出图速度快（~62s）

### 当前基准模板
| 模板 | Seed | 模型 |
|------|------|------|
| photo_009（白瓷肌标杆） | 98994781 | chilloutmix-Ni |

## 表情控制方案对比

| 方案 | 耗时 | 表情控制 | 穿搭控制 | 面部一致性 |
|------|------|---------|---------|-----------|
| 方案A（低权重FaceID） | ~60-70s | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 方案B（两步法） | ~160-300s | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## 生成参数

### FaceID PLUS V2 参数

| 参数 | 值 |
|------|-----|
| 模型 | chilloutmix-Ni |
| weight | 0.85 |
| weight_faceidv2 | 0.6 |
| lora_strength | 0.7 |
| end_at | 0.85 |
| CFG | 3.5 |
| sampler | Euler |
| steps | 30 (base) + 20 (refine) |
| base尺寸 | 512×768 |
| Hi-Res | 2x → 1024×1536 |

### no-faceid 模式

| 参数 | FaceID 模式 | no-faceid 模式 |
|------|-----------|---------------|
| CFG | 3.5 | 5.5 |
| 出图速度 | ~70s | ~62s |

## 手部修复方案

### 方案B：CLIPSeg + DetailerForEach

```python
{
    "guide_size": 512, "steps": 25, "cfg": 7.0,
    "sampler_name": "dpmpp_2m", "scheduler": "karras",
    "denoise": 0.6, "feather": 5, "force_inpaint": True,
    "inpaint_model": False, "cycle": 2, "noise_mask": True
}
```

### 手部修复提示词

正面：`detailed well-shaped hands, natural finger positions, clear knuckles, realistic skin texture on hands, slender fingers`

负面：`deformed hands, mutated hands, extra fingers, missing fingers, fused fingers, twisted fingers, poorly drawn hands, bad hands, oversized hands`

## 换衣工作流

### 原理
CLIPSeg 检测衣服区域 → GrowMask 扩展 mask → InpaintModelConditioning 重绘衣服区域

### 关键参数

| 参数 | 值 |
|------|-----|
| CLIPSeg prompt | "clothing, dress, shirt, outfit, garment" |
| GrowMask expand | 20 |
| KSampler denoise | 0.75 |
| KSampler cfg | 5.5 |

## 已知限制

1. **手部变形严重**：优先用构图避开手
2. **SD1.5 服装控制力弱**：两步法可突破
3. **SDXL 不兼容 FaceID**：Juggernaut-XL 不能用于面部一致性场景
4. **全身照比例失调**：建议使用 512×832 画幅