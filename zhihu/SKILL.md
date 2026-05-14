---
name: zhihu
description: >
  知乎文章搜索与读取。触发场景：(1) 用户提供知乎链接 → 读取文章全文；(2) 用户说"在知乎搜索"→ 搜索知乎文章列表。
  跨 IDE 技能：不同环境功能可用性不同，详见下方「环境适配」章节。
metadata:
  author: zhangjing
  version: "3.1"
  tested: "2026-05-03"
  compatibility: |
    Cherry Studio: 搜索✅ (Exa) + 读取✅ (Browser)
    Trae IDE: 搜索❌ (WebSearch受限) + 读取✅ (WebFetch)
---

# zhihu — 知乎文章搜索与读取

## 环境适配（跨 IDE）

本技能跨 IDE 使用，**不同环境功能可用性不同**：

| IDE | 搜索功能 | 读取功能 | 可用工具 |
|-----|---------|---------|---------|
| **Cherry Studio** | ✅ 可用 | ✅ 可用 | `mcp__exa__web_search_exa` + `mcp__browser` |
| **Trae IDE** | ❌ 受限 | ✅ 可用 | `WebSearch`（受限） + `WebFetch` |

### Cherry Studio 环境

搜索使用 **Exa 搜索引擎**，可成功搜索知乎内容：

```
mcp__exa__web_search_exa(
  query: "<关键词> site:zhuanlan.zhihu.com",
  numResults: 10
)
```

### Trae IDE 环境

- **WebSearch 对知乎索引有限制**：`site:zhihu.com` 搜索返回空结果
- **WebFetch 可以直接获取知乎内容**：无需处理反爬机制
- 搜索功能不可用时，提示用户提供直接链接

---

## Gotchas

这些是代理在没有明确告知的情况下会犯的错误：

- **搜索功能依赖环境** — Cherry Studio 可用 Exa 搜索，Trae IDE 的 WebSearch 对知乎索引有限制
- **WebFetch 可以直接获取知乎内容** — 无需使用 Playwright 或处理反爬机制
- **专栏文章和问答页面都支持** — `zhuanlan.zhihu.com/p/{id}` 和 `zhihu.com/question/{id}` 都可以读取
- **知乎搜索需要登录** — 浏览器直接打开 `zhihu.com/search` 未登录返回空结果

---

## 路由判断

| 输入类型 | 判断依据 | Cherry Studio | Trae IDE |
|----------|----------|---------------|----------|
| URL | 包含 `zhihu.com/p/` 或 `zhihu.com/question` | → **读取流程** ✅ | → **读取流程** ✅ |
| 关键词 | 不含知乎 URL | → **搜索流程** ✅ | → **提示用户提供链接** ⚠️ |

---

## Step A：读取文章（输入 = 知乎 URL）

### A1：获取页面内容

**Trae IDE**：使用 `WebFetch`

```
WebFetch(url: "<知乎文章URL>")
```

**Cherry Studio**：使用 `mcp__browser__open` + `mcp__browser__execute`

### A2：解析返回内容

返回 Markdown 格式内容，包含：标题、作者、正文、图片链接。

### A3：输出结构化结果

```json
{
  "title": "文章标题",
  "url": "原始URL",
  "content": "正文内容（Markdown格式）",
  "images": ["图片链接列表"],
  "fetchedAt": "获取时间"
}
```

---

## Step B：搜索文章（输入 = 关键词）

### Cherry Studio 环境

使用 Exa 搜索知乎：

```
mcp__exa__web_search_exa(
  query: "<关键词> site:zhuanlan.zhihu.com",
  numResults: 10
)
```

**搜索策略**：
- 默认限制 `site:zhuanlan.zhihu.com`（专栏文章，质量更高）
- 可并行发多个查询（不同关键词组合）提高覆盖
- 如需包含问答页面，改用 `site:zhihu.com`

### Trae IDE 环境

**WebSearch 对知乎索引有限制**，搜索返回空结果。

处理方式：提示用户
> "当前搜索引擎对知乎索引有限制，建议您直接在知乎网站搜索后提供文章链接，我可以帮您读取文章内容。"

---

## 验证循环

### 验证 URL 格式

检查 URL 是否匹配以下模式：
- `^https?://zhuanlan\.zhihu\.com/p/\d+`
- `^https?://(www\.)?zhihu\.com/question/\d+`

如果 URL 格式不正确，提示用户提供正确的知乎链接。

---

## References

| 文档 | 说明 |
|------|------|
| [technical-notes.md](references/technical-notes.md) | 技术说明、反爬机制、社区资源 |
| [examples.md](references/examples.md) | 使用示例 |
| [search.md](references/search.md) | 搜索策略详解（Cherry Studio） |
| [methods-comparison.md](references/methods-comparison.md) | 读取方法对比 |

> 📖 详细技术说明见 `references/technical-notes.md`
