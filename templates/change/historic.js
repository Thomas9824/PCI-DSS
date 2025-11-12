document.addEventListener('DOMContentLoaded', () => {
    loadHistoric();
    setupFilters();
});

let allHistoricData = [];

async function loadHistoric() {
    const container = document.getElementById('historic-container');

    try {
        const response = await fetch('/api/historic');
        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Failed to load historic data');
        }

        allHistoricData = result.historic || [];

        if (allHistoricData.length === 0) {
            container.innerHTML = '<div class="no-historic">No historic data available</div>';
            return;
        }

        // Populate category filter
        populateCategoryFilter();

        // Display all data initially
        displayHistoric(allHistoricData);

    } catch (error) {
        console.error('Error loading historic data:', error);
        container.innerHTML = `<div class="loading">Error: ${escapeHtml(error.message)}</div>`;
    }
}

function populateCategoryFilter() {
    const categorySelect = document.getElementById('filter-category');
    const categories = [...new Set(allHistoricData.map(item => item.category))].sort();

    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        categorySelect.appendChild(option);
    });
}

function setupFilters() {
    const typeFilter = document.getElementById('filter-type');
    const categoryFilter = document.getElementById('filter-category');

    typeFilter.addEventListener('change', applyFilters);
    categoryFilter.addEventListener('change', applyFilters);
}

function applyFilters() {
    const typeFilter = document.getElementById('filter-type').value;
    const categoryFilter = document.getElementById('filter-category').value;

    let filtered = allHistoricData;

    // Filter by type
    if (typeFilter !== 'all') {
        filtered = filtered.filter(item => item.type === typeFilter);
    }

    // Filter by category
    if (categoryFilter !== 'all') {
        filtered = filtered.filter(item => item.category === categoryFilter);
    }

    displayHistoric(filtered);
}

function displayHistoric(data) {
    const container = document.getElementById('historic-container');

    if (data.length === 0) {
        container.innerHTML = '<div class="no-historic">No historic data matches the selected filters</div>';
        return;
    }

    // Sort by date (most recent first)
    const sorted = [...data].sort((a, b) => new Date(b.date) - new Date(a.date));

    container.innerHTML = sorted.map(item => createHistoricItem(item)).join('');
}

function createHistoricItem(item) {
    const date = new Date(item.date);
    const formattedDate = date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });

    const typeClass = `type-${item.type}`;
    const typeLabel = item.type.charAt(0).toUpperCase() + item.type.slice(1);

    let versionInfo = '';
    if (item.type === 'updated') {
        versionInfo = `<div class="historic-version"><span class="version-change">${escapeHtml(item.old_version)} → ${escapeHtml(item.new_version)}</span></div>`;
    } else {
        versionInfo = `<div class="historic-version">Version: ${escapeHtml(item.version)}</div>`;
    }

    return `
        <div class="historic-item">
            <div class="historic-header">
                <span class="historic-date">${formattedDate}</span>
                <span class="historic-type ${typeClass}">${typeLabel}</span>
            </div>
            <div class="historic-content">
                <div class="historic-name">${escapeHtml(item.name)}</div>
                <div class="historic-category">${escapeHtml(item.category)}</div>
                ${versionInfo}
            </div>
        </div>
    `;
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
