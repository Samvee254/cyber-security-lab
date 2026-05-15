import psutil
import datetime
import json
import os

BASELINE_FILE = "data/baseline.json"
ALERT_FILE = "logs/alerts.log"

os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

def get_current_stats():
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "connections": len(psutil.net_connections())
    }

def save_baseline(stats):
    with open(BASELINE_FILE, "w") as f:
        json.dump(stats, f)
    print("Baseline saved!")

def load_baseline():
    with open(BASELINE_FILE, "r") as f:
        return json.load(f)

def detect_anomalies(current, baseline):
    alerts = []

    if current["cpu"] > baseline["cpu"] + 30:
        alerts.append(f"HIGH CPU: {current['cpu']}% (baseline: {baseline['cpu']}%)")

    if current["memory"] > baseline["memory"] + 20:
        alerts.append(f"HIGH MEMORY: {current['memory']}% (baseline: {baseline['memory']}%)")

    if current["connections"] > baseline["connections"] + 10:
        alerts.append(
            f"UNUSUAL CONNECTIONS: {current['connections']} "
            f"(baseline: {baseline['connections']})"
        )

    return alerts

print("=== Cyber Lab - AI Anomaly Detector ===")
print(f"Time: {datetime.datetime.now()}")
print()

current = get_current_stats()

print(f"Current Stats: {current}")
print()

if not os.path.exists(BASELINE_FILE):
    print("No baseline found. Saving current stats as baseline...")
    save_baseline(current)

else:
    baseline = load_baseline()

    print(f"Baseline Stats: {baseline}")
    print()

    alerts = detect_anomalies(current, baseline)

    if alerts:
        print("⚠️  ANOMALIES DETECTED:")

        for alert in alerts:
            print(f"   {alert}")

        with open(ALERT_FILE, "a") as f:
            for alert in alerts:
                f.write(f"{datetime.datetime.now()} - {alert}\n")

    else:
        print("✅ All systems normal. No anomalies detected.")

