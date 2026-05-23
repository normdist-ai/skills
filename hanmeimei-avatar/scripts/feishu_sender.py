#!/usr/bin/env python3
"""
飞书三气泡发送器 — 独立于生图脚本，负责把写真消息分三个气泡发到飞书。
用法：echo "selfie-v5 的 stdout" | python3 feishu_sender.py
    或：python3 feishu_sender.py < /path/to/stdout_file
    或：python3 feishu_sender.py "/path/to/stdout_file"

输入格式（selfie-v5.py 的 stdout，兼容新旧两种格式）：
    旧版：MEDIA:/path/to/image.png
    新版：[HMM-xxx.png](file:///path/to/image.png)
    时间：2026-05-23 11:00:00
    地点：咖啡馆
    种子：123456789
    ---
    想法文字

三气泡发送顺序：
    ① 图片
    ② 引用块（时间/地点/种子）
    ③ 想法文字

退出码：0=成功, 1=失败
stdout：空（成功时静默，cron 不会再投递）
stderr：错误信息
"""

import sys
import os
import json
import io
import yaml

# 走 hermes-agent 的 venv，里面有 lark_oapi
_VENV = "/home/jarvis/.hermes/hermes-agent/venv/lib/python3.11/site-packages"
if _VENV not in sys.path:
    sys.path.insert(0, _VENV)

from lark_oapi import Client
from lark_oapi.api.im.v1 import CreateImageRequest, CreateMessageRequest
from lark_oapi.api.im.v1.model import CreateImageRequestBody, CreateMessageRequestBody


def load_feishu_config():
    """从韩梅梅 profile 的 config.yaml 读飞书凭证"""
    # 注意：hermes venv 里 $HOME 可能被覆写，不能用 expanduser
    config_path = "/home/jarvis/.hermes/profiles/hanmeimei/config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    platforms = cfg.get("platforms", {})
    feishu = platforms.get("feishu", {})
    return feishu.get("app_id", ""), feishu.get("app_secret", "")


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


def upload_and_send_image(client: Client, chat_id: str, image_path: str):
    """上传图片到飞书并发送（气泡1）"""
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    image_file = io.BytesIO(image_bytes)
    image_file.name = os.path.basename(image_path)

    body = (
        CreateImageRequestBody.builder()
        .image_type("message")
        .image(image_file)
        .build()
    )
    request = CreateImageRequest.builder().request_body(body).build()
    response = client.im.v1.image.create(request)

    if not response.success():
        raise RuntimeError(
            f"图片上传失败: code={response.code}, msg={response.msg}"
        )

    image_key = response.data.image_key
    payload_str = json.dumps({"image_key": image_key}, ensure_ascii=False)

    send_request = (
        CreateMessageRequest.builder()
        .receive_id_type("chat_id")
        .request_body(
            CreateMessageRequestBody.builder()
            .receive_id(chat_id)
            .msg_type("image")
            .content(payload_str)
            .build()
        )
        .build()
    )
    send_response = client.im.v1.message.create(send_request)

    if not send_response.success():
        raise RuntimeError(
            f"图片发送失败: code={send_response.code}, msg={send_response.msg}"
        )

    print(f"[sender] 气泡1（图片）已发送", file=sys.stderr)


def send_text(client: Client, chat_id: str, text: str, label: str):
    """发送文本消息（气泡2或3）"""
    payload_str = json.dumps({"text": text}, ensure_ascii=False)

    request = (
        CreateMessageRequest.builder()
        .receive_id_type("chat_id")
        .request_body(
            CreateMessageRequestBody.builder()
            .receive_id(chat_id)
            .msg_type("text")
            .content(payload_str)
            .build()
        )
        .build()
    )
    response = client.im.v1.message.create(request)

    if not response.success():
        raise RuntimeError(
            f"{label}发送失败: code={response.code}, msg={response.msg}"
        )

    print(f"[sender] {label}已发送", file=sys.stderr)


def main():
    # 读取 stdin 或参数指定的文件
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
        print("[sender] 未找到 MEDIA: 行，跳过发送", file=sys.stderr)
        sys.exit(1)

    # 读配置
    app_id, app_secret = load_feishu_config()
    if not app_id or not app_secret:
        print("[sender] 飞书凭证缺失", file=sys.stderr)
        sys.exit(1)

    chat_id = os.environ.get("FEISHU_CHAT_ID", "oc_1fac55adbc3e448aabcfc3839955e14a")

    client = Client.builder().app_id(app_id).app_secret(app_secret).build()

    # 气泡1：图片
    upload_and_send_image(client, chat_id, parsed["image_path"])

    # 气泡2：引用块（时间/地点/种子）
    if parsed["info"]:
        send_text(client, chat_id, parsed["info"], "气泡2（信息）")

    # 气泡3：想法
    if parsed["thought"]:
        send_text(client, chat_id, parsed["thought"], "气泡3（想法）")

    # stdout 为空 — cron 不会再投递
    print("[sender] ✅ 三气泡发送完成", file=sys.stderr)


if __name__ == "__main__":
    main()
