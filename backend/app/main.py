from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.services.camera import start_camera
from app.services.alerts import get_alerts
import threading
from app.services.database import init_db

init_db()

app= FastAPI()
@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/start-camera")
def run_camera():
    thread=threading.Thread(target=start_camera)
    thread.start()
    return {"status": "Camera started"}


@app.get("/alerts")
def read_alerts():
    return {"alerts": get_alerts()}


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
        return """
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>Security Alerts Dashboard</title>
            <style>
                :root {
                    color-scheme: dark;
                    --bg: #08111f;
                    --panel: rgba(10, 20, 38, 0.9);
                    --panel-2: rgba(15, 28, 50, 0.95);
                    --text: #e8eefc;
                    --muted: #9eb0d4;
                    --accent: #4fd1c5;
                    --danger: #ff6b6b;
                    --border: rgba(159, 181, 230, 0.18);
                }

                * {
                    box-sizing: border-box;
                }

                body {
                    margin: 0;
                    min-height: 100vh;
                    font-family: Inter, Segoe UI, Arial, sans-serif;
                    color: var(--text);
                    background:
                        radial-gradient(circle at top left, rgba(79, 209, 197, 0.18), transparent 30%),
                        radial-gradient(circle at top right, rgba(255, 107, 107, 0.16), transparent 24%),
                        linear-gradient(180deg, #060b14 0%, var(--bg) 100%);
                }

                .shell {
                    max-width: 1100px;
                    margin: 0 auto;
                    padding: 32px 20px 40px;
                }

                .hero {
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-end;
                    gap: 16px;
                    margin-bottom: 24px;
                }

                h1 {
                    margin: 0;
                    font-size: clamp(2rem, 4vw, 3.5rem);
                    letter-spacing: -0.04em;
                }

                .subtitle {
                    margin: 10px 0 0;
                    color: var(--muted);
                    max-width: 62ch;
                    line-height: 1.5;
                }

                .actions {
                    display: flex;
                    gap: 12px;
                    flex-wrap: wrap;
                }

                button, a.button {
                    border: 1px solid var(--border);
                    background: linear-gradient(180deg, rgba(79, 209, 197, 0.18), rgba(79, 209, 197, 0.08));
                    color: var(--text);
                    border-radius: 14px;
                    padding: 12px 16px;
                    font: inherit;
                    cursor: pointer;
                    text-decoration: none;
                    transition: transform 0.15s ease, border-color 0.15s ease, background 0.15s ease;
                }

                button:hover, a.button:hover {
                    transform: translateY(-1px);
                    border-color: rgba(79, 209, 197, 0.5);
                }

                .grid {
                    display: grid;
                    grid-template-columns: 1.2fr 0.8fr;
                    gap: 18px;
                }

                .card {
                    background: var(--panel);
                    border: 1px solid var(--border);
                    border-radius: 20px;
                    padding: 20px;
                    backdrop-filter: blur(14px);
                    box-shadow: 0 24px 80px rgba(0, 0, 0, 0.22);
                }

                .stat {
                    display: grid;
                    gap: 6px;
                }

                .stat .value {
                    font-size: 2rem;
                    font-weight: 700;
                }

                .stat .label {
                    color: var(--muted);
                }

                .alert-list {
                    display: grid;
                    gap: 12px;
                    margin-top: 16px;
                }

                .alert-item {
                    background: var(--panel-2);
                    border: 1px solid var(--border);
                    border-radius: 16px;
                    padding: 14px 16px;
                }

                .alert-item strong {
                    display: block;
                    margin-bottom: 6px;
                }

                .meta {
                    color: var(--muted);
                    font-size: 0.92rem;
                }

                .badge {
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    padding: 8px 12px;
                    border-radius: 999px;
                    border: 1px solid var(--border);
                    color: var(--muted);
                }

                .dot {
                    width: 10px;
                    height: 10px;
                    border-radius: 50%;
                    background: var(--danger);
                    box-shadow: 0 0 18px rgba(255, 107, 107, 0.7);
                }

                @media (max-width: 800px) {
                    .hero, .grid {
                        grid-template-columns: 1fr;
                        display: grid;
                    }

                    .hero {
                        align-items: start;
                    }
                }
            </style>
        </head>
        <body>
            <main class="shell">
                <section class="hero">
                    <div>
                        <span class="badge"><span class="dot"></span> Live alerts</span>
                        <h1>Security Alerts Dashboard</h1>
                        <p class="subtitle">Monitor threat detections from the backend in a browser. The list refreshes automatically so you can keep the camera running and watch alerts appear here.</p>
                    </div>
                    <div class="actions">
                        <button onclick="startCamera()">Start Camera</button>
                        <a class="button" href="/alerts" target="_blank" rel="noreferrer">Open JSON</a>
                    </div>
                </section>

                <section class="grid">
                    <article class="card">
                        <div class="stat">
                            <span class="label">Total alerts</span>
                            <span class="value" id="alertCount">0</span>
                        </div>
                        <div class="alert-list" id="alerts"></div>
                    </article>

                    <aside class="card">
                        <div class="stat">
                            <span class="label">System</span>
                            <span class="value" style="font-size:1.4rem;">Backend connected</span>
                        </div>
                        <p class="subtitle" style="margin-top:12px;">The dashboard reads from <code>/alerts</code>. Alert history is currently kept in memory, so it resets when the backend restarts.</p>
                    </aside>
                </section>
            </main>

            <script>
                async function loadAlerts() {
                    const response = await fetch('/alerts');
                    const data = await response.json();
                    const alerts = data.alerts || [];

                    document.getElementById('alertCount').textContent = alerts.length;

                    const container = document.getElementById('alerts');
                    container.innerHTML = '';

                    if (!alerts.length) {
                        container.innerHTML = '<div class="alert-item"><strong>No alerts yet</strong><div class="meta">Run the camera and trigger a knife or gun detection to populate this list.</div></div>';
                        return;
                    }

                    for (const alert of alerts) {
                        const item = document.createElement('div');
                        item.className = 'alert-item';
                        const time = new Date(alert.timestamp * 1000).toLocaleString();
                        item.innerHTML = `<strong>${alert.message}</strong><div class="meta">${time}</div><div class="meta">Detected objects: ${alert.detected_objects.join(', ')}</div>`;
                        container.appendChild(item);
                    }
                }

                async function startCamera() {
                    await fetch('/start-camera');
                    await loadAlerts();
                }

                loadAlerts();
                setInterval(loadAlerts, 2000);
            </script>
        </body>
        </html>
        """