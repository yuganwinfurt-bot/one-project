(() => {
  'use strict';

  function canonicalJobId(value, baseOrigin = 'https://www.zhipin.com') {
    const raw = String(value ?? '').trim();
    if (!raw || raw.includes('|')) return '';
    try {
      const url = new URL(raw, baseOrigin);
      const match = url.pathname.match(/\/job_detail\/([^/]+?)(?:\.html)?\/?$/i);
      if (match?.[1]) return String(match[1]).trim();
    } catch {
      // 页面属性中也可能只有不完整的路径，交给下面的正则处理。
    }
    const match = raw.match(/(?:^|\/)job_detail\/([^/?#]+?)(?:\.html)?\/?(?:[?#].*)?$/i);
    return String(match?.[1] || raw.split(/[?#]/)[0]).replace(/\.html$/i, '').replace(/\/$/, '').trim();
  }

  function fromCard(card, baseOrigin = location.origin) {
    if (!card) return '';
    const anchors = [
      ...(card.matches?.('a[href]') ? [card] : []),
      ...card.querySelectorAll('a[href]'),
    ];
    const link = anchors.find(anchor => /(?:^|\/)job_detail\//i.test(anchor.getAttribute('href') || anchor.href || ''));
    const linkId = canonicalJobId(link?.getAttribute('href') || link?.href || '', baseOrigin);
    if (linkId) return linkId;

    const dataNodes = [
      ...(card.matches?.('[data-jobid], [data-job-id], [data-encrypt-job-id]') ? [card] : []),
      ...card.querySelectorAll('[data-jobid], [data-job-id], [data-encrypt-job-id]'),
    ];
    for (const dataNode of dataNodes) {
      const value = dataNode.getAttribute('data-jobid')
        || dataNode.getAttribute('data-job-id')
        || dataNode.dataset.jobid
        || dataNode.dataset.jobId
        || dataNode.getAttribute('data-encrypt-job-id')
        || dataNode.dataset.encryptJobId
        || '';
      const id = canonicalJobId(value, baseOrigin);
      if (id) return id;
    }
    // securityId 是聊天接口的安全标识，不是岗位 ID，不能用于投递去重。
    return '';
  }

  globalThis.BqaJobId = Object.freeze({ canonicalJobId, fromCard });
})();
