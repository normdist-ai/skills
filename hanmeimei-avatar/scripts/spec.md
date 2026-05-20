# generate.py 工作流导出/加载功能规格

## 目标文件
`/home/jarvis/.hermes/profiles/hanmeimei/skills/creative/hanmeimei-avatar/scripts/generate.py`

## 需求

### 1. 固定节点 ID（当前是随机的）
当前 `_build_workflow()` 用 `p = random.randint(40000, 99999)` 作为节点 ID 前缀，导致每次导出的模板节点 ID 不同。

改为固定 ID 方案：
- 节点 ID 用简单递增数字：`1`, `2`, `3`, ... 
- 不用前缀，直接用 `str(i)` 编号

节点映射（无 FaceID 时）：
```
1  = CheckpointLoaderSimple
2  = CLIPTextEncode (positive)
3  = CLIPTextEncode (negative)
4  = EmptyLatentImage
5  = KSampler (base)
6  = LatentUpscale
7  = KSampler (refine)
8  = VAEDecode
9  = SaveImage
```

节点映射（有 FaceID 时）：
```
1  = CheckpointLoaderSimple
2  = LoadImage (face_ref_1)
3  = LoadImage (face_ref_2)
4  = LoadImage (face_ref_3)
5  = ImageBatch (2+3)
6  = ImageBatch (5+4)
7  = IPAdapterUnifiedLoaderFaceID
8  = IPAdapterFaceID
9  = CLIPTextEncode (positive)
10 = CLIPTextEncode (negative)
11 = EmptyLatentImage
12 = KSampler (base)
13 = LatentUpscale
14 = KSampler (refine)
15 = VAEDecode
16 = SaveImage
```

有 FaceDetailer 时，在 VAEDecode 和 SaveImage 之间插入：
```
17 = CLIPSegDetectorProvider
18 = FaceDetailer
```
SaveImage 改为从 FaceDetailer 输出。

### 2. `--export-workflow <path>` 参数
- 构建工作流但不提交到 ComfyUI
- 将工作流 JSON 写入指定文件
- 打印 `导出: <path>` 到 stdout
- 不执行生成，直接退出（exit 0）

### 3. `--load-workflow <path>` 参数
- 从 JSON 文件加载工作流
- 可配合 `--seed` 覆盖工作流中所有 KSampler 的 seed
- 可配合 `--scene`/`--clothing`/`--expression`/`--lighting` 覆盖正面提示词
- 需要 FaceID 时自动上传参考图
- 提交到 ComfyUI 执行，等待结果
- 输出格式与当前 generate() 一致

### 4. 辅助函数

```python
def export_workflow(path, workflow):
    """导出工作流 JSON 到文件"""
    import json
    with open(path, 'w') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)

def load_workflow_file(path):
    """从文件加载工作流 JSON"""
    import json
    with open(path, 'r') as f:
        data = json.load(f)
    # 支持两种格式：
    # 1. 纯工作流 {"1": {...}, "2": {...}, ...} + output_node
    # 2. 包装格式 {"workflow": {...}, "output_node": "16", "meta": {...}}
    if "workflow" in data:
        return data["workflow"], data.get("output_node", "16"), data.get("meta", {})
    return data, None, {}
```

### 5. export 时保存元数据
导出的 JSON 用包装格式，包含元数据方便后续识别：

```json
{
  "meta": {
    "exported_at": "2026-05-18T20:00:00",
    "mode": "faceid",
    "model": "chilloutmix-Ni.safetensors",
    "seed": 98994781,
    "scene": "",
    "clothing": "wearing a white long dress, flowing fabric",
    "expression": "",
    "composition": "waist up",
    "lighting": "soft warm indoor lighting"
  },
  "output_node": "16",
  "workflow": { ... }
}
```

### 6. load 时覆盖逻辑
- `--seed` → 遍历所有节点，找到 class_type 为 KSampler 的，替换 seed
- `--clothing`/`--scene`/`--expression`/`--lighting` → 重建正面提示词，找到 CLIPTextEncode 正面节点替换 text
- 提示词重建需要加载 _default.json 的 prompt_template

### 7. CLI 参数变更
在 argparse 中新增：
```python
parser.add_argument('--export-workflow', metavar='PATH', help='导出工作流到 JSON 文件，不执行')
parser.add_argument('--load-workflow', metavar='PATH', help='从 JSON 文件加载工作流执行')
```

互斥逻辑：
- `--export-workflow` 和 `--load-workflow` 不能同时使用
- `--export-workflow` 和 `--load-workflow` 与 `--scene-config` 可组合使用

### 8. main() 流程调整

```
if --export-workflow:
    构建配置和提示词 → 构建工作流 → 导出 JSON → 打印路径 → 退出
    
elif --load-workflow:
    加载 JSON → 可选覆盖参数 → 上传参考图(如需) → 提交执行 → 输出结果
    
else:
    原有流程不变
```

## 约束
- 不改变 generate() 函数的签名和返回值（保持向后兼容）
- 不改变 _default.json 和场景 JSON 的格式
- 导出的 JSON 必须是合法的 ComfyUI API 格式（可直接在 ComfyUI Web UI 加载）
- 所有 print 输出保持现有格式，新增用 `[EXPORT]` 和 `[LOAD]` 前缀
