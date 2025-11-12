// Global variable for DotFlow
let extractorDotFlow = null;

// Global variable for editable requirements
let currentRequirements = [];
let isEditMode = false;

// Initialize file upload functionality when page loads
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file-input');
    const dragDropZone = document.getElementById('drag-drop-zone');

    // File input change handler
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop handlers
    dragDropZone.addEventListener('click', () => fileInput.click());
    dragDropZone.addEventListener('dragover', handleDragOver);
    dragDropZone.addEventListener('dragleave', handleDragLeave);
    dragDropZone.addEventListener('drop', handleDrop);

    // Initialize DotFlow for the extract button
    const extractBtn = document.getElementById('extract-btn');
    if (extractBtn && typeof DotFlow !== 'undefined') {
        extractorDotFlow = new DotFlow(extractBtn, extractorAnimationFrames);
    }
});

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        displaySelectedFile(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    event.currentTarget.style.borderColor = '#0070f3';
    event.currentTarget.style.background = '#f0f8ff';
}

function handleDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();
    event.currentTarget.style.borderColor = '#ddd';
    event.currentTarget.style.background = '#f9f9f9';
}

function handleDrop(event) {
    event.preventDefault();
    event.stopPropagation();

    const dragDropZone = event.currentTarget;
    dragDropZone.style.borderColor = '#ddd';
    dragDropZone.style.background = '#f9f9f9';

    const files = event.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        if (file.type === 'application/pdf') {
            document.getElementById('file-input').files = files;
            displaySelectedFile(file);
        } else {
            alert('Please select a PDF file');
        }
    }
}

function displaySelectedFile(file) {
    const dragDropZone = document.getElementById('drag-drop-zone');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');

    // Hide drag drop zone, show file info
    dragDropZone.style.display = 'none';
    fileInfo.style.display = 'flex';

    // Display file details
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
}

function removeFile() {
    const dragDropZone = document.getElementById('drag-drop-zone');
    const fileInfo = document.getElementById('file-info');
    const fileInput = document.getElementById('file-input');

    // Clear file input
    fileInput.value = '';

    // Show drag drop zone, hide file info
    dragDropZone.style.display = 'block';
    fileInfo.style.display = 'none';
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

async function runPDFExtractor() {
    const button = document.getElementById('extract-btn');
    const btnText = button.querySelector('.btn-text');
    const languageSelect = document.getElementById('language-select');
    const statusSection = document.getElementById('status-section');
    const statusMessage = document.getElementById('status-message');
    const resultsSection = document.getElementById('results-section');
    const fileInput = document.getElementById('file-input');

    try {
        // Get selected language
        const language = languageSelect.value;

        // Check if a file is selected
        if (!fileInput.files || fileInput.files.length === 0) {
            throw new Error('Please upload a PDF file first');
        }

        // Update button state
        button.disabled = true;
        
        // Start dot animation
        if (extractorDotFlow) {
            extractorDotFlow.start();
        }

        // Hide status and previous results
        statusSection.style.display = 'none';
        resultsSection.style.display = 'none';

        // Prepare FormData with file and language
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('language', language);

        // Call the PDF extractor API
        const extractResponse = await fetch('/api/run-pdf-extractor', {
            method: 'POST',
            body: formData
        });
        
        if (!extractResponse.ok) {
            throw new Error(`HTTP ${extractResponse.status}: ${extractResponse.statusText}`);
        }
        
        const extractResult = await extractResponse.json();
        
        if (!extractResult.success) {
            throw new Error(extractResult.error || 'PDF extractor failed');
        }
        
        // Load the extraction results
        const resultsResponse = await fetch(`/api/pdf-extractor-results/${language}`);
        const resultsData = await resultsResponse.json();
        
        if (!resultsData.success) {
            throw new Error(resultsData.error || 'Failed to load results');
        }
        
        // Display results
        displayResults(resultsData, extractResult);
        
        // Hide status section on success
        statusSection.style.display = 'none';
        
        // Show results section
        resultsSection.style.display = 'block';
        
    } catch (error) {
        console.error('Error running PDF extractor:', error);
        
        // Show error status
        statusMessage.innerHTML = `
            <div class="status-error">
                <h3>❌ Extraction Failed</h3>
                <p>Error: ${escapeHtml(error.message)}</p>
            </div>
        `;
        
    } finally {
        // Reset button state
        button.disabled = false;
        
        // Stop dot animation
        if (extractorDotFlow) {
            extractorDotFlow.reset();
        }
    }
}

function displayResults(resultsData, extractResult) {
    const requirements = resultsData.requirements;
    const tbody = document.getElementById('requirements-tbody');
    const summary = document.getElementById('results-summary');
    const downloadButtons = document.getElementById('download-buttons');

    // Clear previous results
    tbody.innerHTML = '';

    // Store requirements globally for editing
    currentRequirements = [...requirements];
    
    // Add download and edit buttons
    const language = resultsData.language;
    downloadButtons.innerHTML = `
        <button id="edit-mode-btn" class="download-btn" onclick="toggleEditMode()">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M18.5 2.50001C18.8978 2.10219 19.4374 1.87869 20 1.87869C20.5626 1.87869 21.1022 2.10219 21.5 2.50001C21.8978 2.89784 22.1213 3.4374 22.1213 4.00001C22.1213 4.56262 21.8978 5.10219 21.5 5.50001L12 15L8 16L9 12L18.5 2.50001Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span id="edit-mode-text">Edit Mode</span>
        </button>
        <button id="save-changes-btn" class="download-btn" onclick="saveChanges()" style="display: none;">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 20.5304 3 20V4C3 3.46957 3.21071 2.96086 3.58579 2.58579C3.96086 2.21071 4.46957 2 5 2H16L21 7V20C21 20.5304 20.7893 21.0391 20.4142 21.4142C20.0391 21.7893 19.5304 22 19 22Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M17 21V13H7V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7 3V8H15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Save Changes
        </button>
        <button id="compare-btn" class="download-btn" onclick="compareRequirements()">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 5H7C5.89543 5 5 5.89543 5 7V19C5 20.1046 5.89543 21 7 21H9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M15 5H17C18.1046 5 19 5.89543 19 7V19C19 20.1046 18.1046 21 17 21H15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 9L15 12L12 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 9L9 12L12 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Compare
        </button>
        <button id="docx-with-tags-btn" class="download-btn" onclick="generateDocxWithTags()">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M14 2V8H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M9 13H15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M9 17H15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Docx with tags
        </button>
        <a href="/api/download-pdf-results/${language}/csv" class="download-btn" download>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15M7 10L12 15M12 15L17 10M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Download Original CSV
        </a>
    `;

    // Display summary
    const withTests = requirements.filter(req => req.tests && req.tests.trim().length > 0).length;
    const withGuidance = requirements.filter(req => req.guidance && req.guidance.trim().length > 0).length;

    summary.innerHTML = `
        <div class="summary-stats">
            <div class="stat-item">
                <span class="stat-number">${requirements.length}</span>
                <span class="stat-label">Total Requirements</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">${withTests}</span>
                <span class="stat-label">With Tests</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">${withGuidance}</span>
                <span class="stat-label">With Guidance</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">${resultsData.language}</span>
                <span class="stat-label">Language</span>
            </div>
        </div>
    `;
    
    // Populate table
    requirements.forEach((req, index) => {
        const row = document.createElement('tr');
        row.setAttribute('data-index', index);
        row.className = 'requirement-row';

        // Format tests - handle both string and array formats
        let testsText = '';
        if (req.tests) {
            if (typeof req.tests === 'string') {
                testsText = req.tests;
            } else if (Array.isArray(req.tests)) {
                testsText = req.tests.join('; ');
            }
        }

        row.innerHTML = `
            <td class="row-actions">
                <div class="action-buttons-container">
                    <button class="delete-row-btn" onclick="deleteRow(${index})" title="Delete row">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M3 6H5H21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M10 11V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M14 11V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                    <button class="insert-row-btn" onclick="insertRowAfter(${index})" title="Insert row below">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                </div>
            </td>
            <td class="req-num" data-field="req_num">${escapeHtml(req.req_num || '')}</td>
            <td class="req-text editable" data-field="text">${escapeHtml(req.text || '')}</td>
            <td class="req-tests editable" data-field="tests">${escapeHtml(testsText)}</td>
            <td class="req-guidance editable" data-field="guidance">${escapeHtml(req.guidance || '')}</td>
        `;

        tbody.appendChild(row);
    });
    
    // Update statistics tab
    updateStatistics(requirements, resultsData.language);
}

function updateStatistics(requirements, language) {
    const statsContent = document.getElementById('statistics-content');
    
    // Calculate detailed statistics
    const stats = {
        total: requirements.length,
        withTests: requirements.filter(req => req.tests && req.tests.toString().trim().length > 0).length,
        withGuidance: requirements.filter(req => req.guidance && req.guidance.trim().length > 0).length,
        language: language
    };
    
    // Group by main requirement number (1.x, 2.x, etc.)
    const byMainReq = {};
    requirements.forEach(req => {
        const mainNum = req.req_num.split('.')[0];
        if (!byMainReq[mainNum]) byMainReq[mainNum] = 0;
        byMainReq[mainNum]++;
    });
    
    // Calculate total tests
    let totalTests = 0;
    requirements.forEach(req => {
        if (req.tests) {
            if (typeof req.tests === 'string') {
                totalTests += req.tests.split(';').filter(test => test.trim().length > 0).length;
            } else if (Array.isArray(req.tests)) {
                totalTests += req.tests.length;
            }
        }
    });
    
    statsContent.innerHTML = `
        <div class="statistics-grid">
            <div class="stat-card">
                <h3>Overview</h3>
                <ul>
                    <li>Total Requirements: <strong>${stats.total}</strong></li>
                    <li>Requirements with Tests: <strong>${stats.withTests}</strong> (${((stats.withTests/stats.total)*100).toFixed(1)}%)</li>
                    <li>Requirements with Guidance: <strong>${stats.withGuidance}</strong> (${((stats.withGuidance/stats.total)*100).toFixed(1)}%)</li>
                    <li>Total Tests: <strong>${totalTests}</strong></li>
                    <li>Language: <strong>${getLanguageName(language)}</strong></li>
                </ul>
            </div>
            
            <div class="stat-card">
                <h3>Distribution by Main Requirement</h3>
                <ul>
                    ${Object.entries(byMainReq).sort((a,b) => parseInt(a[0]) - parseInt(b[0])).map(([main, count]) => 
                        `<li>Requirement ${main}: <strong>${count}</strong> sub-requirements</li>`
                    ).join('')}
                </ul>
            </div>
        </div>
    `;
}

function showTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + '-tab').classList.add('active');
    
    // Mark button as active
    event.target.classList.add('active');
}

function getLanguageName(code) {
    const languages = {
        'EN': 'English',
        'FR': 'French',
        'DE': 'German',
        'ES': 'Spanish',
        'PT': 'Portuguese'
    };
    return languages[code] || code;
}

function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function toggleEditMode() {
    isEditMode = !isEditMode;
    const editModeBtn = document.getElementById('edit-mode-btn');
    const editModeText = document.getElementById('edit-mode-text');
    const saveChangesBtn = document.getElementById('save-changes-btn');
    const addRowBtn = document.getElementById('add-row-btn');
    const editableCells = document.querySelectorAll('.editable');
    const reqNums = document.querySelectorAll('.req-num');

    if (isEditMode) {
        // Enable edit mode
        document.body.classList.add('edit-mode-active');

        editableCells.forEach(cell => {
            cell.contentEditable = 'true';
            cell.classList.add('editing');
        });

        // Make requirement numbers editable too
        reqNums.forEach(cell => {
            cell.contentEditable = 'true';
            cell.classList.add('editing');
        });

        editModeText.textContent = 'Exit Edit Mode';
        saveChangesBtn.style.display = 'inline-flex';
        if (addRowBtn) addRowBtn.style.display = 'inline-flex';
    } else {
        // Disable edit mode
        document.body.classList.remove('edit-mode-active');

        editableCells.forEach(cell => {
            cell.contentEditable = 'false';
            cell.classList.remove('editing');
        });

        reqNums.forEach(cell => {
            cell.contentEditable = 'false';
            cell.classList.remove('editing');
        });

        editModeText.textContent = 'Edit Mode';
        saveChangesBtn.style.display = 'none';
        if (addRowBtn) addRowBtn.style.display = 'none';

        // Sync changes back to currentRequirements
        syncChangesToData();
    }
}

function insertRowAfter(afterIndex) {
    // Sync current data first
    syncChangesToData();

    // Create new empty requirement
    const newRequirement = {
        req_num: 'NEW',
        text: '',
        tests: '',
        guidance: ''
    };

    // Insert into array at the correct position
    currentRequirements.splice(afterIndex + 1, 0, newRequirement);

    // Rebuild the table
    rebuildTable();

    // Auto-focus on the new row's first editable cell
    setTimeout(() => {
        const tbody = document.getElementById('requirements-tbody');
        const allRows = tbody.querySelectorAll('.requirement-row');
        const newRow = allRows[afterIndex + 1];
        if (newRow) {
            const firstEditableCell = newRow.querySelector('.req-num');
            if (firstEditableCell) {
                firstEditableCell.focus();
                // Select all text
                const range = document.createRange();
                range.selectNodeContents(firstEditableCell);
                const sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);
            }
        }
    }, 50);

    showNotification('New row inserted');
}

function deleteRow(rowIndex) {
    // Confirm deletion
    const req = currentRequirements[rowIndex];
    const reqId = req.req_num || 'this row';

    if (!confirm(`Delete requirement ${reqId}?`)) {
        return;
    }

    // Sync current data first
    syncChangesToData();

    // Remove from array
    currentRequirements.splice(rowIndex, 1);

    // Rebuild table
    rebuildTable();

    showNotification(`Row ${reqId} deleted`);
}

function rebuildTable() {
    const tbody = document.getElementById('requirements-tbody');
    tbody.innerHTML = '';

    currentRequirements.forEach((req, index) => {
        const row = document.createElement('tr');
        row.setAttribute('data-index', index);
        row.className = 'requirement-row';

        // Format tests
        let testsText = '';
        if (req.tests) {
            if (typeof req.tests === 'string') {
                testsText = req.tests;
            } else if (Array.isArray(req.tests)) {
                testsText = req.tests.join('; ');
            }
        }

        row.innerHTML = `
            <td class="row-actions">
                <div class="action-buttons-container">
                    <button class="delete-row-btn" onclick="deleteRow(${index})" title="Delete row">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M3 6H5H21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M10 11V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M14 11V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                    <button class="insert-row-btn" onclick="insertRowAfter(${index})" title="Insert row below">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                </div>
            </td>
            <td class="req-num" data-field="req_num">${escapeHtml(req.req_num || '')}</td>
            <td class="req-text editable" data-field="text">${escapeHtml(req.text || '')}</td>
            <td class="req-tests editable" data-field="tests">${escapeHtml(testsText)}</td>
            <td class="req-guidance editable" data-field="guidance">${escapeHtml(req.guidance || '')}</td>
        `;

        tbody.appendChild(row);
    });

    // Reapply edit mode if active
    if (isEditMode) {
        const editableCells = document.querySelectorAll('.editable');
        const reqNums = document.querySelectorAll('.req-num');

        editableCells.forEach(cell => {
            cell.contentEditable = 'true';
            cell.classList.add('editing');
        });

        reqNums.forEach(cell => {
            cell.contentEditable = 'true';
            cell.classList.add('editing');
        });
    }
}

function syncChangesToData() {
    const rows = document.querySelectorAll('#requirements-tbody .requirement-row');

    // Rebuild the array to match the current table order
    const updatedRequirements = [];

    rows.forEach(row => {
        const reqNumCell = row.querySelector('[data-field="req_num"]');
        const textCell = row.querySelector('[data-field="text"]');
        const testsCell = row.querySelector('[data-field="tests"]');
        const guidanceCell = row.querySelector('[data-field="guidance"]');

        updatedRequirements.push({
            req_num: reqNumCell.textContent.trim(),
            text: textCell.textContent.trim(),
            tests: testsCell.textContent.trim(),
            guidance: guidanceCell.textContent.trim()
        });
    });

    // Update the global array
    currentRequirements = updatedRequirements;
}

function saveChanges() {
    // Sync changes first
    syncChangesToData();
    
    // Convert to CSV
    const csvContent = convertToCSV(currentRequirements);
    
    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', 'pci_requirements_edited.csv');
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Show success message
    showNotification('Changes saved successfully! CSV downloaded.');
}

function convertToCSV(data) {
    const headers = ['id', 'text', 'tests', 'guidance'];
    const csvRows = [];
    
    // Add header row
    csvRows.push(headers.join(','));
    
    // Add data rows
    data.forEach(req => {
        const row = [
            escapeCSV(req.req_num || req.id || ''),
            escapeCSV(req.text || ''),
            escapeCSV(req.tests || ''),
            escapeCSV(req.guidance || '')
        ];
        csvRows.push(row.join(','));
    });
    
    return csvRows.join('\n');
}

function escapeCSV(str) {
    if (str === null || str === undefined) return '';
    str = String(str);

    // If the string contains comma, newline or quote, wrap it in quotes
    if (str.includes(',') || str.includes('\n') || str.includes('"')) {
        // Escape quotes by doubling them
        str = str.replace(/"/g, '""');
        return `"${str}"`;
    }
    return str;
}

async function generateDocxWithTags() {
    try {
        const button = document.getElementById('docx-with-tags-btn');
        const languageSelect = document.getElementById('language-select');
        const language = languageSelect.value;

        // Sync current changes first
        syncChangesToData();

        // Extract all IDs from current requirements with filters
        const idList = currentRequirements
            .filter(req => {
                const id = req.req_num || req.id || '';
                const text = req.text || '';

                // Skip if ID is empty
                if (id.trim() === '') return false;

                // Skip if ID contains only numbers and dots (like 1.1, 2.9, 5.5, etc.)
                // Pattern: one or more digits, optionally followed by dot and more digits
                if (/^\d+(\.\d+)?$/.test(id.trim())) return false;

                // Skip if text contains the specific phrase about issuers or service providers
                if (text.includes('Exigences supplémentaires pour les émetteurs') ||
                    text.includes('entreprises qui prennent en charge les services d\'émission') ||
                    text.includes('stockent les données d\'authentification sensibles') ||
                    text.includes('Exigences supplémentaires pour les prestataires de services uniquement') ||
                    text.includes('Exigences supplémentaires uniquement pour les prestataires de services mutualisés') ||
                    text.includes('Cette exigence est spécifique à l\'Approche Personnalisée') ||
                    text.includes('ne s\'applique pas aux entités remplissant un Questionnaire d\'Auto-Évaluation') ||
                    text.includes('ne s\'applique pas aux entités remplissant un Questionnaire d\'Auto -Évaluation')) {
                    return false;
                }

                return true;
            })
            .map(req => req.req_num || req.id || '');

        // Disable button during processing
        button.disabled = true;
        button.innerHTML = '<span>Processing...</span>';

        // Hide status container at start
        hideDocxStatus();

        showNotification(`Extracted ${idList.length} requirement IDs. Starting DOCX generation...`);

        // Call backend API to generate DOCX with tags
        const response = await fetch('/api/generate-docx-with-tags', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                requirement_ids: idList,
                language: language
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();

        if (!result.success) {
            // Show error status
            showDocxStatus('error', result.error || 'Failed to generate DOCX with tags', result.details);
            throw new Error(result.error || 'Failed to generate DOCX with tags');
        }

        // Analyze the result to determine status
        const stats = result.stats || {};
        const totalRequirements = stats.total_requirements || 0;
        const transformedVariants = stats.transformed_variants || 0;
        const fieldsReplaced = stats.tags_found || 0;
        const unreplacedFields = stats.unreplaced_fields || 0;
        const totalFieldsInDoc = stats.total_fields_in_document || fieldsReplaced;
        const hasError = stats.error_step || stats.error_message;

        let statusType = 'success';
        let statusMessage = 'DOCX with tags generated successfully!';
        let statusDetails = '';

        // Check for errors first (highest priority)
        if (hasError) {
            statusType = 'error';
            const errorStep = stats.error_step || 'unknown';
            const errorMsg = stats.error_message || 'An unknown error occurred';
            statusMessage = 'Error during DOCX generation';

            let stepName = errorStep;
            if (errorStep === 'transformation') stepName = 'ID Transformation';
            else if (errorStep === 'download') stepName = 'DOCX Download';
            else if (errorStep === 'replacement') stepName = 'Form Field Replacement';

            statusDetails = `<p style="margin-bottom: 0.75rem;"><strong>Failed at step:</strong> ${stepName}</p>
                <p style="margin-bottom: 0.75rem;"><strong>Error:</strong> ${errorMsg}</p>
                <ul>
                    <li>Original requirements: ${totalRequirements}</li>
                    <li>Transformed variants: ${transformedVariants || 'N/A'}</li>
                </ul>
                <p style="margin-top: 0.75rem; color: #e74c3c;">✗ The DOCX generation process failed. Please check the console logs for more details or try again.</p>`;
        }
        // Determine status based on unreplaced fields
        else if (unreplacedFields > 0) {
            // Warning: Not enough tags to fill all fields in document
            statusType = 'warning';
            statusMessage = 'Not enough tags to fill all document fields';
            const coverage = totalFieldsInDoc > 0 ? Math.round((fieldsReplaced / totalFieldsInDoc) * 100) : 0;
            const missingIds = stats.missing_ids || Math.floor(unreplacedFields / 5);

            statusDetails = `<ul>
                <li>Original requirements: ${totalRequirements}</li>
                <li>Transformed variants (tags): ${transformedVariants}</li>
                <li>Total fields in tables with IDs: ${totalFieldsInDoc}</li>
                <li>Fields replaced: ${fieldsReplaced}</li>
                <li>Fields NOT replaced: ${unreplacedFields}</li>
                <li><strong>Missing requirement IDs: ~${missingIds}</strong> (${unreplacedFields} fields ÷ 5 variants per ID)</li>
                <li>Coverage: ${coverage}%</li>
            </ul>
            <p style="margin-top: 0.75rem; color: #ff9800;"><strong>⚠ Action required:</strong> You need to add approximately <strong>${missingIds} more requirement IDs</strong> to the extraction results table above.</p>
            <p style="margin-top: 0.5rem; color: #999;">The DOCX template has more form fields than available tags (each requirement ID generates 5 tag variants: a, b, c, d, e).</p>`;
        } else if (fieldsReplaced < transformedVariants) {
            // Warning: Some variants were not used (document has fewer fields than tags)
            statusType = 'warning';
            statusMessage = 'Document has fewer fields than available tags';
            const unusedTags = transformedVariants - fieldsReplaced;
            statusDetails = `<ul>
                <li>Original requirements: ${totalRequirements}</li>
                <li>Transformed variants (tags): ${transformedVariants}</li>
                <li>Total fields in tables with IDs: ${totalFieldsInDoc}</li>
                <li>Fields replaced: ${fieldsReplaced}</li>
                <li>Unused tags: ${unusedTags}</li>
            </ul>
            <p style="margin-top: 0.5rem; color: #ff9800;">The DOCX template has fewer form fields than available tags. All document fields were filled, but ${unusedTags} tags were not used.</p>`;
        } else {
            // Success: Perfect match
            statusMessage = 'Perfect match! All fields filled successfully';
            statusDetails = `<ul>
                <li>Original requirements: ${totalRequirements}</li>
                <li>Transformed variants: ${transformedVariants}</li>
                <li>Total fields in tables with IDs: ${totalFieldsInDoc}</li>
                <li>Form fields replaced: ${fieldsReplaced}</li>
                <li>Coverage: 100%</li>
            </ul>
            <p style="margin-top: 0.5rem; color: #2ecc71;">✓ All document fields have been filled with the available tags.</p>`;
        }

        // Show status
        showDocxStatus(statusType, statusMessage, statusDetails);

        // Download the generated DOCX file
        if (result.download_url) {
            showNotification('DOCX with tags generated successfully! Downloading...');

            // Create download link
            const downloadLink = document.createElement('a');
            downloadLink.href = result.download_url;
            downloadLink.download = result.filename || 'SAQ_tagged.docx';
            downloadLink.style.display = 'none';

            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);

            showNotification(`Success! Downloaded: ${result.filename}`);
        } else {
            showNotification('DOCX with tags generated successfully!');
        }

    } catch (error) {
        console.error('Error generating DOCX with tags:', error);
        showNotification('Error: ' + error.message);

        // Show error status if not already shown
        if (!document.getElementById('docx-status-container').style.display ||
            document.getElementById('docx-status-container').style.display === 'none') {
            showDocxStatus('error', 'Error during DOCX generation',
                `<p>${error.message}</p>
                <p style="margin-top: 0.5rem;">Please check the console for more details or try again.</p>`);
        }
    } finally {
        // Reset button
        const button = document.getElementById('docx-with-tags-btn');
        if (button) {
            button.disabled = false;
            button.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M14 2V8H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M9 13H15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M9 17H15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Docx with tags
            `;
        }
    }
}

function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Update reference with current data
async function updateReference() {
    try {
        // Sync current changes
        syncChangesToData();

        const languageSelect = document.getElementById('language-select');
        const language = languageSelect.value;

        const confirmed = confirm('Update the reference with the current data (including all edits)?');
        if (!confirmed) return;

        // Send current requirements to save as reference
        const response = await fetch(`/api/save-reference/${language}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                current_requirements: currentRequirements
            })
        });

        const result = await response.json();

        if (result.success) {
            showNotification('Reference updated successfully!');
            // Re-run comparison to show updated results
            await compareRequirements();
        } else {
            throw new Error(result.error || 'Failed to update reference');
        }
    } catch (error) {
        console.error('Error updating reference:', error);
        showNotification('Error: ' + error.message);
    }
}

// Trigger file input for importing reference
function triggerImportReference() {
    const fileInput = document.getElementById('import-reference-input');
    fileInput.click();
}

// Import reference from CSV file
async function importReferenceFile(event) {
    const file = event.target.files[0];
    if (!file) return;

    try {
        const languageSelect = document.getElementById('language-select');
        const language = languageSelect.value;

        // Create FormData to send file
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`/api/import-reference/${language}`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            showNotification('Reference imported successfully!');
            // Re-run comparison to show updated results
            await compareRequirements();
        } else {
            throw new Error(result.error || 'Failed to import reference');
        }
    } catch (error) {
        console.error('Error importing reference:', error);
        showNotification('Error: ' + error.message);
    } finally {
        // Reset file input
        event.target.value = '';
    }
}

// Comparison functionality
async function compareRequirements() {
    const compareBtn = document.getElementById('compare-btn');
    const summarySection = document.getElementById('results-summary');

    try {
        // Sync current changes first
        syncChangesToData();

        // Get the current language
        const languageSelect = document.getElementById('language-select');
        const language = languageSelect.value;

        // Disable button during comparison
        compareBtn.disabled = true;
        compareBtn.textContent = 'Comparing...';

        // Send the current requirements data (including edits) for comparison
        const response = await fetch(`/api/compare-requirements/${language}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                current_requirements: currentRequirements
            })
        });

        const result = await response.json();

        if (!result.success) {
            // Check if it's because there's no reference
            if (result.has_reference === false) {
                // Ask user if they want to save current as reference
                const saveRef = confirm('No reference found for this language. Would you like to save the current export as reference?');
                if (saveRef) {
                    await saveAsReference(language);
                } else {
                    showNotification('Comparison cancelled. No reference available.');
                }
                return;
            }

            throw new Error(result.error || 'Comparison failed');
        }

        // Display comparison results
        displayComparisonResults(result.comparison, summarySection);

        showNotification('Comparison completed successfully!');

    } catch (error) {
        console.error('Error comparing requirements:', error);
        showNotification('Error: ' + error.message);
    } finally {
        // Reset button
        compareBtn.disabled = false;
        compareBtn.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 5H7C5.89543 5 5 5.89543 5 7V19C5 20.1046 5.89543 21 7 21H9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M15 5H17C18.1046 5 19 5.89543 19 7V19C19 20.1046 18.1046 21 17 21H15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 9L15 12L12 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 9L9 12L12 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Compare
        `;
    }
}

async function saveAsReference(language) {
    try {
        const response = await fetch(`/api/save-reference/${language}`, {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            showNotification('Reference saved successfully! You can now compare future exports.');
        } else {
            throw new Error(result.error || 'Failed to save reference');
        }
    } catch (error) {
        console.error('Error saving reference:', error);
        showNotification('Error saving reference: ' + error.message);
    }
}

function displayComparisonResults(comparison, summarySection) {
    // Check if comparison block already exists
    let comparisonBlock = document.getElementById('comparison-block');

    if (!comparisonBlock) {
        // Create new comparison block
        comparisonBlock = document.createElement('div');
        comparisonBlock.id = 'comparison-block';
        comparisonBlock.className = 'comparison-block';

        // Insert after summary stats
        summarySection.insertAdjacentElement('afterend', comparisonBlock);
    }

    // Build the comparison HTML with improved design
    const noChanges = comparison.added_count === 0 && comparison.removed_count === 0;

    // Build stats items similar to summary stats
    const statsItems = [];
    if (comparison.added_count > 0) {
        statsItems.push(`
            <div class="stat-item">
                <span class="stat-number added-color">${comparison.added_count}</span>
                <span class="stat-label">Added</span>
            </div>
        `);
    }
    if (comparison.removed_count > 0) {
        statsItems.push(`
            <div class="stat-item">
                <span class="stat-number removed-color">${comparison.removed_count}</span>
                <span class="stat-label">Removed</span>
            </div>
        `);
    }
    statsItems.push(`
        <div class="stat-item">
            <span class="stat-number">${comparison.unchanged_count}</span>
            <span class="stat-label">Unchanged</span>
        </div>
    `);

    const addedHtml = comparison.added_count > 0 ? `
        <div class="comparison-detail-section">
            <h4>Added Requirements</h4>
            <div class="id-list">
                ${comparison.added.map(id => `<span class="id-badge added">${escapeHtml(id)}</span>`).join('')}
            </div>
        </div>
    ` : '';

    const removedHtml = comparison.removed_count > 0 ? `
        <div class="comparison-detail-section">
            <h4>Removed Requirements</h4>
            <div class="id-list">
                ${comparison.removed.map(id => `<span class="id-badge removed">${escapeHtml(id)}</span>`).join('')}
            </div>
        </div>
    ` : '';

    comparisonBlock.innerHTML = `
        <div class="comparison-header-actions">
            <h3>Comparison Results</h3>
            <div class="comparison-action-buttons">
                <button class="comparison-action-btn update-ref-btn" onclick="updateReference()" title="Update reference with current data">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M21.5 2V8H15.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M21.5 8L18 4.5C16.6 3.1 14.8 2.2 12.8 2C7.8 1.3 3.5 5 3 10C2.5 15 5.8 19.5 10.8 20.5C15.8 21.5 20.5 18.5 21.5 13.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    Update Reference
                </button>
                <button class="comparison-action-btn import-ref-btn" onclick="triggerImportReference()" title="Import reference from CSV file">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M21 15V19C21 19.5304 20.7893 21.0391 20.4142 21.4142C20.0391 21.7893 19.5304 22 19 22H5C4.46957 22 3.96086 21.7893 3.58579 21.4142C3.21071 21.0391 3 20.5304 3 19V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M7 10L12 15L17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    Import Reference
                </button>
                <input type="file" id="import-reference-input" accept=".csv" style="display: none;" onchange="importReferenceFile(event)">
            </div>
        </div>
        <div class="comparison-stats">
            ${statsItems.join('')}
        </div>
        ${noChanges ? '<div class="no-changes">No changes detected - Current export matches the reference</div>' : ''}
        ${addedHtml}
        ${removedHtml}
    `;

    // Add CSS styles if not already added
    if (!document.getElementById('comparison-styles')) {
        const style = document.createElement('style');
        style.id = 'comparison-styles';
        style.textContent = `
            .comparison-block {
                background: #1a1a1a;
                padding: 1.5rem;
                border-radius: 12px;
                margin-bottom: 1.5rem;
                border: 1px solid #2a2a2a;
            }

            .comparison-header-actions {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
                padding-bottom: 1rem;
                border-bottom: 1px solid #2a2a2a;
            }

            .comparison-header-actions h3 {
                margin: 0;
                font-size: 1.5rem;
                font-weight: 300;
                color: #fff;
                font-family: 'Geist', sans-serif;
            }

            .comparison-action-buttons {
                display: flex;
                gap: 0.75rem;
            }

            .comparison-action-btn {
                background: #0047ff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 0.9rem;
                font-weight: 400;
                transition: all 0.2s ease;
                font-family: 'Geist', sans-serif;
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
            }

            .comparison-action-btn:hover {
                background: #0039cc;
            }

            .comparison-action-btn svg {
                width: 16px;
                height: 16px;
            }

            .comparison-stats {
                display: flex;
                gap: 2rem;
                flex-wrap: wrap;
                margin-bottom: 1.5rem;
                padding-bottom: 1.5rem;
                border-bottom: 1px solid #2a2a2a;
            }

            .comparison-stats .stat-item {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                font-weight: 300;
                color: #999;
                font-family: 'Geist', sans-serif;
            }

            .comparison-stats .stat-number {
                font-size: 1.8rem;
                font-weight: 300;
                color: #fff;
            }

            .comparison-stats .stat-number.added-color {
                color: #5ad67d;
            }

            .comparison-stats .stat-number.removed-color {
                color: #ff6b7a;
            }

            .comparison-stats .stat-label {
                font-size: 0.95rem;
                font-weight: 400;
                color: #999;
            }

            .comparison-detail-section {
                margin-top: 1.5rem;
            }

            .comparison-detail-section h4 {
                margin: 0 0 1rem 0;
                font-size: 1rem;
                font-weight: 300;
                color: #999;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-family: 'Geist', sans-serif;
            }

            .id-list {
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
            }

            .id-badge {
                display: inline-block;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                font-size: 0.9rem;
                font-weight: 400;
                font-family: 'Geist', monospace;
                background: #2a2a2a;
                color: #fff;
                border: 1px solid #333;
                transition: all 0.2s ease;
            }

            .id-badge.added {
                background: rgba(90, 214, 125, 0.15);
                border-color: rgba(90, 214, 125, 0.3);
                color: #5ad67d;
            }

            .id-badge.added:hover {
                background: rgba(90, 214, 125, 0.25);
            }

            .id-badge.removed {
                background: rgba(255, 107, 122, 0.15);
                border-color: rgba(255, 107, 122, 0.3);
                color: #ff6b7a;
            }

            .id-badge.removed:hover {
                background: rgba(255, 107, 122, 0.25);
            }

            .no-changes {
                padding: 1.5rem;
                text-align: center;
                color: #5ad67d;
                font-size: 1rem;
                font-weight: 300;
                background: rgba(90, 214, 125, 0.1);
                border-radius: 8px;
                border: 1px solid rgba(90, 214, 125, 0.2);
                font-family: 'Geist', sans-serif;
            }

            @media (max-width: 768px) {
                .comparison-stats {
                    flex-direction: column;
                    gap: 1rem;
                }

                .comparison-stats .stat-item {
                    display: block;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// ============================================
// DOCX Status Management Functions
// ============================================

/**
 * Show DOCX generation status with appropriate styling
 * @param {string} type - Status type: 'success', 'warning', or 'error'
 * @param {string} message - Main status message
 * @param {string} details - Optional detailed information (HTML allowed)
 */
function showDocxStatus(type, message, details = '') {
    const container = document.getElementById('docx-status-container');
    const card = container.querySelector('.docx-status-card');
    const messageEl = document.getElementById('docx-status-message');
    const detailsEl = document.getElementById('docx-status-details');

    // Remove all status classes
    card.classList.remove('status-success', 'status-warning', 'status-error');

    // Add appropriate status class
    card.classList.add(`status-${type}`);

    // Set message and details
    messageEl.textContent = message;
    detailsEl.innerHTML = details;

    // Show container with animation
    container.style.display = 'block';

    // Scroll to status container
    setTimeout(() => {
        container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

/**
 * Hide DOCX status container
 */
function hideDocxStatus() {
    const container = document.getElementById('docx-status-container');
    if (container) {
        container.style.display = 'none';
    }
}