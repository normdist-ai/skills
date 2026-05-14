#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""
缓存统计脚本
显示缓存数据的统计信息

Usage: scripts/stats_cache.py [OPTIONS]

Show statistics about LLM Benchmark cache data.

Options:
  --cache-dir PATH   Cache directory path (default: .llm-benchmark/cache)
  --help             Show this help message

Examples:
  scripts/stats_cache.py
  scripts/stats_cache.py --cache-dir ./cache

Exit codes:
  0 - Success
  2 - Script execution error
"""

import json
import sys
from pathlib import Path
from argparse import ArgumentParser
from datetime import datetime
from collections import defaultdict

def main():
    parser = ArgumentParser(description='显示 LLM Benchmark 缓存统计')
    parser.add_argument('--cache-dir', type=str, default='.llm-benchmark/cache',
                        help='缓存目录路径')
    args = parser.parse_args()
    
    cache_dir = Path(args.cache_dir)
    
    if not cache_dir.exists():
        print(f"错误: 缓存目录不存在: {cache_dir}")
        sys.exit(2)
    
    cache_files = list(cache_dir.glob('*.json'))
    
    if not cache_files:
        print(f"缓存目录中没有文件: {cache_dir}")
        sys.exit(0)
    
    print(f"{'='*60}")
    print(f"LLM Benchmark 缓存统计")
    print(f"{'='*60}")
    print(f"缓存目录: {cache_dir}")
    print(f"缓存文件数: {len(cache_files)}")
    
    total_size = sum(f.stat().st_size for f in cache_files)
    print(f"总大小: {total_size/1024:.1f} KB")
    print()
    
    providers = defaultdict(list)
    benchmarks_available = defaultdict(int)
    dates = []
    
    for file_path in cache_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            model = data.get('model', 'Unknown')
            provider = data.get('provider', 'Unknown')
            providers[provider].append(model)
            
            benchmarks = data.get('benchmarks', {})
            for category, scores in benchmarks.items():
                if isinstance(scores, dict):
                    for bench, score in scores.items():
                        if score is not None:
                            benchmarks_available[f"{category}/{bench}"] += 1
            
            retrieved_at = data.get('retrieved_at')
            if retrieved_at:
                dates.append(retrieved_at)
        
        except Exception as e:
            print(f"警告: 无法读取 {file_path.name}: {e}")
    
    print(f"\n{'─'*60}")
    print("按厂商分类:")
    print(f"{'─'*60}")
    for provider, models in sorted(providers.items()):
        print(f"  {provider}: {len(models)} 个模型")
        for model in models:
            print(f"    - {model}")
    
    print(f"\n{'─'*60}")
    print("评测基准覆盖:")
    print(f"{'─'*60}")
    sorted_benchmarks = sorted(benchmarks_available.items(), key=lambda x: -x[1])
    for bench, count in sorted_benchmarks[:15]:
        print(f"  {bench}: {count} 个模型")
    
    if len(sorted_benchmarks) > 15:
        print(f"  ... 还有 {len(sorted_benchmarks) - 15} 个评测基准")
    
    if dates:
        print(f"\n{'─'*60}")
        print("数据时间范围:")
        print(f"{'─'*60}")
        dates.sort()
        print(f"  最早: {dates[0]}")
        print(f"  最新: {dates[-1]}")
    
    print(f"\n{'='*60}")

if __name__ == '__main__':
    main()
