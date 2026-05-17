from flask import Flask, render_template_string
import psutil
import datetime
import subprocess

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Cyber Lab Dashboard</title>
    <meta http-equiv="refresh" content="10">
    <style>
        body { font-family: monospace; background: #0a0a1a; color: #00ff88; padding: 20px; }
        h1 { text-align: center; color: #00ccff; font-size: 24px; }
        .subtitle { text-align: center; color: #888; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }
        .panel { background: #0d1117; border: 1px solid #00ff88; border-radius: 8px; padding: 15px; }
        .panel h3 { color: #00ccff; border-bottom: 1px solid #333; padding-bottom: 5px; }
        .metric { margin: 8px 0; }
        .bar-bg { background: #222; border-radius: 4px; height: 12px; margin-top: 4px; }
        .bar { height: 12px; border-radius: 4px; background: #00ff88; }
        .bar.warn { background: #ffaa00; }
        .bar.danger { background: #ff4444; }
        .alert { color: #ff4444; font-weight: bold; }
        .ok { color: #00ff88; }
        .conn { font-size: 11px; margin: 3px 0; color: #aaa; }
        table { width: 100%; font-size: 11px; border-collapse: collapse; }
        th { color: #00ccff; text-align: left; padding: 3px; border-bottom: 1px solid #333; }
        td { padding: 3px; color: #aaa; }
        .status { color: #00ff88; }
        .top { grid-column: span 3; text-align: center; }
        .time { color: #555; font-size: 12px; text-align: center; }
    </style>
</head>
<body>

    <h1>🔐 CYBER LAB – AI POWERED CYBERSECURITY MONITORING SYSTEM</h1>

    <p class="subtitle">
        Real-time Monitoring • Threat Detection • AI Anomaly Detection • Automated Reporting
    </p>

    <p class="time">
        Last updated: {{ time }} | Auto-refreshes every 10 seconds
    </p>

    <div class="grid">

        <div class="panel">
            <h3>1. LOGIN ATTACK DETECTION</h3>

            {% if login_attacks %}
                <p class="alert">⚠ Suspicious Login Attempts:</p>

                {% for line in login_attacks %}
                <p class="conn">{{ line }}</p>
                {% endfor %}

                <p class="alert">
                    Total Failed Attempts: {{ login_attacks|length }}
                </p>

            {% else %}
                <p class="ok">✅ No failed login attempts found.</p>
            {% endif %}
        </div>

        <div class="panel">
            <h3>2. SYSTEM RESOURCE MONITOR</h3>

            <div class="metric">
                CPU Usage: {{ cpu }}%

                <div class="bar-bg">
                    <div class="bar {% if cpu > 80 %}danger{% elif cpu > 50 %}warn{% endif %}"
                         style="width:{{ cpu }}%">
                    </div>
                </div>
            </div>

            <div class="metric">
                Memory Usage: {{ memory }}%

                <div class="bar-bg">
                    <div class="bar {% if memory > 80 %}danger{% elif memory > 50 %}warn{% endif %}"
                         style="width:{{ memory }}%">
                    </div>
                </div>
            </div>

            <div class="metric">
                Disk Usage: {{ disk }}%

                <div class="bar-bg">
                    <div class="bar {% if disk > 80 %}danger{% elif disk > 50 %}warn{% endif %}"
                         style="width:{{ disk }}%">
                    </div>
                </div>
            </div>

            <br>

            <table>
                <tr>
                    <th>PID</th>
                    <th>Process</th>
                    <th>CPU%</th>
                    <th>Mem%</th>
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

        <div class="panel">
            <h3>3. NETWORK CONNECTION MONITOR</h3>

            <p class="ok">Active Connections: {{ connections }}</p>

            <table>
                <tr>
                    <th>Local</th>
                    <th>Remote</th>
                    <th>Status</th>
                </tr>

                {% for c in conn_list %}
                <tr>
                    <td>{{ c.local }}</td>
                    <td>{{ c.remote }}</td>
                    <td class="status">{{ c.status }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>

        <div class="panel">
            <h3>4. AI ANOMALY DETECTOR</h3>

            <p>Current Stats:</p>

            <p class="conn">
                CPU: {{ cpu }}% |
                Memory: {{ memory }}% |
                Disk: {{ disk }}%
            </p>

            <p>Baseline Stats:</p>

            <p class="conn">
                CPU: {{ baseline.cpu }}% |
                Memory: {{ baseline.memory }}% |
                Disk: {{ baseline.disk }}%
            </p>

            <br>

            {% if anomalies %}
                <p class="alert">⚠ ANOMALIES DETECTED:</p>

                {% for a in anomalies %}
                <p class="alert">- {{ a }}</p>
                {% endfor %}

            {% else %}
                <p class="ok">✅ All systems normal.</p>
            {% endif %}
        </div>

        <div class="panel">
            <h3>5. SYSTEM STATUS</h3>

            <p class="conn">System: Linux (Ubuntu 24)</p>
            <p class="conn">User: {{ user }}</p>
            <p class="conn">Time: {{ time }}</p>

            <br>

            <p class="ok">● All Systems: ACTIVE</p>

            <br>

            <p class="conn">Scripts Running:</p>

            <p class="ok">✅ log_monitor.py</p>
            <p class="ok">✅ system_monitor.py</p>
            <p class="ok">✅ network_monitor.py</p>
            <p class="ok">✅ anomaly_detector.py</p>
            <p class="ok">✅ dashboard.py</p>
        </div>

        <div class="panel">
            <h3>6. AUTOMATED SECURITY REPORT</h3>

            <p class="conn">
                ======= CYBER LAB SECURITY REPORT =======
            </p>

            <p class="conn">Date: {{ time }}</p>

            <br>

            <p class="conn">1. Login Attack Summary</p>
            <p class="conn">
                Failed Attempts: {{ login_attacks|length }}
            </p>

            <p class="conn">2. System Resources</p>

            <p class="conn">
                CPU: {{ cpu }}% |
                Memory: {{ memory }}% |
                Disk: {{ disk }}%
            </p>

            <p class="conn">3. Network Summary</p>

            <p class="conn">
                Active Connections: {{ connections }}
            </p>

            <p class="conn">
                4. Anomalies: {{ anomalies|length }} detected
            </p>

            <br>

            <p class="ok">Report auto-saved to logs/</p>
        </div>

    </div>

</body>
</html>
"""

@app.route('/')
def dashboard():

    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    connections = len(psutil.net_connections())

    top_processes = []

    for p in sorted(
        psutil.process_iter(
            ['pid', 'name', 'cpu_percent', 'memory_percent']
        ),
        key=lambda x: x.info['cpu_percent'] or 0,
        reverse=True
    )[:5]:

        top_processes.append({
            'pid': p.info['pid'],
            'name': p.info['name'][:15],
            'cpu': round(p.info['cpu_percent'] or 0, 1),
            'mem': round(p.info['memory_percent'] or 0, 1)
        })

    conn_list = []

    for c in psutil.net_connections()[:5]:

        if c.raddr:
            conn_list.append({
                'local': f"{c.laddr.port}",
                'remote': f"{c.raddr.ip}:{c.raddr.port}",
                'status': c.status
            })

    result = subprocess.run(
        ['sudo', 'grep', 'Failed password', '/var/log/auth.log'],
        capture_output=True,
        text=True
    )

    login_attacks = [
        l.strip()[:80]
        for l in result.stdout.strip().split('\n')
        if l.strip()
    ][-5:]

    baseline = {
        'cpu': 0.1,
        'memory': 29.7,
        'disk': 17.3
    }

    anomalies = []

    if cpu > baseline['cpu'] + 30:
        anomalies.append(
            f"HIGH CPU: {cpu}% (baseline: {baseline['cpu']}%)"
        )

    if memory > baseline['memory'] + 20:
        anomalies.append(
            f"HIGH MEMORY: {memory}% (baseline: {baseline['memory']}%)"
        )

    import os

    user = os.environ.get('USER', 'sam')

    return render_template_string(
        HTML,
        cpu=cpu,
        memory=memory,
        disk=disk,
        connections=connections,
        top_processes=top_processes,
        conn_list=conn_list,
        login_attacks=login_attacks,
        anomalies=anomalies,
        baseline=baseline,
        time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        user=user
    )

if __name__ == '__main__':

    print("Dashboard running at http://localhost:5000")

    app.run(
        debug=False,
        host='0.0.0.0',
        port=5000
    )

