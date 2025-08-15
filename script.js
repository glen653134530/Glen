(function(){
  const $ = (sel, root=document) => root.querySelector(sel);
  const $$ = (sel, root=document) => Array.from(root.querySelectorAll(sel));

  const input = $('#qr-input');
  const btn = $('#generate-btn');
  const img = $('#qr-img');
  const skeleton = $('#qr-skeleton');
  const feedback = $('#feedback');

  const size = $('#size');
  const sizeValue = $('#size-value');
  const margin = $('#margin');
  const marginValue = $('#margin-value');
  const ecc = $('#ecc');

  const dlPng = $('#download-png');
  const dlSvg = $('#download-svg');
  const copyLink = $('#copy-link');
  const clearBtn = $('#clear');

  const historyList = $('#history-list');
  const historyClear = $('#history-clear');
  const themeToggle = $('#theme-toggle');

  const API = 'https://api.qrserver.com/v1/create-qr-code/';
  const MAX_HISTORY = 8;
  const STORAGE_KEY = 'qrpro.history';
  const THEME_KEY = 'qrpro.theme';

  function buildUrl({data, sz, m, ecl, fmt='png'}){
    const params = new URLSearchParams({
      data, size: `${sz}x${sz}`, margin: m, ecc: ecl
    });
    const base = fmt === 'svg' ? API.replace('create-qr-code', 'create-qr-code') : API;
    // service supports format via 'format' param
    if(fmt === 'svg') params.set('format', 'svg');
    return `${API}?${params.toString()}`;
  }

  function setSkeleton(on){
    skeleton.classList.toggle('hidden', !on);
  }

  function setFeedback(text, ok=true){
    feedback.textContent = text || '';
    feedback.style.color = ok ? 'var(--muted)' : '#e55353';
  }

  function saveHistory(entry){
    try{
      const list = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
      list.unshift(entry);
      while(list.length > MAX_HISTORY) list.pop();
      localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
      renderHistory();
    }catch(e){ /* ignore */ }
  }

  function timeAgo(ts){
    const diff = Math.max(1, Math.floor((Date.now()-ts)/1000));
    const m = 60, h = 3600, d = 86400;
    if(diff < m) return `${diff}s`;
    if(diff < h) return `${Math.floor(diff/m)}m`;
    if(diff < d) return `${Math.floor(diff/h)}h`;
    return `${Math.floor(diff/d)}j`;
  }

  function renderHistory(){
    const list = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    historyList.innerHTML = '';
    list.forEach(item => {
      const el = document.createElement('button');
      el.className = 'history-item';
      el.innerHTML = \`
        <img src="\${item.png}" alt="QR précédent">
        <div class="meta">
          <span class="text" title="\${item.text}">\${item.text}</span>
          <span class="time">\${timeAgo(item.ts)}</span>
        </div>\`;
      el.addEventListener('click', ()=>{
        input.value = item.text;
        generate(true);
      });
      historyList.appendChild(el);
    });
  }

  function updateControlsUI(){
    sizeValue.textContent = size.value + 'px';
    marginValue.textContent = margin.value;
  }

  function currentOpts(){
    return { sz: parseInt(size.value,10), m: parseInt(margin.value,10), ecl: ecc.value };
  }

  function isLikelyUrl(text){
    return /^https?:\/\//i.test(text) || /^[\w.-]+\.[a-z]{2,}(\/|$)/i.test(text);
  }

  function generate(fromHistory=false){
    const value = input.value.trim();
    if(!value){
      setFeedback('⚠️ Entrez un texte ou une URL.', false);
      return;
    }
    updateControlsUI();
    setFeedback('Génération en cours…');
    setSkeleton(true);
    const opts = currentOpts();
    const pngUrl = buildUrl({data: value, ...opts, fmt:'png'});
    const svgUrl = buildUrl({data: value, ...opts, fmt:'svg'});

    img.onload = ()=>{
      setSkeleton(false);
      setFeedback('Prêt ✅');
    };
    img.onerror = ()=>{
      setSkeleton(false);
      setFeedback('Erreur de génération. Réessayez.', false);
    };
    img.src = pngUrl;

    dlPng.href = pngUrl;
    dlSvg.href = svgUrl;

    copyLink.onclick = async ()=>{
      try{
        await navigator.clipboard.writeText(pngUrl);
        setFeedback('Lien copié 📋');
      }catch(e){
        setFeedback('Impossible de copier le lien.', false);
      }
    };

    if(!fromHistory){
      saveHistory({ text: value, png: pngUrl, svg: svgUrl, ts: Date.now() });
    }
  }

  // Events
  $('#qr-form').addEventListener('submit', (e)=>{ e.preventDefault(); generate(); });
  input.addEventListener('keydown', (e)=>{ if(e.key==='Enter'){ e.preventDefault(); generate(); }});
  size.addEventListener('input', ()=> updateControlsUI());
  margin.addEventListener('input', ()=> updateControlsUI());
  ecc.addEventListener('change', ()=> updateControlsUI());
  clearBtn.addEventListener('click', ()=>{ input.value=''; setFeedback(''); img.removeAttribute('src'); });

  historyClear.addEventListener('click', ()=>{
    localStorage.removeItem(STORAGE_KEY);
    renderHistory();
  });

  // Theme
  function applyTheme(theme){
    document.documentElement.dataset.theme = theme;
    if(theme === 'dark'){
      document.documentElement.style.colorScheme = 'dark';
    }else{
      document.documentElement.style.colorScheme = 'light';
    }
  }
  function initTheme(){
    const saved = localStorage.getItem(THEME_KEY);
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    applyTheme(saved || (prefersDark ? 'dark':'light'));
  }
  themeToggle.addEventListener('click', ()=>{
    const current = document.documentElement.dataset.theme || 'light';
    const next = current === 'light' ? 'dark' : 'light';
    localStorage.setItem(THEME_KEY, next);
    applyTheme(next);
  });

  // Init
  initTheme();
  updateControlsUI();
  renderHistory();
})();