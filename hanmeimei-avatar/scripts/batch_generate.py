#!/usr/bin/env python3
"""韩梅梅写真批量生成 - 批量调度引擎

加载多个场景配置，串行调用 generate.py 的 generate() 函数。

用法:
    from batch_generate import batch_generate

    results = batch_generate(scenes=["bedroom", "cafe", "rooftop"])

命令行:
    python batch_generate.py --scenes bedroom cafe rooftop --clothing "white shirt"
"""

import json
import os
import sys
import time

from generate import generate, load_scene_config, _load_default_config


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)


def list_available_scenes():
    scenes_dir = os.path.join(SKILL_DIR, "references", "scenes")
    scenes = []
    for f in sorted(os.listdir(scenes_dir)):
        if f.endswith(".json") and not f.startswith("_"):
            scenes.append(f.replace(".json", ""))
    return scenes


def batch_generate(
    scenes=None,
    clothing=None,
    expression=None,
    composition=None,
    max_retries=3,
):
    """
    批量写真生成

    参数:
        scenes: 场景名称列表，None 则全部场景
        clothing: 统一穿搭（覆盖场景配置）
        expression: 统一表情（覆盖场景配置）
        composition: 统一构图（覆盖场景配置）
        max_retries: 每张最大重试次数

    返回:
        list[dict]: 每张的结果列表
    """
    if scenes is None:
        scenes = list_available_scenes()

    results = []
    total = len(scenes)

    print(f"\n{'='*60}")
    print(f"批量生成 {total} 张写真...")
    print(f"{'='*60}")

    for i, scene_name in enumerate(scenes, 1):
        print(f"\n[{i}/{total}] {scene_name}")
        print("-" * 40)

        scene_config = load_scene_config(scene_name)
        if scene_config is None:
            print(f"  ❌ 场景配置不存在: {scene_name}")
            results.append({"status": "error", "message": f"场景配置不存在: {scene_name}", "scene": scene_name})
            continue

        gen_kwargs = {
            "scene": scene_config.get("scene", ""),
            "clothing": clothing or scene_config.get("clothing", ""),
            "expression": expression or scene_config.get("expression", ""),
            "composition": composition or scene_config.get("composition", "waist up"),
            "lighting": scene_config.get("lighting"),
            "scene_config": scene_config,
            "max_retries": max_retries,
        }

        start_time = time.time()
        result = generate(**gen_kwargs)
        elapsed = time.time() - start_time

        result["_name"] = scene_config.get("name", scene_name)
        result["_scene"] = scene_name
        result["_elapsed"] = round(elapsed, 1)
        results.append(result)

        status_icon = "✅" if result["status"] == "ok" else "❌"
        print(f"  {status_icon} {result['_name']}: {result['status']} ({elapsed:.1f}s)")
        if result["status"] == "ok":
            print(f"    文件: {result['path']}")

    print(f"\n{'='*60}")
    print(f"批量生成完成！")
    print(f"{'='*60}")

    ok_count = sum(1 for r in results if r["status"] == "ok")
    fail_count = sum(1 for r in results if r["status"] != "ok")
    print(f"  成功: {ok_count}, 失败: {fail_count} / 共 {total}")

    for r in results:
        s = "✅" if r["status"] == "ok" else "❌"
        t = r.get("_elapsed", "?")
        print(f"  {s} {r.get('_name', '?')} ({t}s): {r['status']}")

    return results


def main():
    import argparse

    available = list_available_scenes()

    parser = argparse.ArgumentParser(description="韩梅梅写真批量生成")
    parser.add_argument("--scenes", nargs="*", default=None, choices=available,
                        help="场景名称列表，不指定则全部")
    parser.add_argument("--clothing", default=None, help="统一穿搭")
    parser.add_argument("--expression", default=None, help="统一表情")
    parser.add_argument("--composition", default=None, help="统一构图")
    parser.add_argument("--max-retries", type=int, default=3, help="每张最大重试次数")
    args = parser.parse_args()

    results = batch_generate(
        scenes=args.scenes,
        clothing=args.clothing,
        expression=args.expression,
        composition=args.composition,
        max_retries=args.max_retries,
    )

    all_ok = all(r["status"] == "ok" for r in results)
    return results, all_ok


if __name__ == "__main__":
    _, ok = main()
    sys.exit(0 if ok else 1)
