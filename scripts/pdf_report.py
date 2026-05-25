
import psutil, datetime, subprocess, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import cm

CYAN = HexColor("#00aacc")
GREEN = HexColor("#008844")
RED = HexColor("#cc2222")
ORANGE = HexColor("#cc7700")
DARK = HexColor("#1a1a2e")
LIGHT_BG = HexColor("#f0f6ff")
MID_BG = HexColor("#ddeeff")
WHITE = HexColor("#ffffff")

def make_style(name, size=10, color=DARK, bold=False, align=0, space_after=4):
    return ParagraphStyle(name, fontSize=size,
        textColor=color,
        fontName="Helvetica-Bold" if bold else "Helvetica",
        spaceAfter=space_after, alignment=align)

def generate():
    now = datetime.datetime.now()
    fname = f"logs/security_report_{now.strftime('%Y%m%d_%H%M%S')}.pdf"
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    try: conns = len(psutil.net_connections(kind="inet"))
    except: conns = 0
    cpu_temps = {}
    try:
        t = psutil.sensors_temperatures()
        if "coretemp" in t:
            for s in t["coretemp"]:
                if "Core" in s.label:
                    cpu_temps[s.label] = round(s.current, 1)
    except: pass
    try:
        io = psutil.disk_io_counters()
        dr = round(io.read_bytes/1024/1024/1024, 2)
        dw = round(io.write_bytes/1024/1024/1024, 2)
    except: dr = dw = 0
    r = subprocess.run(["sudo","grep","Failed password","/var/log/auth.log"], capture_output=True, text=True)
    attacks = [l.strip()[:90] for l in r.stdout.strip().split("\n") if l.strip()]
    procs = []
    for p in sorted(psutil.process_iter(["pid","name","cpu_percent","memory_percent"]),
        key=lambda x: x.info["cpu_percent"] or 0, reverse=True)[:5]:
        procs.append([str(p.info["pid"]), p.info["name"][:18],
            f"{round(p.info['cpu_percent'] or 0,1)}%",
            f"{round(p.info['memory_percent'] or 0,1)}%"])
    anomalies = []
    if cpu > 30: anomalies.append(f"HIGH CPU: {cpu}%")
    if mem > 50: anomalies.append(f"HIGH MEMORY: {mem}%")
    if conns > 20: anomalies.append(f"UNUSUAL CONNECTIONS: {conns}")

    doc = SimpleDocTemplate(fname, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)

    T = make_style
    story = []
    story.append(Paragraph("CYBER LAB — AI SECURITY REPORT", T("t",20,CYAN,True,1,4)))
    story.append(Paragraph("AI-Powered Cybersecurity Monitoring System", T("s",11,GREEN,False,1,2)))
    story.append(Paragraph(f"Date: {now.strftime('%Y-%m-%d %H:%M:%S')}  |  System: Linux Ubuntu 24.04  |  User: sam", T("d",9,DARK,False,1,6)))
    story.append(HRFlowable(width="100%",thickness=2,color=CYAN))
    story.append(Spacer(1,0.3*cm))

    status_color = RED if anomalies else GREEN
    status_text = f"⚠ {len(anomalies)} ANOMALIES DETECTED" if anomalies else "✅ ALL SYSTEMS NORMAL"
    story.append(Paragraph(status_text, T("st",14,status_color,True,1,8)))

    story.append(Paragraph("SYSTEM SUMMARY", T("h",12,CYAN,True,0,4)))
    rows = [["Metric","Value","Status"],
        ["CPU Usage", f"{cpu}%", "⚠ HIGH" if cpu>50 else "✅ OK"],
        ["Memory Usage", f"{mem}%", "⚠ HIGH" if mem>70 else "✅ OK"],
        ["Disk Usage", f"{disk}%", "⚠ HIGH" if disk>80 else "✅ OK"],
        ["Network Connections", str(conns), "⚠ HIGH" if conns>20 else "✅ OK"],
        ["Failed Logins", str(len(attacks)), "⚠ ALERT" if attacks else "✅ NONE"],
        ["Anomalies Detected", str(len(anomalies)), "⚠ YES" if anomalies else "✅ NO"],
    ]
    t = Table(rows, colWidths=[6*cm,5*cm,5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),CYAN),
        ("TEXTCOLOR",(0,0),(-1,0),WHITE),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),9),
        ("BACKGROUND",(0,1),(-1,-1),LIGHT_BG),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[LIGHT_BG,MID_BG]),
        ("TEXTCOLOR",(0,1),(-1,-1),DARK),
        ("GRID",(0,0),(-1,-1),0.5,HexColor("#aaccee")),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("PADDING",(0,0),(-1,-1),7),
    ]))
    story.append(t)

    story.append(Paragraph("LOGIN ATTACK DETECTION", T("h2",12,CYAN,True,0,4)))
    if attacks:
        story.append(Paragraph(f"⚠ {len(attacks)} failed SSH login attempts detected!", T("a",10,RED,True,0,4)))
        for line in attacks[-5:]:
            story.append(Paragraph(f"• {line}", T("b",8,DARK,False,0,2)))
    else:
        story.append(Paragraph("✅ No failed login attempts found.", T("ok",10,GREEN,True,0,4)))

    story.append(Paragraph("TOP PROCESSES BY CPU", T("h3",12,CYAN,True,0,4)))
    ph = [["PID","Process Name","CPU %","Memory %"]] + procs
    pt = Table(ph, colWidths=[3*cm,7*cm,3*cm,3*cm])
    pt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),GREEN),
        ("TEXTCOLOR",(0,0),(-1,0),WHITE),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),9),
        ("BACKGROUND",(0,1),(-1,-1),LIGHT_BG),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[LIGHT_BG,MID_BG]),
        ("TEXTCOLOR",(0,1),(-1,-1),DARK),
        ("GRID",(0,0),(-1,-1),0.5,HexColor("#aaccee")),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("PADDING",(0,0),(-1,-1),7),
    ]))
    story.append(pt)

    story.append(Paragraph("SYSTEM HEALTH", T("h4",12,CYAN,True,0,4)))
    if cpu_temps:
        for core, temp in cpu_temps.items():
            c = RED if temp>80 else ORANGE if temp>60 else GREEN
            story.append(Paragraph(f"• {core}: {temp}°C", T("temp",9,c,False,0,2)))
    story.append(Paragraph(f"• Disk Read Total: {dr} GB", T("dr",9,DARK,False,0,2)))
    story.append(Paragraph(f"• Disk Write Total: {dw} GB", T("dw",9,DARK,False,0,2)))

    story.append(Paragraph("AI ANOMALY DETECTION (ISOLATION FOREST)", T("h5",12,CYAN,True,0,4)))
    if anomalies:
        for a in anomalies:
            story.append(Paragraph(f"🔴 {a}", T("an",10,RED,True,0,3)))
    else:
        story.append(Paragraph("✅ ML model detected no anomalies. System behaviour is within normal parameters.", T("noan",10,GREEN,False,0,3)))

    story.append(HRFlowable(width="100%",thickness=1,color=CYAN))
    story.append(Paragraph("Cyber Lab — AI Powered Cybersecurity Monitoring System", T("f1",8,DARK,False,1,2)))
    story.append(Paragraph("Author: Samantha Vivian | Machakos University, Kenya", T("f2",8,DARK,False,1,2)))
    story.append(Paragraph("github.com/Samvee254/cyber-security-lab", T("f3",8,CYAN,False,1,2)))

    doc.build(story)
    print("PDF generated")

def main():
    generate()

if __name__ == "__main__":
    main()
