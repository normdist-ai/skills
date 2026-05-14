/**
 * 知乎搜索结果提取器
 * 用于 mcp_Playwright_playwright_evaluate 工具
 * 仅在浏览器直接搜索方案中需要（需要登录态）
 */

(function() {
  const noContent = document.querySelector('.SearchNoContent-wrap');
  if (noContent) {
    return JSON.stringify({
      success: false,
      reason: '未搜索到相关内容（可能未登录）',
      query: new URL(window.location.href).searchParams.get('q') || '',
      results: []
    }, null, 2);
  }

  const results = [];

  const cards = document.querySelectorAll(
    '.SearchResult-Card, .Card.SearchResult-Card, [class*="SearchResult"], .List-item'
  );

  cards.forEach((card, i) => {
    if (i >= 20) return;

    const titleEl = card.querySelector('h2 a, .ContentItem-title a, a[data-za-detail-view-name]');
    const title = titleEl ? titleEl.textContent.trim() : '';
    const url = titleEl ? titleEl.href : '';

    const excerptEl = card.querySelector('.content, .RichContent-inner, .Highlight');
    const excerpt = excerptEl ? excerptEl.textContent.trim().substring(0, 300) : '';

    const authorEl = card.querySelector('.AuthorInfo-name, .UserLink-link');
    const author = authorEl ? authorEl.textContent.trim() : '';

    if (title && url) {
      results.push({ title, url, excerpt, author });
    }
  });

  return JSON.stringify({
    success: true,
    query: new URL(window.location.href).searchParams.get('q') || '',
    source: 'browser',
    totalFound: results.length,
    results
  }, null, 2);
})();
