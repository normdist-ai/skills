#!/usr/bin/env python3
"""使用 default.json 生成韩梅梅照片"""
import json
import urllib.request
import sys

# 从 default.json 读取工作流
with open(r'd:\TRAE\workspace-skills\.trae\skills\hanmeimei-avatar\workflows\default.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# 提交到 ComfyUI 服务器
url = "http://10.28.9.6:8188/api/prompt"
data = json.dumps(workflow).encode('utf-8')
req = urllib.request.Request(url, data=data, method='POST')
req.add_header('Content-Type', 'application/json')

print("正在使用 default.json 提交工作流到 ComfyUI 服务器...")
try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(f"✅ 工作流已提交! prompt_id: {result.get('prompt_id')}")
except Exception as e:
    print(f"❌ 错误: {e}", file=sys.stderr)
    sys.exit(1)
