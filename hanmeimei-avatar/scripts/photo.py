#!/usr/bin/env python3
"""
韩梅梅照片技能 - 默认入口脚本

读取 workflows 文件夹中的工作流文件，调用 comfyui_client 生成图片。

用法:
    python photo.py                    # 使用 default.json，随机种子
    python photo.py --random           # 随机工作流，随机种子
    python photo.py --workflow cafe    # 指定工作流，随机种子
    python photo.py --seed 123456789   # 使用 default.json，指定种子
    python photo.py --workflow cafe --seed 123456789  # 指定工作流和种子
    python photo.py --clothing "red dress" --expression "happy smile"  # 自定义穿搭和表情
    python photo.py --list             # 列出可用工作流
    
模块导入:
    from photo import run_workflow, list_workflows
    result = run_workflow("cafe", seed=123456)
    # result: {"success": True, "file": "...", "seed": 123456, "workflow": "cafe"}
"""

import argparse
import json
import os
import random
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORKFLOWS_DIR = SKILL_DIR / "workflows"
DEFAULT_OUTPUT_DIR = SKILL_DIR / "outputs"

sys.path.append(str(SCRIPT_DIR))
from comfyui_client import ComfyUIClient


def list_workflows() -> list:
    """列出可用的工作流文件，返回工作流名称列表"""
    if not WORKFLOWS_DIR.exists():
        print("❌ workflows 目录不存在", file=sys.stderr)
        return []
    
    workflows = sorted(WORKFLOWS_DIR.glob("*.json"))
    if not workflows:
        print("❌ 未找到工作流文件", file=sys.stderr)
        return []
    
    names = [wf.stem for wf in workflows]
    print("📋 可用工作流:", file=sys.stderr)
    for wf in workflows:
        name = wf.stem
        size = wf.stat().st_size // 1024
        print(f"  - {name} ({size} KB)", file=sys.stderr)
    return names


def get_random_workflow():
    """获取随机工作流名称"""
    workflows = sorted(WORKFLOWS_DIR.glob("*.json"))
    if not workflows:
        return None
    return random.choice(workflows).stem


def get_random_seed():
    """生成随机种子"""
    return random.randint(1, 999999999)


def update_prompt(workflow, clothing=None, expression=None, lighting=None):
    """更新工作流中的提示词"""
    for node_id, node in workflow.get("prompt", {}).items():
        if node.get("class_type") == "CLIPTextEncode" and "text" in node.get("inputs", {}):
            text = node["inputs"]["text"]
            
            if clothing:
                text = re.sub(r'wearing [^,]+', f'wearing {clothing}', text)
            
            if expression:
                expression_weighted = f"({expression}:1.5)"
                text = re.sub(r'playful expression, cute smile, twinkling eyes', expression_weighted, text)
                text = re.sub(r'(gentle|natural|happy|elegant|relaxed) smile', expression_weighted, text, flags=re.IGNORECASE)
                if 'smile' not in text.lower() and 'expression' not in text.lower():
                    text = text.replace('beautiful young Chinese woman', f'beautiful young Chinese woman, {expression_weighted}')
            
            if lighting:
                text = re.sub(r'natural window light, soft diffused daylight', lighting, text)
                text = re.sub(r'natural window light, soft diffused sunlight', lighting, text)
                text = re.sub(r'(soft|warm|natural|golden hour|window light|diffused) [a-zA-Z ]+lighting', f'{lighting}', text, flags=re.IGNORECASE)
            
            node["inputs"]["text"] = text
    return workflow


def update_load_image(workflow: dict, image_path: str) -> tuple:
    """
    更新工作流中的 LoadImage 节点
    
    Args:
        workflow: 工作流 JSON
        image_path: 图片路径
    
    Returns:
        (workflow, filename) 更新后的工作流和图片文件名
    """
    import os
    filename = os.path.basename(image_path)
    
    for node_id, node in workflow.get("prompt", {}).items():
        if node.get("class_type") == "LoadImage":
            node["inputs"]["image"] = filename
            node["inputs"]["upload"] = filename
    
    return workflow, filename


def run_workflow(
    workflow_name: str,
    seed: Optional[int] = None,
    output_dir: Optional[str] = None,
    clothing: Optional[str] = None,
    expression: Optional[str] = None,
    lighting: Optional[str] = None,
    face_image: Optional[str] = None,
) -> Dict:
    """
    运行指定的工作流
    
    Args:
        workflow_name: 工作流名称（不含 .json 后缀）
        seed: 随机种子（None 则自动生成）
        output_dir: 输出目录
        clothing: 穿搭描述
        expression: 表情描述
        lighting: 光线描述
        face_image: 脸部参考图片路径
    
    Returns:
        {"success": bool, "file": str, "seed": int, "workflow": str, "error": str}
    """
    if output_dir is None:
        output_dir = str(DEFAULT_OUTPUT_DIR)
    
    workflow_path = WORKFLOWS_DIR / f"{workflow_name}.json"
    
    if not workflow_path.exists():
        return {"success": False, "error": f"工作流文件不存在: {workflow_path}", "seed": seed, "workflow": workflow_name}
    
    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow = json.load(f)
    
    workflow = update_prompt(workflow, clothing, expression, lighting)
    
    if seed is not None:
        for node_id, node in workflow.get("prompt", {}).items():
            if "seed" in node.get("inputs", {}):
                node["inputs"]["seed"] = seed
    else:
        for node_id, node in sorted(workflow.get("prompt", {}).items()):
            if "seed" in node.get("inputs", {}):
                seed = node["inputs"]["seed"]
                break
        if seed is None:
            seed = get_random_seed()
    
    client = ComfyUIClient()
    
    input_images = None
    if face_image:
        workflow, image_filename = update_load_image(workflow, face_image)
        input_images = {image_filename: face_image}
        print(f"[INFO] 设置脸部参考图片: {face_image}", file=sys.stderr)
    
    result = client.run_workflow(workflow, output_dir=output_dir, input_images=input_images)
    
    if result["success"]:
        original_path = Path(result["file"])
        now = datetime.now()
        datetime_str = now.strftime("%Y%m%d-%H%M%S")
        new_filename = f"HMM-{datetime_str}-{seed}.png"
        new_path = original_path.parent / new_filename
        
        os.rename(result["file"], str(new_path))
        result["file"] = str(new_path)
        result["seed"] = seed
        result["workflow"] = workflow_name
    else:
        result["seed"] = seed
        result["workflow"] = workflow_name
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="韩梅梅照片技能",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python photo.py                    # 使用 default.json，随机种子
  python photo.py --random           # 随机工作流，随机种子
  python photo.py --workflow cafe    # 指定工作流，随机种子
  python photo.py --seed 123456789   # 使用 default.json，指定种子
  python photo.py --workflow cafe --seed 123456789  # 指定工作流和种子
  python photo.py --clothing "red dress" --expression "happy smile"  # 自定义参数
  python photo.py --list             # 列出可用工作流
        """,
    )
    
    parser.add_argument(
        "--workflow", "-w",
        default=None,
        help="工作流名称（默认: default）"
    )
    
    parser.add_argument(
        "--seed", "-s",
        type=str,
        default=None,
        help="随机种子（默认: 使用工作流默认值；'random': 随机生成）"
    )
    
    parser.add_argument(
        "--random", "-r",
        action="store_true",
        help="随机选择工作流和种子"
    )
    
    parser.add_argument(
        "--output", "-o",
        default=None,
        help=f"输出目录（默认: {DEFAULT_OUTPUT_DIR}）"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="列出所有可用工作流"
    )
    
    parser.add_argument(
        "--clothing", "-c",
        help="穿搭描述（覆盖工作流中的默认穿搭）"
    )
    
    parser.add_argument(
        "--expression", "-e",
        help="表情描述（覆盖工作流中的默认表情）"
    )
    
    parser.add_argument(
        "--lighting",
        dest="lighting",
        help="光线描述（覆盖工作流中的默认光线）"
    )
    
    parser.add_argument(
        "--face",
        help="脸部参考图片路径（用于FaceID修正）"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出 JSON 格式结果"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_workflows()
        return
    
    workflow_name = args.workflow
    seed = None
    
    if args.seed:
        if args.seed.lower() == "random":
            seed = get_random_seed()
        else:
            try:
                seed = int(args.seed)
            except ValueError:
                print(f"[ERROR] 无效的种子值: {args.seed}", file=sys.stderr)
                sys.exit(1)
    
    if args.random:
        workflow_name = get_random_workflow()
        seed = get_random_seed()
    else:
        if workflow_name is None:
            workflow_name = "default"
    
    print(f"📋 工作流: {workflow_name}", file=sys.stderr)
    if seed is not None:
        print(f"🔢 Seed: {seed}", file=sys.stderr)
    else:
        print(f"🔢 Seed: 使用工作流默认值", file=sys.stderr)
    if args.clothing:
        print(f"👗 穿搭: {args.clothing}", file=sys.stderr)
    if args.expression:
        print(f"😊 表情: {args.expression}", file=sys.stderr)
    if args.lighting:
        print(f"💡 光线: {args.lighting}", file=sys.stderr)
    print(f"📁 输出目录: {args.output}", file=sys.stderr)
    print(file=sys.stderr)
    
    result = run_workflow(
        workflow_name=workflow_name,
        seed=seed,
        output_dir=args.output,
        clothing=args.clothing,
        expression=args.expression,
        lighting=args.lighting,
        face_image=args.face,
    )
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    elif result["success"]:
        print(f"\n🎊 韩梅梅照片生成成功！", file=sys.stderr)
        print(f"📋 工作流: {result['workflow']}", file=sys.stderr)
        print(f"📁 文件: {result['file']}", file=sys.stderr)
        print(f"🔢 Seed: {result['seed']}", file=sys.stderr)
        print(json.dumps(result, ensure_ascii=False))
    else:
        error_msg = result.get('error', '未知错误')
        print(f"\n❌ 生成失败: {error_msg}", file=sys.stderr)
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()