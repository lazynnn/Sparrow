function _escapeHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function _highlightText(text, searchTerm) {
    if (!searchTerm) return text;
    const escaped = searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${escaped})`, 'gi');
    return text.replace(regex, '<mark class="json-search-highlight">$1</mark>');
}

function _highlightLeaf(text, cls, searchTerm) {
    if (searchTerm) {
        return `<span class="${cls}">${_highlightText(text, searchTerm)}</span>`;
    }
    return `<span class="${cls}">${text}</span>`;
}

function _searchJson(data, term, path) {
    path = path || '';
    const matches = new Set();
    if (!term) return matches;
    const lower = term.toLowerCase();

    if (data !== null && typeof data === 'object') {
        const entries = Array.isArray(data) ? data.map((v, i) => [i, v]) : Object.entries(data);
        for (const [key, value] of entries) {
            const childPath = path ? `${path}.${key}` : String(key);
            if (String(key).toLowerCase().includes(lower)) {
                matches.add(path || String(key));
            }
            if (typeof value === 'string' && value.toLowerCase().includes(lower)) {
                matches.add(childPath);
            } else if (typeof value === 'number' && String(value).toLowerCase().includes(lower)) {
                matches.add(childPath);
            } else if (typeof value === 'boolean' && String(value).toLowerCase().includes(lower)) {
                matches.add(childPath);
            } else if (value !== null && typeof value === 'object') {
                for (const m of _searchJson(value, term, childPath)) {
                    matches.add(m);
                }
            }
        }
    }

    return matches;
}

function _pathHasMatch(path, searchPaths) {
    if (!searchPaths) return false;
    if (searchPaths.has(path)) return true;
    for (const p of searchPaths) {
        if (p.startsWith(path + '.') || path === '') return true;
    }
    return false;
}

function _isSSE(str) {
    if (!str || typeof str !== 'string') return false;
    return str.split('\n').some(line => /^data:\s?\S/.test(line));
}

function _parseSSEChunks(str) {
    if (!str) return [];
    const chunks = [];
    const lines = str.split('\n');
    let index = 0;
    for (const line of lines) {
        const trimmed = line.trim();
        const match = trimmed.match(/^data:\s*(.*)/);
        if (!match) continue;
        const data = match[1];
        const parsed = data === '[DONE]' ? null : (() => { try { return JSON.parse(data); } catch { return null; } })();
        chunks.push({ index: ++index, raw: trimmed, data, parsed, isDone: data === '[DONE]' });
    }
    return chunks;
}

function _mergeSSEContent(chunks) {
    const reasoningParts = [];
    const contentParts = [];
    for (const chunk of chunks) {
        if (!chunk.parsed || chunk.isDone) continue;
        try {
            const p = chunk.parsed;
            if (Array.isArray(p.choices)) {
                for (const choice of p.choices) {
                    if (!choice.delta) continue;
                    const reasoning = choice.delta.reasoning_content ?? choice.delta.reasoning;
                    if (reasoning != null && reasoning !== '') reasoningParts.push(reasoning);
                    if (choice.delta.content != null && choice.delta.content !== '') contentParts.push(choice.delta.content);
                }
            } else if (p.type === 'response.output_text.delta' && p.delta != null && p.delta !== '') {
                contentParts.push(p.delta);
            } else if (p.type === 'content_block_delta' && p.delta) {
                if (p.delta.thinking != null && p.delta.thinking !== '') reasoningParts.push(p.delta.thinking);
                if (p.delta.text != null && p.delta.text !== '') contentParts.push(p.delta.text);
            }
        } catch {}
    }
    return { reasoning: reasoningParts.join(''), content: contentParts.join('') };
}

function _mergeNonSSEContent(parsed) {
    const reasoningParts = [];
    const contentParts = [];
    try {
        if (Array.isArray(parsed.choices)) {
            for (const choice of parsed.choices) {
                if (!choice.message) continue;
                const reasoning = choice.message.reasoning_content ?? choice.message.reasoning;
                if (reasoning != null && reasoning !== '') reasoningParts.push(reasoning);
                if (choice.message.content != null && choice.message.content !== '') contentParts.push(choice.message.content);
            }
        } else if (Array.isArray(parsed.output)) {
            for (const item of parsed.output) {
                if (item.type === 'message' && Array.isArray(item.content)) {
                    for (const c of item.content) {
                        if (c.type === 'output_text' && c.text != null && c.text !== '') contentParts.push(c.text);
                    }
                }
            }
        } else if (Array.isArray(parsed.content)) {
            for (const block of parsed.content) {
                if (block.type === 'thinking' && block.thinking != null && block.thinking !== '') reasoningParts.push(block.thinking);
                if (block.type === 'text' && block.text != null && block.text !== '') contentParts.push(block.text);
            }
        }
    } catch {}
    return { reasoning: reasoningParts.join(''), content: contentParts.join('') };
}

function _renderJsonTree(data, searchTerm, path, searchPaths) {
    path = path || '';
    if (data === null) return _highlightLeaf('null', 'json-null', searchTerm);
    if (typeof data === 'boolean') return _highlightLeaf(String(data), 'json-boolean', searchTerm);
    if (typeof data === 'number') return _highlightLeaf(String(data), 'json-number', searchTerm);
    if (typeof data === 'string') return _highlightLeaf('"' + _escapeHtml(data) + '"', 'json-string', searchTerm);

    const isArray = Array.isArray(data);
    const entries = isArray ? data.map((v, i) => [i, v]) : Object.entries(data);
    const count = entries.length;
    const summary = isArray ? `[${count} item${count !== 1 ? 's' : ''}]` : `{${count} key${count !== 1 ? 's' : ''}}`;
    const open = !searchTerm || _pathHasMatch(path, searchPaths) ? ' open' : '';

    let html = `<details class="json-tree-node"${open}><summary>`;
    html += `<span class="json-tree-summary">${summary}</span>`;
    html += `</summary>`;
    html += `<div class="json-tree-children">`;

    for (const [key, value] of entries) {
        const childPath = path ? `${path}.${key}` : String(key);
        const keyHtml = isArray
            ? ''
            : `<span class="json-key">${_highlightText(_escapeHtml(String(key)), searchTerm)}</span><span class="json-colon">: </span>`;
        html += `<div class="json-tree-item">${keyHtml}${_renderJsonTree(value, searchTerm, childPath, searchPaths)}</div>`;
    }

    html += `</div></details>`;
    return html;
}

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

        jsonViewerOpen: false,
        jsonViewerTitle: '',
        jsonViewerContent: '',
        jsonViewerParsed: null,
        jsonViewerSearch: '',
        jsonViewerSearchPaths: null,
        jsonViewerSearchCount: 0,
        jsonViewerCopyFeedback: '',
        jsonViewerIsSSE: false,
        jsonViewerMode: 'chunks',

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
            if (this.filters.dateFrom) {
                const dt = new Date(this.filters.dateFrom + 'T00:00:00');
                params.set('date_from', dt.toISOString());
            }
            if (this.filters.dateTo) {
                const dt = new Date(this.filters.dateTo + 'T23:59:59.999');
                params.set('date_to', dt.toISOString());
            }
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
                if (this.eventSource) {
                    this.eventSource.close();
                }
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
            return new Intl.DateTimeFormat(undefined, {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false,
            }).format(d);
        },

        formatJSON(str) {
            if (!str) return '<span class="json-null">null</span>';
            try {
                const obj = JSON.parse(str);
                return this.syntaxHighlight(JSON.stringify(obj, null, 2));
            } catch {
                return _escapeHtml(str);
            }
        },

        syntaxHighlight(json) {
            json = _escapeHtml(json);
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
            return _escapeHtml(str);
        },

        openJsonViewer(title, jsonString) {
            this.jsonViewerTitle = title;
            this.jsonViewerContent = jsonString || '';
            this.jsonViewerSearch = '';
            this.jsonViewerSearchPaths = null;
            this.jsonViewerSearchCount = 0;
            this.jsonViewerCopyFeedback = '';
            this.jsonViewerIsSSE = _isSSE(this.jsonViewerContent);
            this.jsonViewerMode = this.jsonViewerIsSSE ? 'chunks' : 'json';
            try {
                this.jsonViewerParsed = JSON.parse(this.jsonViewerContent);
            } catch {
                this.jsonViewerParsed = this.jsonViewerContent;
            }
            this.jsonViewerOpen = true;
            this.$nextTick(() => {
                const el = document.getElementById('json-viewer-dialog');
                if (el) el.focus();
            });
        },

        closeJsonViewer() {
            this.jsonViewerOpen = false;
            this.jsonViewerSearch = '';
            this.jsonViewerSearchPaths = null;
            this.jsonViewerSearchCount = 0;
            this.jsonViewerIsSSE = false;
            this.jsonViewerMode = 'json';
        },

        getJsonViewerTree() {
            if (this.jsonViewerIsSSE) {
                if (this.jsonViewerMode === 'raw') return this.getRawSSEHtml();
                if (this.jsonViewerMode === 'chunks') return this.getChunksViewHtml();
                if (this.jsonViewerMode === 'merged') return this.getMergedViewHtml();
            }
            if (this.jsonViewerMode === 'merged' && typeof this.jsonViewerParsed === 'object' && this.jsonViewerParsed !== null) {
                return this.getNonSSEMergedViewHtml();
            }
            const parsed = this.jsonViewerParsed;
            if (parsed === null || parsed === undefined) return '<span class="json-null">null</span>';
            if (typeof parsed === 'string') {
                return '<pre class="whitespace-pre-wrap text-xs">' + _escapeHtml(parsed) + '</pre>';
            }
            this.jsonViewerSearchPaths = this.jsonViewerSearch ? _searchJson(parsed, this.jsonViewerSearch) : null;
            this.jsonViewerSearchCount = this.jsonViewerSearchPaths ? this.jsonViewerSearchPaths.size : 0;
            return _renderJsonTree(parsed, this.jsonViewerSearch, '', this.jsonViewerSearchPaths);
        },

        getRawSSEHtml() {
            const lines = (this.jsonViewerContent || '').split('\n');
            let html = '<pre class="whitespace-pre-wrap text-xs">';
            for (let i = 0; i < lines.length; i++) {
                const line = _escapeHtml(lines[i]);
                const prefixMatch = lines[i].match(/^(data:\s*)/);
                if (prefixMatch) {
                    const prefixLen = prefixMatch[1].length;
                    html += '<span class="sse-data-prefix">' + line.slice(0, prefixLen) + '</span>' + line.slice(prefixLen);
                } else {
                    html += line;
                }
                if (i < lines.length - 1) html += '\n';
            }
            html += '</pre>';
            return html;
        },

        getChunksViewHtml() {
            const chunks = _parseSSEChunks(this.jsonViewerContent);
            if (chunks.length === 0) return '<pre class="text-xs text-gray-400">No SSE chunks found</pre>';
            let html = '';
            for (const chunk of chunks) {
                html += `<div class="sse-chunk">`;
                html += `<div class="sse-chunk-header">Chunk ${chunk.index}${chunk.isDone ? ' — [DONE]' : ''}</div>`;
                if (chunk.isDone) {
                    html += '<div class="sse-chunk-body text-xs text-gray-400 italic">Stream end marker</div>';
                } else if (chunk.parsed) {
                    html += '<div class="sse-chunk-body">' + _renderJsonTree(chunk.parsed, this.jsonViewerSearch) + '</div>';
                } else {
                    html += '<div class="sse-chunk-body text-xs">' + _escapeHtml(chunk.data) + '</div>';
                }
                html += '</div>';
            }
            return html;
        },

        getMergedViewHtml() {
            const chunks = _parseSSEChunks(this.jsonViewerContent);
            const merged = _mergeSSEContent(chunks);
            if (!merged.reasoning && !merged.content) {
                return '<div class="text-sm text-gray-400 italic p-4">No extractable text content found in SSE chunks.</div>';
            }
            let html = '';
            if (merged.reasoning) {
                html += '<div class="sse-merged-section">';
                html += '<div class="sse-merged-label">Reasoning</div>';
                html += '<pre class="whitespace-pre-wrap text-sm leading-relaxed">' + _escapeHtml(merged.reasoning) + '</pre>';
                html += '</div>';
            }
            if (merged.reasoning && merged.content) {
                html += '<hr class="sse-merged-divider">';
            }
            if (merged.content) {
                html += '<div class="sse-merged-section">';
                html += '<div class="sse-merged-label">Content</div>';
                html += '<pre class="whitespace-pre-wrap text-sm leading-relaxed">' + _escapeHtml(merged.content) + '</pre>';
                html += '</div>';
            }
            return html;
        },

        getNonSSEMergedViewHtml() {
            const parsed = this.jsonViewerParsed;
            const merged = _mergeNonSSEContent(parsed);
            if (!merged.reasoning && !merged.content) {
                return '<div class="text-sm text-gray-400 italic p-4">No extractable text content found.</div>';
            }
            let html = '';
            if (merged.reasoning) {
                html += '<div class="sse-merged-section">';
                html += '<div class="sse-merged-label">Reasoning</div>';
                html += '<pre class="whitespace-pre-wrap text-sm leading-relaxed">' + _escapeHtml(merged.reasoning) + '</pre>';
                html += '</div>';
            }
            if (merged.reasoning && merged.content) {
                html += '<hr class="sse-merged-divider">';
            }
            if (merged.content) {
                html += '<div class="sse-merged-section">';
                html += '<div class="sse-merged-label">Content</div>';
                html += '<pre class="whitespace-pre-wrap text-sm leading-relaxed">' + _escapeHtml(merged.content) + '</pre>';
                html += '</div>';
            }
            return html;
        },

        async copyJsonToClipboard() {
            let text;
            if (this.jsonViewerIsSSE && this.jsonViewerMode === 'merged') {
                const chunks = _parseSSEChunks(this.jsonViewerContent);
                const merged = _mergeSSEContent(chunks);
                text = merged.reasoning && merged.content
                    ? merged.reasoning + '\n\n---\n\n' + merged.content
                    : merged.reasoning || merged.content || this.jsonViewerContent;
            } else if (this.jsonViewerIsSSE) {
                text = this.jsonViewerContent;
            } else if (this.jsonViewerMode === 'merged' && typeof this.jsonViewerParsed === 'object' && this.jsonViewerParsed !== null) {
                const merged = _mergeNonSSEContent(this.jsonViewerParsed);
                text = merged.reasoning && merged.content
                    ? merged.reasoning + '\n\n---\n\n' + merged.content
                    : merged.reasoning || merged.content || JSON.stringify(this.jsonViewerParsed, null, 2);
            } else {
                const parsed = this.jsonViewerParsed;
                text = typeof parsed === 'object' && parsed !== null
                    ? JSON.stringify(parsed, null, 2)
                    : String(parsed || '');
            }
            try {
                await navigator.clipboard.writeText(text);
                this.jsonViewerCopyFeedback = 'Copied!';
                setTimeout(() => { this.jsonViewerCopyFeedback = ''; }, 2000);
            } catch {
                const textarea = document.createElement('textarea');
                textarea.value = text;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                this.jsonViewerCopyFeedback = 'Copied!';
                setTimeout(() => { this.jsonViewerCopyFeedback = ''; }, 2000);
            }
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
