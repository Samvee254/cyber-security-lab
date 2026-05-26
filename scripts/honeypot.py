import socket
import threading
import paramiko
import json
import os
import datetime
import requests

LOG_FILE = "/home/sam/Desktop/cyber-lab/logs/honeypot_attacks.json"
HOST_KEY = paramiko.RSAKey.generate(2048)

def lookup_country(ip):
    try:
        if ip.startswith("127.") or ip.startswith("192.168.") or ip.startswith("10."):
            return "Local"
        r = requests.get(f"https://ipapi.co/{ip}/json/", timeout=3)
        return r.json().get("country_name", "Unknown")
    except:
        return "Unknown"

class FakeSSHServer(paramiko.ServerInterface):
    def __init__(self, ip):
        self.ip = ip

    def check_auth_password(self, username, password):
        country = lookup_country(self.ip)
        entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip": self.ip,
            "country": country,
            "username": username,
            "password": password
        }
        attacks = []
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE) as f:
                    attacks = json.load(f)
            except:
                pass
        attacks.append(entry)
        with open(LOG_FILE, "w") as f:
            json.dump(attacks, f, indent=2)
        print(f"[HONEYPOT] {entry['timestamp']} | {self.ip} ({country}) | {username}:{password}")
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return "password"

    def check_channel_request(self, kind, chanid):
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

def handle_client(sock, ip):
    try:
        t = paramiko.Transport(sock)
        t.add_server_key(HOST_KEY)
        t.start_server(server=FakeSSHServer(ip))
        chan = t.accept(20)
        if chan:
            chan.close()
        t.close()
    except:
        pass
    finally:
        sock.close()

def start_honeypot():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", 2222))
    s.listen(100)
    print("[HONEYPOT] Fake SSH server listening on port 2222...")
    while True:
        client, addr = s.accept()
        print(f"[HONEYPOT] Connection from {addr[0]}")
        threading.Thread(target=handle_client, args=(client, addr[0]), daemon=True).start()

if __name__ == "__main__":
    start_honeypot()
