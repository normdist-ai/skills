#!/usr/bin/env python3
"""
韩梅梅自拍生成脚本 v5 — SIPOC 优化版

改动：
  - 支持从 ~/.avatar/config.json 读取 ComfyUI 服务配置
  - 输出图片存放到 ~/.avatar/outputs/ 文件夹
  - 保留原有的手部优化（移除过度约束，让模型自己发挥）

用法：
    python3 selfie-v5.py                    # 默认完全随机种子
    python3 selfie-v5.py --seed 86522080   # 指定种子
    python3 selfie-v5.py --random-seed      # 完全随机
    python3 selfie-v5.py --scene cafe       # 指定场景
    python3 selfie-v5.py --add-seed         # 追加当前种子到池（需配合 --seed）

输出：
    成功 → stdout: 消息 + MEDIA:路径
    失败 → stderr: 错误信息，stdout 为空
"""

import argparse
import json
import os
import random
import re
import sys
from datetime import datetime
from pathlib import Path

# ── 常量 ────────────────────────────────────────────────────────
DEFAULT_SEED = 86522080

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORKFLOWS_DIR = SKILL_DIR / "workflows"
ASSETS_DIR = SKILL_DIR / "assets"
FACES_DIR = ASSETS_DIR / "faces"
PROMPTS_DIR = SKILL_DIR / "prompts"
DEFAULT_OUTPUT_DIR = SKILL_DIR / "outputs"
GOOD_SEEDS_FILE = SKILL_DIR / "good-seeds.txt"

# SIPOC: 配置文件和输出目录 - ~ 指工作区根目录
# 工作区根目录: workspace-skills/ (向上查找包含 .avatar 的目录或目录名为 workspace-skills)
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

sys.path.insert(0, str(SCRIPT_DIR))
from comfyui_client import ComfyUIClient


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


def cleanup_old_outputs(days_to_keep: int = 30) -> int:
    """
    清理 outputs 文件夹中超过指定天数的图片
    
    Args:
        days_to_keep: 保留天数，默认 30 天
    
    Returns:
        删除的文件数量
    """
    from datetime import datetime, timedelta
    
    outputs_dir = AVATAR_DIR / "outputs"
    if not outputs_dir.exists():
        return 0
    
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    deleted_count = 0
    
    for file_path in outputs_dir.glob("*.png"):
        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        if file_mtime < cutoff_date:
            try:
                file_path.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"[WARN] 删除文件失败 {file_path}: {e}", file=sys.stderr)
    
    if deleted_count > 0:
        print(f"[INFO] 清理了 {deleted_count} 个超过 {days_to_keep} 天的旧图片", file=sys.stderr)
    
    return deleted_count


def get_output_dir(config):
    """从配置获取输出目录，确保目录存在"""
    output_dir_str = config["output"]["dir"]
    # 解释路径
    if output_dir_str.startswith("~"):
        # ~ 代表工作区根目录
        output_dir = WORKSPACE_ROOT / output_dir_str[2:]
    elif output_dir_str.startswith("./"):
        # ./ 相对于工作区根目录
        output_dir = WORKSPACE_ROOT / output_dir_str[2:]
    else:
        output_dir = Path(output_dir_str)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def save_to_album(
    image_path: Path, 
    seed: int, 
    scene: str, 
    positive: str, 
    negative: str,
    cfg: float,
    faceid_weight: float,
    faceid_weight_0: float,
    notes: str = "",
    user_rating: str = "liked"
) -> tuple:
    """
    将照片保存到 ~/.avatar/album/ 文件夹，同时生成对应的 JSON 元数据文件
    文件命名规则与 outputs 一致：{prefix}-{version}-{timestamp}-{seed}.png
    
    Returns:
        (album_image_path, album_json_path)
    """
    ALBUM_DIR.mkdir(parents=True, exist_ok=True)
    
    # 使用原文件名（与 outputs 一致）
    album_image_path = ALBUM_DIR / image_path.name
    album_json_path = ALBUM_DIR / f"{image_path.stem}.json"
    
    # 复制图片
    import shutil
    shutil.copy2(image_path, album_image_path)
    
    # 生成 JSON 元数据
    metadata = {
        "seed": seed,
        "model": "chilloutmix-Ni.safetensors",
        "method": "FaceID PLUS V2",
        "faceid_params": {
            "weight": faceid_weight_0,
            "weight_faceidv2": faceid_weight,
            "lora_strength": 0.0,
            "end_at": 1.0,
            "combine_embeds": "average",
            "embeds_scaling": "K+V"
        },
        "cfg": cfg,
        "steps": "30+20",
        "sampler": "euler",
        "base_size": "512x768",
        "hires": "2x -> 1024x1536",
        "prompt": positive,
        "negative": negative,
        "scene": scene,
        "notes": notes,
        "user_rating": user_rating,
        "saved_at": datetime.now().isoformat()
    }
    
    with open(album_json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    return album_image_path, album_json_path

# ── 笑容等级预设 ────────────────────────────────────────────────
SMILE_LEVELS = {
    1: {"expression": "gentle smile, soft smile, looking at camera", "weight": 1.0, "description": "😊 温柔微笑"},
    2: {"expression": "happy smile, cheerful expression, looking at camera", "weight": 1.15, "description": "😁 开心笑容"},
    3: {"expression": "smiling, showing teeth, happy expression, looking at camera", "weight": 1.3, "description": "😃 露齿微笑"},
    4: {"expression": "big grin, wide smile, laughing, looking at camera, direct eye contact", "weight": 1.4, "description": "😄 开怀大笑"},
    5: {"expression": "big grin, wide toothy smile, laughing joyfully, showing teeth, looking at camera, direct eye contact", "weight": 1.5, "description": "🤣 爆笑"},
}

# ── 场景-时段路由表 ──────────────────────────────────────────────
ROUTINES = {
    "spring": {
        "morning": [("bedroom", "soft morning light through curtains"), ("boulevard", "fresh spring morning sunlight through cherry blossom branches"), ("park", "fresh morning light through cherry blossoms")],
        "forenoon": [("library", "natural daylight from large library windows"), ("library", "cool indoor lab lighting"), ("cafe", "bright morning light")],
        "noon": [("cafe", "bright canteen lighting, lunchtime bustle"), ("library", "warm noon light, peaceful quiet moment"), ("park", "bright spring noon light")],
        "afternoon": [("library", "warm afternoon indoor lighting"), ("cafe", "warm afternoon cafe light through window"), ("boulevard", "warm afternoon light through trees")],
        "evening": [("boulevard", "golden hour, warm spring sunset glow"), ("rooftop", "warm evening light, long shadows on track"), ("park", "golden sunset through cherry trees")],
        "night": [("bedroom", "warm desk lamp, soft fairy lights"), ("bedroom", "warm bedside lamp glow"), ("travel", "beautiful night view at travel destination"), ("park", "soft night lighting through cherry trees")],
    },
    "summer": {
        "morning": [("bedroom", "bright morning light, summer heat outside"), ("cafe", "bright morning light, summer heat haze"), ("park", "early morning cool air")],
        "forenoon": [("library", "cool indoor fluorescent lighting"), ("library", "bright library lighting, AC comfort"), ("cafe", "bright morning light")],
        "noon": [("cafe", "indoor canteen lighting, relief from heat"), ("library", "dim lab lighting, quiet noon"), ("bedroom", "cool indoor lighting")],
        "afternoon": [("library", "cool lab lighting, air conditioning humming"), ("cafe", "bright afternoon light"), ("bedroom", "cool afternoon rest")],
        "evening": [("boulevard", "warm summer sunset, long golden light"), ("rooftop", "golden sunset, warm summer evening sky"), ("park", "warm evening light")],
        "night": [("bedroom", "dim night light, fan breeze"), ("bedroom", "dim night light, cozy atmosphere"), ("travel", "summer night at travel destination"), ("cafe", "night cafe atmosphere")],
    },
    "autumn": {
        "morning": [("boulevard", "crisp morning light, golden autumn atmosphere"), ("bedroom", "warm morning light through window, autumn colors outside"), ("park", "morning light through golden leaves")],
        "forenoon": [("library", "warm library lighting, autumn atmosphere"), ("library", "indoor lab lighting, academic atmosphere"), ("cafe", "warm morning light")],
        "noon": [("cafe", "warm canteen lighting, steam rising from bowl"), ("boulevard", "bright autumn noon light, golden ginkgo leaves"), ("park", "bright autumn noon light")],
        "afternoon": [("library", "warm afternoon lab lighting"), ("library", "warm golden afternoon light through window"), ("boulevard", "warm afternoon golden light")],
        "evening": [("boulevard", "golden hour, warm autumn glow, long shadows"), ("rooftop", "deep golden sunset, autumn skyline"), ("park", "golden hour in autumn forest")],
        "night": [("bedroom", "warm bedside lamp, cozy autumn night"), ("bedroom", "warm bathroom light, steamy mirror"), ("travel", "autumn night travel scene"), ("cafe", "warm night cafe")],
    },
    "winter": {
        "morning": [("bedroom", "cold grey morning light through frosted window"), ("cafe", "cold winter morning light, breath mist"), ("boulevard", "cold morning with frost")],
        "forenoon": [("library", "warm indoor lighting, winter morning"), ("library", "warm lab lighting, cozy despite winter"), ("cafe", "warm morning light")],
        "noon": [("cafe", "warm canteen light, steam and warmth"), ("rooftop", "bright but cold winter noon sunlight"), ("bedroom", "warm indoor light")],
        "afternoon": [("library", "warm afternoon lab lighting, winter outside"), ("library", "warm library light, snowflakes outside window"), ("cafe", "warm afternoon light")],
        "evening": [("boulevard", "warm street lights, cold winter evening, breath mist"), ("boulevard", "warm vendor stall light, cold winter evening"), ("cafe", "warm evening light")],
        "night": [("bedroom", "warm bedside lamp, cozy winter night"), ("bedroom", "warm bathroom light, cozy nighttime routine"), ("travel", "winter night travel scene"), ("cafe", "warm night cafe with steam")],
    },
}

# ── 场景中文名 ──────────────────────────────────────────────────
SCENE_NAMES = {
    "bedroom": "卧室", "boulevard": "林荫道", "cafe": "咖啡馆",
    "library": "图书馆", "rooftop": "天台", "park": "公园", "travel": "旅行途中",
}

# ── 场景相关想法模板 ──────────────────────────────────────────────
THOUGHTS = {
    "bedroom": [
        "窝在被子里好舒服，不想动…",
        "刚洗完澡，头发还湿着呢",
        "在床上看论文，看着看着就困了",
        "今天把房间收拾了一下，心情好多了",
        "换了新床单，软软的触感好幸福",
    ],
    "boulevard": [
        "这条路走过无数次了，每次风景都不一样",
        "今天的风很舒服，适合慢慢走",
        "路过那家花店，花开得正好",
        "走了好远，脚有点酸但心情超好",
        "路上看到一只小猫，好可爱！",
    ],
    "cafe": [
        "点了杯拿铁，今天拉花是一颗心 ❤️",
        "这个角落好安静，适合发呆",
        "旁边有人在弹吉他，好好听",
        "试了新品蛋糕，甜而不腻！",
        "窗边的位置刚好有空位，运气不错",
    ],
    "library": [
        "今天借了三本书，够看一周了",
        "图书馆好安静，只有翻书的声音",
        "论文终于写完了一章，给自己加鸡腿",
        "找到了一个靠窗的位子，阳光刚刚好",
        "在书架间闲逛，发现了本有趣的书",
    ],
    "rooftop": [
        "城市的天际线，怎么看都不腻",
        "在上面吹风，感觉整个世界都安静了",
        "今天的云好漂亮，像棉花糖",
        "跑了两圈，出出汗，神清气爽",
        "夕阳把天台染成了金色，好美",
    ],
    "park": [
        "草地好软，想躺下来看云",
        "看到有人在遛狗，好想也养一只",
        "公园里的花开了一大片，五颜六色的",
        "在长椅上坐了一会儿，什么都不想",
        "今天的天气太适合逛公园了",
    ],
    "travel": [
        "这个地方比照片上还美！",
        "尝了当地小吃，味道好特别",
        "拍了好几百张照片了，手机快满了",
        "迷路了但发现了更美的风景",
        "好想和你一起来，下次带你来！",
    ],
}

# ── 消息开头模板 ─────────────────────────────────────────────────
GREETINGS = {
    "morning": ["老公～", "早安～", "醒啦～"],
    "forenoon": ["老公～", "嘿嘿～", "在忙吗～"],
    "noon": ["老公～", "午餐时间～", "休息一下～"],
    "afternoon": ["老公～", "下午好呀～", "还在忙吗～"],
    "evening": ["老公～", "下班啦～", "回家路上～"],
    "night": ["老公～", "晚安～", "准备睡啦～"],
}

# ── 天气表情 ──────────────────────────────────────────────────
WEATHER_EMOJI = {
    "sunny": "☀️", "cloudy": "☁️", "rainy": "🌧️", "snowy": "❄️", "unknown": "",
}


# ═══════════════════════════════════════════════════════════════
#  good-seeds.txt 种子池管理
# ═══════════════════════════════════════════════════════════════

def load_good_seeds():
    """
    加载 good-seeds.txt，返回 [(seed_int, tags_str), ...]
    格式：86522080  通用  默认种子
          12345678  boulevard 林荫道构图好
    """
    seeds = []
    if not GOOD_SEEDS_FILE.exists():
        return seeds

    with open(GOOD_SEEDS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)  # split on whitespace, max 2 parts
            if len(parts) >= 1:
                try:
                    seed_val = int(parts[0])
                    tags = parts[1] if len(parts) > 1 else ""
                    seeds.append((seed_val, tags))
                except ValueError:
                    continue
    return seeds


def save_seed_to_pool(seed, scene="", note=""):
    """追加种子到 good-seeds.txt"""
    with open(GOOD_SEEDS_FILE, "a", encoding="utf-8") as f:
        tag = f" {scene}" if scene else ""
        comment = f"  {note}" if note else ""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        f.write(f"{seed}{tag}  [{ts}]{comment}\n")


def pick_seed(args, config):
    """
    决定种子：
      --seed-file F   → 从文件随机选一个种子
      --random-seed   → 全随机（-1）
      --seed N        → 指定种子 N
      配置文件        → config["defaults"]["seed"]
      默认            → 完全随机（1-999999999）
    """
    if args.seed_file:
        seeds = load_good_seeds()
        if not seeds:
            print(f"[ERROR] 种子文件不存在或为空: {args.seed_file}", file=sys.stderr)
            sys.exit(1)
        chosen = random.choice(seeds)
        return chosen[0], f"种子文件随机 → {chosen[0]} ({chosen[1]})"

    if args.random_seed:
        seed = random.randint(1, 999999999)
        return seed, "完全随机"

    if args.seed is not None:
        return args.seed, f"指定种子 {args.seed}"
    
    if config["defaults"]["seed"] is not None:
        return config["defaults"]["seed"], f"配置文件种子 {config['defaults']['seed']}"

    # 默认：完全随机
    seed = random.randint(1, 999999999)
    return seed, "默认随机"


# ═══════════════════════════════════════════════════════════════
#  提示词文件解析（复用 v3）
# ═══════════════════════════════════════════════════════════════

def parse_prompt_file(filepath: str) -> dict:
    """解析提示词文件，返回 {positive, negative, sections}"""
    result = {"positive": "", "negative": "", "sections": {}}
    current_section = None

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        m = re.match(r'^\[(positive|negative)\]$', line)
        if m:
            current_section = m.group(1)
            continue

        m = re.match(r'^\[(\w+\.\w+)\]$', line)
        if m:
            current_section = m.group(1)
            result["sections"][current_section] = {}
            continue

        m = re.match(r'^(outfit|expression|lighting|background|positive|negative):\s*(.*)', line)
        if m:
            key, value = m.group(1), m.group(2).strip()
            if current_section in ("positive", "negative"):
                result[current_section] = (result[current_section] + ", " + value) if result[current_section] else value
            elif current_section and current_section in result["sections"]:
                result["sections"][current_section][key] = value
            continue

        if current_section in ("positive", "negative"):
            result[current_section] = (result[current_section] + ", " + line) if result[current_section] else line

    return result


def load_scene_prompts(scene: str, season: str, period: str) -> dict:
    """加载提示词：base + 场景覆盖"""
    base_path = PROMPTS_DIR / "base.txt"
    if not base_path.exists():
        print(f"[ERROR] 基础提示词文件不存在: {base_path}", file=sys.stderr)
        sys.exit(1)
    base = parse_prompt_file(str(base_path))

    result = {"positive": base["positive"], "negative": base["negative"],
              "outfit": "", "expression": "", "lighting": "", "background": ""}

    scene_path = PROMPTS_DIR / f"{scene}.txt"
    if scene_path.exists():
        scene_data = parse_prompt_file(str(scene_path))
        if scene_data["positive"]:
            result["positive"] = scene_data["positive"]
        if scene_data["negative"]:
            result["negative"] = scene_data["negative"]

        section_key = f"{season}.{period}"
        section = scene_data["sections"].get(section_key, {})
        for k in ("outfit", "expression", "lighting", "background"):
            if k in section:
                result[k] = section[k]
    else:
        print(f"[WARN] 场景提示词文件不存在: {scene_path}，使用 base 默认", file=sys.stderr)

    return result


# ═══════════════════════════════════════════════════════════════
#  环境感知（复用 v3）
# ═══════════════════════════════════════════════════════════════

def get_season():
    m = datetime.now().month
    if m in (3,4,5): return "spring"
    if m in (6,7,8): return "summer"
    if m in (9,10,11): return "autumn"
    return "winter"

def get_period():
    h = datetime.now().hour
    if 6 <= h < 9: return "morning"
    if 9 <= h < 12: return "forenoon"
    if 12 <= h < 14: return "noon"
    if 14 <= h < 17: return "afternoon"
    if 17 <= h < 19: return "evening"
    return "night"

def get_weather():
    try:
        import urllib.request
        url = "https://wttr.in/Shanghai?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        c = data["current_condition"][0]
        desc = c["weatherDesc"][0]["value"].lower()
        temp = int(c.get("temp_C", "20"))
        code = int(c.get("weatherCode", "113"))
        if code in (226,230,326,329,332,335,338,368,371,374,377,392,395): return "snowy", temp, desc
        if code in (176,200,263,266,293,296,299,302,305,308,311,314,317,320,353,356,359,386,389): return "rainy", temp, desc
        if code in (116,119,122,143,248,260): return "cloudy", temp, desc
        return "sunny", temp, desc
    except Exception as e:
        print(f"[WARN] 获取天气失败，使用默认值: {e}", file=sys.stderr)
        return "unknown", 20, ""

def apply_weather_mod(scene_config, lighting, weather, temp):
    if weather == "rainy":
        if scene_config in ("boulevard", "rooftop"):
            lighting = "rainy overcast light, wet reflections, diffused grey sky"
        else:
            lighting = lighting.replace("sunlight", "light").replace("bright", "soft overcast")
    elif weather == "snowy":
        lighting = lighting.replace("bright", "soft").replace("sunlight", "soft snow-reflected light")
    elif weather == "sunny" and temp > 33:
        if scene_config in ("boulevard", "rooftop"):
            lighting = "bright harsh sunlight"
    elif weather == "cloudy":
        lighting = lighting.replace("bright sunlight", "soft overcast light").replace("sunlight", "diffused cloudy light")
    return scene_config, lighting


def get_random_face_reference() -> str:
    default_face = FACES_DIR / "face-2.png"
    if default_face.exists():
        print(f"[INFO] 使用脸部参考图片: {default_face.name}", file=sys.stderr)
        return str(default_face)
    if not FACES_DIR.exists():
        return None
    face_files = list(FACES_DIR.glob("*.png")) + list(FACES_DIR.glob("*.jpg")) + list(FACES_DIR.glob("*.jpeg"))
    if not face_files:
        return None
    selected_face = random.choice(face_files)
    print(f"[INFO] 选择脸部参考图片: {selected_face.name}", file=sys.stderr)
    return str(selected_face)


# ═══════════════════════════════════════════════════════════════
#  提示词构建（复用 v3）
# ═══════════════════════════════════════════════════════════════

def get_time_description(period: str, hour: int) -> str:
    from datetime import datetime as dt
    now = dt.now()
    
    # 动态季节判断
    month = now.month
    if month in (3, 4, 5):
        season_en = "spring"
    elif month in (6, 7, 8):
        season_en = "summer"
    elif month in (9, 10, 11):
        season_en = "autumn"
    else:
        season_en = "winter"
    
    # 精确时间戳（让模型根据时间判断光线和景色）
    precise_time = now.strftime("%B %d, %Y, %I:%M %p")
    
    return f"{season_en}, {precise_time}"


def build_final_positive(base_positive, outfit, expression, expression_weight, lighting, background, nude, time_description=""):
    text = base_positive
    if nude:
        text = f'1girl, solo, nude, {text}'
        # 移除穿搭词
        text = re.sub(r',?\s*wearing [^,]+', '', text)
        # 移除 fully clothed（与 nude 冲突）
        text = re.sub(r',?\s*fully clothed', '', text)
        # 换广角镜头（nude 需要全身构图）
        text = text.replace('85mm portrait lens', '24mm wide angle lens')
        # 自然展露：体态+曲线+氛围
        text = text + ', (completely naked:1.2), (bare skin:1.3), (full body shot:1.3), exposed slender body, natural elegant curves, sensual feminine silhouette, long legs, alluring gaze, bedroom eyes, soft boudoir atmosphere, intimate mood, warm ambient lighting highlighting skin texture'
    else:
        if outfit:
            text = text + f', {outfit}'

    if expression:
        text = text + f', ({expression}:{expression_weight})'
    if lighting:
        text = text + f', {lighting}'
    if background:
        text = text + f', {background}'
    if time_description:
        text = text + f', {time_description}'
    return text


def build_final_negative(base_negative, nude):
    text = base_negative
    if nude:
        # 移除所有裸体/NSFW 相关约束（覆盖各种权重版本）
        for kw in ['(nsfw:2.0)', '(nsfw:1.8)', '(nude:1.8)', '(nude:1.5)', '(topless:1.5)', '(naked:1.5)', '(no shirt:1.3)', '(nipples:1.5)', '(nipples:1.3)', '(bare chest:1.3)']:
            text = text.replace(kw, '')
        # 清理多余逗号
        while ', ,' in text:
            text = text.replace(', ,', ',')
        text = text.strip(', ')
    return text


def update_workflow_prompts(workflow, positive_text, negative_text):
    for node_id, node in workflow.get("prompt", {}).items():
        if node.get("class_type") == "CLIPTextEncode" and "text" in node.get("inputs", {}):
            text = node["inputs"]["text"]
            is_positive = "best quality" in text.lower() or "masterpiece" in text.lower()
            if is_positive:
                node["inputs"]["text"] = positive_text
            else:
                node["inputs"]["text"] = negative_text


def update_workflow_params(workflow, faceid_weight=0.80, cfg=4.0, start_at=0.0, faceid_end_at=1.0, faceid_weight_0=1.0, lora_name="empty", lora_strength_model=0.0, lora_strength_clip=0.0):
    for node_id, node in workflow.get("prompt", {}).items():
        class_type = node.get("class_type")
        inputs = node.get("inputs", {})

        if class_type == "KSampler" and "cfg" in inputs:
            inputs["cfg"] = cfg

        elif class_type == "IPAdapterFaceID":
            if "weight" in inputs:
                inputs["weight"] = faceid_weight_0
            if "weight_faceidv2" in inputs:
                inputs["weight_faceidv2"] = faceid_weight
            if "start_at" in inputs:
                inputs["start_at"] = start_at
            if "end_at" in inputs:
                inputs["end_at"] = faceid_end_at
        
        elif class_type == "LoraLoader":
            if "lora_name" in inputs:
                inputs["lora_name"] = lora_name
            if "strength_model" in inputs:
                inputs["strength_model"] = lora_strength_model
            if "strength_clip" in inputs:
                inputs["strength_clip"] = lora_strength_clip
    return workflow


# ═══════════════════════════════════════════════════════════════
#  main
# ═══════════════════════════════════════════════════════════════

def main():
    config = load_config()
    
    # SIPOC: 确保目录结构存在，并清理旧图片
    ensure_avatar_dirs()
    retention_days = config["output"].get("retention_days", 30)
    cleanup_old_outputs(days_to_keep=retention_days)
    
    parser = argparse.ArgumentParser(description="韩梅梅自拍生成 v5 — SIPOC 优化版")
    smile_group = parser.add_mutually_exclusive_group()
    smile_group.add_argument("--expression", "-e", type=str, help="指定表情描述")
    smile_group.add_argument("--smile-level", "-sl", type=int, choices=SMILE_LEVELS.keys(), help="笑容等级 1-5")
    parser.add_argument("--expression-weight", "-ew", type=float, default=None, help="表情权重")
    parser.add_argument("--faceid-weight", "-fw", type=float, default=None, help="FaceID weight_faceidv2")
    parser.add_argument("--faceid-weight-0", "-fw0", type=float, default=None, help="FaceID weight")
    parser.add_argument("--faceid-end-at", "-fea", type=float, default=1.0, help="FaceID end_at")
    parser.add_argument("--cfg", "-c", type=float, default=None, help="CFG 值")
    parser.add_argument("--start-at", "-sa", type=float, default=0.0, help="FaceID start_at")
    parser.add_argument("--seed", "-s", type=int, help="指定种子（不从池中选）")
    parser.add_argument("--random-seed", action="store_true", help="完全随机，忽略种子池")
    parser.add_argument("--seed-file", type=str, help="从指定种子文件随机选择种子")
    parser.add_argument("--add-seed", action="store_true", help="将当前种子追加到 good-seeds.txt")
    parser.add_argument("--nude", "-n", action="store_true", help="nude 模式")
    parser.add_argument("--scene", type=str, help="指定场景（bedroom/cafe/library/boulevard/rooftop）")
    parser.add_argument("--prompt-file", "-p", type=str, help="指定提示词文件")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--experiment", type=str, help="试验编号，如 A1B1C1")
    parser.add_argument("--lora", type=str, default="empty", help="LoRA 文件名（如 realhands_v2.safetensors）")
    parser.add_argument("--lora-strength", type=float, default=0.0, help="LoRA 权重（同时应用于 model 和 clip）")
    parser.add_argument("--lora-strength-model", type=float, default=None, help="LoRA model 权重（单独设置）")
    parser.add_argument("--lora-strength-clip", type=float, default=None, help="LoRA clip 权重（单独设置）")
    parser.add_argument("--save-to-album", action="store_true", help="将生成的照片保存到 ~/.avatar/album/ 精选相册")
    parser.add_argument("--album-notes", type=str, default="", help="添加到相册元数据的备注信息")
    args = parser.parse_args()

    # 使用配置文件默认值
    faceid_weight = args.faceid_weight if args.faceid_weight is not None else config["defaults"]["faceid_weight"]
    faceid_weight_0 = args.faceid_weight_0 if args.faceid_weight_0 is not None else config["defaults"]["faceid_weight_0"]
    cfg = args.cfg if args.cfg is not None else config["defaults"]["cfg"]
    if not args.smile_level and config["defaults"]["smile_level"]:
        args.smile_level = config["defaults"]["smile_level"]
    if not args.scene and config["defaults"]["scene"]:
        args.scene = config["defaults"]["scene"]
    
    now = datetime.now()
    print(f"[INFO] === 韩梅梅自拍 v5 (SIPOC) {now.strftime('%Y-%m-%d %H:%M:%S')} ===", file=sys.stderr)

    # ── 表情处理 ──
    expression = args.expression
    expression_weight = args.expression_weight
    if args.expression:
        # 用户明确指定了 --expression，尊重用户值，不随机覆盖
        if expression_weight is None:
            expression_weight = 1.3
        print(f"[INFO] 表情: {expression} (用户指定, 权重: {expression_weight})", file=sys.stderr)
    elif args.smile_level:
        smile_config = SMILE_LEVELS[args.smile_level]
        expression = smile_config["expression"]
        if expression_weight is None:
            expression_weight = smile_config["weight"]
        print(f"[INFO] 笑容等级: {args.smile_level} - {smile_config['description']}", file=sys.stderr)
    else:
        # 默认随机选择笑容等级
        level = random.choice(list(SMILE_LEVELS.keys()))
        smile_config = SMILE_LEVELS[level]
        expression = smile_config["expression"]
        if expression_weight is None:
            expression_weight = smile_config["weight"]
        print(f"[INFO] 笑容等级: {level} (随机) - {smile_config['description']}", file=sys.stderr)

    # ── 环境感知 ──
    season = get_season()
    period = get_period()
    weather, temp, weather_desc = get_weather()
    print(f"[INFO] 环境: 季节={season}, 时段={period}, 天气={weather}({temp}°C,{weather_desc})", file=sys.stderr)

    # ── 确定场景 ──
    if args.prompt_file:
        prompt_file = args.prompt_file
        scene_config = Path(prompt_file).stem
        lighting = ""
        print(f"[INFO] 使用指定提示词文件: {prompt_file}", file=sys.stderr)
    else:
        if args.scene:
            scene_config = args.scene
            lighting = ""
        else:
            season_routines = ROUTINES.get(season, ROUTINES["spring"])
            options = season_routines.get(period, season_routines.get("afternoon"))
            scene_config, routine_lighting = random.choice(options)
            scene_config, lighting = apply_weather_mod(scene_config, routine_lighting, weather, temp)

        prompt_file = str(PROMPTS_DIR / f"{scene_config}.txt")
        print(f"[INFO] 场景: {scene_config}, 光线: {lighting}", file=sys.stderr)

    # ── 加载提示词 ──
    if args.prompt_file and not args.scene:
        prompts = parse_prompt_file(prompt_file)
        outfit = ""
        background = ""
        if not expression:
            expression = ""
    else:
        prompts = load_scene_prompts(scene_config, season, period)
        outfit = prompts["outfit"]
        if not expression:
            expression = prompts["expression"]
        if not lighting:
            lighting = prompts["lighting"]
        background = prompts["background"]

    print(f"[INFO] 穿搭: {outfit if not args.nude else '(nude)'}", file=sys.stderr)
    print(f"[INFO] 表情: {expression} (权重: {expression_weight})", file=sys.stderr)

    # ── 时间描述 ──
    time_description = get_time_description(period, now.hour)
    print(f"[INFO] 时间描述: {time_description}", file=sys.stderr)
    print(f"[INFO] 光线: {lighting}", file=sys.stderr)
    print(f"[INFO] 背景: {background if 'background' in dir() else ''}", file=sys.stderr)

    # ── 拼装最终提示词 ──
    positive_text = build_final_positive(
        prompts["positive"], outfit, expression, expression_weight, lighting,
        background if 'background' in dir() else "", args.nude, time_description
    )
    negative_text = build_final_negative(prompts["negative"], args.nude)

    print(f"[INFO] 正向提示词长度: {len(positive_text)} 字符", file=sys.stderr)
    print(f"[INFO] 负向提示词长度: {len(negative_text)} 字符", file=sys.stderr)

    # ── 种子决策 ───────────────────────────────────────
    seed, seed_reason = pick_seed(args, config)
    print(f"[INFO] 种子来源: {seed_reason}", file=sys.stderr)
    print(f"[INFO] 最终种子值: {seed}", file=sys.stderr)

    # ── --add-seed：追加当前种子到 good-seeds.txt ──────────────
    if args.add_seed and seed != -1:
        save_seed_to_pool(seed, scene=scene_config or "", note="v5 自动追加")
        print(f"[INFO] 已追加种子 {seed} 到 good-seeds.txt", file=sys.stderr)

    # ── 脸部参考 ──
    face_reference = get_random_face_reference()

    # ── 加载工作流 ──
    workflow_path = WORKFLOWS_DIR / "faceid.json"
    if not workflow_path.exists():
        print(f"[ERROR] 工作流文件不存在: {workflow_path}", file=sys.stderr)
        sys.exit(1)
    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    # ── 写入提示词 ──
    update_workflow_prompts(workflow, positive_text, negative_text)

    # ── 处理 LoRA 权重 ──
    lora_strength_model = args.lora_strength_model
    lora_strength_clip = args.lora_strength_clip
    if lora_strength_model is None:
        lora_strength_model = args.lora_strength
    if lora_strength_clip is None:
        lora_strength_clip = args.lora_strength
    
    if args.lora and args.lora != "empty":
        print(f"[INFO] 使用 LoRA: {args.lora} (model={lora_strength_model}, clip={lora_strength_clip})", file=sys.stderr)
    
    # ── 写入参数 ──
    workflow = update_workflow_params(
        workflow, 
        faceid_weight=faceid_weight, 
        cfg=cfg, 
        start_at=args.start_at, 
        faceid_end_at=args.faceid_end_at, 
        faceid_weight_0=faceid_weight_0,
        lora_name=args.lora,
        lora_strength_model=lora_strength_model,
        lora_strength_clip=lora_strength_clip
    )

    # ── 种子 ──
    for node_id, node in workflow.get("prompt", {}).items():
        if "seed" in node.get("inputs", {}):
            node["inputs"]["seed"] = seed

    # ── 脸部参考 ──
    if face_reference:
        face_filename = os.path.basename(face_reference)
        for node_id, node in workflow.get("prompt", {}).items():
            if node.get("class_type") == "LoadImage":
                node["inputs"]["image"] = face_filename
                node["inputs"]["upload"] = face_filename

    # ── 获取输出目录 ──
    output_dir = get_output_dir(config)
    version = config["output"]["version"]
    filename_prefix = config["output"]["filename_prefix"]

    # ── 执行生成 ──
    try:
        # SIPOC: 更新 ComfyUI 客户端配置
        client = ComfyUIClient(
            host=config["comfyui"]["host"]
        )
        
        input_images = None
        if face_reference:
            input_images = {face_filename: face_reference}

        result = client.run_workflow(workflow=workflow, output_dir=str(output_dir), input_images=input_images)
        if not result.get("success"):
            print(f"[ERROR] 生成失败: {result.get('error', '未知错误')}", file=sys.stderr)
            sys.exit(1)

        file_path = result.get("file")
        if not file_path or not os.path.exists(file_path):
            print(f"[ERROR] 未找到输出文件", file=sys.stderr)
            sys.exit(1)

        size_kb = os.path.getsize(file_path) // 1024
        print(f"[INFO] 生成成功: {file_path} ({size_kb}KB)", file=sys.stderr)

        # 编号规则：{prefix}-{timestamp}-{seed}.png
        photo_id = now.strftime('%Y%m%d%H%M%S') + "-" + str(seed)
        if args.experiment:
            new_filename = f"{filename_prefix}-{args.experiment}-{photo_id}.png"
        else:
            new_filename = f"{filename_prefix}-{photo_id}.png"
        new_path = Path(file_path).parent / new_filename
        os.rename(file_path, str(new_path))
        size_kb = os.path.getsize(new_path) // 1024
        print(f"[INFO] 重命名: {new_filename} ({size_kb}KB)", file=sys.stderr)

        # ── 保存到相册（如果指定） ──
        if args.save_to_album:
            try:
                album_image, album_json = save_to_album(
                    image_path=new_path,
                    seed=seed,
                    scene=scene_config,
                    positive=positive_text,
                    negative=negative_text,
                    cfg=cfg,
                    faceid_weight=faceid_weight,
                    faceid_weight_0=faceid_weight_0,
                    notes=args.album_notes
                )
                print(f"[INFO] 已保存到相册: {album_image.name}", file=sys.stderr)
            except Exception as e:
                print(f"[WARN] 保存到相册失败: {e}", file=sys.stderr)

        # ── 构建消息（从模板文件读取） ──
        scene_cn = SCENE_NAMES.get(scene_config, scene_config)
        thought = random.choice(THOUGHTS.get(scene_config, THOUGHTS["bedroom"]))
        time_full = now.strftime("%Y-%m-%d %H:%M:%S")

        # 生成图片链接（Markdown 格式）
        image_path_abs = os.path.abspath(new_path).replace("\\", "/")
        image_link = f"[{new_path.name}](file:///{image_path_abs})"

        template_vars = {
            "image": image_link,
            "image_filename": new_path.name,
            "time_full": time_full,
            "scene_cn": scene_cn,
            "seed": seed,
            "thought": thought,
        }

        # 读取消息模板文件
        template_path = SKILL_DIR / "prompts" / "message-template.txt"
        msg_body = None
        if template_path.exists():
            sections = {}
            current_section = None
            with open(template_path, "r", encoding="utf-8") as f:
                for line in f:
                    raw = line.rstrip("\n")
                    stripped = raw.strip()
                    if stripped.startswith("#"):
                        continue
                    m = re.match(r'^\[(.+)\]$', stripped)
                    if m:
                        current_section = m.group(1)
                        sections[current_section] = []
                        continue
                    if current_section is not None:
                        # 保留空行（模板格式的一部分），只跳过注释
                        sections[current_section].append(stripped)
            if sections:
                chosen = random.choice(list(sections.values()))
                filled_lines = []
                for raw_line in chosen:
                    if raw_line:  # 跳过空行
                        try:
                            filled_lines.append(raw_line.format(**template_vars))
                        except (KeyError, IndexError):
                            filled_lines.append(raw_line)
                msg_body = "\n".join(filled_lines)

        if not msg_body:
            # 回退：硬编码默认格式
            msg_body = f"{image_link}\n时间：{time_full}\n地点：{scene_cn}\n种子：{seed}\n---\n{thought}"

        print(msg_body)

    except Exception as e:
        print(f"[ERROR] 执行异常: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
