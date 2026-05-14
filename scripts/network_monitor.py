import psutil
import datetime

print("=== Cyber Lab - Network Monitor ===")
print(f"Time: {datetime.datetime.now()}")
print()

print("=== Active Network Connections ===")
connections = psutil.net_connections()
for conn in connections:
    if conn.status == 'ESTABLISHED':
        print(f"  Local: {conn.laddr} --> Remote: {conn.raddr} | Status: {conn.status}")

print()
print("=== Network Interface Stats ===")
stats = psutil.net_if_stats()
for interface, stat in stats.items():
    status = "UP" if stat.isup else "DOWN"
    print(f"  {interface}: {status} | Speed: {stat.speed}Mb/s")

print()
print("=== Data Sent/Received ===")
net_io = psutil.net_io_counters()
print(f"  Data Sent:     {round(net_io.bytes_sent / 1024 / 1024, 2)} MB")
print(f"  Data Received: {round(net_io.bytes_recv / 1024 / 1024, 2)} MB")

print()
print("Scan complete.")
