DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en" class="h-full bg-slate-950 text-slate-100">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Automated Code Review Pipeline Dashboard</title>
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
            <div class="h-9 w-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-500 flex items-center justify-center glow-cyan">
                <i data-lucide="shield-check" class="h-5 w-5 text-white"></i>
            </div>
            <div>
                <span class="font-bold text-lg bg-gradient-to-r from-cyan-400 via-indigo-200 to-white bg-clip-text text-transparent">
                    OpenReviewer
                </span>
                <span class="ml-2 text-xs font-mono px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                    Local LangGraph Pipeline
                </span>
            </div>
        </div>
        
        <div class="flex items-center gap-6">
            <div class="flex items-center gap-2 text-xs font-medium text-slate-400 bg-slate-900 border border-white/5 py-1 px-3 rounded-lg">
                <span class="h-2 w-2 rounded-full bg-emerald-500 pulse-effect"></span>
                System active
            </div>
            <button onclick="toggleSettingsModal()" class="p-2 text-slate-400 hover:text-white transition-colors duration-150 relative">
                <i data-lucide="settings" class="h-5 w-5"></i>
            </button>
        </div>
    </header>

    <!-- Main Workspace -->
    <main class="flex-1 overflow-hidden flex flex-row">

        <!-- Left Sidebar: Review Jobs List -->
        <aside class="w-80 border-r border-white/5 bg-slate-950/20 shrink-0 flex flex-col overflow-hidden">
            <div class="p-4 border-b border-white/5 flex items-center justify-between">
                <h2 class="text-sm font-semibold text-slate-300">Pull Request Reviews</h2>
                <button onclick="refreshReviews()" class="p-1.5 hover:bg-white/5 text-slate-400 hover:text-white rounded-lg transition">
                    <i data-lucide="refresh-cw" class="h-4 w-4"></i>
                </button>
            </div>
            
            <!-- Sleek Interactive Filters -->
            <div class="px-4 py-2 border-b border-white/5 flex gap-1.5 bg-slate-950/40">
                <button onclick="setFilter('all')" id="filter-btn-all" class="text-[10px] px-2.5 py-1 rounded-lg font-semibold transition bg-cyan-600/20 text-cyan-400 border border-cyan-500/30">All</button>
                <button onclick="setFilter('active')" id="filter-btn-active" class="text-[10px] px-2.5 py-1 rounded-lg font-semibold transition bg-slate-900/50 text-slate-400 border border-white/5 hover:text-white">Active</button>
                <button onclick="setFilter('processed')" id="filter-btn-processed" class="text-[10px] px-2.5 py-1 rounded-lg font-semibold transition bg-slate-900/50 text-slate-400 border border-white/5 hover:text-white">Processed</button>
            </div>
            
            <div id="reviews-list" class="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-2">
                <!-- Loaded dynamically -->
                <div class="text-center py-8 text-slate-500 text-xs">
                    <p>No pull requests reviewed yet.</p>
                </div>
            </div>
            
            <!-- Quick Actions Footer -->
            <div class="p-4 border-t border-white/5 bg-slate-950/40">
                <button onclick="toggleTriggerModal()" class="w-full bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-medium text-sm py-2 px-4 rounded-xl transition duration-150 flex items-center justify-center gap-2 shadow-lg shadow-indigo-950/50">
                    <i data-lucide="play" class="h-4 w-4"></i>
                    Simulate PR Review
                </button>
            </div>
        </aside>

        <!-- Right / Core Panel: Selected Review details -->
        <section id="detail-panel" class="flex-1 overflow-hidden flex flex-col bg-slate-950/10">
            <!-- Empty State -->
            <div id="empty-detail-state" class="flex-1 flex flex-col items-center justify-center text-center p-8">
                <div class="h-16 w-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-slate-400 mb-4">
                    <i data-lucide="git-pull-request" class="h-8 w-8"></i>
                </div>
                <h3 class="font-medium text-slate-200 text-lg">No Pull Request Selected</h3>
                <p class="text-slate-400 text-sm max-w-sm mt-1">Select an active pull request from the sidebar or simulate a mock event to see the LangGraph review pipeline in action.</p>
            </div>

            <!-- Detail Grid -->
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
                            <span class="font-medium text-slate-400">Approval Gate</span>
                        </div>
                        <i data-lucide="chevron-right" class="h-4 w-4 text-slate-600"></i>
                        <div class="flex items-center gap-2">
                            <span id="step-publish" class="h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs bg-slate-800 text-slate-400 border border-slate-700">4</span>
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
                    <div id="tab-content-consolidated" class="tab-pane markdown-body">
                        <!-- Loaded dynamically -->
                    </div>

                    <!-- Security Tab -->
                    <div id="tab-content-security" class="tab-pane hidden markdown-body">
                        <!-- Loaded dynamically -->
                    </div>

                    <!-- Quality Tab -->
                    <div id="tab-content-quality" class="tab-pane hidden markdown-body">
                        <!-- Loaded dynamically -->
                    </div>

                    <!-- Test Tab -->
                    <div id="tab-content-test" class="tab-pane hidden space-y-6">
                        <!-- AI Analysis Report -->
                        <div id="test-markdown-report" class="markdown-body">
                            <!-- Loaded dynamically -->
                        </div>
                        
                        <!-- Automated PR Test Runner -->
                        <div class="mt-8 border border-white/10 rounded-2xl bg-slate-900/40 p-6">
                            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                                <div>
                                    <h3 class="text-sm font-bold text-white flex items-center gap-2">
                                        <i data-lucide="play-circle" class="h-4 w-4 text-cyan-400"></i>
                                        Automated PR Test Suite Runner
                                    </h3>
                                    <p class="text-xs text-slate-400 mt-1">Dynamically execute the unit test harness for the modifications introduced in this PR.</p>
                                </div>
                                <button onclick="runPRTests()" id="run-tests-btn" class="px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs transition duration-150 flex items-center gap-2 shrink-0 shadow-lg shadow-cyan-950/50">
                                    <i data-lucide="play" class="h-3.5 w-3.5"></i>
                                    Execute Test Harness
                                </button>
                            </div>
                            
                            <!-- Loading Indicator -->
                            <div id="tests-loading" class="hidden mt-6 flex flex-col items-center justify-center py-10 bg-slate-950/40 border border-white/5 rounded-xl">
                                <div class="h-8 w-8 rounded-full border-4 border-cyan-500/20 border-t-cyan-400 animate-spin mb-3"></div>
                                <span class="text-xs text-slate-400 font-medium">Spawning Python environment & running pytest...</span>
                            </div>
                            
                            <!-- Results Container -->
                            <div id="tests-results" class="hidden mt-6 space-y-5">
                                <div class="grid grid-cols-3 gap-4">
                                    <div class="bg-slate-950/50 border border-white/5 rounded-xl p-3 text-center">
                                        <span class="block text-[10px] uppercase font-bold tracking-wider text-slate-500">Passed Asserts</span>
                                        <span class="block text-xl font-bold text-emerald-400 mt-1" id="test-stat-passed">0/0</span>
                                    </div>
                                    <div class="bg-slate-950/50 border border-white/5 rounded-xl p-3 text-center">
                                        <span class="block text-[10px] uppercase font-bold tracking-wider text-slate-500">Coverage Pct</span>
                                        <span class="block text-xl font-bold text-cyan-400 mt-1" id="test-stat-coverage">0%</span>
                                    </div>
                                    <div class="bg-slate-950/50 border border-white/5 rounded-xl p-3 text-center">
                                        <span class="block text-[10px] uppercase font-bold tracking-wider text-slate-500">Execution Time</span>
                                        <span class="block text-xl font-bold text-slate-300 mt-1" id="test-stat-duration">0.0s</span>
                                    </div>
                                </div>
                                
                                <div class="rounded-xl border border-emerald-500/10 bg-emerald-500/5 p-4 flex gap-3 items-start">
                                    <i data-lucide="check-circle" class="h-5 w-5 text-emerald-400 shrink-0 mt-0.5"></i>
                                    <div>
                                        <span class="text-xs font-semibold text-emerald-400">All PR Tests Passed Successfully!</span>
                                        <p class="text-[11px] text-slate-400 mt-1">Pytest exited with status code 0. No functional regressions detected.</p>
                                    </div>
                                </div>
                                
                                <div>
                                    <span class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Stdout logs</span>
                                    <pre class="bg-slate-950 border border-white/5 p-4 rounded-xl text-[11px] font-mono text-slate-300 max-h-60 overflow-y-auto custom-scrollbar" id="test-stat-console"></pre>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Doc Tab -->
                    <div id="tab-content-doc" class="tab-pane hidden markdown-body">
                        <!-- Loaded dynamically -->
                    </div>

                    <!-- Diff Tab -->
                    <div id="tab-content-diff" class="tab-pane hidden">
                        <div id="diff-visual-container" class="space-y-0.5 rounded-xl overflow-hidden font-mono text-xs border border-white/5 bg-slate-950/60 p-1"></div>
                    </div>
                </div>

                <!-- Action Footer (Human Gate Controller) -->
                <div id="approval-gate-box" class="hidden p-6 border-t border-white/5 bg-slate-900/60 flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
                    <div class="w-full md:flex-1">
                        <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Gate Feedback / Adjustments</label>
                        <input type="text" id="approval-feedback" placeholder="Add comments here before approval (e.g. 'Security issues are valid, refactor before merging')..." class="w-full bg-slate-950 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition duration-150">
                    </div>
                    <div class="flex gap-3 shrink-0 w-full md:w-auto justify-end">
                        <button onclick="submitDecision('reject')" class="flex-1 md:flex-initial px-5 py-2.5 rounded-xl border border-rose-500/30 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 font-semibold text-sm transition duration-150 flex items-center justify-center gap-2">
                            <i data-lucide="x" class="h-4 w-4"></i>
                            Reject Review
                        </button>
                        <button onclick="submitDecision('approve')" class="flex-1 md:flex-initial px-5 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-sm transition duration-150 flex items-center justify-center gap-2 glow-cyan">
                            <i data-lucide="check" class="h-4 w-4"></i>
                            Approve & Publish
                        </button>
                    </div>
                </div>
            </div>
        </section>

    </main>

    <!-- Trigger Modal -->
    <div id="trigger-modal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="glass-panel w-full max-w-2xl rounded-2xl overflow-hidden flex flex-col max-h-[90vh]">
            <div class="p-5 border-b border-white/5 flex items-center justify-between bg-slate-900/50">
                <div class="flex items-center gap-2">
                    <i data-lucide="play-circle" class="h-5 w-5 text-cyan-400"></i>
                    <h3 class="font-bold text-white text-base">Simulate GitHub Pull Request Event</h3>
                </div>
                <button onclick="toggleTriggerModal()" class="text-slate-400 hover:text-white">
                    <i data-lucide="x" class="h-5 w-5"></i>
                </button>
            </div>
            
            <div class="p-6 overflow-y-auto space-y-4 custom-scrollbar">
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Repository Name</label>
                        <input type="text" id="trigger-repo" value="octocat/hello-world" class="w-full bg-slate-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-slate-100 focus:outline-none focus:border-cyan-500">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Author (Developer)</label>
                        <input type="text" id="trigger-author" value="johndoe-dev" class="w-full bg-slate-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-slate-100 focus:outline-none focus:border-cyan-500">
                    </div>
                </div>
                
                <div>
                    <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">PR Title</label>
                    <input type="text" id="trigger-title" value="feat: add SQL execution layer and API access key configs" class="w-full bg-slate-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-slate-100 focus:outline-none focus:border-cyan-500">
                </div>

                <div>
                    <div class="flex items-center justify-between mb-2">
                        <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Select Diff Template</label>
                        <span class="text-[10px] text-cyan-400 font-mono">Simulates real vulnerability analysis</span>
                    </div>
                    <select onchange="loadTemplate(this.value)" class="w-full bg-slate-900 border border-white/10 rounded-xl px-4 py-2 text-sm text-slate-100 focus:outline-none focus:border-cyan-500">
                        <option value="vulnerability">Template 1: OWASP Security Flaw (SQL injection & Exposed Stripe Secret Key)</option>
                        <option value="lint">Template 2: Clean code but Missing Documentation & Docstrings</option>
                        <option value="test">Template 3: Highly Nested Complex Math Function (Zero Test coverage)</option>
                    </select>
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Git Diff Content</label>
                    <textarea id="trigger-diff" rows="8" class="w-full bg-slate-900 border border-white/10 rounded-xl p-4 text-xs font-mono text-cyan-300 focus:outline-none focus:border-cyan-500 custom-scrollbar"></textarea>
                </div>
            </div>
            
            <div class="p-5 border-t border-white/5 bg-slate-900/50 flex justify-end gap-3">
                <button onclick="toggleTriggerModal()" class="px-4 py-2 rounded-xl text-slate-400 hover:text-white font-medium text-sm transition">
                    Cancel
                </button>
                <button onclick="runTriggerPipeline()" class="px-5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-sm transition duration-150 flex items-center gap-2 shadow-lg shadow-cyan-950/50">
                    <i data-lucide="play" class="h-4 w-4"></i>
                    Start LangGraph Pipeline
                </button>
            </div>
        </div>
    </div>

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
                        <option value="mock">Offline Mock Simulator (Instant, Cost-Free)</option>
                        <option value="openai">OpenAI GPT Models</option>
                        <option value="gemini">Google Gemini Models</option>
                        <option value="anthropic">Anthropic Claude Models</option>
                        <option value="groq">Groq Llama 3.3 Models</option>
                    </select>
                    <p class="text-[10px] text-slate-500 mt-1">If Mock is chosen, AI agents generate realistic contextual responses instantly without hitting any external API keys.</p>
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
                    <p class="text-[10px] text-slate-500 mt-1">If specified, the server POSTs a premium Adaptive Card to Teams upon review approval.</p>
                </div>

                <div class="border-t border-white/5 pt-4">
                    <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">GitHub Webhook HMAC Secret (Local Endpoint)</label>
                    <input type="text" id="settings-secret" readonly class="w-full bg-slate-950 border border-white/5 rounded-xl px-4 py-2 text-xs font-mono text-slate-400 select-all cursor-not-allowed">
                    <p class="text-[10px] text-slate-500 mt-1">Used to verify standard GitHub payloads. Configure this secret in your GitHub App config.</p>
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

    <!-- Frontend Core Script logic -->
    <script>
        // Core Mock Templates
        const templates = {
            vulnerability: `diff --git a/app/db.py b/app/db.py
index a235bd2..c1e3a98 100644
--- a/app/db.py
+++ b/app/db.py
@@ -10,3 +10,12 @@ def get_user(username):
-    # Safe database implementation
-    return db.query("SELECT * FROM users WHERE username = :name", {"name": username})
+    # FAST implementation to expedite testing
+    # TODO: Refactor parameterized query later
+    stripe_key = "placeholder_key"
+    raw_query = "SELECT * FROM users WHERE username = '" + username + "'"
+    return db.execute(raw_query)
`,
            lint: `diff --git a/app/calculator.py b/app/calculator.py
index b111c11..e222d22 100644
--- a/app/calculator.py
+++ b/app/calculator.py
@@ -1,6 +1,8 @@
 def solve(x, y, op):
-    pass
+    if op == '+':
+        return x + y
+    if op == '-':
+        return x - y
+    if op == '*':
+        return x * y
+    if op == '/':
+        if y == 0:
+            return 0
+        return x / y
`,
            test: `diff --git a/app/auth.py b/app/auth.py
index d333a33..f444b44 100644
--- a/app/auth.py
+++ b/app/auth.py
@@ -1,9 +1,24 @@
+def parse_token_and_extract_claims(auth_header):
+    if not auth_header:
+        return None
+    parts = auth_header.split()
+    if len(parts) != 2:
+        return None
+    scheme, token = parts[0], parts[1]
+    if scheme.lower() != 'bearer':
+        return None
+    
+    # Complex multi-step manual JWT decoding algorithm without dependencies
+    # Checks permissions scope mapping
+    scopes = []
+    if "admin" in token:
+        scopes.append("write")
+        scopes.append("delete")
+    else:
+        scopes.append("read")
+    return {"user": "auth-client", "scopes": scopes, "token": token}
`
        };

        function safeParseMarkdown(text) {
            if (!text) return "";
            if (typeof marked !== 'undefined' && marked && typeof marked.parse === 'function') {
                return marked.parse(text);
            }
            // Fallback for offline/blocked marked.js CDN
            return `<pre class="whitespace-pre-wrap font-sans text-slate-300 text-sm leading-relaxed">${text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")}</pre>`;
        }

        let selectedReviewId = null;
        let activeTab = "consolidated";
        let reviewsCache = {};
        let currentFilter = "all";

        function setFilter(filterType) {
            currentFilter = filterType;
            const filters = ["all", "active", "processed"];
            filters.forEach(f => {
                const btn = document.getElementById(`filter-btn-${f}`);
                if (btn) {
                    if (f === filterType) {
                        btn.className = "text-[10px] px-2.5 py-1 rounded-lg font-semibold transition bg-cyan-600/20 text-cyan-400 border border-cyan-500/30";
                    } else {
                        btn.className = "text-[10px] px-2.5 py-1 rounded-lg font-semibold transition bg-slate-900/50 text-slate-400 border border-white/5 hover:text-white";
                    }
                }
            });
            refreshReviews();
        }

        // Resilient Loader
        window.addEventListener("DOMContentLoaded", () => {
            try {
                if (typeof lucide !== 'undefined' && lucide && typeof lucide.createIcons === 'function') {
                    lucide.createIcons();
                }
            } catch (e) {
                console.warn("Lucide setup skipped:", e);
            }

            try {
                loadTemplate("vulnerability");
            } catch (e) {
                console.warn("loadTemplate setup skipped:", e);
            }

            try {
                refreshReviews();
            } catch (e) {
                console.warn("refreshReviews execution failed:", e);
            }

            try {
                loadSettings();
            } catch (e) {
                console.warn("loadSettings execution failed:", e);
            }
            
            setInterval(pollActiveReview, 3000);
        });

        // Templates loader
        function loadTemplate(key) {
            document.getElementById("trigger-diff").value = templates[key].trim();
        }

        // Toggle Modals
        function toggleTriggerModal() {
            const modal = document.getElementById("trigger-modal");
            modal.classList.toggle("hidden");
            const isHidden = modal.classList.contains("hidden");
            console.log(`🔍 [UI] Simulation modal ${isHidden ? 'closed' : 'opened'}`);
            if (!isHidden) {
                console.log("👉 Choose a code template and click 'Start LangGraph Pipeline' to trigger the automated review flow!");
            }
        }

        function toggleSettingsModal() {
            const modal = document.getElementById("settings-modal");
            modal.classList.toggle("hidden");
        }

        // UI Tab Switcher
        function switchTab(tab) {
            activeTab = tab;
            document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.add("hidden"));
            document.getElementById(`tab-content-${tab}`).classList.remove("hidden");
            
            // Manage Active tab styling
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

        // Fetch Pipeline settings
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
            } catch (err) {
                console.error("Failed to load settings:", err);
            }
        }

        function toggleProviderFields(provider) {
            document.getElementById("field-model").style.display = provider === "mock" ? "none" : "block";
            document.getElementById("field-openai").style.display = provider === "openai" ? "block" : "none";
            document.getElementById("field-gemini").style.display = provider === "gemini" ? "block" : "none";
            document.getElementById("field-anthropic").style.display = provider === "anthropic" ? "block" : "none";
            document.getElementById("field-groq").style.display = provider === "groq" ? "block" : "none";
        }

        // Save settings configuration
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
                } else {
                    alert("Failed to update settings.");
                }
            } catch (err) {
                alert("Error saving settings.");
            }
        }

        // Trigger local pipeline
        async function runTriggerPipeline() {
            const repo = document.getElementById("trigger-repo").value;
            const author = document.getElementById("trigger-author").value;
            const title = document.getElementById("trigger-title").value;
            const diff = document.getElementById("trigger-diff").value;

            console.log("🚀 [Simulation Trigger] Clicked 'Start LangGraph Pipeline'");
            console.log(`   ├─ Repo:   ${repo}`);
            console.log(`   ├─ Author: @${author}`);
            console.log(`   ├─ Title:  "${title}"`);
            console.log(`   └─ Sending POST to /api/reviews/mock-trigger...`);

            try {
                const startTime = performance.now();
                const res = await fetch("/api/reviews/mock-trigger", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        pr_title: title,
                        repo_name: repo,
                        author: author,
                        diff: diff
                    })
                });
                
                const data = await res.json();
                const duration = ((performance.now() - startTime) / 1000).toFixed(3);
                
                if (data.status === "accepted") {
                    console.log(`✅ [Simulation Trigger] Success (Response time: ${duration}s)`);
                    console.log(`   └─ Assigned PR ID: ${data.pr_id}`);
                    toggleTriggerModal();
                    
                    if (currentFilter === "processed") {
                        setFilter("all");
                    } else {
                        await refreshReviews();
                    }
                    selectReview(data.pr_id);
                } else {
                    console.error("❌ [Simulation Trigger] Server rejected the request:", data);
                }
            } catch (err) {
                console.error("❌ [Simulation Trigger] Fetch error encountered:", err);
                alert("Failed to trigger review pipeline.");
            }
        }

        // Fetch and refresh reviews
        async function refreshReviews() {
            try {
                const res = await fetch("/api/reviews");
                const reviews = await res.json();
                reviewsCache = reviews;

                const container = document.getElementById("reviews-list");
                container.innerHTML = "";

                let keys = Object.keys(reviews).reverse();
                
                // Apply dynamic filters
                if (currentFilter === "active") {
                    keys = keys.filter(id => reviews[id].status === "running" || reviews[id].status === "pending" || reviews[id].status === "processing_decision");
                } else if (currentFilter === "processed") {
                    keys = keys.filter(id => reviews[id].status === "completed" || reviews[id].status === "approved" || reviews[id].status === "rejected");
                }

                if (keys.length === 0) {
                    container.innerHTML = `<div class="text-center py-8 text-slate-500 text-xs"><p>No ${currentFilter !== 'all' ? currentFilter + ' ' : ''}pull requests found.</p></div>`;
                    return;
                }

                keys.forEach(id => {
                    const r = reviews[id];
                    let badgeClass = "";
                    let statusLabel = r.status.toUpperCase();

                    if (r.status === "running") {
                        badgeClass = "bg-cyan-500/10 text-cyan-400 border-cyan-500/20 pulse-effect";
                    } else if (r.status === "pending") {
                        badgeClass = "bg-amber-500/10 text-amber-400 border-amber-500/20";
                        statusLabel = "AWAITING GATE";
                    } else if (r.status === "completed" || r.status === "approved") {
                        badgeClass = "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
                    } else if (r.status === "rejected") {
                        badgeClass = "bg-rose-500/10 text-rose-400 border-rose-500/20";
                    } else {
                        badgeClass = "bg-slate-500/10 text-slate-400 border-white/5";
                    }

                    const activeClass = selectedReviewId === id ? "border-cyan-500 bg-white/5 glow-cyan" : "border-white/5 hover:border-white/10 hover:bg-white/5";

                    const item = document.createElement("div");
                    item.className = `p-3 rounded-xl border ${activeClass} cursor-pointer transition duration-150 flex flex-col gap-2`;
                    item.onclick = () => selectReview(id);
                    item.innerHTML = `
                        <div class="flex items-center justify-between">
                            <span class="text-[10px] font-mono text-slate-400 truncate max-w-[140px]">${r.repo_name}</span>
                            <span class="text-[9px] px-2 py-0.5 rounded-full font-bold border ${badgeClass}">${statusLabel}</span>
                        </div>
                        <h4 class="text-xs font-semibold text-white line-clamp-2">${r.pr_title}</h4>
                        <div class="flex items-center justify-between text-[10px] text-slate-500">
                            <span>@${r.author}</span>
                            <span>${id.startsWith("mock-") ? "Local Simulation" : "GitHub Hook"}</span>
                        </div>
                    `;
                    container.appendChild(item);
                });

                // Auto-select the latest active review when the page first loads
                if (!selectedReviewId && keys.length > 0) {
                    selectReview(keys[0]);
                }
            } catch (err) {
                console.error("Failed to load reviews:", err);
            }
        }

        // Selection Controller
        async function selectReview(id) {
            if (!id) return;
            selectedReviewId = id;
            
            // Instantly apply active highlight to the selected sidebar item
            document.querySelectorAll("#reviews-list > div").forEach(item => {
                item.classList.remove("border-cyan-500", "bg-white/5", "glow-cyan");
                item.classList.add("border-white/5", "hover:border-white/10", "hover:bg-white/5");
            });
            
            // Try fetching the absolute latest state from the server directly to avoid race conditions
            let r = reviewsCache[id];
            try {
                const res = await fetch(`/api/reviews/${id}`);
                if (res.ok) {
                    r = await res.json();
                    reviewsCache[id] = r;
                }
            } catch (err) {
                console.warn(`Failed to fetch fresh state for ${id}:`, err);
            }

            if (!r) return;

            document.getElementById("empty-detail-state").classList.add("hidden");
            document.getElementById("active-detail-content").classList.remove("hidden");

            // Populate Metadata
            document.getElementById("detail-repo").textContent = r.repo_name;
            document.getElementById("detail-author").textContent = `@${r.author}`;
            document.getElementById("detail-title").textContent = r.pr_title;
            document.getElementById("detail-id").textContent = r.pr_id;

            // Populate Status Badge
            const badge = document.getElementById("detail-badge");
            badge.className = "px-3 py-1 rounded-full text-xs font-medium border";
            if (r.status === "running") {
                badge.classList.add("bg-cyan-500/10", "text-cyan-400", "border-cyan-500/20", "pulse-effect");
                badge.textContent = "Agent Execution Running";
            } else if (r.status === "pending") {
                badge.classList.add("bg-amber-500/10", "text-amber-400", "border-amber-500/20");
                badge.textContent = "Pending Approval Gate";
            } else if (r.status === "completed" || r.status === "approved") {
                badge.classList.add("bg-emerald-500/10", "text-emerald-400", "border-emerald-500/20");
                badge.textContent = "Approved & Closed";
            } else if (r.status === "rejected") {
                badge.classList.add("bg-rose-500/10", "text-rose-400", "border-rose-500/20");
                badge.textContent = "Rejected / Closed";
            } else {
                badge.classList.add("bg-slate-500/10", "text-slate-400", "border-white/5");
                badge.textContent = r.status.toUpperCase();
            }

            // Update LangGraph Stepper UI
            updateStepperUI(r.status);

            // Populate Git Highlight diff style
            renderGitDiff(r.diff);

            // Render Markdown Tab content safely in-browser
            document.getElementById("tab-content-consolidated").innerHTML = r.consolidated_report 
                ? safeParseMarkdown(r.consolidated_report) 
                : `<div class="text-center py-8 text-slate-500"><p class="text-sm">Consolidated report will appear once all agents finish scanning.</p></div>`;
            
            document.getElementById("tab-content-security").innerHTML = r.security_report 
                ? safeParseMarkdown(r.security_report) 
                : `<div class="text-center py-8 text-slate-500"><p class="text-sm">Scanning code for OWASP Top 10 vulnerabilities...</p></div>`;
            
            document.getElementById("tab-content-quality").innerHTML = r.quality_report 
                ? safeParseMarkdown(r.quality_report) 
                : `<div class="text-center py-8 text-slate-500"><p class="text-sm">Calculating PEP-8 naming, lint, and cognitive complexity rules...</p></div>`;
            
            // Populate Test markdown report
            document.getElementById("test-markdown-report").innerHTML = r.test_report 
                ? safeParseMarkdown(r.test_report) 
                : `<div class="text-center py-8 text-slate-500"><p class="text-sm">Checking unit test coverage and drafting Pytest mocks...</p></div>`;
            
            // Populate test results if already executed
            const testsResults = document.getElementById("tests-results");
            const testsLoading = document.getElementById("tests-loading");
            if (r.test_results) {
                testsResults.classList.remove("hidden");
                testsLoading.classList.add("hidden");
                document.getElementById("test-stat-passed").textContent = r.test_results.passed;
                document.getElementById("test-stat-coverage").textContent = r.test_results.coverage;
                document.getElementById("test-stat-duration").textContent = r.test_results.duration;
                document.getElementById("test-stat-console").textContent = r.test_results.console;
            } else {
                testsResults.classList.add("hidden");
                testsLoading.classList.add("hidden");
            }
            
            document.getElementById("tab-content-doc").innerHTML = r.documentation_report 
                ? safeParseMarkdown(r.documentation_report) 
                : `<div class="text-center py-8 text-slate-500"><p class="text-sm">Scanning for missing PEP-257 docstrings...</p></div>`;

            // Display Approval gate control box only if status is 'pending'
            const approvalBox = document.getElementById("approval-gate-box");
            if (r.status === "pending") {
                approvalBox.classList.remove("hidden");
                document.getElementById("approval-feedback").value = "";
            } else {
                approvalBox.classList.add("hidden");
            }

            // Focus on active tab
            switchTab(activeTab);
        }

        // Stepper Status Manager
        function updateStepperUI(status) {
            const steps = {
                webhook: document.getElementById("step-webhook"),
                agents: document.getElementById("step-agents"),
                gate: document.getElementById("step-gate"),
                publish: document.getElementById("step-publish")
            };

            // Reset stepper styles
            Object.values(steps).forEach(el => {
                el.className = "h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs bg-slate-800 text-slate-400 border border-slate-700";
            });

            if (status === "running") {
                steps.webhook.className = "h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/30";
                steps.agents.className = "h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs bg-cyan-500/20 text-cyan-400 border border-cyan-500/50 pulse-effect glow-cyan";
            } else if (status === "pending") {
                steps.webhook.className = "h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
                steps.agents.className = "h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
                steps.gate.className = "h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs bg-amber-500/20 text-amber-400 border border-amber-500/50 pulse-effect";
            } else if (status === "completed" || status === "approved") {
                steps.webhook.className = "h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/40";
                steps.agents.className = "h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/40";
                steps.gate.className = "h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/40";
                steps.publish.className = "h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/50 glow-green";
            } else if (status === "rejected") {
                steps.webhook.className = "h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
                steps.agents.className = "h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
                steps.gate.className = "h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs bg-rose-500/20 text-rose-400 border border-rose-500/50";
            }
        }

        // Submit Approval Gate Decision
        async function submitDecision(decision) {
            if (!selectedReviewId) return;

            const feedback = document.getElementById("approval-feedback").value;
            const endpoint = `/api/reviews/${selectedReviewId}/${decision}`;

            try {
                const res = await fetch(endpoint, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ feedback: feedback })
                });

                if (res.ok) {
                    // Update state to loading immediately
                    const badge = document.getElementById("detail-badge");
                    badge.className = "px-3 py-1 rounded-full text-xs font-medium border bg-slate-500/10 text-slate-400 border-white/5 pulse-effect";
                    badge.textContent = "Processing Decision...";
                    document.getElementById("approval-gate-box").classList.add("hidden");
                    
                    // Trigger a fast refresh loop to catch completion!
                    setTimeout(async () => {
                        await refreshReviews();
                        selectReview(selectedReviewId);
                    }, 1500);
                } else {
                    alert("Failed to submit review action.");
                }
            } catch (err) {
                alert("Connection error submitting gate approval.");
            }
        }

        // Long polling mock for active review (when status is running or processing)
        async function pollActiveReview() {
            if (!selectedReviewId) return;
            const r = reviewsCache[selectedReviewId];
            if (!r) return;

            // If the currently selected review is in progress, poll the API to update UI!
            if (r.status === "running" || r.status === "processing_decision") {
                try {
                    const res = await fetch(`/api/reviews/${selectedReviewId}`);
                    if (res.ok) {
                        const latest = await res.json();
                        // If status updated, refresh list and reload details
                        if (latest.status !== r.status || latest.consolidated_report !== r.consolidated_report) {
                            await refreshReviews();
                            selectReview(selectedReviewId);
                        }
                    }
                } catch (err) {
                    console.warn("Polling error:", err);
                }
            }
        }

        // Render code difference layout with green/red colors (identical to GitHub's changes made page)
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

        // Run automated PR test harness and show dynamic loading spinner & statistics
        async function runPRTests() {
            if (!selectedReviewId) return;
            
            const runBtn = document.getElementById("run-tests-btn");
            const loading = document.getElementById("tests-loading");
            const results = document.getElementById("tests-results");
            
            runBtn.disabled = true;
            runBtn.classList.add("opacity-50", "cursor-not-allowed");
            loading.classList.remove("hidden");
            results.classList.add("hidden");
            
            try {
                const res = await fetch(`/api/reviews/${selectedReviewId}/run-tests`, {
                    method: "POST"
                });
                
                if (res.ok) {
                    const data = await res.json();
                    
                    // Update cache and display results
                    reviewsCache[selectedReviewId].test_results = data;
                    
                    document.getElementById("test-stat-passed").textContent = data.passed;
                    document.getElementById("test-stat-coverage").textContent = data.coverage;
                    document.getElementById("test-stat-duration").textContent = data.duration;
                    document.getElementById("test-stat-console").textContent = data.console;
                    
                    results.classList.remove("hidden");
                } else {
                    alert("Failed to run tests.");
                }
            } catch (err) {
                alert("Error during test runner execution.");
            } finally {
                loading.classList.add("hidden");
                runBtn.disabled = false;
                runBtn.classList.remove("opacity-50", "cursor-not-allowed");
            }
        }
    </script>
</body>
</html>
"""
