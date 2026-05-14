#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""
缓存清理脚本
清理过期或损坏的缓存数据

Usage: scripts/clean_cache.py [OPTIONS]

Clean expired or corrupted LLM Benchmark cache data.

Options:
  --cache-dir PATH   Cache directory path (default: .llm-benchmark/cache)
  --days N           Clean cache older than N days (default: 30)
  --dry-run          Show files to delete without actually deleting
  --force            Actually delete files (required for non-dry-run)
  --invalid          Clean invalid cache files
  --help             Show this help message

Examples:
  scripts/clean_cache.py --dry-run
  scripts/clean_cache.py --days 30 --force
  scripts/clean_cache.py --invalid --force

Exit codes:
  0 - Success
  1 - No files to clean or operation cancelled
  2 - Script execution error
"""

import json
import sys
from pathlib import Path
from argparse import ArgumentParser
from datetime import datetime, timedelta

def get_file_age(file_path: Path) -> int:
    """获取文件年龄（天）"""
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
    age = datetime.now() - mtime
    return age.days

def get_retrieved_age(file_path: Path) -> int | None:
    """从缓存数据中获取 retrieved_at 日期并计算年龄"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        retrieved_at = data.get('retrieved_at')
        if retrieved_at:
            retrieved_date = datetime.strptime(retrieved_at, '%Y-%m-%d')
            age = (datetime.now() - retrieved_date).days
            return age
    except:
        pass
    return None

def is_valid_cache(file_path: Path) -> tuple[bool, str]:
    """检查缓存文件是否有效"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        required_fields = ['cache_version', 'model', 'provider', 'benchmarks', 'source', 'retrieved_at']
        missing = [f for f in required_fields if f not in data]
        
        if missing:
            return False, f"缺少必需字段: {', '.join(missing)}"
        
        if not data.get('benchmarks'):
            return False, "benchmarks 字段为空"
        
        return True, ""
    
    except json.JSONDecodeError:
        return False, "JSON 解析错误"
    except Exception as e:
        return False, str(e)

def main():
    parser = ArgumentParser(description='清理 LLM Benchmark 缓存数据')
    parser.add_argument('--cache-dir', type=str, default='.llm-benchmark/cache',
                        help='缓存目录路径')
    parser.add_argument('--days', type=int, default=30,
                        help='清理 N 天前的缓存')
    parser.add_argument('--dry-run', action='store_true',
                        help='仅显示将被删除的文件')
    parser.add_argument('--force', action='store_true',
                        help='强制删除文件（非 dry-run 模式必须）')
    parser.add_argument('--invalid', action='store_true',
                        help='清理无效的缓存文件')
    args = parser.parse_args()
    
    cache_dir = Path(args.cache_dir)
    
    if not cache_dir.exists():
        print(f"错误: 缓存目录不存在: {cache_dir}")
        sys.exit(2)
    
    cache_files = list(cache_dir.glob('*.json'))
    
    if not cache_files:
        print(f"缓存目录中没有文件: {cache_dir}")
        sys.exit(0)
    
    print(f"扫描缓存目录: {cache_dir}")
    print(f"发现 {len(cache_files)} 个缓存文件\n")
    
    to_delete = []
    
    for file_path in sorted(cache_files):
        reasons = []
        
        if args.invalid or args.days > 0:
            is_valid, error = is_valid_cache(file_path)
            if not is_valid:
                reasons.append(f"无效缓存: {error}")
        
        if args.days > 0:
            retrieved_age = get_retrieved_age(file_path)
            if retrieved_age is not None and retrieved_age > args.days:
                reasons.append(f"数据过期 ({retrieved_age} 天)")
            elif retrieved_age is None:
                file_age = get_file_age(file_path)
                if file_age > args.days:
                    reasons.append(f"文件过期 ({file_age} 天)")
        
        if reasons:
            to_delete.append((file_path, reasons))
    
    if not to_delete:
        print("没有需要清理的缓存文件")
        sys.exit(0)
    
    print(f"将清理 {len(to_delete)} 个缓存文件:\n")
    
    total_size = 0
    for file_path, reasons in to_delete:
        size = file_path.stat().st_size
        total_size += size
        print(f"  📁 {file_path.name} ({size/1024:.1f} KB)")
        for reason in reasons:
            print(f"     - {reason}")
    
    print(f"\n总计: {total_size/1024:.1f} KB")
    
    if args.dry_run:
        print("\n[DRY RUN] 未实际删除文件")
    elif not args.force:
        print("\n错误: 非 dry-run 模式需要 --force 参数确认删除")
        print("提示: 使用 --dry-run 预览，或使用 --force 确认删除")
        sys.exit(1)
    else:
        for file_path, _ in to_delete:
            file_path.unlink()
        print(f"\n已删除 {len(to_delete)} 个文件")
    
    sys.exit(0)

if __name__ == '__main__':
    main()
