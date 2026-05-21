# A1111 生成参数格式规范

A1111（AUTOMATIC1111 Stable Diffusion WebUI）定义的参数格式是 SD 社区的事实标准。
Civitai、LibLib 等平台的"一键复制参数"都输出此格式。

## 文本格式

```
{正向提示词}
Negative prompt: {负向提示词}
Steps: 30, Sampler: Euler, Schedule type: normal, CFG scale: 4.0, Seed: 290643261, Size: 512x768, Model hash: abc123, Model: ChilloutMix-Ni, Clip skip: 2
```

## 格式规则

1. **第一段**：纯文本正向提示词（可多行，逗号分隔）
2. **`Negative prompt:`** 换行开头，后跟负向提示词（可多行）
3. **最后一行**：`Key: Value` 逗号分隔的参数行

## 标准字段

| 字段 | 说明 | 示例 |
|------|------|------|
| `Steps` | 采样步数 | `30` |
| `Sampler` | 采样器 | `Euler`, `DPM++ 2M Karras` |
| `Schedule type` | 调度器 | `normal`, `karras`, `exponential` |
| `CFG scale` | CFG 值 | `4.0`, `7.0` |
| `Seed` | 随机种子 | `290643261` |
| `Size` | 图片尺寸 | `512x768` |
| `Model hash` | 模型哈希 | `abc123def` |
| `Model` | 模型名称 | `ChilloutMix-Ni` |
| `VAE` / `VAE hash` | VAE 信息 | `vae-ft-mse` |
| `Clip skip` | CLIP 跳过层数 | `2` |
| `Denoising strength` | 去噪强度（图生图） | `0.75` |
| `Hires upscale` / `Hires steps` 等 | 高清放大参数 | `2.0`, `15` |

## 解析正则（A1111 源码）

```python
re_param = re.compile(r'\s*(\w[\w \-/]+):\s*("(?:\\.|[^\\"])+"|[^,]*)(?:,|$)')
```

## Civitai 处理方式

Civitai 支持两种来源的元数据：
1. **A1111 格式** — 存在 PNG 的 `parameters` 文本块中，直接解析
2. **ComfyUI 格式** — 存在 PNG 的 `prompt` + `extra_pnginfo` JSON 块中，Civitai 解析工作流节点反推参数

## LibLib 处理方式

LibLib 的在线 WebUI 是 A1111 魔改版，复制出的参数格式与 A1111 完全一致。

## 对我们的意义

我们用 ComfyUI 生成，元数据是 JSON 格式的工作流，不是 A1111 格式。
selfie-v3.py 的提示词文件格式是自定义的（base.txt + 场景文件），不直接兼容 A1111 格式。
如果需要上传到 Civitai 并自动识别参数，需要装 ComfyUI-Image-Saver 插件做格式转换。
