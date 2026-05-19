const API_URL = window.location.origin;

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

        // Clear grid first to support clean filtering and layout in-feed ads
        grid.innerHTML = '';

        let cardCount = 0;
        data.forEach(opp => {
            grid.appendChild(createCard(opp));
            cardCount++;

            // Inject a native premium ad card after every 3 patents!
            if (cardCount % 3 === 0 && cardCount < data.length) {
                grid.appendChild(createAdCard(Math.floor(cardCount / 3) - 1));
            }
        });
    } catch (err) {
        grid.innerHTML = `<div class="loader">❌ Erro ao conectar com a API: ${err.message}</div>`;
    }
}

// ── Utility: Anti-XSS ────────────────────────────────────────────────
function escapeHTML(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// ── Card Builder ───────────────────────────────────────────────────
function createCard(opp) {
    const card = document.createElement('div');
    card.className = 'card';
    card.id = `card-${escapeHTML(opp.id)}`;

    // Complexity bar
    const dots = Array.from({ length: 5 }, (_, i) =>
        `<span class="${i < opp.mvp_complexity ? 'filled' : ''}"></span>`
    ).join('');

    // Investment tier CSS class
    const tierMap = { 'Baixo': 'tier-baixo', 'Médio': 'tier-medio', 'Alto': 'tier-alto' };
    const tierClass = tierMap[opp.investment_tier] || '';

    const dateStr = opp.patent_date ? `Concedida: ${escapeHTML(opp.patent_date)}` : '';
    const sourceUrl = `https://europepmc.org/article/PAT/${encodeURIComponent(opp.id)}`;

    card.innerHTML = `
        <div class="card-header">
            <div class="card-title">${escapeHTML(opp.title)}</div>
            <div class="card-meta">
                ${opp.source_query ? `<span class="badge badge-niche">${escapeHTML(opp.source_query)}</span>` : ''}
                ${dateStr ? `<span class="badge badge-date">${dateStr}</span>` : ''}
            </div>
        </div>

        <div class="card-actions">
            <a href="${sourceUrl}" target="_blank" class="action-btn source-btn">Ver Fonte Original ↗</a>
        </div>

        <div class="analysis-box">
            <div class="label">Conceito de Negócio</div>
            <div class="content">${escapeHTML(opp.concept) || '—'}</div>
        </div>

        <div class="analysis-box">
            <div class="label">Insumos Modernos (2026)</div>
            <div class="content">${formatInputs(opp.modern_inputs)}</div>
        </div>

        <div class="details-grid">
            <div class="detail-item">
                <span class="label">Investimento</span>
                <span class="val ${tierClass}">${escapeHTML(opp.investment_tier) || '—'}</span>
            </div>
            <div class="detail-item">
                <span class="label">Complexidade MVP</span>
                <div class="complexity-bar">${dots}</div>
                <span class="val">${escapeHTML(opp.mvp_complexity) || '—'}/5</span>
            </div>
            <div class="detail-item">
                <span class="label">Time to Market</span>
                <span class="val">${escapeHTML(opp.time_to_market) || '—'}</span>
            </div>
            <div class="detail-item">
                <span class="label">Nicho</span>
                <span class="val">${escapeHTML(opp.niche) || escapeHTML(opp.source_query) || '—'}</span>
            </div>
        </div>
    `;
    return card;
}

// ── sponsoredAds (Advertising Monetization Demonstration) ─────────────────────────────
const sponsoredAds = [
    {
        title: "Infraestrutura de Nuvem para Startups e IA com Carlos Cloud",
        sponsor: "CarlosCloud Enterprise",
        description: "Hospede seu processamento de IA local na nuvem com servidores GPU Nvidia H100 sob demanda. Ganhe US$ 100 em créditos de boas-vindas para novos projetos.",
        tagline: "NUVEM & GPU",
        cta: "Resgatar US$ 100 Grátis",
        url: "#"
    },
    {
        title: "Consultoria Especializada em Registro de Patentes e Propriedade Intelectual",
        sponsor: "BR Patents Advogados",
        description: "Proteja suas inovações e garanta exclusividade de mercado com a maior equipe jurídica de propriedade intelectual do Brasil. Auditoria de patentes gratuita.",
        tagline: "JURÍDICO & IP",
        cta: "Falar com Especialista",
        url: "#"
    },
    {
        title: "Acelere seu MVP de Tecnologia com Desenvolvimento Inteligente",
        sponsor: "CarlosDev Labs",
        description: "Precisa de ajuda para tirar a sua ideia do papel? Nós construímos o seu MVP de SaaS ou Inteligência Artificial em tempo recorde com design e arquitetura premium.",
        tagline: "DESENVOLVIMENTO",
        cta: "Solicitar Orçamento",
        url: "#"
    }
];

function createAdCard(index) {
    const ad = sponsoredAds[index % sponsoredAds.length];
    const card = document.createElement('div');
    card.className = 'card ad-card';
    card.innerHTML = `
        <div class="card-header">
            <div class="card-title sponsored-title">${escapeHTML(ad.title)}</div>
            <div class="card-meta">
                <span class="badge badge-sponsored">PATROCINADO</span>
                <span class="badge badge-partner">${escapeHTML(ad.sponsor)}</span>
            </div>
        </div>
        <div class="analysis-box ad-body">
            <div class="label">Destaque do Parceiro</div>
            <div class="content">${escapeHTML(ad.description)}</div>
        </div>
        <div class="ad-actions">
            <span class="ad-tagline">${escapeHTML(ad.tagline)}</span>
            <a href="${escapeHTML(ad.url)}" class="ad-cta-btn">${escapeHTML(ad.cta)} →</a>
        </div>
    `;
    return card;
}

function formatInputs(raw) {
    if (!raw) return '—';
    // Remove Postgres set notation { "a", "b" } if present
    const cleaned = raw.replace(/^\{|\}$/g, '').replace(/"/g, '').trim();
    const items = cleaned.split(',').map(s => s.trim()).filter(Boolean);
    if (items.length <= 1) return escapeHTML(cleaned) || '—';
    return items.map(i => `• ${escapeHTML(i)}`).join('<br>');
}

// ── Start ──────────────────────────────────────────────────────────
init();
