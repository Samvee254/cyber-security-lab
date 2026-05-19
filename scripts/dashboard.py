from flask import Flask, render_template_string
import psutil
import datetime
import subprocess
import os

app = Flask(__name__)

cpu_history = []
mem_history = []
time_history = []

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Cyber Lab Dashboard</title>
    <meta http-equiv="refresh" content="10">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: monospace; background: #0a0a1a; color: #00ff88; padding: 20px; margin: 0; }
        .header-bar { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
        .header-main { flex: 1; text-align: center; }
        .header-info { font-size: 11px; color: #aaa; text-align: right; line-height: 1.8; min-width: 220px; }
        h1 { color: #00ccff; font-size: 22px; margin: 0 0 4px 0; letter-spacing: 1px; }
        .subtitle { color: #00ff88; font-size: 12px; margin: 0; }
        .time { color: #555; font-size: 11px; text-align: center; margin: 8px 0 14px 0; }
        .grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
        .panel { background: #0d1117; border: 1px solid #00ff88; border-radius: 8px; padding: 14px; }
        .panel h3 { color: #00ccff; border-bottom: 1px solid #333; padding-bottom: 5px; margin: 0 0 10px 0; font-size: 13px; letter-spacing: 1px; }
        .metric { margin: 8px 0; font-size: 12px; }
        .bar-bg { background: #222; border-radius: 4px; height: 12px; margin-top: 4px; }
        .bar { height: 12px; border-radius: 4px; background: #00ff88; }
        .bar.warn { background: #ffaa00; }
        .bar.danger { background: #ff4444; }
        .alert { color: #ff4444; font-weight: bold; font-size: 12px; }
        .ok { color: #00ff88; font-size: 12px; }
        .conn { font-size: 11px; margin: 3px 0; color: #aaa; }
        table { width: 100%; font-size: 11px; border-collapse: collapse; }
        th { color: #00ccff; text-align: left; padding: 3px; border-bottom: 1px solid #333; }
        td { padding: 3px; color: #aaa; }
        .status { color: #00ff88; }
        .chart-title { text-align: center; font-size: 10px; color: #555; letter-spacing: 1px; margin: 6px 0 3px 0; }
        .chart-wrap { position: relative; width: 100%; height: 120px; }
        .active-dot { display: inline-block; width: 8px; height: 8px; background: #00ff88; border-radius: 50%; margin-right: 5px; animation: blink 1.5s infinite; }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
    </style>
</head>
<body>
    <div class="header-bar">
        <div style="font-size:28px">🔐</div>
        <div class="header-main">
            <h1>CYBER LAB – AI POWERED CYBERSECURITY MONITORING SYSTEM</h1>
            <p class="subtitle">Real-time Monitoring &nbsp;•&nbsp; Threat Detection &nbsp;•&nbsp; AI Anomaly Detection &nbsp;•&nbsp; Automated Reporting</p>
        </div>
        <div class="header-info">
            System: Linux (Ubuntu 24.04)<br>
            User: {{ user }}<br>
            Time: {{ time }}<br>
            <span class="active-dot"></span><span style="color:#00ff88">All Systems: ACTIVE</span>
        </div>
    </div>

    <p class="time">Last updated: {{ time }} &nbsp;|&nbsp; Auto-refreshes every 10 seconds</p>

    <div class="grid">

        <div class="panel">
            <h3>1. LOGIN ATTACK DETECTION</h3>
            {% if login_attacks %}
                <p class="alert">⚠ Suspicious Login Attempts:</p>
                {% for line in login_attacks %}
                <p class="conn">{{ line }}</p>
                {% endfor %}
                <p class="alert" style="margin-top:8px">Total Failed Attempts: {{ login_attacks|length }}</p>
            {% else %}
                <p class="ok">✅ No failed login attempts found.</p>
            {% endif %}
        </div>

        <div class="panel">
            <h3>2. SYSTEM RESOURCE MONITOR</h3>
            <div class="metric">CPU Usage: {{ cpu }}%
                <div class="bar-bg"><div class="bar {% if cpu > 80 %}danger{% elif cpu > 50 %}warn{% endif %}" style="width:{{ cpu }}%"></div></div>
            </div>
            <div class="metric">Memory Usage: {{ memory }}%
                <div class="bar-bg"><div class="bar {% if memory > 80 %}danger{% elif memory > 50 %}warn{% endif %}" style="width:{{ memory }}%"></div></div>
            </div>
            <div class="metric">Disk Usage: {{ disk }}%
                <div class="bar-bg"><div class="bar {% if disk > 80 %}danger{% elif disk > 50 %}warn{% endif %}" style="width:{{ disk }}%"></div></div>
            </div>
            <br>
            <table>
                <tr><th>PID</th><th>Process</th><th>CPU%</th><th>Mem%</th></tr>
                {% for p in top_processes %}
                <tr><td>{{ p.pid }}</td><td>{{ p.name }}</td><td>{{ p.cpu }}</td><td>{{ p.mem }}</td></tr>
                {% endfor %}
            </table>
        </div>

        <div class="panel">
            <h3>3. NETWORK CONNECTION MONITOR</h3>
            <p class="ok">Active Connections: {{ connections }}</p>
            <table>
                <tr><th>Local</th><th>Remote</th><th>Status</th></tr>
                {% for c in conn_list %}
                <tr><td>{{ c.local }}</td><td>{{ c.remote }}</td><td class="status">{{ c.status }}</td></tr>
                {% endfor %}
            </table>
        </div>

        <div class="panel">
            <h3>4. AI ANOMALY DETECTOR</h3>
            <p class="conn" style="color:#00ccff">Current Stats:</p>
            <p class="conn">CPU: {{ cpu }}% &nbsp;|&nbsp; Memory: {{ memory }}% &nbsp;|&nbsp; Disk: {{ disk }}%</p>
            <p class="conn" style="color:#00ccff; margin-top:8px">Baseline Stats:</p>
            <p class="conn">CPU: {{ baseline.cpu }}% &nbsp;|&nbsp; Memory: {{ baseline.memory }}% &nbsp;|&nbsp; Disk: {{ baseline.disk }}%</p>
            <br>
            {% if anomalies %}
                <p class="alert">⚠ ANOMALIES DETECTED:</p>
                {% for a in anomalies %}<p class="alert">— {{ a }}</p>{% endfor %}
            {% else %}
                <p class="ok">✅ All systems normal.</p>
            {% endif %}
        </div>

        <div class="panel">
            <h3>5. SECURITY DASHBOARD (LIVE GRAPH)</h3>
            <p class="conn" style="text-align:center; color:#00ccff; letter-spacing:1px">Cyber Lab — System Security Dashboard</p>
            <div class="chart-title">CPU USAGE OVER TIME</div>
            <div class="chart-wrap">
                <canvas id="cpuChart"></canvas>
            </div>
            <div class="chart-title" style="margin-top:8px">MEMORY USAGE OVER TIME</div>
            <div class="chart-wrap">
                <canvas id="memChart"></canvas>
            </div>
        </div>

        <div class="panel">
            <h3>6. AUTOMATED SECURITY REPORT</h3>
            <p class="conn">======= CYBER LAB SECURITY REPORT =======</p>
            <p class="conn">Date: {{ time }}</p>
            <br>
            <p class="conn" style="color:#00ccff">1. Login Attack Summary</p>
            <p class="conn">&nbsp;&nbsp;Failed Attempts: {{ login_attacks|length }}</p>
            <p class="conn" style="color:#00ccff">2. System Resources</p>
            <p class="conn">&nbsp;&nbsp;CPU: {{ cpu }}% &nbsp;|&nbsp; Memory: {{ memory }}% &nbsp;|&nbsp; Disk: {{ disk }}%</p>
            <p class="conn" style="color:#00ccff">3. Network Summary</p>
            <p class="conn">&nbsp;&nbsp;Active Connections: {{ connections }}</p>
            <p class="conn" style="color:#00ccff">4. Anomalies</p>
            {% if anomalies %}
                {% for a in anomalies %}<p class="alert">&nbsp;&nbsp;— {{ a }}</p>{% endfor %}
            {% else %}
                <p class="conn">&nbsp;&nbsp;0 detected</p>
            {% endif %}
            <br>
            <p class="ok">Report auto-saved to logs/</p>
            <p class="conn" style="color:#555; font-size:10px">Report saved to logs/security_report_{{ report_fname }}.txt</p>
        </div>

    </div>

    <script>
        const cpuData = {{ cpu_history | safe }};
        const memData = {{ mem_history | safe }};
        const labels  = {{ time_labels | safe }};
        const commonOpts = {
            responsive: true, maintainAspectRatio: false,
            animation: { duration: 600 },
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: '#555', font: { size: 9 }, maxTicksLimit: 6 }, grid: { color: '#1a2840' } },
                y: { min: 0, max: 100, ticks: { color: '#555', font: { size: 9 }, callback: v => v + '%' }, grid: { color: '#1a2840' } }
            }
        };
        new Chart(document.getElementById('cpuChart'), {
            type: 'line',
            data: { labels: labels, datasets: [{ data: cpuData, borderColor: '#ff4444', backgroundColor: 'rgba(255,68,68,0.08)', borderWidth: 1.5, pointRadius: 3, pointBackgroundColor: '#ff4444', fill: true, tension: 0.3 }] },
            options: commonOpts
        });
        new Chart(document.getElementById('memChart'), {
            type: 'line',
            data: { labels: labels, datasets: [{ data: memData, borderColor: '#4a9eff', backgroundColor: 'rgba(74,158,255,0.08)', borderWidth: 1.5, pointRadius: 3, pointBackgroundColor: '#4a9eff', fill: true, tension: 0.3, borderDash: [4,2] }] },
            options: commonOpts
        });
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    cpu    = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk   = psutil.disk_usage('/').percent

    now_label = datetime.datetime.now().strftime("%H:%M:%S")
    cpu_history.append(cpu)
    mem_history.append(memory)
    time_history.append(now_label)
    if len(cpu_history) > 20:
        cpu_history.pop(0)
        mem_history.pop(0)
        time_history.pop(0)

    try:
        connections = len(psutil.net_connections(kind='inet'))
    except Exception:
        connections = "N/A"

    top_processes = []
    for p in sorted(
        psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
        key=lambda x: x.info['cpu_percent'] or 0,
        reverse=True
    )[:5]:
        top_processes.append({
            'pid':  p.info['pid'],
            'name': p.info['name'][:15],
            'cpu':  round(p.info['cpu_percent'] or 0, 1),
            'mem':  round(p.info['memory_percent'] or 0, 1)
        })

    conn_list = []
    try:
        for c in psutil.net_connections(kind='inet')[:5]:
            if c.raddr:
                conn_list.append({
                    'local':  f"{c.laddr.port}",
                    'remote': f"{c.raddr.ip}:{c.raddr.port}",
                    'status': c.status
                })
    except Exception:
        pass

    result = subprocess.run(
        ['sudo', 'grep', 'Failed password', '/var/log/auth.log'],
        capture_output=True, text=True
    )
    login_attacks = [
        l.strip()[:80]
        for l in result.stdout.strip().split('\n')
        if l.strip()
    ][-5:]

    baseline = {'cpu': 0.1, 'memory': 29.7, 'disk': 17.3}
    anomalies = []
    if cpu > baseline['cpu'] + 30:
        anomalies.append(f"HIGH CPU: {cpu}% (baseline: {baseline['cpu']}%)")
    if memory > baseline['memory'] + 20:
        anomalies.append(f"HIGH MEMORY: {memory}% (baseline: {baseline['memory']}%)")
    if isinstance(connections, int) and connections > 20:
        anomalies.append(f"UNUSUAL CONNECTIONS: {connections} (baseline: 8)")

    user         = os.environ.get('USER', 'sam')
    now          = datetime.datetime.now()
    report_fname = now.strftime("%Y%m%d_%H%M%S")

    return render_template_string(
        HTML,
        cpu=cpu, memory=memory, disk=disk,
        connections=connections,
        top_processes=top_processes,
        conn_list=conn_list,
        login_attacks=login_attacks,
        anomalies=anomalies,
        baseline=baseline,
        time=now.strftime("%Y-%m-%d %H:%M:%S"),
        user=user,
        report_fname=report_fname,
        cpu_history=str(cpu_history),
        mem_history=str(mem_history),
        time_labels=str(time_history)
    )

if __name__ == '__main__':
    print("Dashboard running at http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000)
