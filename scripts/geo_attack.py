import subprocess
import requests
import json
import os
from collections import Counter

def get_failed_ips():
    result = subprocess.run(
        ['sudo', 'grep', 'Failed password', '/var/log/auth.log'],
        capture_output=True, text=True
    )
    ips = []
    for line in result.stdout.strip().split('\n'):
        if 'from' in line:
            parts = line.split('from ')
            if len(parts) > 1:
                ip = parts[1].split(' ')[0].strip()
                if ip:
                    ips.append(ip)
    return ips

def lookup_country(ip):
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}', timeout=3)
        data = response.json()
        if data['status'] == 'success':
            return data.get('country', 'Unknown')
    except:
        pass
    return 'Unknown'

def get_attack_map():
    ips = get_failed_ips()
    if not ips:
        return {}
    country_counts = Counter()
    seen_ips = {}
    for ip in ips:
        if ip not in seen_ips:
            country = lookup_country(ip)
            seen_ips[ip] = country
        country_counts[seen_ips[ip]] += 1
    return dict(country_counts.most_common(10))

if __name__ == '__main__':
    print("🌍 Cyber Lab — Attack Origin Map")
    print("=" * 40)
    attack_map = get_attack_map()
    if attack_map:
        for country, count in attack_map.items():
            bar = '█' * min(count, 20)
            print(f"{country:<20} {bar} ({count})")
    else:
        print("No attacks detected!")
