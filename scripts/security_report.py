import psutil
import datetime
import subprocess
import os

timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
report_file = f"logs/security_report_{timestamp}.txt"

def write(f, text=""):
    print(text)
    f.write(text + "\n")

os.makedirs("logs", exist_ok=True)

with open(report_file, "w") as f:
    write(f, "="*50)
    write(f, "   CYBER LAB - FULL SECURITY REPORT")
    write(f, f"   Generated: {datetime.datetime.now()}")
    write(f, "="*50)

    write(f, "\n--- SYSTEM STATS ---")
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    write(f, f"CPU Usage:    {cpu}%")
    write(f, f"Memory Used:  {memory.percent}%")
    write(f, f"Disk Used:    {disk.percent}%")

    write(f, "\n--- NETWORK CONNECTIONS ---")
    for conn in psutil.net_connections():
        if conn.status == 'ESTABLISHED':
            write(f, f"  {conn.laddr} --> {conn.raddr}")

    write(f, "\n--- LOGIN ATTACK CHECK ---")
    result = subprocess.run(
        ["sudo", "grep", "Failed password", "/var/log/auth.log"],
        capture_output=True, text=True
    )
    if result.stdout:
        write(f, "WARNING: Failed logins detected!")
        write(f, result.stdout)
    else:
        write(f, "No failed login attempts found.")

    write(f, "\n--- DATA USAGE ---")
    net_io = psutil.net_io_counters()
    write(f, f"Sent:     {round(net_io.bytes_sent/1024/1024, 2)} MB")
    write(f, f"Received: {round(net_io.bytes_recv/1024/1024, 2)} MB")

    write(f, "\n" + "="*50)
    write(f, "Report saved to: " + report_file)

print(f"\nReport file created: {report_file}")
