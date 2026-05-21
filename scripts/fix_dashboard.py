# Test if template renders correctly
from flask import render_template_string

template = "{{ test }}"
try:
    from jinja2 import Environment
    env = Environment()
    t = env.from_string(template)
    print("Jinja2 OK")
except Exception as e:
    print(f"Error: {e}")

# Check what's actually in dashboard.py around line 104
with open('/home/sam/Desktop/cyber-lab/scripts/dashboard.py', 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[100:115], start=101):
        print(f"{i}: {line}", end='')
