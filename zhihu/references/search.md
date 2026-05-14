# 知乎搜索策略详解

## 测试日期
2026-05-03

## 核心结论

**WebFetch 可以直接获取知乎内容**：测试验证 WebFetch 可以成功获取知乎专栏文章和问答页面内容。

**WebSearch 对知乎索引有限制**：测试发现 `site:zhihu.com` 限制搜索返回空结果。

## 技术调研

### 知乎反爬机制

根据社区资料，知乎的反爬机制包括：

1. **x-zse-96 动态签名**
   - 格式：`2.0_` + Base64(HMAC-SHA256(签名字符串))
   - 签名字符串 = `方法+路径+参数+密钥`
   - 密钥：`d1a7f3566c0ef9b7c065e0e93b5b7e6a`（可能变化）

2. **Cookie/Session 校验**
   - 需要 `d_c0` Cookie
   - 需要 `_xsrf` 参数

3. **User-Agent 验证**
   - 需要模拟浏览器 User-Agent

4. **请求频率限制**
   - 频繁请求可能导致 IP 被封

### 页面数据结构

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

## 搜索策略

### 方案 A：WebFetch 直接获取（✅ 推荐）

**适用场景**：用户直接提供知乎链接

**优点**：
- 无需处理反爬机制
- 获取完整内容
- 返回 Markdown 格式

**测试结果**：
- 专栏文章：✅ 成功
- 问答页面：✅ 成功

### 方案 B：WebSearch 搜索（❌ 受限）

**适用场景**：用户提供关键词

**限制**：
- `site:zhihu.com` 限制搜索返回空结果
- 广泛搜索可能不返回知乎链接

**测试结果**：
- `site:zhihu.com hermes 应用场景`：❌ 无结果
- `hermes 应用场景 知乎`：❌ 无知乎链接

### 方案 C：用户自行搜索（✅ 推荐）

**适用场景**：用户需要搜索知乎内容

**流程**：
1. 用户在知乎网站或 App 搜索
2. 用户提供文章链接
3. 使用 WebFetch 读取内容

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

## 最佳实践

1. **优先使用 WebFetch**：直接获取页面内容，无需处理反爬
2. **建议用户提供链接**：避免搜索限制
3. **尊重 robots.txt**：遵守知乎的使用条款
4. **控制请求频率**：避免对服务器造成压力

## 更新日志

- 2026-05-03：发现 WebFetch 可以直接获取知乎内容，更新策略
- 2026-05-03：初始版本，使用 Playwright 方案
