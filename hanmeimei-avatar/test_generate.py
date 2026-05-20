#!/usr/bin/env python3
"""测试生成韩梅梅照片"""
import json
import urllib.request
import sys

# 工作流 JSON（从 faceid.json 读取）
workflow = {
    "prompt": {
        "3": {
            "inputs": {
                "seed": 98994781,
                "steps": 30,
                "cfg": 3.5,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1,
                "model": ["18", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler"
        },
        "4": {
            "inputs": {
                "ckpt_name": "chilloutmix-Ni.safetensors"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "5": {
            "inputs": {
                "width": 512,
                "height": 768,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        }
    }
}

# 提交到 ComfyUI 服务器
url = "http://10.28.9.6:8188/api/prompt"
data = json.dumps(workflow).encode('utf-8')
req = urllib.request.Request(url, data=data, method='POST')
req.add_header('Content-Type', 'application/json')

print("正在提交工作流到 ComfyUI 服务器...")
try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(f"工作流已提交! prompt_id: {result.get('prompt_id')}")
except Exception as e:
    print(f"错误: {e}", file=sys.stderr)
    sys.exit(1)
