# Whisper 语音识别服务

模型服务器上部署的 faster-whisper API 服务，用于语音转文字。

## 服务信息

| 项目 | 值 |
|------|-----|
| 地址 | `http://10.28.9.6:4299` |
| 模型 | faster-whisper base（139MB） |
| 设备 | CPU int8（ctranslate2 未编译 CUDA 支持） |
| 语言 | 中文优先（language='zh'） |
| Screen 会话 | `whisper` |
| 脚本路径 | `/home/tony/whisper-api.py` |

## API 接口

### POST /transcribe
上传音频文件，返回识别文字。

```bash
curl -X POST http://10.28.9.6:4299/transcribe \
  -F "file=@audio.ogg"
```

返回：
```json
{
  "text": "识别出的文字",
  "language": "zh",
  "language_probability": 0.95,
  "duration": 3.2,
  "elapsed": 1.1
}
```

### GET /health
健康检查。

## 部署注意事项

1. **必须 `local_files_only=True`**：服务器网络访问 HuggingFace 会卡死，模型必须预下载到缓存
2. **不支持 CUDA**：该服务器 ctranslate2 未编译 CUDA 后端，只能用 CPU
3. **cgi 模块弃用**：Python 3.12 中 `cgi` 模块已弃用（3.13 移除），日志会有 DeprecationWarning，不影响功能
4. **模型缓存位置**：`~/.cache/huggingface/hub/models--Systran--faster-whisper-base/`
5. **下载更大模型**：需设 `HF_ENDPOINT=https://hf-mirror.com`（国内镜像），base/small/medium/large-v3 可选

## 启动/重启

```bash
# SSH 到模型服务器
ssh tony@10.28.9.6

# 启动
screen -dmS whisper bash -c 'python3 whisper-api.py --model base --device cpu --compute-type int8 --port 4299 2>&1 | tee whisper-api.log'

# 检查
curl -s http://localhost:4299/health
```

## 与 Hermes 集成

未来可在 Hermes 侧添加语音消息处理流程：
1. 收到语音消息 → 下载音频文件
2. POST 到 Whisper API → 获取文字
3. 将文字作为用户输入继续对话
