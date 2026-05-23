#!/usr/bin/env python3
"""
韩梅梅技能定时任务入口

功能列表：
1. 定时出图
2. 清理过期图片（本地和 ComfyUI 服务器）
3. 推送精选照片到飞书
4. 种子池维护
5. 生成统计报告

使用方法：
    # 执行所有任务
    python scheduler.py --all
    
    # 只执行定时出图
    python scheduler.py --generate
    
    # 只清理过期图片
    python scheduler.py --cleanup
    
    # 推送精选照片
    python scheduler.py --feature
    
    # 种子池维护
    python scheduler.py --maintain-seeds
    
    # 生成统计报告
    python scheduler.py --stats
    
    # 清理 ComfyUI 服务器缓存
    python scheduler.py --cleanup-comfyui
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime
import json
import importlib.util

# 添加 scripts 目录到路径
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

# 动态导入 selfie-v5.py（带连字符的文件名无法直接 import）
selfie_v5_spec = importlib.util.spec_from_file_location("selfie_v5", SCRIPT_DIR / "selfie-v5.py")
selfie_v5 = importlib.util.module_from_spec(selfie_v5_spec)
sys.modules["selfie_v5"] = selfie_v5  # 注册到 sys.modules，允许 from selfie_v5 import ...
selfie_v5_spec.loader.exec_module(selfie_v5)

WORKSPACE_ROOT = selfie_v5.WORKSPACE_ROOT
AVATAR_DIR = selfie_v5.AVATAR_DIR
CONFIG_FILE = selfie_v5.CONFIG_FILE
ALBUM_DIR = selfie_v5.ALBUM_DIR
load_config = selfie_v5.load_config
cleanup_old_outputs = selfie_v5.cleanup_old_outputs
ensure_avatar_dirs = selfie_v5.ensure_avatar_dirs
find_workspace_root = selfie_v5.find_workspace_root
get_output_dir = selfie_v5.get_output_dir

from comfyui_client import ComfyUIClient


def cleanup_comfyui_server():
    """
    清理 ComfyUI 服务器上的缓存图片
    
    调用 deletefile.py 脚本执行清理
    """
    print("[INFO] ComfyUI 服务器缓存清理")
    print("[INFO] ------------------------------------------------")
    
    try:
        config = load_config()
        ssh_config = config.get("ssh", {})
        
        if not ssh_config.get("enabled"):
            print("[WARN] SSH 清理未启用", file=sys.stderr)
            print("[INFO] ------------------------------------------------")
            print("[INFO] 在 config.json 中配置 SSH 以启用服务器清理：")
            print('[INFO]')
            print('[INFO] {')
            print('[INFO]   "ssh": {')
            print('[INFO]     "enabled": true,')
            print('[INFO]     "host": "10.28.9.6",')
            print('[INFO]     "user": "your_username",')
            print('[INFO]     "output_dir": "/path/to/ComfyUI/output"')
            print('[INFO]   }')
            print('[INFO] }')
            print("[INFO] ------------------------------------------------")
            return
        
        # 调用 deletefile.py 执行清理
        retention_days = config.get("output", {}).get("retention_days", 30)
        cmd = [
            sys.executable,
            str(SCRIPT_DIR / "deletefile.py"),
            "--cleanup",
            "--pattern", "HMM-*.png",
            "--retention-days", str(retention_days)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"[INFO] {result.stdout.strip()}")
        else:
            print(f"[ERROR] 清理失败: {result.stderr.strip()}", file=sys.stderr)
        
        print("[INFO] ------------------------------------------------")
        
    except Exception as e:
        print(f"[ERROR] 清理 ComfyUI 服务器失败: {e}", file=sys.stderr)


def task_generate():
    """
    任务1：定时出图
    使用 selfie-v5.py 生成一张随机场景的照片
    """
    print("[TASK] 开始定时出图...")
    
    from selfie_v5 import main as generate_main
    
    # 临时修改 sys.argv 模拟命令行参数
    old_argv = sys.argv
    try:
        sys.argv = ['selfie-v5.py']
        generate_main()
        print("[TASK] 定时出图完成")
    except Exception as e:
        print(f"[ERROR] 定时出图失败: {e}")
        raise
    finally:
        sys.argv = old_argv


def task_cleanup():
    """
    任务2：清理过期图片
    清理 outputs 文件夹中超过保留天数的图片
    """
    print("[TASK] 开始清理过期图片...")
    
    try:
        config = load_config()
        retention_days = config["output"].get("retention_days", 30)
        
        deleted_count = cleanup_old_outputs(days_to_keep=retention_days)
        
        if deleted_count > 0:
            print(f"[TASK] 清理了 {deleted_count} 个过期图片（保留 {retention_days} 天）")
        else:
            print("[TASK] 没有需要清理的过期图片")
            
    except Exception as e:
        print(f"[ERROR] 清理过期图片失败: {e}")
        raise


def task_feature():
    """
    任务3：推送精选照片到飞书
    从 album 文件夹中随机选择一张照片推送到飞书
    """
    print("[TASK] 开始推送精选照片...")
    
    try:
        # 获取 album 中的照片
        album_images = sorted(ALBUM_DIR.glob("*.png"))
        
        if not album_images:
            print("[INFO] album 文件夹中没有精选照片")
            return
        
        # 随机选择一张
        import random
        selected = random.choice(album_images)
        
        # 读取对应的 JSON 元数据
        json_path = selected.with_suffix(".json")
        metadata = {}
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        
        # 构建消息
        seed = metadata.get("seed", "unknown")
        scene = metadata.get("scene", "unknown")
        saved_at = metadata.get("saved_at", selected.stat().st_mtime)
        
        # 格式化时间
        if isinstance(saved_at, str):
            time_str = saved_at[:19]  # ISO 8601 格式
        else:
            time_str = datetime.fromtimestamp(saved_at).strftime('%Y-%m-%d %H:%M:%S')
        
        # 中文场景名映射
        SCENE_NAMES = {
            "bedroom": "卧室",
            "boulevard": "林荫道",
            "cafe": "咖啡馆",
            "library": "图书馆",
            "rooftop": "天台",
            "park": "公园",
            "travel": "旅行途中"
        }
        scene_cn = SCENE_NAMES.get(scene, scene)
        
        message = f"""MEDIA:{selected}

时间：{time_str}
地点：{scene_cn}
种子：{seed}

---
来自精选相册的回忆"""
        
        # 输出到 stdout（cron 会捕获并发送）
        print(message)
        print(f"[TASK] 已推送精选照片: {selected.name}")
        
    except Exception as e:
        print(f"[ERROR] 推送精选照片失败: {e}")
        raise


def task_maintain_seeds():
    """
    任务4：种子池维护
    检查并清理 good-seeds.txt 中的重复种子
    """
    print("[TASK] 开始种子池维护...")
    
    try:
        seeds_file = SCRIPT_DIR.parent / "good-seeds.txt"
        
        if not seeds_file.exists():
            print("[INFO] good-seeds.txt 文件不存在")
            return
        
        with open(seeds_file, "r", encoding="utf-8") as f:
            seeds = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        # 去重
        unique_seeds = list(dict.fromkeys(seeds))  # 保持顺序去重
        
        if len(unique_seeds) < len(seeds):
            # 重新写入（保留注释）
            with open(seeds_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # 分离注释和种子
            comments = [line for line in lines if line.strip().startswith("#")]
            
            with open(seeds_file, "w", encoding="utf-8") as f:
                # 写入注释
                for comment in comments:
                    f.write(comment)
                # 写入去重后的种子
                for seed in unique_seeds:
                    f.write(f"{seed}\n")
            
            removed = len(seeds) - len(unique_seeds)
            print(f"[TASK] 种子池维护完成，移除了 {removed} 个重复种子")
        else:
            print("[TASK] 种子池无需维护（没有重复种子）")
        
    except Exception as e:
        print(f"[ERROR] 种子池维护失败: {e}")
        raise


def task_stats():
    """
    任务5：生成统计报告
    统计 outputs、album 文件夹的图片数量
    """
    print("[TASK] 开始生成统计报告...")
    
    try:
        ensure_avatar_dirs()
        
        outputs_dir = AVATAR_DIR / "outputs"
        album_dir = AVATAR_DIR / "album"
        
        # 统计 outputs 文件夹
        outputs_images = list(outputs_dir.glob("*.png")) if outputs_dir.exists() else []
        
        # 统计 album 文件夹
        album_images = list(album_dir.glob("*.png")) if album_dir.exists() else []
        
        # 计算总大小
        outputs_size = sum(img.stat().st_size for img in outputs_images) / (1024 * 1024)  # MB
        album_size = sum(img.stat().st_size for img in album_images) / (1024 * 1024)  # MB
        
        # 最近 7 天生成的图片数
        from datetime import timedelta
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_outputs = [img for img in outputs_images 
                          if datetime.fromtimestamp(img.stat().st_mtime) > seven_days_ago]
        
        report = f"""
========== 韩梅梅技能统计报告 ==========
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

1. 输出文件夹 (~/.avatar/outputs)
   - 总图片数: {len(outputs_images)} 张
   - 总大小: {outputs_size:.2f} MB
   - 最近7天: {len(recent_outputs)} 张

2. 精选相册 (~/.avatar/album)
   - 总图片数: {len(album_images)} 张
   - 总大小: {album_size:.2f} MB

3. 质量指标
   - 精选率: {len(album_images)/len(outputs_images)*100:.1f}% ({len(album_images)}/{len(outputs_images)})
   - 近期活跃度: {len(recent_outputs)} 张/周

4. 存储占用
   - 总计: {(outputs_size + album_size):.2f} MB
=====================================
"""
        print(report)
        
    except Exception as e:
        print(f"[ERROR] 生成统计报告失败: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(
        description="韩梅梅技能定时任务入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument("--all", action="store_true", help="执行所有任务")
    parser.add_argument("--generate", action="store_true", help="定时出图")
    parser.add_argument("--cleanup", action="store_true", help="清理过期图片")
    parser.add_argument("--feature", action="store_true", help="推送精选照片")
    parser.add_argument("--maintain-seeds", action="store_true", help="种子池维护")
    parser.add_argument("--stats", action="store_true", help="生成统计报告")
    parser.add_argument("--cleanup-comfyui", action="store_true", help="显示 ComfyUI 服务器缓存清理方案")
    
    args = parser.parse_args()
    
    # 如果没有指定任何任务，默认执行定时出图
    if not any([args.all, args.generate, args.cleanup, args.feature, args.maintain_seeds, args.stats, args.cleanup_comfyui]):
        print("[INFO] 未指定任务，默认执行定时出图")
        task_generate()
        return
    
    print(f"\n{'='*50}")
    print(f"韩梅梅技能定时任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")
    
    # 执行任务
    if args.all:
        print("[INFO] 执行所有任务\n")
        task_generate()
        print()
        task_cleanup()
        print()
        # task_feature()  # 可选：是否定时推送精选照片
        # print()
        task_maintain_seeds()
        print()
        task_stats()
    
    if args.generate:
        task_generate()
    
    if args.cleanup:
        task_cleanup()
    
    if args.feature:
        task_feature()
    
    if args.maintain_seeds:
        task_maintain_seeds()
    
    if args.stats:
        task_stats()
    
    if args.cleanup_comfyui:
        cleanup_comfyui_server()
    
    print(f"\n{'='*50}")
    print("定时任务完成")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()