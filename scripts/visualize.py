import psutil
import datetime
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print("=== Cyber Lab - Security Dashboard ===")
print("Collecting data for 10 seconds...")

cpu_data = []
memory_data = []
timestamps = []

for i in range(10):
    cpu_data.append(psutil.cpu_percent(interval=1))
    memory_data.append(psutil.virtual_memory().percent)
    timestamps.append(i + 1)
    print(f"  Sample {i+1}/10 collected...")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
fig.suptitle('Cyber Lab - System Security Dashboard', fontsize=14, fontweight='bold')

ax1.plot(timestamps, cpu_data, color='red', marker='o', linewidth=2)
ax1.set_title('CPU Usage Over Time')
ax1.set_ylabel('CPU %')
ax1.set_ylim(0, 100)
ax1.grid(True)

ax2.plot(timestamps, memory_data, color='blue', marker='o', linewidth=2)
ax2.set_title('Memory Usage Over Time')
ax2.set_ylabel('Memory %')
ax2.set_ylim(0, 100)
ax2.grid(True)

plt.tight_layout()
plt.savefig('dashboards/security_dashboard.png')

print()
print("Dashboard saved to dashboards/security_dashboard.png")
