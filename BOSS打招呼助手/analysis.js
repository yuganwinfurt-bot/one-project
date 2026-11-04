(() => {
  'use strict';

  const KEY = 'bqa-screening-records';
  const list = document.querySelector('#records-list');
  const count = document.querySelector('#records-count');
  const escapeHtml = value => String(value || '').replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[char]);

  function formatTime(timestamp) {
    const date = new Date(timestamp);
    if (Number.isNaN(date.getTime())) return '时间待确认';
    return new Intl.DateTimeFormat('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }).format(date);
  }

  function render(records) {
    const sorted = [...(Array.isArray(records) ? records : [])]
      .sort((left, right) => Number(right.analyzedAt || 0) - Number(left.analyzedAt || 0));
    count.textContent = `${sorted.length} 条记录`;
    if (!sorted.length) {
      list.innerHTML = '<div class="records-empty">还没有识别记录。回到 BOSS 职位列表，点击助手入口即可开始筛选。</div>';
      return;
    }
    list.innerHTML = sorted.map(record => {
      const title = escapeHtml(record.title || '岗位名称待确认');
      const titleContent = record.detailUrl
        ? `<a href="${escapeHtml(record.detailUrl)}" target="_blank" rel="noreferrer">${title}</a>`
        : title;
      return `<article class="record-card ${record.match ? 'is-match' : 'is-skip'}">
        <div class="record-card__status">${record.match ? '推荐' : '跳过'}</div>
        <div class="record-card__main">
          <h2>${titleContent}</h2>
          <p class="record-card__meta"><span>${escapeHtml(record.company || '公司信息待确认')}</span><i></i><span>${escapeHtml(record.salary || '薪资待确认')}</span><i></i><span>版本 ${escapeHtml(record.screeningVersion || '历史')}</span></p>
          ${record.tags ? `<p class="record-card__tags">${escapeHtml(record.tags)}</p>` : ''}
          <div class="record-card__analysis"><span>AI 判断</span><p>${escapeHtml(record.reason || 'AI 未返回判断')}</p></div>
        </div>
        <time datetime="${escapeHtml(record.analyzedAt || '')}">${formatTime(record.analyzedAt)}</time>
      </article>`;
    }).join('');
  }

  chrome.storage.local.get(KEY, data => render(data[KEY] || []));
  chrome.storage.onChanged.addListener((changes = {}) => {
    if (changes[KEY]) render(changes[KEY].newValue || []);
  });
})();
