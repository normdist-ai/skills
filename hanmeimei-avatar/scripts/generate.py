#!/usr/bin/env python3
"""韩梅梅写真生成引擎 - 单张出图

纯 requests + 标准库，不依赖 hermes_tools。
支持从 JSON 配置加载场景参数。

用法:
    from generate import generate

    result = generate(
        scene="in a cozy bedroom",
        clothing="white silk nightgown",
        expression="gentle smile",
    )

命令行:
    python generate.py --scene "in a cozy bedroom" --clothing "white silk nightgown"
"""

import json
import os
import random
import sys
import time
from datetime import datetime

import requests


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)


def _load_default_config():
    path = os.path.join(SKILL_DIR, "references", "scenes", "_default.json")
    with open(path, "r") as f:
        return json.load(f)


def _scan_face_files():
    faces_dir = os.path.join(SKILL_DIR, "assets", "faces")
    files = sorted(
        [
            f
            for f in os.listdir(faces_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]
    )
    return [
        (os.path.join(faces_dir, f), f"face_ref_{i+1}.png")
        for i, f in enumerate(files)
    ]


FACE_FILES = _scan_face_files()


def _merge_config(scene_config=None):
    config = _load_default_config()
    config["skill_dir"] = SKILL_DIR

    if scene_config:
        for key in ("scene", "clothing", "expression", "lighting", "composition"):
            if key in scene_config and scene_config[key]:
                config[key] = scene_config[key]

        faceid_overrides = scene_config.get("faceid_overrides", {})
        for k, v in faceid_overrides.items():
            if v is not None and k in config.get("faceid", {}):
                config["faceid"][k] = v

        face_detailer_overrides = scene_config.get("face_detailer_overrides", {})
        for k, v in face_detailer_overrides.items():
            if v is not None and k in config.get("face_detailer", {}):
                config["face_detailer"][k] = v

        neg_extras = scene_config.get("neg_extras", [])
        if neg_extras:
            config["_neg_extras"] = neg_extras

    return config


def _detect_expression_flags(expression):
    smile = "smile" in expression.lower() or "微笑" in expression
    eyes_closed = "closed" in expression.lower() or "闭眼" in expression
    return smile, eyes_closed

def _get_faceid_params(config, smile):
    faceid = dict(config.get("faceid", {}))
    if smile:
        # With FaceDetailer, we can lower FaceID slightly to allow expression
        faceid["weight"] = 0.8
        faceid["weight_faceidv2"] = 0.55
        faceid["end_at"] = 0.8
    return faceid


def _build_prompts(config, clothing, expression, composition):
    comp = config["compositions"].get(composition, config["compositions"]["waist up"])

    lighting = config.get("lighting", "soft warm indoor lighting")

    # 空穿搭时用默认
    if not clothing:
        clothing = config.get("default_clothing", "")

    prompt = config["prompt_template"].format(
        scene=config.get("scene", ""),
        clothing=clothing,
        expression=expression,
        lighting=lighting,
        composition_kw=comp["kw"],
    )

    neg_parts = [config["neg_prompt_base"]]

    smile, eyes_closed = _detect_expression_flags(expression)
    if eyes_closed:
        neg_parts.append("(open eyes:1.5)")
    if "t-shirt" in clothing.lower() or "T恤" in clothing:
        neg_parts.append(
            "(camisole:1.3),(tank top:1.3),(sleeveless:1.3),(crop top:1.2),(sports bra:1.2)"
        )
    if composition in ("full body", "full body sit"):
        neg_parts.append(
            "large breasts,oversized breasts,implants,latex,rubber,plastic clothing"
        )
        neg_parts.append(
            "extra fingers,deformed hands,mutated hands,bad hands,poorly drawn hands"
        )
        neg_parts.append(
            "(((extra arms and legs))),missing fingers,extra digit,lowers,bad hands"
        )

    neg_extras = config.get("_neg_extras", [])
    if neg_extras:
        neg_parts.extend(neg_extras)

    neg_prompt = ",".join(neg_parts)
    return prompt, neg_prompt, comp


def _upload_faces(comfy_url):
    for local_path, remote_name in FACE_FILES:
        with open(local_path, "rb") as f:
            requests.post(
                f"{comfy_url}/upload/image",
                files={"image": (remote_name, f, "image/png")},
                data={"overwrite": "true"},
                timeout=30,
            )


def _free_memory(comfy_url):
    requests.post(
        f"{comfy_url}/free", json={"unload_models": True}, timeout=10
    )
    time.sleep(2)


def _build_workflow(
    prompt, neg_prompt, seed, comp, faceid_params, sampler_config, hires_config, model,
    face_detailer_config=None, no_faceid=False,
):
    wf = {}
    fd_enabled = face_detailer_config and face_detailer_config.get("enabled", False)

    wf["1"] = {
        "class_type": "CheckpointLoaderSimple",
        "inputs": {"ckpt_name": model},
    }

    if no_faceid:
        model_source = ["1", 0]
        n_pos, n_neg = "2", "3"
        n_empty, n_base = "4", "5"
        n_upscale, n_refine = "6", "7"
        n_vae = "8"
        if fd_enabled:
            n_save, n_clipseg, n_detailer = "11", "9", "10"
        else:
            n_save = "9"
    else:
        wf["2"] = {"class_type": "LoadImage", "inputs": {"image": "face_ref_1.png"}}
        wf["3"] = {"class_type": "LoadImage", "inputs": {"image": "face_ref_2.png"}}
        wf["4"] = {"class_type": "LoadImage", "inputs": {"image": "face_ref_3.png"}}

        wf["5"] = {
            "class_type": "ImageBatch",
            "inputs": {"image1": ["2", 0], "image2": ["3", 0]},
        }
        wf["6"] = {
            "class_type": "ImageBatch",
            "inputs": {"image1": ["5", 0], "image2": ["4", 0]},
        }

        wf["7"] = {
            "class_type": "IPAdapterUnifiedLoaderFaceID",
            "inputs": {
                "model": ["1", 0],
                "preset": faceid_params.get("preset", "FACEID PLUS V2"),
                "lora_strength": faceid_params.get("lora_strength", 0.8),
                "provider": "CUDA",
            },
        }

        wf["8"] = {
            "class_type": "IPAdapterFaceID",
            "inputs": {
                "model": ["7", 0],
                "ipadapter": ["7", 1],
                "image": ["6", 0],
                "weight": faceid_params["weight"],
                "weight_faceidv2": faceid_params["weight_faceidv2"],
                "weight_type": "linear",
                "combine_embeds": faceid_params.get("combine_embeds", "average"),
                "start_at": 0.0,
                "end_at": faceid_params["end_at"],
                "embeds_scaling": faceid_params.get("embeds_scaling", "K+V"),
            },
        }
        model_source = ["8", 0]
        n_pos, n_neg = "9", "10"
        n_empty, n_base = "11", "12"
        n_upscale, n_refine = "13", "14"
        n_vae = "15"
        if fd_enabled:
            n_save, n_clipseg, n_detailer = "16", "17", "18"
        else:
            n_save = "16"

    wf[n_pos] = {
        "class_type": "CLIPTextEncode",
        "inputs": {"text": prompt, "clip": ["1", 1]},
    }
    wf[n_neg] = {
        "class_type": "CLIPTextEncode",
        "inputs": {"text": neg_prompt, "clip": ["1", 1]},
    }

    wf[n_empty] = {
        "class_type": "EmptyLatentImage",
        "inputs": {"width": comp["w"], "height": comp["h"], "batch_size": 1},
    }

    wf[n_base] = {
        "class_type": "KSampler",
        "inputs": {
            "seed": seed,
            "steps": sampler_config["base_steps"],
            "cfg": sampler_config["cfg"],
            "sampler_name": sampler_config["sampler_name"],
            "scheduler": sampler_config["scheduler"],
            "denoise": 1.0,
            "model": model_source,
            "positive": [n_pos, 0],
            "negative": [n_neg, 0],
            "latent_image": [n_empty, 0],
        },
    }

    wf[n_upscale] = {
        "class_type": "LatentUpscale",
        "inputs": {
            "upscale_method": hires_config["method"],
            "width": comp["w"] * hires_config["scale"],
            "height": comp["h"] * hires_config["scale"],
            "crop": "disabled",
            "samples": [n_base, 0],
        },
    }

    wf[n_refine] = {
        "class_type": "KSampler",
        "inputs": {
            "seed": seed + 1,
            "steps": sampler_config["refine_steps"],
            "cfg": sampler_config["cfg"],
            "sampler_name": sampler_config["sampler_name"],
            "scheduler": sampler_config["scheduler"],
            "denoise": sampler_config["refine_denoise"],
            "model": model_source,
            "positive": [n_pos, 0],
            "negative": [n_neg, 0],
            "latent_image": [n_upscale, 0],
        },
    }

    wf[n_vae] = {
        "class_type": "VAEDecode",
        "inputs": {"samples": [n_refine, 0], "vae": ["1", 2]},
    }

    if fd_enabled:
        wf[n_clipseg] = {
            "class_type": "CLIPSegDetectorProvider",
            "inputs": {
                "text": "face",
                "blur": 7.0,
                "threshold": 0.4,
                "dilation_factor": 4,
            },
        }

        fd = face_detailer_config
        wf[n_detailer] = {
            "class_type": "FaceDetailer",
            "inputs": {
                "image": [n_vae, 0],
                "model": model_source,
                "clip": ["1", 1],
                "vae": ["1", 2],
                "guide_size": fd["guide_size"],
                "guide_size_for": True,
                "max_size": fd["max_size"],
                "seed": seed + 2,
                "steps": fd["steps"],
                "cfg": fd["cfg"],
                "sampler_name": fd["sampler_name"],
                "scheduler": fd["scheduler"],
                "denoise": fd["denoise"],
                "feather": fd["feather"],
                "noise_mask": fd["noise_mask"],
                "force_inpaint": fd["force_inpaint"],
                "bbox_threshold": fd["bbox_threshold"],
                "bbox_dilation": fd.get("bbox_dilation", 10),
                "bbox_crop_factor": 3.0,
                "sam_detection_hint": "center-1",
                "sam_dilation": 0,
                "sam_threshold": 0.93,
                "sam_bbox_expansion": 0,
                "sam_mask_hint_threshold": 0.7,
                "sam_mask_hint_use_negative": "False",
                "drop_size": 10,
                "bbox_detector": [n_clipseg, 0],
                "wildcard": "",
                "cycle": 1,
                "positive": [n_pos, 0],
                "negative": [n_neg, 0],
            },
        }

    wf[n_save] = {
        "class_type": "SaveImage",
        "inputs": {
            "filename_prefix": "hm_gen",
            "images": [n_detailer, 0] if fd_enabled else [n_vae, 0],
        },
    }

    return wf, n_save


def _submit_and_wait(workflow, output_node, comfy_url, timeout=360):
    resp = requests.post(
        f"{comfy_url}/prompt",
        json={"prompt": workflow},
        timeout=15,
    )
    data = resp.json()

    if "error" in data:
        return {"status": "error", "message": str(data.get("error"))}

    pid = data.get("prompt_id", "")

    for _ in range(timeout // 3):
        time.sleep(3)
        try:
            r = requests.get(f"{comfy_url}/history/{pid}", timeout=10)
            hdata = r.json()
        except Exception:
            continue

        if pid in hdata and "outputs" in hdata.get(pid, {}):
            outputs = hdata[pid]["outputs"]
            msgs = hdata.get(pid, {}).get("status", {}).get("messages", [])
            for m in msgs:
                if "execution_error" in str(m):
                    return {"status": "error", "message": str(m)}

            if output_node in outputs:
                fname = outputs[output_node]["images"][0]["filename"]
                local_path = f"/tmp/hm_gen_{pid[:8]}.png"
                r = requests.get(
                    f"{comfy_url}/view",
                    params={"filename": fname, "type": "output"},
                    timeout=30,
                )
                with open(local_path, "wb") as f:
                    f.write(r.content)
                size_kb = os.path.getsize(local_path) // 1024
                return {"status": "ok", "path": local_path, "size_kb": size_kb}
            break

    return {"status": "timeout"}


def export_workflow(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_workflow_file(path):
    with open(path, "r") as f:
        data = json.load(f)
    if "workflow" in data:
        return data["workflow"], data.get("output_node"), data.get("meta", {})
    return data, None, {}


def _find_positive_clip_node(workflow):
    sampler_nodes = {
        nid: n
        for nid, n in workflow.items()
        if n.get("class_type") == "KSampler"
    }
    for nid, node in workflow.items():
        if node.get("class_type") != "CLIPTextEncode":
            continue
        for sid, snode in sampler_nodes.items():
            if snode["inputs"].get("positive") == [nid, 0]:
                return nid
    return None


def _find_save_image_node(workflow):
    for nid, node in workflow.items():
        if node["class_type"] == "SaveImage":
            return nid
    return None


def load_scene_config(scene_name):
    path = os.path.join(SKILL_DIR, "references", "scenes", f"{scene_name}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def generate(
    scene="",
    clothing="",
    expression="",
    composition="waist up",
    lighting=None,
    seed=None,
    scene_config=None,
    max_retries=3,
    no_faceid=False,
):
    """
    单张写真生成

    参数:
        scene: 场景描述（英文）
        clothing: 穿搭描述（英文）
        expression: 表情描述（英文）
        composition: 构图: close-up / waist up / mid-thigh up / full body / full body sit
        lighting: 光线描述（英文），None 则从配置读取
        seed: 指定 seed，None 则随机
        scene_config: 从 JSON 加载的场景配置，None 则仅用默认值
        max_retries: 最大重试次数
        no_faceid: 不使用 FaceID，纯 seed + prompt 控制（CFG 自动提高到 5.5）

    返回:
        dict: {status, path, seed, attempt, prompt, neg_prompt, config, log}
    """
    log = []
    config = _merge_config(scene_config)

    if lighting:
        config["lighting"] = lighting

    # no_faceid 模式：CFG 提高到 5.5，释放提示词控制力
    if no_faceid:
        config["sampler"]["cfg"] = 5.5
        log.append("模式: no_faceid (纯 seed + prompt，CFG=5.5)")

    smile, eyes_closed = _detect_expression_flags(expression)
    faceid_params = _get_faceid_params(config, smile)

    prompt, neg_prompt, comp = _build_prompts(config, clothing, expression, composition)

    comfy_url = config.get("comfyui_url", "http://10.28.9.6:8188")

    log.append(f"场景: {scene or config.get('scene', '')}")
    log.append(f"穿搭: {clothing}")
    log.append(f"表情: {expression}")
    log.append(f"构图: {composition} ({comp['w']}x{comp['h']} -> {comp['w']*2}x{comp['h']*2})")
    log.append(f"光线: {config.get('lighting', '')}")
    log.append(f"微笑: {smile}, 闭眼: {eyes_closed}")
    if no_faceid:
        log.append("FaceID: 关闭")
    else:
        log.append(f"FaceID: weight={faceid_params['weight']}, v2={faceid_params['weight_faceidv2']}, end_at={faceid_params['end_at']}")

    fd_config = config.get("face_detailer", {"enabled": False})
    log.append(f"FaceDetailer: enabled={fd_config.get('enabled', False)}, denoise={fd_config.get('denoise', 0.35)}, cfg={fd_config.get('cfg', 7.0)}")

    if not no_faceid:
        if not FACE_FILES:
            return {"status": "error", "message": "无参考图文件", "log": log}
        _upload_faces(comfy_url)
    _free_memory(comfy_url)

    current_seed = seed if seed is not None else random.randint(0, 2**32 - 1)

    for attempt in range(1, max_retries + 1):
        log.append(f"\n尝试 {attempt}/{max_retries}, seed={current_seed}")

        workflow, output_node = _build_workflow(
            prompt,
            neg_prompt,
            current_seed,
            comp,
            faceid_params,
            config["sampler"],
            config["hires"],
            config["model"],
            fd_config,
            no_faceid=no_faceid,
        )

        result = _submit_and_wait(workflow, output_node, comfy_url)

        if result["status"] != "ok":
            log.append(f"  失败: {result}")
            current_seed = random.randint(0, 2**32 - 1)
            _free_memory(comfy_url)
            continue

        log.append(f"  成功: {result['path']} ({result['size_kb']}KB)")

        return {
            "status": "ok",
            "path": result["path"],
            "seed": current_seed,
            "attempt": attempt,
            "prompt": prompt,
            "neg_prompt": neg_prompt,
            "config": {
                k: v for k, v in config.items() if k not in ("prompt_template", "neg_prompt_base")
            },
            "composition": f"{composition} ({comp['w']}x{comp['h']} -> {comp['w']*2}x{comp['h']*2})",
            "faceid": faceid_params,
            "smile": smile,
            "eyes_closed": eyes_closed,
            "log": log,
        }

    return {
        "status": "failed",
        "attempts": max_retries,
        "log": log,
    }


def main():
    """命令行入口"""
    import argparse

    default_config = _load_default_config()
    comp_choices = list(default_config["compositions"].keys())

    scenes_dir = os.path.join(SKILL_DIR, "references", "scenes")
    scene_names = sorted(
        f.replace(".json", "")
        for f in os.listdir(scenes_dir)
        if f.endswith(".json") and not f.startswith("_")
    )

    parser = argparse.ArgumentParser(description="韩梅梅写真生成")
    parser.add_argument("--scene", default="", help="场景描述")
    parser.add_argument("--clothing", default="", help="穿搭描述")
    parser.add_argument("--expression", default="", help="表情描述")
    parser.add_argument("--composition", default="waist up", choices=comp_choices)
    parser.add_argument("--lighting", default=None, help="光线描述")
    parser.add_argument("--seed", type=int, default=None, help="随机种子")
    parser.add_argument("--scene-config", default=None, help="场景配置名称", choices=scene_names)
    parser.add_argument("--max-retries", type=int, default=3, help="最大重试次数")
    parser.add_argument("--no-faceid", action="store_true", help="不使用 FaceID，纯 seed + prompt 模式")
    parser.add_argument("--export-workflow", metavar="PATH", help="导出工作流到 JSON 文件，不执行")
    parser.add_argument("--load-workflow", metavar="PATH", help="从 JSON 文件加载工作流执行")
    args = parser.parse_args()

    if args.export_workflow and args.load_workflow:
        parser.error("--export-workflow 和 --load-workflow 不能同时使用")

    scene_config = None
    if args.scene_config:
        scene_config = load_scene_config(args.scene_config)

    normal_seed = 98994781 if args.seed is None else args.seed

    if args.export_workflow:
        config = _merge_config(scene_config)
        if args.lighting:
            config["lighting"] = args.lighting
        if args.no_faceid:
            config["sampler"]["cfg"] = 5.5

        smile, eyes_closed = _detect_expression_flags(args.expression)
        faceid_params = _get_faceid_params(config, smile)
        prompt, neg_prompt, comp = _build_prompts(
            config, args.clothing, args.expression, args.composition
        )

        seed_val = normal_seed
        fd_config = config.get("face_detailer", {"enabled": False})

        workflow, output_node = _build_workflow(
            prompt, neg_prompt, seed_val, comp,
            faceid_params, config["sampler"], config["hires"], config["model"],
            fd_config, no_faceid=args.no_faceid,
        )

        mode = "no_faceid" if args.no_faceid else "faceid"
        meta = {
            "exported_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "mode": mode,
            "model": config["model"],
            "seed": seed_val,
            "scene": args.scene,
            "clothing": args.clothing,
            "expression": args.expression,
            "composition": args.composition,
            "lighting": config.get("lighting", ""),
        }

        export_data = {
            "meta": meta,
            "output_node": output_node,
            "workflow": workflow,
        }

        export_workflow(args.export_workflow, export_data)
        print(f"[EXPORT] 导出: {args.export_workflow}")
        sys.exit(0)

    if args.load_workflow:
        workflow, output_node, meta = load_workflow_file(args.load_workflow)
        config = _merge_config(scene_config)
        comfy_url = config.get("comfyui_url", "http://10.28.9.6:8188")
        log = []

        if args.seed is not None:
            ks_found = 0
            for nid, node in workflow.items():
                if node["class_type"] == "KSampler":
                    node["inputs"]["seed"] = args.seed + ks_found
                    ks_found += 1
            log.append(f"[LOAD] 覆写 seed={args.seed}")

        prompt_changed = any([
            args.clothing, args.scene, args.expression, args.lighting,
        ])
        if prompt_changed:
            cfg = _load_default_config()
            if args.scene:
                cfg["scene"] = args.scene
            if args.lighting:
                cfg["lighting"] = args.lighting
            clothing = args.clothing or meta.get("clothing", "")
            expression = args.expression or meta.get("expression", "")
            composition = args.composition or meta.get("composition", "waist up")
            new_prompt, _, _ = _build_prompts(cfg, clothing, expression, composition)
            pos_node = _find_positive_clip_node(workflow)
            if pos_node:
                workflow[pos_node]["inputs"]["text"] = new_prompt
                log.append(f"[LOAD] 覆写正面提示词 (node {pos_node})")
            else:
                log.append("[LOAD] 警告: 未找到正面提示词节点")

        if output_node is None:
            output_node = _find_save_image_node(workflow)
        if output_node is None:
            output_node = meta.get("output_node", "16")

        has_load_image = any(
            node["class_type"] == "LoadImage" for node in workflow.values()
        )
        if has_load_image:
            if not FACE_FILES:
                print("[LOAD] 错误: 无参考图文件")
                sys.exit(1)
            _upload_faces(comfy_url)

        for line in log:
            print(line)

        result = _submit_and_wait(workflow, output_node, comfy_url)

        if result["status"] == "ok":
            print(f"[LOAD] 结果: {result['path']} ({result['size_kb']}KB)")
        elif result["status"] == "timeout":
            print("[LOAD] 超时")
        else:
            print(f"[LOAD] 错误: {result.get('message', '')}")
        sys.exit(0 if result["status"] == "ok" else 1)

    result = generate(
        scene=args.scene,
        clothing=args.clothing,
        expression=args.expression,
        composition=args.composition,
        lighting=args.lighting,
        seed=normal_seed,
        scene_config=scene_config,
        max_retries=args.max_retries,
        no_faceid=args.no_faceid,
    )

    for line in result.get("log", []):
        print(line)

    print(f"\n结果: {result['status']}")
    if result["status"] == "ok":
        print(f"文件: {result['path']}")
        print(f"Seed: {result['seed']}")
    return result


if __name__ == "__main__":
    COMPOSITIONS_LOOKUP = _load_default_config()["compositions"]
    result = main()
    sys.exit(0 if result.get("status") == "ok" else 1)
