# 手部修复方案研究笔记

> 调研日期：2026-05-17
> 目标：提升韩梅梅AI写真照片中手部细节质量

## 一、环境现状

### 已有工具
| 工具 | 状态 | 用途 |
|------|------|------|
| MeshGraphormer-DepthMapPreprocessor | ✅ 可用 | 检测手部→输出深度图+手部MASK |
| CLIPSegDetectorProvider | ✅ 可用 | 文本描述检测→输出BBOX_DETECTOR |
| DetailerForEach | ✅ 可用 | Impact Pack通用局部修复器（接受SEGS输入） |
| FaceDetailer | ✅ 可用 | 可用于面部（但含FaceID时面部一致性差） |
| ControlNet OpenPose (SD1.5) | ✅ 可用 | `control_v11p_sd15_openpose.pth` |
| InpaintModelConditioning | ✅ 可用 | inpaint编码 |

### 缺失组件
| 组件 | 状态 | 影响 |
|------|------|------|
| `control_sd15_inpaint_depth_hand_fp16.safetensors` | ❌ 缺失 | MeshGraphormer深度图方案需要 |
| HandDetailer 节点 | ❌ 不存在 | Impact Pack无专门手部Detailer |
| hand_yolov8n.pt | ❓ 未确认 | UltralyticsDetectorProvider未装，但MeshGraphormer自带检测 |
| ControlNet Inpaint (SD1.5) | ❌ 缺失 | `control_v11p_sd15_inpaint` 不存在 |
| DWPose | ❓ 未确认 | 草凡方案需 `dw_openpose_full` |

### 关键发现
- MeshGraphormer 节点输出：IMAGE(深度图) + INPAINTING_MASK(手部遮罩)
- DetailerForEach 接受 SEGS 输入 → 需要先将 MASK 转为 SEGS
- CLIPSeg 可以检测 "hand" → 输出 BBOX_DETECTOR → 可转 SEGS → 接入 DetailerForEach

---

## 二、方案对比（4种）

### 方案A：MeshGraphormer + ControlNet深度图引导（最专业）
**来源**：CSDN / RunComfy 教程

**流程**：
1. 加载原图 → MeshGraphormer-DepthMapPreprocessor → 输出深度图 + 手部MASK
2. 深度图 → ControlNet（`control_sd15_inpaint_depth_hand`）
3. 手部MASK → VAE Encode for Inpainting → KSampler → VAE Decode

**优点**：深度图提供3D结构引导，手部姿势最准确
**缺点**：需要下载 `control_sd15_inpaint_depth_hand_fp16.safetensors` 模型（约1.5GB）
**参数**：
- MeshGraphormer: mask_type="based_on_depth", mask_expand=5, detect_thr=0.6
- KSampler: denoise=0.5-0.8, steps=20-30

### 方案B：CLIPSeg手部检测 + DetailerForEach局部重绘（最易实现）✅推荐
**来源**：已有环境可直接实现

**流程**：
1. 加载原图 → CLIPSegDetectorProvider(text="hand") → BBOX_DETECTOR
2. BBOX_DETECTOR → SimpleDetectorForEach → SEGS（手部区域）
3. SEGS → DetailerForEach → 局部重绘手部

**优点**：无需下载任何模型，CLIPSeg已在环境中
**缺点**：无3D结构引导，手部姿势可能不如方案A精准
**关键参数**：
- CLIPSeg: text="hand", dilation_factor=10, threshold=0.3, blur=7
- DetailerForEach: guide_size=512, steps=25, cfg=7.0, denoise=0.5-0.7, cycle=2
- sampler: dpmpp_2m, scheduler: karras

### 方案C：MeshGraphormer深度图 + DetailerForEach（折中方案）
**来源**：结合A和B的优势

**流程**：
1. MeshGraphormer-DepthMapPreprocessor → IMAGE(深度图) + MASK(手部)
2. MASK → MaskToSEGS → SEGS
3. SEGS → DetailerForEach → 局部重绘手部
4. 深度图仅作为参考（不接ControlNet，不依赖缺失模型）

**优点**：利用MeshGraphormer的精准手部检测和MASK，无需下载新模型
**缺点**：深度图仅检测用，不引导重绘过程

### 方案D：草凡方案 - ADetailer + ControlNet OpenPose + Inpaint
**来源**：caovan.com（草凡博客）

**流程**：
1. ADetailer 自动检测手部 → 生成MASK
2. ControlNet OpenPose (dw_openpose_full) → 锁定全身姿势
3. ControlNet Inpaint (inpaint_global_harmonious) → 保持一致性
4. 局部重绘手部
5. 进阶：+ControlNet Depth + SoftEdge

**优点**：最科学的方法，保持原姿势
**缺点**：ComfyUI中无ADetailer节点（ADetailer是WebUI插件）；需要多个ControlNet模型
**适配ComfyUI**：用 MeshGraphormer替代ADetailer做手部检测

---

## 三、推荐实施路线

### 首选：方案B（CLIPSeg + DetailerForEach）
理由：零下载，立即可用，已在环境中验证过CLIPSeg检测能力。

### 提升路线：方案C（MeshGraphormer + DetailerForEach）
如果方案B的手部检测不够精准，升级到MeshGraphormer检测。

### 终极方案：方案A（MeshGraphormer + ControlNet深度图）
需要下载 `control_sd15_inpaint_depth_hand_fp16.safetensors`，可通过看板任务让小美处理。

---

## 四、实施参数（方案B）

### Step3: 手部局部重绘（接在Step2面部重绘之后）

```python
# 节点链路：
# CLIPSegDetectorProvider(text="hand") → BBOX_DETECTOR
# SimpleDetectorForEach(image, bbox_detector) → SEGS
# DetailerForEach(image, segs, model, clip, vae, ...) → IMAGE(修复后)

# DetailerForEach 关键参数
{
    "guide_size": 512,          # 引导大小，手部需要足够像素
    "steps": 25,                # 足够的采样步数
    "cfg": 7.0,                 # 较高CFG确保手部结构清晰
    "sampler_name": "dpmpp_2m",
    "scheduler": "karras",
    "denoise": 0.6,             # 手部需要较高denoise重构
    "feather": 5,               # 边缘羽化
    "force_inpaint": True,
    "inpaint_model": False,     # SD1.5普通模型即可
    "cycle": 2,                 # 循环2次提高质量
    "noise_mask": True
}
```

### 注意事项
1. **手部检测精度**：CLIPSeg对"hand"的检测可能不够精准，可尝试"hand,fingers"
2. **手部结构**：如果原图手部结构严重错误（多指/少指），任何inpaint都无法修复
3. **denoise值**：手部通常需要0.5-0.7，比面部(0.15-0.3)高很多
4. **cycle次数**：cycle=2可以改善手部细节，但耗时翻倍
5. **prompt**：手部重绘时prompt应包含手部相关描述词

---

## 五、参考文献

1. 草凡博客《SD在保持原姿势的基础上解决手部崩坏》- caovan.com
   - ADetailer + ControlNet OpenPose + Inpaint 三重引导方案
   - 进阶加 Depth + SoftEdge
   
2. CSDN《ComfyUI_015 自动检测手部并修手》
   - FaceDetailer用hand模型检测手部，仅能增强细节不能修复结构
   - person_yolov8m-seg.pt 可做整体人物修复
   
3. CSDN《ComfyUI手部修复讲解》
   - MeshGraphormer + control_sd15_inpaint_depth_hand 方案
   - 需要安装mediapipe依赖
   
4. RunComfy《Mesh Graphormer ControlNet 修复手部》
   - 完整工作流，MeshGraphormer生成深度图+MASK
   - ControlNet inpaint_depth_hand 引导重绘
   
5. 知乎《HandRefiner：解决AI图像生成中手部畸形》
   - ACM MM 2024 论文的实现
   - 基于MeshGraphormer深度图的ControlNet方案
