#!/usr/bin/env python3
# /// script
# dependencies = [
#   "jsonschema>=4.0",
# ]
# ///
"""
缓存数据验证脚本
验证 .llm-benchmark/cache/ 目录中的缓存数据是否符合 JSON Schema

Usage: scripts/validate_cache.py [OPTIONS]

Validate LLM Benchmark cache data against JSON Schema.

Options:
  --cache-dir PATH   Cache directory path (default: .llm-benchmark/cache)
  --verbose, -v      Show detailed output
  --help             Show this help message

Examples:
  scripts/validate_cache.py
  scripts/validate_cache.py --cache-dir ./cache --verbose

Exit codes:
  0 - All cache files passed validation
  1 - Some cache files failed validation
  2 - Script execution error
"""

import json
import sys
from pathlib import Path
from argparse import ArgumentParser
import jsonschema

CACHE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["cache_version", "model", "provider", "benchmarks", "source", "retrieved_at"],
    "properties": {
        "cache_version": {"type": "string"},
        "model": {"type": "string"},
        "provider": {"type": "string"},
        "benchmarks": {"type": "object"},
        "source": {"type": "string"},
        "retrieved_at": {"type": "string"}
    }
}

def validate_cache_file(file_path: Path, verbose: bool = False) -> tuple[bool, str]:
    """验证单个缓存文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        jsonschema.validate(instance=data, schema=CACHE_SCHEMA)
        
        if verbose:
            print(f"  ✅ {file_path.name}: 验证通过")
            print(f"     模型: {data.get('model', 'N/A')}")
            print(f"     厂商: {data.get('provider', 'N/A')}")
            print(f"     获取日期: {data.get('retrieved_at', 'N/A')}")
        
        return True, ""
    
    except json.JSONDecodeError as e:
        error_msg = f"JSON 解析错误: {e}"
        if verbose:
            print(f"  ❌ {file_path.name}: {error_msg}")
        return False, error_msg
    
    except jsonschema.ValidationError as e:
        error_msg = f"Schema 验证错误: {e.message}"
        if verbose:
            print(f"  ❌ {file_path.name}: {error_msg}")
        return False, error_msg
    
    except Exception as e:
        error_msg = f"未知错误: {e}"
        if verbose:
            print(f"  ❌ {file_path.name}: {error_msg}")
        return False, error_msg

def main():
    parser = ArgumentParser(description='验证 LLM Benchmark 缓存数据')
    parser.add_argument('--cache-dir', type=str, default='.llm-benchmark/cache',
                        help='缓存目录路径')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='显示详细输出')
    args = parser.parse_args()
    
    cache_dir = Path(args.cache_dir)
    
    if not cache_dir.exists():
        print(f"错误: 缓存目录不存在: {cache_dir}")
        sys.exit(2)
    
    cache_files = list(cache_dir.glob('*.json'))
    
    if not cache_files:
        print(f"警告: 缓存目录中没有 JSON 文件: {cache_dir}")
        sys.exit(0)
    
    print(f"验证缓存目录: {cache_dir}")
    print(f"发现 {len(cache_files)} 个缓存文件\n")
    
    passed = 0
    failed = 0
    errors = []
    
    for file_path in sorted(cache_files):
        success, error = validate_cache_file(file_path, args.verbose)
        if success:
            passed += 1
        else:
            failed += 1
            errors.append((file_path.name, error))
    
    print(f"\n{'='*50}")
    print(f"验证结果: 通过 {passed}/{len(cache_files)}")
    
    if failed > 0:
        print(f"\n失败的文件:")
        for name, error in errors:
            print(f"  - {name}: {error}")
        sys.exit(1)
    else:
        print("所有缓存文件验证通过!")
        sys.exit(0)

if __name__ == '__main__':
    main()
