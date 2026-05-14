# 知乎技能技术说明

## 跨 IDE 环境适配

本技能跨 IDE 使用，**不同环境功能可用性不同**：

| IDE | 搜索功能 | 读取功能 | 可用工具 |
|-----|---------|---------|---------|
| **Cherry Studio** | ✅ 可用 | ✅ 可用 | `mcp__exa__web_search_exa` + `mcp__browser` |
| **Trae IDE** | ❌ 受限 | ✅ 可用 | `WebSearch`（受限） + `WebFetch` |

### Cherry Studio 环境

**搜索**：使用 Exa 搜索引擎

```
mcp__exa__web_search_exa(
  query: "<关键词> site:zhuanlan.zhihu.com",
  numResults: 10
)
```

Exa 是专门的 AI 搜索引擎，对知乎索引无限制。

**读取**：使用 Browser 工具

```
mcp__browser__open(url: "<知乎URL>")
mcp__browser__execute(script: "<extractor.js>")
```

### Trae IDE 环境

**搜索**：WebSearch 对知乎索引有限制

- `site:zhihu.com` 搜索返回空结果
- 建议用户提供直接链接

**读取**：使用 WebFetch

```
WebFetch(url: "<知乎URL>")
```

WebFetch 可以直接获取知乎内容，无需处理反爬机制。

---

## 为什么不同环境工具不同？

### Exa vs WebSearch

| 对比项 | Exa (Cherry Studio) | WebSearch (Trae IDE) |
|--------|---------------------|----------------------|
| 知乎索引 | ✅ 完整 | ❌ 受限 |
| 搜索质量 | 高 | 低 |
| 登录要求 | 无 | 无 |
| 返回格式 | 结构化 | 简单 |

### Browser vs WebFetch

| 对比项 | Browser (Cherry Studio) | WebFetch (Trae IDE) |
|--------|-------------------------|---------------------|
| 反爬处理 | 需要手动 | 自动处理 |
| JavaScript 执行 | ✅ 支持 | ❌ 不支持 |
| 配置复杂度 | 高 | 低 |
| 稳定性 | 中 | 高 |

---

## 知乎反爬机制

根据社区资料，知乎的反爬机制包括：

### x-zse-96 动态签名

- 格式：`2.0_` + Base64(HMAC-SHA256(签名字符串))
- 签名字符串 = `方法+路径+参数+密钥`
- 密钥：`d1a7f3566c0ef9b7c065e0e93b5b7e6a`（可能变化）

### 其他机制

- Cookie/Session 校验（需要 `d_c0` Cookie）
- User-Agent 验证
- 请求频率限制
- **搜索登录墙**：未登录返回"未搜索到相关内容"

---

## 页面数据结构

知乎页面在 `<script id="js-initialData">` 标签中包含完整的 JSON 数据：

```json
{
  "initialState": {
    "entities": {
      "questions": { ... },
      "answers": { ... },
      "articles": { ... }
    }
  }
}
```

---

## 社区资源

### 开源项目

1. **zhihu-api** (Node.js)
   - 项目地址：https://github.com/syaning/zhihu-api
   - 需要 Cookie 认证

2. **zhihu-api** (Python)
   - 项目地址：https://github.com/lzjun567/zhihu-api
   - 需要 Cookie 认证

3. **zhihu_crawler**
   - 项目地址：https://github.com/SmileXie/zhihu_crawler
   - 支持多账户、多线程

### API 接口

知乎内部 API 接口（需要签名）：

- 问答接口：`https://www.zhihu.com/api/v4/questions/{id}/answers`
- 用户接口：`https://www.zhihu.com/api/v4/members/{id}/profile`
- 搜索接口：`https://www.zhihu.com/api/v4/search_v3`

---

## 最佳实践

1. **根据环境选择工具**：Cherry Studio 用 Exa+Browser，Trae IDE 用 WebFetch
2. **建议用户提供链接**：避免搜索限制
3. **尊重 robots.txt**：遵守知乎的使用条款
4. **控制请求频率**：避免对服务器造成压力
