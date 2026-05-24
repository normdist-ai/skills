#!/usr/bin/env python3
"""
Trae 发送器 — 独立于生图脚本，负责把写真消息发送到 Trae 平台。
用法：echo "selfie-v5 的 stdout" | python3 send_to_trea.py
    或：python3 send_to_trea.py < /path/to/stdout_file
    或：python3 send_to_trea.py "/path/to/stdout_file"

输入格式（selfie-v5.py 的 stdout）：
    MEDIA:/path/to/image.png
    > 📸 时间：2026-05-23 11:00:00
    > 📍 地点：咖啡馆
    > 🎲 种子：123456789
    ---
    想法文字

输出格式（JSON）：
    {
        "image_path": "/path/to/image.png",
        "info": "📸 时间：2026-05-23 11:00:00\n📍 地点：咖啡馆\n🎲 种子：123456789",
        "thought": "想法文字",
        "image_link": "[图片](file:///d:/path/to/image.png)"
    }

退出码：0=成功, 1=失败
stdout：JSON 格式的输出数据
stderr：日志信息
"""

import sys
import os
import json
from pathlib import Path


def parse_stdin(text: str) -> dict:
    """解析 selfie-v5.py 的 stdout，提取图片路径、信息行、想法
    
    兼容两种图片行格式：
    - 旧版：MEDIA:/path/to/image.png
    - 新版：[HMM-xxx.png](file:///path/to/image.png)
    
    输入格式：
        图片行
        ---（可选分隔符）
        信息行（时间/地点/种子）
        ---
        想法文字
    """
    import re
    lines = text.strip().split("\n")
    image_path = None
    info_lines = []
    thought_lines = []
    
    # 找最后一个 --- 作为 thought 分界线
    last_sep_idx = -1
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == "---":
            last_sep_idx = i
            break
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # 图片路径：兼容 MEDIA: 和 [name](file:///path) 两种格式
        if stripped.startswith("MEDIA:"):
            image_path = stripped[6:]
        elif re.match(r'^\[.*\]\(file:///', stripped):
            # 新版格式：[filename](file:///path) — 提取 file:/// 后的路径（保留前导 /）
            m = re.match(r'^\[.*\]\(file:///*(/.+?)\)', stripped)
            if m:
                image_path = m.group(1)
        elif i > last_sep_idx and last_sep_idx >= 0:
            # 最后一个 --- 之后的内容是 thought
            if stripped:
                thought_lines.append(stripped)
        elif stripped != "---":
            # 图片行和最后一个 --- 之间的非空非分隔行是 info
            if stripped:
                info_lines.append(stripped)

    return {
        "image_path": image_path,
        "info": "\n".join(info_lines),
        "thought": "\n".join(thought_lines),
    }


def create_image_link(image_path: str) -> str:
    """创建图片的 Markdown 链接"""
    abs_path = Path(image_path).resolve().as_posix()
    return f"[图片](file:///{abs_path})"


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            raw = f.read()
    else:
        raw = sys.stdin.read()

    if not raw.strip():
        print("[sender] 输入为空，跳过", file=sys.stderr)
        sys.exit(0)

    parsed = parse_stdin(raw)
    if not parsed["image_path"]:
        print("[sender] 未找到 MEDIA: 行，跳过", file=sys.stderr)
        sys.exit(1)

    image_path = parsed["image_path"]
    if not os.path.exists(image_path):
        print(f"[sender] 图片文件不存在: {image_path}", file=sys.stderr)
        sys.exit(1)

    result = {
        "image_path": image_path,
        "info": parsed["info"],
        "thought": parsed["thought"],
        "image_link": create_image_link(image_path),
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("[sender] ✅ 数据已发送到 Trae", file=sys.stderr)


if __name__ == "__main__":
    main()