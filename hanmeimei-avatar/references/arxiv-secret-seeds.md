# arXiv 2405.14828 "Good Seed Makes a Good Crop" — 核心发现

## 论文摘要
- **标题**: Good Seed Makes a Good Crop: Discovering Secret Seeds in Text-to-Image Diffusion Models
- **作者**: ZJU-AICV Lab, 2024
- **规模**: 46M 张图（SD 2.0 + SDXL Turbo，1024 seeds × 多 prompts）

## 核心发现

### 1. 种子可区分性极高
- 仅看生成图就能以 **99.9% 准确率**反推出用的是哪个种子（从 1024 个候选中）
- 证明每个种子编码了高度判别性的视觉信息

### 2. "黄金种子"确实存在
- SD 2.0: k=65 golden seeds
- SDXL Turbo: k=67 golden seeds
- Golden seeds 跨提示词泛化性好（在 A prompt 上好，在 B prompt 上也倾向好）
- **论文未公开具体种子列表**（无 supplementary data、无 GitHub repo）

### 3. 黄金种子的影响维度
- **图像质量**: golden seed #469 (SD2.0) FID 显著优于随机种子
- **人类偏好对齐**: HPS v2 评分更高
- **风格聚类**: 某些种子 consistently 生成灰度/暖色调/天空丰富等
- **构图模式**: 对象位置、大小的一致性

### 4. 推荐采样池
- 60+ golden seeds 的采样池 > 随机采样
- 用 farthest point sampling 选 diverse seeds（最大化特征空间距离）

## ⚠️ 对我们不适用

| 维度 | 论文设定 | 我们的场景 |
|------|---------|-----------|
| 模型 | SD 2.0 / SDXL Turbo | ChilloutMix-Ni (SD1.5) + FaceID |
| Prompts | MS-COCO dense captions (通用物体/场景) | 韩梅梅人像写真（特定角色、服装、场景） |
| 种子范围 | 0-1023 | 全整数范围（~4B+） |
| CFG | DDIM scheduler, ~50 steps | CFG=4.0, euler sampler |

**结论**: golden seeds 不能直接迁移。我们的 good-seeds.txt 必须用自己的场景数据积累。

## 社区参考
- Reddit: u/wonderflex seed selection tutorial（种子主题理论）
- Civitai: "list of useful seeds" article（社区种子收集）
- Chris McCormick: Steps and Seeds 教程
