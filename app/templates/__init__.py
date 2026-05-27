DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en" class="h-full bg-slate-950 text-slate-100">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Automated Code Review & CI Failure Pipeline Dashboard</title>
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <!-- Markdown Parser -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
                        mono: ['"JetBrains Mono"', 'monospace'],
                    },
                }
            }
        }
    </script>
    <style>
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #020617 70%);
        }
        .glass-panel {
            background: rgba(15, 23, 42, 0.45);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.07);
        }
        .glow-cyan {
            box-shadow: 0 0 25px -5px rgba(6, 182, 212, 0.35);
        }
        .glow-rose {
            box-shadow: 0 0 25px -5px rgba(244, 63, 94, 0.35);
        }
        .glow-green {
            box-shadow: 0 0 25px -5px rgba(34, 197, 94, 0.35);
        }
        .custom-scrollbar::-webkit-scrollbar {
            width: 5px;
            height: 5px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.2);
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 99px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.25);
        }
        .markdown-body h1, .markdown-body h2, .markdown-body h3 {
            font-weight: 700;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
            color: #f8fafc;
        }
        .markdown-body h1 { font-size: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.5rem; }
        .markdown-body h2 { font-size: 1.25rem; }
        .markdown-body h3 { font-size: 1.1rem; }
        .markdown-body p { margin-bottom: 1rem; color: #cbd5e1; line-height: 1.6; }
        .markdown-body ul { list-style-type: disc; margin-left: 1.5rem; margin-bottom: 1rem; }
        .markdown-body li { margin-bottom: 0.5rem; color: #cbd5e1; }
        .markdown-body code { font-family: 'JetBrains Mono', monospace; background: rgba(0,0,0,0.4); padding: 0.2rem 0.4rem; border-radius: 4px; font-size: 0.875rem; color: #67e8f9; }
        .markdown-body pre { background: rgba(0,0,0,0.5); padding: 1rem; border-radius: 8px; overflow-x: auto; margin-bottom: 1rem; border: 1px solid rgba(255,255,255,0.05); }
        .markdown-body pre code { background: transparent; padding: 0; font-size: 0.85rem; color: #e2e8f0; }
        
        /* Pulse Animation */
        @keyframes pulse-ring {
            0% { transform: scale(0.95); opacity: 1; }
            50% { transform: scale(1.1); opacity: 0.5; }
            100% { transform: scale(0.95); opacity: 1; }
        }
        .pulse-effect {
            animation: pulse-ring 2s infinite ease-in-out;
        }
    </style>
</head>
<body class="h-full overflow-hidden flex flex-col antialiased">

    <!-- Header bar -->
    <header class="h-16 shrink-0 border-b border-white/5 bg-slate-950/80 backdrop-blur-md flex items-center justify-between px-6 z-10">
        <div class="flex items-center gap-3">
            <div class="h-9 w-9 rounded-xl bg-gradient-to-tr from-cyan-500 via-indigo-500 to-rose-500 flex items-center justify-center glow-cyan">
                <i data-lucide="shield-check" class="h-5 w-5 text-white"></i>
            </div>
            <div>
                <span class="font-bold text-lg bg-gradient-to-r from-cyan-400 via-indigo-200 to-rose-400 bg-clip-text text-transparent">
                    OpenReviewer
                </span>
                <span class="ml-2 text-xs font-mono px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                    AI Agent Platform
                </span>
            </div>
        </div>
        
        <div class="flex items-center gap-6">
            <div class="flex items-center gap-2 text-xs font-medium text-slate-400 bg-slate-900 border border-white/5 py-1 px-3 rounded-lg">
                <span class="h-2 w-2 rounded-full bg-emerald-500 pulse-effect"></span>
                DevOps agents active
            </div>
            <button onclick="toggleSettingsModal()" class="p-2 text-slate-400 hover:text-white transition-colors duration-150 relative">
                <i data-lucide="settings" class="h-5 w-5"></i>
            </button>
        </div>
    </header>

    <!-- Main Workspace -->
    <main class="flex-1 overflow-hidden flex flex-row">

        <!-- Left Sidebar: Review Jobs & CI failures switcher -->
        <aside class="w-80 border-r border-white/5 bg-slate-950/20 shrink-0 flex flex-col overflow-hidden">
            <!-- Navigation Switcher inside Sidebar -->
            <div class="flex border-b border-white/5 bg-slate-950/40">
                <button onclick="switchSidebarTab('reviews')" id="sidebar-tab-reviews" class="flex-1 py-3 text-[10px] font-bold border-b-2 border-transparent text-slate-400 hover:text-white transition flex items-center justify-center gap-1">
                    <i data-lucide="git-pull-request" class="h-3 w-3"></i>
                    PR Reviews
                </button>
                <button onclick="switchSidebarTab('ci')" id="sidebar-tab-ci" class="flex-1 py-3 text-[10px] font-bold border-b-2 border-transparent text-slate-400 hover:text-white transition flex items-center justify-center gap-1">
                    <i data-lucide="alert-triangle" class="h-3 w-3"></i>
                    CI/CD Failures
                </button>
                <button onclick="switchSidebarTab('issues')" id="sidebar-tab-issues" class="flex-1 py-3 text-[10px] font-bold border-b-2 border-transparent text-slate-400 hover:text-white transition flex items-center justify-center gap-1">
                    <i data-lucide="alert-circle" class="h-3 w-3"></i>
                    Issues
                </button>
            </div>
            
            <div class="p-3 border-b border-white/5 flex items-center justify-between bg-slate-950/10">
                <h2 id="sidebar-list-title" class="text-xs font-bold text-slate-400 uppercase tracking-wider">CI/CD Pipeline Log Files</h2>
                <button onclick="handleRefresh()" class="p-1.5 hover:bg-white/5 text-slate-400 hover:text-white rounded-lg transition">
                    <i data-lucide="refresh-cw" class="h-3.5 w-3.5"></i>
                </button>
            </div>
            
            <!-- List Containers -->
            <div id="reviews-list" class="hidden flex-1 overflow-y-auto custom-scrollbar p-3 space-y-2">
                <!-- Loaded dynamically -->
                <div class="text-center py-8 text-slate-500 text-xs">
                    <p>Loading pull requests...</p>
                </div>
            </div>
            <div id="ci-list" class="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-2">
                <!-- Loaded dynamically -->
                <div class="text-center py-8 text-slate-500 text-xs">
                    <p>Loading CI/CD failures...</p>
                </div>
            </div>
            <div id="issues-list" class="hidden flex-1 overflow-y-auto custom-scrollbar p-3 space-y-2">
                <!-- Loaded dynamically -->
                <div class="text-center py-8 text-slate-500 text-xs">
                    <p>Loading issues...</p>
                </div>
            </div>
            
        </aside>

        <!-- Right / Core Panel: Selected Review details -->
        <section id="detail-panel" class="flex-1 overflow-hidden flex flex-col bg-slate-950/10">
            <!-- Empty State -->
            <div id="empty-detail-state" class="flex-1 flex flex-col items-center justify-center text-center p-8">
                <div id="empty-icon-box" class="h-16 w-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-slate-400 mb-4">
                    <i data-lucide="alert-triangle" class="h-8 w-8"></i>
                </div>
                <h3 id="empty-title" class="font-medium text-slate-200 text-lg">No CI Failure Log Selected</h3>
                <p id="empty-desc" class="text-slate-400 text-sm max-w-sm mt-1">Select a failed deployment workflow run to diagnose environment variables or code bugs.</p>
            </div>

            <!-- Detail Grid for Pull Request Review -->
            <div id="active-detail-content" class="hidden flex-1 overflow-hidden flex flex-col">
                <!-- Details Header -->
                <div class="p-6 border-b border-white/5 bg-slate-900/40 flex items-start justify-between">
                    <div>
                        <div class="flex items-center gap-3">
                            <span id="detail-repo" class="text-sm font-mono text-cyan-400">repo/name</span>
                            <span class="text-slate-600">•</span>
                            <span id="detail-author" class="text-xs text-slate-400">@username</span>
                        </div>
                        <h1 id="detail-title" class="text-xl font-bold text-white mt-1">PR Title</h1>
                        <p class="text-xs font-mono text-slate-500 mt-0.5">Thread ID: <span id="detail-id">n/a</span></p>
                    </div>
                    
                    <div id="detail-badge" class="px-3 py-1 rounded-full text-xs font-medium border">
                        Status
                    </div>
                </div>

                <!-- Stepper Visualizer (LangGraph State) -->
                <div class="px-6 py-4 bg-slate-950/40 border-b border-white/5 flex items-center justify-between text-xs overflow-x-auto custom-scrollbar">
                    <div class="flex items-center gap-6 shrink-0">
                        <div class="flex items-center gap-2">
                            <span id="step-webhook" class="h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs bg-slate-800 text-slate-400 border border-slate-700">1</span>
                            <span class="font-medium text-slate-400">Webhook Input</span>
                        </div>
                        <i data-lucide="chevron-right" class="h-4 w-4 text-slate-600"></i>
                        <div class="flex items-center gap-2">
                            <span id="step-agents" class="h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs bg-slate-800 text-slate-400 border border-slate-700">2</span>
                            <span class="font-medium text-slate-400">Parallel Agents</span>
                        </div>
                        <i data-lucide="chevron-right" class="h-4 w-4 text-slate-600"></i>
                        <div class="flex items-center gap-2">
                            <span id="step-gate" class="h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs bg-slate-800 text-slate-400 border border-slate-700">3</span>
                            <span class="font-medium text-slate-400">Consolidated PR Report</span>
                        </div>
                    </div>
                </div>

                <!-- Tabs Selector -->
                <div class="flex border-b border-white/5 bg-slate-900/20 shrink-0">
                    <button onclick="switchTab('consolidated')" id="tab-btn-consolidated" class="px-5 py-3 text-sm font-medium border-b-2 border-cyan-500 text-cyan-400 transition">
                        Consolidated Report
                    </button>
                    <button onclick="switchTab('security')" id="tab-btn-security" class="px-5 py-3 text-sm font-medium border-b-2 border-transparent text-slate-400 hover:text-white transition flex items-center gap-1.5">
                        🛡️ Security
                    </button>
                    <button onclick="switchTab('quality')" id="tab-btn-quality" class="px-5 py-3 text-sm font-medium border-b-2 border-transparent text-slate-400 hover:text-white transition flex items-center gap-1.5">
                        📐 Quality
                    </button>
                    <button onclick="switchTab('test')" id="tab-btn-test" class="px-5 py-3 text-sm font-medium border-b-2 border-transparent text-slate-400 hover:text-white transition flex items-center gap-1.5">
                        🧪 Test Coverage
                    </button>
                    <button onclick="switchTab('doc')" id="tab-btn-doc" class="px-5 py-3 text-sm font-medium border-b-2 border-transparent text-slate-400 hover:text-white transition flex items-center gap-1.5">
                        📝 Docs
                    </button>
                    <button onclick="switchTab('diff')" id="tab-btn-diff" class="px-5 py-3 text-sm font-medium border-b-2 border-transparent text-slate-400 hover:text-white transition flex items-center gap-1.5">
                        📜 Diff File
                    </button>
                </div>

                <!-- Content Area -->
                <div class="flex-1 overflow-y-auto p-6 custom-scrollbar bg-slate-950/45">
                    <!-- Consolidated Tab -->
                    <div id="tab-content-consolidated" class="tab-pane markdown-body"></div>
                    <!-- Security Tab -->
                    <div id="tab-content-security" class="tab-pane hidden markdown-body"></div>
                    <!-- Quality Tab -->
                    <div id="tab-content-quality" class="tab-pane hidden markdown-body"></div>
                    
                    <!-- Test Tab -->
                    <div id="tab-content-test" class="tab-pane hidden space-y-6">
                        <div id="test-markdown-report" class="markdown-body"></div>
                    </div>

                    <!-- Doc Tab -->
                    <div id="tab-content-doc" class="tab-pane hidden markdown-body"></div>
                    <!-- Diff Tab -->
                    <div id="tab-content-diff" class="tab-pane hidden font-mono text-xs border border-white/5 bg-slate-950/60 p-2 rounded-xl">
                        <div id="diff-visual-container" class="space-y-0.5"></div>
                    </div>
                </div>
            </div>

            <!-- Detail Grid for CI/CD Failure Analysis -->
            <div id="active-ci-detail-content" class="hidden flex-1 overflow-hidden flex flex-col">
                <!-- Details Header -->
                <div class="p-6 border-b border-white/5 bg-slate-900/40 flex items-start justify-between">
                    <div>
                        <div class="flex items-center gap-3">
                            <span id="ci-detail-repo" class="text-sm font-mono text-rose-400">repo/name</span>
                            <span class="text-slate-600">•</span>
                            <span id="ci-detail-step" class="text-xs text-slate-400">failed_step</span>
                        </div>
                        <h1 class="text-xl font-bold text-white mt-1">CI/CD Pipeline Failure Debugger</h1>
                        <p class="text-xs font-mono text-slate-500 mt-0.5">Workflow ID: <span id="ci-detail-id">n/a</span></p>
                    </div>
                    
                    <div id="ci-detail-badge" class="px-3 py-1 rounded-full text-xs font-medium border bg-rose-500/10 text-rose-400 border-rose-500/20">
                        Status
                    </div>
                </div>

                <!-- Classification Status Panel -->
                <div class="px-6 py-4 bg-slate-950/40 border-b border-white/5 flex items-center justify-between text-xs">
                    <div class="flex items-center gap-4">
                        <span class="text-slate-400 font-semibold uppercase tracking-wider">Analysis Classification:</span>
                        <span id="ci-detail-domain" class="px-3 py-0.5 rounded-lg text-xs font-mono font-bold uppercase border"></span>
                    </div>
                    <div id="ci-action-indicator" class="text-xs font-medium flex items-center gap-1.5 text-cyan-400">
                        <!-- Loaded dynamically -->
                    </div>
                </div>

                <!-- Tabs Selector -->
                <div class="flex border-b border-white/5 bg-slate-900/20 shrink-0">
                    <button onclick="switchCITab('ci-report')" id="tab-btn-ci-report" class="px-5 py-3 text-sm font-medium border-b-2 border-rose-500 text-rose-400 transition">
                        AI Debugging Report & Fix
                    </button>
                    <button onclick="switchCITab('ci-stacktrace')" id="tab-btn-ci-stacktrace" class="px-5 py-3 text-sm font-medium border-b-2 border-transparent text-slate-400 hover:text-white transition flex items-center gap-1.5">
                        🔍 Preprocessed Error Snippet
                    </button>
                    <button onclick="switchCITab('ci-raw')" id="tab-btn-ci-raw" class="px-5 py-3 text-sm font-medium border-b-2 border-transparent text-slate-400 hover:text-white transition flex items-center gap-1.5">
                        📜 Raw Workflow Logs
                    </button>
                </div>

                <!-- Content Area -->
                <div class="flex-1 overflow-y-auto p-6 custom-scrollbar bg-slate-950/45">
                    <!-- Failure Report Tab -->
                    <div id="tab-content-ci-report" class="tab-pane-ci markdown-body"></div>

                    <!-- Extracted Stacktrace Tab -->
                    <div id="tab-content-ci-stacktrace" class="tab-pane-ci hidden">
                        <span class="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">Isolated Stacktrace (Noise filtered by preprocessor)</span>
                        <pre id="ci-detail-stacktrace" class="bg-slate-950 border border-white/5 p-4 rounded-xl text-[11px] font-mono text-rose-300 max-h-[70vh] overflow-y-auto custom-scrollbar whitespace-pre-wrap"></pre>
                    </div>

                    <!-- Raw Logs Tab -->
                    <div id="tab-content-ci-raw" class="tab-pane-ci hidden">
                        <span class="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">Complete execution logs received from workflow run</span>
                        <pre id="ci-detail-raw" class="bg-slate-950 border border-white/5 p-4 rounded-xl text-[11px] font-mono text-slate-400 max-h-[70vh] overflow-y-auto custom-scrollbar whitespace-pre-wrap"></pre>
                    </div>
                </div>
            </div>

            <!-- Detail Grid for GitHub Issues Analysis -->
            <div id="active-issue-detail-content" class="hidden flex-1 overflow-hidden flex flex-col">
                <!-- Details Header -->
                <div class="p-6 border-b border-white/5 bg-slate-900/40 flex items-start justify-between">
                    <div>
                        <div class="flex items-center gap-3">
                            <span id="issue-detail-repo" class="text-sm font-mono text-cyan-400">repo/name</span>
                            <span class="text-slate-600">•</span>
                            <span id="issue-detail-author" class="text-xs text-slate-400">@username</span>
                        </div>
                        <h1 id="issue-detail-title" class="text-xl font-bold text-white mt-1">Issue Title</h1>
                        <p class="text-xs font-mono text-slate-500 mt-0.5">Issue ID: <span id="issue-detail-id">n/a</span></p>
                    </div>
                    
                    <div id="issue-detail-badge" class="px-3 py-1 rounded-full text-xs font-medium border bg-cyan-500/10 text-cyan-400 border-cyan-500/20">
                        Status
                    </div>
                </div>

                <!-- Classification Status Panel -->
                <div class="px-6 py-4 bg-slate-950/40 border-b border-white/5 flex items-center justify-between text-xs">
                    <div class="flex items-center gap-4">
                        <span class="text-slate-400 font-semibold uppercase tracking-wider">Criticality:</span>
                        <span id="issue-detail-criticality" class="px-3 py-0.5 rounded-lg text-xs font-mono font-bold uppercase border"></span>
                    </div>
                    <div class="text-xs font-medium flex items-center gap-1.5 text-cyan-400">
                        <i data-lucide="message-square" class="h-3.5 w-3.5"></i> Posted Comment to GitHub Issue
                    </div>
                </div>

                <!-- Tabs Selector -->
                <div class="flex border-b border-white/5 bg-slate-900/20 shrink-0">
                    <button onclick="switchIssueTab('issue-report')" id="tab-btn-issue-report" class="px-5 py-3 text-sm font-medium border-b-2 border-cyan-500 text-cyan-400 transition">
                        AI Diagnosis & Remedy
                    </button>
                    <button onclick="switchIssueTab('issue-file')" id="tab-btn-issue-file" class="px-5 py-3 text-sm font-medium border-b-2 border-transparent text-slate-400 hover:text-white transition flex items-center gap-1.5">
                        🔍 Target File Content (<span id="issue-target-filename">none</span>)
                    </button>
                    <button onclick="switchIssueTab('issue-raw')" id="tab-btn-issue-raw" class="px-5 py-3 text-sm font-medium border-b-2 border-transparent text-slate-400 hover:text-white transition flex items-center gap-1.5">
                        📜 Raw Issue Text
                    </button>
                </div>

                <!-- Content Area -->
                <div class="flex-1 overflow-y-auto p-6 custom-scrollbar bg-slate-950/45">
                    <!-- Failure Report Tab -->
                    <div id="tab-content-issue-report" class="tab-pane-issue markdown-body font-sans text-slate-300 text-sm leading-relaxed"></div>

                    <!-- Referenced File Content Tab -->
                    <div id="tab-content-issue-file" class="tab-pane-issue hidden">
                        <span class="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">Source Code pulled from main branch</span>
                        <pre id="issue-detail-file-code" class="bg-slate-950 border border-white/5 p-4 rounded-xl text-[11px] font-mono text-slate-300 max-h-[70vh] overflow-y-auto custom-scrollbar whitespace-pre-wrap"></pre>
                    </div>

                    <!-- Raw Issue Text Tab -->
                    <div id="tab-content-issue-raw" class="tab-pane-issue hidden">
                        <pre id="issue-detail-raw-body" class="bg-slate-950 border border-white/5 p-4 rounded-xl text-xs font-sans text-slate-400 max-h-[70vh] overflow-y-auto custom-scrollbar whitespace-pre-wrap"></pre>
                    </div>
                </div>
            </div>
        </section>

    </main>

    <!-- Settings Modal -->
    <div id="settings-modal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="glass-panel w-full max-w-lg rounded-2xl overflow-hidden flex flex-col">
            <div class="p-5 border-b border-white/5 flex items-center justify-between bg-slate-900/50">
                <div class="flex items-center gap-2">
                    <i data-lucide="settings" class="h-5 w-5 text-indigo-400"></i>
                    <h3 class="font-bold text-white text-base">Pipeline & Model Configuration</h3>
                </div>
                <button onclick="toggleSettingsModal()" class="text-slate-400 hover:text-white">
                    <i data-lucide="x" class="h-5 w-5"></i>
                </button>
            </div>
            
            <div class="p-6 space-y-4 overflow-y-auto max-h-[70vh] custom-scrollbar">
                <div>
                    <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Active LLM Provider</label>
                    <select id="settings-provider" onchange="toggleProviderFields(this.value)" class="w-full bg-slate-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-slate-100 focus:outline-none focus:border-cyan-500">
                        <option value="openai">OpenAI GPT Models</option>
                        <option value="gemini">Google Gemini Models</option>
                        <option value="anthropic">Anthropic Claude Models</option>
                        <option value="groq">Groq Llama 3.3 Models</option>
                    </select>
                </div>

                <div id="field-model" class="hidden">
                    <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Specific LLM Model</label>
                    <input type="text" id="settings-model" placeholder="e.g. gpt-4o-mini, gemini-2.5-flash, llama-3.3-70b-versatile" class="w-full bg-slate-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500">
                </div>

                <div id="field-openai" class="hidden">
                    <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">OpenAI API Key</label>
                    <input type="password" id="settings-openai-key" placeholder="sk-..." class="w-full bg-slate-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500">
                </div>

                <div id="field-gemini" class="hidden">
                    <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Gemini API Key</label>
                    <input type="password" id="settings-gemini-key" placeholder="AIzaSy..." class="w-full bg-slate-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500">
                </div>

                <div id="field-anthropic" class="hidden">
                    <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Anthropic API Key</label>
                    <input type="password" id="settings-anthropic-key" placeholder="sk-ant-..." class="w-full bg-slate-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500">
                </div>

                <div id="field-groq" class="hidden">
                    <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Groq API Key</label>
                    <input type="password" id="settings-groq-key" placeholder="gsk_..." class="w-full bg-slate-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500">
                </div>

                <div class="border-t border-white/5 pt-4">
                    <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Microsoft Teams Workflow Webhook URL</label>
                    <input type="text" id="settings-teams" placeholder="https://prod-XX.westus.logic.azure.com:443/workflows/..." class="w-full bg-slate-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500">
                </div>

                <div class="border-t border-white/5 pt-4">
                    <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">GitHub Webhook HMAC Secret</label>
                    <input type="text" id="settings-secret" readonly class="w-full bg-slate-950 border border-white/5 rounded-xl px-4 py-2 text-xs font-mono text-slate-400 select-all cursor-not-allowed">
                </div>
            </div>
            
            <div class="p-5 border-t border-white/5 bg-slate-900/50 flex justify-end gap-3">
                <button onclick="toggleSettingsModal()" class="px-4 py-2 rounded-xl text-slate-400 hover:text-white font-medium text-sm transition">
                    Close
                </button>
                <button onclick="saveSettings()" class="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition duration-150 flex items-center gap-2 shadow-lg shadow-indigo-950/50">
                    <i data-lucide="save" class="h-4 w-4"></i>
                    Save Config
                </button>
            </div>
        </div>
    </div>

    <!-- Script Logic -->
    <script>
        function safeParseMarkdown(text) {
            if (!text) return "";
            if (typeof marked !== 'undefined' && marked && typeof marked.parse === 'function') {
                return marked.parse(text);
            }
            return `<pre class="whitespace-pre-wrap font-sans text-slate-300 text-sm leading-relaxed">${text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")}</pre>`;
        }

        let selectedReviewId = null;
        let selectedCIId = null;
        let selectedIssueId = null;
        let activeTab = "consolidated";
        let activeCITab = "ci-report";
        let activeIssueTab = "issue-report";
        let activeSidebarTab = "ci";
        let reviewsCache = {};
        let ciCache = {};
        let issuesCache = {};

        window.addEventListener("DOMContentLoaded", () => {
            try {
                if (typeof lucide !== 'undefined' && lucide && typeof lucide.createIcons === 'function') {
                    lucide.createIcons();
                }
            } catch (e) {}
            
            handleRefresh();
            loadSettings();
            
            // Fast status polling loops
            setInterval(pollActiveJobs, 3000);
        });

        function switchSidebarTab(tab) {
            activeSidebarTab = tab;
            const title = document.getElementById("sidebar-list-title");
            
            // Style Tab buttons
            const revBtn = document.getElementById("sidebar-tab-reviews");
            const ciBtn = document.getElementById("sidebar-tab-ci");
            const issBtn = document.getElementById("sidebar-tab-issues");
            
            revBtn.className = "flex-1 py-3 text-[10px] font-bold border-b-2 border-transparent text-slate-400 hover:text-white transition flex items-center justify-center gap-1";
            ciBtn.className = "flex-1 py-3 text-[10px] font-bold border-b-2 border-transparent text-slate-400 hover:text-white transition flex items-center justify-center gap-1";
            issBtn.className = "flex-1 py-3 text-[10px] font-bold border-b-2 border-transparent text-slate-400 hover:text-white transition flex items-center justify-center gap-1";
            
            document.getElementById("reviews-list").classList.add("hidden");
            document.getElementById("ci-list").classList.add("hidden");
            document.getElementById("issues-list").classList.add("hidden");
            
            if (tab === "reviews") {
                revBtn.className = "flex-1 py-3 text-[10px] font-bold border-b-2 border-cyan-500 text-cyan-400 transition flex items-center justify-center gap-1";
                title.textContent = "Active Pull Requests";
                document.getElementById("reviews-list").classList.remove("hidden");
                
                if (selectedReviewId) {
                    selectReview(selectedReviewId);
                } else {
                    showEmptyDetailState("git-pull-request", "No Pull Request Selected", "Select an active pull request from the sidebar to inspect the automated code reviews.");
                }
            } else if (tab === "ci") {
                ciBtn.className = "flex-1 py-3 text-[10px] font-bold border-b-2 border-rose-500 text-rose-400 transition flex items-center justify-center gap-1";
                title.textContent = "CI/CD Pipeline Log Files";
                document.getElementById("ci-list").classList.remove("hidden");
                
                if (selectedCIId) {
                    selectCIFailure(selectedCIId);
                } else {
                    showEmptyDetailState("alert-triangle", "No CI Failure Log Selected", "Select a failed deployment workflow run to diagnose environment variables or code bugs.");
                }
            } else if (tab === "issues") {
                issBtn.className = "flex-1 py-3 text-[10px] font-bold border-b-2 border-cyan-500 text-cyan-400 transition flex items-center justify-center gap-1";
                title.textContent = "Active GitHub Issues";
                document.getElementById("issues-list").classList.remove("hidden");
                
                if (selectedIssueId) {
                    selectIssue(selectedIssueId);
                } else {
                    showEmptyDetailState("alert-circle", "No GitHub Issue Selected", "Select a reported issue from the sidebar to view criticality assessment and suggested remedies.");
                }
            }
            handleRefresh();
        }

        function showEmptyDetailState(icon, title, desc) {
            document.getElementById("empty-detail-state").classList.remove("hidden");
            document.getElementById("active-detail-content").classList.add("hidden");
            document.getElementById("active-ci-detail-content").classList.add("hidden");
            document.getElementById("active-issue-detail-content").classList.add("hidden");
            
            document.getElementById("empty-icon-box").innerHTML = `<i data-lucide="${icon}" class="h-8 w-8"></i>`;
            document.getElementById("empty-title").textContent = title;
            document.getElementById("empty-desc").textContent = desc;
            if (typeof lucide !== 'undefined') lucide.createIcons();
        }

        function handleRefresh() {
            if (activeSidebarTab === "reviews") {
                refreshReviews();
            } else if (activeSidebarTab === "ci") {
                refreshCIFailures();
            } else if (activeSidebarTab === "issues") {
                refreshIssues();
            }
        }

        async function refreshReviews() {
            try {
                const res = await fetch("/api/reviews");
                const reviews = await res.json();
                reviewsCache = reviews;

                const container = document.getElementById("reviews-list");
                container.innerHTML = "";

                let keys = Object.keys(reviews).reverse();
                if (keys.length === 0) {
                    container.innerHTML = `<div class="text-center py-8 text-slate-500 text-xs"><p>No pull requests reviewed yet.</p></div>`;
                    return;
                }

                keys.forEach(id => {
                    const r = reviews[id];
                    let badgeClass = "bg-cyan-500/10 text-cyan-400 border-cyan-500/20";
                    let label = r.status.toUpperCase();
                    
                    if (r.status === "running") {
                        badgeClass = "bg-cyan-500/10 text-cyan-400 border-cyan-500/20 pulse-effect";
                    } else if (r.status === "completed") {
                        badgeClass = "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
                        label = "PUBLISHED";
                    } else if (r.status === "failed") {
                        badgeClass = "bg-rose-500/10 text-rose-400 border-rose-500/20";
                    }

                    const activeClass = selectedReviewId === id ? "border-cyan-500 bg-white/5 glow-cyan" : "border-white/5 hover:border-white/10 hover:bg-white/5";

                    const item = document.createElement("div");
                    item.className = `p-3 rounded-xl border ${activeClass} cursor-pointer transition duration-150 flex flex-col gap-2`;
                    item.onclick = () => selectReview(id);
                    item.innerHTML = `
                        <div class="flex items-center justify-between">
                            <span class="text-[10px] font-mono text-slate-400 truncate max-w-[140px]">${r.repo_name}</span>
                            <span class="text-[9px] px-2 py-0.5 rounded-full font-bold border ${badgeClass}">${label}</span>
                        </div>
                        <h4 class="text-xs font-semibold text-white line-clamp-2">${r.pr_title}</h4>
                        <div class="flex items-center justify-between text-[10px] text-slate-500">
                            <span>@${r.author}</span>
                            <span>Simulation</span>
                        </div>
                    `;
                    container.appendChild(item);
                });

                if (!selectedReviewId && keys.length > 0 && activeSidebarTab === "reviews") {
                    selectReview(keys[0]);
                }
            } catch (err) {
                console.error("Failed to load reviews:", err);
            }
        }

        async function refreshCIFailures() {
            try {
                const res = await fetch("/api/ci");
                const failures = await res.json();
                ciCache = failures;

                const container = document.getElementById("ci-list");
                container.innerHTML = "";

                let keys = Object.keys(failures).reverse();
                if (keys.length === 0) {
                    container.innerHTML = `<div class="text-center py-8 text-slate-500 text-xs"><p>No CI Failure logs analyzed yet.</p></div>`;
                    return;
                }

                keys.forEach(id => {
                    const f = failures[id];
                    let badgeClass = "bg-rose-500/10 text-rose-400 border-rose-500/20";
                    let label = f.status.toUpperCase();
                    
                    if (f.status === "running") {
                        badgeClass = "bg-amber-500/10 text-amber-400 border-amber-500/20 pulse-effect";
                        label = "ANALYZING...";
                    } else if (f.status === "completed") {
                        badgeClass = f.domain === "code-side" ? "bg-cyan-500/10 text-cyan-400 border-cyan-500/20" : "bg-purple-500/10 text-purple-400 border-purple-500/20";
                        label = f.domain.toUpperCase();
                    }

                    const activeClass = selectedCIId === id ? "border-rose-500 bg-white/5 glow-rose" : "border-white/5 hover:border-white/10 hover:bg-white/5";

                    const item = document.createElement("div");
                    item.className = `p-3 rounded-xl border ${activeClass} cursor-pointer transition duration-150 flex flex-col gap-2`;
                    item.onclick = () => selectCIFailure(id);
                    item.innerHTML = `
                        <div class="flex items-center justify-between">
                            <span class="text-[10px] font-mono text-slate-400 truncate max-w-[140px]">${f.repo_name}</span>
                            <span class="text-[9px] px-2 py-0.5 rounded-full font-bold border ${badgeClass}">${label}</span>
                        </div>
                        <h4 class="text-xs font-semibold text-white line-clamp-2">CI Fail: ${f.failed_step}</h4>
                        <div class="flex items-center justify-between text-[10px] text-slate-500">
                            <span>ID: ${id}</span>
                            <span>Simulation</span>
                        </div>
                    `;
                    container.appendChild(item);
                });

                if (!selectedCIId && keys.length > 0 && activeSidebarTab === "ci") {
                    selectCIFailure(keys[0]);
                }
            } catch (err) {
                console.error("Failed to load CI failures:", err);
            }
        }

        async function refreshIssues() {
            try {
                const res = await fetch("/api/issues");
                const issues = await res.json();
                issuesCache = issues;

                const container = document.getElementById("issues-list");
                container.innerHTML = "";

                let keys = Object.keys(issues).reverse();
                if (keys.length === 0) {
                    container.innerHTML = `<div class="text-center py-8 text-slate-500 text-xs"><p>No GitHub Issues analyzed yet.</p></div>`;
                    return;
                }

                keys.forEach(id => {
                    const iss = issues[id];
                    let badgeClass = "bg-cyan-500/10 text-cyan-400 border-cyan-500/20";
                    let label = iss.status.toUpperCase();
                    
                    if (iss.status === "running") {
                        badgeClass = "bg-amber-500/10 text-amber-400 border-amber-500/20 pulse-effect";
                        label = "ANALYZING...";
                    } else if (iss.status === "completed") {
                        badgeClass = iss.criticality === "critical" ? "bg-rose-500/10 text-rose-400 border-rose-500/20" : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
                        label = iss.criticality.toUpperCase();
                    }

                    const activeClass = selectedIssueId === id ? "border-cyan-500 bg-white/5 glow-cyan" : "border-white/5 hover:border-white/10 hover:bg-white/5";

                    const item = document.createElement("div");
                    item.className = `p-3 rounded-xl border ${activeClass} cursor-pointer transition duration-150 flex flex-col gap-2`;
                    item.onclick = () => selectIssue(id);
                    item.innerHTML = `
                        <div class="flex items-center justify-between">
                            <span class="text-[10px] font-mono text-slate-400 truncate max-w-[140px]">${iss.repo_name}</span>
                            <span class="text-[9px] px-2 py-0.5 rounded-full font-bold border ${badgeClass}">${label}</span>
                        </div>
                        <h4 class="text-xs font-semibold text-white line-clamp-2">Issue #${iss.issue_number}: ${iss.issue_title}</h4>
                        <div class="flex items-center justify-between text-[10px] text-slate-500">
                            <span>@${iss.author}</span>
                            <span>Simulation</span>
                        </div>
                    `;
                    container.appendChild(item);
                });

                if (!selectedIssueId && keys.length > 0 && activeSidebarTab === "issues") {
                    selectIssue(keys[0]);
                }
            } catch (err) {
                console.error("Failed to load issues:", err);
            }
        }

        async function selectReview(id) {
            if (!id) return;
            selectedReviewId = id;
            
            document.getElementById("empty-detail-state").classList.add("hidden");
            document.getElementById("active-detail-content").classList.remove("hidden");
            document.getElementById("active-ci-detail-content").classList.add("hidden");

            // Instantly style active sidebar
            document.querySelectorAll("#reviews-list > div").forEach(item => {
                item.classList.remove("border-cyan-500", "bg-white/5", "glow-cyan");
                item.classList.add("border-white/5", "hover:border-white/10", "hover:bg-white/5");
            });

            let r = reviewsCache[id];
            try {
                const res = await fetch(`/api/reviews/${id}`);
                if (res.ok) {
                    r = await res.json();
                    reviewsCache[id] = r;
                }
            } catch (err) {}

            if (!r) return;

            document.getElementById("detail-repo").textContent = r.repo_name;
            document.getElementById("detail-author").textContent = `@${r.author}`;
            document.getElementById("detail-title").textContent = r.pr_title;
            document.getElementById("detail-id").textContent = r.pr_id;

            const badge = document.getElementById("detail-badge");
            badge.className = "px-3 py-1 rounded-full text-xs font-medium border";
            if (r.status === "running") {
                badge.classList.add("bg-cyan-500/10", "text-cyan-400", "border-cyan-500/20", "pulse-effect");
                badge.textContent = "Pipeline Running";
            } else if (r.status === "completed") {
                badge.classList.add("bg-emerald-500/10", "text-emerald-400", "border-emerald-500/20");
                badge.textContent = "Review Completed";
            } else {
                badge.classList.add("bg-rose-500/10", "text-rose-400", "border-rose-500/20");
                badge.textContent = r.status.toUpperCase();
            }

            // Stepper
            const step1 = document.getElementById("step-webhook");
            const step2 = document.getElementById("step-agents");
            const step3 = document.getElementById("step-gate");
            
            step1.className = "h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/40";
            if (r.status === "running") {
                step2.className = "h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs bg-cyan-500/20 text-cyan-400 border border-cyan-500/50 pulse-effect glow-cyan";
                step3.className = "h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs bg-slate-800 text-slate-400 border border-slate-700";
            } else {
                step2.className = "h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/40";
                step3.className = "h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/50 glow-green";
            }

            renderGitDiff(r.diff);

            document.getElementById("tab-content-consolidated").innerHTML = r.consolidated_report 
                ? safeParseMarkdown(r.consolidated_report) 
                : `<div class="text-center py-8 text-slate-500"><p class="text-sm">Generating token-optimized report summary...</p></div>`;
            
            document.getElementById("tab-content-security").innerHTML = r.security_report 
                ? safeParseMarkdown(r.security_report) 
                : `<div class="text-center py-8 text-slate-500"><p class="text-sm">Scanning code for OWASP Top 10 vulnerabilities...</p></div>`;
            
            document.getElementById("tab-content-quality").innerHTML = r.quality_report 
                ? safeParseMarkdown(r.quality_report) 
                : `<div class="text-center py-8 text-slate-500"><p class="text-sm">Evaluating linter formatting and complexity triggers...</p></div>`;
            
            document.getElementById("test-markdown-report").innerHTML = r.test_report 
                ? safeParseMarkdown(r.test_report) 
                : `<div class="text-center py-8 text-slate-500"><p class="text-sm">Synthesizing and scanning test coverages...</p></div>`;
            
            
            document.getElementById("tab-content-doc").innerHTML = r.documentation_report 
                ? safeParseMarkdown(r.documentation_report) 
                : `<div class="text-center py-8 text-slate-500"><p class="text-sm">Scanning PEP-257 docstring rules...</p></div>`;

            switchTab(activeTab);
        }

        async function selectCIFailure(id) {
            if (!id) return;
            selectedCIId = id;

            document.getElementById("empty-detail-state").classList.add("hidden");
            document.getElementById("active-detail-content").classList.add("hidden");
            document.getElementById("active-ci-detail-content").classList.remove("hidden");

            // Style active sidebar item
            document.querySelectorAll("#ci-list > div").forEach(item => {
                item.classList.remove("border-rose-500", "bg-white/5", "glow-rose");
                item.classList.add("border-white/5", "hover:border-white/10", "hover:bg-white/5");
            });

            let f = ciCache[id];
            try {
                const res = await fetch(`/api/ci/${id}`);
                if (res.ok) {
                    f = await res.json();
                    ciCache[id] = f;
                }
            } catch (err) {}

            if (!f) return;

            document.getElementById("ci-detail-repo").textContent = f.repo_name;
            document.getElementById("ci-detail-step").textContent = f.failed_step;
            document.getElementById("ci-detail-id").textContent = f.workflow_id;

            const badge = document.getElementById("ci-detail-badge");
            badge.className = "px-3 py-1 rounded-full text-xs font-medium border";
            if (f.status === "running") {
                badge.classList.add("bg-amber-500/10", "text-amber-400", "border-amber-500/20", "pulse-effect");
                badge.textContent = "AI Analysis Running";
                
                document.getElementById("ci-detail-domain").className = "hidden";
                document.getElementById("ci-action-indicator").innerHTML = ``;
            } else if (f.status === "completed") {
                badge.classList.add("bg-emerald-500/10", "text-emerald-400", "border-emerald-500/20");
                badge.textContent = "Diagnosed";
                
                const domBadge = document.getElementById("ci-detail-domain");
                domBadge.className = "px-3 py-0.5 rounded-lg text-xs font-mono font-bold uppercase border";
                domBadge.textContent = f.domain;
                if (f.domain === "code-side") {
                    domBadge.classList.add("bg-cyan-500/10", "text-cyan-400", "border-cyan-500/30");
                    document.getElementById("ci-action-indicator").innerHTML = `<i data-lucide="message-square" class="h-3.5 w-3.5"></i> Posted Comment to PR`;
                } else {
                    domBadge.classList.add("bg-purple-500/10", "text-purple-400", "border-purple-500/30");
                    document.getElementById("ci-action-indicator").innerHTML = `<i data-lucide="plus-circle" class="h-3.5 w-3.5 text-purple-400"></i> Opened GitHub Alert Issue`;
                }
            } else {
                badge.classList.add("bg-rose-500/10", "text-rose-400", "border-rose-500/20");
                badge.textContent = f.status.toUpperCase();
            }

            if (typeof lucide !== 'undefined') lucide.createIcons();

            document.getElementById("tab-content-ci-report").innerHTML = f.report 
                ? safeParseMarkdown(f.report) 
                : `<div class="text-center py-8 text-slate-500"><p class="text-sm">Analysing console trace logs and writing code fix suggestions...</p></div>`;
            
            document.getElementById("ci-detail-stacktrace").textContent = f.stacktrace || "Awaiting extraction...";
            document.getElementById("ci-detail-raw").textContent = f.raw_logs || "No logs available.";

            switchCITab(activeCITab);
        }

        async function selectIssue(id) {
            if (!id) return;
            selectedIssueId = id;

            document.getElementById("empty-detail-state").classList.add("hidden");
            document.getElementById("active-detail-content").classList.add("hidden");
            document.getElementById("active-ci-detail-content").classList.add("hidden");
            document.getElementById("active-issue-detail-content").classList.remove("hidden");

            // Style active sidebar item
            document.querySelectorAll("#issues-list > div").forEach(item => {
                item.classList.remove("border-cyan-500", "bg-white/5", "glow-cyan");
                item.classList.add("border-white/5", "hover:border-white/10", "hover:bg-white/5");
            });

            let iss = issuesCache[id];
            try {
                const res = await fetch(`/api/issues/${id}`);
                if (res.ok) {
                    iss = await res.json();
                    issuesCache[id] = iss;
                }
            } catch (err) {}

            if (!iss) return;

            document.getElementById("issue-detail-repo").textContent = iss.repo_name;
            document.getElementById("issue-detail-author").textContent = `@${iss.author}`;
            document.getElementById("issue-detail-title").textContent = `Issue #${iss.issue_number}: ${iss.issue_title}`;
            document.getElementById("issue-detail-id").textContent = iss.issue_id;

            const badge = document.getElementById("issue-detail-badge");
            badge.className = "px-3 py-1 rounded-full text-xs font-medium border";
            if (iss.status === "running") {
                badge.classList.add("bg-amber-500/10", "text-amber-400", "border-amber-500/20", "pulse-effect");
                badge.textContent = "AI Analysis Running";
                
                document.getElementById("issue-detail-criticality").className = "hidden";
            } else if (iss.status === "completed") {
                badge.classList.add("bg-emerald-500/10", "text-emerald-400", "border-emerald-500/20");
                badge.textContent = "Analyzed";
                
                const critBadge = document.getElementById("issue-detail-criticality");
                critBadge.className = "px-3 py-0.5 rounded-lg text-xs font-mono font-bold uppercase border";
                critBadge.textContent = iss.criticality;
                if (iss.criticality === "critical") {
                    critBadge.classList.add("bg-rose-500/10", "text-rose-400", "border-rose-500/30", "glow-rose");
                } else {
                    critBadge.classList.add("bg-emerald-500/10", "text-emerald-400", "border-emerald-500/30");
                }
            } else {
                badge.classList.add("bg-rose-500/10", "text-rose-400", "border-rose-500/20");
                badge.textContent = iss.status.toUpperCase();
            }

            if (typeof lucide !== 'undefined') lucide.createIcons();

            document.getElementById("tab-content-issue-report").innerHTML = iss.report 
                ? safeParseMarkdown(iss.report) 
                : `<div class="text-center py-8 text-slate-500"><p class="text-sm">Analysing issue context and preparing diagnostic remedy...</p></div>`;
            
            document.getElementById("issue-target-filename").textContent = iss.target_file || "None";
            document.getElementById("issue-detail-file-code").textContent = iss.file_content || "No source code pulled for this issue.";
            document.getElementById("issue-detail-raw-body").textContent = (iss.issue_title + "\n\n" + (iss.issue_body || "No description provided."));

            switchIssueTab(activeIssueTab);
        }

        function switchIssueTab(tab) {
            activeIssueTab = tab;
            document.querySelectorAll(".tab-pane-issue").forEach(pane => pane.classList.add("hidden"));
            document.getElementById(`tab-content-${tab}`).classList.remove("hidden");
            
            const tabButtons = ["issue-report", "issue-file", "issue-raw"];
            tabButtons.forEach(t => {
                const btn = document.getElementById(`tab-btn-${t}`);
                if (btn) {
                    if (t === tab) {
                        btn.classList.add("border-cyan-500", "text-cyan-400");
                        btn.classList.remove("border-transparent", "text-slate-400");
                    } else {
                        btn.classList.add("border-transparent", "text-slate-400");
                        btn.classList.remove("border-cyan-500", "text-cyan-400");
                    }
                }
            });
        }

        function switchTab(tab) {
            activeTab = tab;
            document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.add("hidden"));
            document.getElementById(`tab-content-${tab}`).classList.remove("hidden");
            
            const tabButtons = ["consolidated", "security", "quality", "test", "doc", "diff"];
            tabButtons.forEach(t => {
                const btn = document.getElementById(`tab-btn-${t}`);
                if (t === tab) {
                    btn.classList.add("border-cyan-500", "text-cyan-400");
                    btn.classList.remove("border-transparent", "text-slate-400");
                } else {
                    btn.classList.add("border-transparent", "text-slate-400");
                    btn.classList.remove("border-cyan-500", "text-cyan-400");
                }
            });
        }

        function switchCITab(tab) {
            activeCITab = tab;
            document.querySelectorAll(".tab-pane-ci").forEach(pane => pane.classList.add("hidden"));
            document.getElementById(`tab-content-${tab}`).classList.remove("hidden");
            
            const tabButtons = ["ci-report", "ci-stacktrace", "ci-raw"];
            tabButtons.forEach(t => {
                const btn = document.getElementById(`tab-btn-${t}`);
                if (t === tab) {
                    btn.classList.add("border-rose-500", "text-rose-400");
                    btn.classList.remove("border-transparent", "text-slate-400");
                } else {
                    btn.classList.add("border-transparent", "text-slate-400");
                    btn.classList.remove("border-rose-500", "text-rose-400");
                }
            });
        }

        function toggleSettingsModal() {
            document.getElementById("settings-modal").classList.toggle("hidden");
        }

        async function pollActiveJobs() {
            if (activeSidebarTab === "reviews" && selectedReviewId) {
                const r = reviewsCache[selectedReviewId];
                if (r && r.status === "running") {
                    try {
                        const res = await fetch(`/api/reviews/${selectedReviewId}`);
                        if (res.ok) {
                            const latest = await res.json();
                            if (latest.status !== r.status) {
                                await refreshReviews();
                                selectReview(selectedReviewId);
                            }
                        }
                    } catch (e) {}
                }
            } else if (activeSidebarTab === "ci" && selectedCIId) {
                const f = ciCache[selectedCIId];
                if (f && f.status === "running") {
                    try {
                        const res = await fetch(`/api/ci/${selectedCIId}`);
                        if (res.ok) {
                            const latest = await res.json();
                            if (latest.status !== f.status) {
                                await refreshCIFailures();
                                selectCIFailure(selectedCIId);
                            }
                        }
                    } catch (e) {}
                }
            } else if (activeSidebarTab === "issues" && selectedIssueId) {
                const iss = issuesCache[selectedIssueId];
                if (iss && iss.status === "running") {
                    try {
                        const res = await fetch(`/api/issues/${selectedIssueId}`);
                        if (res.ok) {
                            const latest = await res.json();
                            if (latest.status !== iss.status) {
                                await refreshIssues();
                                selectIssue(selectedIssueId);
                            }
                        }
                    } catch (e) {}
                }
            }
        }

        async function loadSettings() {
            try {
                const response = await fetch("/api/settings");
                const data = await response.json();
                document.getElementById("settings-provider").value = data.llm_provider;
                document.getElementById("settings-model").value = data.llm_model || "";
                document.getElementById("settings-openai-key").value = data.openai_api_key;
                document.getElementById("settings-gemini-key").value = data.gemini_api_key;
                document.getElementById("settings-anthropic-key").value = data.anthropic_api_key;
                document.getElementById("settings-groq-key").value = data.groq_api_key;
                document.getElementById("settings-teams").value = data.teams_webhook_url || "";
                document.getElementById("settings-secret").value = data.github_webhook_secret;
                toggleProviderFields(data.llm_provider);
            } catch (err) {}
        }

        function toggleProviderFields(provider) {
            document.getElementById("field-model").style.display = "block";
            document.getElementById("field-openai").style.display = provider === "openai" ? "block" : "none";
            document.getElementById("field-gemini").style.display = provider === "gemini" ? "block" : "none";
            document.getElementById("field-anthropic").style.display = provider === "anthropic" ? "block" : "none";
            document.getElementById("field-groq").style.display = provider === "groq" ? "block" : "none";
        }

        async function saveSettings() {
            const provider = document.getElementById("settings-provider").value;
            const model = document.getElementById("settings-model").value;
            const openai = document.getElementById("settings-openai-key").value;
            const gemini = document.getElementById("settings-gemini-key").value;
            const anthropic = document.getElementById("settings-anthropic-key").value;
            const groq = document.getElementById("settings-groq-key").value;
            const teams = document.getElementById("settings-teams").value;

            try {
                const res = await fetch("/api/settings", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        llm_provider: provider,
                        openai_api_key: openai,
                        gemini_api_key: gemini,
                        anthropic_api_key: anthropic,
                        groq_api_key: groq,
                        llm_model: model,
                        teams_webhook_url: teams
                    })
                });
                if (res.ok) {
                    alert("Settings updated successfully!");
                    toggleSettingsModal();
                    loadSettings();
                }
            } catch (err) {
                alert("Error saving configurations.");
            }
        }

        function renderGitDiff(diffText) {
            const container = document.getElementById("diff-visual-container");
            if (!container) return;
            container.innerHTML = "";
            
            if (!diffText) {
                container.innerHTML = `<div class="p-8 text-center text-slate-500">No diff contents available.</div>`;
                return;
            }
            
            const lines = diffText.split("\\n");
            lines.forEach(line => {
                const lineEl = document.createElement("div");
                lineEl.className = "py-1 px-4 border-l-4 border-transparent select-none whitespace-pre-wrap";
                
                if (line.startsWith("diff --git") || line.startsWith("index ")) {
                    lineEl.className = "py-1.5 px-4 bg-slate-900/60 text-slate-400 font-semibold border-b border-white/5 font-mono text-[11px]";
                    lineEl.textContent = line;
                } else if (line.startsWith("--- a/") || line.startsWith("+++ b/")) {
                    lineEl.className = "py-1.5 px-4 bg-slate-900/40 text-slate-500 font-semibold font-mono text-[11px]";
                    lineEl.textContent = line;
                } else if (line.startsWith("@@")) {
                    lineEl.className = "py-1.5 px-4 bg-cyan-950/30 text-cyan-400 font-semibold border-y border-white/5 font-mono text-[11px]";
                    lineEl.textContent = line;
                } else if (line.startsWith("+") && !line.startsWith("+++")) {
                    lineEl.className = "py-1.5 px-4 bg-emerald-950/30 text-emerald-400 border-l-4 border-emerald-500 font-mono text-[11px] whitespace-pre-wrap";
                    lineEl.textContent = line;
                } else if (line.startsWith("-") && !line.startsWith("---")) {
                    lineEl.className = "py-1.5 px-4 bg-rose-950/30 text-rose-400 border-l-4 border-rose-500 font-mono text-[11px] whitespace-pre-wrap";
                    lineEl.textContent = line;
                } else {
                    lineEl.className = "py-1 px-4 text-slate-300 font-mono text-[11px] whitespace-pre-wrap";
                    lineEl.textContent = line;
                }
                container.appendChild(lineEl);
            });
        }
    </script>
</body>
</html>
"""
