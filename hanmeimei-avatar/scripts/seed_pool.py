#!/usr/bin/env python3
"""
seed_pool.py — good-seeds.txt 种子池管理工具（独立可运行）

用法：
    # 列出当前种子池
    python seed_pool.py list
    
    # 追加一个好种子到池
    python seed_pool.py add <seed> [scene_tag] [note]
    
    # 从池中随机选一个种子
    python seed_pool.py pick
    
    # 列出某个场景的种子
    python seed_pool.py list --scene cafe
"""

import argparse
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
GOOD_SEEDS_FILE = SCRIPT_DIR / "good-seeds.txt"


def load_seeds():
    """加载 good-seeds.txt，返回 [(seed, tags, note)]"""
    seeds = []
    if not GOOD_SEEDS_FILE.exists():
        return seeds
    with open(GOOD_SEEDS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)
            if len(parts) >= 1:
                try:
                    seed_val = int(parts[0])
                    rest = parts[1] if len(parts) > 1 else ""
                    # 解析 tags 和 note（格式：tag1 tag2  [timestamp] note）
                    ts_match = rest.find(" [")
                    if ts_match >= 0:
                        note_part = rest[ts_match + 2:]  # skip " ["
                        bracket_end = note_part.rfind("]")
                        note = note_part[:bracket_end] if bracket_end > 0 else note_part
                        tags = rest[:ts_match].strip()
                    else:
                        tags = rest.strip()
                        note = ""
                    seeds.append((seed_val, tags, note))
                except ValueError:
                    continue
    return seeds


def add_seed(seed, scene="", note=""):
    """追加种子到 good-seeds.txt"""
    tag = f" {scene}" if scene else ""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    comment = f"  {note}" if note else ""
    with open(GOOD_SEEDS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{seed}{tag}  [{ts}]{comment}\n")
    print(f"[OK] 已追加种子 {seed}{tag}")


def pick():
    """从池中随机选一个"""
    import random
    seeds = load_seeds()
    if not seeds:
        print("[WARN] 种子池为空")
        return
    chosen = random.choice(seeds)
    print(f"选中: {chosen[0]} ({chosen[1]}) — {chosen[2]}")


def list_seeds(scene=None):
    """列出种子池"""
    seeds = load_seeds()
    if not seeds:
        print("[WARN] 种子池为空")
        return
    
    # 按场景分组显示
    groups = {"通用": []}
    for seed, tags, note in seeds:
        scene_tags = [t.strip() for t in tags.split(",")] if tags else ["通用"]
        found_group = False
        for st in scene_tags:
            if st not in groups:
                groups[st] = []
            groups[st].append((seed, note))
    
    # 过滤场景
    if scene and scene != "全部":
        seeds_to_show = groups.get(scene, [])
        if seeds_to_show:
            print(f"\n=== {scene} 种子池 ({len(seeds_to_show)}个) ===")
            for s, n in seeds_to_show:
                note_str = f" — {n}" if n else ""
                print(f"  {s}{note_str}")
        else:
            print(f"[WARN] 场景 '{scene}' 没有种子")
    else:
        # 按场景分组显示
        total = sum(len(v) for v in groups.values())
        print(f"\n=== 种子池总计 ({total}个种子) ===")
        for name, seeds_in_group in sorted(groups.items()):
            if not seeds_in_group:
                continue
            print(f"\n--- {name} ({len(seeds_in_group)}个) ---")
            for s, n in seeds_in_group:
                note_str = f" — {n}" if n else ""
                print(f"  {s}{note_str}")


def main():
    parser = argparse.ArgumentParser(description="种子池管理工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # add
    add_parser = subparsers.add_parser("add", help="追加种子到池")
    add_parser.add_argument("seed", type=int, help="种子号")
    add_parser.add_argument("--scene", default="", help="场景标签（逗号分隔）")
    add_parser.add_argument("--note", default="", help="备注说明")
    
    # list
    list_parser = subparsers.add_parser("list", help="列出种子池")
    list_parser.add_argument("--scene", default=None, help="按场景过滤")
    
    # pick
    subparsers.add_parser("pick", help="从池中随机选一个种子")
    
    args = parser.parse_args()
    
    if args.command == "add":
        add_seed(args.seed, scene=args.scene, note=args.note)
    elif args.command == "list":
        list_seeds(scene=args.scene)
    elif args.command == "pick":
        pick()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
