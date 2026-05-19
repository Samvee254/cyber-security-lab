import smtplib
import psutil
import subprocess
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email config
SENDER = "Samvee4141@gmail.com"
RECEIVER = "Samvee4141@gmail.com"
APP_PASSWORD = "ncsvftzcgtpkskgb"

BASELINE = {'cpu': 0.1, 'memory': 29.7, 'disk': 17.3}

def send_alert(subject, body):
    msg = MIMEMultipart()
    msg['From'] = SENDER
    msg['To'] = RECEIVER
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER, APP_PASSWORD)
        server.sendmail(SENDER, RECEIVER, msg.as_string())
        server.quit()
        print(f"[{datetime.datetime.now()}] ✅ Alert sent: {subject}")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] ❌ Failed to send alert: {e}")

def check_and_alert():
    alerts = []
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check CPU
    cpu = psutil.cpu_percent(interval=1)
    if cpu > BASELINE['cpu'] + 30:
        alerts.append(f"🔴 HIGH CPU: {cpu}% (baseline: {BASELINE['cpu']}%)")

    # Check Memory
    memory = psutil.virtual_memory().percent
    if memory > BASELINE['memory'] + 20:
        alerts.append(f"🔴 HIGH MEMORY: {memory}% (baseline: {BASELINE['memory']}%)")

    # Check Disk
    disk = psutil.disk_usage('/').percent
    if disk > BASELINE['disk'] + 30:
        alerts.append(f"🔴 HIGH DISK: {disk}% (baseline: {BASELINE['disk']}%)")

    # Check Connections
    try:
        connections = len(psutil.net_connections(kind='inet'))
        if connections > 20:
            alerts.append(f"🔴 UNUSUAL CONNECTIONS: {connections} (baseline: 8)")
    except Exception:
        pass

    # Check Failed Logins
    result = subprocess.run(
        ['sudo', 'grep', 'Failed password', '/var/log/auth.log'],
        capture_output=True, text=True
    )
    failed_logins = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
    if len(failed_logins) >= 3:
        alerts.append(f"🔴 FAILED LOGINS: {len(failed_logins)} attempts detected")
        for line in failed_logins[-3:]:
            alerts.append(f"   {line[:80]}")

    # Send email if any alerts
    if alerts:
        subject = f"⚠ CYBER LAB ALERT — {len(alerts)} issue(s) detected"
        body = f"""
CYBER LAB — SECURITY ALERT
===========================
Time: {now}
System: Linux (Ubuntu 24.04)
User: sam

ISSUES DETECTED:
{chr(10).join(alerts)}

===========================
This is an automated alert from your Cyber Lab monitoring system.
        """
        send_alert(subject, body)
    else:
        print(f"[{now}] ✅ All systems normal — no alerts.")

if __name__ == '__main__':
    print("🔔 Cyber Lab Alert System starting...")
    check_and_alert()
