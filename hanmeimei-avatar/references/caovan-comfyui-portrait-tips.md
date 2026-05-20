# 草凡博客 ComfyUI 人像写实技巧摘录

> 来源：caovan.com（最大的中文 AIGC 独立博客）
> 日期：2026-05-17
> 用途：韩梅梅 AI 写真优化参考

## FaceID 相关文章

### IPAdapter FaceID Portrait 模型
- URL: https://caovan.com/ipadapter-faceiddezhegexinmoxinghenxiaodanshichaojinihai-portrait-aihuihuajiaocheng/.html
- Portrait 模型仅 64.6MB，FaceID 系列最小
- **无需搭配 LoRA 即可独立使用**
- 效果达 PlusV2 同级别
- 推荐 512×768 分辨率

### IPAdapter FaceID Plus/PlusV2 使用要点
- URL: https://caovan.com/aihuihuajiaochengzaicomfyuizhongshiyongipadapater-faceidjiedianjinxinghuanlian/.html
- 阅读量 32544，草凡最热门文章之一
- PlusV2 必须设 `faceid_v2=True`
- 需要 Plus 版 LoRA 配套使用
- clip_vision 必须选 SD1.5 版
- antelopev2 模型需放在 insightface/models 目录

### InstantID vs FaceID 对比
- 博主评价：InstantID 人脸相似度更胜 FaceID，但图片质量不如 FaceID
- InstantID 只支持 SDXL，不支持 SD1.5
- **博主更偏爱 FaceID PlusV2**

## 提示词技巧

### 9 大类别
主题 → 媒介 → 风格 → 艺术家 → 网站 → 分辨率 → 细节 → 颜色 → 灯光

### 写实关键提示词
```
best quality, masterpiece, ultra-detailed, photorealistic, realistic, photograph
```

### 画质提示词
```
best quality, ultra-detailed, masterpiece, hires, 8k
```

### 权重语法
- `(keyword:1.5)` — 精确权重
- `((keyword))` — 每层 ×1.1
- `[[keyword]]` — 每层 ×0.9（减弱）

### 草凡推荐负面提示词（完整版）
```
NSFW,(worst quality:2),(low quality:2),lowres,normal quality,((monochrome)),((grayscale)),skin spots,acnes,skin blemishes,age spot,(ugly:1.331),(morbid:1.21),(mutilated:1.21),(tranny:1.331),mutated hands,(poorly drawn hands:1.5),blurry,(bad anatomy:1.21),(bad proportions:1.331),extra limbs,(disfigured:1.331),(missing arms:1.331),(extra legs:1.331),(fused fingers:1.61051),(too many fingers:1.61051),(unclear eyes:1.331),lowers,bad hands,missing fingers,extra digit,bad hands,missing fingers,(((extra arms and legs)))
```

### 推荐采样参数
- 采样器：DPM++ 2M Karras
- 步数：30
- 分辨率：512×704
- CFG: 7（通用场景），FaceID 模式下用 3.5

## 推荐写实模型
- `chilloutmix_NiPrunedFp32Fix.safetensors` ← 我们在用
- `beautifulRealistic_brav5.safetensors`

## 面部修复参数（图生图）
```
Sampling: DPM adaptive
Steps: 20
Restore faces: ✓ (GFPGAN)
CFG: 7
Denoising: 0.05（极低降噪保原图特征）
```

## 服装试穿 — MagicClothing
- URL: 草凡博客服装试穿 ComfyUI 工作流 MagicClothing
- 节点：`ComfyUI_MagicClothing`
- 上传服装图片 → 生成模特试穿效果（80-90% 相似度）
- 可用于解决 SD1.5 服装控制力不足的问题

## 对韩梅梅写真的应用
1. ✅ 已采纳：负面词权重 `(bad anatomy:1.21)` 等
2. ✅ 已采纳：正面加 `best quality, masterpiece, ultra-detailed`
3. ✅ 已采纳：全身照负面词 `(((extra arms and legs)))`
4. 🔄 待验证：FaceID Portrait 模型（无需 LoRA）
5. 🔄 待验证：MagicClothing 服装控制
6. 🔄 待验证：SDXL 模型（提示词理解力更强）
7. 🔄 待验证：GFPGAN 面部修复节点
