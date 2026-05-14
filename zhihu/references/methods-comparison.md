# 知乎文章读取方法对比测试

## 测试日期
2026-04-26

## 测试链接
- https://zhuanlan.zhihu.com/p/81248091
- https://zhuanlan.zhihu.com/p/2026323277375643746

## 方法对比

| 方法 | 工具 | 结果 | 推荐度 |
|------|------|------|--------|
| 直接 HTTP GET | WebFetch | ❌ 403 Forbidden | ❌ 不推荐 |
| 浏览器 txt | Playwright + get_visible_text | ✅ 成功（含导航栏） | ⚠️ 可用 |
| 浏览器 HTML | Playwright + get_visible_html | ⚠️ 需要清理 | ⚠️ 备选 |
| **浏览器 JS 执行** | **Playwright_evaluate** | **✅ 成功且精准** | **✅ 强烈推荐** |

## 推荐方案：Playwright_evaluate

### 优势
1. ✅ 完全绕过反爬虫
2. ✅ 精准提取 DOM 内容
3. ✅ 可返回结构化 JSON
4. ✅ 稳定性高
5. ✅ 灵活可扩展

### 示例代码

```javascript
const title = document.querySelector('.Post-title')?.textContent || document.title;
const author = document.querySelector('.AuthorInfo-name')?.textContent || '未知作者';
const content = document.querySelector('.Post-RichText')?.textContent || '';

JSON.stringify({
  title: title.trim(),
  author: author.trim(),
  content: content.trim(),
  url: window.location.href,
  length: content.length
}, null, 2);
```

## CSS 选择器验证

| 选择器 | 测试结果 | 说明 |
|--------|----------|------|
| `.Post-title` | ✅ 有效 | 文章主标题 |
| `.AuthorInfo-name` | ✅ 有效 | 作者名称 |
| `.Post-RichText` | ✅ 有效 | 文章正文区域 |
| `.ContentItem-time` | ⚠️ 部分有效 | 发布时间（部分页面有） |

## 反爬虫机制分析

知乎的反爬虫策略：
1. **User-Agent 检测**：要求完整浏览器 UA
2. **Cookie 验证**：部分内容需要登录
3. **JavaScript 渲染**：内容通过 JS 动态加载
4. **频率限制**：高频请求会被封禁

因此，**必须使用真实浏览器环境**（Playwright 工具）。

## 注意事项

1. 登录墙：部分文章可能需要登录才能查看完整内容
2. 图片：如需图片，用 `Playwright_screenshot` 或单独提取 `img` 标签
3. 代码块：知乎文章的代码块需要额外处理，当前方法会丢失格式
4. 表格：Markdown 表格会转换为纯文本

## 未来改进方向

- [ ] 支持问答页面（`www.zhihu.com/question`）
- [ ] 保留代码块格式
- [ ] 提取图片 URL
- [ ] 批量下载文章
- [ ] 导出为 Markdown 文件
