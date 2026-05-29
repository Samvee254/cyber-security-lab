from flask import Flask, render_template_string
import json
import os
from collections import Counter

app = Flask(__name__)
LOG_FILE = "/home/sam/Desktop/cyber-lab/logs/honeypot_attacks.json"

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Honeypot Dashboard</title>
    <meta http-equiv="refresh" content="10">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Courier New', monospace; background: #0a0a1a; color: #00ff88; padding: 15px; }
        h1 { color: #00ccff; text-align: center; letter-spacing: 3px; padding: 15px; font-size: 20px; }
        .subtitle { text-align: center; color: #555; font-size: 11px; margin-bottom: 15px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-bottom: 12px; }
        .panel { border: 1px solid #00ff88; padding: 12px; background: #0d1117; border-radius: 4px; }
        .panel h3 { color: #00ccff; font-size: 11px; letter-spacing: 2px; border-bottom: 1px solid #1a3a2a; padding-bottom: 6px; margin-bottom: 10px; }
        .stat-number { font-size: 36px; color: #00ff88; text-align: center; padding: 10px; }
        .stat-label { text-align: center; color: #555; font-size: 10px; }
        .alert { color: #ff4444; }
        table { width: 100%; border-collapse: collapse; font-size: 10px; }
        th { color: #00ccff; text-align: left; padding: 4px; border-bottom: 1px solid #1a3a2a; }
        td { padding: 4px; color: #00ff88; border-bottom: 1px solid #0a0a1a; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 10px; }
        .badge-red { background: #3a0000; color: #ff4444; border: 1px solid #ff4444; }
        .badge-green { background: #003a1a; color: #00ff88; border: 1px solid #00ff88; }
        .full-panel { border: 1px solid #00ff88; padding: 12px; background: #0d1117; border-radius: 4px; margin-bottom: 12px; }
        .top-item { display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #1a3a2a; font-size: 11px; }
        .bar { background: #1a3a2a; border-radius: 2px; height: 6px; margin-top: 3px; }
        .bar-fill { background: #00ff88; height: 100%; border-radius: 2px; }
        .bar-fill-red { background: #ff4444; height: 100%; border-radius: 2px; }
    </style>
</head>
<body>
<div style="display:flex;gap:10px;margin-bottom:12px;border:1px solid #00ff88;padding:10px;background:#0d1117;border-radius:4px;">
    <a href="http://localhost:5000" style="color:#00ccff;text-decoration:none;font-family:monospace;font-size:12px;padding:6px 14px;border:1px solid #00ccff;border-radius:3px;">🖥 System Monitor</a>
    <a href="http://localhost:5001" style="color:#00ff88;text-decoration:none;font-family:monospace;font-size:12px;padding:6px 14px;border:1px solid #00ff88;border-radius:3px;">🍯 Honeypot Dashboard</a>
</div>
<h1>🍯 HONEYPOT ATTACK DASHBOARD</h1>
<p class="subtitle">Last updated: {{ now }} | Auto-refreshes every 10 seconds</p>

<!-- STATS ROW -->
<div class="grid">
    <div class="panel">
        <h3>TOTAL ATTACKS</h3>
        <div class="stat-number alert">{{ total }}</div>
        <div class="stat-label">login attempts captured</div>
    </div>
    <div class="panel">
        <h3>UNIQUE IPs</h3>
        <div class="stat-number">{{ unique_ips }}</div>
        <div class="stat-label">distinct attackers</div>
    </div>
    <div class="panel">
        <h3>COUNTRIES</h3>
        <div class="stat-number">{{ unique_countries }}</div>
        <div class="stat-label">attack origins</div>
    </div>
</div>

<!-- TOP USERNAMES + PASSWORDS + COUNTRIES -->
<div class="grid">
    <div class="panel">
        <h3>TOP USERNAMES TRIED</h3>
        {% for username, count in top_usernames %}
        <div class="top-item">
            <span>{{ username }}</span>
            <span class="alert">{{ count }}x</span>
        </div>
        <div class="bar"><div class="bar-fill-red" style="width:{{ (count / total * 100)|int }}%"></div></div>
        {% endfor %}
    </div>
    <div class="panel">
        <h3>TOP PASSWORDS TRIED</h3>
        {% for password, count in top_passwords %}
        <div class="top-item">
            <span>{{ password }}</span>
            <span class="alert">{{ count }}x</span>
        </div>
        <div class="bar"><div class="bar-fill-red" style="width:{{ (count / total * 100)|int }}%"></div></div>
        {% endfor %}
    </div>
    <div class="panel">
        <h3>ATTACK ORIGINS</h3>
        {% for country, count in top_countries %}
        <div class="top-item">
            <span>{{ country }}</span>
            <span class="alert">{{ count }}x</span>
        </div>
        <div class="bar"><div class="bar-fill" style="width:{{ (count / total * 100)|int }}%"></div></div>
        {% endfor %}
    </div>
</div>

<!-- LIVE ATTACK FEED -->
<div class="full-panel">
    <h3>LIVE ATTACK FEED (latest 20)</h3>
    <table>
        <tr>
            <th>Timestamp</th>
            <th>IP Address</th>
            <th>Country</th>
            <th>Username</th>
            <th>Password</th>
            <th>Status</th>
        </tr>
        {% for attack in attacks %}
        <tr>
            <td>{{ attack.timestamp }}</td>
            <td>{{ attack.ip }}</td>
            <td>{{ attack.country }}</td>
            <td class="alert">{{ attack.username }}</td>
            <td class="alert">{{ attack.password }}</td>
            <td><span class="badge badge-red">BLOCKED</span></td>
        </tr>
        {% endfor %}
    </table>
</div>

</body>
</html>
"""

@app.route('/')
def dashboard():
    import datetime
    attacks = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE) as f:
                attacks = json.load(f)
        except:
            pass

    total = len(attacks)
    unique_ips = len(set(a['ip'] for a in attacks))
    unique_countries = len(set(a['country'] for a in attacks))
    top_usernames = Counter(a['username'] for a in attacks).most_common(5)
    top_passwords = Counter(a['password'] for a in attacks).most_common(5)
    top_countries = Counter(a['country'] for a in attacks).most_common(5)

    return render_template_string(HTML,
        attacks=list(reversed(attacks))[:20],
        total=total if total > 0 else 0,
        unique_ips=unique_ips,
        unique_countries=unique_countries,
        top_usernames=top_usernames,
        top_passwords=top_passwords,
        top_countries=top_countries,
        now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

if __name__ == '__main__':
    print("Honeypot Dashboard running at http://localhost:5001")
    app.run(host='0.0.0.0', port=5001)
