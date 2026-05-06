const API_URL = 'http://localhost:8000';

// ── State ──────────────────────────────────────────────────────────
let selectedNiche = null;
let activeFilter  = '';
let allNiches     = [];

// ── Bootstrap ──────────────────────────────────────────────────────
async function init() {
    await loadNiches();
    renderFilterBar();
    refreshStats();
    loadOpportunities();

    // Poll stats & pending count every 8 seconds
    setInterval(refreshStats, 8000);
    setInterval(loadOpportunities, 15000);
}

// ── Load niches from API ────────────────────────────────────────────
async function loadNiches() {
    try {
        const res  = await fetch(`${API_URL}/niches`);
        const data = await res.json();
        allNiches  = data.niches || [];
    } catch {
        allNiches = ['Agro','Saúde','Beleza','Mecânica','Energia','Pet','Logística'];
    }
    renderNicheSelector();
}

function renderNicheSelector() {
    const container = document.getElementById('niche-selector');
    container.innerHTML = allNiches.map(n => `
        <button class="niche-btn" data-niche="${n}" id="niche-${n}">${n}</button>
    `).join('');

    container.querySelectorAll('.niche-btn').forEach(btn => {
        btn.addEventListener('click', () => selectNiche(btn.dataset.niche));
    });
}

function selectNiche(niche) {
    selectedNiche = niche;
    document.querySelectorAll('.niche-btn').forEach(b => b.classList.remove('selected'));
    document.getElementById(`niche-${niche}`)?.classList.add('selected');

    const btn = document.getElementById('search-btn');
    btn.disabled = false;
    document.getElementById('btn-text').textContent = `Pesquisar "${niche}"`;
}

// ── Search Trigger ──────────────────────────────────────────────────
document.getElementById('search-btn').addEventListener('click', triggerSearch);

async function triggerSearch() {
    if (!selectedNiche) return;

    const limit = parseInt(document.getElementById('limit-input').value) || 5;
    const btn   = document.getElementById('search-btn');

    btn.disabled = true;
    document.getElementById('btn-text').textContent = '🔍 Buscando...';
    showStatus(`🔍 Buscando ${limit} patentes no nicho "${selectedNiche}"...`, 'info');

    try {
        const res  = await fetch(`${API_URL}/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ niche: selectedNiche, limit }),
        });
        const data = await res.json();

        if (!res.ok) {
            showStatus(`❌ Erro: ${data.detail || 'Falha na busca.'}`, 'error');
            return;
        }

        const { inserted, skipped, demo_mode, error } = data;

        if (error) {
            showStatus(`❌ ${error}`, 'error');
            return;
        }

        showStatus(
            `✅ Busca concluída: ${inserted} patentes novas enfileiradas, ${skipped} já existentes ignoradas. O Worker analisará em breve.`,
            'success'
        );

        refreshStats();
    } catch (err) {
        showStatus(`❌ Erro de conexão com a API: ${err.message}`, 'error');
    } finally {
        btn.disabled = false;
        document.getElementById('btn-text').textContent = `Pesquisar "${selectedNiche}"`;
    }
}

function showStatus(msg, type) {
    const el = document.getElementById('search-status');
    el.textContent = msg;
    el.className = type;
}

// ── Filter Bar ─────────────────────────────────────────────────────
function renderFilterBar() {
    const bar = document.getElementById('filter-bar');
    // Keep "Todos" button, add one per niche
    const existing = bar.querySelector('[data-niche=""]');
    existing?.addEventListener('click', () => setFilter('', existing));

    allNiches.forEach(n => {
        const btn = document.createElement('button');
        btn.className = 'filter-btn';
        btn.dataset.niche = n;
        btn.textContent = n;
        btn.addEventListener('click', () => setFilter(n, btn));
        bar.appendChild(btn);
    });
}

function setFilter(niche, btnEl) {
    activeFilter = niche;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btnEl.classList.add('active');
    loadOpportunities();
}

// ── Stats ──────────────────────────────────────────────────────────
async function refreshStats() {
    try {
        const res  = await fetch(`${API_URL}/stats`);
        const data = await res.json();
        document.getElementById('total-count').textContent     = data.total;
        document.getElementById('processed-count').textContent = data.processed;
        document.getElementById('pending-count').textContent   = data.pending;
    } catch { /* silencioso */ }
}

// ── Opportunities ──────────────────────────────────────────────────
async function loadOpportunities() {
    const grid = document.getElementById('opportunities-grid');
    try {
        const url = activeFilter
            ? `${API_URL}/opportunities?niche=${encodeURIComponent(activeFilter)}`
            : `${API_URL}/opportunities`;

        const res  = await fetch(url);
        const data = await res.json();

        if (!data.length) {
            grid.innerHTML = `<div class="empty-state">Nenhuma patente analisada ainda.<br>Selecione um nicho e clique em "Pesquisar" para começar.</div>`;
            return;
        }

        const empty = grid.querySelector('.empty-state');
        if (empty) empty.remove();

        data.forEach(opp => {
            if (!document.getElementById(`card-${opp.id}`)) {
                grid.appendChild(createCard(opp));
            }
        });
    } catch (err) {
        grid.innerHTML = `<div class="loader">❌ Erro ao conectar com a API: ${err.message}</div>`;
    }
}

// ── Card Builder ───────────────────────────────────────────────────
function createCard(opp) {
    const card = document.createElement('div');
    card.className = 'card';
    card.id = `card-${opp.id}`;

    // Complexity bar
    const dots = Array.from({ length: 5 }, (_, i) =>
        `<span class="${i < opp.mvp_complexity ? 'filled' : ''}"></span>`
    ).join('');

    // Investment tier CSS class
    const tierMap = { 'Baixo': 'tier-baixo', 'Médio': 'tier-medio', 'Alto': 'tier-alto' };
    const tierClass = tierMap[opp.investment_tier] || '';

    const dateStr = opp.patent_date ? `Concedida: ${opp.patent_date}` : '';
    const sourceUrl = `https://europepmc.org/article/PAT/${opp.id}`;

    card.innerHTML = `
        <div class="card-header">
            <div class="card-title">${opp.title}</div>
            <div class="card-meta">
                ${opp.source_query ? `<span class="badge badge-niche">${opp.source_query}</span>` : ''}
                ${dateStr ? `<span class="badge badge-date">${dateStr}</span>` : ''}
            </div>
        </div>

        <div class="card-actions">
            <a href="${sourceUrl}" target="_blank" class="action-btn source-btn">Ver Fonte Original ↗</a>
        </div>

        <div class="analysis-box">
            <div class="label">Conceito de Negócio</div>
            <div class="content">${opp.concept || '—'}</div>
        </div>

        <div class="analysis-box">
            <div class="label">Insumos Modernos (2026)</div>
            <div class="content">${formatInputs(opp.modern_inputs)}</div>
        </div>

        <div class="details-grid">
            <div class="detail-item">
                <span class="label">Investimento</span>
                <span class="val ${tierClass}">${opp.investment_tier || '—'}</span>
            </div>
            <div class="detail-item">
                <span class="label">Complexidade MVP</span>
                <div class="complexity-bar">${dots}</div>
                <span class="val">${opp.mvp_complexity || '—'}/5</span>
            </div>
            <div class="detail-item">
                <span class="label">Time to Market</span>
                <span class="val">${opp.time_to_market || '—'}</span>
            </div>
            <div class="detail-item">
                <span class="label">Nicho</span>
                <span class="val">${opp.niche || opp.source_query || '—'}</span>
            </div>
        </div>
    `;
    return card;
}



function formatInputs(raw) {
    if (!raw) return '—';
    // Remove Postgres set notation { "a", "b" } if present
    const cleaned = raw.replace(/^\{|\}$/g, '').replace(/"/g, '').trim();
    const items = cleaned.split(',').map(s => s.trim()).filter(Boolean);
    if (items.length <= 1) return cleaned || '—';
    return items.map(i => `• ${i}`).join('<br>');
}

// ── Start ──────────────────────────────────────────────────────────
init();
