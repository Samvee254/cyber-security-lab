from flask import Flask, render_template_string
import psutil
import datetime

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Cyber Lab Dashboard</title>
    <meta http-equiv="refresh" content="10">
    <style>
        body { font-family: Arial; background: #1a1a2e; color: #eee; padding: 20px; }
        h1 { color: #00ff88; text-align: center; }
        .card { background: #16213e; border-radius: 10px; padding: 20px; margin: 10px; display: inline-block; width: 200px; text-align: center; }
        .value { font-size: 40px; font-weight: bold; color: #00ff88; }
        .label { color: #aaa; margin-top: 5px; }
        .cards { text-align: center; }
        .time { text-align: center; color: #aaa; margin-bottom: 20px; }
    </style>
</head>
<body>
    <h1>🔐 Cyber Lab Security Dashboard</h1>
    <p class="time">Last updated: {{ time }} | Auto-refreshes every 10 seconds</p>
    <div class="cards">
        <div class="card">
            <div class="value">{{ cpu }}%</div>
            <div class="label">CPU Usage</div>
        </div>
        <div class="card">
            <div class="value">{{ memory }}%</div>
            <div class="label">Memory Used</div>
        </div>
        <div class="card">
            <div class="value">{{ disk }}%</div>
            <div class="label">Disk Used</div>
        </div>
        <div class="card">
            <div class="value">{{ connections }}</div>
            <div class="label">Active Connections</div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(HTML,
        cpu=psutil.cpu_percent(interval=1),
        memory=psutil.virtual_memory().percent,
        disk=psutil.disk_usage('/').percent,
        connections=len(psutil.net_connections()),
        time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

if __name__ == '__main__':
    print("Dashboard running at http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000)
