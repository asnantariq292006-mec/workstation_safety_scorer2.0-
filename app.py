import streamlit as st
import sqlite3
import hashlib
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER

st.set_page_config(
    page_title="ICT in Health and Ergonomics: Workstation Safety Scorer",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #0f172a;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; background: #f0f4f8; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060e1a 0%, #0d1f35 40%, #0a1628 100%);
    border-right: 2px solid rgba(56,189,248,0.2);
}
[data-testid="stSidebar"] * { color: #e2eaf4 !important; }
[data-testid="stSidebar"] .stRadio label {
    font-size: 0.93rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.2px;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(56,189,248,0.15) !important;
}

/* ── HERO BANNER ── */
.hero-banner {
    background: linear-gradient(135deg, #060e1a 0%, #0d2d4a 40%, #0a3d62 70%, #0d2d4a 100%);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 1.8rem;
    border: 1px solid rgba(56,189,248,0.25);
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(6,14,26,0.4), 0 4px 20px rgba(56,189,248,0.1);
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 340px; height: 340px;
    background: radial-gradient(circle, rgba(56,189,248,0.18) 0%, transparent 65%);
    border-radius: 50%;
}
.hero-banner::after {
    content: '';
    position: absolute;
    bottom: -50px; left: 30%;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 65%);
    border-radius: 50%;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 0.4rem;
    letter-spacing: -0.8px;
    text-shadow: 0 2px 20px rgba(56,189,248,0.3);
}
.hero-sub {
    color: #7dd3fc;
    font-size: 1rem;
    font-weight: 400;
    letter-spacing: 0.2px;
}
.hero-badge {
    display: inline-block;
    background: rgba(56,189,248,0.15);
    border: 1px solid rgba(56,189,248,0.3);
    color: #7dd3fc;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 3px 12px;
    border-radius: 20px;
    margin-top: 0.8rem;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* ── SECTION CARDS ── */
.section-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.2rem;
    border: 1px solid #dde4ef;
    box-shadow: 0 4px 24px rgba(15,23,42,0.07), 0 1px 4px rgba(15,23,42,0.04);
}
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 1rem;
}

/* ── SCORE BADGES ── */
.score-badge {
    display: inline-block;
    font-family: 'Syne', sans-serif;
    font-size: 3.8rem;
    font-weight: 800;
    padding: 0.6rem 1.8rem;
    border-radius: 16px;
    letter-spacing: -2px;
}
.badge-excellent { background: linear-gradient(135deg,#d1fae5,#a7f3d0); color:#064e3b; border:2px solid #6ee7b7; box-shadow:0 4px 20px rgba(16,185,129,0.2); }
.badge-good      { background: linear-gradient(135deg,#dbeafe,#bfdbfe); color:#1e3a8a; border:2px solid #93c5fd; box-shadow:0 4px 20px rgba(59,130,246,0.2); }
.badge-moderate  { background: linear-gradient(135deg,#fef3c7,#fde68a); color:#78350f; border:2px solid #fbbf24; box-shadow:0 4px 20px rgba(245,158,11,0.2); }
.badge-poor      { background: linear-gradient(135deg,#fee2e2,#fecaca); color:#7f1d1d; border:2px solid #f87171; box-shadow:0 4px 20px rgba(239,68,68,0.2); }

/* ── METRIC TILES ── */
.metric-tile {
    background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%);
    border-radius: 14px;
    padding: 1.4rem 1.2rem;
    text-align: center;
    border: 1px solid #c7def8;
    box-shadow: 0 4px 20px rgba(29,78,216,0.08);
    transition: transform 0.2s;
}
.metric-tile:hover { transform: translateY(-2px); }
.metric-tile .val {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #1e3a8a;
    line-height: 1.1;
}
.metric-tile .lbl {
    font-size: 0.75rem;
    color: #334155;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 4px;
}
.metric-tile .icon { font-size: 1.6rem; margin-bottom: 4px; }

/* ── QUESTION CARDS ── */
.q-card {
    background: linear-gradient(135deg, #f8fafc 0%, #f0f6ff 100%);
    border-left: 5px solid #2563eb;
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.3rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 2px 8px rgba(37,99,235,0.07);
}
.q-label {
    font-size: 0.93rem;
    color: #0f172a;
    font-weight: 600;
    line-height: 1.4;
}
.q-weight {
    font-size: 0.75rem;
    color: #475569;
    font-weight: 500;
    margin-top: 3px;
}

/* ── RISK TAGS ── */
.risk-high   { background:#fef2f2; color:#7f1d1d; padding:3px 12px; border-radius:20px; font-size:0.78rem; font-weight:700; border:1px solid #fca5a5; }
.risk-medium { background:#fffbeb; color:#78350f; padding:3px 12px; border-radius:20px; font-size:0.78rem; font-weight:700; border:1px solid #fcd34d; }
.risk-low    { background:#f0fdf4; color:#14532d; padding:3px 12px; border-radius:20px; font-size:0.78rem; font-weight:700; border:1px solid #86efac; }

/* ── RECOMMENDATION CARD ── */
.rec-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.7rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 10px rgba(15,23,42,0.05);
}
.rec-text { font-size: 0.92rem; color: #0f172a; font-weight: 500; margin-top: 5px; line-height: 1.5; }
.rec-cat  { font-size: 0.78rem; color: #334155; font-weight: 600; margin-top: 2px; }

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 50%, #3b82f6 100%);
    color: white !important;
    border: none;
    border-radius: 10px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    padding: 0.65rem 1.6rem;
    transition: all 0.25s;
    letter-spacing: 0.2px;
    box-shadow: 0 4px 15px rgba(29,78,216,0.3);
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1e40af 0%, #1d4ed8 100%);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(29,78,216,0.4);
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: #e2e8f0;
    padding: 6px;
    border-radius: 12px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 0.88rem;
    color: #334155;
    padding: 7px 18px;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #1d4ed8 !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

/* ── FORM LABELS ── */
label { color: #0f172a !important; font-size: 0.9rem !important; font-weight: 600 !important; }
.stTextInput input, .stSelectbox select {
    border-radius: 8px !important;
    border: 1.5px solid #cbd5e1 !important;
    color: #0f172a !important;
    font-weight: 500 !important;
}
.stTextInput input:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.15) !important;
}

/* ── DATA TABLE ── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    border: 1px solid #dde4ef !important;
    overflow: hidden;
}

/* ── ALERTS ── */
.stSuccess { background: #f0fdf4 !important; border-left: 4px solid #22c55e !important; color: #14532d !important; }
.stError   { background: #fef2f2 !important; border-left: 4px solid #ef4444 !important; color: #7f1d1d !important; }
.stInfo    { background: #eff6ff !important; border-left: 4px solid #3b82f6 !important; color: #1e3a8a !important; }

/* ── DIVIDERS ── */
hr { border-color: #e2e8f0 !important; margin: 1.5rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── DATABASE ──────────────────────────────────
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

# ── ASSESSMENT FRAMEWORK ──────────────────────
CATEGORIES = {
    "🪑 Seating & Posture": {
        "color": "#2563eb",
        "questions": [
            {"id": "seat_height",  "text": "Chair height allows feet flat on floor / footrest",        "weight": 8},
            {"id": "lumbar",       "text": "Chair provides adequate lumbar (lower back) support",        "weight": 9},
            {"id": "seat_depth",   "text": "Seat depth supports thighs without pressure behind knees",  "weight": 7},
            {"id": "armrests",     "text": "Armrests allow relaxed shoulders (90° elbow angle)",        "weight": 6},
            {"id": "back_upright", "text": "Back remains upright (90–110° recline) during work",       "weight": 8},
        ]
    },
    "🖥️ Monitor & Display": {
        "color": "#7c3aed",
        "questions": [
            {"id": "monitor_dist",   "text": "Monitor at arm's length (50–70 cm) from eyes",           "weight": 8},
            {"id": "monitor_height", "text": "Top of screen at or slightly below eye level",            "weight": 9},
            {"id": "monitor_glare",  "text": "Screen free from glare and reflections",                 "weight": 7},
            {"id": "refresh_rate",   "text": "Display refresh rate ≥ 60 Hz; resolution clear",         "weight": 5},
            {"id": "dual_monitor",   "text": "If dual monitors: primary centred, secondary same height","weight": 4},
        ]
    },
    "⌨️ Keyboard & Mouse": {
        "color": "#059669",
        "questions": [
            {"id": "kb_position", "text": "Keyboard positioned so wrists are straight (neutral)",      "weight": 8},
            {"id": "mouse_close", "text": "Mouse adjacent to keyboard, same surface level",            "weight": 7},
            {"id": "wrist_rest",  "text": "Wrist rest used only during pauses, not while typing",      "weight": 5},
            {"id": "kb_tilt",     "text": "Keyboard tilt is low / flat to avoid wrist extension",      "weight": 6},
        ]
    },
    "💡 Lighting & Environment": {
        "color": "#d97706",
        "questions": [
            {"id": "ambient_light", "text": "Ambient lighting adequate (300–500 lux for office work)", "weight": 7},
            {"id": "no_flicker",    "text": "No flickering lights; lighting uniform across workspace", "weight": 6},
            {"id": "noise_level",   "text": "Background noise below 55 dB (acceptable for ICT work)", "weight": 6},
            {"id": "temperature",   "text": "Room temperature comfortable (20–24 °C) & ventilated",   "weight": 6},
            {"id": "air_quality",   "text": "Air quality good; no dust, fumes, or stale air",         "weight": 5},
        ]
    },
    "📐 Desk & Workspace Layout": {
        "color": "#dc2626",
        "questions": [
            {"id": "desk_height",   "text": "Desk height allows 90° elbow angle when typing",         "weight": 8},
            {"id": "reach_zone",    "text": "Frequently used items within primary reach zone (30 cm)", "weight": 7},
            {"id": "leg_clearance", "text": "Adequate leg clearance under desk (no obstructions)",    "weight": 6},
            {"id": "cable_mgmt",    "text": "Cables managed; no trip/entanglement hazards",           "weight": 5},
            {"id": "documents",     "text": "Document holder used for reference material (if needed)", "weight": 4},
        ]
    },
    "🧘 Work Habits & Breaks": {
        "color": "#0891b2",
        "questions": [
            {"id": "micro_breaks",  "text": "Micro-breaks taken every 30–45 min (stand/stretch)",     "weight": 9},
            {"id": "eye_breaks",    "text": "20-20-20 rule followed (every 20 min, look 20 ft, 20 s)","weight": 8},
            {"id": "posture_aware", "text": "Worker aware of posture and self-corrects during day",   "weight": 8},
            {"id": "hydration",     "text": "Water available and regularly consumed at workstation",   "weight": 5},
            {"id": "exercise",      "text": "Regular physical activity / ergonomic exercises practised","weight": 7},
        ]
    },
    "🧠 Psychosocial Factors": {
        "color": "#be185d",
        "questions": [
            {"id": "workload",         "text": "Workload is manageable within working hours",          "weight": 8},
            {"id": "job_control",      "text": "Worker has control over task pace and method",        "weight": 7},
            {"id": "social_support",   "text": "Good social support from colleagues/supervisors",     "weight": 6},
            {"id": "stress_level",     "text": "Stress levels are low to moderate (self-reported)",   "weight": 8},
            {"id": "digital_wellbeing","text": "Digital screen time managed; no tech-induced fatigue","weight": 7},
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

# ── CHART LAYOUT DEFAULTS ─────────────────────
CHART_FONT = dict(family="DM Sans", size=13, color="#0f172a")
CHART_BASE = dict(
    paper_bgcolor="#ffffff",
    plot_bgcolor="#f8fafc",
    font=CHART_FONT,
    margin=dict(l=20, r=20, t=50, b=20),
)

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
    return round((total_weighted / (total_weight * 5)) * 100, 1), category_scores

def get_risk_level(score):
    if score >= 80: return "Excellent", "badge-excellent", "🟢"
    if score >= 65: return "Good",      "badge-good",      "🔵"
    if score >= 45: return "Moderate",  "badge-moderate",  "🟡"
    return "Poor", "badge-poor", "🔴"

def bar_color(v):
    if v >= 80: return "#059669"
    if v >= 65: return "#2563eb"
    if v >= 45: return "#d97706"
    return "#dc2626"

def generate_recommendations(category_scores, responses):
    recs = []
    THRESHOLDS = {
        "🪑 Seating & Posture": {
            "seat_height":  ("Adjust chair height so feet rest flat on the floor or use a footrest.", "High"),
            "lumbar":       ("Add a lumbar support cushion or adjust built-in lumbar support.", "High"),
            "back_upright": ("Set reminders to correct posture every 30 minutes.", "Medium"),
        },
        "🖥️ Monitor & Display": {
            "monitor_height":("Raise monitor using a stand so top aligns with eye level.", "High"),
            "monitor_dist":  ("Move monitor to arm's-length distance (50–70 cm).", "High"),
            "monitor_glare": ("Reposition monitor perpendicular to windows; use anti-glare filter.", "Medium"),
        },
        "⌨️ Keyboard & Mouse": {
            "kb_position": ("Place keyboard so forearms are parallel to floor, wrists neutral.", "High"),
            "mouse_close": ("Move mouse adjacent to keyboard to reduce shoulder reach.", "Medium"),
        },
        "💡 Lighting & Environment": {
            "ambient_light": ("Install task lighting (300–500 lux) or adjust blind/curtain positions.", "Medium"),
            "noise_level":   ("Use acoustic panels or noise-cancelling headphones.", "Medium"),
            "temperature":   ("Adjust HVAC or use personal fan/heater within 20–24 °C range.", "Low"),
        },
        "📐 Desk & Workspace Layout": {
            "desk_height": ("Use a height-adjustable desk or monitor/keyboard risers.", "High"),
            "reach_zone":  ("Reorganise desktop: keep mouse, phone, stationery within 30 cm.", "Medium"),
            "cable_mgmt":  ("Use cable trays/clips to remove trip hazards under/around desk.", "Low"),
        },
        "🧘 Work Habits & Breaks": {
            "micro_breaks": ("Set a timer every 30–45 min to stand, stretch, or walk briefly.", "High"),
            "eye_breaks":   ("Follow the 20-20-20 rule; use a reminder app if needed.", "High"),
            "exercise":     ("Incorporate 10-min desk stretches and a 30-min walk into daily routine.", "Medium"),
        },
        "🧠 Psychosocial Factors": {
            "workload":         ("Discuss workload with supervisor; use task prioritisation matrix.", "High"),
            "stress_level":     ("Use mindfulness breaks, limit after-hours emails, consider counselling.", "High"),
            "digital_wellbeing":("Apply digital detox periods; enable blue-light filter after 6 PM.", "Medium"),
        },
    }
    for cat, q_map in THRESHOLDS.items():
        for qid, (advice, priority) in q_map.items():
            if responses.get(qid, 5) <= 2:
                recs.append({"category": cat, "advice": advice, "priority": priority})
    for cat, score in category_scores.items():
        if score < 50 and not any(r["category"] == cat for r in recs):
            recs.append({"category": cat,
                         "advice": f"Overall {cat.split(' ',1)[1]} score is low ({score}%). Schedule an ergonomic review.",
                         "priority": "Medium"})
    recs.sort(key=lambda x: {"High":0,"Medium":1,"Low":2}.get(x["priority"], 3))
    return recs

# ── PDF REPORT ────────────────────────────────
def build_pdf_report(username, department, total_score, risk_level, category_scores, recs, date_str):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('T', parent=styles['Title'], fontSize=18,
                                 textColor=colors.HexColor('#0f172a'),
                                 fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=2)
    sub_style   = ParagraphStyle('S', parent=styles['Normal'], fontSize=10,
                                 textColor=colors.HexColor('#334155'), alignment=TA_CENTER, spaceAfter=4)
    h2_style    = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12,
                                 textColor=colors.HexColor('#1e3a8a'),
                                 fontName='Helvetica-Bold', spaceBefore=14, spaceAfter=4)
    small_style = ParagraphStyle('Sm', parent=styles['Normal'], fontSize=8,
                                 textColor=colors.HexColor('#475569'))
    RISK_COLORS = {
        "Excellent": colors.HexColor('#064e3b'),
        "Good":      colors.HexColor('#1e3a8a'),
        "Moderate":  colors.HexColor('#78350f'),
        "Poor":      colors.HexColor('#7f1d1d'),
    }
    rc = RISK_COLORS.get(risk_level, colors.black)
    story = []

    story.append(Paragraph("ICT in Health and Ergonomics", title_style))
    story.append(Paragraph("Workstation Safety Scorer — Assessment Report", sub_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1d4ed8')))
    story.append(Spacer(1, 0.4*cm))

    meta_table = Table(
        [["Assessor:", username, "Date:", date_str],
         ["Department:", department, "Risk Level:", risk_level]],
        colWidths=[3*cm, 6*cm, 3*cm, 5*cm]
    )
    meta_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (1,0), (1,0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (1,1), (1,1), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (3,1), (3,1), rc),
        ('FONTNAME', (3,1), (3,1), 'Helvetica-Bold'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Overall Safety Score", h2_style))
    score_table = Table([[f"{total_score:.1f} / 100", risk_level]], colWidths=[4*cm, 6*cm])
    score_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (0,0), 26),
        ('TEXTCOLOR', (0,0), (0,0), rc),
        ('FONTNAME', (1,0), (1,0), 'Helvetica-Bold'), ('FONTSIZE', (1,0), (1,0), 14),
        ('TEXTCOLOR', (1,0), (1,0), rc),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 10), ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#eff6ff')),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#93c5fd')),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Category Breakdown", h2_style))
    cat_data = [["Category", "Score (%)", "Status"]]
    for cat, score in category_scores.items():
        status = "Excellent" if score>=80 else "Good" if score>=65 else "Moderate" if score>=45 else "Needs Attention"
        cat_data.append([cat, f"{score:.1f}%", status])
    cat_table = Table(cat_data, colWidths=[8*cm, 3.5*cm, 5.5*cm])
    cat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor('#0f172a')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f8fafc'), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(cat_table)
    story.append(Spacer(1, 0.5*cm))

    if recs:
        story.append(Paragraph("Prioritised Recommendations", h2_style))
        rec_data = [["#", "Priority", "Category", "Recommended Action"]]
        P_COLORS = {
            "High":   colors.HexColor('#fef2f2'),
            "Medium": colors.HexColor('#fffbeb'),
            "Low":    colors.HexColor('#f0fdf4'),
        }
        for i, r in enumerate(recs[:15], 1):
            rec_data.append([str(i), r["priority"], r["category"].split(" ",1)[1][:20], r["advice"]])
        rec_table = Table(rec_data, colWidths=[0.7*cm, 2*cm, 4.3*cm, 10*cm])
        style_cmds = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor('#0f172a')),
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
        "Generated by ICT in Health and Ergonomics: Workstation Safety Scorer | ISO 9241 & OSHA Guidelines | Not a substitute for professional ergonomic assessment",
        small_style))
    doc.build(story)
    buffer.seek(0)
    return buffer

# ── SESSION STATE ─────────────────────────────
if "user"      not in st.session_state: st.session_state.user      = None
if "admin"     not in st.session_state: st.session_state.admin     = None
if "responses" not in st.session_state: st.session_state.responses = {}
if "result"    not in st.session_state: st.session_state.result    = None

# ── SIDEBAR ───────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1.2rem 0 0.8rem;'>
        <div style='font-size:2.2rem;margin-bottom:6px;'>🖥️</div>
        <div style='font-family:Syne,sans-serif;font-size:1rem;font-weight:800;color:#ffffff;line-height:1.4;'>
            ICT in Health<br>and Ergonomics
        </div>
        <div style='font-size:0.7rem;color:#7dd3fc;margin-top:6px;font-weight:500;letter-spacing:0.5px;text-transform:uppercase;'>
            Workstation Safety Scorer
        </div>
        <div style='width:40px;height:2px;background:linear-gradient(90deg,#38bdf8,#818cf8);border-radius:2px;margin:10px auto 0;'></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    if st.session_state.user:
        st.markdown(f"""
        <div style='background:rgba(56,189,248,0.1);border-radius:10px;padding:0.7rem 0.9rem;margin-bottom:0.8rem;border:1px solid rgba(56,189,248,0.2);'>
            <div style='font-size:0.75rem;color:#7dd3fc;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;'>Logged in as</div>
            <div style='font-size:0.95rem;font-weight:700;color:#ffffff;margin-top:2px;'>{st.session_state.user['full_name']}</div>
            <div style='font-size:0.78rem;color:#94a3b8;'>{st.session_state.user['department']}</div>
        </div>
        """, unsafe_allow_html=True)
        nav = st.radio("Navigate", ["🏠 Dashboard", "📋 New Assessment", "📊 My History", "⬇️ Download Report"])
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.result = None
            st.rerun()
    elif st.session_state.admin:
        st.markdown("""
        <div style='background:rgba(239,68,68,0.12);border-radius:10px;padding:0.7rem 0.9rem;margin-bottom:0.8rem;border:1px solid rgba(239,68,68,0.2);'>
            <div style='font-size:0.78rem;color:#fca5a5;font-weight:600;'>🛡️ Admin Panel</div>
        </div>""", unsafe_allow_html=True)
        nav = st.radio("Navigate", ["📊 Overview", "👥 Users", "📋 All Assessments"])
        st.markdown("---")
        if st.button("🚪 Admin Logout", use_container_width=True):
            st.session_state.admin = None
            st.rerun()
    else:
        nav = st.radio("Navigate", ["🏠 Home", "🔑 Login", "📝 Register", "🛡️ Admin"])

    st.markdown("""
    <div style='position:absolute;bottom:1rem;left:0;right:0;text-align:center;'>
        <div style='font-size:0.68rem;color:#475569;line-height:1.6;'>
            ISO 9241 · OSHA Standards<br>
            <span style='color:#38bdf8;'>ICT Health & Ergonomics</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── PUBLIC PAGES ──────────────────────────────
if not st.session_state.user and not st.session_state.admin and nav == "🏠 Home":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">ICT in Health and Ergonomics</div>
        <div class="hero-sub">Workstation Safety Scorer — Advanced Assessment Platform</div>
        <div class="hero-badge">ISO 9241 · OSHA Aligned · Evidence-Based</div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    for col, (val, lbl, icon) in zip(cols, [
        ("35","Assessment Questions","📋"),
        ("7","Evaluation Categories","🗂️"),
        ("ISO 9241","Ergonomics Standard","✅"),
        ("PDF","Professional Reports","📄"),
    ]):
        col.markdown(f"""
        <div class="metric-tile">
            <div class="icon">{icon}</div>
            <div class="val">{val}</div>
            <div class="lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="section-card">
            <div class="section-title">🎯 Assessment Domains</div>
        """, unsafe_allow_html=True)
        for cat in CATEGORIES:
            st.markdown(f"<div style='padding:5px 0;font-size:0.92rem;color:#0f172a;font-weight:500;border-bottom:1px solid #f1f5f9;'>• {cat}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="section-card">
            <div class="section-title">⚙️ Platform Features</div>
            <div style="display:grid;gap:8px;">
                <div style="background:#eff6ff;border-radius:8px;padding:8px 12px;font-size:0.88rem;color:#1e3a8a;font-weight:600;">📊 Weighted 5-point Likert scale scoring</div>
                <div style="background:#f0fdf4;border-radius:8px;padding:8px 12px;font-size:0.88rem;color:#064e3b;font-weight:600;">📈 Real-time radar + bar chart visualisation</div>
                <div style="background:#fdf4ff;border-radius:8px;padding:8px 12px;font-size:0.88rem;color:#581c87;font-weight:600;">🎯 Priority-ranked recommendations</div>
                <div style="background:#fffbeb;border-radius:8px;padding:8px 12px;font-size:0.88rem;color:#78350f;font-weight:600;">📅 Trend tracking across sessions</div>
                <div style="background:#fff1f2;border-radius:8px;padding:8px 12px;font-size:0.88rem;color:#881337;font-weight:600;">📄 Downloadable PDF report</div>
                <div style="background:#f0f9ff;border-radius:8px;padding:8px 12px;font-size:0.88rem;color:#0c4a6e;font-weight:600;">🛡️ Admin analytics dashboard</div>
            </div>
        </div>""", unsafe_allow_html=True)

elif not st.session_state.user and not st.session_state.admin and nav == "🔑 Login":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">Sign In</div>
        <div class="hero-sub">ICT in Health and Ergonomics: Workstation Safety Scorer</div>
    </div>""", unsafe_allow_html=True)
    col, _ = st.columns([1.2, 1])
    with col:
        with st.form("login_form"):
            uname = st.text_input("Username")
            pw    = st.text_input("Password", type="password")
            sub   = st.form_submit_button("Sign In →", use_container_width=True)
        if sub:
            u = login_user(uname, pw)
            if u:
                st.session_state.user = u
                st.success(f"Welcome back, {u['full_name']}!")
                st.rerun()
            else:
                st.error("Invalid credentials.")

elif not st.session_state.user and not st.session_state.admin and nav == "📝 Register":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">Create Account</div>
        <div class="hero-sub">ICT in Health and Ergonomics: Workstation Safety Scorer</div>
    </div>""", unsafe_allow_html=True)
    col, _ = st.columns([1.2, 1])
    with col:
        with st.form("reg_form"):
            fn   = st.text_input("Full Name")
            un   = st.text_input("Username")
            dept = st.selectbox("Department", ["ICT / IT","Administration","Healthcare","Education","Engineering","Finance","HR","Other"])
            pw1  = st.text_input("Password", type="password")
            pw2  = st.text_input("Confirm Password", type="password")
            sub  = st.form_submit_button("Create Account →", use_container_width=True)
        if sub:
            if pw1 != pw2:         st.error("Passwords do not match.")
            elif len(pw1) < 6:     st.error("Password must be at least 6 characters.")
            elif not fn or not un: st.error("All fields are required.")
            elif register_user(un, pw1, fn, dept): st.success("Account created! Please log in.")
            else: st.error("Username already taken.")

elif not st.session_state.user and not st.session_state.admin and nav == "🛡️ Admin":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">Admin Login</div>
        <div class="hero-sub">ICT in Health and Ergonomics: Workstation Safety Scorer</div>
    </div>""", unsafe_allow_html=True)
    col, _ = st.columns([1.2, 1])
    with col:
        with st.form("admin_form"):
            au = st.text_input("Admin Username")
            ap = st.text_input("Admin Password", type="password")
            s  = st.form_submit_button("Admin Sign In →", use_container_width=True)
        if s:
            a = login_admin(au, ap)
            if a:
                st.session_state.admin = a
                st.success("Admin access granted.")
                st.rerun()
            else:
                st.error("Invalid admin credentials.")
        st.caption("Default: admin / admin123")

# ── AUTHENTICATED USER PAGES ──────────────────
elif st.session_state.user:
    user = st.session_state.user

    if nav == "🏠 Dashboard":
        st.markdown(f"""
        <div class="hero-banner">
            <div class="hero-title">Welcome, {user['full_name'].split()[0]} 👋</div>
            <div class="hero-sub">ICT in Health and Ergonomics: Workstation Safety Scorer · {user['department']}</div>
        </div>""", unsafe_allow_html=True)

        history = get_user_history(user["id"])
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"""<div class="metric-tile"><div class="icon">📋</div><div class="val">{len(history)}</div><div class="lbl">Total Assessments</div></div>""", unsafe_allow_html=True)
        if history:
            ls = history[0]["total_score"]
            rl, _, icon = get_risk_level(ls)
            c2.markdown(f"""<div class="metric-tile"><div class="icon">📊</div><div class="val">{ls:.0f}%</div><div class="lbl">Latest Score</div></div>""", unsafe_allow_html=True)
            c3.markdown(f"""<div class="metric-tile"><div class="icon">{icon}</div><div class="val">{rl}</div><div class="lbl">Risk Level</div></div>""", unsafe_allow_html=True)
            df = pd.DataFrame([{"Date": h["created_at"][:10], "Score": h["total_score"]} for h in history])
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["Date"], y=df["Score"],
                mode="lines+markers",
                line=dict(color="#1d4ed8", width=3),
                marker=dict(size=9, color="#1d4ed8", line=dict(color="white", width=2)),
                fill="tozeroy",
                fillcolor="rgba(29,78,216,0.1)",
                name="Safety Score"
            ))
            fig.add_hline(y=80, line_dash="dash", line_color="#059669", line_width=1.5,
                          annotation_text="Excellent (80+)", annotation_font_color="#059669",
                          annotation_font_size=12)
            fig.add_hline(y=65, line_dash="dash", line_color="#d97706", line_width=1.5,
                          annotation_text="Good (65+)", annotation_font_color="#d97706",
                          annotation_font_size=12)
            fig.update_layout(
                title=dict(text="Score History Over Time", font=dict(size=16, color="#0f172a", family="DM Sans"), x=0.01),
                yaxis=dict(range=[0,110], title="Score (%)", title_font=dict(color="#0f172a", size=13),
                           tickfont=dict(color="#0f172a", size=12), gridcolor="#e2e8f0"),
                xaxis=dict(title="Date", title_font=dict(color="#0f172a", size=13),
                           tickfont=dict(color="#0f172a", size=12), gridcolor="#e2e8f0"),
                height=320, **CHART_BASE
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            c2.markdown("""<div class="metric-tile"><div class="icon">📊</div><div class="val">—</div><div class="lbl">Latest Score</div></div>""", unsafe_allow_html=True)
            c3.markdown("""<div class="metric-tile"><div class="icon">⚠️</div><div class="val">—</div><div class="lbl">Risk Level</div></div>""", unsafe_allow_html=True)
            st.info("No assessments yet. Go to **New Assessment** to get started!")

    elif nav == "📋 New Assessment":
        st.markdown("""
        <div class="hero-banner">
            <div class="hero-title">📋 New Assessment</div>
            <div class="hero-sub">ICT in Health and Ergonomics: Workstation Safety Scorer · Rate each criterion 1 (Never) → 5 (Always)</div>
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
                            <div class="q-weight">⚖️ Weight: {q['weight']}/10</div>
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
            st.success("✅ Assessment saved successfully!")
            st.rerun()

        if st.session_state.result:
            r = st.session_state.result
            rl, badge_cls, _ = get_risk_level(r["total"])
            icon = "🟢" if rl=="Excellent" else "🔵" if rl=="Good" else "🟡" if rl=="Moderate" else "🔴"

            st.markdown("---")
            st.markdown("""
            <div style="font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:800;color:#0f172a;margin-bottom:1rem;">
                📊 Assessment Results
            </div>""", unsafe_allow_html=True)

            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#f8fafc,#eff6ff);border-radius:16px;padding:2rem 1rem;text-align:center;border:1px solid #dde4ef;box-shadow:0 4px 20px rgba(15,23,42,0.08);">
                    <div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#334155;margin-bottom:0.8rem;">Overall Score</div>
                    <div class="score-badge {badge_cls}">{r['total']:.1f}</div>
                    <div style="margin-top:0.8rem;font-size:1.15rem;font-weight:700;color:#0f172a;">{icon} {rl}</div>
                    <div style="font-size:0.82rem;color:#475569;margin-top:0.3rem;font-weight:500;">out of 100 points</div>
                </div>""", unsafe_allow_html=True)

            with c2:
                cats = list(r["cat_scores"].keys())
                vals = list(r["cat_scores"].values())
                cat_colors = [cat_data["color"] for cat_data in CATEGORIES.values()]
                fig = go.Figure(go.Scatterpolar(
                    r=vals + [vals[0]],
                    theta=[c.split(" ",1)[1] for c in cats] + [cats[0].split(" ",1)[1]],
                    fill="toself",
                    fillcolor="rgba(29,78,216,0.12)",
                    line=dict(color="#1d4ed8", width=2.5),
                    marker=dict(size=7, color="#1d4ed8"),
                ))
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            range=[0, 100],
                            tickfont=dict(size=11, color="#0f172a"),
                            gridcolor="#cbd5e1",
                            linecolor="#94a3b8",
                        ),
                        angularaxis=dict(
                            tickfont=dict(size=11, color="#0f172a", family="DM Sans"),
                            linecolor="#94a3b8",
                        ),
                        bgcolor="#f8fafc",
                    ),
                    paper_bgcolor="#ffffff",
                    height=360,
                    margin=dict(l=40, r=40, t=50, b=40),
                    font=dict(family="DM Sans", size=12, color="#0f172a"),
                    title=dict(text="Category Radar Chart", font=dict(size=15, color="#0f172a", family="DM Sans"), x=0.5, xanchor="center"),
                )
                st.plotly_chart(fig, use_container_width=True)

            # Bar chart
            fig2 = go.Figure(go.Bar(
                x=[c.split(" ",1)[1] for c in cats],
                y=vals,
                marker=dict(
                    color=[bar_color(v) for v in vals],
                    line=dict(color="#ffffff", width=1.5),
                    opacity=0.92,
                ),
                text=[f"<b>{v:.0f}%</b>" for v in vals],
                textposition="outside",
                textfont=dict(size=13, color="#0f172a", family="DM Sans"),
            ))
            fig2.update_layout(
                title=dict(text="Category Score Breakdown", font=dict(size=15, color="#0f172a", family="DM Sans"), x=0.01),
                yaxis=dict(
                    range=[0, 120],
                    title="Score (%)",
                    title_font=dict(color="#0f172a", size=13),
                    tickfont=dict(color="#0f172a", size=12),
                    gridcolor="#e2e8f0",
                    zerolinecolor="#cbd5e1",
                ),
                xaxis=dict(
                    tickfont=dict(color="#0f172a", size=11, family="DM Sans"),
                    tickangle=-25,
                    linecolor="#cbd5e1",
                ),
                paper_bgcolor="#ffffff",
                plot_bgcolor="#f8fafc",
                height=340,
                margin=dict(l=20, r=20, t=50, b=100),
                font=dict(family="DM Sans", color="#0f172a"),
                bargap=0.35,
            )
            st.plotly_chart(fig2, use_container_width=True)

            if r["recs"]:
                st.markdown("""
                <div style="font-family:'Syne',sans-serif;font-size:1.2rem;font-weight:800;color:#0f172a;margin:1rem 0 0.8rem;">
                    🎯 Prioritised Recommendations
                </div>""", unsafe_allow_html=True)
                for rec in r["recs"][:12]:
                    rc_cls = "risk-high" if rec["priority"]=="High" else "risk-medium" if rec["priority"]=="Medium" else "risk-low"
                    st.markdown(f"""
                    <div class="rec-card">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span class="{rc_cls}">{rec['priority']}</span>
                            <span class="rec-cat">{rec['category']}</span>
                        </div>
                        <div class="rec-text">{rec['advice']}</div>
                    </div>""", unsafe_allow_html=True)

    elif nav == "📊 My History":
        st.markdown("""
        <div class="hero-banner">
            <div class="hero-title">📊 My History</div>
            <div class="hero-sub">ICT in Health and Ergonomics: Workstation Safety Scorer</div>
        </div>""", unsafe_allow_html=True)
        history = get_user_history(user["id"])
        if not history:
            st.info("No assessments recorded yet.")
        else:
            df = pd.DataFrame([{
                "Date": h["created_at"][:16],
                "Score (%)": h["total_score"],
                "Risk Level": h["risk_level"]
            } for h in history])
            st.dataframe(df, use_container_width=True, hide_index=True)
            if len(history) >= 2:
                fig = go.Figure(go.Bar(
                    x=df["Date"],
                    y=df["Score (%)"],
                    marker=dict(
                        color=[bar_color(s) for s in df["Score (%)"]],
                        line=dict(color="white", width=1.5),
                        opacity=0.9,
                    ),
                    text=[f"<b>{s:.1f}%</b>" for s in df["Score (%)"]],
                    textposition="outside",
                    textfont=dict(size=13, color="#0f172a"),
                ))
                fig.update_layout(
                    title=dict(text="All Assessment Scores", font=dict(size=15, color="#0f172a"), x=0.01),
                    yaxis=dict(range=[0,120], title="Score (%)",
                               title_font=dict(color="#0f172a", size=13),
                               tickfont=dict(color="#0f172a", size=12),
                               gridcolor="#e2e8f0"),
                    xaxis=dict(tickfont=dict(color="#0f172a", size=11), tickangle=-30),
                    paper_bgcolor="#ffffff", plot_bgcolor="#f8fafc",
                    height=340, margin=dict(l=20,r=20,t=50,b=100),
                    font=dict(family="DM Sans", color="#0f172a"),
                )
                st.plotly_chart(fig, use_container_width=True)

    elif nav == "⬇️ Download Report":
        st.markdown("""
        <div class="hero-banner">
            <div class="hero-title">⬇️ Download Report</div>
            <div class="hero-sub">ICT in Health and Ergonomics: Workstation Safety Scorer</div>
        </div>""", unsafe_allow_html=True)
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
                with st.spinner("Building PDF report..."):
                    buf = build_pdf_report(user["full_name"], user["department"],
                                           chosen["total_score"], chosen["risk_level"],
                                           cat_scores, recs, chosen["created_at"][:10])
                st.download_button("⬇️ Download PDF", data=buf,
                                   file_name=f"ICT_Ergonomics_Report_{chosen['created_at'][:10]}.pdf",
                                   mime="application/pdf")

# ── ADMIN PAGES ───────────────────────────────
elif st.session_state.admin:
    if nav == "📊 Overview":
        st.markdown("""
        <div class="hero-banner">
            <div class="hero-title">🛡️ Admin Overview</div>
            <div class="hero-sub">ICT in Health and Ergonomics: Workstation Safety Scorer</div>
        </div>""", unsafe_allow_html=True)
        all_a = get_all_assessments()
        all_u = get_all_users()
        avg = sum(a["total_score"] for a in all_a) / len(all_a) if all_a else 0
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"""<div class="metric-tile"><div class="icon">👥</div><div class="val">{len(all_u)}</div><div class="lbl">Registered Users</div></div>""", unsafe_allow_html=True)
        c2.markdown(f"""<div class="metric-tile"><div class="icon">📋</div><div class="val">{len(all_a)}</div><div class="lbl">Total Assessments</div></div>""", unsafe_allow_html=True)
        c3.markdown(f"""<div class="metric-tile"><div class="icon">📈</div><div class="val">{avg:.1f}%</div><div class="lbl">Avg Score</div></div>""", unsafe_allow_html=True)
        if all_a:
            df = pd.DataFrame([{"Risk": a["risk_level"], "Dept": a["department"], "Score": a["total_score"]} for a in all_a])
            col1, col2 = st.columns(2)
            with col1:
                rc = df["Risk"].value_counts().reset_index()
                rc.columns = ["Risk Level","Count"]
                fig = px.pie(rc, values="Count", names="Risk Level",
                             color="Risk Level",
                             color_discrete_map={"Excellent":"#059669","Good":"#2563eb","Moderate":"#d97706","Poor":"#dc2626"},
                             title="Risk Level Distribution")
                fig.update_traces(textfont=dict(size=13, color="#0f172a", family="DM Sans"))
                fig.update_layout(
                    paper_bgcolor="white",
                    font=dict(family="DM Sans", size=13, color="#0f172a"),
                    title=dict(font=dict(size=15, color="#0f172a")),
                    height=340,
                    legend=dict(font=dict(color="#0f172a", size=12))
                )
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                da = df.groupby("Dept")["Score"].mean().reset_index()
                da.columns = ["Department","Average Score"]
                fig2 = px.bar(da, x="Department", y="Average Score",
                              title="Avg Score by Department",
                              color="Average Score",
                              color_continuous_scale=["#dc2626","#d97706","#2563eb","#059669"])
                fig2.update_traces(textfont=dict(size=13, color="#0f172a"))
                fig2.update_layout(
                    paper_bgcolor="white", plot_bgcolor="#f8fafc",
                    font=dict(family="DM Sans", size=13, color="#0f172a"),
                    title=dict(font=dict(size=15, color="#0f172a")),
                    yaxis=dict(title_font=dict(color="#0f172a"), tickfont=dict(color="#0f172a", size=12), gridcolor="#e2e8f0"),
                    xaxis=dict(tickfont=dict(color="#0f172a", size=11), tickangle=-20),
                    height=340,
                    coloraxis_colorbar=dict(tickfont=dict(color="#0f172a"), title=dict(font=dict(color="#0f172a")))
                )
                st.plotly_chart(fig2, use_container_width=True)

    elif nav == "👥 Users":
        st.markdown("""
        <div class="hero-banner">
            <div class="hero-title">👥 Users</div>
            <div class="hero-sub">ICT in Health and Ergonomics: Workstation Safety Scorer</div>
        </div>""", unsafe_allow_html=True)
        users = get_all_users()
        df = pd.DataFrame(users)[["username","full_name","department","created_at"]]
        df.columns = ["Username","Full Name","Department","Registered"]
        st.dataframe(df, use_container_width=True, hide_index=True)

    elif nav == "📋 All Assessments":
        st.markdown("""
        <div class="hero-banner">
            <div class="hero-title">📋 All Assessments</div>
            <div class="hero-sub">ICT in Health and Ergonomics: Workstation Safety Scorer</div>
        </div>""", unsafe_allow_html=True)
        all_a = get_all_assessments()
        if all_a:
            df = pd.DataFrame([{
                "User": a["username"], "Dept": a["department"],
                "Score": f"{a['total_score']:.1f}%", "Risk": a["risk_level"],
                "Date": a["created_at"][:16]
            } for a in all_a])
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button("⬇️ Export CSV", df.to_csv(index=False),
                               "ICT_Ergonomics_Assessments.csv", "text/csv")
        else:
            st.info("No assessments yet.")

else:
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">ICT in Health and Ergonomics</div>
        <div class="hero-sub">Workstation Safety Scorer — Please log in or register to continue.</div>
    </div>""", unsafe_allow_html=True)
    st.info("Use the sidebar to **Login** or **Register**.")
