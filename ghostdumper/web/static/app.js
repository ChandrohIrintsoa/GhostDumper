/**
 * GhostDumper v2.2 — Web UI Application
 */

class GhostDumperApp {
    constructor() {
        this.socket = null;
        this.currentAnalysis = null;
        this.currentTab = 'overview';
        this.searchDebounce = null;
        this.init();
    }

    init() {
        this.initSocket();
        this.initEventListeners();
        this.initDragDrop();
        this.loadTheme();
    }

    // ===== SOCKET.IO =====
    initSocket() {
        this.socket = io({
            transports: ['websocket', 'polling'],
            reconnection: true,
            reconnectionAttempts: 5
        });

        this.socket.on('connect', () => {
            console.log('[GhostDumper] Connected to server');
            this.showToast('Connected to server', 'success');
        });

        this.socket.on('disconnect', () => {
            console.log('[GhostDumper] Disconnected');
            this.showToast('Disconnected from server', 'warning');
        });

        this.socket.on('progress', (data) => {
            this.updateProgress(data);
        });

        this.socket.on('complete', (data) => {
            this.onAnalysisComplete(data);
        });

        this.socket.on('error', (data) => {
            this.onAnalysisError(data);
        });
    }

    // ===== EVENT LISTENERS =====
    initEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const tab = item.dataset.tab;
                this.switchTab(tab);
            });
        });

        // File upload
        const uploadZone = document.getElementById('upload-zone');
        const fileInput = document.getElementById('file-input');

        if (uploadZone && fileInput) {
            uploadZone.addEventListener('click', () => fileInput.click());
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e.target.files));
        }

        // Search
        const searchInput = document.getElementById('global-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                clearTimeout(this.searchDebounce);
                this.searchDebounce = setTimeout(() => this.performSearch(e.target.value), 300);
            });
        }

        // Analyze button
        const analyzeBtn = document.getElementById('analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.startAnalysis());
        }

        // Theme toggle
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }

    // ===== DRAG & DROP =====
    initDragDrop() {
        const uploadZone = document.getElementById('upload-zone');
        if (!uploadZone) return;

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadZone.addEventListener(eventName, () => {
                uploadZone.classList.add('dragover');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadZone.addEventListener(eventName, () => {
                uploadZone.classList.remove('dragover');
            });
        });

        uploadZone.addEventListener('drop', (e) => {
            this.handleFileSelect(e.dataTransfer.files);
        });
    }

    // ===== FILE HANDLING =====
    handleFileSelect(files) {
        this.files = Array.from(files);
        this.updateFileList();
    }

    updateFileList() {
        const fileList = document.getElementById('file-list');
        if (!fileList || !this.files) return;

        fileList.innerHTML = this.files.map(file => `
            <div class="file-item">
                <span class="file-icon">📄</span>
                <span class="file-name">${this.escapeHtml(file.name)}</span>
                <span class="file-size">${this.formatBytes(file.size)}</span>
                <button class="btn btn-sm btn-danger" onclick="app.removeFile('${this.escapeHtml(file.name)}')">✕</button>
            </div>
        `).join('');
    }

    removeFile(fileName) {
        this.files = this.files.filter(f => f.name !== fileName);
        this.updateFileList();
    }

    // ===== ANALYSIS =====
    async startAnalysis() {
        if (!this.files || this.files.length === 0) {
            this.showToast('Please select files first', 'error');
            return;
        }

        const formData = new FormData();
        this.files.forEach(file => formData.append('files', file));

        // Show progress
        document.getElementById('upload-section').classList.add('hidden');
        document.getElementById('progress-section').classList.remove('hidden');

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.currentAnalysis = result;
                this.loadResults();
            } else {
                throw new Error(result.error || 'Analysis failed');
            }
        } catch (err) {
            this.onAnalysisError({ message: err.message });
        }
    }

    updateProgress(data) {
        const fill = document.getElementById('progress-fill');
        const status = document.getElementById('progress-status');

        if (fill) fill.style.width = `${data.progress}%`;
        if (status) status.textContent = data.stage;

        // Update step indicators
        document.querySelectorAll('.progress-step').forEach(step => {
            const stepName = step.dataset.step;
            if (data.completed_steps && data.completed_steps.includes(stepName)) {
                step.classList.add('done');
                step.classList.remove('active');
            } else if (stepName === data.current_step) {
                step.classList.add('active');
            }
        });
    }

    onAnalysisComplete(data) {
        document.getElementById('progress-section').classList.add('hidden');
        document.getElementById('results-section').classList.remove('hidden');
        this.showToast('Analysis complete!', 'success');
        this.updateStats(data);
    }

    onAnalysisError(data) {
        document.getElementById('progress-section').classList.add('hidden');
        document.getElementById('upload-section').classList.remove('hidden');
        this.showToast(data.message, 'error');
    }

    // ===== RESULTS =====
    async loadResults() {
        try {
            const response = await fetch('/api/results');
            this.currentAnalysis = await response.json();
            this.updateStats(this.currentAnalysis);
            this.populateTables();
        } catch (err) {
            console.error('Failed to load results:', err);
        }
    }

    updateStats(data) {
        const stats = {
            'stat-classes': data.classes || 0,
            'stat-methods': data.methods || 0,
            'stat-fields': data.fields || 0,
            'stat-strings': data.strings || 0,
            'stat-symbols': data.symbols || 0,
            'stat-duration': `${(data.duration || 0).toFixed(2)}s`
        };

        Object.entries(stats).forEach(([id, value]) => {
            const el = document.getElementById(id);
            if (el) el.textContent = value;
        });
    }

    populateTables() {
        if (!this.currentAnalysis) return;

        this.populateClassesTable();
        this.populateMethodsTable();
        this.populateStringsTable();
        this.populateSymbolsTable();
    }

    populateClassesTable() {
        const tbody = document.getElementById('class-table-body');
        if (!tbody || !this.currentAnalysis.types) return;

        tbody.innerHTML = this.currentAnalysis.types.slice(0, 100).map(cls => `
            <tr>
                <td class="mono">${this.escapeHtml(cls.name)}</td>
                <td class="mono text-secondary">${this.escapeHtml(cls.namespace || '-')}</td>
                <td class="mono">${this.escapeHtml(cls.parent || '-')}</td>
                <td>${(cls.methods || []).length}</td>
                <td>${(cls.fields || []).length}</td>
                <td class="token mono">0x${(cls.token || 0).toString(16).padStart(8, '0')}</td>
            </tr>
        `).join('');
    }

    populateMethodsTable() {
        const tbody = document.getElementById('method-table-body');
        if (!tbody || !this.currentAnalysis.methods) return;

        tbody.innerHTML = this.currentAnalysis.methods.slice(0, 100).map(method => `
            <tr>
                <td class="mono">${this.escapeHtml(method.name)}</td>
                <td class="mono text-accent">${this.escapeHtml(method.return_type || 'void')}</td>
                <td class="mono text-secondary">${(method.parameters || []).map(p => this.escapeHtml(p)).join(', ')}</td>
                <td class="addr mono">${method.address ? '0x' + method.address.toString(16).padStart(8, '0') : '-'}</td>
                <td class="token mono">0x${(method.token || 0).toString(16).padStart(8, '0')}</td>
            </tr>
        `).join('');
    }

    populateStringsTable() {
        const tbody = document.getElementById('string-table-body');
        if (!tbody || !this.currentAnalysis.strings) return;

        tbody.innerHTML = this.currentAnalysis.strings.slice(0, 500).map((str, i) => `
            <tr>
                <td class="mono text-muted">${i}</td>
                <td>${this.escapeHtml(str)}</td>
            </tr>
        `).join('');
    }

    populateSymbolsTable() {
        const tbody = document.getElementById('symbol-table-body');
        if (!tbody || !this.currentAnalysis.symbols) return;

        tbody.innerHTML = this.currentAnalysis.symbols.slice(0, 500).map(sym => `
            <tr>
                <td class="mono">${this.escapeHtml(sym.name)}</td>
                <td class="addr mono">0x${(sym.address || 0).toString(16).padStart(8, '0')}</td>
                <td>${sym.size || 0}</td>
                <td><span class="badge badge-${this.getSymbolTypeClass(sym.type)}">${this.escapeHtml(sym.type || '?')}</span></td>
            </tr>
        `).join('');
    }

    // ===== SEARCH =====
    async performSearch(query) {
        if (!query || query.length < 2) {
            this.populateTables();
            return;
        }

        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, top_k: 50 })
            });

            const data = await response.json();
            this.displaySearchResults(data.results);
        } catch (err) {
            console.error('Search failed:', err);
        }
    }

    displaySearchResults(results) {
        const tbody = document.getElementById('search-results-body');
        if (!tbody) return;

        tbody.innerHTML = results.map(r => `
            <tr>
                <td><span class="badge badge-${r.type}">${this.escapeHtml(r.type)}</span></td>
                <td class="mono">${this.escapeHtml(r.name)}</td>
                <td>
                    <div class="progress-bar-bg" style="height: 4px; width: 100px;">
                        <div class="progress-bar-fill" style="width: ${(r.score * 100).toFixed(0)}%;"></div>
                    </div>
                </td>
                <td class="mono text-secondary">${(r.score * 100).toFixed(1)}%</td>
            </tr>
        `).join('');

        this.switchTab('search');
    }

    // ===== NAVIGATION =====
    switchTab(tabName) {
        this.currentTab = tabName;

        // Update nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.toggle('active', item.dataset.tab === tabName);
        });

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === `tab-${tabName}`);
        });
    }

    // ===== THEME =====
    loadTheme() {
        const saved = localStorage.getItem('ghostdumper-theme');
        if (saved === 'light') {
            document.body.classList.add('light-theme');
        }
    }

    toggleTheme() {
        document.body.classList.toggle('light-theme');
        const isLight = document.body.classList.contains('light-theme');
        localStorage.setItem('ghostdumper-theme', isLight ? 'light' : 'dark');
    }

    // ===== UTILITIES =====
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    getSymbolTypeClass(type) {
        const map = { 'FUNC': 'public', 'OBJECT': 'static', 'SECTION': 'private' };
        return map[type] || 'private';
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container') || this.createToastContainer();
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} fade-in`;
        toast.style.cssText = 'margin-bottom: 0.5rem; animation: fadeIn 0.3s ease;';
        toast.innerHTML = `
            <span>${this.escapeHtml(message)}</span>
            <button onclick="this.parentElement.remove()" style="margin-left: auto; background: none; border: none; color: inherit; cursor: pointer;">✕</button>
        `;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 5000);
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = 'position: fixed; top: 1rem; right: 1rem; z-index: 9999; max-width: 400px;';
        document.body.appendChild(container);
        return container;
    }
}

// Initialize app
const app = new GhostDumperApp();
