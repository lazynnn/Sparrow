function sparrowApp() {
    return {
        currentView: 'traces',
        traces: [],
        selectedTrace: null,
        models: [],
        dashboard: { total_requests: 0, total_tokens: 0, total_cost: null, avg_duration_ms: null, models: [] },
        archives: [],
        archiveDate: '',
        isDark: true,
        filters: { model: '', status: '', dateFrom: '', dateTo: '', minDuration: '', path: '' },
        pagination: { page: 1, pageSize: 50, total: 0, totalPages: 1 },
        eventSource: null,

        async init() {
            this.initTheme();
            await this.loadModels();
            await this.loadTraces();
            await this.loadDashboard();
            this.connectSSE();
        },

        initTheme() {
            const saved = localStorage.getItem('sparrow-theme');
            this.isDark = saved ? saved === 'dark' : true;
            this.applyTheme();
        },

        toggleTheme() {
            this.isDark = !this.isDark;
            localStorage.setItem('sparrow-theme', this.isDark ? 'dark' : 'light');
            this.applyTheme();
        },

        applyTheme() {
            document.documentElement.classList.toggle('dark', this.isDark);
        },

        async loadModels() {
            try {
                const resp = await fetch('/api/traces?page=1&page_size=1');
                const data = await resp.json();
            } catch (e) {}
        },

        async loadTraces() {
            const params = new URLSearchParams({
                page: this.pagination.page,
                page_size: this.pagination.pageSize,
            });
            if (this.filters.model) params.set('model', this.filters.model);
            if (this.filters.status) params.set('status', this.filters.status);
            if (this.filters.dateFrom) params.set('date_from', this.filters.dateFrom);
            if (this.filters.dateTo) params.set('date_to', this.filters.dateTo);
            if (this.filters.minDuration) params.set('min_duration', this.filters.minDuration);
            if (this.filters.path) params.set('path', this.filters.path);

            try {
                const resp = await fetch(`/api/traces?${params}`);
                const data = await resp.json();
                this.traces = data.traces;
                this.pagination.total = data.total;
                this.pagination.totalPages = data.total_pages;

                const modelSet = new Set(this.models);
                data.traces.forEach(t => { if (t.model_name) modelSet.add(t.model_name); });
                this.models = [...modelSet];
            } catch (e) {
                console.error('Failed to load traces:', e);
            }
        },

        async showTraceDetail(id) {
            try {
                const resp = await fetch(`/api/traces/${id}`);
                this.selectedTrace = await resp.json();
            } catch (e) {
                console.error('Failed to load trace:', e);
            }
        },

        async loadDashboard() {
            try {
                const resp = await fetch('/api/dashboard');
                this.dashboard = await resp.json();
            } catch (e) {
                console.error('Failed to load dashboard:', e);
            }
        },

        async loadArchives() {
            try {
                const resp = await fetch('/api/archives');
                this.archives = await resp.json();
            } catch (e) {
                console.error('Failed to load archives:', e);
            }
        },

        async createArchive() {
            try {
                const body = {};
                if (this.archiveDate) body.older_than = this.archiveDate;
                const resp = await fetch('/api/archives', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body),
                });
                const result = await resp.json();
                if (result.path) {
                    await this.loadArchives();
                    await this.loadTraces();
                }
            } catch (e) {
                console.error('Failed to create archive:', e);
            }
        },

        async importArchive(path) {
            try {
                const resp = await fetch('/api/archives/import', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ path }),
                });
                await resp.json();
                await this.loadTraces();
                await this.loadDashboard();
            } catch (e) {
                console.error('Failed to import archive:', e);
            }
        },

        connectSSE() {
            try {
                this.eventSource = new EventSource('/api/traces/stream');
                this.eventSource.addEventListener('trace', (event) => {
                    if (this.currentView === 'traces' && this.pagination.page === 1) {
                        try {
                            const trace = JSON.parse(event.data);
                            this.traces.unshift(trace);
                            if (this.traces.length > this.pagination.pageSize) {
                                this.traces.pop();
                            }
                        } catch (e) {}
                    }
                });
                this.eventSource.addEventListener('ping', () => {});
            } catch (e) {}
        },

        formatTime(ts) {
            if (!ts) return '-';
            const d = new Date(ts);
            return d.toLocaleString();
        },

        formatJSON(str) {
            if (!str) return '<span class="json-null">null</span>';
            try {
                const obj = JSON.parse(str);
                return this.syntaxHighlight(JSON.stringify(obj, null, 2));
            } catch {
                return this.escapeHtml(str);
            }
        },

        syntaxHighlight(json) {
            json = this.escapeHtml(json);
            return json.replace(
                /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
                (match) => {
                    let cls = 'json-number';
                    if (/^"/.test(match)) {
                        if (/:$/.test(match)) {
                            cls = 'json-key';
                        } else {
                            cls = 'json-string';
                        }
                    } else if (/true|false/.test(match)) {
                        cls = 'json-boolean';
                    } else if (/null/.test(match)) {
                        cls = 'json-null';
                    }
                    return `<span class="${cls}">${match}</span>`;
                }
            );
        },

        escapeHtml(str) {
            return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        },

        formatBytes(bytes) {
            if (!bytes) return '0 B';
            const units = ['B', 'KB', 'MB', 'GB'];
            let i = 0;
            while (bytes >= 1024 && i < units.length - 1) { bytes /= 1024; i++; }
            return bytes.toFixed(1) + ' ' + units[i];
        },
    };
}
