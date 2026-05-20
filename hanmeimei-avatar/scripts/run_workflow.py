#!/usr/bin/env python3
"""
韩梅梅技能 - 工作流执行器
读取工作流文件，调用 comfyui_client 生成图片。

用法:
    python run_workflow.py --workflow workflows/default.json
    python run_workflow.py --workflow workflows/default.json --output ./outputs
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "outputs"

sys.path.append(str(SCRIPT_DIR))

from comfyui_client import ComfyUIClient


def run_workflow_file(
    workflow_path: str,
    output_dir: Optional[str] = None,
    host: str = "http://10.28.9.6:8188",
    seed: int = None,
):
    """
    读取工作流文件并执行
    
    Args:
        workflow_path: 工作流 JSON 文件路径
        output_dir: 输出目录
        host: ComfyUI 服务器地址
        seed: 可选的随机种子（覆盖工作流中的 seed）
    
    Returns:
        dict: {"success": bool, "file": str, "error": str}
    """
    if output_dir is None:
        output_dir = str(DEFAULT_OUTPUT_DIR)
    
    workflow_path = Path(workflow_path)
    
    if not workflow_path.exists():
        return {"success": False, "error": f"工作流文件不存在: {workflow_path}"}
    
    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow = json.load(f)
    
    if seed is not None:
        workflow = update_seed(workflow, seed)
    
    client = ComfyUIClient(host=host)
    result = client.run_workflow(workflow, output_dir=output_dir)
    
    if result["success"]:
        original_path = Path(result["file"])
        now = datetime.now()
        datetime_str = now.strftime("%Y%m%d-%H%M%S")
        seed_value = seed if seed is not None else "default"
        new_filename = f"HMM-{seed_value}-{datetime_str}.png"
        new_path = original_path.parent / new_filename
        
        import os
        os.rename(result["file"], str(new_path))
        result["file"] = str(new_path)
    
    return result


def update_seed(workflow: dict, seed: int) -> dict:
    """更新工作流中的所有 seed 值"""
    for node_id, node in workflow.get("prompt", {}).items():
        if "seed" in node.get("inputs", {}):
            node["inputs"]["seed"] = seed
    return workflow


def main():
    parser = argparse.ArgumentParser(
        description="韩梅梅技能 - 工作流执行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--workflow", "-w",
        required=True,
        help="工作流 JSON 文件路径"
    )
    
    parser.add_argument(
        "--output", "-o",
        default=None,
        help=f"输出目录（默认: {DEFAULT_OUTPUT_DIR}）"
    )
    
    parser.add_argument(
        "--host",
        default="http://10.28.9.6:8188",
        help="ComfyUI 服务器地址"
    )
    
    parser.add_argument(
        "--seed", "-s",
        type=int,
        help="随机种子（覆盖工作流中的 seed）"
    )
    
    args = parser.parse_args()
    
    print(f"📋 工作流文件: {args.workflow}")
    print(f"📁 输出目录: {args.output}")
    print(f"🌐 服务器: {args.host}")
    if args.seed:
        print(f"🔢 Seed: {args.seed}")
    print()
    
    result = run_workflow_file(
        workflow_path=args.workflow,
        output_dir=args.output,
        host=args.host,
        seed=args.seed,
    )
    
    if result["success"]:
        print(f"✅ 生成成功！")
        print(f"📁 输出文件: {result['file']}")
        print(f'"file": "{result["file"]}"')
    else:
        print(f"❌ 生成失败！")
        print(f"错误: {result.get('error', '未知错误')}")
        sys.exit(1)


if __name__ == "__main__":
    main()