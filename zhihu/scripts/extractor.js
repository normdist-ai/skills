/**
 * 知乎文章内容提取器
 * 用于 mcp_Playwright_playwright_evaluate 工具
 */

(function() {
  const titleEl = document.querySelector('.Post-title');
  const title = titleEl ? titleEl.textContent.trim() : document.title.replace(' - 知乎', '');

  const authorEl = document.querySelector('.AuthorInfo-name');
  const author = authorEl ? authorEl.textContent.trim() : '未知作者';

  const contentEl = document.querySelector('.Post-RichText');
  const content = contentEl ? contentEl.textContent.trim() : '';

  const url = window.location.href;
  const publishTime = document.querySelector('.ContentItem-time')?.textContent.trim() || '';

  return JSON.stringify({
    title,
    author,
    content,
    url,
    publishTime,
    wordCount: content.length,
    extractedAt: new Date().toISOString()
  }, null, 2);
})();
