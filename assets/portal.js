(() => {
  'use strict';
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase('ja').replace(/\s+/g, ' ').trim();
  document.querySelectorAll('[data-filter]').forEach(root => {
    const input = root.querySelector('[data-search-input]');
    const select = root.querySelector('[data-category-input]');
    const items = Array.from(root.querySelectorAll('[data-search-item]'));
    const count = root.querySelector('[data-result-count]');
    const empty = root.querySelector('[data-no-results]');
    const pager = root.querySelector('[data-pager]');
    const size = Number(root.dataset.pageSize || 0);
    let currentPage = 0;
    const index = items.map(item => ({item, text: normalize(item.textContent), category: item.dataset.category}));
    function render(reset = false) {
      if (reset) currentPage = 0;
      const terms = normalize(input.value).split(' ').filter(Boolean);
      const selected = select ? select.value : '';
      const matches = index.filter(x => (!selected || x.category === selected) && terms.every(t => x.text.includes(t)));
      const pages = size ? Math.max(1, Math.ceil(matches.length / size)) : 1;
      currentPage = Math.min(currentPage, pages - 1);
      items.forEach(item => { item.hidden = true; });
      (size ? matches.slice(currentPage * size, (currentPage + 1) * size) : matches).forEach(x => { x.item.hidden = false; });
      count.textContent = `${matches.length}件 / 全${items.length}件`;
      empty.hidden = matches.length > 0;
      if (pager) {
        pager.hidden = pages <= 1;
        pager.querySelector('[data-page-status]').textContent = `${currentPage + 1} / ${pages}ページ`;
        pager.querySelector('[data-previous]').disabled = currentPage === 0;
        pager.querySelector('[data-next]').disabled = currentPage === pages - 1;
      }
    }
    input.addEventListener('input', () => render(true));
    if (select) select.addEventListener('change', () => render(true));
    if (pager) {
      pager.querySelector('[data-previous]').addEventListener('click', () => {currentPage--;render();root.scrollIntoView({block:'start'});});
      pager.querySelector('[data-next]').addEventListener('click', () => {currentPage++;render();root.scrollIntoView({block:'start'});});
    }
    const params = new URLSearchParams(location.search);
    if (params.has('q')) input.value = params.get('q');
    if (select && Array.from(select.options).some(x => x.value === params.get('category'))) select.value = params.get('category');
    render();
  });
  document.querySelectorAll('[data-checklist]').forEach(root => {
    const checks = Array.from(root.querySelectorAll('input[type=checkbox]'));
    const key = 'kikugawa-checklist-v1:' + root.dataset.checklist;
    const status = root.querySelector('[data-save-status]');
    let storageWorks = true;
    try {
      const stored = JSON.parse(localStorage.getItem(key) || '[]');
      if (Array.isArray(stored)) checks.forEach(c => { c.checked = stored.includes(c.id); });
    } catch {storageWorks = false;}
    const update = (save = true) => {
      root.querySelector('[data-check-progress]').textContent = `${checks.filter(c => c.checked).length} / ${checks.length} 完了`;
      if (save) {
        try {localStorage.setItem(key, JSON.stringify(checks.filter(c => c.checked).map(c => c.id)));}
        catch {storageWorks = false;}
      }
      status.textContent = storageWorks ? 'チェック状況はこのブラウザだけに保存されます。共有端末では終了後に「チェックを外す」を押してください。' : 'このブラウザでは保存できません。画面を閉じる前に印刷してください。';
    };
    checks.forEach(c => c.addEventListener('change', () => update()));
    root.querySelector('[data-check-reset]').addEventListener('click', () => {checks.forEach(c => {c.checked=false;});update();});
    root.querySelector('[data-print]').addEventListener('click', () => window.print());
    update(false);
  });
})();
