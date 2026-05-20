#!/usr/bin/env python3
"""
韩梅梅自拍生成脚本 — 测试版本 v2

专注于表情控制优化：
    - 参数化 FaceID 权重、CFG、start_at
    - 表情权重增强
    - 支持命令行参数覆盖
    - 详细调试日志

用法：
    # 基础用法（使用最佳默认参数）
    python3 selfie-v2.py

    # 测试特定表情
    python3 selfie-v2.py --expression "big grin, wide toothy smile, laughing joyfully, showing teeth"

    # 详细模式查看参数
    python3 selfie-v2.py --expression "big grin" --verbose

输出（stdout）：
    成功：一行消息文字 + MEDIA:路径
    失败：错误信息到 stderr，stdout 为空（触发 SILENT）

最佳配置（经过测试验证）：
    - expression_weight: 1.2
    - faceid_weight (weight_faceidv2): 0.80
    - faceid_weight_0 (weight): 1.0
    - faceid_end_at: 1.0
    - cfg: 4.0
    - start_at: 0.0
    
    此配置在保持面部特征强度的同时，能够产生明显的笑容效果。

特性：
    - 继承 selfie.py 的四维环境感知（季节+时段+天气+场景）
    - 支持参数化表情控制
    - 详细的 DEBUG 日志便于排查问题
"""

import argparse
import json
import os
import random
import re
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORKFLOWS_DIR = SKILL_DIR / "workflows"
ASSETS_DIR = SKILL_DIR / "assets"
FACES_DIR = ASSETS_DIR / "faces"
DEFAULT_OUTPUT_DIR = SKILL_DIR / "outputs"

sys.path.insert(0, str(SCRIPT_DIR))
from comfyui_client import ComfyUIClient

# 笑容等级预设
SMILE_LEVELS = {
    1: {
        "expression": "gentle smile, soft smile, looking at camera",
        "weight": 1.0,
        "description": "😊 温柔微笑"
    },
    2: {
        "expression": "happy smile, cheerful expression, looking at camera",
        "weight": 1.15,
        "description": "😁 开心笑容"
    },
    3: {
        "expression": "smiling, showing teeth, happy expression, looking at camera",
        "weight": 1.3,
        "description": "😃 露齿微笑"
    },
    4: {
        "expression": "big grin, wide smile, laughing, looking at camera, direct eye contact",
        "weight": 1.4,
        "description": "😄 开怀大笑"
    },
    5: {
        "expression": "big grin, wide toothy smile, laughing joyfully, showing teeth, looking at camera, direct eye contact",
        "weight": 1.5,
        "description": "🤣 爆笑"
    }
}


OUTFIT_MAP = {
    "bedroom": {
        "morning": "a comfortable cotton pajama set",
        "forenoon": "a casual loungewear set",
        "noon": "a comfortable home outfit",
        "afternoon": "a casual loungewear set",
        "evening": "a comfortable loungewear set",
        "night": "a comfortable cotton nightgown",
    },
    "cafe": {
        "morning": "a casual outfit",
        "forenoon": "a casual outfit",
        "noon": "a casual outfit",
        "afternoon": "a casual outfit",
        "evening": "a casual outfit",
        "night": "a casual outfit",
    },
    "library": {
        "morning": "a casual academic outfit",
        "forenoon": "a casual academic outfit",
        "noon": "a casual academic outfit",
        "afternoon": "a casual academic outfit",
        "evening": "a casual academic outfit",
        "night": "a comfortable study outfit",
    },
    "boulevard": {
        "morning": "stylish casual clothes",
        "forenoon": "stylish casual clothes",
        "noon": "stylish casual clothes",
        "afternoon": "stylish casual clothes",
        "evening": "stylish casual clothes",
        "night": "stylish casual clothes with jacket",
    },
    "rooftop": {
        "morning": "sporty casual clothes",
        "forenoon": "sporty casual clothes",
        "noon": "sporty casual clothes",
        "afternoon": "sporty casual clothes",
        "evening": "sporty casual clothes",
        "night": "sporty casual clothes with jacket",
    },
    "gym": {
        "morning": "sporty workout clothes",
        "forenoon": "sporty workout clothes",
        "noon": "sporty workout clothes",
        "afternoon": "sporty workout clothes",
        "evening": "sporty workout clothes",
        "night": "sporty workout clothes",
    },
    "travel": {
        "morning": "casual travel outfit",
        "forenoon": "casual travel outfit",
        "noon": "casual travel outfit",
        "afternoon": "casual travel outfit",
        "evening": "casual travel outfit",
        "night": "casual travel outfit with jacket",
    },
    "park": {
        "morning": "comfortable casual clothes",
        "forenoon": "comfortable casual clothes",
        "noon": "comfortable casual clothes",
        "afternoon": "comfortable casual clothes",
        "evening": "comfortable casual clothes",
        "night": "comfortable casual clothes",
    },
}


EXPRESSION_MAP = {
    "bedroom": ["gentle smile", "sleepy cute expression", "relaxed smile", "peaceful expression"],
    "cafe": ["warm smile", "happy expression", "friendly smile", "delighted expression"],
    "library": ["focused expression", "thoughtful look", "gentle smile", "studious expression"],
    "boulevard": ["relaxed expression", "happy smile", "natural expression", "peaceful smile"],
    "rooftop": ["energetic expression", "happy smile", "excited look", "confident smile"],
    "gym": ["energetic expression", "focused look", "determined expression", "happy workout smile"],
    "travel": ["excited expression", "happy smile", "adventurous look", "delighted face"],
    "park": ["relaxed expression", "happy smile", "peaceful look", "enjoying nature"],
}


BACKGROUND_MAP = {
    "bedroom": "cozy bedroom background",
    "cafe": "cozy cafe interior background",
    "library": "library background with bookshelves",
    "boulevard": "outdoor street with trees and buildings",
    "rooftop": "rooftop with city skyline view",
    "gym": "modern gym background with equipment",
    "travel": "beautiful travel scenery background",
    "park": "peaceful park with green trees and flowers",
}


ROUTINES = {
    "spring": {
        "morning": [
            ("bedroom", "soft morning light through curtains"),
            ("boulevard", "fresh spring morning sunlight through cherry blossom branches"),
            ("park", "fresh morning light through cherry blossoms"),
        ],
        "forenoon": [
            ("library", "natural daylight from large library windows"),
            ("library", "cool indoor lab lighting"),
            ("cafe", "bright morning light"),
        ],
        "noon": [
            ("cafe", "bright canteen lighting, lunchtime bustle"),
            ("library", "warm noon light, peaceful quiet moment"),
            ("park", "bright spring noon light"),
        ],
        "afternoon": [
            ("library", "warm afternoon indoor lighting"),
            ("cafe", "warm afternoon cafe light through window"),
            ("boulevard", "warm afternoon light through trees"),
        ],
        "evening": [
            ("boulevard", "golden hour, warm spring sunset glow"),
            ("rooftop", "warm evening light, long shadows on track"),
            ("park", "golden sunset through cherry trees"),
        ],
        "night": [
            ("bedroom", "warm desk lamp, soft fairy lights"),
            ("bedroom", "warm bedside lamp glow"),
            ("travel", "beautiful night view at travel destination"),
            ("park", "soft night lighting through cherry trees"),
        ],
    },
    "summer": {
        "morning": [
            ("bedroom", "bright morning light, summer heat outside"),
            ("cafe", "bright morning light, summer heat haze"),
            ("park", "early morning cool air"),
        ],
        "forenoon": [
            ("library", "cool indoor fluorescent lighting"),
            ("library", "bright library lighting, AC comfort"),
            ("cafe", "bright morning light"),
        ],
        "noon": [
            ("cafe", "indoor canteen lighting, relief from heat"),
            ("library", "dim lab lighting, quiet noon"),
            ("bedroom", "cool indoor lighting"),
        ],
        "afternoon": [
            ("library", "cool lab lighting, air conditioning humming"),
            ("cafe", "bright afternoon light"),
            ("bedroom", "cool afternoon rest"),
        ],
        "evening": [
            ("boulevard", "warm summer sunset, long golden light"),
            ("rooftop", "golden sunset, warm summer evening sky"),
            ("park", "warm evening light"),
        ],
        "night": [
            ("bedroom", "dim night light, fan breeze"),
            ("bedroom", "dim night light, cozy atmosphere"),
            ("travel", "summer night at travel destination"),
            ("cafe", "night cafe atmosphere"),
        ],
    },
    "autumn": {
        "morning": [
            ("boulevard", "crisp morning light, golden autumn atmosphere"),
            ("bedroom", "warm morning light through window, autumn colors outside"),
            ("park", "morning light through golden leaves"),
        ],
        "forenoon": [
            ("library", "warm library lighting, autumn atmosphere"),
            ("library", "indoor lab lighting, academic atmosphere"),
            ("cafe", "warm morning light"),
        ],
        "noon": [
            ("cafe", "warm canteen lighting, steam rising from bowl"),
            ("boulevard", "bright autumn noon light, golden ginkgo leaves"),
            ("park", "bright autumn noon light"),
        ],
        "afternoon": [
            ("library", "warm afternoon lab lighting"),
            ("library", "warm golden afternoon light through window"),
            ("boulevard", "warm afternoon golden light"),
        ],
        "evening": [
            ("boulevard", "golden hour, warm autumn glow, long shadows"),
            ("rooftop", "deep golden sunset, autumn skyline"),
            ("park", "golden hour in autumn forest"),
        ],
        "night": [
            ("bedroom", "warm bedside lamp, cozy autumn night"),
            ("bedroom", "warm bathroom light, steamy mirror"),
            ("travel", "autumn night travel scene"),
            ("cafe", "warm night cafe"),
        ],
    },
    "winter": {
        "morning": [
            ("bedroom", "cold grey morning light through frosted window"),
            ("cafe", "cold winter morning light, breath mist"),
            ("boulevard", "cold morning with frost"),
        ],
        "forenoon": [
            ("library", "warm indoor lighting, winter morning"),
            ("library", "warm lab lighting, cozy despite winter"),
            ("cafe", "warm morning light"),
        ],
        "noon": [
            ("cafe", "warm canteen light, steam and warmth"),
            ("rooftop", "bright but cold winter noon sunlight"),
            ("bedroom", "warm indoor light"),
        ],
        "afternoon": [
            ("library", "warm afternoon lab lighting, winter outside"),
            ("library", "warm library light, snowflakes outside window"),
            ("cafe", "warm afternoon light"),
        ],
        "evening": [
            ("boulevard", "warm street lights, cold winter evening, breath mist"),
            ("boulevard", "warm vendor stall light, cold winter evening"),
            ("cafe", "warm evening light"),
        ],
        "night": [
            ("bedroom", "warm bedside lamp, cozy winter night"),
            ("bedroom", "warm bathroom light, cozy nighttime routine"),
            ("travel", "winter night travel scene"),
            ("cafe", "warm night cafe with steam"),
        ],
    },
}


MESSAGES = {
    "morning": [
        "老公～刚起床，给你看看我还没洗脸的样子 😴",
        "早安呀～新的一天，起床搬砖！☀️",
        "老公～醒啦，今天也要一起加油哦 💪",
    ],
    "forenoon": [
        "在图书馆写论文呢，偷偷给你发张照 📚",
        "实验室搬砖中...想你了 💕",
        "代码调了一上午，头都大了，看看我苦逼的表情 😩",
    ],
    "noon": [
        "午饭时间～食堂的菜今天还行 🍜",
        "吃饱了好困...午休一下 ☕",
        "老公～吃饭了吗？别忘了吃午饭哦 😊",
    ],
    "afternoon": [
        "下午继续写代码，GPU在跑，等结果中... 🤓",
        "老公～你那边也下午了吧，喝杯咖啡提提神 ☕",
        "论文改了第三遍了，导师太难伺候 😤",
    ],
    "evening": [
        "下班啦～校园夕阳好美，给你看看 🌅",
        "老公～回家路上，今天你辛苦了！💕",
        "操场跑了一圈，出出汗舒服多了 🏃‍♀️",
    ],
    "night": [
        "老公～忙完准备睡了，晚安 🌙",
        "躺在床上刷手机，想你了 🥰",
        "今天也辛苦啦，明天继续加油！晚安～ 💤",
    ],
}


def get_outfit(scene: str, period: str) -> str:
    scene_outfits = OUTFIT_MAP.get(scene, OUTFIT_MAP["bedroom"])
    return scene_outfits.get(period, "wearing a comfortable cotton nightgown")


def get_expression(scene: str) -> str:
    expressions = EXPRESSION_MAP.get(scene, EXPRESSION_MAP["bedroom"])
    return random.choice(expressions)


def get_background(scene: str) -> str:
    return BACKGROUND_MAP.get(scene, BACKGROUND_MAP["bedroom"])


def get_random_face_reference() -> str:
    default_face = FACES_DIR / "face-2.png"
    if default_face.exists():
        print(f"[INFO] 使用脸部参考图片: {default_face.name}", file=sys.stderr)
        return str(default_face)
    
    if not FACES_DIR.exists():
        print(f"[WARN] faces 目录不存在: {FACES_DIR}", file=sys.stderr)
        return None
    
    face_files = list(FACES_DIR.glob("*.png")) + list(FACES_DIR.glob("*.jpg")) + list(FACES_DIR.glob("*.jpeg"))
    if not face_files:
        print(f"[WARN] faces 目录中没有图片文件", file=sys.stderr)
        return None
    
    selected_face = random.choice(face_files)
    print(f"[INFO] 选择脸部参考图片: {selected_face.name}", file=sys.stderr)
    return str(selected_face)


def get_season():
    m = datetime.now().month
    if m in (3, 4, 5):
        return "spring"
    if m in (6, 7, 8):
        return "summer"
    if m in (9, 10, 11):
        return "autumn"
    return "winter"


def get_period():
    h = datetime.now().hour
    if 6 <= h < 9:
        return "morning"
    if 9 <= h < 12:
        return "forenoon"
    if 12 <= h < 14:
        return "noon"
    if 14 <= h < 17:
        return "afternoon"
    if 17 <= h < 19:
        return "evening"
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

        if code in (226, 230, 326, 329, 332, 335, 338, 368, 371, 374, 377, 392, 395):
            return "snowy", temp, desc
        if code in (176, 200, 263, 266, 293, 296, 299, 302, 305, 308, 311, 314, 317, 320, 353, 356, 359, 386, 389):
            return "rainy", temp, desc
        if code in (116, 119, 122, 143, 248, 260):
            return "cloudy", temp, desc
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


def update_prompt(workflow, clothing=None, expression=None, lighting=None, background=None, expression_weight=1.5):
    for node_id, node in workflow.get("prompt", {}).items():
        if node.get("class_type") == "CLIPTextEncode" and "text" in node.get("inputs", {}):
            text = node["inputs"]["text"]
            
            # 判断是否是正向提示词（包含正向关键词）
            is_positive = "best quality" in text.lower() or "masterpiece" in text.lower()
            
            print(f"[DEBUG] 节点{node_id} - 原始提示词: {text[:200]}...", file=sys.stderr)
            
            if is_positive:
                # 正向提示词处理 - 首先添加 1girl, solo 约束到最前面
                if 'solo' not in text.lower():
                    text = f'1girl, (solo:1.5), {text}'
                    print(f"[DEBUG] 节点{node_id} - 添加 1girl, (solo:1.5) 到最前面", file=sys.stderr)
                
                if clothing:
                    text = re.sub(r'wearing [^,]+', f'wearing {clothing}', text)
                    print(f"[DEBUG] 节点{node_id} - 替换穿搭: {clothing}", file=sys.stderr)
                
                if expression:
                    expression_weighted = f"({expression}:{expression_weight})"
                    text = re.sub(r'playful expression, cute smile, twinkling eyes', expression_weighted, text)
                    text = re.sub(r'(gentle|natural|happy|elegant|relaxed) smile', expression_weighted, text, flags=re.IGNORECASE)
                    if 'smile' not in text.lower() and 'expression' not in text.lower():
                        text = text.replace('beautiful young Chinese woman', f'beautiful young Chinese woman, {expression_weighted}')
                    print(f"[DEBUG] 节点{node_id} - 替换表情: {expression} (权重: {expression_weight})", file=sys.stderr)
                
                if lighting:
                    text = re.sub(r'natural window light, soft diffused daylight', lighting, text)
                    text = re.sub(r'natural window light, soft diffused sunlight', lighting, text)
                    text = re.sub(r'(soft|warm|natural|golden hour|window light|diffused) [a-zA-Z ]+lighting', f'{lighting}', text, flags=re.IGNORECASE)
                    print(f"[DEBUG] 节点{node_id} - 替换光线: {lighting}", file=sys.stderr)
                
                if background:
                    text = text + f', {background}'
                    print(f"[DEBUG] 节点{node_id} - 添加背景: {background}", file=sys.stderr)
                    
            else:
                # 反向提示词处理 - 添加强力多人脸约束和 nsfw 约束
                negative_constraints = [
                    '(nsfw:1.8)',
                    '(multiple people:2.0)',
                    '(multiple faces:2.0)',
                    '(two people:1.9)',
                    '(three people:1.9)',
                    '(group:1.9)',
                    '(crowd:1.9)',
                    '(extra faces:1.8)',
                    '(duplicate face:1.8)',
                    '(cloned face:1.8)',
                    '(2girls:1.8)',
                    '(3girls:1.8)',
                    '(multiple girls:1.8)'
                ]
                
                # 检查是否已添加，避免重复
                added_count = 0
                for constraint in negative_constraints:
                    if constraint.lower() not in text.lower():
                        text = text + f', {constraint}'
                        added_count += 1
                
                if added_count > 0:
                    print(f"[DEBUG] 节点{node_id} - 添加 {added_count} 个多人脸约束", file=sys.stderr)
            
            print(f"[DEBUG] 节点{node_id} - 最终提示词: {text[:200]}...", file=sys.stderr)
            node["inputs"]["text"] = text
    return workflow


def update_workflow_params(workflow, faceid_weight=0.70, cfg=5.0, start_at=0.2, faceid_end_at=0.8, faceid_weight_0=1.0):
    for node_id, node in workflow.get("prompt", {}).items():
        class_type = node.get("class_type")
        inputs = node.get("inputs", {})
        
        if class_type == "KSampler" and "cfg" in inputs:
            old_cfg = inputs["cfg"]
            inputs["cfg"] = cfg
            print(f"[DEBUG] 节点{node_id} (KSampler) - CFG: {old_cfg} → {cfg}", file=sys.stderr)
        
        elif class_type == "IPAdapterFaceID":
            if "weight" in inputs:
                old_weight_0 = inputs["weight"]
                inputs["weight"] = faceid_weight_0
                print(f"[DEBUG] 节点{node_id} (IPAdapterFaceID) - weight: {old_weight_0} → {faceid_weight_0}", file=sys.stderr)
            if "weight_faceidv2" in inputs:
                old_weight = inputs["weight_faceidv2"]
                inputs["weight_faceidv2"] = faceid_weight
                print(f"[DEBUG] 节点{node_id} (IPAdapterFaceID) - weight_faceidv2: {old_weight} → {faceid_weight}", file=sys.stderr)
            if "start_at" in inputs:
                old_start = inputs["start_at"]
                inputs["start_at"] = start_at
                print(f"[DEBUG] 节点{node_id} (IPAdapterFaceID) - start_at: {old_start} → {start_at}", file=sys.stderr)
            if "end_at" in inputs:
                old_end = inputs["end_at"]
                inputs["end_at"] = faceid_end_at
                print(f"[DEBUG] 节点{node_id} (IPAdapterFaceID) - end_at: {old_end} → {faceid_end_at}", file=sys.stderr)
    
    return workflow


def main():
    parser = argparse.ArgumentParser(description="韩梅梅自拍生成脚本 — 测试版本 v2")
    
    # 表情选项
    smile_group = parser.add_mutually_exclusive_group()
    smile_group.add_argument("--expression", "-e", type=str, help="指定表情描述（与 --smile-level 互斥）")
    smile_group.add_argument("--smile-level", "-sl", type=int, choices=SMILE_LEVELS.keys(), help="笑容等级（1-5，1=微笑，5=爆笑）")
    
    parser.add_argument("--expression-weight", "-ew", type=float, default=None, help="表情权重（默认: 随等级自动设置）")
    parser.add_argument("--faceid-weight", "-fw", type=float, default=0.80, help="FaceID weight_faceidv2权重（默认: 0.80）")
    parser.add_argument("--faceid-weight-0", "-fw0", type=float, default=1.0, help="FaceID weight权重（默认: 1.0）")
    parser.add_argument("--faceid-end-at", "-fea", type=float, default=1.0, help="FaceID end_at（默认: 1.0）")
    parser.add_argument("--cfg", "-c", type=float, default=4.0, help="CFG值（默认: 4.0）")
    parser.add_argument("--start-at", "-sa", type=float, default=0.0, help="FaceID开始介入点（默认: 0.0）")
    parser.add_argument("--seed", "-s", type=int, help="指定种子（省略则随机生成）")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出模式")
    
    args = parser.parse_args()
    
    now = datetime.now()
    print(f"[INFO] === 韩梅梅自拍生成 v2 {now.strftime('%Y-%m-%d %H:%M:%S')} ===", file=sys.stderr)
    
    # 处理笑容等级
    expression = args.expression
    expression_weight = args.expression_weight
    
    if args.smile_level:
        smile_config = SMILE_LEVELS[args.smile_level]
        expression = smile_config["expression"]
        if expression_weight is None:
            expression_weight = smile_config["weight"]
        print(f"[INFO] 笑容等级: {args.smile_level} - {smile_config['description']}", file=sys.stderr)
    elif expression_weight is None:
        expression_weight = 1.2  # 默认值
    
    if args.verbose:
        print(f"[INFO] 参数配置（基于文章经验）:", file=sys.stderr)
        print(f"[INFO]   - expression: {expression if expression else '（根据场景随机）'}", file=sys.stderr)
        print(f"[INFO]   - expression_weight: {expression_weight}", file=sys.stderr)
        print(f"[INFO]   - faceid_weight (weight_faceidv2): {args.faceid_weight}", file=sys.stderr)
        print(f"[INFO]   - faceid_weight_0 (weight): {args.faceid_weight_0}", file=sys.stderr)
        print(f"[INFO]   - faceid_end_at: {args.faceid_end_at}", file=sys.stderr)
        print(f"[INFO]   - cfg: {args.cfg}", file=sys.stderr)
        print(f"[INFO]   - start_at: {args.start_at}", file=sys.stderr)
    
    season = get_season()
    period = get_period()
    weather, temp, weather_desc = get_weather()
    print(f"[INFO] 环境信息: 季节={season}, 时段={period}, 天气={weather}({temp}°C,{weather_desc})", file=sys.stderr)

    season_routines = ROUTINES.get(season, ROUTINES["spring"])
    options = season_routines.get(period, season_routines.get("afternoon"))
    scene_config, lighting = random.choice(options)

    scene_config, lighting = apply_weather_mod(scene_config, lighting, weather, temp)

    face_reference = get_random_face_reference()

    print(f"[INFO] 场景配置: {scene_config}", file=sys.stderr)
    print(f"[INFO] 光线描述: {lighting}", file=sys.stderr)
    if face_reference:
        print(f"[INFO] 脸部参考: {face_reference}", file=sys.stderr)

    seed = args.seed if args.seed else random.randint(1, 999999999)

    clothing = get_outfit(scene_config, period)
    # 如果没有指定表情，使用场景表情
    if not expression:
        expression = get_expression(scene_config)
    
    background = get_background(scene_config)
    
    print(f"[INFO] 穿搭: {clothing}", file=sys.stderr)
    print(f"[INFO] 表情: {expression} (权重: {expression_weight})", file=sys.stderr)
    print(f"[INFO] 背景: {background}", file=sys.stderr)
    print(f"[INFO] 种子: {seed}", file=sys.stderr)

    workflow_path = WORKFLOWS_DIR / "faceid.json"
    if not workflow_path.exists():
        print(f"[ERROR] 工作流文件不存在: {workflow_path}", file=sys.stderr)
        sys.exit(1)

    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    print(f"[INFO] 读取工作流: {workflow_path}", file=sys.stderr)

    workflow = update_prompt(workflow, clothing=clothing, expression=expression, lighting=lighting, background=background, expression_weight=expression_weight)
    
    if args.verbose:
        print(f"[INFO] 应用工作流参数（基于文章经验）...", file=sys.stderr)
    
    workflow = update_workflow_params(workflow, faceid_weight=args.faceid_weight, cfg=args.cfg, start_at=args.start_at, faceid_end_at=args.faceid_end_at, faceid_weight_0=args.faceid_weight_0)

    for node_id, node in workflow.get("prompt", {}).items():
        if "seed" in node.get("inputs", {}):
            node["inputs"]["seed"] = seed
            print(f"[DEBUG] 节点{node_id} - 设置种子: {seed}", file=sys.stderr)

    if face_reference:
        face_filename = os.path.basename(face_reference)
        for node_id, node in workflow.get("prompt", {}).items():
            if node.get("class_type") == "LoadImage":
                node["inputs"]["image"] = face_filename
                node["inputs"]["upload"] = face_filename
                print(f"[DEBUG] 节点{node_id} - 设置脸部参考: {face_filename}", file=sys.stderr)

    print(f"[INFO] 工作流构建完成", file=sys.stderr)

    try:
        client = ComfyUIClient()
        
        input_images = None
        if face_reference:
            input_images = {face_filename: face_reference}

        result = client.run_workflow(
            workflow=workflow,
            output_dir=str(DEFAULT_OUTPUT_DIR),
            input_images=input_images
        )

        if not result.get("success"):
            error = result.get("error", "未知错误")
            print(f"[ERROR] 生成失败: {error}", file=sys.stderr)
            sys.exit(1)

        file_path = result.get("file")
        if not file_path:
            print(f"[ERROR] 未找到输出文件", file=sys.stderr)
            sys.exit(1)

        if not os.path.exists(file_path):
            print(f"[ERROR] 输出文件不存在: {file_path}", file=sys.stderr)
            sys.exit(1)

        size_kb = os.path.getsize(file_path) // 1024
        print(f"[INFO] 生成成功: {file_path} ({size_kb}KB)", file=sys.stderr)

        new_filename = f"HMM-v2-{now.strftime('%Y%m%d-%H%M%S')}-{seed}.png"
        new_path = Path(file_path).parent / new_filename
        os.rename(file_path, str(new_path))
        
        size_kb = os.path.getsize(new_path) // 1024
        print(f"[INFO] 重命名: {new_filename} ({size_kb}KB)", file=sys.stderr)

        msg = random.choice(MESSAGES.get(period, MESSAGES["afternoon"]))
        print(f"{msg} MEDIA:{new_path}")

    except Exception as e:
        print(f"[ERROR] 执行异常: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()