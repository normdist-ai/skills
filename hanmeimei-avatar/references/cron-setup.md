# 韩梅梅自拍定时任务配置指南

## 架构概览

```
cron scheduler (no_agent=true)
    → selfie.sh (统一入口，改一行切版本)
        → selfie-v5.py (当前生产版，纯生图, stdout → 临时文件)
        → feishu_sender.py (读临时文件, 三气泡发送)
```

三气泡顺序：①图片 → ②信息（纯文本，无引用标记无emoji） → ③想法

## 当前 Cron Job 配置

| 字段 | 值 |
|------|-----|
| job_id | `ecd3c0146879` |
| schedule | `*/30 6-23 * * *` |
| repeat | forever |
| no_agent | true |
| wrap_response | false |
| script | `selfie.sh`（位于 `~/.hermes/profiles/hanmeimei/scripts/`） |
| model | 无（no_agent 模式不需要） |
| deliver | origin |

## 统一入口模式

`selfie.sh` 是版本无关的入口脚本。切换生产版本只需改一行：

```bash
# 使用 v5（当前生产版）
SELFIE_V5="$SKILL_SCRIPTS/selfie-v5.py"

# 切换到 v6（开发中暂停）
# SELFIE_V6="$SKILL_SCRIPTS/selfie-v6.py"
```

## 关键配置依赖

1. **`cron.wrap_response: false`** — 防止 scheduler 把 script stdout 再包装投递
2. **Cron 超时** — 默认 5 分钟，生图一般 1-2 分钟，足够
3. **飞书凭证** — 从 `~/.hermes/profiles/hanmeimei/config.yaml` 的 `platforms.feishu` 读取
4. **chat_id** — 硬编码在 `feishu_sender.py` 中：`oc_1fac55adbc3e448aabcfc3839955e14a`
5. **必须用 venv python3** — selfie.sh 里用系统 python3 会导致 cffi 版本冲突（lark_oapi import 失败），必须硬编码 `/home/jarvis/.hermes/hermes-agent/venv/bin/python3`

## 文件清单

| 文件 | 位置 | 作用 |
|------|------|------|
| `selfie.sh` | `~/.hermes/profiles/hanmeimei/scripts/` | 统一入口，管道连接 |
| `selfie-v5.py` | `skills/creative/hanmeimei-avatar/scripts/` | 生产版生图脚本 |
| `feishu_sender.py` | `skills/creative/hanmeimei-avatar/scripts/` | 飞书三气泡发送 |
| `message-template.txt` | `skills/creative/hanmeimei-avatar/prompts/` | 消息格式模板 |
| `base.txt` + 场景文件 | `skills/creative/hanmeimei-avatar/prompts/` | 提示词 |

## 消息格式

stdout 输出格式（`selfie-v5.py` → `feishu_sender.py` 解析）：

```
MEDIA:/path/to/image.png
时间：2026-05-23 14:00:06
地点：咖啡馆
种子：12345678
---
今天天气真好
```

`feishu_sender.py` 解析规则：
- `MEDIA:` 开头的行 → 图片路径（气泡1）
- `MEDIA:` 和 `---` 之间的非空行 → 信息文本（气泡2）
- `---` 之后的行 → 想法（气泡3）

## 调试流程

1. 手动跑 `selfie-v5.py --scene cafe` 确认生图正常
2. 手动跑完整管道：`selfie-v5.py > tmp.txt && feishu_sender.py tmp.txt`
3. 触发 cron：`cronjob action=run job_id=ecd3c0146879`
4. 让用户在飞书验证效果

## 常见问题

| 症状 | 原因 | 修复 |
|------|------|------|
| cron 触发但无图 | 残留进程占 ComfyUI 队列 | `ps aux \| grep selfie` 杀掉残留进程 |
| 生图失败 + 路径错误 | hermes venv 里 `$HOME` 被覆写 | 硬编码绝对路径，不用 `~` 或 `expanduser` |
| 气泡2 为空 | `feishu_sender.py` 解析逻辑不匹配格式 | 确保 MEDIA 和 `---` 之间有非空信息行 |
| 13:30/14:00 没收到 | cron 正在跑错误版本的脚本 | 检查 `selfie.sh` 指向的是 v5 还是 v6 |
| sender 报 cffi 版本冲突 | selfie.sh 用了系统 python3 | 改用 venv python3 硬编码路径 |

## 切换到单气泡

如果三气泡出问题，可以在 `selfie.sh` 中跳过 `feishu_sender.py`：

```bash
# 单气泡模式：直接让 cron 投递 stdout
python3 "$SELFIE_V5" 2>/dev/null
# 不调用 feishu_sender.py
```

需要同时把 `cron.wrap_response` 改回 `true`。
