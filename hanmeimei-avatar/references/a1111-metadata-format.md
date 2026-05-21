# A1111 元数据格式规范

Civitai 和 LibLib "一键复制参数" 输出的格式，基于 AUTOMATIC1111 Stable Diffusion WebUI 定义的事实标准。

## 完整格式

```
{正向提示词}
Negative prompt: {负向提示词}
Steps: 30, Sampler: Euler, Schedule type: normal, CFG scale: 4.0, Seed: 290643261, Size: 512x768, Model hash: abc123, Model: ChilloutMix-Ni, Clip skip: 2
```

## 三段结构

1. **正向提示词**（第一段，可多行）
2. **`Negative prompt:` 开头**（换行，后跟负向提示词）
3. **参数行**（最后一行，`Key: Value` 逗号分隔）

## 参数行字段

| 字段 | 说明 | 必选 |
|------|------|------|
| `Steps` | 采样步数 | ✅ |
| `Sampler` | 采样器名称 | ✅ |
| `Schedule type` | 调度器（normal/karras等） | ❌ |
| `CFG scale` | CFG值 | ✅ |
| `Seed` | 随机种子 | ✅ |
| `Size` | 图片尺寸（宽x高） | ✅ |
| `Model hash` | 模型哈希 | ❌ |
| `Model` | 模型名称 | ❌ |
| `VAE` / `VAE hash` | VAE信息 | ❌ |
| `Clip skip` | CLIP跳过层数 | ❌ |
| `Denoising strength` | 去噪强度（图生图） | ❌ |
| `Hires upscale` / `Hires steps` | 高清放大参数 | ❌ |

## 解析正则（A1111 源码）

```python
re_param_code = r'\s*(\w[\w \-/]+):\s*("(?:\\.|[^\\"])+\"|[^,]*)(?:,|$)'
```

## 存储位置

| 格式 | PNG | JPEG |
|------|-----|------|
| A1111 | PNG `parameters` 文本块 | EXIF UserComment |
| ComfyUI | PNG `prompt` + `extra_pnginfo` JSON 块 | 不常用 |

## Civitai 处理方式

1. **A1111 格式** — 从 PNG `parameters` 块直接解析
2. **ComfyUI 格式** — 从 PNG `prompt` + `extra_pnginfo` JSON 块解析工作流节点，反推参数

## 对我们的意义

- selfie-v3.py 的提示词文件格式参考此规范，方便用户从 Civitai/LibLib 复制粘贴
- 我们的 ComfyUI 输出是 JSON 格式，上传 Civitai 需要装 ComfyUI-Image-Saver 插件做格式转换
- LibLib 在线 WebUI 本身是 A1111 魔改版，复制参数格式与 A1111 完全一致

## 参考

- A1111 源码: `modules/processing.py` → `create_infotext()` 函数
- A1111 源码: `modules/infotext_utils.py` → `re_param` 解析正则
- ComfyUI-Image-Saver: https://github.com/alexopus/ComfyUI-Image-Saver（生成 Civitai 兼容元数据）
