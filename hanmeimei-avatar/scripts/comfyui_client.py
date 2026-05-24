#!/usr/bin/env python3
"""
韩梅梅技能 - ComfyUI 客户端
专门用于调用 comfyui 技能的封装层，提供统一的 API 接口。

职责：
1. 查找 comfyui 技能路径
2. 构建工作流 JSON
3. 调用 comfyui 技能执行
4. 处理输出结果
5. 上传图片到 ComfyUI 服务器

用法：
    from comfyui_client import ComfyUIClient
    client = ComfyUIClient()
    result = client.run_workflow(workflow_json, output_dir=None)  # 默认输出到技能目录下的 outputs 文件夹
"""

import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, Optional, List

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_OUTPUT_DIR = SKILL_DIR / "outputs"


class ComfyUIClient:
    """ComfyUI 技能客户端"""
    
    def __init__(self, host: str = "http://10.28.9.6:8188"):
        self.host = host
        self.comfyui_skill = self._find_comfyui_skill()
        self.run_workflow_script = self.comfyui_skill / "scripts" / "run_workflow.py"
        
        if not self.run_workflow_script.exists():
            raise FileNotFoundError(f"comfyui 技能脚本未找到: {self.run_workflow_script}")
    
    def _find_comfyui_skill(self) -> Path:
        """查找 comfyui 技能的路径"""
        script_dir = Path(__file__).resolve().parent
        skill_dir = script_dir.parent
        
        comfyui_path = skill_dir.parent / "comfyui"
        if comfyui_path.exists():
            return comfyui_path
        
        trae_skills = skill_dir.parent.parent / "skills" / "comfyui"
        if trae_skills.exists():
            return trae_skills
        
        workspace_root = skill_dir.parent.parent.parent
        comfyui_paths = list(workspace_root.rglob("skills/comfyui"))
        if comfyui_paths:
            return comfyui_paths[0]
        
        raise FileNotFoundError("comfyui 技能未找到")
    
    def upload_image(self, image_path: str, subfolder: str = "", image_type: str = "input") -> Dict:
        """
        上传图片到 ComfyUI 服务器
        
        Args:
            image_path: 本地图片路径
            subfolder: 子文件夹名称
            image_type: 图片类型 (input/temp)
        
        Returns:
            {"success": bool, "name": str, "error": str}
        """
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            filename = os.path.basename(image_path)
            
            boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
            body = []
            
            body.append(f'--{boundary}'.encode())
            body.append(f'Content-Disposition: form-data; name="image"; filename="{filename}"'.encode())
            body.append(b'Content-Type: image/png')
            body.append(b'')
            body.append(image_data)
            
            if subfolder:
                body.append(f'--{boundary}'.encode())
                body.append(f'Content-Disposition: form-data; name="subfolder"'.encode())
                body.append(b'')
                body.append(subfolder.encode())
            
            body.append(f'--{boundary}'.encode())
            body.append(f'Content-Disposition: form-data; name="type"'.encode())
            body.append(b'')
            body.append(image_type.encode())
            
            body.append(f'--{boundary}--'.encode())
            body.append(b'')
            
            body_data = b'\r\n'.join(body)
            
            url = f"{self.host}/upload/image"
            req = urllib.request.Request(
                url,
                data=body_data,
                headers={
                    "Content-Type": f"multipart/form-data; boundary={boundary}"
                }
            )
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
                return {"success": True, "name": result.get("name", filename)}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_image(self, filename: str, is_temp: bool = False) -> Dict:
        """
        删除 ComfyUI 服务器上的图片
        
        需要 ComfyUI-api-tools 扩展支持：
        cd ComfyUI/custom_nodes
        git clone https://github.com/brantje/ComfyUI-api-tools
        重启 ComfyUI 服务器
        
        Args:
            filename: 文件名（如 "HMM-FaceID_00001.png"）
            is_temp: 是否为临时图片（PreviewImage 节点生成）
        
        Returns:
            {"success": bool, "error": str}
        """
        try:
            url = f"{self.host}/api-tools/v1/images/output/{urllib.parse.quote(filename)}"
            if is_temp:
                url += "?temp=true"
            
            req = urllib.request.Request(url, method="DELETE")
            with urllib.request.urlopen(req, timeout=10) as resp:
                status_code = resp.getcode()
                if status_code in (200, 204):
                    print(f"[INFO] 删除服务器图片成功: {filename}", file=sys.stderr)
                    return {"success": True}
                else:
                    return {"success": False, "error": f"HTTP {status_code}"}
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"[WARN] 服务器图片不存在: {filename}", file=sys.stderr)
                return {"success": True}  # 404 也算成功（已不存在）
            elif e.code == 405:
                return {"success": False, "error": "未安装 ComfyUI-api-tools 扩展或不支持删除操作"}
            else:
                return {"success": False, "error": f"HTTP {e.code}: {e.reason}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_images(self, filenames: list[str], is_temp: bool = False) -> Dict:
        """
        批量删除 ComfyUI 服务器上的图片
        
        Args:
            filenames: 文件名列表
            is_temp: 是否为临时图片
        
        Returns:
            {"success": bool, "deleted": int, "failed": int, "errors": list}
        """
        deleted = 0
        failed = 0
        errors = []
        
        for filename in filenames:
            result = self.delete_image(filename, is_temp)
            if result.get("success"):
                deleted += 1
            else:
                failed += 1
                errors.append(f"{filename}: {result.get('error')}")
        
        return {
            "success": failed == 0,
            "deleted": deleted,
            "failed": failed,
            "errors": errors
        }
    
    def run_workflow(
        self,
        workflow: Dict,
        output_dir: Optional[str] = None,
        timeout: int = 600,
        input_images: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        调用 comfyui 技能执行工作流
        
        Args:
            workflow: ComfyUI 工作流 JSON
            output_dir: 输出目录（默认为技能目录下的 outputs 文件夹）
            timeout: 超时时间（秒）
            input_images: 输入图片字典，格式: {"文件名": "本地路径"}
        
        Returns:
            {"success": bool, "file": str, "error": str, "server_filename": str}
        """
        if output_dir is None:
            output_dir = str(DEFAULT_OUTPUT_DIR)
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        if input_images:
            for filename, local_path in input_images.items():
                result = self.upload_image(local_path)
                if not result.get("success"):
                    return {"success": False, "error": f"上传图片失败: {result.get('error')}"}
                uploaded_name = result.get("name", filename)
                print(f"[INFO] 上传图片: {filename} -> {uploaded_name}", file=sys.stderr)
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(workflow, f, indent=2)
            temp_workflow = Path(f.name)
        
        try:
            cmd = [
                sys.executable,
                str(self.run_workflow_script),
                "--workflow", str(temp_workflow),
                "--host", self.host,
                "--output-dir", output_dir,
                "--timeout", str(timeout),
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            
            if result.returncode != 0:
                return {"success": False, "error": result.stderr.strip()}
            
            output_path, server_filename = self._parse_output_path(result.stdout, output_dir)
            
            if output_path and os.path.exists(output_path):
                return {"success": True, "file": output_path, "server_filename": server_filename}
            else:
                return {"success": False, "error": f"未找到输出文件: {output_path or '解析失败'}"}
                
        finally:
            if temp_workflow.exists():
                temp_workflow.unlink()
    
    def _parse_output_path(self, stdout: str, output_dir: str) -> tuple[Optional[str], Optional[str]]:
        """
        解析 comfyui 技能输出，提取文件路径和服务器文件名
        
        Returns:
            (本地文件路径, 服务器文件名)
        """
        for line in stdout.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("{") and line.endswith("}"):
                try:
                    data = json.loads(line)
                    if "file" in data:
                        # 尝试从数据中获取服务器文件名
                        server_filename = None
                        if "outputs" in data and isinstance(data["outputs"], list) and len(data["outputs"]) > 0:
                            server_filename = data["outputs"][0].get("filename")
                        return data["file"], server_filename
                except json.JSONDecodeError:
                    pass
            
            if ".png" in line.lower() or ".jpg" in line.lower():
                match = re.search(r'["\']?([/\w\-\.]+\.(?:png|jpg|jpeg))["\']?', line, re.IGNORECASE)
                if match:
                    path = match.group(1)
                    if not os.path.isabs(path):
                        path = os.path.join(output_dir, os.path.basename(path))
                    server_filename = os.path.basename(path)
                    return path, server_filename
        
        return None, None


def main():
    """命令行测试入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ComfyUI 技能客户端")
    parser.add_argument("--workflow", required=True, help="工作流 JSON 文件路径")
    parser.add_argument("--output-dir", default=None, help=f"输出目录（默认: {DEFAULT_OUTPUT_DIR}）")
    parser.add_argument("--host", default="http://10.28.9.6:8188", help="ComfyUI 服务器地址")
    
    args = parser.parse_args()
    
    with open(args.workflow, "r", encoding="utf-8") as f:
        workflow = json.load(f)
    
    client = ComfyUIClient(host=args.host)
    result = client.run_workflow(workflow, output_dir=args.output_dir)
    
    if result["success"]:
        print(f"✅ 成功: {result['file']}")
    else:
        print(f"❌ 失败: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()