# 服务器缓存清理功能说明

## 概述

提供通过 SSH 远程删除 ComfyUI 服务器缓存图片的功能。

---

## 架构设计

### 职责分离

| 脚本 | 职责 |
|------|------|
| `selfie-v5.py` | 生成图片，不处理服务器缓存删除 |
| `deletefile.py` | 专门负责服务器文件删除操作 |
| `scheduler.py` | 调用 `deletefile.py` 执行批量清理 |

### 工作流程

```
生成流程：
selfie-v5.py → 生成图片 → 保存到本地
              ↓ (服务器缓存保留)

清理流程：
scheduler.py → 调用 deletefile.py → SSH 删除服务器文件
```

---

## 使用方法

### 1. 配置 SSH

编辑 `~/.avatar/config.json`：

```json
{
  "ssh": {
    "enabled": true,
    "host": "10.28.9.6",
    "user": "your_username",
    "output_dir": "/path/to/ComfyUI/output"
  }
}
```

### 2. 删除单个文件

```bash
py scripts/deletefile.py --filename HMM-FaceID_00250_.png
```

### 3. 批量清理

```bash
py scripts/deletefile.py --cleanup --retention-days 7
```

### 4. 列出文件

```bash
py scripts/deletefile.py --list --pattern "HMM-*.png"
```

### 5. 定时清理

```bash
py scripts/scheduler.py --cleanup-comfyui
```

---

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--enabled` | 是否启用 SSH | `false` |
| `--host` | SSH 主机地址 | - |
| `--user` | SSH 用户名 | - |
| `--output_dir` | ComfyUI output 目录路径 | - |
| `--pattern` | 文件匹配模式 | `HMM-*.png` |
| `--retention-days` | 保留天数 | `7` |

---

## 安全考虑

1. **SSH 密钥认证**（推荐）
   - 使用 SSH 密钥而非密码
   - 配置 `~/.ssh/config` 管理连接

2. **权限隔离**
   - SSH 用户仅需删除权限
   - 不建议使用 root 用户

3. **日志记录**
   - 所有删除操作会输出到 stderr
   - 便于审计和故障排查

---

## 配置示例

### Linux 服务器

```json
{
  "ssh": {
    "enabled": true,
    "host": "10.28.9.6",
    "user": "comfyui",
    "output_dir": "/opt/ComfyUI/output"
  }
}
```

### Windows 服务器

```json
{
  "ssh": {
    "enabled": true,
    "host": "10.28.9.6",
    "user": "administrator",
    "output_dir": "C:/ComfyUI/output"
  }
}
```

---

## 注意事项

1. **SSH 未启用时**
   - 不会执行删除操作
   - 生成图片功能正常
   - 服务器缓存会保留

2. **删除失败**
   - 不影响本地图片保存
   - 输出错误信息到 stderr

3. **清理策略**
   - 默认清理 7 天前的图片
   - 可在 config.json 中调整 `output.retention_days`

---

## 测试

### 测试删除功能

```bash
# 列出文件
py scripts/deletefile.py --list

# 删除单个文件（测试）
py scripts/deletefile.py --filename HMM-FaceID_00250_.png

# 批量清理（测试）
py scripts/deletefile.py --cleanup --retention-days 1
```

### 测试 scheduler 集成

```bash
py scripts/scheduler.py --cleanup-comfyui
```

---

## 故障排查

### 问题：SSH 连接失败

**错误**：`ssh: connect to host ... port 22: Connection refused`

**解决**：
1. 检查 SSH 服务是否运行
2. 检查防火墙设置
3. 检查主机地址是否正确

### 问题：权限不足

**错误**：`Permission denied`

**解决**：
1. 检查用户权限
2. 确认 output_dir 路径可写
3. 检查文件所有者

### 问题：文件不存在

**错误**：`No such file or directory`

**解决**：
1. 检查 output_dir 路径是否正确
2. 检查文件名是否匹配

---

## 版本历史

- **v5.2.0** (2026-05-23)：添加 SSH 远程删除功能
  - 创建独立的 deletefile.py 脚本
  - 移除 ClearNode 节点
  - 实现职责分离设计

---

## 参考文档

- [最佳实践指南](./BEST_PRACTICES.md)
- [SIPOC 优化文档](./SIPOC_OPTIMIZATION.md)
- [测试报告](./TEST_REPORT.md)