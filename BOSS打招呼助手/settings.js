(() => {
  'use strict';

  const SETTINGS_KEY = 'bqa-ai-settings';
  const SETTINGS_BACKUP_KEY = 'bqa-ai-settings-backup';
  const HIDDEN_COMPANIES_KEY = 'bqa-hidden-companies';
  const DISMISSED_JOBS_KEY = 'bqa-dismissed-jobs';
  const DELIVERED_KEY = 'bqa-delivered-jobs';
  const DELIVERY_RECORDS_KEY = 'bqa-delivery-records';
  const SCREENING_RECORDS_KEY = 'bqa-screening-records';
  const SEARCH_RUN_STATUS_KEY = 'bqa-search-run-status';
  const AI_DIAGNOSTIC_LOGS_KEY = 'bqa-ai-diagnostic-logs';
  const DELIVERY_DIAGNOSTIC_LOGS_KEY = 'bqa-delivery-diagnostic-logs';
  const DEFAULT_LIMIT = 150;
  const HISTORY_PAGE_SIZE = 25;
  const DEFAULT_API_URL = 'https://api.deepseek.com/chat/completions';
  const DEFAULT_MODEL = 'deepseek-flash';
  const DEFAULT_SCREENING_PROMPT = '你是谨慎的求职助手。仅依据求职者简历、多个目标岗位画像与岗位信息判断岗位是否匹配。每个岗位画像必须独立判断；岗位方向明显无关、要求明显超出简历时应判为不匹配。判断理由要具体、简洁，且只能基于已提供的信息。';
  const DEFAULT_GREETING_PROMPT = '你是求职者本人，正在 BOSS 直聘向 HR 发第一句招呼语。内容会原样发送。只能根据简历中真实具备的能力和经历写，严禁虚构。写自然真诚的中文开场白，优先点出与岗位最相关的技能和经历。';
  const CITY_CODES = { 全国: '100010000', 北京: '101010100', 上海: '101020100', 广州: '101280100', 深圳: '101280600', 杭州: '101210100', 成都: '101270100', 武汉: '101200100', 南京: '101190100', 苏州: '101190400', 西安: '101110100', 重庆: '101040100', 天津: '101030100', 长沙: '101250100', 郑州: '101180100', 厦门: '101230200', 青岛: '101120200', 济南: '101120100', 合肥: '101220100', 佛山: '101280800' };
  const FALLBACK_CITY_REGIONS = [
    { province: '全国', cities: ['全国'] }, { province: '北京市', cities: ['北京'] }, { province: '上海市', cities: ['上海'] },
    { province: '天津市', cities: ['天津'] }, { province: '重庆市', cities: ['重庆'] }, { province: '广东省', cities: ['广州', '深圳', '佛山'] },
    { province: '浙江省', cities: ['杭州'] }, { province: '四川省', cities: ['成都'] }, { province: '湖北省', cities: ['武汉'] },
    { province: '江苏省', cities: ['南京', '苏州'] }, { province: '陕西省', cities: ['西安'] }, { province: '湖南省', cities: ['长沙'] },
    { province: '河南省', cities: ['郑州'] }, { province: '福建省', cities: ['厦门'] }, { province: '山东省', cities: ['济南', '青岛'] },
    { province: '安徽省', cities: ['合肥'] },
  ];
  let CITY_REGIONS = FALLBACK_CITY_REGIONS.map(region => ({ province: region.province, cities: region.cities.map(name => ({ name, code: CITY_CODES[name] })) }));
  let CITY_ALIASES = {};
  const salaryOptions = [['0', '不限'], ['402', '3K 以下'], ['403', '3–5K'], ['404', '5–10K'], ['405', '10–20K'], ['406', '20–50K'], ['407', '50K 以上']];
  const jobTypeOptions = [['1902', '实习'], ['0', '不限'], ['1901', '全职'], ['1903', '兼职']];
  const $ = selector => document.querySelector(selector);
  const escapeHtml = value => String(value || '').replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[char]);
  const read = key => new Promise(resolve => chrome.storage.local.get(key, data => resolve(data[key])));
  const write = data => new Promise((resolve, reject) => chrome.storage.local.set(data, () => chrome.runtime.lastError ? reject(new Error(chrome.runtime.lastError.message)) : resolve()));
  const makeId = () => `search-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
  const CONFIG_EXPORT_VERSION = 1;
  const screeningConfigValue = value => String(value ?? '').trim();
  function screeningVersionFor(settings) {
    const profiles = Array.isArray(settings?.profiles) ? settings.profiles.map(profile => ({ id: profile.id, name: profile.name, targetProfile: profile.targetProfile, enabled: profile.enabled !== false })) : [];
    const snapshot = JSON.stringify({
      resumePdfText: screeningConfigValue(settings?.resumePdfText),
      targetProfile: screeningConfigValue(settings?.targetProfile),
      screeningPrompt: screeningConfigValue(settings?.screeningPrompt || DEFAULT_SCREENING_PROMPT),
      profiles,
    });
    let hash = 2166136261;
    for (let index = 0; index < snapshot.length; index += 1) {
      hash ^= snapshot.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    return `v1-${(hash >>> 0).toString(16).padStart(8, '0')}`;
  }

  function profileVersion(profile, settings) {
    return screeningVersionFor({ ...settings, targetProfile: `${profile.name}\n${profile.targetProfile}`, profiles: [] });
  }

  function normalizeProfiles(value, settings = {}) {
    if (Array.isArray(value) && value.length) return value.map((profile, index) => ({
      id: profile.id || `profile-${Date.now()}-${index}`,
      name: String(!profile.name || profile.name === '目标岗位' || profile.name === '默认岗位' || /^AI 细筛条件\s*\d+$/.test(profile.name) ? `岗位条件 ${index + 1}` : profile.name).trim(),
      targetProfile: String(profile.targetProfile ?? profile.description ?? '').trim(),
      enabled: profile.enabled !== false,
      version: profile.version || profileVersion(profile, settings),
    }));
    if (String(settings.targetProfile || '').trim()) return [{ id: 'legacy-default', name: '岗位条件 1', targetProfile: settings.targetProfile.trim(), enabled: true, version: profileVersion({ name: '岗位条件 1', targetProfile: settings.targetProfile }, settings) }];
    return [{ id: `profile-${Date.now()}`, name: '岗位条件 1', targetProfile: '', enabled: true, version: '' }];
  }
  const tabFromQuery = new URLSearchParams(location.search).get('tab') || 'basic';
  let settings = {};
  let blockedJobs = [];
  let blockedCompanies = [];
  let deliveredJobs = [];
  let deliveryRecords = [];
  let screeningRecords = [];
  let latestRunStatus = null;
  const historyPages = { ai: 1, manual: 1, companies: 1, contacted: 1, records: 1 };
  let searchConditions = [];
  let configRenderRevision = 0;

  function notice(message, type = 'success') {
    const target = $('#settings-notice');
    const displayedMessage = message && type === 'success' ? `✓ ${message}` : message;
    target.textContent = displayedMessage;
    target.className = `is-${type}`;
    if (displayedMessage) setTimeout(() => {
      if (target.textContent !== displayedMessage) return;
      target.textContent = '';
      target.className = '';
    }, 3600);
  }

  function cityCode(value) {
    const text = String(value || '').trim();
    return CITY_CODES[text] || CITY_CODES[CITY_ALIASES[text]] || (/^\d{6,12}$/.test(text) ? text : '');
  }

  function cityName(value) {
    const text = String(value || '').trim();
    return Object.entries(CITY_CODES).find(([, code]) => code === text)?.[0] || CITY_ALIASES[text] || text;
  }

  async function loadBossCityDirectory() {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 2200);
    try {
      const response = await fetch('https://www.zhipin.com/wapi/zpCommon/data/city.json', { credentials: 'include', cache: 'no-store', signal: controller.signal });
      if (!response.ok) return false;
      const payload = await response.json();
      const rows = payload?.zpData?.cityList;
      if (!Array.isArray(rows) || !rows.length) return false;
      const regions = rows.map(row => ({
        province: String(row?.name || '').trim(),
        cities: (Array.isArray(row?.subLevelModelList) ? row.subLevelModelList : []).map(city => ({ name: String(city?.name || '').trim(), code: String(city?.code || '').trim() })).filter(city => city.name && /^\d{6,12}$/.test(city.code)),
      })).filter(region => region.province && region.cities.length);
      if (!regions.length) return false;
      const codes = { 全国: '100010000' };
      regions.forEach(region => region.cities.forEach(city => { codes[city.name] = city.code; }));
      const aliases = {};
      Object.entries(CITY_CODES).forEach(([oldName, oldCode]) => {
        const canonicalName = Object.entries(codes).find(([, code]) => code === oldCode)?.[0];
        if (canonicalName && canonicalName !== oldName) aliases[oldName] = canonicalName;
      });
      Object.keys(CITY_CODES).forEach(name => delete CITY_CODES[name]);
      Object.assign(CITY_CODES, codes);
      CITY_ALIASES = aliases;
      CITY_REGIONS = [{ province: '全国', cities: [{ name: '全国', code: '100010000' }] }, ...regions];
      return true;
    } catch {
      return false;
    } finally {
      clearTimeout(timeout);
    }
  }

  function provinceForCity(name) {
    return CITY_REGIONS.find(region => region.cities.some(city => city.name === name))?.province || '全国';
  }

  function splitCityNames(value) {
    return [...new Set(String(value || '').split(/[、，,;；\/|\s]+/).map(city => cityName(city.trim())).filter(Boolean))];
  }

  function expandSearchCondition(condition) {
    const cities = splitCityNames(condition.city);
    return (cities.length ? cities : [condition.city]).map((city, index) => {
      const next = { ...condition, id: index === 0 ? condition.id : makeId(), city, url: '' };
      try { next.url = buildUrl(next); } catch { /* 暂未填写完整的任务保留为草稿。 */ }
      return next;
    });
  }

  function buildUrl(condition) {
    const city = cityCode(splitCityNames(condition.city)[0]);
    if (!city) throw new Error('请选择常用城市，或输入 BOSS 城市编码。');
    if (!String(condition.keyword || '').trim()) throw new Error('请填写搜索关键词。');
    const url = new URL('https://www.zhipin.com/web/geek/jobs');
    url.searchParams.set('query', String(condition.keyword).trim());
    url.searchParams.set('city', city);
    if (condition.salary && condition.salary !== '0') url.searchParams.set('salary', condition.salary);
    if (condition.jobType && condition.jobType !== '0') url.searchParams.set('jobType', condition.jobType);
    const position = String(condition.position || '').replace(/\s+/g, '');
    if (position) url.searchParams.set('position', position);
    return url.href;
  }

  function normalizeConditions(autoSearch = {}) {
    const legacy = autoSearch?.city || autoSearch?.keyword ? [autoSearch] : [];
    const items = Array.isArray(autoSearch?.conditions) ? autoSearch.conditions : legacy;
    return items.length ? items.map(item => {
      const condition = { id: item.id || makeId(), city: cityName(item.city), salary: item.salary || '0', jobType: item.jobType || '1902', position: item.position || '', keyword: item.keyword || '', enabled: Boolean(item.enabled), url: item.url || '' };
      try { condition.url = buildUrl(condition); } catch { /* 未填完整的旧条件继续作为草稿保留。 */ }
      return condition;
    }) : [{ id: makeId(), city: '', salary: '0', jobType: '1902', position: '', keyword: '', enabled: false, url: '' }];
  }

  function groupSearchConditions(conditions = searchConditions) {
    const groups = new Map();
    conditions.forEach(condition => {
      const common = { salary: condition.salary || '0', jobType: condition.jobType || '1902', enabled: Boolean(condition.enabled) };
      const key = JSON.stringify([common.salary, common.jobType, common.enabled]);
      if (!groups.has(key)) groups.set(key, { id: condition.id || makeId(), ...common, cities: [] });
      groups.get(key).cities.push(...splitCityNames(condition.city));
    });
    return [...groups.values()].map(group => ({ ...group, cities: [...new Set(group.cities)] }));
  }

  function isPlaceholderProfileName(name) {
    return /^(?:岗位条件|AI 细筛条件)\s*\d+$/.test(String(name || '').trim());
  }

  function profileSearchTerms(profiles = settings.profiles, currentSettings = settings) {
    return [...new Set(normalizeProfiles(profiles, currentSettings)
      .filter(profile => profile.enabled !== false)
      .map(profile => String(profile.name || '').trim())
      .filter(name => name && !isPlaceholderProfileName(name)))];
  }

  function visibleProfileSearchTerms() {
    const cards = [...document.querySelectorAll('[data-profile-list] .profile-editor')];
    if (!cards.length) return profileSearchTerms();
    return [...new Set(cards
      .filter(card => card.querySelector('[data-profile-enabled]')?.checked)
      .map(card => String(card.querySelector('[data-profile-name]')?.value || '').trim())
      .filter(name => name && !isPlaceholderProfileName(name)))];
  }

  function mergeLegacySearchTermsIntoProfiles(profiles, conditions, currentSettings = settings) {
    const normalized = normalizeProfiles(profiles, currentSettings);
    const legacyTerms = [...new Set((conditions || []).map(item => String(item.keyword || '').trim()).filter(Boolean))];
    if (!legacyTerms.length) return { profiles: normalized, changed: false };
    const next = normalized.map(profile => ({ ...profile }));
    const placeholders = next.filter(profile => isPlaceholderProfileName(profile.name));
    const seen = new Set(next.filter(profile => !isPlaceholderProfileName(profile.name)).map(profile => profile.name.toLocaleLowerCase()));
    let changed = false;
    legacyTerms.forEach(term => {
      const key = term.toLocaleLowerCase();
      if (seen.has(key)) return;
      const placeholder = placeholders.shift();
      if (placeholder) placeholder.name = term;
      else next.push({ id: `profile-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`, name: term, targetProfile: '', enabled: true, version: '' });
      seen.add(key);
      changed = true;
    });
    return { profiles: next, changed };
  }

  function conditionsForTemplate(template, terms = visibleProfileSearchTerms()) {
    const cities = template.cities.length ? template.cities : [''];
    const roleTerms = terms.length ? terms : [''];
    return cities.flatMap(city => roleTerms.map(keyword => ({
      id: makeId(), city, salary: template.salary, jobType: template.jobType, keyword, position: '',
      enabled: template.enabled, url: '',
    })));
  }

  function chooseTab(name) {
    const requestedTarget = name === 'auto-search' ? 'basic' : name;
    const target = document.querySelector(`[data-tab="${requestedTarget}"]`) ? requestedTarget : 'basic';
    document.querySelectorAll('[data-tab]').forEach(button => button.setAttribute('aria-selected', String(button.dataset.tab === target)));
    document.querySelectorAll('[data-panel]').forEach(panel => { panel.hidden = panel.dataset.panel !== target; });
    if (name === 'auto-search') $('[data-search-tasks]')?.scrollIntoView({ block: 'start' });
  }

  function renderBasic() {
    const renderRevision = configRenderRevision;
    const screeningVersion = settings.screeningVersion || screeningVersionFor(settings);
    $('[data-panel="basic"]').innerHTML = `<section class="script-launch-bar" aria-label="手动搜索入口"><div><strong>手动搜索</strong><span>按纳入顺序搜索的方案逐个搜索各城市岗位</span></div><button type="button" class="button primary" id="run-all-search">立即顺序搜索纳入方案</button></section><form id="basic-form" class="form-grid">
      <div class="settings-column">
        <section class="config-section wide">
          <header class="config-section__header"><span class="config-section__icon" aria-hidden="true">✦</span><div><h3>AI 接口</h3><p>用于岗位匹配与生成专属招呼语。</p></div></header>
          <div class="config-section__grid">
            <label class="field">API URL<input name="apiUrl" type="url" value="${escapeHtml(settings.apiUrl || DEFAULT_API_URL)}" placeholder="${DEFAULT_API_URL}"></label>
            <label class="field">API Key<input name="apiKey" type="password" value="${escapeHtml(settings.apiKey)}" placeholder="输入你的 API Key"></label>
            <label class="field">模型名<input name="model" value="${escapeHtml(settings.model || DEFAULT_MODEL)}" placeholder="${DEFAULT_MODEL}"><em class="field-note">V4.1 Flash-1017 的 API 模型名是 deepseek-flash；默认官方接口会使用 max 思考强度。</em></label>
            <div class="api-test-action"><button type="button" class="button" data-test-api>测试 API</button></div>
          </div>
        </section>
        <section class="config-section wide">
          <header class="config-section__header"><span class="config-section__icon" aria-hidden="true">◎</span><div><h3>岗位名称与 AI 匹配</h3><p>岗位名称同时作为 BOSS 搜索词；岗位要求只用于 AI 匹配，不用在右侧重复填写。</p></div><small class="screening-version">匹配机制版本号 ${escapeHtml(screeningVersion)}</small></header>
          <div class="config-section__grid">
            <div class="field wide"><span class="field-label"><span>岗位名称与岗位要求</span><em>名称用于 BOSS 搜索；岗位要求用于 AI 匹配</em></span><div class="profile-list" data-profile-list></div><button type="button" class="button" data-add-profile>＋增加岗位条件</button></div>
          </div>
        </section>
        <section class="config-section wide">
          <header class="config-section__header"><span class="config-section__icon" aria-hidden="true">→</span><div><h3>投递规则</h3><p>控制每轮投递的确认方式与每日额度。</p></div></header>
          <div class="config-section__grid">
            <label class="field">每日投递上限 <em>BOSS 每日可投递岗位数量</em><input name="dailyDeliveryLimit" type="number" min="1" value="${escapeHtml(settings.dailyDeliveryLimit || DEFAULT_LIMIT)}"></label>
            <fieldset class="delivery-mode"><legend>投递方式</legend><label><input type="radio" name="deliveryMode" value="confirm" ${settings.deliveryMode === 'confirm' ? 'checked' : ''}><span><strong>确认岗位后投递</strong><small>AI 筛选后，由你确认本轮要投递的岗位</small></span></label><label><input type="radio" name="deliveryMode" value="auto" ${settings.deliveryMode !== 'confirm' ? 'checked' : ''}><span><strong>不确认岗位自动投递</strong><small>AI 筛选完成后，立即向所有匹配岗位发起沟通</small></span></label></fieldset>
          </div>
        </section>
        <section class="config-section wide config-transfer">
          <header class="config-section__header"><span class="config-section__icon" aria-hidden="true">⇄</span><div><h3>导入导出</h3><p>导出或恢复当前基础配置与搜索方案。</p></div></header>
          <div class="config-transfer__body">
            <div><strong>配置文件</strong><span>API Key 和 PDF 提取文本也会包含在 JSON 文件中，请妥善保管。</span></div>
            <div class="config-transfer__actions"><button type="button" class="button" data-export-config>导出配置</button><button type="button" class="button primary" data-import-config>导入配置</button><input type="file" data-import-config-file accept="application/json,.json" hidden></div>
          </div>
        </section>
        <section class="config-section wide config-transfer">
          <header class="config-section__header"><span class="config-section__icon" aria-hidden="true">⌁</span><div><h3>运行诊断日志</h3><p>记录 AI 识别、投递队列、沟通按钮与确认弹窗的状态；不记录 API Key、简历全文或招呼语。</p></div></header>
          <div class="config-transfer__body">
            <div><strong>用于排查识别与投递异常</strong><span>导出包含当前队列快照、最近 600 条独立投递日志和 500 条综合运行事件；可在识别弹窗点击“队列诊断”查看卡住的步骤。</span></div>
            <div class="config-transfer__actions"><button type="button" class="button" data-export-ai-logs>导出运行日志</button><button type="button" class="button" data-clear-ai-logs>清空日志</button></div>
          </div>
        </section>
      </div>
      <div class="settings-column">
        <section class="config-section wide">
          <header class="config-section__header"><span class="config-section__icon" aria-hidden="true">▣</span><div><h3>简历资料</h3><p>PDF 在本机提取文字；AI 使用时会把文字发送到你设置的模型接口。</p></div></header>
          <div class="config-section__grid">
            <div class="field wide resume-pdf-field">
              <span>PDF 简历</span>
              <input name="resumePdf" type="file" accept="application/pdf,.pdf">
              <div class="resume-pdf-status" data-resume-pdf-status></div>
              <details class="resume-pdf-details" data-resume-pdf-details hidden><summary>查看本机提取的简历文字</summary><pre data-resume-pdf-preview></pre></details>
              <button type="button" class="button primary" data-generate-from-resume disabled>一键根据简历配置岗位</button>
              <small class="resume-pdf-help" data-resume-pdf-help>先填写 AI 接口 URL、Key 和模型，再上传 PDF 简历；生成结果会替换岗位条件和搜索词，城市、薪资、求职类型及投递规则保持不变。</small>
            </div>
          </div>
        </section>
        <section class="config-section wide config-prompts">
          <header class="config-section__header"><span class="config-section__icon" aria-hidden="true">✎</span><div><h3>AI 提示词</h3><p>岗位筛选和 AI 招呼语分别使用下方对应提示词；招呼方式由开关控制。</p></div></header>
          <div class="config-section__grid">
            <label class="field wide"><span class="field-label"><span>岗位识别提示词</span><em>自动保存后，当前任务下一条岗位生效</em></span><textarea class="short" name="screeningPrompt" placeholder="填写岗位匹配策略…">${escapeHtml(settings.screeningPrompt || DEFAULT_SCREENING_PROMPT)}</textarea><span class="prompt-field-help">停止输入约 0.6 秒后自动保存；正在进行的模型请求不会中途替换，后续岗位使用新提示词。自动注入：PDF 简历、岗位名称与岗位要求、岗位信息；JSON 返回结构由插件固定保护。</span><button type="button" class="prompt-reset" data-reset-prompt="screening">恢复默认</button></label>
            <label class="field wide"><span class="field-label"><span>打招呼话术提示词</span><em>控制开场白语气、重点和长度</em></span><textarea class="short" name="greetingPrompt" placeholder="填写话术生成策略…">${escapeHtml(settings.greetingPrompt || DEFAULT_GREETING_PROMPT)}</textarea><span class="prompt-field-help">自动注入：PDF 简历、岗位 JD 和匹配方向；最终只发送纯文本招呼语。</span><button type="button" class="prompt-reset" data-reset-prompt="greeting">恢复默认</button></label>
          </div>
          <div class="prompt-toggle-row"><div><strong>AI 招呼语开关</strong><small>开启后使用上方“打招呼话术提示词”生成并发送招呼语；关闭后，插件点击 BOSS“立即沟通”，招呼语由 BOSS 自动招呼设置决定。岗位筛选仍使用上方自定义规则。</small></div><label class="switch prompt-toggle"><input type="checkbox" name="aiGreetingEnabled" aria-label="启用 AI 招呼语" ${settings.aiGreetingEnabled !== false ? 'checked' : ''}><i></i></label></div>
        </section>
        <section class="config-section wide search-task-settings" data-search-tasks></section>
      </div>
      </form>`;
    const form = $('#basic-form');
    let profiles = normalizeProfiles(settings.profiles, settings);
    const profileList = form.querySelector('[data-profile-list]');
    const readProfileCards = () => [...profileList.querySelectorAll('.profile-editor')].map((card, index) => {
      const prior = profiles[Number(card.dataset.profileIndex)] || {};
      return {
        id: prior.id || `profile-${Date.now()}-${index}`,
        name: card.querySelector('[data-profile-name]').value.trim(),
        targetProfile: card.querySelector('[data-profile-target]').value.trim(),
        enabled: card.querySelector('[data-profile-enabled]').checked,
      };
    });
    const renderProfiles = () => {
      profileList.innerHTML = profiles.map((profile, index) => `<article class="profile-editor" data-profile-index="${index}"><header><strong>${escapeHtml(profile.name)}</strong><label><input type="checkbox" data-profile-enabled ${profile.enabled ? 'checked' : ''}>启用</label><button type="button" data-remove-profile title="删除岗位条件">×</button></header><label class="field">岗位名称<input data-profile-name value="${escapeHtml(profile.name)}" placeholder="例如：AI 应用开发实习生"></label><label class="field">岗位要求<textarea data-profile-target placeholder="填写职责、技术栈或实习要求；搜索关键词已有的信息不用重复写">${escapeHtml(profile.targetProfile)}</textarea></label><small>匹配机制版本号 ${escapeHtml(profile.version || '保存后生成')}</small></article>`).join('');
      profileList.querySelectorAll('[data-profile-name], [data-profile-target], [data-profile-enabled]').forEach(input => input.addEventListener('input', () => { if (input.matches('[data-profile-name]')) input.closest('.profile-editor').querySelector('header strong').textContent = input.value || '岗位条件'; scheduleAutoSave(); }));
      profileList.querySelectorAll('[data-profile-enabled]').forEach(input => input.addEventListener('change', () => scheduleAutoSave(true)));
      profileList.querySelectorAll('[data-remove-profile]').forEach(button => button.addEventListener('click', () => { if (profileList.children.length <= 1) return notice('至少保留一个岗位条件。', 'error'); profiles = readProfileCards(); profiles.splice(Number(button.closest('[data-profile-index]').dataset.profileIndex), 1); renderProfiles(); scheduleAutoSave(true); }));
    };
    renderProfiles();
    form.querySelector('[data-add-profile]').addEventListener('click', () => { profiles = readProfileCards(); profiles.push({ id: `profile-${Date.now()}`, name: `岗位条件 ${profiles.length + 1}`, targetProfile: '', enabled: true, version: '' }); renderProfiles(); scheduleAutoSave(true); });
    form.querySelectorAll('[data-reset-prompt]').forEach(button => button.addEventListener('click', () => {
      const field = button.dataset.resetPrompt === 'screening' ? form.elements.screeningPrompt : form.elements.greetingPrompt;
      field.value = button.dataset.resetPrompt === 'screening' ? DEFAULT_SCREENING_PROMPT : DEFAULT_GREETING_PROMPT;
      scheduleAutoSave(true);
    }));
    let pendingResumePdfText = settings.resumePdfText || '';
    let pendingResumePdfName = settings.resumePdfName || '';
    let pendingResumePdfPages = Number(settings.resumePdfPages) || 0;
    let autoSaveTimer;
    let saveRevision = 0;
    let basicSaveChain = Promise.resolve();
    const pdfStatus = form.querySelector('[data-resume-pdf-status]');
    const pdfDetails = form.querySelector('[data-resume-pdf-details]');
    const pdfTextPreview = form.querySelector('[data-resume-pdf-preview]');
    const pdfHelp = form.querySelector('[data-resume-pdf-help]');
    const generateFromResumeButton = form.querySelector('[data-generate-from-resume]');
    const importFile = form.querySelector('[data-import-config-file]');
    form.querySelector('[data-export-config]').addEventListener('click', exportConfig);
    form.querySelector('[data-import-config]').addEventListener('click', () => importFile.click());
    form.querySelector('[data-export-ai-logs]').addEventListener('click', exportAiDiagnostics);
    form.querySelector('[data-clear-ai-logs]').addEventListener('click', clearAiDiagnostics);
    importFile.addEventListener('change', async () => {
      const file = importFile.files?.[0];
      importFile.value = '';
      if (!file) return;
      try {
        const text = await file.text();
        await importConfig(text);
      } catch (error) {
        notice(error.message || '配置文件导入失败。', 'error');
      }
    });
    const saveBasic = async revision => {
      if (renderRevision !== configRenderRevision) return;
      const data = new FormData(form);
      const previousSearchTerms = [...new Set(searchConditions.map(item => String(item.keyword || '').trim()).filter(Boolean))].sort();
      const nextProfiles = readProfileCards();
      const nextSearchTerms = profileSearchTerms(nextProfiles).sort();
      await saveSettings({
        apiUrl: data.get('apiUrl').trim(),
        apiKey: data.get('apiKey').trim(),
        model: data.get('model').trim(),
        resumePdfText: pendingResumePdfText,
        resumePdfName: pendingResumePdfName,
        resumePdfPages: pendingResumePdfPages,
        screeningPrompt: data.get('screeningPrompt').trim() || DEFAULT_SCREENING_PROMPT,
        greetingPrompt: data.get('greetingPrompt').trim() || DEFAULT_GREETING_PROMPT,
        // 自定义筛选和招呼提示词始终生效；旧版本该开关已由 AI 招呼语开关取代。
        customPromptsEnabled: true,
        profileSalaryMin: null,
        profileSalaryMax: null,
        salaryMin: null,
        salaryMax: null,
        profiles: nextProfiles.map(profile => {
          return { ...profile, version: profileVersion(profile, settings) };
        }),
        resumeImage: '',
        deliveryMode: data.get('deliveryMode'),
        aiGreetingEnabled: data.get('aiGreetingEnabled') === 'on',
        // 页面点击方式已从设置中隐藏；历史配置也统一恢复为后台沟通。
        greetingMode: 'background',
        dailyDeliveryLimit: Number(data.get('dailyDeliveryLimit')) || DEFAULT_LIMIT,
      });
      if (revision !== saveRevision) return;
      if (JSON.stringify(previousSearchTerms) !== JSON.stringify(nextSearchTerms)) {
        const templates = groupSearchConditions(searchConditions);
        const nextConditions = templates.flatMap(template => conditionsForTemplate(template, nextSearchTerms));
        await saveAutoSearch(nextConditions);
      }
      const version = form.querySelector('.screening-version');
      if (version) version.textContent = `匹配机制版本号 ${settings.screeningVersion}`;
      notice('设置已自动保存');
    };
    const scheduleAutoSave = (immediate = false) => {
      clearTimeout(autoSaveTimer);
      const revision = ++saveRevision;
      autoSaveTimer = setTimeout(() => {
        basicSaveChain = basicSaveChain
          .catch(() => {})
          .then(() => saveBasic(revision))
          .catch(error => notice(error.message || '自动保存失败。', 'error'));
      }, immediate ? 0 : 600);
    };
    const updateResumePdfUi = () => {
      if (pendingResumePdfText) {
        pdfStatus.innerHTML = `<span>已读取 ${escapeHtml(pendingResumePdfName || '简历.pdf')}，${pendingResumePdfPages} 页，提取 ${pendingResumePdfText.length.toLocaleString()} 个字符。</span><button type="button" class="resume-pdf-remove" data-clear-resume-pdf>移除</button>`;
        pdfDetails.hidden = false;
        pdfTextPreview.textContent = pendingResumePdfText;
      } else {
        pdfStatus.innerHTML = '<span>尚未上传 PDF 简历。</span>';
        pdfDetails.hidden = true;
        pdfTextPreview.textContent = '';
      }
      updateAgentGate();
    };
    const updateAgentGate = () => {
      const agentReady = Boolean(form.apiUrl.value.trim() && form.apiKey.value.trim() && form.model.value.trim());
      generateFromResumeButton.disabled = !agentReady || !pendingResumePdfText || generateFromResumeButton.dataset.busy === 'true';
      if (!agentReady) pdfHelp.textContent = '先在上方 AI 接口填写 API URL、API Key 和模型，再使用此功能。';
      else if (!pendingResumePdfText) pdfHelp.textContent = '上传可复制文字的 PDF 简历后，即可一键生成岗位条件。扫描件暂不支持 OCR。';
      else pdfHelp.textContent = '生成结果会替换岗位条件和搜索词；城市、薪资、求职类型及投递规则保持不变。';
    };
    const flushBasicSave = async () => {
      clearTimeout(autoSaveTimer);
      const revision = ++saveRevision;
      basicSaveChain = basicSaveChain.catch(() => {}).then(() => saveBasic(revision));
      await basicSaveChain;
    };
    const readPdfLocally = async file => {
      if (!file || (!/\.pdf$/i.test(file.name) && file.type !== 'application/pdf')) throw new Error('请选择 PDF 简历文件。');
      if (file.size > 15 * 1024 * 1024) throw new Error('PDF 文件不能超过 15 MB。');
      const pdfjs = await import(chrome.runtime.getURL('vendor/pdfjs/build/pdf.mjs'));
      pdfjs.GlobalWorkerOptions.workerSrc = chrome.runtime.getURL('vendor/pdfjs/build/pdf.worker.mjs');
      const loadingTask = pdfjs.getDocument({
        data: new Uint8Array(await file.arrayBuffer()),
        cMapUrl: chrome.runtime.getURL('vendor/pdfjs/cmaps/'),
        cMapPacked: true,
        standardFontDataUrl: chrome.runtime.getURL('vendor/pdfjs/standard_fonts/'),
        wasmUrl: chrome.runtime.getURL('vendor/pdfjs/wasm/'),
        useSystemFonts: true,
        isEvalSupported: false,
      });
      try {
        const document = await loadingTask.promise;
        if (document.numPages > 12) throw new Error('简历 PDF 超过 12 页，请上传精简版简历。');
        const pages = [];
        for (let pageNumber = 1; pageNumber <= document.numPages; pageNumber += 1) {
          const page = await document.getPage(pageNumber);
          const content = await page.getTextContent();
          pages.push(content.items.map(item => `${item.str || ''}${item.hasEOL ? '\n' : ' '}`).join('')
            .replace(/[ \t]+\n/g, '\n').replace(/\n{3,}/g, '\n\n').trim());
        }
        const text = pages.filter(Boolean).join('\n\n');
        if (!text.trim()) throw new Error('没有提取到文字。若这是扫描件，请先用 OCR 转成可复制文字的 PDF。');
        if (text.length > 50000) throw new Error('提取文字超过 5 万字，请上传简历版 PDF。');
        return { text, pages: document.numPages };
      } finally {
        await loadingTask.destroy().catch(() => {});
      }
    };
    form.resumePdf.addEventListener('change', async () => {
      const file = form.resumePdf.files?.[0];
      form.resumePdf.value = '';
      if (!file) return;
      pdfStatus.textContent = '正在本机读取 PDF…';
      try {
        const extracted = await readPdfLocally(file);
        pendingResumePdfText = extracted.text;
        pendingResumePdfName = file.name;
        pendingResumePdfPages = extracted.pages;
        updateResumePdfUi();
        await flushBasicSave();
        notice('PDF 简历已在本机提取并保存。');
      } catch (error) {
        pdfStatus.textContent = error.message || 'PDF 读取失败。';
        updateAgentGate();
        notice(error.message || 'PDF 读取失败。', 'error');
      }
    });
    pdfStatus.addEventListener('click', event => {
      if (!event.target.matches('[data-clear-resume-pdf]')) return;
      pendingResumePdfText = '';
      pendingResumePdfName = '';
      pendingResumePdfPages = 0;
      updateResumePdfUi();
      scheduleAutoSave(true);
    });
    form.querySelectorAll('[name="apiUrl"], [name="apiKey"], [name="model"]').forEach(input => {
      input.addEventListener('input', updateAgentGate);
      input.addEventListener('change', updateAgentGate);
    });
    generateFromResumeButton.addEventListener('click', async () => {
      if (generateFromResumeButton.disabled) return;
      const agent = { apiUrl: form.apiUrl.value.trim(), apiKey: form.apiKey.value.trim(), model: form.model.value.trim() };
      if (!agent.apiUrl || !agent.apiKey || !agent.model) return notice('请先设置智能体：填写 AI 接口 URL、API Key 和模型名。', 'error');
      if (!pendingResumePdfText) return notice('请先上传并解析 PDF 简历。', 'error');
      generateFromResumeButton.dataset.busy = 'true';
      generateFromResumeButton.disabled = true;
      generateFromResumeButton.textContent = 'AI 正在生成岗位条件…';
      try {
        await flushBasicSave();
        const currentProfiles = readProfileCards();
        const preferences = groupSearchConditions(searchConditions).map(item => ({ cities: item.cities, jobType: item.jobType, salary: item.salary }));
        const response = await chrome.runtime.sendMessage({
          type: 'BQA_CONFIGURE_FROM_RESUME',
          settings: { ...agent, resumePdfText: pendingResumePdfText, profiles: currentProfiles },
          preferences,
        });
        if (!response) throw new Error('扩展后台没有返回 AI 结果。请到 edge://extensions 重新加载本扩展，刷新设置页后重试。');
        if (!response.ok) throw new Error(response.error || 'AI 请求失败但没有返回原因。请先点“测试 API”，再查看基础配置中的运行诊断日志。');
        profiles = response.profiles.map((profile, index) => ({ id: `profile-${Date.now()}-${index}`, name: profile.name, targetProfile: profile.targetProfile, enabled: true, version: '' }));
        renderProfiles();
        await flushBasicSave();
        notice(`已生成 ${profiles.length} 个岗位条件，搜索词已同步；城市、薪资、求职类型与投递规则未更改。`);
      } catch (error) {
        notice(error.message || '岗位条件生成失败。', 'error');
      } finally {
        generateFromResumeButton.dataset.busy = 'false';
        generateFromResumeButton.textContent = '一键根据简历配置岗位';
        updateResumePdfUi();
      }
    });
    updateResumePdfUi();
    form.querySelector('[data-test-api]').addEventListener('click', async event => {
      const button = event.currentTarget;
      const apiUrl = form.apiUrl.value.trim();
      const apiKey = form.apiKey.value.trim();
      const model = form.model.value.trim();
      if (!apiUrl || !apiKey || !model) return notice('请先填写 API URL、Key 和模型名。', 'error');
      button.disabled = true;
      button.textContent = '测试中…';
      try {
        const result = await chrome.runtime.sendMessage({ type: 'BQA_TEST_AI_CONNECTION', settings: { apiUrl, apiKey, model } });
        if (!result?.ok) throw new Error(result?.error || '测试请求未完成');
        notice(`API 调用成功：${result.status}，耗时 ${result.elapsed}ms；模型回复「${result.reply}」。`);
      } catch (error) { notice(`API 连接失败：${error.message || '未知错误'}`, 'error'); }
      finally { button.disabled = false; button.textContent = '测试 API'; }
    });
    form.addEventListener('input', event => { if (event.target.name !== 'resumePdf' && !event.target.closest('[data-search-tasks]')) scheduleAutoSave(); });
    form.addEventListener('change', event => { if (event.target.name !== 'resumePdf' && !event.target.closest('[data-search-tasks]')) scheduleAutoSave(true); });
    form.addEventListener('submit', event => { event.preventDefault(); scheduleAutoSave(true); });
  }

  function configExportPayload() {
    const exportSettings = { ...settings, screeningVersion: screeningVersionFor(settings) };
    if (exportSettings.autoSearch) exportSettings.autoSearch = { conditions: normalizeConditions(exportSettings.autoSearch) };
    delete exportSettings.resumeImage;
    return {
      format: 'boss-quick-apply-config',
      version: CONFIG_EXPORT_VERSION,
      exportedAt: new Date().toISOString(),
      settings: exportSettings,
    };
  }

  function exportConfig() {
    try {
      const json = JSON.stringify(configExportPayload(), null, 2);
      const blob = new Blob([json], { type: 'application/json;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      const stamp = new Date().toISOString().slice(0, 10);
      anchor.href = url;
      anchor.download = `boss直聘助手-配置-${stamp}.json`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      setTimeout(() => URL.revokeObjectURL(url), 0);
      notice('配置已导出');
    } catch (error) {
      notice(error.message || '配置导出失败。', 'error');
    }
  }

  async function exportAiDiagnostics() {
    try {
      const logs = await read(AI_DIAGNOSTIC_LOGS_KEY) || [];
      const deliveryLogs = await read(DELIVERY_DIAGNOSTIC_LOGS_KEY) || [];
      let queueSnapshot = null;
      let queueDiagnosticsError = '';
      let diagnosticsTimer;
      try {
        const response = await Promise.race([
          chrome.runtime.sendMessage({ type: 'BQA_GET_DELIVERY_DIAGNOSTICS' }),
          new Promise((_, reject) => { diagnosticsTimer = setTimeout(() => reject(new Error('读取队列快照超时')), 8000); }),
        ]);
        if (!response?.ok) throw new Error(response?.error || '读取队列快照失败');
        queueSnapshot = response.snapshot;
      } catch (error) { queueDiagnosticsError = String(error?.message || '读取队列快照失败').slice(0, 160); }
      finally { clearTimeout(diagnosticsTimer); }
      const json = JSON.stringify({ format: 'boss-quick-apply-runtime-diagnostics', version: 3, extensionVersion: chrome.runtime.getManifest().version, exportedAt: new Date().toISOString(), queueSnapshot, queueDiagnosticsError, deliveryLogs, logs }, null, 2);
      const url = URL.createObjectURL(new Blob([json], { type: 'application/json;charset=utf-8' }));
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `boss直聘助手-运行诊断日志-${new Date().toISOString().slice(0, 10)}.json`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      setTimeout(() => URL.revokeObjectURL(url), 0);
      notice(`已导出 ${logs.length} 条综合事件、${deliveryLogs.length} 条投递日志${queueDiagnosticsError ? '；队列快照读取失败，原因已写入文件' : '和当前队列快照'}`);
    } catch (error) {
      notice(error.message || '运行日志导出失败。', 'error');
    }
  }

  async function clearAiDiagnostics() {
    await write({ [AI_DIAGNOSTIC_LOGS_KEY]: [], [DELIVERY_DIAGNOSTIC_LOGS_KEY]: [] });
    notice('运行日志已清空');
  }

  async function importConfig(text) {
    let payload;
    try {
      payload = JSON.parse(text);
    } catch {
      throw new Error('配置文件不是有效的 JSON。');
    }
    if (!payload || typeof payload !== 'object' || Array.isArray(payload)) throw new Error('配置文件格式不正确。');
    if (payload.format && payload.format !== 'boss-quick-apply-config') throw new Error('这不是 BOSS 直聘助手的配置文件。');
    const imported = payload.settings;
    if (!imported || typeof imported !== 'object' || Array.isArray(imported)) throw new Error('配置文件中没有有效的配置内容。');
    if (imported.apiUrl !== undefined && typeof imported.apiUrl !== 'string') throw new Error('配置文件中的 API URL 格式不正确。');
    if (imported.autoSearch !== undefined && (typeof imported.autoSearch !== 'object' || Array.isArray(imported.autoSearch))) throw new Error('配置文件中的搜索方案格式不正确。');
    const next = { ...imported };
    delete next.resumeImage;
    const importedConditions = normalizeConditions(next.autoSearch);
    const migration = mergeLegacySearchTermsIntoProfiles(next.profiles, importedConditions, next);
    next.profiles = migration.profiles;
    delete next.screeningVersion;
    next.screeningVersion = screeningVersionFor(next);
    configRenderRevision += 1;
    await write({ [SETTINGS_KEY]: next, [SETTINGS_BACKUP_KEY]: settings });
    settings = next;
    searchConditions = importedConditions;
    const importedTemplates = groupSearchConditions(searchConditions);
    const importedRoleTerms = profileSearchTerms(settings.profiles, settings);
    searchConditions = importedTemplates.flatMap(template => conditionsForTemplate(template, importedRoleTerms));
    await saveAutoSearch(searchConditions);
    renderBasic();
    renderAutoSearch();
    notice('配置已导入并替换当前配置');
  }

  function searchTemplateCard(template, index) {
    const salaryOptionsMarkup = salaryOptions.map(([value, label]) => `<option value="${value}" ${template.salary === value ? 'selected' : ''}>${label}</option>`).join('');
    const jobTypeOptionsMarkup = jobTypeOptions.map(([value, label]) => `<option value="${value}" ${template.jobType === value ? 'selected' : ''}>${label}</option>`).join('');
    const province = template.province || provinceForCity(template.cities[0] || '全国');
    const provinceOptionsMarkup = CITY_REGIONS.map(region => `<option value="${escapeHtml(region.province)}" ${region.province === province ? 'selected' : ''}>${escapeHtml(region.province)}</option>`).join('');
    return `<article class="search-template" data-id="${escapeHtml(template.id)}" data-selected-cities="[]">
      <header class="search-template__header"><div><strong>搜索方案 ${index + 1}</strong><small class="search-template__city-count">已选 ${template.cities.length} 个城市</small></div><label class="search-template__enabled"><input data-template-enabled type="checkbox" ${template.enabled ? 'checked' : ''}><span>纳入手动顺序搜索</span></label><button type="button" class="search-template__remove" data-remove-template>删除方案</button></header>
      <div class="search-template__grid">
        <div class="search-template__cities">
          <div class="search-template__city-heading"><strong>搜索城市</strong><span>先选省份，再勾选城市；可切换省份继续添加</span></div>
          <div class="search-template__province-row"><label class="field">省份<select data-template-province>${provinceOptionsMarkup}</select></label><button type="button" class="button" data-select-province>全选本省</button></div>
          <div class="search-template__city-options" data-city-options></div>
          <div class="search-template__selected-cities" data-selected-city-list></div>
        </div>
        <label class="field">求职类型<select data-template-field="jobType">${jobTypeOptionsMarkup}</select></label>
        <label class="field">薪资范围<select data-template-field="salary">${salaryOptionsMarkup}</select></label>
      </div>
    </article>`;
  }

  function selectedCitiesFromTemplate(card) {
    try { return JSON.parse(card.dataset.selectedCities || '[]').map(cityName); } catch { return []; }
  }

  function templateFromCard(card) {
    const value = name => card.querySelector(`[data-template-field="${name}"]`).value.trim();
    return {
      id: card.dataset.id || makeId(), cities: selectedCitiesFromTemplate(card), salary: value('salary'), jobType: value('jobType'),
      enabled: card.querySelector('[data-template-enabled]').checked,
      province: card.querySelector('[data-template-province]').value,
    };
  }

  function renderTemplateCityPicker(card) {
    const selectedCities = selectedCitiesFromTemplate(card);
    const provinceSelect = card.querySelector('[data-template-province]');
    const region = CITY_REGIONS.find(item => item.province === provinceSelect.value) || CITY_REGIONS[0];
    const names = region?.cities || [];
    card.querySelector('[data-city-options]').innerHTML = names.map(city => `<label><input data-template-city type="checkbox" value="${escapeHtml(city.name)}" ${selectedCities.includes(city.name) ? 'checked' : ''}><span>${escapeHtml(city.name)}</span></label>`).join('') || '<span class="search-template__empty">该省份暂时没有可选城市</span>';
    card.querySelector('[data-selected-city-list]').innerHTML = selectedCities.map(city => `<button type="button" class="search-city-chip" data-remove-selected-city="${escapeHtml(city)}">${escapeHtml(city)}<span aria-hidden="true">×</span></button>`).join('') || '<span class="search-template__empty">还没有选择城市</span>';
    card.querySelector('.search-template__city-count').textContent = `已选 ${selectedCities.length} 个城市`;
    card.dataset.selectedCities = JSON.stringify(selectedCities);
  }

  function refreshTemplateCityPickers() {
    document.querySelectorAll('.search-template').forEach(card => {
      const provinceSelect = card.querySelector('[data-template-province]');
      const selectedCities = selectedCitiesFromTemplate(card);
      const preferredProvince = CITY_REGIONS.some(region => region.province === provinceSelect.value) ? provinceSelect.value : provinceForCity(selectedCities[0] || '全国');
      provinceSelect.innerHTML = CITY_REGIONS.map(region => `<option value="${escapeHtml(region.province)}">${escapeHtml(region.province)}</option>`).join('');
      provinceSelect.value = CITY_REGIONS.some(region => region.province === preferredProvince) ? preferredProvince : (CITY_REGIONS[0]?.province || '');
      card.dataset.selectedCities = JSON.stringify(selectedCities);
      renderTemplateCityPicker(card);
    });
  }

  function renderAutoSearch() {
    const panel = $('[data-search-tasks]');
    const templates = groupSearchConditions();
    panel.innerHTML = `<header class="config-section__header"><span class="config-section__icon" aria-hidden="true">⌕</span><div><h3>搜索方案</h3><p>仅手动搜索：选择纳入顺序搜索的方案，再点击页面顶部按钮启动；扩展不会按时间自动搜索。</p></div></header><div class="search-template-toolbar"><button type="button" class="button" id="add-search">+新增搜索方案</button></div><p class="task-table-hint">省份和城市可多选；切换省份不会清掉已选城市。岗位要求用于 AI 匹配，不会重复作为搜索词。</p><div class="search-template-list">${templates.map(searchTemplateCard).join('')}</div>`;
    const list = panel.querySelector('.search-template-list');
    const readTemplates = () => [...list.querySelectorAll('.search-template')].map(templateFromCard);
    const persistTemplates = items => saveAutoSearch(items.flatMap(item => conditionsForTemplate(item)));
    let autoSaveTimer;
    const autoSave = () => {
      clearTimeout(autoSaveTimer);
      autoSaveTimer = setTimeout(async () => {
        try {
          await persistTemplates(readTemplates());
          notice('搜索方案已自动保存');
        } catch (error) { notice(error.message || '自动保存失败。', 'error'); }
      }, 300);
    };
    list.querySelectorAll('.search-template').forEach((card, index) => {
      card.dataset.selectedCities = JSON.stringify(templates[index]?.cities || []);
      renderTemplateCityPicker(card);
      const province = card.querySelector('[data-template-province]');
      province.addEventListener('change', () => renderTemplateCityPicker(card));
      card.querySelectorAll('[data-template-field]').forEach(field => {
        field.addEventListener('input', autoSave);
        field.addEventListener('change', autoSave);
      });
      card.querySelector('[data-template-enabled]').addEventListener('change', autoSave);
      card.querySelector('[data-city-options]').addEventListener('change', event => {
        if (!event.target.matches('[data-template-city]')) return;
        const city = cityName(event.target.value);
        let selected = selectedCitiesFromTemplate(card);
        if (city === '全国' && event.target.checked) selected = ['全国'];
        else if (event.target.checked) selected = [...selected.filter(item => item !== '全国'), city];
        else selected = selected.filter(item => item !== city);
        card.dataset.selectedCities = JSON.stringify([...new Set(selected)]);
        renderTemplateCityPicker(card);
        autoSave();
      });
      card.querySelector('[data-selected-city-list]').addEventListener('click', event => {
        const remove = event.target.closest('[data-remove-selected-city]');
        if (!remove) return;
        const city = cityName(remove.dataset.removeSelectedCity);
        card.dataset.selectedCities = JSON.stringify(selectedCitiesFromTemplate(card).filter(item => item !== city));
        renderTemplateCityPicker(card);
        autoSave();
      });
      card.querySelector('[data-select-province]').addEventListener('click', () => {
        const region = CITY_REGIONS.find(item => item.province === province.value);
        const names = (region?.cities || []).map(city => city.name);
        const selected = names.includes('全国') ? ['全国'] : [...new Set([...selectedCitiesFromTemplate(card).filter(city => city !== '全国'), ...names])];
        card.dataset.selectedCities = JSON.stringify(selected);
        renderTemplateCityPicker(card);
        autoSave();
      });
      card.querySelector('[data-remove-template]').addEventListener('click', async () => {
        if (list.children.length <= 1) return notice('至少保留一个搜索方案。', 'error');
        const remaining = readTemplates().filter(item => item.id !== card.dataset.id);
        try { await persistTemplates(remaining); renderAutoSearch(); }
        catch (error) { notice(error.message || '删除方案失败。', 'error'); }
      });
    });
    $('#add-search').addEventListener('click', async () => {
      const current = readTemplates();
      current.push({ id: makeId(), cities: [], salary: '0', jobType: '1902', enabled: false, province: CITY_REGIONS.find(region => region.province === '广东省')?.province || CITY_REGIONS[0]?.province || '' });
      try { await persistTemplates(current); renderAutoSearch(); }
      catch (error) { notice(error.message || '新建方案失败。', 'error'); }
    });
    $('#run-all-search').onclick = async event => {
      const button = event.currentTarget;
      const current = readTemplates();
      const enabledTemplates = current.filter(item => item.enabled);
      if (!enabledTemplates.length) return notice('请先勾选至少一个“纳入手动顺序搜索”的方案。', 'error');
      if (enabledTemplates.some(item => !item.cities.length)) return notice('请给已纳入的方案选择城市。', 'error');
      const roleTerms = visibleProfileSearchTerms();
      if (!roleTerms.length) return notice('请先在左侧“岗位名称”填写并启用至少一个岗位。', 'error');
      button.disabled = true;
      try {
        const saved = await persistTemplates(current);
        const enabled = saved.filter(item => item.enabled && item.url);
        if (!enabled.length) throw new Error('没有可运行的任务，请检查城市名称和关键词。');
        if (saved.some(item => item.enabled && !item.url)) throw new Error('有城市没有对应的 BOSS 编码，请重新选择城市。');
        const result = await chrome.runtime.sendMessage({ type: 'BQA_RUN_AUTO_SEARCH_BATCH', conditions: enabled });
        if (!result?.ok) throw new Error(result?.error || '无法启动多城市搜索');
        notice(`已启动 ${enabled.length} 条搜索（${enabledTemplates.reduce((sum, item) => sum + item.cities.length, 0)} 个城市 × ${roleTerms.length} 个岗位名称），将按顺序运行`);
      } catch (error) { notice(error.message || '无法启动多城市搜索。', 'error'); }
      finally { button.disabled = false; }
    };
  }

  async function saveAutoSearch(items) {
    const conditions = items.flatMap(expandSearchCondition).map(item => {
      if (!item.url) return item;
      return { ...item, url: buildUrl(item) };
    });
    await saveSettings({ autoSearch: { conditions } });
    searchConditions = conditions;
    return conditions;
  }

  function detailLink(job, fallback) { return job.detailUrl ? `<a href="${escapeHtml(job.detailUrl)}" target="_blank" rel="noopener noreferrer">${escapeHtml(job.title || fallback)}</a>` : `<strong>${escapeHtml(job.title || fallback)}</strong>`; }
  function formatTime(timestamp) { const date = new Date(timestamp); return Number.isNaN(date.getTime()) ? '时间待记录' : new Intl.DateTimeFormat('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }).format(date); }
  function normalizeBlockedText(value) { return String(value || '').replace(/\s+/g, '').trim().toLocaleLowerCase(); }
  function blockedIdentityTokens(job) {
    if (typeof job === 'string') return job.trim() ? [`id:${job.trim().toLocaleLowerCase()}`] : [];
    if (!job || typeof job !== 'object') return [];
    const tokens = [];
    const id = job.id ?? job.jobId ?? job.encryptJobId;
    if (id !== undefined && id !== null && String(id).trim()) tokens.push(`id:${String(id).trim().toLocaleLowerCase()}`);
    if (job.detailUrl) {
      try {
        const url = new URL(job.detailUrl, location.origin);
        tokens.push(`url:${url.host.toLocaleLowerCase()}${url.pathname.replace(/\/+$/, '').toLocaleLowerCase()}`);
      } catch { /* 无效链接仍可用岗位 ID 或标题识别。 */ }
    }
    const title = normalizeBlockedText(job.title);
    const company = normalizeBlockedText(job.company);
    if (title || company) tokens.push(`text:${title}|${company}`);
    return [...new Set(tokens)];
  }
  function blockedIdentity(job) { return blockedIdentityTokens(job)[0] || `unknown:${JSON.stringify(job || {})}`; }
  function identitiesOverlap(left, right) {
    const rightTokens = new Set(blockedIdentityTokens(right));
    return blockedIdentityTokens(left).some(token => rightTokens.has(token));
  }
  function aiExcludedJobs() {
    const delivered = communicationJobs().filter(job => job.deliveryStatus === '已投递');
    const manual = blockedJobs;
    const hiddenCompanyNames = new Set(blockedCompanies.map(normalizeBlockedText));
    const seen = new Set();
    return [...screeningRecords]
      .filter(record => record && record.match === false && !record.manualOverride)
      .sort((a, b) => Number(b.analyzedAt || 0) - Number(a.analyzedAt || 0))
      .filter(record => {
        if (delivered.some(job => identitiesOverlap(record, job)) || manual.some(job => identitiesOverlap(record, job))) return false;
        if (record.company && hiddenCompanyNames.has(normalizeBlockedText(record.company))) return false;
        const key = blockedIdentity(record);
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      });
  }
  function paginatedRows(items, key, renderRow, emptyText) {
    const total = items.length;
    const pageCount = Math.max(1, Math.ceil(total / HISTORY_PAGE_SIZE));
    historyPages[key] = Math.min(Math.max(1, historyPages[key] || 1), pageCount);
    const page = historyPages[key];
    const start = (page - 1) * HISTORY_PAGE_SIZE;
    const rows = total ? items.slice(start, start + HISTORY_PAGE_SIZE).map(renderRow).join('') : `<p class="empty">${emptyText}</p>`;
    const controls = pageCount > 1 ? `<nav class="history-pagination" aria-label="历史记录分页"><span>第 ${page} / ${pageCount} 页 · 共 ${total} 条</span><button type="button" data-history-page="${key}" data-page="${page - 1}" ${page <= 1 ? 'disabled' : ''}>上一页</button><button type="button" data-history-page="${key}" data-page="${page + 1}" ${page >= pageCount ? 'disabled' : ''}>下一页</button></nav>` : '';
    return { rows, controls };
  }
  function runStatusMarkup() {
    if (!latestRunStatus) return '<div class="run-status is-empty"><strong>本轮搜索进度</strong><p>还没有保存过本轮扫描数据。屏蔽数和沟通数是历史记录，不能代表搜索总量。</p></div>';
    const status = latestRunStatus;
    const stale = status.status === 'running' && Date.now() - Number(status.updatedAt || 0) > 60000;
    const labels = { running: stale ? '进度已停止更新' : '正在运行', completed: '已完成', partial: '中途异常，已保留结果', stopped: '用户已停止', 'daily-limit': '达到今日投递上限', failed: '运行失败', interrupted: '任务提前结束' };
    const stamp = status.updatedAt ? new Date(status.updatedAt).toLocaleString('zh-CN', { hour12: false }) : '时间未知';
    const search = [status.keyword, status.city && `城市 ${status.city}`, status.jobType && `类型 ${status.jobType}`].filter(Boolean).join(' · ') || '当前 BOSS 搜索条件';
    return `<div class="run-status ${stale ? 'is-stale' : `is-${escapeHtml(status.status || 'unknown')}`}" data-run-status-card><div class="run-status__head"><strong>本轮搜索进度</strong><span>${escapeHtml(labels[status.status] || '状态未知')}</span></div><div class="run-status__metrics"><span>唯一岗位 <b>${Number(status.eligible || 0)}</b></span><span>本页新增 <b>${Number(status.pageNew || 0)}</b></span><span>本页重复 <b>${Number(status.pageRepeated || 0)}</b></span><span>已筛选 <b>${Number(status.screened || 0)}</b></span><span>匹配 <b>${Number(status.matched || 0)}</b></span><span>排除 <b>${Number(status.excluded || 0)}</b></span></div><p>${escapeHtml(search)}${status.page ? ` · 第 ${Number(status.page)} 页` : ''}</p><small>最近更新：${escapeHtml(stamp)} · ${escapeHtml(status.phase || '')}${stale ? '。超过 1 分钟没有可见进度，可能卡住，也可能仍在等待接口重试。' : ''}</small></div>`;
  }
  function refreshRunStatusCards() {
    document.querySelectorAll('[data-run-status]').forEach(element => { element.innerHTML = runStatusMarkup(); });
  }
  function handleHistoryPage(event) {
    const button = event.target.closest('[data-history-page]');
    if (!button || button.disabled) return;
    const page = Number(button.dataset.page);
    if (!Number.isInteger(page) || page < 1) return;
    historyPages[button.dataset.historyPage] = page;
    if (['ai', 'manual', 'companies'].includes(button.dataset.historyPage)) renderBlocked();
    else if (button.dataset.historyPage === 'contacted') renderContacted();
    else if (button.dataset.historyPage === 'records') renderRecords();
  }
  function refreshBlockedCount() {
    const count = blockedJobs.length + blockedCompanies.length + aiExcludedJobs().length;
    const badge = $('#blocked-count');
    if (badge) badge.textContent = String(count);
  }
  function renderBlocked() {
    const aiJobs = aiExcludedJobs();
    const manualJobs = blockedJobs;
    const ai = paginatedRows(aiJobs, 'ai', job => `<div class="rule-row"><span class="rule-type">AI 排除</span><span class="rule-content">${detailLink(job, 'AI 排除岗位')}<small>${escapeHtml(job.company || '公司信息待确认')}　${escapeHtml(job.salary || '薪资待确认')}</small><small>排除原因：${escapeHtml(job.reason || 'AI 判断为不匹配')}</small></span><button type="button" class="rule-action" data-block-action="restore-ai" data-block-key="${escapeHtml(blockedIdentity(job))}">恢复岗位</button></div>`, '暂时没有 AI 排除岗位');
    const manual = paginatedRows(manualJobs, 'manual', job => `<div class="rule-row"><span class="rule-type">手动屏蔽</span><span class="rule-content">${detailLink(job, '已屏蔽岗位')}<small>${escapeHtml(job.company || '公司信息待确认')}　${escapeHtml(job.salary || '薪资待确认')}</small></span><button type="button" class="rule-action" data-block-action="remove-job" data-block-key="${escapeHtml(blockedIdentity(job))}">移出屏蔽</button></div>`, '暂时没有手动屏蔽的岗位');
    const companies = paginatedRows(blockedCompanies, 'companies', company => `<div class="rule-row"><span class="rule-type">屏蔽公司</span><span class="rule-content"><strong>${escapeHtml(company)}</strong><small>该公司的职位将自动隐藏</small></span><button type="button" class="rule-action" data-block-action="remove-company" data-block-key="${escapeHtml(normalizeBlockedText(company))}">移出屏蔽</button></div>`, '暂时没有屏蔽的公司');
    $('[data-panel="blocked"]').innerHTML = `<div class="history-intro"><h2>屏蔽岗位</h2><p>这里保存的是历史排除记录，不是本轮搜索总量。AI 排除表示岗位与当前画像不匹配；相同岗位按 ID 更新，不设置固定条数上限。</p><div data-run-status>${runStatusMarkup()}</div></div><section class="list-section"><h3>AI 排除岗位 <span>${aiJobs.length}</span></h3><div class="rule-list">${ai.rows}</div>${ai.controls}</section><section class="list-section"><h3>手动屏蔽岗位 <span>${manualJobs.length}</span></h3><div class="rule-list">${manual.rows}</div>${manual.controls}</section><section class="list-section"><h3>屏蔽公司 <span>${blockedCompanies.length}</span></h3><div class="rule-list">${companies.rows}</div>${companies.controls}</section>`;
    refreshBlockedCount();
  }
  async function handleBlockedAction(event) {
    const button = event.target.closest('[data-block-action]');
    if (!button) return;
    const action = button.dataset.blockAction;
    const key = button.dataset.blockKey;
    button.disabled = true;
    try {
      if (action === 'remove-company') {
        const latest = await read(HIDDEN_COMPANIES_KEY);
        const companies = Array.isArray(latest) ? latest : [];
        await write({ [HIDDEN_COMPANIES_KEY]: companies.filter(company => normalizeBlockedText(company) !== key) });
        notice('已将公司移出屏蔽列表。');
      } else if (action === 'remove-job') {
        const latest = await read(DISMISSED_JOBS_KEY);
        const jobs = Array.isArray(latest) ? latest : [];
        await write({ [DISMISSED_JOBS_KEY]: jobs.filter(job => !blockedIdentityTokens(job).includes(key)) });
        notice('已将岗位移出手动屏蔽列表。');
      } else if (action === 'restore-ai') {
        const latest = await read(SCREENING_RECORDS_KEY);
        const records = Array.isArray(latest) ? latest : [];
        let restored = false;
        const updated = records.map(record => {
          if (!record || !blockedIdentityTokens(record).includes(key) || record.match !== false) return record;
          restored = true;
          return { ...record, match: true, manualOverride: true, reason: '用户从屏蔽岗位列表恢复（原 AI 排除）', restoredAt: Date.now() };
        });
        if (!restored) throw new Error('岗位记录已变化，请刷新页面后重试。');
        await write({ [SCREENING_RECORDS_KEY]: updated });
        notice('岗位已恢复，不会自动投递。');
      }
    } catch (error) {
      button.disabled = false;
      notice(error.message || '操作失败，请重试。', 'error');
    }
  }
  function communicationJobs() {
    const jobs = new Map(deliveryRecords.filter(job => job?.id).map(job => [job.id, job]));
    deliveredJobs.filter(job => job?.id).forEach(job => jobs.set(job.id, { ...(jobs.get(job.id) || {}), ...job, deliveryStatus: '已投递', deliveredAt: job.deliveredAt || jobs.get(job.id)?.deliveredAt }));
    return [...jobs.values()].sort((a, b) => Number(b.deliveredAt || b.updatedAt || b.queuedAt || 0) - Number(a.deliveredAt || a.updatedAt || a.queuedAt || 0));
  }
  function renderContacted() {
    const jobs = communicationJobs();
    const page = paginatedRows(jobs, 'contacted', job => {
      const deliveryStatus = job.deliveryStatus || '排队中';
      // 失败、超时、被停止或消费者页面关闭都会携带 error；无论当前状态文案如何，均在沟通记录中完整展示。
      const error = job.error ? `<small class="contact-status__error">${escapeHtml(job.error)}</small>` : '';
      const failed = Boolean(job.error) || /失败|超时|停止/.test(deliveryStatus);
      const retry = failed && job.detailUrl
        ? `<a class="contact-retry" href="${escapeHtml(job.detailUrl)}" target="_blank" rel="noopener noreferrer">打开岗位重试</a>`
        : '<span class="contact-retry is-empty">—</span>';
      return `<div class="contact-row"><span>${escapeHtml(job.company || '公司待确认')}</span><span>${detailLink(job, '岗位名称待确认')}</span><span>${escapeHtml(job.salary || '—')}</span><span class="contact-status ${deliveryStatus === '已投递' ? 'is-done' : failed ? 'is-error' : ''}" title="${escapeHtml(job.error || deliveryStatus)}"><b>${escapeHtml(deliveryStatus)}</b>${error}</span><time>${formatTime(job.deliveredAt || job.updatedAt || job.queuedAt)}</time><span>${retry}</span></div>`;
    }, '暂时没有进入投递队列的岗位');
    $('[data-panel="contacted"]').innerHTML = `<div class="history-intro"><h2>沟通记录</h2><p>数量统计进入投递/沟通队列的本地唯一岗位，包含排队中、已投递和失败记录；它不包含 AI 排除岗位，也不等于本轮搜索量。</p><div data-run-status>${runStatusMarkup()}</div></div><div class="contact-list"><div class="contact-row contact-head"><span>公司</span><span>岗位名称</span><span>薪资</span><span>投递状态</span><span>沟通时间</span><span>操作</span></div>${page.rows}</div>${page.controls}`;
  }
  function renderRecords() {
    const records = [...screeningRecords].sort((a, b) => Number(b.analyzedAt || 0) - Number(a.analyzedAt));
    const page = paginatedRows(records, 'records', record => {
      const profileNames = Array.isArray(record.matchedProfiles) ? record.matchedProfiles.map(profile => profile.name).join('、') : '';
      return `<article class="record-row ${record.match ? 'is-match' : ''}"><span class="record-status">${record.match ? '匹配' : '不匹配'}</span><div><strong>${record.detailUrl ? `<a href="${escapeHtml(record.detailUrl)}" target="_blank" rel="noopener noreferrer">${escapeHtml(record.title || '岗位名称待确认')}</a>` : escapeHtml(record.title || '岗位名称待确认')}</strong><small>${escapeHtml(record.company || '公司信息待确认')}　${escapeHtml(record.salary || '薪资待确认')}　版本 ${escapeHtml(record.screeningVersion || '历史')}${profileNames ? `　匹配岗位：${escapeHtml(profileNames)}` : ''}</small><p>${escapeHtml(record.reason || 'AI 未返回判断')}</p></div><time>${formatTime(record.analyzedAt)}</time></article>`;
    }, '还没有识别记录。回到 BOSS 岗位列表，点击“AI 精准投递”即可开始积累。');
    $('[data-panel="records"]').innerHTML = `<div class="history-intro"><h2>识别记录</h2><p>扫描按 BOSS 列表逐页读取；岗位按 ID 去重并更新，历史记录不设固定条数上限。</p><div data-run-status>${runStatusMarkup()}</div></div><div class="records-list">${page.rows}</div>${page.controls}`;
  }
  async function saveSettings(updates) { const current = await read(SETTINGS_KEY) || {}; const backup = Object.keys(current).length ? current : await read(SETTINGS_BACKUP_KEY) || {}; settings = { ...current, ...updates }; settings.profiles = normalizeProfiles(settings.profiles, settings).map(profile => ({ ...profile, version: profileVersion(profile, settings) })); settings.screeningVersion = screeningVersionFor(settings); await write({ [SETTINGS_KEY]: settings, [SETTINGS_BACKUP_KEY]: backup }); }
  async function init() {
    const [current, backup, jobs, companies, delivered, records, queued, runStatus] = await Promise.all([read(SETTINGS_KEY), read(SETTINGS_BACKUP_KEY), read(DISMISSED_JOBS_KEY), read(HIDDEN_COMPANIES_KEY), read(DELIVERED_KEY), read(SCREENING_RECORDS_KEY), read(DELIVERY_RECORDS_KEY), read(SEARCH_RUN_STATUS_KEY)]);
    const currentSettings = current && typeof current === 'object' && !Array.isArray(current) ? current : {};
    const backupSettings = backup && typeof backup === 'object' && !Array.isArray(backup) ? backup : {};
    const selectedSettings = Object.keys(currentSettings).length ? currentSettings : backupSettings;
    if (Object.prototype.hasOwnProperty.call(currentSettings, 'resumeImage') || Object.prototype.hasOwnProperty.call(backupSettings, 'resumeImage')) {
      const cleanCurrent = { ...currentSettings };
      const cleanBackup = { ...backupSettings };
      delete cleanCurrent.resumeImage;
      delete cleanBackup.resumeImage;
      await write({
        [SETTINGS_KEY]: Object.keys(currentSettings).length ? cleanCurrent : cleanBackup,
        [SETTINGS_BACKUP_KEY]: cleanBackup,
      });
    }
    settings = { apiUrl: DEFAULT_API_URL, model: DEFAULT_MODEL, ...selectedSettings };
    delete settings.resumeImage;
    if (!settings.apiUrl) settings.apiUrl = DEFAULT_API_URL;
    if (!settings.model) settings.model = DEFAULT_MODEL;
    settings.profiles = normalizeProfiles(settings.profiles, settings);
    // 兼容旧配置：每次加载设置页都按当前画像内容校正版本号，避免旧版本缺失或过期。
    settings.screeningVersion = screeningVersionFor(settings);
    blockedJobs = Array.isArray(jobs) ? jobs.map(job => typeof job === 'string' ? { id: job } : job) : [];
    blockedCompanies = Array.isArray(companies) ? companies : [];
    deliveredJobs = Array.isArray(delivered) ? delivered.map(job => typeof job === 'string' ? { id: job } : job) : [];
    deliveryRecords = Array.isArray(queued) ? queued.filter(Boolean) : [];
    screeningRecords = Array.isArray(records) ? records : [];
    latestRunStatus = runStatus && typeof runStatus === 'object' ? runStatus : null;
    searchConditions = normalizeConditions(settings.autoSearch);
    const storedSearchConditions = Array.isArray(settings.autoSearch?.conditions) ? settings.autoSearch.conditions : [];
    const hasLegacyRunTime = Object.prototype.hasOwnProperty.call(settings.autoSearch || {}, 'time') || storedSearchConditions.some(condition => Object.prototype.hasOwnProperty.call(condition || {}, 'time'));
    if (hasLegacyRunTime) await saveSettings({ autoSearch: { conditions: searchConditions } });
    const migration = mergeLegacySearchTermsIntoProfiles(settings.profiles, searchConditions, settings);
    if (migration.changed) {
      settings.profiles = migration.profiles;
      await saveSettings({ profiles: settings.profiles });
      const templates = groupSearchConditions(searchConditions);
      const roleTerms = profileSearchTerms(settings.profiles, settings);
      searchConditions = templates.flatMap(template => conditionsForTemplate(template, roleTerms));
      await saveAutoSearch(searchConditions);
    }
    refreshBlockedCount();
    $('#contacted-count').textContent = communicationJobs().length;
    renderBasic(); renderAutoSearch(); renderBlocked(); renderContacted(); renderRecords();
    $('[data-panel="blocked"]').addEventListener('click', event => { void handleBlockedAction(event); });
    document.querySelectorAll('.settings-panel').forEach(panel => panel.addEventListener('click', handleHistoryPage));
    void loadBossCityDirectory().then(loaded => { if (loaded) refreshTemplateCityPickers(); });
    document.querySelectorAll('[data-tab]').forEach(button => button.addEventListener('click', () => chooseTab(button.dataset.tab)));
    chooseTab(tabFromQuery);
  }
  chrome.storage.onChanged.addListener((changes = {}) => {
    let refresh = false;
    let blockedRefresh = false;
    if (changes[DISMISSED_JOBS_KEY]) {
      blockedJobs = Array.isArray(changes[DISMISSED_JOBS_KEY].newValue) ? changes[DISMISSED_JOBS_KEY].newValue.map(job => typeof job === 'string' ? { id: job } : job) : [];
      blockedRefresh = true;
    }
    if (changes[HIDDEN_COMPANIES_KEY]) {
      blockedCompanies = Array.isArray(changes[HIDDEN_COMPANIES_KEY].newValue) ? changes[HIDDEN_COMPANIES_KEY].newValue : [];
      blockedRefresh = true;
    }
    if (changes[SCREENING_RECORDS_KEY]) {
      screeningRecords = Array.isArray(changes[SCREENING_RECORDS_KEY].newValue) ? changes[SCREENING_RECORDS_KEY].newValue : [];
      blockedRefresh = true;
      renderRecords();
    }
    if (changes[DELIVERED_KEY]) {
      deliveredJobs = Array.isArray(changes[DELIVERED_KEY].newValue) ? changes[DELIVERED_KEY].newValue.map(job => typeof job === 'string' ? { id: job } : job) : [];
      refresh = true;
      blockedRefresh = true;
    }
    if (changes[DELIVERY_RECORDS_KEY]) {
      deliveryRecords = Array.isArray(changes[DELIVERY_RECORDS_KEY].newValue) ? changes[DELIVERY_RECORDS_KEY].newValue.filter(Boolean) : [];
      refresh = true;
      blockedRefresh = true;
    }
    if (changes[SEARCH_RUN_STATUS_KEY]) {
      latestRunStatus = changes[SEARCH_RUN_STATUS_KEY].newValue && typeof changes[SEARCH_RUN_STATUS_KEY].newValue === 'object' ? changes[SEARCH_RUN_STATUS_KEY].newValue : null;
      refreshRunStatusCards();
    }
    if (blockedRefresh) renderBlocked();
    if (refresh) {
      $('#contacted-count').textContent = communicationJobs().length;
      renderContacted();
    }
  });
  init().catch(error => notice(`设置页加载失败：${error.message}`, 'error'));
})();
