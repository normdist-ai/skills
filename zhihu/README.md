# zhihu - 知乎文章搜索与读取技能

知乎文章搜索与读取技能，支持专栏文章和问答页面的内容获取。

**跨 IDE 技能**：不同环境功能可用性不同。

## 环境适配

| IDE | 搜索功能 | 读取功能 | 可用工具 |
|-----|---------|---------|---------|
| **Cherry Studio** | ✅ 可用 | ✅ 可用 | `mcp__exa__web_search_exa` + `mcp__browser` |
| **Trae IDE** | ❌ 受限 | ✅ 可用 | `WebSearch`（受限） + `WebFetch` |

### Cherry Studio

- 搜索：使用 **Exa 搜索引擎**，可成功搜索知乎内容
- 读取：使用 **Browser 工具**，支持 JavaScript 提取

### Trae IDE

- 搜索：**WebSearch 对知乎索引有限制**，搜索返回空结果
- 读取：使用 **WebFetch**，无需处理反爬机制

## 目录结构

```
zhihu/
├── SKILL.md                 # 代理执行指令
├── README.md                # 本文件 - 人类阅读说明
├── scripts/                 # 可执行脚本
│   ├── extractor.js         # 文章内容提取器
│   └── search-extractor.js  # 搜索结果提取器
└── references/              # 参考文档
    ├── methods-comparison.md # 读取方法对比
    ├── search.md            # 搜索策略详解（Cherry Studio）
    ├── technical-notes.md   # 技术说明
    └── examples.md          # 使用示例
```

## 使用方法

### 读取文章（所有环境可用）

提供知乎链接，代理会自动读取文章内容：

```
读取这篇文章：https://zhuanlan.zhihu.com/p/81248091
```

### 搜索文章（仅 Cherry Studio）

在 Cherry Studio 中，可以直接搜索知乎：

```
在知乎搜索：人工智能量化交易
```

### Trae IDE 搜索替代方案

由于 WebSearch 对知乎索引有限制，建议用户直接在知乎网站搜索后提供链接。

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 3.1 | 2026-05-03 | 添加跨 IDE 环境适配说明 |
| 3.0 | 2026-05-03 | 使用 WebFetch 替代 Playwright，简化架构 |
| 2.1 | 2026-05-03 | 添加搜索策略文档 |
| 2.0 | 2026-05-03 | 初始版本，使用 Playwright |

## 相关资源

- [agentskills.io 官方规范](https://agentskills.io/home)
- [知乎 API 文档](https://www.zhihu.com/api/v4/)
