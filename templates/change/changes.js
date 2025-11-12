// Initialize DotFlow and load initial data
let dotFlow;
document.addEventListener('DOMContentLoaded', () => {
    const buttonContent = document.querySelector('.btn-content');
    if (buttonContent) {
        dotFlow = new DotFlow(buttonContent, scraperAnimationFrames);
    }

    // Load initial data on page load
    loadInitialData();
});

async function loadInitialData() {
    try {
        const response = await fetch('/api/documents');
        const result = await response.json();

        if (result.success && result.documents && result.documents.length > 0) {
            const documents = result.documents;

            // Update last updated date
            const dates = documents
                .map(doc => doc.last_updated)
                .filter(date => date && date.trim() !== '');

            if (dates.length > 0) {
                const mostRecentDate = dates.reduce((latest, current) => {
                    const currentDate = new Date(current);
                    const latestDate = new Date(latest);
                    return currentDate > latestDate ? current : latest;
                });

                const formattedDate = new Date(mostRecentDate);
                const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
                document.getElementById('last-updated-date').textContent = formattedDate.toLocaleDateString('en-US', options);
            }

            // Populate the table
            const tbody = document.getElementById('documents-tbody');
            tbody.innerHTML = '';

            documents.forEach(doc => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${escapeHtml(doc.name || '')}</td>
                    <td>${escapeHtml(doc.version || '')}</td>
                    <td>${escapeHtml(doc.category || '')}</td>
                    <td><span class="languages-badge">${escapeHtml(doc.available_languages || 'EN')}</span></td>
                    <td>${escapeHtml(doc.last_updated || '')}</td>
                `;
                tbody.appendChild(row);
            });

            // Update statistics
            const categoryStats = getCategoryStats(documents);
            document.getElementById('total-docs').textContent = documents.length;
            document.getElementById('total-categories').textContent = Object.keys(categoryStats).length;

            const categoryBreakdown = document.getElementById('category-breakdown');
            categoryBreakdown.innerHTML = Object.entries(categoryStats).map(([category, count]) =>
                `<span class="category-stat">${category}: ${count}</span>`
            ).join('');
        }
    } catch (error) {
        console.error('Error loading initial data:', error);
        // Keep default values if error
    }
}

async function loadPCIDocuments() {
    const button = document.getElementById('load-data-btn');
    const tableContainer = document.getElementById('documents-table-container');
    const summary = document.getElementById('documents-summary');
    const tbody = document.getElementById('documents-tbody');

    try {
        // Start animation
        button.disabled = true;
        if (dotFlow) {
            dotFlow.start();
        }

        // Launch scraper in background
        const scraperResponse = await fetch('/api/run-scraper', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!scraperResponse.ok) {
            throw new Error(`HTTP ${scraperResponse.status}: ${scraperResponse.statusText}`);
        }

        const scraperResult = await scraperResponse.json();

        if (!scraperResult.success) {
            throw new Error(scraperResult.error || 'Failed to start scraper');
        }

        // Poll for scraper completion
        let statusCheckInterval;
        const checkStatus = async () => {
            try {
                const statusResponse = await fetch('/api/scraper-status');
                const status = await statusResponse.json();

                // Update progress message if available
                if (status.progress) {
                    console.log('Scraper status:', status.progress);
                }

                if (status.error) {
                    clearInterval(statusCheckInterval);
                    throw new Error(status.error);
                }

                if (status.completed && !status.running) {
                    clearInterval(statusCheckInterval);

                    // Load the results
                    const [dataResponse, changesResponse] = await Promise.all([
                        fetch('/api/documents'),
                        fetch('/api/changes')
                    ]);

                    const dataResult = await dataResponse.json();
                    const changesResult = await changesResponse.json();

                    if (!dataResult.success) {
                        throw new Error(dataResult.error || 'Failed to load documents');
                    }

                    const documents = dataResult.documents;
                    const changes = changesResult.success ? changesResult.changes : null;

                    // Display results
                    displayResults(documents, changes, tbody, summary);

                    // Reset button
                    if (dotFlow) {
                        dotFlow.reset();
                    }
                    button.disabled = false;
                }
            } catch (error) {
                clearInterval(statusCheckInterval);
                throw error;
            }
        };

        // Check status every 2 seconds
        statusCheckInterval = setInterval(checkStatus, 2000);

        // Initial check immediately
        await checkStatus();

    } catch (error) {
        console.error('Error running scraper or loading documents:', error);

        // Update status indicator to red for error
        const statusIndicator = document.getElementById('status-indicator');
        const statusMessage = document.getElementById('status-message');
        const statusCard = document.getElementById('status-card');

        if (statusIndicator && statusMessage) {
            statusIndicator.querySelector('svg').style.color = '#dc3545'; // Red
            statusMessage.innerHTML = `Error: ${escapeHtml(error.message)}`;
            statusCard.className = 'stat-card status-error'; // Red background
        }

        // Show error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'scraper-error';
        errorDiv.innerHTML = `
            <h3>❌ Error: ${escapeHtml(error.message)}</h3>
        `;

        if (summary) {
            summary.appendChild(errorDiv);
        } else {
            alert(`Error: ${error.message}`);
        }

        // Reset button
        if (dotFlow) {
            dotFlow.reset();
        }
        button.disabled = false;
    }
}

function displayResults(documents, changes, tbody, summary) {
    // Clear existing content
    tbody.innerHTML = '';

    // Populate the table
    documents.forEach(doc => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${escapeHtml(doc.name || '')}</td>
            <td>${escapeHtml(doc.version || '')}</td>
            <td>${escapeHtml(doc.category || '')}</td>
            <td><span class="languages-badge">${escapeHtml(doc.available_languages || 'EN')}</span></td>
            <td>${escapeHtml(doc.last_updated || '')}</td>
        `;
        tbody.appendChild(row);
    });

    // Clear summary section
    summary.innerHTML = '';

    // Update the statistics cards
    const summaryStats = document.getElementById('summary-stats');
    const categoryStats = getCategoryStats(documents);

    // Update total documents
    document.getElementById('total-docs').textContent = documents.length;

    // Update total categories
    document.getElementById('total-categories').textContent = Object.keys(categoryStats).length;

    // Update category breakdown
    const categoryBreakdown = document.getElementById('category-breakdown');
    categoryBreakdown.innerHTML = Object.entries(categoryStats).map(([category, count]) =>
        `<span class="category-stat">${category}: ${count}</span>`
    ).join('');

    // Update status message, indicator color, card background, and details
    const statusMessage = document.getElementById('status-message');
    const statusIndicator = document.getElementById('status-indicator');
    const statusDetails = document.getElementById('status-details');
    const statusCard = document.getElementById('status-card');

    if (changes) {
        const totalChanges = changes.new_documents.length +
                           changes.updated_versions.length +
                           changes.removed_documents.length;

        if (totalChanges > 0) {
            statusMessage.innerHTML = `Changes detected - ${totalChanges} modification(s)`;
            statusIndicator.querySelector('svg').style.color = '#ffa500'; // Orange
            statusCard.className = 'stat-card status-warning'; // Orange background

            // Build changes details HTML
            let detailsHTML = '';

            // Updated versions
            if (changes.updated_versions.length > 0) {
                changes.updated_versions.forEach(change => {
                    detailsHTML += `
                        <div class="status-change-item">
                            <div class="status-change-name">${escapeHtml(change.name)} (${escapeHtml(change.category)})</div>
                            <div class="status-change-version">${escapeHtml(change.old_version)} → ${escapeHtml(change.new_version)}</div>
                        </div>
                    `;
                });
            }

            // New documents
            if (changes.new_documents.length > 0) {
                changes.new_documents.forEach(doc => {
                    detailsHTML += `
                        <div class="status-change-item">
                            <div class="status-change-name">${escapeHtml(doc.name)} (${escapeHtml(doc.category)})</div>
                            <div class="status-change-version">New - ${escapeHtml(doc.version)}</div>
                        </div>
                    `;
                });
            }

            // Removed documents
            if (changes.removed_documents.length > 0) {
                changes.removed_documents.forEach(doc => {
                    detailsHTML += `
                        <div class="status-change-item">
                            <div class="status-change-name">${escapeHtml(doc.name)} (${escapeHtml(doc.category)})</div>
                            <div class="status-change-version">Removed - ${escapeHtml(doc.version)}</div>
                        </div>
                    `;
                });
            }

            statusDetails.innerHTML = detailsHTML;
        } else {
            statusMessage.innerHTML = `No changes detected - ${changes.unchanged_documents.length} documents unchanged`;
            statusIndicator.querySelector('svg').style.color = '#28a745'; // Green
            statusCard.className = 'stat-card status-success'; // Green background
            statusDetails.innerHTML = '';
        }
    }

    // Update last updated date
    const now = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById('last-updated-date').textContent = now.toLocaleDateString('en-US', options);
}

function parseCSV(csvText) {
    const lines = csvText.split('\n').filter(line => line.trim());
    if (lines.length === 0) return [];
    
    // Get headers from first line
    const headers = lines[0].split(',').map(header => header.trim());
    const documents = [];
    
    // Parse each data line
    for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;
        
        const values = parseCSVLine(line);
        if (values.length >= headers.length) {
            const doc = {};
            headers.forEach((header, index) => {
                doc[header] = values[index] ? values[index].trim() : '';
            });
            documents.push(doc);
        }
    }
    
    return documents;
}

function parseCSVLine(line) {
    const values = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        
        if (char === '"') {
            if (inQuotes && line[i + 1] === '"') {
                // Escaped quote
                current += '"';
                i++; // Skip next quote
            } else {
                // Toggle quote state
                inQuotes = !inQuotes;
            }
        } else if (char === ',' && !inQuotes) {
            values.push(current);
            current = '';
        } else {
            current += char;
        }
    }
    
    values.push(current); // Don't forget the last value
    return values;
}

function generateChangesDetails(changes) {
    let html = '';

    // New Documents
    if (changes.new_documents.length > 0) {
        html += `
            <div class="change-section">
                <h4>📄 New Documents (${changes.new_documents.length})</h4>
                <ul class="change-list">
                    ${changes.new_documents.map(doc => `
                        <li>
                            <strong>${escapeHtml(doc.name)}</strong>
                            (${escapeHtml(doc.category)})
                            - Version: ${escapeHtml(doc.version)}
                            ${doc.available_languages ? `- Languages: ${escapeHtml(doc.available_languages)}` : ''}
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
    }

    // Updated Versions
    if (changes.updated_versions.length > 0) {
        html += `
            <div class="change-section">
                <h4>🔄 Updated Versions (${changes.updated_versions.length})</h4>
                <ul class="change-list">
                    ${changes.updated_versions.map(change => `
                        <li>
                            <strong>${escapeHtml(change.name)}</strong>
                            (${escapeHtml(change.category)})
                            <br>
                            <span class="version-change">
                                ${escapeHtml(change.old_version)} → ${escapeHtml(change.new_version)}
                            </span>
                            ${change.old_languages !== change.new_languages ? `
                                <br>
                                <span class="language-change">
                                    Languages: ${escapeHtml(change.old_languages)} → ${escapeHtml(change.new_languages)}
                                </span>
                            ` : ''}
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
    }

    // Removed Documents
    if (changes.removed_documents.length > 0) {
        html += `
            <div class="change-section">
                <h4>🗑️ Removed Documents (${changes.removed_documents.length})</h4>
                <ul class="change-list">
                    ${changes.removed_documents.map(doc => `
                        <li>
                            <strong>${escapeHtml(doc.name)}</strong>
                            (${escapeHtml(doc.category)})
                            - Version: ${escapeHtml(doc.version)}
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
    }

    return html || '<p>No details available</p>';
}

function getCategoryStats(documents) {
    const stats = {};
    documents.forEach(doc => {
        const category = doc.category || 'Unknown';
        stats[category] = (stats[category] || 0) + 1;
    });
    return stats;
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}