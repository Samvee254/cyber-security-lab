import subprocess
import datetime

print("=== Cyber Lab - Login Monitor ===")
print(f"Scan Time: {datetime.datetime.now()}")
print()

result = subprocess.run(
    ["sudo", "grep", "Failed password", "/var/lo/auth.log"],
    capture_output=True, text=True
)

if result.stdout:
    print("FAILED LOGIN ATTEMPTS FOUND:")
    print(result.stdout)
else:
    print("No failed login attempts found.")
