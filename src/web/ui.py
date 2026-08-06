"""
Embedded single-page web UI for AIHawk Resume Builder.
Returns a complete HTML page with inline CSS and JavaScript.
"""


def get_html() -> str:
    """Return the complete HTML page for the web UI."""
    return _HTML


_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIHawk Jobs Applier</title>
    <style>
        :root {
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --primary-light: #dbeafe;
            --success: #16a34a;
            --danger: #dc2626;
            --warning: #d97706;
            --gray-50: #f9fafb;
            --gray-100: #f3f4f6;
            --gray-200: #e5e7eb;
            --gray-300: #d1d5db;
            --gray-400: #9ca3af;
            --gray-500: #6b7280;
            --gray-600: #4b5563;
            --gray-700: #374151;
            --gray-800: #1f2937;
            --gray-900: #111827;
            --radius: 8px;
            --shadow: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: var(--gray-50);
            color: var(--gray-800);
            line-height: 1.6;
        }

        .header {
            background: white;
            border-bottom: 1px solid var(--gray-200);
            padding: 16px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: var(--shadow);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .header h1 {
            font-size: 20px;
            font-weight: 700;
            color: var(--gray-900);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .header h1 .icon { font-size: 24px; }

        .header-actions { display: flex; gap: 12px; align-items: center; }

        .badge { padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }
        .badge-success { background: #dcfce7; color: var(--success); }
        .badge-warning { background: #fef3c7; color: var(--warning); }
        .badge-danger { background: #fee2e2; color: var(--danger); }

        .container { max-width: 1200px; margin: 0 auto; padding: 24px; }

        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
        @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }

        .card {
            background: white;
            border-radius: var(--radius);
            border: 1px solid var(--gray-200);
            box-shadow: var(--shadow);
            overflow: hidden;
        }

        .card-header {
            padding: 16px 20px;
            border-bottom: 1px solid var(--gray-200);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .card-header h2 { font-size: 16px; font-weight: 600; color: var(--gray-900); }
        .card-body { padding: 20px; }

        .form-group { margin-bottom: 16px; }
        .form-group label {
            display: block; font-size: 13px; font-weight: 600;
            color: var(--gray-700); margin-bottom: 6px;
        }

        .form-group input[type="text"],
        .form-group input[type="password"],
        .form-group input[type="url"],
        .form-group select,
        .form-group textarea {
            width: 100%; padding: 10px 12px;
            border: 1px solid var(--gray-300);
            border-radius: var(--radius);
            font-size: 14px; color: var(--gray-800);
            background: white;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        .form-group input[type="text"]:focus,
        .form-group input[type="password"]:focus,
        .form-group input[type="url"]:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px var(--primary-light);
        }

        .form-group textarea {
            font-family: 'SF Mono', 'Fira Code', 'Fira Mono', monospace;
            font-size: 12px; resize: vertical; min-height: 200px;
        }

        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
        .form-help { font-size: 12px; color: var(--gray-500); margin-top: 4px; }

        .btn {
            display: inline-flex; align-items: center; justify-content: center;
            gap: 6px; padding: 10px 20px; border-radius: var(--radius);
            font-size: 14px; font-weight: 600; cursor: pointer;
            border: none; transition: all 0.2s;
        }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .btn-primary { background: var(--primary); color: white; }
        .btn-primary:hover:not(:disabled) { background: var(--primary-dark); }
        .btn-success { background: var(--success); color: white; }
        .btn-outline { background: white; color: var(--gray-700); border: 1px solid var(--gray-300); }
        .btn-outline:hover:not(:disabled) { background: var(--gray-50); }
        .btn-sm { padding: 6px 12px; font-size: 12px; }
        .btn-block { width: 100%; }
        .btn-group { display: flex; gap: 8px; flex-wrap: wrap; }

        .main-tabs {
            display: flex; border-bottom: 2px solid var(--gray-200);
            margin-bottom: 24px; gap: 4px;
        }

        .main-tab {
            padding: 12px 24px; font-size: 15px; font-weight: 600;
            color: var(--gray-500); cursor: pointer;
            border-bottom: 3px solid transparent; margin-bottom: -2px;
            transition: all 0.2s; background: none;
            border-top: none; border-left: none; border-right: none;
            user-select: none;
        }
        .main-tab:hover { color: var(--gray-700); background: var(--gray-50); }
        .main-tab.active { color: var(--primary); border-bottom-color: var(--primary); }

        .tab-panel { display: none; }
        .tab-panel.active { display: block; }

        .progress-container { padding: 20px; display: none; }
        .progress-container.active { display: block; }

        .progress-bar-track {
            height: 8px; background: var(--gray-200);
            border-radius: 4px; overflow: hidden; margin: 12px 0;
        }
        .progress-bar-fill {
            height: 100%; background: var(--primary);
            border-radius: 4px; transition: width 0.5s ease; width: 0%;
        }
        .progress-bar-fill.success { background: var(--success); }
        .progress-bar-fill.error { background: var(--danger); }
        .progress-text { font-size: 14px; color: var(--gray-600); text-align: center; }
        .progress-percent { font-size: 24px; font-weight: 700; color: var(--gray-800); text-align: center; }

        .status-log {
            max-height: 200px; overflow-y: auto; font-size: 13px;
            font-family: monospace; background: var(--gray-50);
            border: 1px solid var(--gray-200); border-radius: var(--radius);
            padding: 12px; margin-top: 12px;
        }
        .status-entry { padding: 4px 0; border-bottom: 1px solid var(--gray-100); }
        .status-entry:last-child { border-bottom: none; }
        .status-time { color: var(--gray-400); font-size: 11px; margin-right: 8px; }

        .alert {
            padding: 12px 16px; border-radius: var(--radius);
            margin-bottom: 16px; font-size: 14px; display: none;
        }
        .alert.show { display: block; }
        .alert-error { background: #fee2e2; color: var(--danger); border: 1px solid #fecaca; }
        .alert-success { background: #dcfce7; color: var(--success); border: 1px solid #bbf7d0; }
        .alert-info { background: var(--primary-light); color: var(--primary-dark); border: 1px solid #93c5fd; }

        .action-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px; }
        @media (max-width: 768px) { .action-cards { grid-template-columns: 1fr; } }
        .action-card {
            padding: 16px; border: 2px solid var(--gray-200);
            border-radius: var(--radius); cursor: pointer;
            transition: all 0.2s; text-align: center;
        }
        .action-card:hover { border-color: var(--primary); background: var(--primary-light); }
        .action-card.selected { border-color: var(--primary); background: var(--primary-light); }
        .action-card .action-icon { font-size: 28px; margin-bottom: 8px; }
        .action-card .action-title { font-weight: 600; font-size: 14px; color: var(--gray-800); }
        .action-card .action-desc { font-size: 12px; color: var(--gray-500); margin-top: 4px; }

        .history-item {
            display: flex; align-items: center; justify-content: space-between;
            padding: 12px 0; border-bottom: 1px solid var(--gray-100);
        }
        .history-item:last-child { border-bottom: none; }
        .history-info h4 { font-size: 14px; color: var(--gray-800); }
        .history-info p { font-size: 12px; color: var(--gray-500); }

        .spinner {
            display: inline-block; width: 16px; height: 16px;
            border: 2px solid var(--gray-300); border-top-color: var(--primary);
            border-radius: 50%; animation: spin 0.8s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        .tooltip { position: relative; }
        .tooltip::after {
            content: attr(data-tip); position: absolute; bottom: 100%;
            left: 50%; transform: translateX(-50%);
            background: var(--gray-800); color: white;
            padding: 4px 8px; border-radius: 4px; font-size: 12px;
            white-space: nowrap; opacity: 0; pointer-events: none;
            transition: opacity 0.2s;
        }
        .tooltip:hover::after { opacity: 1; }

        .full-width { grid-column: 1 / -1; }
        .hidden { display: none !important; }
        #jobUrlGroup { display: none; }
        #jobUrlGroup.show { display: block; }

        .example-link { font-size: 12px; color: var(--primary); cursor: pointer; text-decoration: underline; }
        .example-link:hover { color: var(--primary-dark); }

        .settings-section {
            margin-bottom: 24px; padding-bottom: 20px;
            border-bottom: 1px solid var(--gray-200);
        }
        .settings-section:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
        .settings-section h3 {
            font-size: 15px; font-weight: 600; color: var(--gray-800);
            margin-bottom: 12px; display: flex; align-items: center; gap: 8px;
        }

        .check-group { display: flex; flex-wrap: wrap; gap: 12px; }
        .check-item {
            display: flex; align-items: center; gap: 6px;
            font-size: 14px; color: var(--gray-700); cursor: pointer;
        }
        .check-item input[type="checkbox"],
        .check-item input[type="radio"] {
            width: 16px; height: 16px; accent-color: var(--primary); cursor: pointer;
        }

        .tag-input-wrap { display: flex; gap: 8px; margin-bottom: 8px; }
        .tag-input-wrap input {
            flex: 1; padding: 8px 12px;
            border: 1px solid var(--gray-300); border-radius: var(--radius);
            font-size: 14px; color: var(--gray-800); background: white;
        }
        .tag-input-wrap input:focus {
            outline: none; border-color: var(--primary);
            box-shadow: 0 0 0 3px var(--primary-light);
        }

        .tag-list { display: flex; flex-wrap: wrap; gap: 6px; min-height: 28px; }
        .tag {
            display: inline-flex; align-items: center; gap: 4px;
            padding: 4px 10px; background: var(--primary-light);
            color: var(--primary-dark); border-radius: 16px;
            font-size: 13px; font-weight: 500;
        }
        .tag-remove {
            cursor: pointer; font-size: 14px; font-weight: 700;
            line-height: 1; opacity: 0.7; border: none;
            background: none; color: var(--primary-dark); padding: 0 2px;
        }
        .tag-remove:hover { opacity: 1; }

        .status-msg {
            padding: 10px 14px; border-radius: var(--radius);
            font-size: 13px; margin-top: 12px; display: none;
        }
        .status-msg.show { display: block; }
        .status-msg.success { background: #dcfce7; color: var(--success); border: 1px solid #bbf7d0; }
        .status-msg.error { background: #fee2e2; color: var(--danger); border: 1px solid #fecaca; }
        .status-msg.info { background: var(--primary-light); color: var(--primary-dark); border: 1px solid #93c5fd; }

        .settings-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
        @media (max-width: 768px) { .settings-grid { grid-template-columns: 1fr; } }

        .resume-hint {
            background: var(--primary-light); border: 1px solid #93c5fd;
            border-radius: var(--radius); padding: 10px 14px;
            font-size: 13px; color: var(--primary-dark); margin-bottom: 16px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1><span class="icon">&#128640;</span> AIHawk Jobs Applier</h1>
        <div class="header-actions">
            <span id="healthBadge" class="badge badge-warning">Checking...</span>
        </div>
    </div>

    <div class="container">
        <div id="alertArea"><div id="alertBox" class="alert"></div></div>

        <div class="main-tabs">
            <button class="main-tab active" onclick="switchTab('generate')">&#9889; Generate</button>
            <button class="main-tab" onclick="switchTab('resume')">&#128221; Resume</button>
            <button class="main-tab" onclick="switchTab('settings')">&#9881; Settings</button>
            <button class="main-tab" onclick="switchTab('bot')">&#129302; Auto Apply</button>
            <button class="main-tab" onclick="switchTab('applications')">&#128196; Applications</button>
        </div>

        <!-- TAB 1: GENERATE -->
        <div id="tab-generate" class="tab-panel active">
            <div class="grid">
                <div>
                    <div class="card" style="margin-bottom: 24px;">
                        <div class="card-header"><h2>&#128273; API Configuration</h2></div>
                        <div class="card-body">
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="llmProvider">LLM Provider</label>
                                    <select id="llmProvider" onchange="onProviderChange()">
                                        <option value="claude">Claude (Anthropic)</option>
                                        <option value="openai">OpenAI</option>
                                        <option value="gemini">Google Gemini</option>
                                        <option value="ollama">Ollama (Local)</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="llmModel">Model</label>
                                    <select id="llmModel">
                                        <option value="claude-sonnet-4-20250514">Claude Sonnet 4</option>
                                        <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</option>
                                        <option value="claude-3-haiku-20240307">Claude 3 Haiku</option>
                                    </select>
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="apiKey">API Key</label>
                                <input type="password" id="apiKey" placeholder="Enter your API key...">
                                <p class="form-help">Your API key is sent directly to the generation endpoint and is not stored.</p>
                            </div>
                        </div>
                    </div>

                    <div class="card" style="margin-bottom: 24px;">
                        <div class="card-header"><h2>&#9889; Action</h2></div>
                        <div class="card-body">
                            <div class="action-cards">
                                <div class="action-card selected" onclick="selectAction('resume')" id="action-resume">
                                    <div class="action-icon">&#128196;</div>
                                    <div class="action-title">Resume</div>
                                    <div class="action-desc">Generate base resume</div>
                                </div>
                                <div class="action-card" onclick="selectAction('resume_tailored')" id="action-resume_tailored">
                                    <div class="action-icon">&#127919;</div>
                                    <div class="action-title">Tailored Resume</div>
                                    <div class="action-desc">Resume for a job</div>
                                </div>
                                <div class="action-card" onclick="selectAction('cover_letter')" id="action-cover_letter">
                                    <div class="action-icon">&#9993;</div>
                                    <div class="action-title">Cover Letter</div>
                                    <div class="action-desc">Tailored cover letter</div>
                                </div>
                            </div>
                            <div class="form-group" id="jobUrlGroup">
                                <label for="jobUrl">Job Posting URL</label>
                                <input type="url" id="jobUrl" placeholder="https://www.linkedin.com/jobs/view/...">
                                <p class="form-help">URL of the job posting to tailor your document to.</p>
                            </div>
                            <div class="form-group">
                                <label for="styleSelect">Resume Style</label>
                                <select id="styleSelect"><option value="">Loading styles...</option></select>
                            </div>
                        </div>
                    </div>
                </div>

                <div>
                    <div class="card" style="margin-bottom: 24px;">
                        <div class="card-header"><h2>&#128221; Resume Data</h2></div>
                        <div class="card-body">
                            <div class="resume-hint">
                                &#128161; Edit your resume in the <strong>Resume</strong> tab. Your resume data will be loaded automatically when generating.
                            </div>
                            <div id="resumePreview" style="font-size: 13px; color: var(--gray-600);">
                                <p>No resume loaded yet. Go to the Resume tab to enter your data.</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="full-width">
                    <div class="card">
                        <div class="card-body">
                            <button id="generateBtn" class="btn btn-primary btn-block" onclick="startGeneration()">&#9889; Generate Document</button>
                            <div id="progressContainer" class="progress-container">
                                <div class="progress-percent" id="progressPercent">0%</div>
                                <div class="progress-bar-track"><div class="progress-bar-fill" id="progressBar"></div></div>
                                <div class="progress-text" id="progressText">Waiting...</div>
                                <div class="status-log" id="statusLog"></div>
                            </div>
                            <div id="downloadSection" class="hidden" style="text-align: center; margin-top: 16px;">
                                <button id="downloadBtn" class="btn btn-success" onclick="downloadDocument()">&#11015; Download PDF</button>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="full-width">
                    <div class="card">
                        <div class="card-header">
                            <h2>&#128203; Recent Generations</h2>
                            <button class="btn btn-outline btn-sm" onclick="clearHistory()">Clear</button>
                        </div>
                        <div class="card-body" id="historyList">
                            <p style="color: var(--gray-400); text-align: center; padding: 20px;">No documents generated yet.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 2: RESUME -->
        <div id="tab-resume" class="tab-panel">
            <div class="card">
                <div class="card-header">
                    <h2>&#128221; Resume Data (YAML)</h2>
                    <div class="btn-group">
                        <button class="btn btn-outline btn-sm" onclick="loadResumeFromServer()">Load from Server</button>
                        <button class="btn btn-outline btn-sm" onclick="loadExample()">Load Example</button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="form-group">
                        <textarea id="resumeYaml" rows="30" placeholder="Paste your resume YAML here..."></textarea>
                        <p class="form-help">Paste your resume in YAML format or load it from the server. Click &quot;Load Example&quot; to see the expected structure.</p>
                    </div>
                    <div class="btn-group">
                        <button class="btn btn-primary" onclick="saveResumeToServer()">&#128190; Save to Server</button>
                    </div>
                    <div id="resumeStatus" class="status-msg"></div>
                </div>
            </div>
        </div>

        <!-- TAB 3: SETTINGS -->
        <div id="tab-settings" class="tab-panel">
            <div class="card">
                <div class="card-header">
                    <h2>&#9881; Work Preferences</h2>
                    <div class="btn-group">
                        <button class="btn btn-outline btn-sm" onclick="loadPreferencesFromServer()">Load from Server</button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="settings-grid">
                        <div>
                            <div class="settings-section">
                                <h3>&#127968; Work Location</h3>
                                <div class="check-group">
                                    <label class="check-item"><input type="checkbox" id="pref_remote" checked> Remote</label>
                                    <label class="check-item"><input type="checkbox" id="pref_hybrid" checked> Hybrid</label>
                                    <label class="check-item"><input type="checkbox" id="pref_onsite" checked> On-site</label>
                                </div>
                            </div>
                            <div class="settings-section">
                                <h3>&#128188; Experience Level</h3>
                                <div class="check-group">
                                    <label class="check-item"><input type="checkbox" id="pref_exp_internship"> Internship</label>
                                    <label class="check-item"><input type="checkbox" id="pref_exp_entry" checked> Entry</label>
                                    <label class="check-item"><input type="checkbox" id="pref_exp_associate" checked> Associate</label>
                                    <label class="check-item"><input type="checkbox" id="pref_exp_mid_senior" checked> Mid-Senior Level</label>
                                    <label class="check-item"><input type="checkbox" id="pref_exp_director"> Director</label>
                                    <label class="check-item"><input type="checkbox" id="pref_exp_executive"> Executive</label>
                                </div>
                            </div>
                            <div class="settings-section">
                                <h3>&#128196; Job Types</h3>
                                <div class="check-group">
                                    <label class="check-item"><input type="checkbox" id="pref_jt_full_time" checked> Full-time</label>
                                    <label class="check-item"><input type="checkbox" id="pref_jt_contract"> Contract</label>
                                    <label class="check-item"><input type="checkbox" id="pref_jt_part_time"> Part-time</label>
                                    <label class="check-item"><input type="checkbox" id="pref_jt_temporary" checked> Temporary</label>
                                    <label class="check-item"><input type="checkbox" id="pref_jt_internship"> Internship</label>
                                    <label class="check-item"><input type="checkbox" id="pref_jt_other"> Other</label>
                                    <label class="check-item"><input type="checkbox" id="pref_jt_volunteer" checked> Volunteer</label>
                                </div>
                            </div>
                            <div class="settings-section">
                                <h3>&#128197; Date Posted</h3>
                                <div class="check-group">
                                    <label class="check-item"><input type="radio" name="datePosted" value="all_time"> All Time</label>
                                    <label class="check-item"><input type="radio" name="datePosted" value="month"> Month</label>
                                    <label class="check-item"><input type="radio" name="datePosted" value="week"> Week</label>
                                    <label class="check-item"><input type="radio" name="datePosted" value="24_hours" checked> 24 Hours</label>
                                </div>
                            </div>
                        </div>
                        <div>
                            <div class="settings-section">
                                <h3>&#128269; Search Criteria</h3>
                                <div class="form-group">
                                    <label>Positions</label>
                                    <div class="tag-input-wrap">
                                        <input type="text" id="positionInput" placeholder="Add a position...">
                                        <button class="btn btn-outline btn-sm" onclick="addTag('positions')">Add</button>
                                    </div>
                                    <div class="tag-list" id="positions-tags"></div>
                                </div>
                                <div class="form-group">
                                    <label>Locations</label>
                                    <div class="tag-input-wrap">
                                        <input type="text" id="locationInput" placeholder="Add a location...">
                                        <button class="btn btn-outline btn-sm" onclick="addTag('locations')">Add</button>
                                    </div>
                                    <div class="tag-list" id="locations-tags"></div>
                                </div>
                                <div class="form-group">
                                    <label for="pref_distance">Distance (miles)</label>
                                    <select id="pref_distance">
                                        <option value="0">0</option>
                                        <option value="5">5</option>
                                        <option value="10">10</option>
                                        <option value="25">25</option>
                                        <option value="50">50</option>
                                        <option value="100" selected>100</option>
                                    </select>
                                </div>
                            </div>
                            <div class="settings-section">
                                <h3>&#128683; Blacklists</h3>
                                <div class="form-group">
                                    <label>Company Blacklist</label>
                                    <div class="tag-input-wrap">
                                        <input type="text" id="companyBlInput" placeholder="Add a company...">
                                        <button class="btn btn-outline btn-sm" onclick="addTag('company_blacklist')">Add</button>
                                    </div>
                                    <div class="tag-list" id="company_blacklist-tags"></div>
                                </div>
                                <div class="form-group">
                                    <label>Title Blacklist</label>
                                    <div class="tag-input-wrap">
                                        <input type="text" id="titleBlInput" placeholder="Add a title keyword...">
                                        <button class="btn btn-outline btn-sm" onclick="addTag('title_blacklist')">Add</button>
                                    </div>
                                    <div class="tag-list" id="title_blacklist-tags"></div>
                                </div>
                                <div class="form-group">
                                    <label>Location Blacklist</label>
                                    <div class="tag-input-wrap">
                                        <input type="text" id="locationBlInput" placeholder="Add a location...">
                                        <button class="btn btn-outline btn-sm" onclick="addTag('location_blacklist')">Add</button>
                                    </div>
                                    <div class="tag-list" id="location_blacklist-tags"></div>
                                </div>
                            </div>
                            <div class="settings-section">
                                <h3>&#9881; Other</h3>
                                <div class="check-group">
                                    <label class="check-item"><input type="checkbox" id="pref_apply_once" checked> Apply Once at Company</label>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div style="border-top: 1px solid var(--gray-200); padding-top: 20px; margin-top: 8px;">
                        <div class="btn-group">
                            <button class="btn btn-primary" onclick="savePreferencesToServer()">&#128190; Save Preferences</button>
                            <button class="btn btn-outline" onclick="loadPreferencesFromServer()">&#128259; Reload from Server</button>
                        </div>
                        <div id="settingsStatus" class="status-msg"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 4: AUTO APPLY BOT -->
        <div id="tab-bot" class="tab-panel">
            <div class="grid">
                <!-- Left: Configuration -->
                <div>
                    <!-- Platforms -->
                    <div class="card" style="margin-bottom:20px">
                        <div class="card-header"><h2>&#127758; Platforms</h2></div>
                        <div class="card-body">
                            <p style="margin-bottom:12px;color:var(--gray-500);font-size:13px">Select which job platforms to search and apply on.</p>
                            <div style="display:flex;flex-wrap:wrap;gap:10px">
                                <label style="display:flex;align-items:center;gap:6px;cursor:pointer"><input type="checkbox" id="plt-linkedin" checked> LinkedIn</label>
                                <label style="display:flex;align-items:center;gap:6px;cursor:pointer"><input type="checkbox" id="plt-indeed"> Indeed</label>
                                <label style="display:flex;align-items:center;gap:6px;cursor:pointer"><input type="checkbox" id="plt-glassdoor"> Glassdoor</label>
                                <label style="display:flex;align-items:center;gap:6px;cursor:pointer"><input type="checkbox" id="plt-ziprecruiter"> ZipRecruiter</label>
                                <label style="display:flex;align-items:center;gap:6px;cursor:pointer"><input type="checkbox" id="plt-dice"> Dice</label>
                                <label style="display:flex;align-items:center;gap:6px;cursor:pointer"><input type="checkbox" id="plt-universal"> Universal (any URL)</label>
                            </div>
                        </div>
                    </div>

                    <!-- Credentials -->
                    <div class="card" style="margin-bottom:20px">
                        <div class="card-header">
                            <h2>&#128272; Platform Credentials</h2>
                            <button class="btn btn-outline btn-sm" onclick="loadCredentials()">Load Saved</button>
                        </div>
                        <div class="card-body">
                            <p style="margin-bottom:12px;color:var(--gray-500);font-size:13px">Saved to <code>data_folder/credentials.yaml</code> on your machine.</p>
                            <div id="credentials-panels">
                                <div class="cred-panel" id="cred-linkedin">
                                    <strong style="font-size:13px">LinkedIn</strong>
                                    <div class="form-row" style="margin-top:8px">
                                        <div class="form-group"><label class="form-label">Email</label><input type="email" id="cred-linkedin-email" class="form-input" placeholder="you@email.com"></div>
                                        <div class="form-group"><label class="form-label">Password</label><input type="password" id="cred-linkedin-password" class="form-input" placeholder="••••••••"></div>
                                    </div>
                                </div>
                                <div class="cred-panel" id="cred-indeed" style="margin-top:12px;display:none">
                                    <strong style="font-size:13px">Indeed</strong>
                                    <div class="form-row" style="margin-top:8px">
                                        <div class="form-group"><label class="form-label">Email</label><input type="email" id="cred-indeed-email" class="form-input" placeholder="you@email.com"></div>
                                        <div class="form-group"><label class="form-label">Password</label><input type="password" id="cred-indeed-password" class="form-input" placeholder="••••••••"></div>
                                    </div>
                                </div>
                                <div class="cred-panel" id="cred-glassdoor" style="margin-top:12px;display:none">
                                    <strong style="font-size:13px">Glassdoor</strong>
                                    <div class="form-row" style="margin-top:8px">
                                        <div class="form-group"><label class="form-label">Email</label><input type="email" id="cred-glassdoor-email" class="form-input" placeholder="you@email.com"></div>
                                        <div class="form-group"><label class="form-label">Password</label><input type="password" id="cred-glassdoor-password" class="form-input" placeholder="••••••••"></div>
                                    </div>
                                </div>
                                <div class="cred-panel" id="cred-ziprecruiter" style="margin-top:12px;display:none">
                                    <strong style="font-size:13px">ZipRecruiter</strong>
                                    <div class="form-row" style="margin-top:8px">
                                        <div class="form-group"><label class="form-label">Email</label><input type="email" id="cred-ziprecruiter-email" class="form-input" placeholder="you@email.com"></div>
                                        <div class="form-group"><label class="form-label">Password</label><input type="password" id="cred-ziprecruiter-password" class="form-input" placeholder="••••••••"></div>
                                    </div>
                                </div>
                                <div class="cred-panel" id="cred-dice" style="margin-top:12px;display:none">
                                    <strong style="font-size:13px">Dice</strong>
                                    <div class="form-row" style="margin-top:8px">
                                        <div class="form-group"><label class="form-label">Email</label><input type="email" id="cred-dice-email" class="form-input" placeholder="you@email.com"></div>
                                        <div class="form-group"><label class="form-label">Password</label><input type="password" id="cred-dice-password" class="form-input" placeholder="••••••••"></div>
                                    </div>
                                </div>
                            </div>
                            <div style="margin-top:12px">
                                <button class="btn btn-primary btn-sm" onclick="saveCredentials()">&#128190; Save Credentials</button>
                            </div>
                            <div id="credStatus" class="status-msg"></div>
                        </div>
                    </div>

                    <!-- Bot Settings -->
                    <div class="card">
                        <div class="card-header"><h2>&#9881; Bot Settings</h2></div>
                        <div class="card-body">
                            <div class="form-group">
                                <label class="form-label">LLM Provider</label>
                                <select id="bot-llm-type" class="form-input" onchange="updateBotModelOptions()">
                                    <option value="openai">OpenAI</option>
                                    <option value="claude">Claude (Anthropic)</option>
                                    <option value="gemini">Google Gemini</option>
                                    <option value="ollama">Ollama (local)</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Model</label>
                                <select id="bot-llm-model" class="form-input"></select>
                            </div>
                            <div class="form-group">
                                <label class="form-label">API Key</label>
                                <input type="password" id="bot-api-key" class="form-input" placeholder="sk-...  (not needed for Ollama)">
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label class="form-label">Min Score (1-10)</label>
                                    <input type="number" id="bot-min-score" class="form-input" value="7" min="1" max="10">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">Max Applications</label>
                                    <input type="number" id="bot-max-apps" class="form-input" value="50" min="1" max="500">
                                </div>
                            </div>
                            <div style="display:flex;gap:20px;margin-top:4px">
                                <label style="display:flex;align-items:center;gap:6px;cursor:pointer">
                                    <input type="checkbox" id="bot-headless" checked> Headless browser
                                </label>
                                <label style="display:flex;align-items:center;gap:6px;cursor:pointer">
                                    <input type="checkbox" id="bot-tailored-resume"> Generate tailored resume per job
                                </label>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Right: Live Status & Log -->
                <div>
                    <div class="card" style="margin-bottom:20px">
                        <div class="card-header">
                            <h2>&#9654; Bot Control</h2>
                            <div class="btn-group">
                                <button id="btn-bot-start" class="btn btn-primary" onclick="botStart()">&#9654; Start</button>
                                <button id="btn-bot-pause" class="btn btn-outline" onclick="botPause()" disabled>&#9646;&#9646; Pause</button>
                                <button id="btn-bot-stop" class="btn" style="background:var(--danger);color:white" onclick="botStop()" disabled>&#9632; Stop</button>
                            </div>
                        </div>
                        <div class="card-body">
                            <div id="bot-status-banner" style="padding:12px;border-radius:6px;background:var(--gray-100);margin-bottom:16px;font-size:14px">
                                Status: <strong id="bot-status-text">Idle</strong>
                                &nbsp;|&nbsp; Platform: <span id="bot-platform-text">—</span>
                                &nbsp;|&nbsp; Job: <span id="bot-job-text">—</span>
                            </div>
                            <div style="display:flex;gap:16px;margin-bottom:16px;text-align:center">
                                <div style="flex:1;padding:12px;background:var(--gray-50);border-radius:6px;border:1px solid var(--gray-200)">
                                    <div style="font-size:24px;font-weight:700;color:var(--success)" id="stat-applied">0</div>
                                    <div style="font-size:12px;color:var(--gray-500)">Applied</div>
                                </div>
                                <div style="flex:1;padding:12px;background:var(--gray-50);border-radius:6px;border:1px solid var(--gray-200)">
                                    <div style="font-size:24px;font-weight:700;color:var(--warning)" id="stat-skipped">0</div>
                                    <div style="font-size:12px;color:var(--gray-500)">Skipped</div>
                                </div>
                                <div style="flex:1;padding:12px;background:var(--gray-50);border-radius:6px;border:1px solid var(--gray-200)">
                                    <div style="font-size:24px;font-weight:700;color:var(--danger)" id="stat-failed">0</div>
                                    <div style="font-size:12px;color:var(--gray-500)">Failed</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <h2>&#128221; Live Log</h2>
                            <button class="btn btn-outline btn-sm" onclick="clearBotLog()">Clear</button>
                        </div>
                        <div class="card-body" style="padding:0">
                            <div id="bot-log" style="font-family:monospace;font-size:12px;background:#1e1e1e;color:#d4d4d4;padding:12px;height:300px;overflow-y:auto;border-radius:0 0 8px 8px">
                                <div style="color:#888">Bot log will appear here when running...</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 5: APPLICATIONS HISTORY -->
        <div id="tab-applications" class="tab-panel">
            <div class="card">
                <div class="card-header">
                    <h2>&#128196; Application History</h2>
                    <div class="btn-group">
                        <button class="btn btn-outline btn-sm" onclick="loadApplications()">&#128259; Refresh</button>
                        <a id="btn-export-csv" href="/api/applications/export/csv" class="btn btn-outline btn-sm" download="applications.csv">&#128229; Export CSV</a>
                    </div>
                </div>
                <div class="card-body" style="padding:0">
                    <!-- Stats bar -->
                    <div id="app-stats-bar" style="display:flex;gap:16px;padding:16px;border-bottom:1px solid var(--gray-200);flex-wrap:wrap">
                        <div>Total: <strong id="app-stat-total">—</strong></div>
                        <div style="color:var(--success)">Applied: <strong id="app-stat-applied">—</strong></div>
                        <div style="color:var(--warning)">Skipped: <strong id="app-stat-skipped">—</strong></div>
                        <div style="color:var(--danger)">Failed: <strong id="app-stat-failed">—</strong></div>
                    </div>
                    <!-- Filters -->
                    <div style="display:flex;gap:12px;padding:12px 16px;border-bottom:1px solid var(--gray-200);flex-wrap:wrap">
                        <select id="app-filter-platform" class="form-input" style="width:auto" onchange="loadApplications()">
                            <option value="">All Platforms</option>
                            <option value="linkedin">LinkedIn</option>
                            <option value="indeed">Indeed</option>
                            <option value="glassdoor">Glassdoor</option>
                            <option value="ziprecruiter">ZipRecruiter</option>
                            <option value="dice">Dice</option>
                            <option value="universal">Universal</option>
                        </select>
                        <select id="app-filter-status" class="form-input" style="width:auto" onchange="loadApplications()">
                            <option value="">All Statuses</option>
                            <option value="applied">Applied</option>
                            <option value="skipped">Skipped</option>
                            <option value="failed">Failed</option>
                            <option value="discovered">Discovered</option>
                            <option value="scored">Scored</option>
                        </select>
                    </div>
                    <!-- Table -->
                    <div style="overflow-x:auto">
                        <table id="app-table" style="width:100%;border-collapse:collapse;font-size:13px">
                            <thead>
                                <tr style="background:var(--gray-50);border-bottom:2px solid var(--gray-200)">
                                    <th style="padding:10px 16px;text-align:left;font-weight:600">Platform</th>
                                    <th style="padding:10px 16px;text-align:left;font-weight:600">Company</th>
                                    <th style="padding:10px 16px;text-align:left;font-weight:600">Title</th>
                                    <th style="padding:10px 16px;text-align:left;font-weight:600">Score</th>
                                    <th style="padding:10px 16px;text-align:left;font-weight:600">Status</th>
                                    <th style="padding:10px 16px;text-align:left;font-weight:600">Date</th>
                                    <th style="padding:10px 16px;text-align:left;font-weight:600">Link</th>
                                </tr>
                            </thead>
                            <tbody id="app-tbody">
                                <tr><td colspan="7" style="padding:24px;text-align:center;color:var(--gray-400)">Click Refresh to load applications.</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

    </div>
    <script>
        /* ========== STATE ========== */
        let currentAction = 'resume';
        let currentJobId = null;
        let ws = null;
        let downloadUrl = null;
        let genHistory = JSON.parse(localStorage.getItem('aihawk_history') || '[]');

        const tagData = {
            positions: [],
            locations: [],
            company_blacklist: [],
            title_blacklist: [],
            location_blacklist: [],
        };

        const tagInputIds = {
            positions: 'positionInput',
            locations: 'locationInput',
            company_blacklist: 'companyBlInput',
            title_blacklist: 'titleBlInput',
            location_blacklist: 'locationBlInput',
        };

        const modelOptions = {
            claude: [
                { value: 'claude-sonnet-4-20250514', label: 'Claude Sonnet 4' },
                { value: 'claude-3-5-sonnet-20241022', label: 'Claude 3.5 Sonnet' },
                { value: 'claude-3-haiku-20240307', label: 'Claude 3 Haiku' },
            ],
            openai: [
                { value: 'gpt-4o-mini', label: 'GPT-4o Mini' },
                { value: 'gpt-4o', label: 'GPT-4o' },
                { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
            ],
            gemini: [
                { value: 'gemini-pro', label: 'Gemini Pro' },
                { value: 'gemini-1.5-pro', label: 'Gemini 1.5 Pro' },
            ],
            ollama: [
                { value: 'llama3', label: 'Llama 3' },
                { value: 'mixtral', label: 'Mixtral' },
                { value: 'codellama', label: 'Code Llama' },
            ],
        };

        const exampleYaml = `personal_information:
  name: "John"
  surname: "Doe"
  date_of_birth: "01/15/1990"
  country: "United States"
  city: "San Francisco"
  address: "123 Tech Street"
  zip_code: "94105"
  phone_prefix: "+1"
  phone: "5551234567"
  email: "john.doe@email.com"
  github: "https://github.com/johndoe"
  linkedin: "https://www.linkedin.com/in/johndoe"

education_details:
  - education_level: "Master's Degree"
    institution: "Stanford University"
    field_of_study: "Computer Science"
    final_evaluation_grade: "3.9"
    start_date: "2018"
    year_of_completion: 2020
    additional_info:
      exam:
        "Machine Learning": "A+"
        "Distributed Systems": "A"
        "Algorithms": "A"

experience_details:
  - position: "Senior Software Engineer"
    company: "TechCorp Inc."
    employment_period: "06/2020 - Present"
    location: "San Francisco, CA"
    industry: "Technology"
    key_responsibilities:
      - responsibility: "Led backend architecture redesign reducing latency by 40%"
      - responsibility: "Mentored team of 5 junior engineers"
      - responsibility: "Implemented CI/CD pipeline with 99.9% uptime"
    skills_acquired:
      - "Python"
      - "Kubernetes"
      - "AWS"
      - "System Design"

projects:
  - name: "AI Resume Builder"
    description: "Open-source tool for generating tailored resumes using LLMs"
    link: "https://github.com/johndoe/ai-resume"

achievements:
  - name: "Employee of the Year"
    description: "Recognized for outstanding technical contributions"

certifications:
  - name: "AWS Solutions Architect"
    description: "Professional certification for cloud architecture"

languages:
  - language: "English"
    proficiency: "Native"
  - language: "Spanish"
    proficiency: "Intermediate"

interests:
  - "Machine Learning"
  - "Open Source"
  - "Cloud Architecture"`;

        /* ========== INITIALIZATION ========== */
        document.addEventListener('DOMContentLoaded', () => {
            checkHealth();
            loadStyles();
            renderHistory();
            loadResumeFromServer();
            loadPreferencesFromServer();
            setupTagEnterKeys();
        });

        /* ========== TAB SWITCHING ========== */
        function switchTab(tabName) {
            document.querySelectorAll('.main-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
            document.getElementById('tab-' + tabName).classList.add('active');
            const tabs = document.querySelectorAll('.main-tab');
            const tabMap = ['generate', 'resume', 'settings', 'bot', 'applications'];
            const idx = tabMap.indexOf(tabName);
            if (idx >= 0 && tabs[idx]) tabs[idx].classList.add('active');
            if (tabName === 'generate') updateResumePreview();
            if (tabName === 'bot') updateBotModelOptions();
            if (tabName === 'applications') loadApplications();
        }

        /* ========== PLATFORM CREDENTIAL PANEL TOGGLE ========== */
        ['linkedin','indeed','glassdoor','ziprecruiter','dice'].forEach(p => {
            const cb = document.getElementById('plt-' + p);
            if (cb) cb.addEventListener('change', function() {
                const panel = document.getElementById('cred-' + p);
                if (panel) panel.style.display = this.checked ? 'block' : 'none';
            });
        });

        /* ========== BOT LLM MODEL OPTIONS ========== */
        function updateBotModelOptions() {
            const type = document.getElementById('bot-llm-type').value;
            const select = document.getElementById('bot-llm-model');
            const options = modelOptions[type] || [];
            select.innerHTML = options.map(o => `<option value="${o.value}">${o.label}</option>`).join('');
        }

        /* ========== CREDENTIALS ========== */
        async function loadCredentials() {
            try {
                const res = await fetch('/api/credentials');
                const data = await res.json();
                ['linkedin','indeed','glassdoor','ziprecruiter','dice'].forEach(p => {
                    const creds = data[p] || {};
                    const emailEl = document.getElementById('cred-' + p + '-email');
                    const passEl = document.getElementById('cred-' + p + '-password');
                    if (emailEl && creds.email) emailEl.value = creds.email;
                    if (passEl && creds.password) passEl.value = creds.password === '***' ? '' : creds.password;
                });
                showStatusMsg('credStatus', 'success', 'Credentials loaded.');
            } catch(e) {
                showStatusMsg('credStatus', 'error', 'Failed to load credentials: ' + e.message);
            }
        }

        async function saveCredentials() {
            const body = {};
            ['linkedin','indeed','glassdoor','ziprecruiter','dice'].forEach(p => {
                const emailEl = document.getElementById('cred-' + p + '-email');
                const passEl = document.getElementById('cred-' + p + '-password');
                if (emailEl && passEl && (emailEl.value || passEl.value)) {
                    body[p] = { email: emailEl.value, password: passEl.value };
                }
            });
            try {
                const res = await fetch('/api/credentials', {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(body),
                });
                const data = await res.json();
                if (res.ok) showStatusMsg('credStatus', 'success', 'Credentials saved.');
                else showStatusMsg('credStatus', 'error', data.detail || 'Save failed.');
            } catch(e) {
                showStatusMsg('credStatus', 'error', 'Network error: ' + e.message);
            }
        }

        /* ========== BOT CONTROL ========== */
        let botWs = null;

        function botAppendLog(msg, color) {
            const log = document.getElementById('bot-log');
            const div = document.createElement('div');
            div.style.color = color || '#d4d4d4';
            div.textContent = '[' + new Date().toLocaleTimeString() + '] ' + msg;
            log.appendChild(div);
            log.scrollTop = log.scrollHeight;
        }

        function clearBotLog() {
            const log = document.getElementById('bot-log');
            log.innerHTML = '';
        }

        function updateBotStatus(data) {
            const stats = data.stats || {};
            document.getElementById('bot-status-text').textContent = data.status || 'idle';
            document.getElementById('bot-platform-text').textContent = stats.current_platform || '—';
            document.getElementById('bot-job-text').textContent = stats.current_job || '—';
            document.getElementById('stat-applied').textContent = stats.applied || 0;
            document.getElementById('stat-skipped').textContent = stats.skipped || 0;
            document.getElementById('stat-failed').textContent = stats.failed || 0;

            const running = data.status === 'running';
            const paused = data.status === 'paused';
            const idle = data.status === 'idle';
            document.getElementById('btn-bot-start').disabled = running || paused;
            document.getElementById('btn-bot-pause').disabled = idle || paused;
            document.getElementById('btn-bot-stop').disabled = idle;
        }

        function connectBotWs() {
            if (botWs) botWs.close();
            const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
            botWs = new WebSocket(proto + '//' + location.host + '/ws/bot');
            botWs.onmessage = function(e) {
                const data = JSON.parse(e.data);
                if (data.msg) botAppendLog(data.msg);
                updateBotStatus(data);
            };
            botWs.onclose = function() {
                setTimeout(() => { if (document.getElementById('tab-bot').classList.contains('active')) connectBotWs(); }, 3000);
            };
        }

        async function botStart() {
            const platforms = ['linkedin','indeed','glassdoor','ziprecruiter','dice','universal']
                .filter(p => document.getElementById('plt-' + p) && document.getElementById('plt-' + p).checked);
            if (!platforms.length) { alert('Select at least one platform.'); return; }
            const apiKey = document.getElementById('bot-api-key').value.trim();
            const llmType = document.getElementById('bot-llm-type').value;
            if (!apiKey && llmType !== 'ollama') { alert('Please enter your LLM API key.'); return; }

            const body = {
                platforms,
                llm_api_key: apiKey,
                llm_model_type: llmType,
                llm_model: document.getElementById('bot-llm-model').value,
                min_score: parseInt(document.getElementById('bot-min-score').value) || 7,
                max_applications: parseInt(document.getElementById('bot-max-apps').value) || 50,
                headless: document.getElementById('bot-headless').checked,
                generate_tailored_resume: document.getElementById('bot-tailored-resume').checked,
            };
            try {
                const res = await fetch('/api/bot/start', {
                    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body),
                });
                const data = await res.json();
                if (res.ok) {
                    botAppendLog('Bot started — session ' + data.session_id, '#4ec9b0');
                    connectBotWs();
                } else {
                    botAppendLog('Start failed: ' + (data.detail || 'Unknown error'), '#f44747');
                }
            } catch(e) {
                botAppendLog('Network error: ' + e.message, '#f44747');
            }
        }

        async function botPause() {
            const s = document.getElementById('btn-bot-pause');
            if (s.textContent.includes('Pause')) {
                await fetch('/api/bot/pause', {method:'POST'});
                s.textContent = '▶ Resume';
            } else {
                await fetch('/api/bot/resume', {method:'POST'});
                s.textContent = '⏸ Pause';
            }
        }

        async function botStop() {
            await fetch('/api/bot/stop', {method:'POST'});
            botAppendLog('Stop requested...', '#ce9178');
        }

        /* ========== APPLICATIONS ========== */
        async function loadApplications() {
            const platform = document.getElementById('app-filter-platform').value;
            const status = document.getElementById('app-filter-status').value;
            let url = '/api/applications?limit=200';
            if (platform) url += '&platform=' + encodeURIComponent(platform);
            if (status) url += '&status=' + encodeURIComponent(status);
            try {
                const res = await fetch(url);
                const data = await res.json();
                // Update stats
                const stats = data.stats || {};
                document.getElementById('app-stat-total').textContent = stats.total || 0;
                document.getElementById('app-stat-applied').textContent = stats.applied || 0;
                document.getElementById('app-stat-skipped').textContent = stats.skipped || 0;
                document.getElementById('app-stat-failed').textContent = stats.failed || 0;
                // Populate table
                const tbody = document.getElementById('app-tbody');
                const apps = data.applications || [];
                if (!apps.length) {
                    tbody.innerHTML = '<tr><td colspan="7" style="padding:24px;text-align:center;color:var(--gray-400)">No applications found.</td></tr>';
                    return;
                }
                const statusColors = {applied:'var(--success)',skipped:'var(--warning)',failed:'var(--danger)',discovered:'var(--gray-500)',scored:'var(--primary)'};
                tbody.innerHTML = apps.map(a => `
                    <tr style="border-bottom:1px solid var(--gray-100);cursor:pointer" onmouseover="this.style.background='var(--gray-50)'" onmouseout="this.style.background=''">
                        <td style="padding:10px 16px"><span class="badge" style="background:var(--primary-light);color:var(--primary)">${a.platform || '—'}</span></td>
                        <td style="padding:10px 16px">${escHtml(a.company || '—')}</td>
                        <td style="padding:10px 16px">${escHtml(a.title || '—')}</td>
                        <td style="padding:10px 16px;text-align:center">${a.score ? '<strong>' + a.score + '</strong>/10' : '—'}</td>
                        <td style="padding:10px 16px"><span style="color:${statusColors[a.status]||'var(--gray-500)'};font-weight:600">${a.status || '—'}</span></td>
                        <td style="padding:10px 16px;color:var(--gray-500)">${a.applied_at ? new Date(a.applied_at).toLocaleDateString() : (a.discovered_at ? new Date(a.discovered_at).toLocaleDateString() : '—')}</td>
                        <td style="padding:10px 16px">${a.url ? '<a href="' + escHtml(a.url) + '" target="_blank" style="color:var(--primary)">Open &#8599;</a>' : '—'}</td>
                    </tr>
                `).join('');
            } catch(e) {
                console.error('Failed to load applications:', e);
            }
        }

        function escHtml(s) {
            return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
        }

        function showStatusMsg(id, type, msg) {
            const el = document.getElementById(id);
            if (!el) return;
            el.className = 'status-msg status-' + type;
            el.textContent = msg;
            setTimeout(() => { el.textContent = ''; el.className = 'status-msg'; }, 5000);
        }

        function updateResumePreview() {
            const yaml = document.getElementById('resumeYaml').value.trim();
            const preview = document.getElementById('resumePreview');
            if (yaml) {
                const lines = yaml.split('\n');
                const previewLines = lines.slice(0, 8).join('\n');
                const more = lines.length > 8 ? `\n... (${lines.length - 8} more lines)` : '';
                preview.innerHTML = `<pre style="font-size:12px;color:var(--gray-600);white-space:pre-wrap;margin:0;background:var(--gray-50);padding:12px;border-radius:var(--radius);border:1px solid var(--gray-200);max-height:200px;overflow-y:auto;">${escapeHtml(previewLines + more)}</pre>`;
            } else {
                preview.innerHTML = '<p>No resume loaded yet. Go to the Resume tab to enter your data.</p>';
            }
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        /* ========== HEALTH CHECK ========== */
        async function checkHealth() {
            const badge = document.getElementById('healthBadge');
            try {
                const res = await fetch('/api/health');
                if (res.ok) {
                    badge.className = 'badge badge-success';
                    badge.textContent = 'Connected';
                } else {
                    badge.className = 'badge badge-danger';
                    badge.textContent = 'Error';
                }
            } catch(e) {
                badge.className = 'badge badge-danger';
                badge.textContent = 'Offline';
            }
        }

        /* ========== LOAD STYLES ========== */
        async function loadStyles() {
            const select = document.getElementById('styleSelect');
            try {
                const res = await fetch('/api/styles');
                const data = await res.json();
                select.innerHTML = '';
                if (data.styles && data.styles.length > 0) {
                    data.styles.forEach(s => {
                        const opt = document.createElement('option');
                        opt.value = s.name;
                        opt.textContent = `${s.name} (by ${s.author})`;
                        select.appendChild(opt);
                    });
                } else {
                    select.innerHTML = '<option value="">No styles available</option>';
                }
            } catch(e) {
                select.innerHTML = '<option value="">Failed to load styles</option>';
            }
        }

        /* ========== PROVIDER CHANGE ========== */
        function onProviderChange() {
            const provider = document.getElementById('llmProvider').value;
            const modelSelect = document.getElementById('llmModel');
            const models = modelOptions[provider] || [];
            modelSelect.innerHTML = '';
            models.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m.value;
                opt.textContent = m.label;
                modelSelect.appendChild(opt);
            });
        }

        /* ========== ACTION SELECTION ========== */
        function selectAction(action) {
            currentAction = action;
            document.querySelectorAll('.action-card').forEach(c => c.classList.remove('selected'));
            document.getElementById('action-' + action).classList.add('selected');
            const jobUrlGroup = document.getElementById('jobUrlGroup');
            if (action === 'resume_tailored' || action === 'cover_letter') {
                jobUrlGroup.classList.add('show');
            } else {
                jobUrlGroup.classList.remove('show');
            }
        }

        /* ========== LOAD EXAMPLE ========== */
        function loadExample() {
            document.getElementById('resumeYaml').value = exampleYaml;
            showStatusMsg('resumeStatus', 'info', 'Example template loaded (not saved to server).');
        }

        /* ========== ALERTS ========== */
        function showAlert(type, message) {
            const box = document.getElementById('alertBox');
            box.className = `alert alert-${type} show`;
            box.textContent = message;
            setTimeout(() => { box.classList.remove('show'); }, 5000);
        }

        function showStatusMsg(elementId, type, message) {
            const el = document.getElementById(elementId);
            if (!el) return;
            el.className = `status-msg ${type} show`;
            el.textContent = message;
            setTimeout(() => { el.classList.remove('show'); }, 5000);
        }

        /* ========== STATUS LOG ========== */
        function addStatusLog(message) {
            const log = document.getElementById('statusLog');
            const time = new Date().toLocaleTimeString();
            const entry = document.createElement('div');
            entry.className = 'status-entry';
            entry.innerHTML = `<span class="status-time">${time}</span>${escapeHtml(message)}`;
            log.appendChild(entry);
            log.scrollTop = log.scrollHeight;
        }

        /* ========== RESUME: LOAD / SAVE ========== */
        async function loadResumeFromServer() {
            try {
                const res = await fetch('/api/resume');
                if (!res.ok) throw new Error('Failed to load resume');
                const data = await res.json();
                if (data.resume_yaml) {
                    document.getElementById('resumeYaml').value = data.resume_yaml;
                    showStatusMsg('resumeStatus', 'success', 'Resume loaded from server.');
                }
            } catch(e) {
                showStatusMsg('resumeStatus', 'error', `Failed to load resume: ${e.message}`);
            }
        }

        async function saveResumeToServer() {
            const yaml = document.getElementById('resumeYaml').value.trim();
            if (!yaml) {
                showStatusMsg('resumeStatus', 'error', 'Resume YAML cannot be empty.');
                return;
            }
            try {
                const res = await fetch('/api/resume', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ resume_yaml: yaml }),
                });
                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || 'Save failed');
                }
                const data = await res.json();
                showStatusMsg('resumeStatus', 'success', data.message || 'Resume saved.');
            } catch(e) {
                showStatusMsg('resumeStatus', 'error', `Failed to save: ${e.message}`);
            }
        }

        /* ========== PREFERENCES: LOAD / SAVE ========== */
        async function loadPreferencesFromServer() {
            try {
                const res = await fetch('/api/preferences');
                if (!res.ok) throw new Error('Failed to load preferences');
                const data = await res.json();
                populatePreferencesForm(data);
                showStatusMsg('settingsStatus', 'success', 'Preferences loaded from server.');
            } catch(e) {
                showStatusMsg('settingsStatus', 'error', `Failed to load preferences: ${e.message}`);
            }
        }

        function populatePreferencesForm(data) {
            document.getElementById('pref_remote').checked = !!data.remote;
            document.getElementById('pref_hybrid').checked = !!data.hybrid;
            document.getElementById('pref_onsite').checked = !!data.onsite;

            const exp = data.experience_level || {};
            document.getElementById('pref_exp_internship').checked = !!exp.internship;
            document.getElementById('pref_exp_entry').checked = !!exp.entry;
            document.getElementById('pref_exp_associate').checked = !!exp.associate;
            document.getElementById('pref_exp_mid_senior').checked = !!exp.mid_senior_level;
            document.getElementById('pref_exp_director').checked = !!exp.director;
            document.getElementById('pref_exp_executive').checked = !!exp.executive;

            const jt = data.job_types || {};
            document.getElementById('pref_jt_full_time').checked = !!jt.full_time;
            document.getElementById('pref_jt_contract').checked = !!jt.contract;
            document.getElementById('pref_jt_part_time').checked = !!jt.part_time;
            document.getElementById('pref_jt_temporary').checked = !!jt.temporary;
            document.getElementById('pref_jt_internship').checked = !!jt.internship;
            document.getElementById('pref_jt_other').checked = !!jt.other;
            document.getElementById('pref_jt_volunteer').checked = !!jt.volunteer;

            const dt = data.date || {};
            let selectedDate = '24_hours';
            if (dt.all_time) selectedDate = 'all_time';
            else if (dt.month) selectedDate = 'month';
            else if (dt.week) selectedDate = 'week';
            else if (dt['24_hours']) selectedDate = '24_hours';
            const radios = document.querySelectorAll('input[name="datePosted"]');
            radios.forEach(r => { r.checked = (r.value === selectedDate); });

            tagData.positions = Array.isArray(data.positions) ? [...data.positions] : [];
            renderTags('positions');
            tagData.locations = Array.isArray(data.locations) ? [...data.locations] : [];
            renderTags('locations');

            document.getElementById('pref_distance').value = String(data.distance != null ? data.distance : 100);

            tagData.company_blacklist = Array.isArray(data.company_blacklist) ? [...data.company_blacklist] : [];
            renderTags('company_blacklist');
            tagData.title_blacklist = Array.isArray(data.title_blacklist) ? [...data.title_blacklist] : [];
            renderTags('title_blacklist');
            tagData.location_blacklist = Array.isArray(data.location_blacklist) ? [...data.location_blacklist] : [];
            renderTags('location_blacklist');

            document.getElementById('pref_apply_once').checked = data.apply_once_at_company !== false;
        }

        function gatherPreferencesFromForm() {
            const selectedDate = document.querySelector('input[name="datePosted"]:checked');
            const dateValue = selectedDate ? selectedDate.value : '24_hours';

            return {
                remote: document.getElementById('pref_remote').checked,
                hybrid: document.getElementById('pref_hybrid').checked,
                onsite: document.getElementById('pref_onsite').checked,
                experience_level: {
                    internship: document.getElementById('pref_exp_internship').checked,
                    entry: document.getElementById('pref_exp_entry').checked,
                    associate: document.getElementById('pref_exp_associate').checked,
                    mid_senior_level: document.getElementById('pref_exp_mid_senior').checked,
                    director: document.getElementById('pref_exp_director').checked,
                    executive: document.getElementById('pref_exp_executive').checked,
                },
                job_types: {
                    full_time: document.getElementById('pref_jt_full_time').checked,
                    contract: document.getElementById('pref_jt_contract').checked,
                    part_time: document.getElementById('pref_jt_part_time').checked,
                    temporary: document.getElementById('pref_jt_temporary').checked,
                    internship: document.getElementById('pref_jt_internship').checked,
                    other: document.getElementById('pref_jt_other').checked,
                    volunteer: document.getElementById('pref_jt_volunteer').checked,
                },
                date: {
                    all_time: dateValue === 'all_time',
                    month: dateValue === 'month',
                    week: dateValue === 'week',
                    twenty_four_hours: dateValue === '24_hours',
                },
                positions: [...tagData.positions],
                locations: [...tagData.locations],
                apply_once_at_company: document.getElementById('pref_apply_once').checked,
                distance: parseInt(document.getElementById('pref_distance').value, 10),
                company_blacklist: [...tagData.company_blacklist],
                title_blacklist: [...tagData.title_blacklist],
                location_blacklist: [...tagData.location_blacklist],
            };
        }

        async function savePreferencesToServer() {
            const prefs = gatherPreferencesFromForm();
            try {
                const res = await fetch('/api/preferences', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(prefs),
                });
                if (!res.ok) {
                    const err = await res.json();
                    const detail = err.detail;
                    const msg = Array.isArray(detail) ? detail.join('; ') : (detail || 'Save failed');
                    throw new Error(msg);
                }
                const data = await res.json();
                showStatusMsg('settingsStatus', 'success', data.message || 'Preferences saved.');
            } catch(e) {
                showStatusMsg('settingsStatus', 'error', `Failed to save: ${e.message}`);
            }
        }

        /* ========== TAG MANAGEMENT ========== */
        function setupTagEnterKeys() {
            Object.entries(tagInputIds).forEach(([key, inputId]) => {
                const el = document.getElementById(inputId);
                if (el) {
                    el.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter') {
                            e.preventDefault();
                            addTag(key);
                        }
                    });
                }
            });
        }

        function addTag(group) {
            const inputId = tagInputIds[group];
            const input = document.getElementById(inputId);
            if (!input) return;
            const val = input.value.trim();
            if (!val) return;
            if (tagData[group].includes(val)) {
                input.value = '';
                return;
            }
            tagData[group].push(val);
            input.value = '';
            renderTags(group);
        }

        function removeTag(group, index) {
            tagData[group].splice(index, 1);
            renderTags(group);
        }

        function renderTags(group) {
            const container = document.getElementById(group + '-tags');
            if (!container) return;
            if (tagData[group].length === 0) {
                container.innerHTML = '<span style="color:var(--gray-400);font-size:12px;">None</span>';
                return;
            }
            container.innerHTML = tagData[group].map((item, i) =>
                `<span class="tag">${escapeHtml(item)}<button class="tag-remove" onclick="removeTag('${group}', ${i})" title="Remove">&times;</button></span>`
            ).join('');
        }

        /* ========== GENERATION ========== */
        async function startGeneration() {
            const apiKey = document.getElementById('apiKey').value.trim();
            const resumeYaml = document.getElementById('resumeYaml').value.trim();
            const jobUrl = document.getElementById('jobUrl').value.trim();
            const style = document.getElementById('styleSelect').value;
            const provider = document.getElementById('llmProvider').value;
            const model = document.getElementById('llmModel').value;

            if (!apiKey) { showAlert('error', 'Please enter your API key.'); return; }
            if (!resumeYaml) {
                showAlert('error', 'No resume data found. Please go to the Resume tab and enter your resume YAML.');
                return;
            }
            if ((currentAction === 'resume_tailored' || currentAction === 'cover_letter') && !jobUrl) {
                showAlert('error', 'Please enter a job posting URL for tailored documents.');
                return;
            }

            const btn = document.getElementById('generateBtn');
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span> Generating...';
            document.getElementById('downloadSection').classList.add('hidden');
            document.getElementById('progressContainer').classList.add('active');
            document.getElementById('progressBar').style.width = '0%';
            document.getElementById('progressBar').className = 'progress-bar-fill';
            document.getElementById('progressPercent').textContent = '0%';
            document.getElementById('progressText').textContent = 'Starting...';
            document.getElementById('statusLog').innerHTML = '';
            addStatusLog('Submitting generation request...');

            try {
                const res = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        action: currentAction,
                        resume_yaml: resumeYaml,
                        job_url: jobUrl || null,
                        style: style || null,
                        llm_api_key: apiKey,
                        llm_model_type: provider,
                        llm_model: model,
                    }),
                });

                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || 'Request failed');
                }

                const data = await res.json();
                currentJobId = data.job_id;
                addStatusLog(`Job created: ${currentJobId.substring(0, 8)}...`);
                connectWebSocket(currentJobId);
                pollStatus(currentJobId);

            } catch(err) {
                showAlert('error', `Failed to start generation: ${err.message}`);
                btn.disabled = false;
                btn.innerHTML = '&#9889; Generate Document';
                document.getElementById('progressContainer').classList.remove('active');
            }
        }

        /* ========== WEBSOCKET ========== */
        function connectWebSocket(jobId) {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/${jobId}`;
            try {
                ws = new WebSocket(wsUrl);
                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    updateProgress(data);
                };
                ws.onerror = () => { /* Fallback to polling */ };
                ws.onclose = () => { ws = null; };
            } catch(e) { /* Fallback to polling */ }
        }

        /* ========== POLLING ========== */
        async function pollStatus(jobId) {
            const interval = setInterval(async () => {
                try {
                    const res = await fetch(`/api/status/${jobId}`);
                    const data = await res.json();
                    updateProgress(data);
                    if (data.status === 'completed' || data.status === 'failed') {
                        clearInterval(interval);
                    }
                } catch(e) { /* continue polling */ }
            }, 2000);
        }

        /* ========== PROGRESS UI ========== */
        function updateProgress(data) {
            const bar = document.getElementById('progressBar');
            const percent = document.getElementById('progressPercent');
            const text = document.getElementById('progressText');
            const btn = document.getElementById('generateBtn');

            bar.style.width = `${data.progress || 0}%`;
            percent.textContent = `${data.progress || 0}%`;
            text.textContent = data.message || '';
            addStatusLog(data.message || data.status);

            if (data.status === 'completed') {
                bar.classList.add('success');
                btn.disabled = false;
                btn.innerHTML = '&#9889; Generate Document';
                downloadUrl = data.download_url;
                document.getElementById('downloadSection').classList.remove('hidden');
                showAlert('success', 'Document generated successfully! Click Download to save.');
                addToHistory(currentAction, downloadUrl);
                if (ws) { ws.close(); ws = null; }
            } else if (data.status === 'failed') {
                bar.classList.add('error');
                btn.disabled = false;
                btn.innerHTML = '&#9889; Generate Document';
                showAlert('error', `Generation failed: ${data.error || data.message}`);
                if (ws) { ws.close(); ws = null; }
            }
        }

        /* ========== DOWNLOAD ========== */
        function downloadDocument() {
            if (downloadUrl) {
                window.location.href = downloadUrl;
            }
        }

        /* ========== HISTORY ========== */
        function addToHistory(action, url) {
            const labels = {
                resume: 'Base Resume',
                resume_tailored: 'Tailored Resume',
                cover_letter: 'Cover Letter',
            };
            genHistory.unshift({
                action: labels[action] || action,
                time: new Date().toLocaleString(),
                url: url,
            });
            if (genHistory.length > 10) genHistory = genHistory.slice(0, 10);
            localStorage.setItem('aihawk_history', JSON.stringify(genHistory));
            renderHistory();
        }

        function renderHistory() {
            const list = document.getElementById('historyList');
            if (genHistory.length === 0) {
                list.innerHTML = '<p style="color: var(--gray-400); text-align: center; padding: 20px;">No documents generated yet.</p>';
                return;
            }
            list.innerHTML = genHistory.map(h => `
                <div class="history-item">
                    <div class="history-info">
                        <h4>${escapeHtml(h.action)}</h4>
                        <p>${escapeHtml(h.time)}</p>
                    </div>
                    ${h.url ? `<a href="${h.url}" class="btn btn-outline btn-sm" style="text-decoration:none;">Download</a>` : ''}
                </div>
            `).join('');
        }

        function clearHistory() {
            genHistory = [];
            localStorage.removeItem('aihawk_history');
            renderHistory();
        }

    </script>
</body>
</html>"""
