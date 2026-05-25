from flask import Flask, render_template_string
import psutil
import datetime
import subprocess
import os
import pickle
import numpy as np
import sys
sys.path.insert(0, "/home/sam/Desktop/cyber-lab/scripts")
from geo_attack import get_attack_map
import json

app = Flask(__name__, static_folder='/home/sam/Desktop/cyber-lab/static')

cpu_history = []
mem_history = []
time_history = []

MODEL_FILE = os.path.expanduser("~/Desktop/cyber-lab/data/ml_model.pkl")
LOG_DIR = os.path.expanduser("~/Desktop/cyber-lab/logs")

def ml_detect(cpu, memory, disk, connections):
    try:
        with open(MODEL_FILE, 'rb') as f:
            model = pickle.load(f)
        processes = len(psutil.pids())
        X = np.array([[cpu, memory, disk, connections, processes]])
        prediction = model.predict(X)[0]
        score = model.decision_function(X)[0]
        return {
            'is_anomaly': prediction == -1,
            'score': float(score),
            'processes': processes,
            'status': 'ANOMALY' if prediction == -1 else 'Normal'
        }
    except:
        return {
            'is_anomaly': False,
            'score': 0.0,
            'processes': len(psutil.pids()),
            'status': 'Model not ready'
        }

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Cyber Lab Dashboard</title>
    <meta http-equiv="refresh" content="10">
    <script src="/static/chart.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Courier New', monospace;
            background: #0a0a1a;
            color: #00ff88;
            padding: 15px;
            font-size: 13px;
        }

        /* ── Header ── */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border: 1px solid #00ff88;
            padding: 12px 16px;
            margin-bottom: 12px;
            background: #0d1117;
            border-radius: 6px;
        }
        .header-left h1 {
            color: #00ccff;
            font-size: 20px;
            letter-spacing: 1px;
            margin-bottom: 6px;
        }
        .header-left .subtitle {
            color: #00ff88;
            font-size: 12px;
        }
        .header-left .subtitle span { margin: 0 6px; }
        .header-left .last-updated {
            color: #666;
            font-size: 11px;
            margin-top: 4px;
        }
        .header-right {
            text-align: right;
            font-size: 12px;
            color: #aaa;
            line-height: 1.8;
        }
        .header-right .active {
            color: #00ff88;
        }
        .header-right .dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #00ff88;
            border-radius: 50%;
            margin-right: 4px;
        }

        /* ── Grid ── */
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 12px;
        }

        /* ── Panel ── */
        .panel {
            border: 1px solid #00ff88;
            padding: 12px;
            background: #0d1117;
            border-radius: 6px;
            min-height: 200px;
        }
        .panel h3 {
            color: #00ccff;
            font-size: 13px;
            letter-spacing: 1px;
            margin-bottom: 10px;
            border-bottom: 1px solid #1a2a1a;
            padding-bottom: 6px;
        }

        /* ── Login attacks ── */
        .attack-line {
            color: #ff4444;
            font-size: 11px;
            margin-bottom: 4px;
            line-height: 1.4;
        }
        .attack-label {
            color: #ff4444;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 6px;
        }
        .attack-label::before { content: "⚠ "; }
        .total-failed {
            color: #ff4444;
            margin-top: 8px;
            font-size: 12px;
            font-weight: bold;
        }
        .ok { color: #00ff88; }
        .alert { color: #ff4444; }
        .warn { color: #ffaa00; }

        /* ── Progress bars ── */
        .resource-row {
            margin-bottom: 10px;
        }
        .resource-label {
            margin-bottom: 4px;
            font-size: 12px;
        }
        .bar-bg {
            background: #1a2a1a;
            border-radius: 3px;
            height: 10px;
            width: 100%;
        }
        .bar-fill {
            height: 10px;
            border-radius: 3px;
            background: #00ff88;
            transition: width 0.5s ease;
        }
        .bar-fill.warn { background: #ffaa00; }
        .bar-fill.danger { background: #ff4444; }

        /* ── Process table ── */
        .proc-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
            margin-top: 10px;
        }
        .proc-table th {
            color: #00ccff;
            text-align: left;
            padding: 2px 4px;
            border-bottom: 1px solid #1a2a1a;
        }
        .proc-table td {
            padding: 3px 4px;
            color: #00ff88;
        }
        .proc-table tr:nth-child(even) td { color: #aaffcc; }

        /* ── Network table ── */
        .net-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
            margin-top: 8px;
        }
        .net-table th {
            color: #00ccff;
            text-align: left;
            padding: 2px 4px;
            border-bottom: 1px solid #1a2a1a;
        }
        .net-table td {
            padding: 3px 4px;
        }
        .status-established { color: #00ff88; }
        .status-time_wait   { color: #ffaa00; }
        .status-other       { color: #aaa; }

        /* ── AI Anomaly ── */
        .stat-row {
            font-size: 12px;
            margin-bottom: 4px;
            color: #aaffcc;
        }
        .stat-section-label {
            color: #00ccff;
            font-size: 11px;
            margin-top: 8px;
            margin-bottom: 2px;
        }
        .anomaly-item {
            font-size: 12px;
            font-weight: bold;
        }
        .anomaly-item.alert::before { content: "— "; }

        /* ── Charts ── */
        .chart-title {
            color: #00ccff;
            font-size: 11px;
            text-align: center;
            margin-bottom: 4px;
        }
        canvas { width: 100% !important; }

        /* ── Security Report ── */
        .report-box {
            font-size: 11px;
            line-height: 1.7;
            color: #aaffcc;
        }
        .report-box .report-header {
            color: #00ccff;
            text-align: center;
            margin-bottom: 6px;
            font-size: 12px;
        }
        .report-box .report-section {
            color: #00ccff;
            margin-top: 6px;
        }
        .report-box .report-line {
            color: #aaffcc;
            padding-left: 4px;
        }
        .report-box .report-anomaly {
            color: #ff4444;
            font-weight: bold;
        }
        .report-footer {
            color: #888;
            font-size: 10px;
            margin-top: 8px;
        }

        /* ── Project Structure ── */
        .tree {
            font-size: 12px;
            line-height: 1.9;
            color: #aaffcc;
        }
        .tree .branch { color: #00ccff; }

        /* ── How-to ── */
        .howto-cmd {
            background: #111827;
            border: 1px solid #1a3a2a;
            border-radius: 4px;
            padding: 6px 8px;
            font-size: 11px;
            color: #00ff88;
            margin-bottom: 6px;
        }
        .howto-label {
            color: #888;
            font-size: 10px;
            margin-bottom: 2px;
        }

        /* ── About ── */
        .about-item {
            font-size: 12px;
            color: #aaffcc;
            padding: 3px 0;
            border-bottom: 1px solid #1a2a1a;
        }
        .about-item span { color: #00ccff; }
        .about-badge {
            display: inline-block;
            background: #00ff8820;
            border: 1px solid #00ff88;
            border-radius: 3px;
            padding: 1px 6px;
            font-size: 10px;
            color: #00ff88;
            margin-top: 6px;
        }
    </style>
</head>
<body>

<!-- ═══════════════ HEADER ═══════════════ -->
<div class="header">
    <div class="header-left">
        <h1>🔒 CYBER LAB – AI POWERED CYBERSECURITY MONITORING SYSTEM</h1>
        <div class="subtitle">
            Real-time Monitoring
            <span>•</span> Threat Detection
            <span>•</span> AI Anomaly Detection
            <span>•</span> Automated Reporting
        </div>
        <div class="last-updated">
            Last updated: {{ datetime_full }} &nbsp;|&nbsp; Auto-refreshes every 10 seconds
        </div>
    </div>
    <div class="header-right">
        System: Linux (Ubuntu 24.04)<br>
        User: {{ username }}<br>
        Time: {{ datetime_full }}<br>
        <span class="active"><span class="dot"></span>All Systems: ACTIVE</span>
    </div>
</div>

<!-- ═══════════════ 3-COLUMN GRID ═══════════════ -->
<div class="grid">

    <!-- ① LOGIN ATTACK DETECTION -->
    <div class="panel">
        <h3>1. LOGIN ATTACK DETECTION</h3>
        {% if login_attacks %}
            <div class="attack-label">Suspicious Login Attempts:</div>
            {% for line in login_attacks %}
                <div class="attack-line">{{ line }}</div>
            {% endfor %}
            <div class="total-failed">Total Failed Attempts: {{ login_attacks | length }}</div>
        {% else %}
            <p class="ok">✓ No suspicious login attempts detected.</p>
        {% endif %}
    </div>

    <!-- ② SYSTEM RESOURCE MONITOR -->
    <div class="panel">
        <h3>2. SYSTEM RESOURCE MONITOR</h3>

        <div class="resource-row">
            <div class="resource-label">CPU Usage: <strong>{{ cpu }}%</strong></div>
            <div class="bar-bg">
                <div class="bar-fill {% if cpu > 80 %}danger{% elif cpu > 50 %}warn{% endif %}"
                     style="width: {{ cpu }}%"></div>
            </div>
        </div>

        <div class="resource-row">
            <div class="resource-label">Memory Usage: <strong>{{ memory }}%</strong></div>
            <div class="bar-bg">
                <div class="bar-fill {% if memory > 80 %}danger{% elif memory > 50 %}warn{% endif %}"
                     style="width: {{ memory }}%"></div>
            </div>
        </div>

        <div class="resource-row">
            <div class="resource-label">Disk Usage: <strong>{{ disk }}%</strong></div>
            <div class="bar-bg">
                <div class="bar-fill {% if disk > 80 %}danger{% elif disk > 50 %}warn{% endif %}"
                     style="width: {{ disk }}%"></div>
            </div>
        </div>

        <table class="proc-table">
            <tr>
                <th>PID</th><th>Process</th><th>CPU%</th><th>Mem%</th>
            </tr>
            {% for p in top_processes %}
            <tr>
                <td>{{ p.pid }}</td>
                <td>{{ p.name }}</td>
                <td>{{ p.cpu }}</td>
                <td>{{ p.mem }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>

    <!-- ③ NETWORK CONNECTION MONITOR -->
    <div class="panel">
        <h3>3. NETWORK CONNECTION MONITOR</h3>
        <div style="margin-bottom:8px;">Active Connections: <strong>{{ connections }}</strong></div>
        <table class="net-table">
            <tr>
                <th>Local</th><th>Remote</th><th>Status</th>
            </tr>
            {% for c in net_connections %}
            <tr>
                <td>{{ c.local }}</td>
                <td>{{ c.remote }}</td>
                <td class="status-{{ c.status | lower }}">{{ c.status }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>

    <!-- ④ AI ANOMALY DETECTOR -->
    <div class="panel">
        <h3>4. AI ANOMALY DETECTOR</h3>
        <div class="stat-section-label">Current Stats:</div>
        <div class="stat-row">CPU: {{ cpu }}% &nbsp;|&nbsp; Memory: {{ memory }}% &nbsp;|&nbsp; Disk: {{ disk }}%</div>
        <div class="stat-section-label">Baseline Stats:</div>
        <div class="stat-row">CPU: {{ baseline.cpu }}% &nbsp;|&nbsp; Memory: {{ baseline.mem }}% &nbsp;|&nbsp; Disk: {{ baseline.disk }}%</div>

        {% if ml.is_anomaly or anomalies %}
        <br>
        <div class="attack-label">ANOMALIES DETECTED:</div>
        {% for a in anomalies %}
            <div class="anomaly-item alert">{{ a }}</div>
        {% endfor %}
        {% if ml.is_anomaly %}
            <div class="anomaly-item alert">ML MODEL: {{ ml.status }} (score: {{ "%.2f" | format(ml.score) }})</div>
        {% endif %}
        {% else %}
        <br>
        <div class="ok">✓ No anomalies detected. (ML score: {{ "%.2f" | format(ml.score) }})</div>
        {% endif %}
    </div>

    <!-- ⑤ SECURITY DASHBOARD – CPU Graph -->
    <div class="panel">
        <h3>5. SECURITY DASHBOARD (LIVE GRAPH)</h3>
        <div class="chart-title">Cyber Lab – System Security Dashboard</div>
        <div class="chart-title">CPU USAGE OVER TIME</div>
        <canvas id="cpuChart" height="100"></canvas>
        <div class="chart-title" style="margin-top:10px;">MEMORY USAGE OVER TIME</div>
        <canvas id="memChart" height="100"></canvas>
    </div>

    <!-- ⑥ AUTOMATED SECURITY REPORT -->
    <div class="panel">
        <h3>6. AUTOMATED SECURITY REPORT</h3>
        <div class="report-box">
            <div class="report-header">======= CYBER LAB SECURITY REPORT =======</div>
            <div>Date: {{ datetime_full }}</div>
            <br>
            <div class="report-section">1. Login Attack Summary</div>
            <div class="report-line">Failed Attempts: {{ login_attacks | length }}</div>

            <div class="report-section">2. System Resources</div>
            <div class="report-line">CPU: {{ cpu }}% &nbsp;|&nbsp; Memory: {{ memory }}% &nbsp;|&nbsp; Disk: {{ disk }}%</div>

            <div class="report-section">3. Network Summary</div>
            <div class="report-line">Active Connections: {{ connections }}</div>

            <div class="report-section">4. Anomalies</div>
            {% for a in anomalies %}
                <div class="report-line report-anomaly">&nbsp;&nbsp;— {{ a }}</div>
            {% else %}
                <div class="report-line ok">&nbsp;&nbsp;None detected.</div>
            {% endfor %}

            <div class="report-footer">
                Report auto-saved to logs/<br>
                Report saved to logs/security_report_{{ report_filename }}.txt
            </div>
        </div>
    </div>

    <!-- ⑦ PROJECT STRUCTURE -->

    <div class="panel">
        <h3>10. SYSTEM HEALTH</h3>
        <p class="conn" style="color:#00ccff">CPU TEMPERATURES:</p>
        {% for core, temp in cpu_temps.items() %}
        <div class="metric">{{ core }}: {{ temp }}°C
            <div class="bar-bg"><div class="bar {% if temp > 80 %}danger{% elif temp > 60 %}warn{% endif %}" style="width:{{ [temp, 100]|min }}%"></div></div>
        </div>
        {% endfor %}
        <br>
        <p class="conn" style="color:#00ccff">DISK I/O:</p>
        <p class="conn">Read: {{ disk_read }} MB/s</p>
        <p class="conn">Write: {{ disk_write }} MB/s</p>
        <br>
        <p class="conn" style="color:#00ccff">ATTACK ORIGIN MAP:</p>
        {% if attack_map %}
            {% for country, count in attack_map.items() %}
            <p class="conn">{{ country }}: <span class="alert">{{ count }} attacks</span></p>
            {% endfor %}
        {% else %}
            <p class="ok">✅ No attacks detected</p>
        {% endif %}
    </div>

    <div class="panel">
        <h3>7. PROJECT STRUCTURE</h3>
        <div class="tree">
            <span class="branch">cyber-lab/</span><br>
            ├── <span class="branch">scripts/</span><br>
            │&nbsp;&nbsp;&nbsp;├── dashboard.py<br>
            │&nbsp;&nbsp;&nbsp;├── ml_trainer.py<br>
            │&nbsp;&nbsp;&nbsp;└── monitor.py<br>
            ├── <span class="branch">logs/</span><br>
            │&nbsp;&nbsp;&nbsp;└── security_report_*.txt<br>
            ├── <span class="branch">data/</span><br>
            │&nbsp;&nbsp;&nbsp;└── ml_model.pkl<br>
            └── <span class="branch">static/</span><br>
            &nbsp;&nbsp;&nbsp;&nbsp;└── chart.js
        </div>
    </div>

    <!-- ⑧ HOW TO RUN -->
    <div class="panel">
        <h3>8. HOW TO RUN</h3>
        <div class="howto-label">1. Collect training data (run for ~5 min):</div>
        <div class="howto-cmd">python3 scripts/ml_trainer.py --collect</div>

        <div class="howto-label">2. Train the ML model:</div>
        <div class="howto-cmd">python3 scripts/ml_trainer.py --train</div>

        <div class="howto-label">3. Launch the dashboard:</div>
        <div class="howto-cmd">python3 scripts/dashboard.py</div>

        <div class="howto-label">4. Open in browser:</div>
        <div class="howto-cmd">http://localhost:5000</div>
    </div>

    <!-- ⑨ ABOUT -->
    <div class="panel">
        <h3>9. ABOUT</h3>
        <div class="about-item"><span>Project:</span> Cyber Lab</div>
        <div class="about-item"><span>Purpose:</span> AI Cybersecurity Monitoring</div>
        <div class="about-item"><span>ML Model:</span> Isolation Forest (Anomaly Detection)</div>
        <div class="about-item"><span>Stack:</span> Python · Flask · psutil · scikit-learn</div>
        <div class="about-item"><span>Charts:</span> Chart.js</div>
        <div class="about-item"><span>Refresh:</span> Every 10 seconds</div>
        <div class="about-item"><span>Log Dir:</span> ~/Desktop/cyber-lab/logs/</div>
        <br>
        <span class="about-badge">● SYSTEM ACTIVE</span>
        <span class="about-badge" style="margin-left:6px;">🔒 SECURE</span>
    </div>

</div>

<!-- ═══════════════ CHART SCRIPTS ═══════════════ -->
<script>
const cpuData  = {{ cpu_history  | tojson }};
const memData  = {{ mem_history  | tojson }};
const labels   = {{ time_labels  | tojson }};

const chartDefaults = {
    type: 'line',
    options: {
        responsive: true,
        animation: false,
        plugins: { legend: { display: false } },
        scales: {
            x: { ticks: { color: '#666', font: { size: 9 } }, grid: { color: '#1a2a1a' } },
            y: {
                min: 0, max: 100,
                ticks: { color: '#666', font: { size: 9 },
                         callback: v => v + '%' },
                grid: { color: '#1a2a1a' }
            }
        }
    }
};

new Chart(document.getElementById('cpuChart'), {
    ...chartDefaults,
    data: {
        labels,
        datasets: [{
            data: cpuData,
            borderColor: '#ff4444',
            backgroundColor: '#ff444422',
            borderWidth: 1.5,
            pointRadius: 3,
            pointBackgroundColor: '#ff4444',
            fill: false,
            tension: 0.1
        }]
    }
});

new Chart(document.getElementById('memChart'), {
    ...chartDefaults,
    data: {
        labels,
        datasets: [{
            data: memData,
            borderColor: '#4488ff',
            backgroundColor: '#4488ff22',
            borderWidth: 1.5,
            pointRadius: 3,
            pointBackgroundColor: '#4488ff',
            fill: false,
            tension: 0.1
        }]
    }
});
</script>
</body>
</html>
"""

def get_top_processes(n=5):
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            procs.append({
                'pid':  p.info['pid'],
                'name': p.info['name'][:18],
                'cpu':  round(p.info['cpu_percent'], 1),
                'mem':  round(p.info['memory_percent'], 1)
            })
        except:
            pass
    procs.sort(key=lambda x: x['cpu'], reverse=True)
    return procs[:n]

def get_net_connections(n=6):
    rows = []
    try:
        for c in psutil.net_connections(kind='inet'):
            if c.raddr:
                local  = f"{c.laddr.port}" if c.laddr else "-"
                remote = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "-"
                status = c.status if c.status else "?"
                rows.append({'local': local, 'remote': remote, 'status': status})
                if len(rows) >= n:
                    break
    except:
        pass
    return rows

def get_baseline():
    # Simple rolling average of the last 10 readings; fallback to fixed defaults
    if len(cpu_history) >= 2:
        return {
            'cpu':  round(sum(cpu_history[:-1]) / len(cpu_history[:-1]), 1),
            'mem':  round(sum(mem_history[:-1]) / len(mem_history[:-1]), 1),
            'disk': 0.0
        }
    return {'cpu': 0.1, 'mem': 29.7, 'disk': 17.3}

def detect_anomalies(connections, baseline_connections=8):
    issues = []
    if connections > baseline_connections * 2:
        issues.append(f"UNUSUAL CONNECTIONS: {connections} (baseline: {baseline_connections})")
    return issues

def save_report(now_str, cpu, memory, disk, connections, login_attacks, anomalies):
    os.makedirs(LOG_DIR, exist_ok=True)
    filename = f"security_report_{now_str.replace(' ', '_').replace(':', '')}.txt"
    path = os.path.join(LOG_DIR, filename)
    lines = [
        "======= CYBER LAB SECURITY REPORT =======",
        f"Date: {now_str}",
        "",
        "1. Login Attack Summary",
        f"   Failed Attempts: {len(login_attacks)}",
        "",
        "2. System Resources",
        f"   CPU: {cpu}%  |  Memory: {memory}%  |  Disk: {disk}%",
        "",
        "3. Network Summary",
        f"   Active Connections: {connections}",
        "",
        "4. Anomalies",
    ]
    for a in anomalies:
        lines.append(f"   — {a}")
    if not anomalies:
        lines.append("   None detected.")
    with open(path, 'w') as f:
        f.write("\n".join(lines))
    return now_str.replace(' ', '_').replace(':', '').replace('-', '')

@app.route('/')
def dashboard():
    cpu    = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk   = psutil.disk_usage('/').percent

    now          = datetime.datetime.now()
    now_str      = now.strftime("%Y-%m-%d %H:%M:%S")
    report_ts    = now.strftime("%Y%m%d_%H%M%S")

    cpu_history.append(round(cpu, 1))
    mem_history.append(round(memory, 1))
    time_history.append(now.strftime("%H:%M:%S"))

    if len(cpu_history) > 20:
        cpu_history.pop(0)
        mem_history.pop(0)
        time_history.pop(0)

    connections = len(psutil.net_connections(kind='inet'))
    ml          = ml_detect(cpu, memory, disk, connections)
    baseline    = get_baseline()
    anomalies   = detect_anomalies(connections)

    # Login attacks from auth.log
    try:
        result = subprocess.run(
            ['sudo', 'grep', 'Failed password', '/var/log/auth.log'],
            capture_output=True, text=True, timeout=3
        )
        login_attacks = [l.strip() for l in result.stdout.split("\n") if l.strip()][:5]
    except:
        login_attacks = []

    # CPU temperatures
    cpu_temps = {}
    try:
        temps = psutil.sensors_temperatures()
        if "coretemp" in temps:
            for t in temps["coretemp"]:
                if "Core" in t.label:
                    cpu_temps[t.label] = round(t.current, 1)
    except:
        cpu_temps = {"Core 0": 0}
    # Disk I/O
    try:
        disk_io = psutil.disk_io_counters()
        disk_read = round(disk_io.read_bytes / 1024 / 1024 / 1024, 2)
        disk_write = round(disk_io.write_bytes / 1024 / 1024 / 1024, 2)
    except:
        disk_read = disk_write = 0
    # Attack map
    try:
        from geo_attack import get_attack_map
        attack_map = get_attack_map()
    except:
        attack_map = {}

    report_filename = save_report(now_str, cpu, memory, disk, connections, login_attacks, anomalies)

    return render_template_string(
        HTML,
        cpu           = round(cpu, 1),
        memory        = round(memory, 1),
        disk          = round(disk, 1),
        connections   = connections,
        ml            = ml,
        datetime_full = now_str,
        username      = os.environ.get('USER', 'sam'),
        login_attacks = login_attacks,
        top_processes = get_top_processes(),
        net_connections = get_net_connections(),
        baseline      = baseline,
        anomalies     = anomalies,
        cpu_history   = cpu_history,
        cpu_temps      = cpu_temps,
        disk_read      = disk_read,
        disk_write     = disk_write,
        attack_map     = attack_map,
        mem_history   = mem_history,
        time_labels   = time_history,
        report_filename = report_ts,
    )

if __name__ == '__main__':
    print("Dashboard running at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
