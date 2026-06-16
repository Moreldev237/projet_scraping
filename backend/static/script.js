let currentPage = 1;
const itemsPerPage = 10;
let totalItems = 0;

// Charger les opportunités au démarrage
document.addEventListener('DOMContentLoaded', async () => {
    // Afficher le message de l'API sur l'UI
    try {
        const res = await fetch('/');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const el = document.getElementById('apiMessage');
        if (el && data && data.message) el.textContent = data.message;
    } catch (e) {
        const el = document.getElementById('apiMessage');
        if (el) el.textContent = 'Bienvenue sur le Scraper Opportunités Cameroun';
        console.warn('Impossible de charger le message API:', e);
    }

    loadOpportunites();
    loadStats();
});


function loadOpportunites(page = 1) {
    const searchQuery = document.getElementById('searchInput').value;
    const typeFilter = document.getElementById('typeFilter').value;
    const statutFilter = document.getElementById('statutFilter').value;
    
    let url = `/api/opportunites?skip=${(page-1)*itemsPerPage}&limit=${itemsPerPage}`;
    
    if (searchQuery) url += `&query=${encodeURIComponent(searchQuery)}`;
    if (typeFilter) url += `&type=${encodeURIComponent(typeFilter)}`;
    if (statutFilter) url += `&statut=${encodeURIComponent(statutFilter)}`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            renderOpportunites(data);
            updatePagination(page);
        })
        .catch(error => {
            console.error('Erreur:', error);
            document.getElementById('opportunitesList').innerHTML = 
                '<div class="loading">❌ Erreur lors du chargement des données</div>';
        });
}

function renderOpportunites(opportunites) {
    const container = document.getElementById('opportunitesList');
    
    if (!opportunites || opportunites.length === 0) {
        container.innerHTML = `
            <div class="loading">
                <span style="font-size: 3rem;">🔍</span>
                <p>Aucune opportunité trouvée</p>
                <p style="font-size: 0.9rem; color: #9ca3af;">Essayez de modifier vos filtres</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    opportunites.forEach(opp => {
        const typeBadge = getTypeBadge(opp.type);
        const statutBadge = getStatutBadge(opp.statut);
        const dateLimite = opp.date_limite ? new Date(opp.date_limite).toLocaleDateString('fr-FR') : 'Non spécifiée';
        
        html += `
            <div class="opportunite-card">
                <div class="opportunite-title">
                    <a href="${opp.source_url || '#'}" target="_blank">${opp.titre}</a>
                </div>
                <div class="opportunite-meta">
                    <span class="meta-tag">🏢 ${opp.organisation || 'Non spécifiée'}</span>
                    <span class="meta-tag">📍 ${opp.lieu || 'Cameroun'}</span>
                    <span class="meta-tag">📅 ${dateLimite}</span>
                    <span class="badge ${typeBadge.class}">${typeBadge.label}</span>
                    <span class="badge ${statutBadge.class}">${statutBadge.label}</span>
                    ${opp.niveau_etude ? `<span class="meta-tag">🎓 ${opp.niveau_etude}</span>` : ''}
                    ${opp.montant ? `<span class="meta-tag">💰 ${opp.montant}</span>` : ''}
                </div>
                ${opp.description ? `<div class="opportunite-description">${opp.description.substring(0, 200)}${opp.description.length > 200 ? '...' : ''}</div>` : ''}
                <div class="opportunite-source">
                    Source: ${opp.source}
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function getTypeBadge(type) {
    const types = {
        'emploi': { label: '💼 Emploi', class: 'badge-emploi' },
        'bourse_universitaire': { label: '🎓 Bourse Univ.', class: 'badge-bourse' },
        'bourse_scolaire': { label: '📚 Bourse Scol.', class: 'badge-bourse' },
        'stage': { label: '📋 Stage', class: 'badge-emploi' },
        'concours': { label: '🏆 Concours', class: 'badge-emploi' }
    };
    return types[type] || { label: type, class: 'badge-emploi' };
}

function getStatutBadge(statut) {
    const statuses = {
        'actif': { label: '✅ Actif', class: 'badge-actif' },
        'expire': { label: '⛔ Expiré', class: 'badge-expire' },
        'en_attente': { label: '⏳ En attente', class: 'badge-actif' }
    };
    return statuses[statut] || { label: statut, class: 'badge-actif' };
}

function loadStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('totalCount').textContent = data.total_opportunites || 0;
            document.getElementById('emploiCount').textContent = data.offres_emploi || 0;
            document.getElementById('bourseUnivCount').textContent = data.bourses_universitaires || 0;
            document.getElementById('bourseScolaireCount').textContent = data.bourses_scolaires || 0;
        })
        .catch(error => console.error('Erreur stats:', error));
}

function applyFilters() {
    currentPage = 1;
    loadOpportunites(currentPage);
}

function resetFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('typeFilter').value = '';
    document.getElementById('statutFilter').value = '';
    currentPage = 1;
    loadOpportunites(currentPage);
}

function updatePagination(page) {
    currentPage = page;
    document.getElementById('pageInfo').textContent = `Page ${page}`;
    document.getElementById('prevBtn').disabled = page <= 1;
    // La désactivation du bouton suivant se ferait avec le nombre total d'items
}

function previousPage() {
    if (currentPage > 1) {
        loadOpportunites(currentPage - 1);
    }
}

function nextPage() {
    loadOpportunites(currentPage + 1);
}

function scrapeAll() {
    const btn = event.target;
    btn.textContent = '⏳ Scraping en cours...';
    btn.disabled = true;
    
    fetch('/api/scrape/all', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            alert(data.message || 'Scraping démarré avec succès!');
            setTimeout(() => {
                loadOpportunites(currentPage);
                loadStats();
            }, 5000);
        })
        .catch(error => {
            alert('Erreur lors du scraping');
            console.error(error);
        })
        .finally(() => {
            btn.textContent = '🔄 Scraper toutes les sources';
            btn.disabled = false;
        });
}