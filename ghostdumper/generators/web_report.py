"""
Web Report Generator for GhostDumper v2.2

Generates an interactive HTML report with:
- Searchable class/method browser
- Interactive graphs (class hierarchy, call graph)
- String browser with filtering
- Symbol explorer
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class WebReportGenerator:
    """Generate interactive HTML web report."""

    def __init__(self, result, output_dir: Path, stem: str):
        self.result = result
        self.output_dir = output_dir
        self.stem = stem

    def generate(self):
        """Generate HTML report file."""
        html = self._build_html()

        path = self.output_dir / f"{self.stem}_analysis.html"
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

    def _build_html(self) -> str:
        """Build complete HTML page."""
        data = {
            "binary": self.result.binary_info,
            "metadata": self.result.metadata_info,
            "types": self.result.types,
            "methods": self.result.methods[:1000],
            "fields": self.result.fields[:1000],
            "strings": self.result.strings[:5000],
            "symbols": self.result.symbols[:2000],
            "duration": self.result.duration,
            "version": "2.2.1",
            "generated": datetime.now().isoformat(),
        }

        json_data = json.dumps(data, default=str)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GhostDumper v2.2 — Analysis Report</title>
    <style>
        :root {{
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-tertiary: #21262d;
            --text-primary: #c9d1d9;
            --text-secondary: #8b949e;
            --accent: #58a6ff;
            --accent-hover: #79c0ff;
            --border: #30363d;
            --success: #3fb950;
            --warning: #d29922;
            --danger: #f85149;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }}
        .header {{
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            padding: 1.5rem 2rem;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .header h1 {{
            font-size: 1.5rem;
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .header .subtitle {{
            color: var(--text-secondary);
            font-size: 0.875rem;
            margin-top: 0.25rem;
        }}
        .stats-bar {{
            display: flex;
            gap: 2rem;
            padding: 1rem 2rem;
            background: var(--bg-tertiary);
            border-bottom: 1px solid var(--border);
            flex-wrap: wrap;
        }}
        .stat {{
            display: flex;
            flex-direction: column;
        }}
        .stat-value {{
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--accent);
        }}
        .stat-label {{
            font-size: 0.75rem;
            color: var(--text-secondary);
            text-transform: uppercase;
        }}
        .container {{
            display: flex;
            height: calc(100vh - 180px);
        }}
        .sidebar {{
            width: 280px;
            background: var(--bg-secondary);
            border-right: 1px solid var(--border);
            overflow-y: auto;
        }}
        .nav-item {{
            padding: 0.75rem 1.5rem;
            cursor: pointer;
            border-bottom: 1px solid var(--border);
            transition: background 0.2s;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .nav-item:hover {{ background: var(--bg-tertiary); }}
        .nav-item.active {{ background: var(--bg-tertiary); border-left: 3px solid var(--accent); }}
        .main-content {{
            flex: 1;
            overflow-y: auto;
            padding: 1.5rem 2rem;
        }}
        .search-box {{
            width: 100%;
            padding: 0.75rem 1rem;
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text-primary);
            font-size: 0.875rem;
            margin-bottom: 1rem;
        }}
        .search-box:focus {{
            outline: none;
            border-color: var(--accent);
        }}
        .table-container {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.875rem;
        }}
        th {{
            background: var(--bg-tertiary);
            padding: 0.75rem 1rem;
            text-align: left;
            font-weight: 600;
            color: var(--text-secondary);
            border-bottom: 1px solid var(--border);
            position: sticky;
            top: 0;
        }}
        td {{
            padding: 0.625rem 1rem;
            border-bottom: 1px solid var(--border);
            color: var(--text-primary);
        }}
        tr:hover td {{ background: var(--bg-tertiary); }}
        .mono {{ font-family: 'SF Mono', Monaco, monospace; font-size: 0.8125rem; }}
        .addr {{ color: var(--accent); }}
        .token {{ color: var(--warning); }}
        .offset {{ color: var(--success); }}
        .hidden {{ display: none; }}
        .badge {{
            display: inline-block;
            padding: 0.125rem 0.5rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
        }}
        .badge-public {{ background: rgba(63, 185, 80, 0.2); color: var(--success); }}
        .badge-private {{ background: rgba(139, 148, 158, 0.2); color: var(--text-secondary); }}
        .badge-static {{ background: rgba(88, 166, 255, 0.2); color: var(--accent); }}
        .section-title {{
            font-size: 1.25rem;
            margin-bottom: 1rem;
            color: var(--text-primary);
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}
        .info-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
        }}
        .info-card h3 {{
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
        }}
        .info-card p {{
            font-family: monospace;
            font-size: 0.875rem;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>👻 GhostDumper v2.2</h1>
        <div class="subtitle">IL2CPP Deep Analyzer & Runtime Toolkit — Analysis Report</div>
    </div>

    <div class="stats-bar">
        <div class="stat">
            <span class="stat-value">{len(self.result.types)}</span>
            <span class="stat-label">Classes</span>
        </div>
        <div class="stat">
            <span class="stat-value">{len(self.result.methods)}</span>
            <span class="stat-label">Methods</span>
        </div>
        <div class="stat">
            <span class="stat-value">{len(self.result.fields)}</span>
            <span class="stat-label">Fields</span>
        </div>
        <div class="stat">
            <span class="stat-value">{self.result.metadata_info.get('string_count', 0)}</span>
            <span class="stat-label">Strings</span>
        </div>
        <div class="stat">
            <span class="stat-value">{len(self.result.symbols)}</span>
            <span class="stat-label">Symbols</span>
        </div>
        <div class="stat">
            <span class="stat-value">{self.result.duration:.2f}s</span>
            <span class="stat-label">Analysis Time</span>
        </div>
    </div>

    <div class="container">
        <div class="sidebar">
            <div class="nav-item active" data-tab="overview">📊 Overview</div>
            <div class="nav-item" data-tab="classes">📁 Classes</div>
            <div class="nav-item" data-tab="methods">⚡ Methods</div>
            <div class="nav-item" data-tab="strings">🔤 Strings</div>
            <div class="nav-item" data-tab="symbols">🏷️ Symbols</div>
            <div class="nav-item" data-tab="deobfuscation">🔓 Deobfuscation</div>
        </div>

        <div class="main-content">
            <div id="overview" class="tab-content">
                <h2 class="section-title">Binary Information</h2>
                <div class="info-grid">
                    <div class="info-card">
                        <h3>Format</h3>
                        <p>{self.result.binary_info.get('format', 'N/A')}</p>
                    </div>
                    <div class="info-card">
                        <h3>Architecture</h3>
                        <p>{self.result.binary_info.get('arch', 'N/A')} ({self.result.binary_info.get('bitness', 0)}-bit)</p>
                    </div>
                    <div class="info-card">
                        <h3>Base Address</h3>
                        <p class="addr">0x{self.result.binary_info.get('base_address', 0):08X}</p>
                    </div>
                    <div class="info-card">
                        <h3>Entry Point</h3>
                        <p class="addr">{hex(self.result.binary_info.get('entry_point', 0)) if self.result.binary_info.get('entry_point') else 'N/A'}</p>
                    </div>
                    <div class="info-card">
                        <h3>File Size</h3>
                        <p>{self.result.binary_info.get('size', 0):,} bytes</p>
                    </div>
                    <div class="info-card">
                        <h3>Metadata Version</h3>
                        <p>{self.result.metadata_info.get('version', 'N/A')}</p>
                    </div>
                </div>
            </div>

            <div id="classes" class="tab-content hidden">
                <h2 class="section-title">Classes ({len(self.result.types)})</h2>
                <input type="text" class="search-box" id="class-search" placeholder="Search classes...">
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Namespace</th>
                                <th>Parent</th>
                                <th>Methods</th>
                                <th>Fields</th>
                                <th>Token</th>
                            </tr>
                        </thead>
                        <tbody id="class-table">
                        </tbody>
                    </table>
                </div>
            </div>

            <div id="methods" class="tab-content hidden">
                <h2 class="section-title">Methods ({len(self.result.methods)})</h2>
                <input type="text" class="search-box" id="method-search" placeholder="Search methods...">
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Return Type</th>
                                <th>Parameters</th>
                                <th>Address</th>
                                <th>Token</th>
                            </tr>
                        </thead>
                        <tbody id="method-table">
                        </tbody>
                    </table>
                </div>
            </div>

            <div id="strings" class="tab-content hidden">
                <h2 class="section-title">Strings ({self.result.metadata_info.get('string_count', 0)})</h2>
                <input type="text" class="search-box" id="string-search" placeholder="Search strings...">
                <div class="table-container">
                    <table>
                        <thead>
                            <tr><th>#</th><th>String</th></tr>
                        </thead>
                        <tbody id="string-table">
                        </tbody>
                    </table>
                </div>
            </div>

            <div id="symbols" class="tab-content hidden">
                <h2 class="section-title">Symbols ({len(self.result.symbols)})</h2>
                <input type="text" class="search-box" id="symbol-search" placeholder="Search symbols...">
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Address</th>
                                <th>Size</th>
                                <th>Type</th>
                            </tr>
                        </thead>
                        <tbody id="symbol-table">
                        </tbody>
                    </table>
                </div>
            </div>

            <div id="deobfuscation" class="tab-content hidden">
                <h2 class="section-title">Deobfuscation Results</h2>
                <div class="info-grid">
                    <div class="info-card">
                        <h3>Applied Techniques</h3>
                        <p>{', '.join(self.result.deobfuscation_applied) if self.result.deobfuscation_applied else 'None'}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const data = {json_data};

        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {{
            item.addEventListener('click', () => {{
                document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                document.querySelectorAll('.tab-content').forEach(t => t.classList.add('hidden'));
                document.getElementById(item.dataset.tab).classList.remove('hidden');
            }});
        }});

        // Populate tables
        function populateClasses() {{
            const tbody = document.getElementById('class-table');
            tbody.innerHTML = data.types.map((t, i) => `
                <tr>
                    <td class="mono">${{t.name}}</td>
                    <td class="mono">${{t.namespace || '-'}}</td>
                    <td class="mono">${{t.parent || '-'}}</td>
                    <td>${{(t.methods || []).length}}</td>
                    <td>${{(t.fields || []).length}}</td>
                    <td class="token mono">0x${{(t.token || 0).toString(16).padStart(8, '0')}}</td>
                </tr>
            `).join('');
        }}

        function populateMethods() {{
            const tbody = document.getElementById('method-table');
            tbody.innerHTML = data.methods.map(m => `
                <tr>
                    <td class="mono">${{m.name}}</td>
                    <td class="mono">${{m.return_type}}</td>
                    <td class="mono">${{(m.parameters || []).join(', ')}}</td>
                    <td class="addr mono">0x${{(m.address || 0).toString(16).padStart(8, '0')}}</td>
                    <td class="token mono">0x${{(m.token || 0).toString(16).padStart(8, '0')}}</td>
                </tr>
            `).join('');
        }}

        function populateStrings() {{
            const tbody = document.getElementById('string-table');
            const strings = data.strings.slice(0, 1000);
            tbody.innerHTML = strings.map((s, i) => `
                <tr>
                    <td class="mono">${{i}}</td>
                    <td>${{s.replace(/</g, '&lt;').replace(/>/g, '&gt;')}}</td>
                </tr>
            `).join('');
        }}

        function populateSymbols() {{
            const tbody = document.getElementById('symbol-table');
            tbody.innerHTML = data.symbols.slice(0, 1000).map(s => `
                <tr>
                    <td class="mono">${{s.name}}</td>
                    <td class="addr mono">0x${{(s.address || 0).toString(16).padStart(8, '0')}}</td>
                    <td>${{s.size || 0}}</td>
                    <td>${{s.type || '?'}}</td>
                </tr>
            `).join('');
        }}

        // Search functionality
        function setupSearch(inputId, tableId) {{
            const input = document.getElementById(inputId);
            const tbody = document.getElementById(tableId);
            input.addEventListener('input', (e) => {{
                const term = e.target.value.toLowerCase();
                Array.from(tbody.children).forEach(row => {{
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(term) ? '' : 'none';
                }});
            }});
        }}

        // Initialize
        populateClasses();
        populateMethods();
        populateStrings();
        populateSymbols();
        setupSearch('class-search', 'class-table');
        setupSearch('method-search', 'method-table');
        setupSearch('string-search', 'string-table');
        setupSearch('symbol-search', 'symbol-table');
    </script>
</body>
</html>"""
