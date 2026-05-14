import psutil
import datetime

print("=== Cyber Lab - System Monitor ===")
print(f"Time: {datetime.datetime.now()}")
print()

cpu = psutil.cpu_percent(interval=1)
memory = psutil.virtual_memory()
disk = psutil.disk_usage('/')

print(f"CPU Usage:    {cpu}%")
print(f"Memory Used:  {memory.percent}%")
print(f"Disk Used:    {disk.percent}%")
print()

print("=== Running Processes ===")
for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
    try:
        if proc.info['cpu_percent'] > 5.0:
            print(f"  PID {proc.info['pid']} | {proc.info['name']} | CPU: {proc.info['cpu_percent']}%")
    except:
        pass

print()
print("Scan complete.")
