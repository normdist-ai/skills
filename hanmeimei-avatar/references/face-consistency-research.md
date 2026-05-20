# ComfyUI 脸部一致性与表情控制 — 社区方案调研

调研日期：2026-05-18
来源：searxng 搜索 + CSDN/知乎/技术博客

## 核心问题

FaceID PLUS V2 weight=1.2 锁死表情（无法微笑），降到 0.8 后表情自然但脸部一致性丢失。
两步法（Step1 高CFG构图 + Step2 CLIPSeg+FaceID局部重绘）可行，但表情控制仍不稳定。

## 社区公认最佳方案：三层叠加

### 第一层：InstantID（身份保持）
- 专门的身份保持模型，通过 InsightFace antelopev2 提取面部特征
- 比 FaceID 更强的"身份锁定"能力
- 不受参考图构图限制（参考图大头照也能生成全身照）
- 需要额外模型：
  - InstantID 主模型 (ip-adapter.bin)
  - InstantID ControlNet (diffusion_pytorch_model.safetensors)
  - InsightFace antelopev2 模型
- ComfyUI 节点：`cubiq/ComfyUI_InstantID`

### 第二层：IPAdapter FaceID PLUS V2（我们已有）
- 作为 InstantID 的补充，提供额外面部特征注入
- 两者叠加可显著提高相似度
- 过拟合时降低 IPAdapter 权重和 end_at

### 第三层：FaceDetailer（Impact Pack）
- 在生成最后一步对脸部区域做局部重绘精修
- 自动检测脸部 → 重绘 → 解决"脸崩"
- 节点：Impact Pack 中的 FaceDetailer
- 连接方式：InstantID 输出 → FaceDetailer 输入

## 参数调优建议

| 参数 | 当前值 | 建议值 | 说明 |
|------|--------|--------|------|
| CFG | 3.5 | 4-5 | 偏低可适当提高 |
| 步数 | 20 | 30+ | 提高步数可减少过拟合 |
| IPAdapter weight | 1.2 | 0.6-0.8（配合InstantID时）| 叠加后可降低 |
| InstantID strength | - | 0.8-1.0 | 主要身份来源 |

## 关键参考文章

1. 知乎「升级版ComfyUI InstantID换脸：FaceDetailer + InstantID + IP-Adapter」
   - https://zhuanlan.zhihu.com/p/695672799
   - 详细工作流搭建步骤，包含 SDXL/SD1.5 适配

2. CSDN「用ComfyUI打造数字分身：IPAdapter与InstantID底层原理与最佳实践」
   - IPAdapter = 风格迁移的"调色盘"
   - InstantID = 身份保持的"锚点"
   - FaceDetailer = 局部精修的"画笔"
   - 三者互补而非替代

3. RunComfy「Create Consistent Characters with IPAdapter FaceID Plus」
   - https://www.runcomfy.com/zh-CN/comfyui-workflows/create-consistent-characters-in-comfyui-with-ipadapter-faceid-plus

4. RunningHub「最强人脸一致性方案」
   - https://www.runninghub.cn/post/1911019448445169666/aiDetail

## 落地状态（2026-05-18）

### 已实现：FaceID PLUS V2 + FaceDetailer（两层）

跳过了 InstantID（未安装，需下载模型），直接用 FaceID PLUS V2 + FaceDetailer 后处理：

- generate.py 已集成 FaceDetailer 作为 VAEDecode 后的精修步骤
- 核心思路：降低 FaceID 权重释放表情 → FaceDetailer 轻量精修补偿质量
- 默认参数：weight=0.85, v2=0.6, end_at=0.85, lora=0.7 + FaceDetailer(denoise=0.35, cfg=7.0)
- 微笑参数：weight=0.8, v2=0.55, end_at=0.8
- 完整流程耗时约 291s（原 68s），质量显著提升
- FaceDetailer 通过 scene JSON 的 `face_detailer.enabled` 开关控制

### 待验证

- InstantID 三层叠加方案（需下载模型 ~700MB，交给小美处理）
- 更多 seed 的微笑模式测试（weight=0.8 表情效果尚可但不稳定）

### 已验证的结论

- FaceDetailer 用于两步法 Step2（面部重绘主导）→ ❌ 变脸严重
- FaceDetailer 用于单步法后处理（轻量精修）→ ✅ 质量提升不变脸
- 关键区别：后处理模式用原始 checkpoint model，不传 FaceID model
