#!/bin/bash

cd /home/sam/Desktop/cyber-lab

echo "=== Cyber Lab Auto-Scan Starting ==="
echo "Time: $(date)"

python3 scripts/log_monitor.py
python3 scripts/system_monitor.py
python3 scripts/network_monitor.py
python3 scripts/security_report.py
python3 scripts/anomaly_detector.py
python3 scripts/visualize.py

echo "=== Auto-Scan Complete ==="

