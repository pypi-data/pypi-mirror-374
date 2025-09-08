TEMPLATE = """<!doctype html>
<html lang="en">

<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Temp Mail Generator</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@200..1000&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-1: #0ea5e9;
            --bg-2: #8b5cf6;
            --bg-3: #14b8a6;
            --card-bg: rgba(255, 255, 255, 0.06);
            --card-border: rgba(255, 255, 255, 0.18);
            --text: #eef2ff;
            --muted: #c7d2fe;
            --accent: #22c55e;
            --accent-2: #38bdf8;
        }

        * {
            box-sizing: border-box;
            font-family: "Cairo";
        }

        html, body { height: 100%; }

        body {
            margin: 0;
            font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
            color: var(--text);
            background: linear-gradient(120deg, var(--bg-1), var(--bg-2), var(--bg-3));
            background-size: 180% 180%;
            animation: gradientShift 12s ease infinite;
            /* display: grid; */
            place-items: center;
            padding: 24px;
        }

        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .card {
            width: 85%;
            border-radius: 24px;
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.06);
            backdrop-filter: blur(14px) saturate(140%);
            -webkit-backdrop-filter: blur(14px) saturate(140%);
            padding: 28px 28px 32px;
            position: relative;
            overflow: hidden;
        }

        .glow {
            position: absolute;
            inset: -40%;
            background: radial-gradient(600px 300px at 20% 10%, rgba(56, 189, 248, .25), transparent 60%),
                        radial-gradient(600px 300px at 90% 80%, rgba(34, 197, 94, .22), transparent 60%);
            filter: blur(40px);
            pointer-events: none;
        }

        header {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 18px;
        }

        .logo {
            width: 64px;
            height: 64px;
            display: grid;
            place-items: center;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid var(--card-border);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
        }

        h1 {
            font-size: clamp(22px, 2.4vw, 28px);
            line-height: 1.1;
            margin: 0;
            font-weight: 800;
            letter-spacing: -0.02em;
        }

        p.sub {
            margin: 4px 0 0;
            color: var(--muted);
            font-size: 14px;
        }

        .panel {
            margin-top: 18px;
            display: grid;
            gap: 14px;
        }

        .row {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 10px;
            align-items: center;
        }

        .email-box {
            height: 54px;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid var(--card-border);
            display: flex;
            align-items: center;
            padding: 0 12px;
            gap: 10px;
        }

        .email-box input {
            background: transparent;
            border: 0;
            outline: none;
            color: var(--text);
            font-size: 16px;
            width: 100%;
            font-weight: 600;
        }

        button.primary {
            height: 54px;
            padding: 0 20px;
            border-radius: 14px;
            border: 0;
            cursor: pointer;
            font-weight: 700;
            letter-spacing: 0.01em;
            color: #0b1220;
            background: linear-gradient(180deg, #a7f3d0, #22c55e);
            box-shadow: 0 10px 24px rgba(16, 185, 129, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.4);
            transition: transform .06s ease, filter .2s ease;
            font-size: 24px;
        }

        button.primary:hover { filter: brightness(1.03); }
        button.primary:active { transform: translateY(1px); }

        button.icon {
            height: 46px;
            padding: 0 14px;
            border-radius: 12px;
            border: 1px solid var(--card-border);
            background: rgba(255, 255, 255, 0.08);
            color: var(--text);
            cursor: pointer;
        }

        button.icon:active { transform: translateY(1px); }

        .hint {
            font-size: 12px;
            color: var(--muted);
            text-align: center;
            margin-top: 6px;
        }

        footer {
            margin-top: 20px;
            font-size: 12px;
            color: var(--muted);
            text-align: center;
        }

        .inbox {
            margin-top: 20px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--card-border);
            border-radius: 18px;
            padding: 16px;
            max-height: 300px;
            overflow-y: auto;
            backdrop-filter: blur(8px);
        }

        .inbox-item {
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 14px;
            padding: 12px 14px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: background 0.2s ease, transform 0.1s ease;
        }

        .inbox-item:hover { background: rgba(255, 255, 255, 0.1); transform: translateY(-1px); }

        .inbox-item strong {
            color: var(--accent-2);
            font-weight: 600;
            display: block;
            margin-bottom: 2px;
        }

        .inbox-item small {
            color: var(--muted);
            font-size: 12px;
        }

        .inbox-message {
            margin-top: 8px;
            font-size: 14px;
            line-height: 1.4;
            color: var(--text);
            display: none;
        }

        .inbox-item.open .inbox-message { display: block; }

        .sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }

        #fr { display: none; }
        #delBtn { display: none; background: linear-gradient(180deg, #f3a7a7, #c5228bb0) !important; }
    </style>
</head>

<body>
    <main class="card" role="main" aria-labelledby="title">
        <div class="glow" aria-hidden="true"></div>

        <header>
            <div class="logo" aria-hidden="true">
                <svg width="36" height="36" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                    <rect x="4" y="10" width="56" height="44" rx="8" fill="url(#g1)" stroke="rgba(255,255,255,.35)" />
                    <defs>
                        <linearGradient id="g1" x1="4" y1="10" x2="60" y2="54" gradientUnits="userSpaceOnUse">
                            <stop stop-color="#1f2937" />
                            <stop offset="1" stop-color="#0b1220" />
                        </linearGradient>
                    </defs>
                    <path d="M8 16l24 18L56 16" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
                    <circle cx="50" cy="48" r="10" fill="#16a34a" stroke="rgba(255,255,255,.5)" />
                    <path d="M45 48l3.5 3.5L55 45" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
            </div>
            <div>
                <h1 id="title">Temp Mail Generator</h1>
                <p class="sub">Generate a disposable address with one click.</p>
            </div>
        </header>

        <section class="panel" aria-label="Email generator">
            <div class="row" id="fr">
                <div class="email-box" aria-live="polite">
                    <span aria-hidden="true">📧</span>
                    <input id="email" type="text" value="" placeholder="your.temp@mail" readonly aria-readonly="true" />
                </div>
                <button id="copyBtn" class="icon" type="button" title="Copy to clipboard" aria-label="Copy email">Copy</button>
            </div>
            <div class="row">
                <button id="genBtn" class="primary ripple" type="button">Generate Email</button>
                <button id="delBtn" class="primary ripple" type="button">Delete Email</button>
            </div>
            <div class="hint" id="refreshHint" style="display:none;">Refreshing in <span id="refreshTimer">10</span>s</div>

            <div id="inboxContainer" class="inbox">
                <div class="inbox-item">No messages yet.</div>
            </div>
        </section>

        <footer>
            <span>Made with ❤️ MrJo0x01</span>
        </footer>
    </main>

    <script>
        const emailInput = document.getElementById('email');
        const genBtn = document.getElementById('genBtn');
        const delBtn = document.getElementById('delBtn');
        const copyBtn = document.getElementById('copyBtn');
        const inboxContainer = document.getElementById('inboxContainer');
        const refreshHint = document.getElementById('refreshHint');
        const refreshTimer = document.getElementById('refreshTimer');
        let inboxInterval = null;
        let countdownInterval = null;
        let refreshSeconds = 10;
        let tokenValue = null;

        function sample(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
        function randomInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
        function randomChunk() { return Math.random().toString(36).slice(2, 2 + randomInt(2, 4)); }

        function startRefreshCountdown() {
            if (countdownInterval) clearInterval(countdownInterval);
            refreshSeconds = 10;
            refreshHint.style.display = "block";
            refreshTimer.textContent = refreshSeconds;
            countdownInterval = setInterval(() => {
                refreshSeconds--;
                if (refreshSeconds < 0) refreshSeconds = 10;
                refreshTimer.textContent = refreshSeconds;
            }, 1000);
        }

        function generateEmail() {
            genBtn.style.display = "none";
            fetch('/generate')
                .then(res => res.json())
                .then(data => {
                    emailInput.value = data.email;
                    tokenValue = data.token;
                    document.getElementById('fr').style.display = 'grid';
                    if (inboxInterval) clearInterval(inboxInterval);
                    inboxInterval = setInterval(loadInbox, 10000);
                    startRefreshCountdown();
                    delBtn.style.display = "inline";
                    genBtn.style.display = "none";
                });
        }

        async function copyEmail() {
            const val = emailInput.value.trim();
            if (!val) return;
            try {
                await navigator.clipboard.writeText(val);
                copyBtn.textContent = 'Copied!';
                setTimeout(() => (copyBtn.textContent = 'Copy'), 1200);
            } catch {
                emailInput.select();
                document.execCommand('copy');
            }
        }

        async function loadInbox() {
            const email = tokenValue?.trim();
            if (!email) return;
            await fetch(`/inbox?tk=${encodeURIComponent(tokenValue)}`)
                .then(res => res.json())
                .then(data => {
                    if (data.messages || data.messages.length !== 0) {
                        data.messages.forEach(msg => {
                            if (document.getElementById(msg.id) === null) {
                                const div = document.createElement('div');
                                div.id = msg.id;
                                div.className = 'inbox-item ' + (msg.unread ? 'unread' : '');
                                div.innerHTML = `
                                    <strong>From: ${msg.from}</strong>
                                    <div>Subject: ${msg.subject}</div>
                                    <small>Created Date: ${msg.created_at || ''}</small>
                                    <div class="inbox-message">
                                        ${msg.body_html || msg.body_text || 'No content'}
                                    </div>
                                `;
                                div.addEventListener('click', () => {
                                    div.classList.toggle('open');
                                });
                                inboxContainer.appendChild(div);
                            }
                        });
                    }
                });
                
            startRefreshCountdown();
        }

        genBtn.addEventListener('click', () => {
            delBtn.style.display = "inline-block";
            genBtn.style.display = "none";
            document.getElementById("fr").style.display = "grid";
            generateEmail();
        });

        delBtn.addEventListener("click", () => { window.location.reload(); });
        copyBtn.addEventListener('click', copyEmail);

        window.addEventListener('keydown', (e) => {
            if (e.key.toLowerCase() === 'c') { copyEmail(); }
        });
    </script>
</body>
</html>
"""