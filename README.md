# 🔐 AI-Powered Cybersecurity Monitoring Lab

A real-time cybersecurity monitoring system built on Linux (Ubuntu) using Python.
This project combines cybersecurity, cloud computing, data engineering, Linux,
and AI concepts to monitor system activity, detect suspicious behavior,
and generate automated security reports.

## 🛠️ Tools & Technologies
- Python 3.12
- psutil (system & network monitoring)
- Flask (web dashboard)
- Linux (Ubuntu 24)
- Git & GitHub

## 📁 Project Structure
- scripts/ - All monitoring scripts
- logs/ - Auto-generated security reports
- dashboards/ - Charts and screenshots
- data/ - Baseline and processed data
- ai_models/ - AI detection models

## 🚀 How to Run
```bash
git clone https://github.com/Samvee254/cyber-security-lab.git
cd cyber-security-lab
pip3 install psutil flask --break-system-packages
python3 scripts/security_report.py
python3 scripts/dashboard.py
