import streamlit as st
import sqlite3
import hashlib
import json
import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="WorkSafe Pro — Ergonomics Scorer",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; }

[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0f1923 0%, #162032 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] * { color: #e2eaf4 !important; }
[data-testid="stSidebar"] .stRadio label { font-size: 0.92rem; }

.hero-banner {
    background: linear-gradient(135deg, #0d1f2d 0%, #1a3a5c 50%, #0d2d4a 100%);
    border-radius: 16px;
    padding: 2.2rem 2.5rem;
    margin-bottom: 1.6rem;
    border: 1px solid rgba(56,189,248,0.15);
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(56,189,248,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.1rem;
    font-weight: 800;
    color: #e0f2fe;
    margin: 0 0 0.3rem;
    letter-spacing: -0.5px;
}
.hero-sub {
    color: #7dd3fc;
    font-size: 0.95rem;
    font-weight: 300;
}

.section-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.2rem;
    border: 1px solid #e8edf4;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #1e3a5f;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.score-badge {
    display: inline-block;
    font-family: 'Syne', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    padding: 0.5rem 1.5rem;
    border-radius: 12px;
    letter-spacing: -1px;
}
.badge-excellent { background:#dcfce7; color:#166534; }
.badge-good      { background:#dbeafe; color:#1e40af; }
.badge-moderate  { background:#fef9c3; color:#854d0e; }
.badge-poor      { background:#fee2e2; color:#991b1b; }

.metric-tile {
    background: linear-gradient(135deg, #f0f7ff, #e8f4ff);
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    text-align: center;
    border: 1px solid #c7def8;
}
.metric-tile .val {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: #1e40af;
}
.metric-tile .lbl {
    font-size: 0.78rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}

.q-card {
    background: #f8fafc;
    border-left: 4px solid #38bdf8;
    border-radius: 0 8px 8px 0;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.7rem;
}
.q-label { font-size: 0.9rem; color:#374151; font-weight: 500; }
.q-weight { font-size: 0.75rem; color:#94a3b8; }

.risk-high   { background:#fee2e2; color:#b91c1c; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.risk-medium { background:#fef3c7; color:#b45309; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.risk-low    { background:#d1fae5; color:#065f46; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }

.stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #2563eb);
    color: white !important;
    border: none;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 0.9rem;
    padding: 0.55rem 1.4rem;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1e40af, #1d4ed8);
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(29,78,216,0.3);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: #f1f5f9;
    padding: 6px;
    border-radius: 10px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 0.88rem;
    color: #475569;
    padding: 6px 18px;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #1d4ed8 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.stSelectbox > div, .stSlider > div { color: #1e293b; }
label { color: #374151 !important; font-size: 0.88rem !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  DATABASE
# ─────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect("worksafe.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT,
        department TEXT,
        role TEXT DEFAULT 'user',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        department TEXT,
        scores_json TEXT,
        total_score REAL,
        risk_level TEXT,
        recommendations_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS admin_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );
    """)
    try:
        c.execute("INSERT INTO admin_users (username, password) VALUES (?, ?)",
                  ("admin", hashlib.sha256("admin123".encode()).hexdigest()))
    except sqlite3.IntegrityError:
        pass
    conn.commit()
    conn.close()

init_db()

def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

def register_user(username, password, full_name, department):
    conn = get_db()
    try:
        conn.execute("INSERT INTO users (username,password,full_name,department) VALUES (?,?,?,?)",
                     (username, hash_pw(password), full_name, department))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE username=? AND password=?",
                       (username, hash_pw(password))).fetchone()
    conn.close()
    return dict(row) if row else None

def login_admin(username, password):
    conn = get_db()
    row = conn.execute("SELECT * FROM admin_users WHERE username=? AND password=?",
                       (username, hash_pw(password))).fetchone()
    conn.close()
    return dict(row) if row else None

def save_assessment(user_id, username, department, scores, total, risk, recs):
    conn = get_db()
    conn.execute(
        "INSERT INTO assessments (user_id,username,department,scores_json,total_score,risk_level,recommendations_json) VALUES (?,?,?,?,?,?,?)",
        (user_id, username, department, json.dumps(scores), total, risk, json.dumps(recs))
    )
    conn.commit()
    conn.close()

def get_user_history(user_id):
    conn = get_db()
    rows = conn.execute("SELECT * FROM assessments WHERE user_id=? ORDER BY created_at DESC", (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_assessments():
    conn = get_db()
    rows = conn.execute("SELECT * FROM assessments ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_users():
    conn = get_db()
    rows = conn.execute("SELECT id,username,full_name,department,created_at FROM users").fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ─────────────────────────────────────────────
#  ASSESSMENT FRAMEWORK
# ─────────────────────────────────────────────
CATEGORIES = {
    "🪑 Seating & Posture": {
        "color": "#3b82f6",
        "questions": [
            {"id": "seat_height",   "text": "Chair height allows feet flat on floor / footrest",       "weight": 8},
            {"id": "lumbar",        "text": "Chair provides adequate lumbar (lower back) support",       "weight": 9},
            {"id": "seat_depth",    "text": "Seat depth supports thighs without pressure behind knees", "weight": 7},
            {"id": "armrests",      "text": "Armrests allow relaxed shoulders (90° elbow angle)",       "weight": 6},
            {"id": "back_upright",  "text": "Back remains upright (90–110° recline) during work",      "weight": 8},
        ]
    },
    "🖥️ Monitor & Display": {
        "color": "#8b5cf6",
        "questions": [
            {"id": "monitor_dist",  "text": "Monitor at arm's length (50–70 cm) from eyes",            "weight": 8},
            {"id": "monitor_height","text": "Top of screen at or slightly below eye level",             "weight": 9},
            {"id": "monitor_glare", "text": "Screen free from glare and reflections",                  "weight": 7},
            {"id": "refresh_rate",  "text": "Display refresh rate ≥ 60 Hz; resolution clear",          "weight": 5},
            {"id": "dual_monitor",  "text": "If dual monitors: primary centred, secondary at same height","weight": 4},
        ]
    },
    "⌨️ Keyboard & Mouse": {
        "color": "#10b981",
        "questions": [
            {"id": "kb_position",   "text": "Keyboard positioned so wrists are straight (neutral)",    "weight": 8},
            {"id": "mouse_close",   "text": "Mouse adjacent to keyboard, same surface level",          "weight": 7},
            {"id": "wrist_rest",    "text": "Wrist rest used only during pauses, not while typing",    "weight": 5},
            {"id": "kb_tilt",       "text": "Keyboard tilt is low / flat to avoid wrist extension",    "weight": 6},
        ]
    },
    "💡 Lighting & Environment": {
        "color": "#f59e0b",
        "questions": [
            {"id": "ambient_light", "text": "Ambient lighting adequate (300–500 lux for office work)", "weight": 7},
            {"id": "no_flicker",    "text": "No flickering lights; lighting uniform across workspace", "weight": 6},
            {"id": "noise_level",   "text": "Background noise below 55 dB (acceptable for ICT work)", "weight": 6},
            {"id": "temperature",   "text": "Room temperature comfortable (20–24 °C) & ventilated",   "weight": 6},
            {"id": "air_quality",   "text": "Air quality good; no dust, fumes, or stale air",         "weight": 5},
        ]
    },
    "📐 Desk & Workspace Layout": {
        "color": "#ef4444",
        "questions": [
            {"id": "desk_height",   "text": "Desk height allows 90° elbow angle when typing",         "weight": 8},
            {"id": "reach_zone",    "text": "Frequently used items within primary reach zone (30 cm)", "weight": 7},
            {"id": "leg_clearance", "text": "Adequate leg clearance under desk (no obstructions)",    "weight": 6},
            {"id": "cable_mgmt",    "text": "Cables managed; no trip/entanglement hazards",           "weight": 5},
            {"id": "documents",     "text": "Document holder used for reference material (if needed)", "weight": 4},
        ]
    },
    "🧘 Work Habits & Breaks": {
        "color": "#06b6d4",
        "questions": [
            {"id": "micro_breaks",  "text": "Micro-breaks taken every 30–45 min (stand/stretch)",     "weight": 9},
            {"id": "eye_breaks",    "text": "20-20-20 rule followed (every 20 min, look 20 ft, 20 s)","weight": 8},
            {"id": "posture_aware", "text": "Worker aware of posture and self-corrects during day",   "weight": 8},
            {"id": "hydration",     "text": "Water available and regularly consumed at workstation",   "weight": 5},
            {"id": "exercise",      "text": "Regular physical activity / ergonomic exercises practised","weight": 7},
        ]
    },
    "🧠 Psychosocial Factors": {
        "color": "#ec4899",
        "questions": [
            {"id": "workload",      "text": "Workload is manageable within working hours",             "weight": 8},
            {"id": "job_control",   "text": "Worker has control over task pace and method",           "weight": 7},
            {"id": "social_support","text": "Good social support from colleagues/supervisors",        "weight": 6},
            {"id": "stress_level",  "text": "Stress levels are low to moderate (self-reported)",      "weight": 8},
            {"id": "digital_wellbeing","text":"Digital screen time managed; no tech-induced fatigue", "weight": 7},
        ]
    },
}

SCALE_LABELS = {
    1: "Never / Not at all",
    2: "Rarely",
    3: "Sometimes",
    4: "Often",
    5: "Always / Fully"
}

def compute_scores(responses):
    category_scores = {}
    total_weighted = 0
    total_weight = 0
    for cat_name, cat_data in CATEGORIES.items():
        cat_weighted = 0
        cat_weight = 0
        for q in cat_data["questions"]:
            val = responses.get(q["id"], 3)
            w = q["weight"]
            cat_weighted += val * w
            cat_weight += w
        pct = (cat_weighted / (cat_weight * 5)) * 100
        category_scores[cat_name] = round(pct, 1)
        total_weighted += cat_weighted
        total_weight += cat_weight
    total_pct = (total_weighted / (total_weight * 5)) * 100
    return round(total_pct, 1), category_scores

def get_risk_level(score):
    if score >= 80: return "Excellent", "badge-excellent", "🟢"
    if score >= 65: return "Good",      "badge-good",      "🔵"
    if score >= 45: return "Moderate",  "badge-moderate",  "🟡"
    return "Poor", "badge-poor", "🔴"

def generate_recommendations(category_scores, responses):
    recs = []
    THRESHOLDS = {
        "🪑 Seating & Posture": {
            "seat_height":   ("Adjust chair height so feet rest flat on the floor or use a footrest.", "High"),
            "lumbar":        ("Add a lumbar support cushion or adjust built-in lumbar support.", "High"),
            "back_upright":  ("Set monitor/task reminders to correct posture every 30 minutes.", "Medium"),
        },
        "🖥️ Monitor & Display": {
            "monitor_height":("Raise monitor using a stand or books so top aligns with eye level.", "High"),
            "monitor_dist":  ("Move monitor to arm's-length distance (50–70 cm).", "High"),
            "monitor_glare": ("Reposition monitor perpendicular to windows; use anti-glare filter.", "Medium"),
        },
        "⌨️ Keyboard & Mouse": {
            "kb_position":   ("Place keyboard so forearms are parallel to floor, wrists neutral.", "High"),
            "mouse_close":   ("Move mouse adjacent to keyboard to reduce shoulder reach.", "Medium"),
        },
        "💡 Lighting & Environment": {
            "ambient_light": ("Install task lighting (300–500 lux) or adjust blind/curtain positions.", "Medium"),
            "noise_level":   ("Use acoustic panels, noise-cancelling headphones, or quiet hours policy.", "Medium"),
            "temperature":   ("Adjust HVAC or use personal fan/heater within 20–24 °C range.", "Low"),
        },
        "📐 Desk & Workspace Layout": {
            "desk_height":   ("Use a height-adjustable desk or monitor/keyboard risers.", "High"),
            "reach_zone":    ("Reorganise desktop: keep mouse, phone, stationery within 30 cm.", "Medium"),
            "cable_mgmt":    ("Use cable trays/clips to remove trip hazards under/around desk.", "Low"),
        },
        "🧘 Work Habits & Breaks": {
            "micro_breaks":  ("Set a timer every 30–45 min to stand, stretch, or walk briefly.", "High"),
            "eye_breaks":    ("Follow the 20-20-20 rule; use a reminder app if needed.", "High"),
            "exercise":      ("Incorporate 10-min desk stretches and a 30-min walk into daily routine.", "Medium"),
        },
        "🧠 Psychosocial Factors": {
            "workload":      ("Discuss workload with supervisor; use task prioritisation matrix.", "High"),
            "stress_level":  ("Use mindfulness breaks, limit after-hours emails, consider counselling.", "High"),
            "digital_wellbeing":("Apply digital detox periods; enable blue-light filter after 6 PM.", "Medium"),
        },
    }
    for cat, q_map in THRESHOLDS.items():
        for qid, (advice, priority) in q_map.items():
            if responses.get(qid, 5) <= 2:
                recs.append({"category": cat, "advice": advice, "priority": priority, "score": responses.get(qid, 5)})
    for cat, score in category_scores.items():
        if score < 50 and not any(r["category"] == cat for r in recs):
            recs.append({
                "category": cat,
                "advice": f"Overall {cat.split(' ', 1)[1]} score is low ({score}%). Schedule a workstation ergonomic review.",
                "priority": "Medium",
                "score": score
            })
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    recs.sort(key=lambda x: priority_order.get(x["priority"], 3))
    return recs

# ─────────────────────────────────────────────
#  PDF REPORT
# ─────────────────────────────────────────────
def build_pdf_report(username, department, total_score, risk_level, category_scores, recs, date_str):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title2', parent=styles['Title'],
                                 fontSize=20, textColor=colors.HexColor('#1e3a5f'),
                                 spaceAfter=4, fontName='Helvetica-Bold', alignment=TA_CENTER)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'],
                              fontSize=13, textColor=colors.HexColor('#1d4ed8'),
                              spaceBefore=14, spaceAfter=4, fontName='Helvetica-Bold')
    body_style = ParagraphStyle('Body2', parent=styles['Normal'],
                                fontSize=9.5, leading=14, spaceAfter=4)
    small_style = ParagraphStyle('Small', parent=styles['Normal'],
                                 fontSize=8.5, textColor=colors.HexColor('#64748b'))
    RISK_COLORS = {
        "Excellent": colors.HexColor('#166534'),
        "Good":      colors.HexColor('#1e40af'),
        "Moderate":  colors.HexColor('#854d0e'),
        "Poor":      colors.HexColor('#991b1b'),
    }
    risk_color = RISK_COLORS.get(risk_level, colors.black)
    story = []

    story.append(Paragraph("WorkSafe Pro", title_style))
    story.append(Paragraph("Workstation Ergonomics & Safety Assessment Report",
                           ParagraphStyle('sub', parent=styles['Normal'], fontSize=11,
                                          textColor=colors.HexColor('#475569'), alignment=TA_CENTER)))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1d4ed8')))
    story.append(Spacer(1, 0.4*cm))

    meta = [
        ["Assessor:", username, "Date:", date_str],
        ["Department:", department, "Risk Level:", risk_level],
    ]
    meta_table = Table(meta, colWidths=[3*cm, 6*cm, 3*cm, 5*cm])
    meta_table.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (-1,-1), 'Helvetica'),
        ('FONTNAME',  (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',  (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE',  (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (3,1), (3,1), risk_color),
        ('FONTNAME',  (3,1), (3,1), 'Helvetica-Bold'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Overall Safety Score", h2_style))
    score_data = [[f"{total_score:.1f} / 100", risk_level]]
    score_table = Table(score_data, colWidths=[4*cm, 6*cm])
    score_table.setStyle(TableStyle([
        ('FONTNAME',  (0,0), (0,0), 'Helvetica-Bold'),
        ('FONTSIZE',  (0,0), (0,0), 26),
        ('TEXTCOLOR', (0,0), (0,0), risk_color),
        ('FONTNAME',  (1,0), (1,0), 'Helvetica-Bold'),
        ('FONTSIZE',  (1,0), (1,0), 14),
        ('TEXTCOLOR', (1,0), (1,0), risk_color),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0f9ff')),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#bae6fd')),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Category Breakdown", h2_style))
    cat_data = [["Category", "Score (%)", "Status"]]
    for cat, score in category_scores.items():
        if score >= 80:   status = "Excellent"
        elif score >= 65: status = "Good"
        elif score >= 45: status = "Moderate"
        else:             status = "Needs Attention"
        cat_data.append([cat, f"{score:.1f}%", status])
    cat_table = Table(cat_data, colWidths=[8*cm, 3.5*cm, 5.5*cm])
    cat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1d4ed8')),
        ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f8fafc'), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(cat_table)
    story.append(Spacer(1, 0.5*cm))

    if recs:
        story.append(Paragraph("Prioritised Recommendations", h2_style))
        rec_data = [["#", "Priority", "Category", "Recommended Action"]]
        P_COLORS = {"High": colors.HexColor('#fee2e2'), "Medium": colors.HexColor('#fef3c7'), "Low": colors.HexColor('#d1fae5')}
        for i, r in enumerate(recs[:15], 1):
            rec_data.append([str(i), r["priority"], r["category"].split(" ", 1)[1][:20], r["advice"]])
        rec_table = Table(rec_data, colWidths=[0.7*cm, 2*cm, 4.3*cm, 10*cm])
        style_cmds = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1d4ed8')),
            ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
            ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',   (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]
        for i, r in enumerate(recs[:15], 1):
            style_cmds.append(('BACKGROUND', (1,i), (1,i), P_COLORS.get(r["priority"], colors.white)))
        rec_table.setStyle(TableStyle(style_cmds))
        story.append(rec_table)

    story.append(Spacer(1, 0.6*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "Generated by WorkSafe Pro | Based on ISO 9241 Ergonomics Standards & OSHA Guidelines | Not a substitute for professional ergonomic assessment",
        small_style))
    doc.build(story)
    buffer.seek(0)
    return buffer

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
if "user" not in st.session_state:       st.session_state.user = None
if "admin" not in st.session_state:      st.session_state.admin = None
if "responses" not in st.session_state:  st.session_state.responses = {}
if "result" not in st.session_state:     st.session_state.result = None

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 0.5rem;'>
        <div style='font-family:Syne,sans-serif; font-size:1.4rem; font-weight:800; color:#e0f2fe;'>
            🏥 WorkSafe Pro
        </div>
        <div style='font-size:0.75rem; color:#7dd3fc; margin-top:2px;'>
            Ergonomics & Safety Scorer
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    if st.session_state.user:
        st.markdown(f"**👤 {st.session_state.user['full_name']}**")
        st.markdown(f"<span style='font-size:0.8rem;color:#94a3b8;'>{st.session_state.user['department']}</span>", unsafe_allow_html=True)
        st.markdown("---")
        nav = st.radio("Navigate", ["🏠 Dashboard", "📋 New Assessment", "📊 My History", "⬇️ Download Report"])
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.user = None
            st.session_state.result = None
            st.rerun()
    elif st.session_state.admin:
        st.markdown("**🛡️ Admin Panel**")
        st.markdown("---")
        nav = st.radio("Navigate", ["📊 Overview", "👥 Users", "📋 All Assessments"])
        st.markdown("---")
        if st.button("🚪 Admin Logout"):
            st.session_state.admin = None
            st.rerun()
    else:
        nav = st.radio("Navigate", ["🏠 Home", "🔑 Login", "📝 Register", "🛡️ Admin"])

    st.markdown("""
    <div style='position:absolute;bottom:1rem;left:0;right:0;text-align:center;font-size:0.72rem;color:#475569;'>
        v2.0 · ICT Health & Ergonomics<br>ISO 9241 · OSHA Standards
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGES — PUBLIC
# ─────────────────────────────────────────────
if not st.session_state.user and not st.session_state.admin and nav == "🏠 Home":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">WorkSafe Pro 2.0</div>
        <div class="hero-sub">Advanced ICT Workstation Ergonomics & Safety Assessment Platform</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    for col, (val, lbl, icon) in zip([col1,col2,col3,col4], [
        ("35","Assessment Questions","📋"),
        ("7","Evaluation Categories","🗂️"),
        ("ISO 9241","Ergonomics Standard","✅"),
        ("PDF","Professional Reports","📄"),
    ]):
        col.markdown(f"""<div class="metric-tile"><div style="font-size:1.8rem">{icon}</div>
        <div class="val">{val}</div><div class="lbl">{lbl}</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-card"><div class="section-title">🎯 Assessment Domains</div>', unsafe_allow_html=True)
        for cat in CATEGORIES:
            st.markdown(f"• {cat}")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="section-card">
            <div class="section-title">⚙️ Key Features</div>
            <ul style="color:#374151;font-size:0.88rem;line-height:2;">
                <li>Weighted 5-point Likert scale scoring</li>
                <li>Real-time radar + bar chart visualisation</li>
                <li>AI-driven priority recommendations</li>
                <li>Trend tracking across sessions</li>
                <li>Downloadable professional PDF report</li>
                <li>Admin analytics dashboard</li>
                <li>Department benchmarking</li>
            </ul>
        </div>""", unsafe_allow_html=True)

elif not st.session_state.user and not st.session_state.admin and nav == "🔑 Login":
    st.markdown('<div class="hero-banner"><div class="hero-title">Sign In</div></div>', unsafe_allow_html=True)
    col, _ = st.columns([1.2, 1])
    with col:
        with st.form("login_form"):
            uname = st.text_input("Username")
            pw    = st.text_input("Password", type="password")
            sub   = st.form_submit_button("Sign In →")
        if sub:
            u = login_user(uname, pw)
            if u:
                st.session_state.user = u
                st.success(f"Welcome back, {u['full_name']}!")
                st.rerun()
            else:
                st.error("Invalid credentials.")

elif not st.session_state.user and not st.session_state.admin and nav == "📝 Register":
    st.markdown('<div class="hero-banner"><div class="hero-title">Create Account</div></div>', unsafe_allow_html=True)
    col, _ = st.columns([1.2, 1])
    with col:
        with st.form("reg_form"):
            fn   = st.text_input("Full Name")
            un   = st.text_input("Username")
            dept = st.selectbox("Department", ["ICT / IT","Administration","Healthcare","Education","Engineering","Finance","HR","Other"])
            pw1  = st.text_input("Password", type="password")
            pw2  = st.text_input("Confirm Password", type="password")
            sub  = st.form_submit_button("Create Account →")
        if sub:
            if pw1 != pw2:       st.error("Passwords do not match.")
            elif len(pw1) < 6:   st.error("Password must be at least 6 characters.")
            elif not fn or not un: st.error("All fields are required.")
            elif register_user(un, pw1, fn, dept): st.success("Account created! Please log in.")
            else: st.error("Username already taken.")

elif not st.session_state.user and not st.session_state.admin and nav == "🛡️ Admin":
    st.markdown('<div class="hero-banner"><div class="hero-title">Admin Login</div></div>', unsafe_allow_html=True)
    col, _ = st.columns([1.2, 1])
    with col:
        with st.form("admin_form"):
            au = st.text_input("Admin Username")
            ap = st.text_input("Admin Password", type="password")
            s  = st.form_submit_button("Admin Sign In →")
        if s:
            a = login_admin(au, ap)
            if a:
                st.session_state.admin = a
                st.success("Admin access granted.")
                st.rerun()
            else:
                st.error("Invalid admin credentials.")
        st.caption("Default: admin / admin123")

# ─────────────────────────────────────────────
#  PAGES — AUTHENTICATED USER
# ─────────────────────────────────────────────
elif st.session_state.user:
    user = st.session_state.user

    if nav == "🏠 Dashboard":
        st.markdown(f"""
        <div class="hero-banner">
            <div class="hero-title">Welcome, {user['full_name'].split()[0]} 👋</div>
            <div class="hero-sub">Your Ergonomics & Safety Dashboard · {user['department']}</div>
        </div>""", unsafe_allow_html=True)

        history = get_user_history(user["id"])
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"""<div class="metric-tile"><div class="val">{len(history)}</div><div class="lbl">Total Assessments</div></div>""", unsafe_allow_html=True)
        if history:
            last_score = history[0]["total_score"]
            rl, _, icon = get_risk_level(last_score)
            c2.markdown(f"""<div class="metric-tile"><div class="val">{last_score:.0f}%</div><div class="lbl">Latest Score</div></div>""", unsafe_allow_html=True)
            c3.markdown(f"""<div class="metric-tile"><div class="val">{icon} {rl}</div><div class="lbl">Risk Level</div></div>""", unsafe_allow_html=True)

            df = pd.DataFrame([{"Date": h["created_at"][:10], "Score": h["total_score"]} for h in history])
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["Date"], y=df["Score"],
                mode="lines+markers",
                line=dict(color="#1d4ed8", width=3),
                marker=dict(size=8, color="#3b82f6"),
                fill="tozeroy", fillcolor="rgba(59,130,246,0.08)"
            ))
            fig.add_hline(y=80, line_dash="dash", line_color="#10b981", annotation_text="Excellent (80+)")
            fig.add_hline(y=65, line_dash="dash", line_color="#f59e0b", annotation_text="Good (65+)")
            fig.update_layout(title="Score History", paper_bgcolor="white", plot_bgcolor="#f8fafc",
                              yaxis=dict(range=[0,105], title="Score (%)"),
                              height=300, margin=dict(l=20,r=20,t=40,b=20), font=dict(family="DM Sans"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            c2.markdown("""<div class="metric-tile"><div class="val">—</div><div class="lbl">Latest Score</div></div>""", unsafe_allow_html=True)
            c3.markdown("""<div class="metric-tile"><div class="val">—</div><div class="lbl">Risk Level</div></div>""", unsafe_allow_html=True)
            st.info("No assessments yet. Go to **New Assessment** to get started!")

    elif nav == "📋 New Assessment":
        st.markdown("""
        <div class="hero-banner">
            <div class="hero-title">📋 New Assessment</div>
            <div class="hero-sub">Rate each criterion: 1 (Never) → 5 (Always / Fully)</div>
        </div>""", unsafe_allow_html=True)

        with st.form("assessment_form"):
            all_responses = {}
            tabs = st.tabs(list(CATEGORIES.keys()))
            for tab, (cat_name, cat_data) in zip(tabs, CATEGORIES.items()):
                with tab:
                    for q in cat_data["questions"]:
                        st.markdown(f"""
                        <div class="q-card">
                            <div class="q-label">{q['text']}</div>
                            <div class="q-weight">Weight: {q['weight']}/10</div>
                        </div>""", unsafe_allow_html=True)
                        val = st.select_slider(
                            " ", options=list(SCALE_LABELS.keys()),
                            format_func=lambda x: f"{x} — {SCALE_LABELS[x]}",
                            value=3, key=f"q_{q['id']}"
                        )
                        all_responses[q["id"]] = val
            submitted = st.form_submit_button("🚀 Calculate Safety Score", use_container_width=True)

        if submitted:
            total, cat_scores = compute_scores(all_responses)
            rl, badge_cls, icon = get_risk_level(total)
            recs = generate_recommendations(cat_scores, all_responses)
            save_assessment(user["id"], user["username"], user["department"],
                            all_responses, total, rl, recs)
            st.session_state.result = {"total": total, "cat_scores": cat_scores,
                                       "risk": rl, "recs": recs, "responses": all_responses}
            st.success("Assessment saved!")
            st.rerun()

        if st.session_state.result:
            r = st.session_state.result
            rl, badge_cls, _ = get_risk_level(r["total"])
            icon = "🟢" if rl=="Excellent" else "🔵" if rl=="Good" else "🟡" if rl=="Moderate" else "🔴"
            st.markdown("---")
            st.markdown("## 📊 Results")

            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown(f"""
                <div style="text-align:center;padding:2rem 1rem;">
                    <div class="score-badge {badge_cls}">{r['total']:.1f}</div>
                    <div style="margin-top:0.8rem;font-size:1.1rem;font-weight:600;color:#374151;">{icon} {rl}</div>
                    <div style="font-size:0.8rem;color:#94a3b8;margin-top:0.3rem;">out of 100</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                cats = list(r["cat_scores"].keys())
                vals = list(r["cat_scores"].values())
                fig = go.Figure(go.Scatterpolar(
                    r=vals+[vals[0]],
                    theta=[c.split(" ",1)[1] for c in cats]+[cats[0].split(" ",1)[1]],
                    fill="toself", fillcolor="rgba(29,78,216,0.15)",
                    line=dict(color="#1d4ed8", width=2), marker=dict(size=6),
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(range=[0,100])),
                    paper_bgcolor="white", height=320,
                    margin=dict(l=30,r=30,t=30,b=30),
                    font=dict(family="DM Sans"), title="Category Radar"
                )
                st.plotly_chart(fig, use_container_width=True)

            fig2 = go.Figure(go.Bar(
                x=[c.split(" ",1)[1] for c in cats], y=vals,
                marker_color=["#10b981" if v>=80 else "#3b82f6" if v>=65 else "#f59e0b" if v>=45 else "#ef4444" for v in vals],
                text=[f"{v:.0f}%" for v in vals], textposition="outside"
            ))
            fig2.update_layout(title="Category Scores", yaxis=dict(range=[0,115]),
                               paper_bgcolor="white", plot_bgcolor="#f8fafc",
                               height=280, margin=dict(l=10,r=10,t=40,b=80),
                               font=dict(family="DM Sans"), xaxis_tickangle=-30)
            st.plotly_chart(fig2, use_container_width=True)

            if r["recs"]:
                st.markdown("### 🎯 Recommendations")
                for rec in r["recs"][:12]:
                    rc = "risk-high" if rec["priority"]=="High" else "risk-medium" if rec["priority"]=="Medium" else "risk-low"
                    st.markdown(f"""
                    <div class="section-card" style="padding:0.8rem 1rem;margin-bottom:0.6rem;">
                        <span class="{rc}">{rec['priority']}</span>&nbsp;
                        <span style="font-size:0.8rem;color:#64748b;">{rec['category']}</span><br>
                        <span style="font-size:0.9rem;color:#1e293b;">{rec['advice']}</span>
                    </div>""", unsafe_allow_html=True)

    elif nav == "📊 My History":
        st.markdown('<div class="hero-banner"><div class="hero-title">📊 History</div></div>', unsafe_allow_html=True)
        history = get_user_history(user["id"])
        if not history:
            st.info("No assessments recorded yet.")
        else:
            df = pd.DataFrame([{"Date": h["created_at"][:16], "Score (%)": h["total_score"], "Risk Level": h["risk_level"]} for h in history])
            st.dataframe(df, use_container_width=True, hide_index=True)
            if len(history) >= 2:
                fig = go.Figure(go.Bar(
                    x=df["Date"], y=df["Score (%)"],
                    marker_color=["#10b981" if s>=80 else "#3b82f6" if s>=65 else "#f59e0b" if s>=45 else "#ef4444" for s in df["Score (%)"]],
                    text=df["Score (%)"].apply(lambda x: f"{x:.1f}%"), textposition="outside"
                ))
                fig.update_layout(title="All Scores", yaxis=dict(range=[0,115]),
                                  paper_bgcolor="white", plot_bgcolor="#f8fafc",
                                  height=320, font=dict(family="DM Sans"), xaxis_tickangle=-30)
                st.plotly_chart(fig, use_container_width=True)

    elif nav == "⬇️ Download Report":
        st.markdown('<div class="hero-banner"><div class="hero-title">⬇️ Download Report</div></div>', unsafe_allow_html=True)
        history = get_user_history(user["id"])
        if not history:
            st.info("No assessments found. Complete an assessment first.")
        else:
            options = {f"{h['created_at'][:16]} — Score: {h['total_score']:.1f}% ({h['risk_level']})": h for h in history}
            choice  = st.selectbox("Select Assessment", list(options.keys()))
            chosen  = options[choice]
            responses = json.loads(chosen["scores_json"])
            _, cat_scores = compute_scores(responses)
            recs = json.loads(chosen["recommendations_json"])
            if st.button("📄 Generate PDF Report"):
                with st.spinner("Building PDF..."):
                    buf = build_pdf_report(user["full_name"], user["department"],
                                           chosen["total_score"], chosen["risk_level"],
                                           cat_scores, recs, chosen["created_at"][:10])
                st.download_button("⬇️ Download PDF", data=buf,
                                   file_name=f"worksafe_report_{chosen['created_at'][:10]}.pdf",
                                   mime="application/pdf")

# ─────────────────────────────────────────────
#  PAGES — ADMIN
# ─────────────────────────────────────────────
elif st.session_state.admin:
    if nav == "📊 Overview":
        st.markdown('<div class="hero-banner"><div class="hero-title">🛡️ Admin Overview</div></div>', unsafe_allow_html=True)
        all_a = get_all_assessments()
        all_u = get_all_users()
        c1, c2, c3 = st.columns(3)
        avg = sum(a["total_score"] for a in all_a) / len(all_a) if all_a else 0
        c1.markdown(f"""<div class="metric-tile"><div class="val">{len(all_u)}</div><div class="lbl">Registered Users</div></div>""", unsafe_allow_html=True)
        c2.markdown(f"""<div class="metric-tile"><div class="val">{len(all_a)}</div><div class="lbl">Total Assessments</div></div>""", unsafe_allow_html=True)
        c3.markdown(f"""<div class="metric-tile"><div class="val">{avg:.1f}%</div><div class="lbl">Avg Score</div></div>""", unsafe_allow_html=True)
        if all_a:
            df = pd.DataFrame([{"Risk": a["risk_level"], "Dept": a["department"], "Score": a["total_score"]} for a in all_a])
            col1, col2 = st.columns(2)
            with col1:
                rc = df["Risk"].value_counts().reset_index()
                rc.columns = ["Risk Level","Count"]
                fig = px.pie(rc, values="Count", names="Risk Level",
                             color="Risk Level",
                             color_discrete_map={"Excellent":"#10b981","Good":"#3b82f6","Moderate":"#f59e0b","Poor":"#ef4444"},
                             title="Risk Distribution")
                fig.update_layout(paper_bgcolor="white", font=dict(family="DM Sans"), height=320)
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                da = df.groupby("Dept")["Score"].mean().reset_index()
                da.columns = ["Department","Average Score"]
                fig2 = px.bar(da, x="Department", y="Average Score", title="Avg Score by Dept",
                              color="Average Score",
                              color_continuous_scale=["#ef4444","#f59e0b","#3b82f6","#10b981"])
                fig2.update_layout(paper_bgcolor="white", plot_bgcolor="#f8fafc",
                                   font=dict(family="DM Sans"), height=320)
                st.plotly_chart(fig2, use_container_width=True)

    elif nav == "👥 Users":
        st.markdown('<div class="hero-banner"><div class="hero-title">👥 Users</div></div>', unsafe_allow_html=True)
        users = get_all_users()
        df = pd.DataFrame(users)[["username","full_name","department","created_at"]]
        df.columns = ["Username","Full Name","Department","Registered"]
        st.dataframe(df, use_container_width=True, hide_index=True)

    elif nav == "📋 All Assessments":
        st.markdown('<div class="hero-banner"><div class="hero-title">📋 All Assessments</div></div>', unsafe_allow_html=True)
        all_a = get_all_assessments()
        if all_a:
            df = pd.DataFrame([{"User":a["username"],"Dept":a["department"],"Score":f"{a['total_score']:.1f}%","Risk":a["risk_level"],"Date":a["created_at"][:16]} for a in all_a])
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button("⬇️ Export CSV", df.to_csv(index=False), "all_assessments.csv", "text/csv")

else:
    st.markdown('<div class="hero-banner"><div class="hero-title">Access Required</div><div class="hero-sub">Please log in or register to continue.</div></div>', unsafe_allow_html=True)
    st.info("Use the sidebar to **Login** or **Register**.")
