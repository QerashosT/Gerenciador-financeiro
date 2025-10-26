// static/script.js - atualizado: conserta export PDF (com fallback), atualiza gráficos ao adicionar/importar/remover
document.addEventListener('DOMContentLoaded', () => {
  let expenses = [];
  let serverPrediction = null;
  window._charts = window._charts || {};

  const $ = id => document.getElementById(id);
  const money = v => Number(v || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  const safeNum = v => Number(String(v).replace(',', '.')) || 0;

  // Theme init
  (function initTheme(){
    const stored = localStorage.getItem('fp_theme_v1');
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = stored || (prefersDark ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', theme === 'dark' ? 'dark' : 'light');
    const tbtn = $('themeToggle'); if(tbtn) tbtn.textContent = theme === 'dark' ? '☀️' : '🌙';
  })();

  // theme toggle
  $('themeToggle')?.addEventListener('click', () => {
    const cur = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    const next = cur === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('fp_theme_v1', next);
    $('themeToggle').textContent = next === 'dark' ? '☀️' : '🌙';
    renderCharts(); // re-render to pick up color changes
  });

  // use server-provided initial state if present (fast)
  const init = window.INITIAL_STATE || {};
  if (Array.isArray(init.expenses) && init.expenses.length) expenses = init.expenses;
  if (init.prediction) serverPrediction = init.prediction;

  // --- Fetch helpers ---
  async function fetchExpenses() {
    try {
      const r = await fetch('/api/expenses');
      if (!r.ok) throw new Error('fetch failed');
      expenses = await r.json();
      return expenses;
    } catch (e) {
      console.warn('fetchExpenses error', e);
      return expenses;
    }
  }
  async function fetchPredictionFromServer() {
    try {
      const r = await fetch('/api/predict');
      if (!r.ok) return null;
      const p = await r.json();
      serverPrediction = p || null;
      return serverPrediction;
    } catch (e) {
      console.warn('fetchPredict error', e);
      return null;
    }
  }

  // --- date helpers ---
  function parseDate(s) {
    if (!s) return null;
    if (s.includes('-')) return new Date(s);
    if (s.includes('/')) {
      const [d,m,y] = s.split('/');
      if (d && m && y) return new Date(Number(y), Number(m)-1, Number(d));
    }
    const n = Number(s);
    if (!Number.isNaN(n)) return new Date(n);
    return new Date(s);
  }
  function formatDate(s) { const d = parseDate(s); return d ? d.toLocaleDateString() : s; }

  // --- grouping helpers ---
  function groupByMonth(items = expenses) {
    const map = new Map();
    items.forEach(e => {
      const d = parseDate(e.date);
      if (!d) return;
      const key = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`;
      const label = d.toLocaleDateString('pt-BR', { month:'short', year:'numeric' });
      const prev = map.get(key) || { key, label, amount: 0 };
      prev.amount += Number(e.amount || 0);
      map.set(key, prev);
    });
    return Array.from(map.values()).sort((a,b) => a.key.localeCompare(b.key));
  }
  function groupByCategory(items = expenses) {
    const map = new Map();
    items.forEach(e => { map.set(e.category, (map.get(e.category)||0) + Number(e.amount||0)); });
    return Array.from(map.entries()).map(([k,v]) => ({ name:k, value:v })).sort((a,b)=>b.value-a.value);
  }

  // --- charts lifecycle ---
  function destroyCharts(){ Object.values(window._charts).forEach(c=>c?.destroy && c.destroy()); window._charts = {}; }

  // simple linear regression (client-side) using visible months => next index
  function linearPredictFromMonths(months) {
    if (!months || months.length < 2) return null;
    const n = months.length;
    let sumX=0,sumY=0,sumXY=0,sumXX=0;
    for (let i=0;i<n;i++){
      const x=i; const y=Number(months[i].amount||0);
      sumX+=x; sumY+=y; sumXY+=x*y; sumXX+=x*x;
    }
    const denom = (n*sumXX - sumX*sumX);
    if (denom === 0) return null;
    const slope = (n*sumXY - sumX*sumY) / denom;
    const intercept = (sumY - slope*sumX) / n;
    const predicted = intercept + slope * n;
    return { predicted, slope, intercept };
  }

  function renderCharts(filtered = null) {
    const items = filtered || expenses;
    const months = groupByMonth(items);
    const categories = groupByCategory(items);

    const ctxPred = $('predictionChart')?.getContext('2d');
    const ctxCat = $('categoryChart')?.getContext('2d');
    const ctxMonth = $('monthlyChart')?.getContext('2d');
    const ctxTrend = $('trendChart')?.getContext('2d');
    if (!ctxPred) return;

    destroyCharts();

    const labelColor = getComputedStyle(document.documentElement).getPropertyValue('--text') || '#000';
    const commonOptions = {
      responsive:true, maintainAspectRatio:false,
      interaction:{ mode:'nearest', intersect:false },
      plugins:{
        tooltip:{
          position:'nearest',
          backgroundColor:getComputedStyle(document.documentElement).getPropertyValue('--surface'),
          titleColor: labelColor, bodyColor: labelColor,
          callbacks:{ label: ctx => `${ctx.dataset.label ? ctx.dataset.label+': ' : ''}${money(ctx.raw ?? ctx.parsed ?? 0)}` }
        },
        legend:{ display:false }
      },
      scales:{ x:{ ticks:{ color: labelColor } }, y:{ ticks:{ color: labelColor } } }
    };

    // prediction computed from visible months
    const predInfo = linearPredictFromMonths(months);
    const labelsPred = months.map(m=>m.label);
    const dataPred = months.map(m=>m.amount);
    if (predInfo && Number.isFinite(predInfo.predicted)) { labelsPred.push('Próx. mês'); dataPred.push(predInfo.predicted); }

    window._charts.prediction = new Chart(ctxPred, {
      type:'bar',
      data:{ labels: labelsPred, datasets:[{ label:'Valor', data: dataPred, backgroundColor: labelsPred.map((_,i)=> i===labelsPred.length-1 && predInfo ? '#ffb86b' : getComputedStyle(document.documentElement).getPropertyValue('--primary') + 'cc') }] },
      options: commonOptions
    });

    window._charts.category = new Chart(ctxCat, {
      type:'doughnut',
      data:{ labels: categories.map(c=>c.name), datasets:[{ data: categories.map(c=>c.value), backgroundColor:['#0b5fd7','#12b886','#f59e0b','#ef4444','#8b5cf6'] }] },
      options:{ ...commonOptions, plugins:{ ...commonOptions.plugins, legend:{ display:true, position:'bottom' } } }
    });

    window._charts.monthly = new Chart(ctxMonth, {
      type:'bar',
      data:{ labels: months.map(m=>m.label), datasets:[{ label:'Mensal', data: months.map(m=>m.amount), backgroundColor:getComputedStyle(document.documentElement).getPropertyValue('--primary') + 'cc' }] },
      options: commonOptions
    });

    window._charts.trend = new Chart(ctxTrend, {
      type:'line',
      data:{ labels: months.map(m=>m.label), datasets:[{ label:'Tendência', data: months.map(m=>m.amount), borderColor:getComputedStyle(document.documentElement).getPropertyValue('--accent'), backgroundColor:getComputedStyle(document.documentElement).getPropertyValue('--accent') + '33', fill:true, tension:0.35 }] },
      options: commonOptions
    });
  }

  // stats & list
  function updateStats(filtered=null) {
    const items = filtered || expenses;
    const total = items.reduce((s,e)=>s + Number(e.amount||0), 0);
    if ($('total')) $('total').textContent = money(total);
    const months = groupByMonth(items);
    const avg = months.length ? months.reduce((s,m)=>s+m.amount,0)/months.length : 0;
    if ($('media')) $('media').textContent = money(avg);
    const nowKey = `${new Date().getFullYear()}-${String(new Date().getMonth()+1).padStart(2,'0')}`;
    const thisMonth = months.find(m=>m.key===nowKey)?.amount || 0;
    if ($('mes')) $('mes').textContent = money(thisMonth);
    const lastTwo = months.slice(-2);
    let trend = 0;
    if (lastTwo.length===2 && lastTwo[0].amount>0) trend = ((lastTwo[1].amount - lastTwo[0].amount)/lastTwo[0].amount)*100;
    if ($('tendencia')) $('tendencia').textContent = (trend||0).toFixed(1) + '%';
  }

  function renderList(filtered=null) {
    const items = (filtered || expenses).slice().sort((a,b)=>new Date(b.date)-new Date(a.date));
    const ul = $('expenseList'); if(!ul) return;
    ul.innerHTML = '';
    items.forEach(e=>{
      const li = document.createElement('li');
      li.innerHTML = `<div class="meta"><div class="desc">${escapeHtml(e.description)}</div><div class="info">${escapeHtml(e.category)} • ${formatDate(e.date)}</div></div><div><strong>${money(e.amount)}</strong><button class="btn ghost remove" data-id="${e.id}" style="margin-left:10px">Remover</button></div>`;
      ul.appendChild(li);
    });
    ul.querySelectorAll('.remove').forEach(btn => btn.onclick = async ev => {
      const id = ev.currentTarget.dataset.id;
      btn.disabled = true;
      try {
        const res = await fetch(`/api/expenses/${id}`, { method:'DELETE' });
        if (!res.ok) throw new Error('delete failed');
        await refreshAll();
      } catch(err) { console.error(err); alert('Erro ao remover'); } finally { btn.disabled = false; }
    });
  }

  function escapeHtml(t=''){ return String(t).replace(/[&<>"']/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[s]); }

  // filters
  function renderFilters() {
    const months = groupByMonth();
    const fm = $('filterMonth');
    if (fm) { fm.innerHTML = '<option value="">Todos</option>'; months.forEach(m => fm.appendChild(new Option(m.label, m.key))); }
    const cats = Array.from(new Set(expenses.map(e=>e.category))).sort();
    const fc = $('filterCategory');
    if (fc) { fc.innerHTML = '<option value="">Todas</option>'; cats.forEach(c => fc.appendChild(new Option(c,c))); }
  }

  function applyFilters() {
    const mk = $('filterMonth')?.value || '';
    const cat = $('filterCategory')?.value || '';
    const q = $('searchInput')?.value.trim().toLowerCase() || '';
    let filtered = expenses.slice();
    if (mk) filtered = filtered.filter(e => { const d = parseDate(e.date); if (!d) return false; return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}` === mk; });
    if (cat) filtered = filtered.filter(e => e.category === cat);
    if (q) filtered = filtered.filter(e => (e.description + ' ' + e.category).toLowerCase().includes(q));
    updateStats(filtered); renderList(filtered); renderCharts(filtered);
  }

  // events
  $('filterMonth')?.addEventListener('change', applyFilters);
  $('filterCategory')?.addEventListener('change', applyFilters);
  $('searchInput')?.addEventListener('input', applyFilters);

  // Add expense (modal)
  $('modalExpenseForm')?.addEventListener('submit', async e => {
    e.preventDefault();
    const btn = e.submitter || $('modalExpenseForm').querySelector('button[type=submit]');
    if (btn) btn.disabled = true;
    try {
      const obj = { description: $('m_description').value.trim(), amount: safeNum($('m_amount').value), category: $('m_category').value.trim() || 'Geral', date: $('m_date').value || new Date().toISOString().slice(0,10) };
      if (!obj.description || !obj.amount || !obj.date) { alert('Preencha corretamente'); return; }
      const res = await fetch('/api/expenses', { method:'POST', headers:{ 'Content-Type':'application/json' }, body: JSON.stringify(obj) });
      if (!res.ok) throw new Error('save failed');
      await refreshAll();
      $('addModal').setAttribute('aria-hidden','true'); $('modalExpenseForm').reset();
    } catch(err) { console.error(err); alert('Erro ao adicionar despesa'); } finally { if (btn) btn.disabled = false; }
  });

  // modal toggles
  $('openAddModal')?.addEventListener('click', ()=>$('addModal')?.setAttribute('aria-hidden','false'));
  $('closeAddModal')?.addEventListener('click', ()=>$('addModal')?.setAttribute('aria-hidden','true'));
  $('cancelModal')?.addEventListener('click', ()=>$('addModal')?.setAttribute('aria-hidden','true'));

  // import CSV
  $('csvUpload')?.addEventListener('change', async ev => {
    const f = ev.target.files?.[0]; if (!f) return;
    try {
      const fd = new FormData(); fd.append('file', f);
      const res = await fetch('/api/import_csv', { method:'POST', body: fd });
      const data = await res.json();
      alert(`Importado: ${data.imported} itens`);
      await refreshAll();
    } catch(err){ console.error(err); alert('Erro ao importar CSV'); } finally { ev.target.value = ''; }
  });

  // export CSV
  $('exportCsv')?.addEventListener('click', async () => {
    try {
      const r = await fetch('/api/export_csv'); if (!r.ok) throw new Error('export fail');
      const blob = await r.blob(); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = 'despesas.csv'; a.click(); URL.revokeObjectURL(url);
    } catch(err){ console.error(err); alert('Erro ao exportar CSV'); }
  });

  // export PDF (client-side) with robust fallback to server /report
  $('exportPdf')?.addEventListener('click', async () => {
    const btn = $('exportPdf');
    btn.disabled = true; const prevText = btn.textContent; btn.textContent = 'Gerando...';
    try {
      // build filtered list (based on UI filters)
      const mk = $('filterMonth')?.value || ''; const cat = $('filterCategory')?.value || ''; const q = $('searchInput')?.value.trim().toLowerCase() || '';
      let filtered = expenses.slice();
      if (mk) filtered = filtered.filter(e => { const d = parseDate(e.date); if (!d) return false; return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}` === mk; });
      if (cat) filtered = filtered.filter(e => e.category === cat);
      if (q) filtered = filtered.filter(e => (e.description + ' ' + e.category).toLowerCase().includes(q));

      // create DOM with two tables
      const container = document.createElement('div'); container.style.padding='18px'; container.style.background='#fff'; container.style.color='#000';
      const h = document.createElement('h2'); h.textContent = 'Relatório Financeiro — Sumário por Categoria'; container.appendChild(h);

      const total_sum = filtered.reduce((s,e)=>s + Number(e.amount||0),0);
      const cat_map = {}; filtered.forEach(e=>{ cat_map[e.category] = (cat_map[e.category]||0) + Number(e.amount||0); });

      const tbl1 = document.createElement('table'); tbl1.style.width='100%'; tbl1.style.borderCollapse='collapse';
      tbl1.innerHTML = '<thead><tr><th style="padding:6px;background:#0b5fd7;color:#fff">Categoria</th><th style="padding:6px;background:#0b5fd7;color:#fff">Total (R$)</th><th style="padding:6px;background:#0b5fd7;color:#fff">% do Total</th></tr></thead>';
      const tb1 = document.createElement('tbody');
      Object.keys(cat_map).sort((a,b)=>cat_map[b]-cat_map[a]).forEach(cat=>{ const tr = document.createElement('tr'); tr.innerHTML = `<td style="padding:6px;border-bottom:1px solid #ddd">${cat}</td><td style="padding:6px;border-bottom:1px solid #ddd;text-align:right">${Number(cat_map[cat]).toLocaleString('pt-BR',{style:'currency',currency:'BRL'})}</td><td style="padding:6px;border-bottom:1px solid #ddd;text-align:right">${((cat_map[cat]/(total_sum||1))*100).toFixed(2)}%</td>`; tb1.appendChild(tr); });
      tbl1.appendChild(tb1); container.appendChild(tbl1);

      const h2 = document.createElement('h3'); h2.textContent = 'Detalhamento por Categoria'; h2.style.marginTop = '18px'; container.appendChild(h2);
      const tbl2 = document.createElement('table'); tbl2.style.width='100%'; tbl2.style.borderCollapse='collapse';
      tbl2.innerHTML = '<thead><tr><th style="padding:6px;background:#0b5fd7;color:#fff">Data</th><th style="padding:6px;background:#0b5fd7;color:#fff">Categoria</th><th style="padding:6px;background:#0b5fd7;color:#fff">Descrição</th><th style="padding:6px;background:#0b5fd7;color:#fff">Valor (R$)</th><th style="padding:6px;background:#0b5fd7;color:#fff">% da Categoria</th></tr></thead>';
      const tb2 = document.createElement('tbody');
      filtered.forEach(e=>{ const pct = (e.amount / (cat_map[e.category]||1) * 100) || 0; const tr = document.createElement('tr'); tr.innerHTML = `<td style="padding:6px;border-bottom:1px solid #ddd">${e.date}</td><td style="padding:6px;border-bottom:1px solid #ddd">${e.category}</td><td style="padding:6px;border-bottom:1px solid #ddd">${e.description}</td><td style="padding:6px;border-bottom:1px solid #ddd;text-align:right">${Number(e.amount).toLocaleString('pt-BR',{style:'currency',currency:'BRL'})}</td><td style="padding:6px;border-bottom:1px solid #ddd;text-align:right">${pct.toFixed(2)}%</td>`; tb2.appendChild(tr); });
      tbl2.appendChild(tb2); container.appendChild(tbl2);

      // try client-side html2canvas -> jsPDF
      try {
        const canvas = await html2canvas(container, { scale: 2, useCORS: true, logging: false });
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF({ unit:'px', format:[canvas.width, canvas.height] });
        pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 0, 0, canvas.width, canvas.height);
        pdf.save(`relatorio_detalhado_${new Date().toISOString().slice(0,10)}.pdf`);
      } catch (canvasErr) {
        console.warn('html2canvas/pdf client-side failed:', canvasErr);
        // fallback: open server side PDF /report
        window.open('/report', '_blank');
      }
    } catch (err) {
      console.error('Export PDF top-level error', err);
      alert('Erro ao gerar PDF. Fazendo download do relatório do servidor.');
      window.open('/report', '_blank');
    } finally {
      btn.disabled = false;
      btn.textContent = '📄 Exportar PDF';
    }
  });

  // refresh all (re-fetch server data and server prediction for compatibility)
  async function refreshAll() {
    await fetchExpenses();
    await fetchPredictionFromServer();
    renderFilters();
    updateStats();
    renderList();
    renderCharts();
  }

  // initial render
  updateStats(); renderList(); renderCharts();
  setTimeout(()=>refreshAll(), 200);
});
