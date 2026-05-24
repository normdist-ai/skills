#!/usr/bin/env python3
"""
韩梅梅技能 - 远程文件删除工具

通过 SSH 删除 ComfyUI 服务器上的缓存图片。

使用方法：
    # 删除单个文件
    python deletefile.py --filename HMM-FaceID_00250_.png
    
    # 批量清理超过保留期的文件
    python deletefile.py --cleanup --retention-days 7
    
    # 列出匹配的文件（不删除）
    python deletefile.py --list --pattern "HMM-*.png"

配置：
    在 .avatar/config.json 中配置 SSH：
    {
      "ssh": {
        "enabled": true,
        "host": "10.28.9.6",
        "user": "your_username",
        "output_dir": "/path/to/ComfyUI/output"
      }
    }
"""

import sys
import json
import argparse
import shlex
from pathlib import Path
import subprocess

# 添加 scripts 目录到路径
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from common import load_config


def delete_file(filename: str, ssh_config: dict) -> dict:
    """
    通过 SSH 删除单个文件
    
    Args:
        filename: 文件名
        ssh_config: SSH 配置
    
    Returns:
        {"success": bool, "error": str}
    """
    if not ssh_config.get("enabled"):
        return {"success": False, "error": "SSH 未启用"}
    
    try:
        host = ssh_config["host"]
        user = ssh_config["user"]
        output_dir = ssh_config["output_dir"]
        remote_file = f"{output_dir}/{filename}"
        
        cmd = [
            "ssh",
            f"{user}@{host}",
            f"rm -f {shlex.quote(remote_file)}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"[INFO] 删除成功: {remote_file}")
            return {"success": True}
        else:
            return {"success": False, "error": result.stderr.strip()}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_files(pattern: str, ssh_config: dict) -> list:
    """
    通过 SSH 列出匹配的文件
    
    Args:
        pattern: 文件模式（如 "HMM-*.png"）
        ssh_config: SSH 配置
    
    Returns:
        文件列表
    """
    if not ssh_config.get("enabled"):
        print("[WARN] SSH 未启用", file=sys.stderr)
        return []
    
    try:
        host = ssh_config["host"]
        user = ssh_config["user"]
        output_dir = ssh_config["output_dir"]
        
        cmd = [
            "ssh",
            f"{user}@{host}",
            f"ls -lh {shlex.quote(output_dir)}/{shlex.quote(pattern)}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return result.stdout.strip().split("\n")
        else:
            print(f"[ERROR] 列表失败: {result.stderr.strip()}", file=sys.stderr)
            return []
            
    except Exception as e:
        print(f"[ERROR] 列表失败: {e}", file=sys.stderr)
        return []


def cleanup_files(pattern: str, retention_days: int, ssh_config: dict) -> dict:
    """
    通过 SSH 批量清理超过保留期的文件
    
    Args:
        pattern: 文件模式
        retention_days: 保留天数
        ssh_config: SSH 配置
    
    Returns:
        {"success": bool, "deleted": int, "error": str}
    """
    if not ssh_config.get("enabled"):
        return {"success": False, "deleted": 0, "error": "SSH 未启用"}
    
    try:
        host = ssh_config["host"]
        user = ssh_config["user"]
        output_dir = ssh_config["output_dir"]
        
        cmd = [
            "ssh",
            f"{user}@{host}",
            f"find {shlex.quote(output_dir)} -name {shlex.quote(pattern)} -mtime +{retention_days} -delete -print"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            deleted_files = [line.strip() for line in result.stdout.split("\n") if line.strip()]
            deleted_count = len(deleted_files)
            return {"success": True, "deleted": deleted_count}
        else:
            return {"success": False, "deleted": 0, "error": result.stderr.strip()}
            
    except Exception as e:
        return {"success": False, "deleted": 0, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="远程文件删除工具")
    parser.add_argument("--filename", help="要删除的文件名")
    parser.add_argument("--cleanup", action="store_true", help="批量清理旧文件")
    parser.add_argument("--list", action="store_true", help="列出匹配的文件")
    parser.add_argument("--pattern", default="HMM-*.png", help="文件匹配模式")
    parser.add_argument("--retention-days", type=int, default=7, help="保留天数")
    
    args = parser.parse_args()
    
    config = load_config()
    ssh_config = config.get("ssh", {})
    
    if not ssh_config.get("enabled"):
        print("[WARN] SSH 未启用", file=sys.stderr)
        print("[INFO] 请在 config.json 中配置 SSH", file=sys.stderr)
        sys.exit(1)
    
    if args.filename:
        print(f"[INFO] 删除文件: {args.filename}")
        result = delete_file(args.filename, ssh_config)
        if result["success"]:
            print("[INFO] 删除成功")
            sys.exit(0)
        else:
            print(f"[ERROR] 删除失败: {result['error']}", file=sys.stderr)
            sys.exit(1)
    
    elif args.cleanup:
        print(f"[INFO] 批量清理: {args.pattern}, 保留 {args.retention_days} 天")
        result = cleanup_files(args.pattern, args.retention_days, ssh_config)
        if result["success"]:
            print(f"[INFO] 清理完成，删除了 {result['deleted']} 个文件")
            sys.exit(0)
        else:
            print(f"[ERROR] 清理失败: {result['error']}", file=sys.stderr)
            sys.exit(1)
    
    elif args.list:
        print(f"[INFO] 列出文件: {args.pattern}")
        files = list_files(args.pattern, ssh_config)
        if files:
            print(f"[INFO] 找到 {len(files)} 个文件：")
            for f in files:
                print(f"  {f}")
        else:
            print("[INFO] 未找到匹配的文件")
        sys.exit(0)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()