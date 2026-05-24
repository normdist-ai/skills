#!/usr/bin/env python3
"""
韩梅梅技能 - 公共模块

提供跨脚本共享的路径常量和工具函数：
  - 工作区根目录查找
  - 配置文件加载
  - 目录结构初始化
  - 场景中文名映射
"""

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent


def find_workspace_root() -> Path:
    """查找工作区根目录（.avatar 文件夹所在位置）"""
    current = SKILL_DIR
    # 向上查找，最多查 5 级
    for _ in range(5):
        # 优先检查目录名是否为 workspace-skills
        if current.name == "workspace-skills":
            return current
        # 然后检查 .avatar 目录是否存在
        if (current / ".avatar").exists():
            return current
        if current.parent == current:  # 到达根目录了
            break
        current = current.parent
    # 默认回退到技能目录的上级目录
    return SKILL_DIR.parent.parent.parent  # skills -> .trae -> workspace-skills


WORKSPACE_ROOT = find_workspace_root()
AVATAR_DIR = WORKSPACE_ROOT / ".avatar"
CONFIG_FILE = AVATAR_DIR / "config.json"
ALBUM_DIR = AVATAR_DIR / "album"


def load_config():
    """加载配置文件 ~/.avatar/config.json"""
    default_config = {
        "comfyui": {
            "host": "http://10.28.9.6:8188",
            "client_id": "hanmeimei-avatar",
            "timeout": 600
        },
        "output": {
            "dir": "~/.avatar/outputs",
            "filename_prefix": "HMM",
            "version": "v5",
            "retention_days": 30
        },
        "defaults": {
            "faceid_weight": 0.80,
            "faceid_weight_0": 1.0,
            "cfg": 4.0,
            "seed": None,
            "scene": None,
            "smile_level": None
        }
    }

    if not CONFIG_FILE.exists():
        return default_config

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        # 合并默认配置
        for key in default_config:
            if key not in config:
                config[key] = default_config[key]
            else:
                for subkey in default_config[key]:
                    if subkey not in config[key]:
                        config[key][subkey] = default_config[key][subkey]
        return config
    except Exception as e:
        print(f"[WARN] 加载配置文件失败，使用默认配置: {e}", file=sys.stderr)
        return default_config


def ensure_avatar_dirs():
    """
    确保 ~/.avatar/ 文件夹结构存在
    首次运行时自动创建：
      - ~/.avatar/
      - ~/.avatar/outputs/
      - ~/.avatar/album/
      - ~/.avatar/profile/
    """
    dirs_to_create = [
        AVATAR_DIR,
        AVATAR_DIR / "outputs",
        AVATAR_DIR / "album",
        AVATAR_DIR / "profile",
    ]

    for dir_path in dirs_to_create:
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"[INFO] 创建目录: {dir_path}", file=sys.stderr)


# ── 场景中文名（selfie-v5.py 和 scheduler.py 共用） ──
SCENE_NAMES = {
    "bedroom": "卧室", "boulevard": "林荫道", "cafe": "咖啡馆",
    "library": "图书馆", "rooftop": "天台", "park": "公园", "travel": "旅行途中",
}