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
                <h2 class="text-sm font-semibold text-slate-300">Active Pull Requests</h2>
                <button onclick="refreshReviews()" class="p-1.5 hover:bg-white/5 text-slate-400 hover:text-white rounded-lg transition">
                    <i data-lucide="refresh-cw" class="h-4 w-4"></i>
                </button>
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
                    <div id="tab-content-test" class="tab-pane hidden markdown-body">
                        <!-- Loaded dynamically -->
                    </div>

                    <!-- Doc Tab -->
                    <div id="tab-content-doc" class="tab-pane hidden markdown-body">
                        <!-- Loaded dynamically -->
                    </div>

                    <!-- Diff Tab -->
                    <div id="tab-content-diff" class="tab-pane hidden">
                        <pre class="bg-slate-950/80 p-4 border border-white/5 rounded-xl overflow-x-auto text-xs font-mono text-emerald-400"><code id="diff-raw-code"></code></pre>
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

        let selectedReviewId = null;
        let activeTab = "consolidated";
        let reviewsCache = {};

        // Load Lucide Icons
        window.addEventListener("DOMContentLoaded", () => {
            lucide.createIcons();
            loadTemplate("vulnerability");
            refreshReviews();
            loadSettings();
            
            // Poll for updates every 3 seconds to keep pipeline progress real-time!
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

            try {
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
                if (data.status === "accepted") {
                    toggleTriggerModal();
                    await refreshReviews();
                    selectReview(data.pr_id);
                }
            } catch (err) {
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

                const keys = Object.keys(reviews).reverse();
                if (keys.length === 0) {
                    container.innerHTML = `<div class="text-center py-8 text-slate-500 text-xs"><p>No pull requests reviewed yet.</p></div>`;
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
            } catch (err) {
                console.error("Failed to load reviews:", err);
            }
        }

        // Selection Controller
        function selectReview(id) {
            selectedReviewId = id;
            
            // Re-render list to show active state
            refreshReviews();

            const r = reviewsCache[id];
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
                badge.classList.add("bg-cyan-500/10", "text-cyan-400", "border-cyan-500/20");
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

            // Populate Raw Diff Code
            document.getElementById("diff-raw-code").textContent = r.diff;

            // Render Markdown Tab content in-browser using marked.js
            document.getElementById("tab-content-consolidated").innerHTML = r.consolidated_report 
                ? marked.parse(r.consolidated_report) 
                : `<div class="text-center py-8 text-slate-500"><p class="text-sm">Consolidated report will appear once all agents finish scanning.</p></div>`;
            
            document.getElementById("tab-content-security").innerHTML = r.security_report 
                ? marked.parse(r.security_report) 
                : `<div class="text-center py-8 text-slate-500"><p class="text-sm">Scanning code for OWASP Top 10 vulnerabilities...</p></div>`;
            
            document.getElementById("tab-content-quality").innerHTML = r.quality_report 
                ? marked.parse(r.quality_report) 
                : `<div class="text-center py-8 text-slate-500"><p class="text-sm">Calculating PEP-8 naming, lint, and cognitive complexity rules...</p></div>`;
            
            document.getElementById("tab-content-test").innerHTML = r.test_report 
                ? marked.parse(r.test_report) 
                : `<div class="text-center py-8 text-slate-500"><p class="text-sm">Checking unit test coverage and drafting Pytest mocks...</p></div>`;
            
            document.getElementById("tab-content-doc").innerHTML = r.documentation_report 
                ? marked.parse(r.documentation_report) 
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
    </script>
</body>
</html>
"""
