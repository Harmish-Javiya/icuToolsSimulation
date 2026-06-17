from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from network.shared_state import simulator_data


app = FastAPI(title="CRRT Simulator")


def start_web_server():
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="warning",
    )


@app.get("/api/state")
def state():
    return simulator_data


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>CRRT Simulator Dashboard</title>
        <style>
            :root {
                color-scheme: dark;
                --bg: #07111f;
                --panel: rgba(10, 18, 32, 0.88);
                --panel-2: rgba(15, 26, 46, 0.9);
                --text: #e5eefc;
                --muted: #93a4bf;
                --accent: #5dd6c6;
                --accent-2: #7c9cff;
                --danger: #ff6b7a;
                --warning: #ffcc66;
                --border: rgba(148, 163, 184, 0.18);
                --shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
            }

            * { box-sizing: border-box; }

            body {
                margin: 0;
                font-family: "Segoe UI", "Trebuchet MS", sans-serif;
                color: var(--text);
                background:
                    radial-gradient(circle at top left, rgba(93, 214, 198, 0.14), transparent 28%),
                    radial-gradient(circle at top right, rgba(124, 156, 255, 0.16), transparent 24%),
                    linear-gradient(180deg, #091120, #050a13 72%);
                min-height: 100vh;
            }

            .shell {
                max-width: 1280px;
                margin: 0 auto;
                padding: 28px;
            }

            .hero {
                display: grid;
                grid-template-columns: 1.4fr 0.8fr;
                gap: 18px;
                align-items: stretch;
                margin-bottom: 18px;
            }

            .panel {
                background: var(--panel);
                border: 1px solid var(--border);
                border-radius: 22px;
                box-shadow: var(--shadow);
                backdrop-filter: blur(16px);
            }

            .branding {
                padding: 26px;
            }

            .eyebrow {
                display: inline-block;
                padding: 6px 12px;
                border-radius: 999px;
                background: rgba(93, 214, 198, 0.12);
                color: var(--accent);
                font-size: 12px;
                letter-spacing: 0.14em;
                text-transform: uppercase;
                margin-bottom: 14px;
            }

            h1 {
                margin: 0;
                font-size: clamp(30px, 4vw, 52px);
                line-height: 1.02;
            }

            .lede {
                color: var(--muted);
                max-width: 70ch;
                margin: 14px 0 0;
                font-size: 15px;
                line-height: 1.6;
            }

            .status-card {
                padding: 22px;
                display: grid;
                gap: 16px;
                align-content: space-between;
            }

            .status-row {
                display: flex;
                justify-content: space-between;
                gap: 16px;
                padding: 14px 16px;
                border-radius: 16px;
                background: var(--panel-2);
                border: 1px solid var(--border);
            }

            .status-label {
                color: var(--muted);
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.12em;
            }

            .status-value {
                font-size: 18px;
                font-weight: 700;
                text-align: right;
            }

            .grid {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 14px;
                margin-top: 18px;
            }

            .card {
                background: var(--panel);
                border: 1px solid var(--border);
                border-radius: 18px;
                padding: 18px;
                box-shadow: var(--shadow);
                min-height: 120px;
            }

            .card .label {
                color: var(--muted);
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.14em;
                margin-bottom: 10px;
            }

            .card .value {
                font-size: 28px;
                font-weight: 800;
                line-height: 1.1;
            }

            .card .subvalue {
                margin-top: 8px;
                color: var(--muted);
                font-size: 14px;
            }

            .wide {
                grid-column: span 2;
            }

            .alarms {
                margin-top: 18px;
                padding: 18px;
            }

            .section-title {
                margin: 0 0 12px;
                font-size: 18px;
            }

            ul {
                margin: 0;
                padding-left: 20px;
                color: #ffd9dc;
            }

            .ok {
                color: #aef6d0;
            }

            .pill {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 8px 12px;
                border-radius: 999px;
                background: rgba(124, 156, 255, 0.12);
                color: #c9d6ff;
                font-size: 13px;
            }

            .dot {
                width: 10px;
                height: 10px;
                border-radius: 999px;
                background: var(--accent);
                box-shadow: 0 0 0 6px rgba(93, 214, 198, 0.14);
            }

            @media (max-width: 960px) {
                .hero,
                .grid {
                    grid-template-columns: 1fr 1fr;
                }

                .wide {
                    grid-column: span 1;
                }
            }

            @media (max-width: 640px) {
                .shell { padding: 16px; }
                .hero,
                .grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <main class="shell">
            <section class="hero">
                <div class="panel branding">
                    <div class="eyebrow">Live CRRT Monitor</div>
                    <h1>Web-Based CRRT Simulator Dashboard</h1>
                    <p class="lede">
                        Track patient vitals, pressure values, filter health, fluid balance,
                        and active alarms in real time. Leave the simulator running in the
                        background and refresh data every second.
                    </p>
                </div>
                <div class="panel status-card">
                    <div class="status-row">
                        <div>
                            <div class="status-label">Machine Status</div>
                            <div class="status-value" id="machineStatus">Loading...</div>
                        </div>
                        <span class="pill"><span class="dot"></span><span id="therapyMode">--</span></span>
                    </div>
                    <div class="status-row">
                        <div>
                            <div class="status-label">Blood Pressure</div>
                            <div class="status-value" id="bloodPressure">--</div>
                        </div>
                        <div>
                            <div class="status-label">Heart Rate</div>
                            <div class="status-value" id="heartRate">--</div>
                        </div>
                    </div>
                </div>
            </section>

            <section class="grid">
                <div class="card">
                    <div class="label">SpO2</div>
                    <div class="value" id="spo2">--</div>
                    <div class="subvalue">Oxygen saturation</div>
                </div>
                <div class="card">
                    <div class="label">Temperature</div>
                    <div class="value" id="temperature">--</div>
                    <div class="subvalue">Body temperature in °C</div>
                </div>
                <div class="card">
                    <div class="label">BUN</div>
                    <div class="value" id="bun">--</div>
                    <div class="subvalue">Blood urea nitrogen</div>
                </div>
                <div class="card">
                    <div class="label">Creatinine</div>
                    <div class="value" id="creatinine">--</div>
                    <div class="subvalue">Kidney function marker</div>
                </div>
                <div class="card">
                    <div class="label">Potassium</div>
                    <div class="value" id="potassium">--</div>
                    <div class="subvalue">mmol/L</div>
                </div>
                <div class="card">
                    <div class="label">TMP</div>
                    <div class="value" id="tmp">--</div>
                    <div class="subvalue">Transmembrane pressure</div>
                </div>
                <div class="card wide">
                    <div class="label">Filter Health</div>
                    <div class="value" id="filterHealth">--</div>
                    <div class="subvalue" id="filterStatus">--</div>
                </div>
                <div class="card wide">
                    <div class="label">Fluid Balance</div>
                    <div class="value" id="fluidBalance">--</div>
                    <div class="subvalue">Net balance in mL</div>
                </div>
            </section>

            <section class="panel alarms">
                <h2 class="section-title">Alarms</h2>
                <div id="alarms" class="ok">No active alarms</div>
            </section>
        </main>

        <script>
            function setValue(id, value) {
                document.getElementById(id).textContent = value;
            }

            async function refresh() {
                const response = await fetch('/api/state');
                const data = await response.json();

                setValue('heartRate', `${data.heart_rate} bpm`);
                setValue('bloodPressure', `${data.blood_pressure} mmHg`);
                setValue('spo2', `${data.spo2}%`);
                setValue('temperature', `${data.temperature} °C`);
                setValue('bun', data.bun);
                setValue('creatinine', data.creatinine);
                setValue('potassium', data.potassium);
                setValue('tmp', data.pressure.tmp);
                setValue('filterHealth', `${data.filter.health}%`);
                setValue('filterStatus', data.filter.status);
                setValue('fluidBalance', `${data.fluid_balance} mL`);
                setValue('therapyMode', data.therapy_mode);
                setValue('machineStatus', data.machine_status);

                const alarms = document.getElementById('alarms');
                if (data.alarms && data.alarms.length) {
                    alarms.className = '';
                    alarms.innerHTML = '<ul>' + data.alarms.map(alarm => `<li>${alarm}</li>`).join('') + '</ul>';
                } else {
                    alarms.className = 'ok';
                    alarms.textContent = 'No active alarms';
                }
            }

            refresh();
            setInterval(refresh, 1000);
        </script>
    </body>
    </html>
    """