"""
╔══════════════════════════════════════════════════════════════════════╗
║     ICT in Health & Ergonomics: Workstation Safety Scorer v3.0      ║
║               UET Taxila — Engineering Department                    ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import sqlite3
import hashlib
import json
import os
import math
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
import io
import base64
import time

# ─────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Workstation Safety Scorer",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────────────────────────────
STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --bg:       #0B0F19;
    --panel:    rgba(255,255,255,0.04);
    --border:   rgba(0,240,255,0.18);
    --cyan:     #00F0FF;
    --cyan-dim: rgba(0,240,255,0.15);
    --white:    #FFFFFF;
    --silver:   #A0AEC0;
    --green:    #00FF94;
    --amber:    #FFB800;
    --red:      #FF4D6D;
    --purple:   #B48FFF;
}

/* ── Global reset ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--white) !important;
    font-family: 'Inter', sans-serif;
}
[data-testid="stSidebar"] {
    background: rgba(11,15,25,0.95) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none; }

/* ── Typography ── */
h1,h2,h3 { font-family: 'Orbitron', monospace !important; }
.rajdhani { font-family: 'Rajdhani', sans-serif; }

/* ── Glass card ── */
.glass-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    backdrop-filter: blur(20px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(0,240,255,0.1);
    margin-bottom: 16px;
    transition: box-shadow .3s;
}
.glass-card:hover {
    box-shadow: 0 0 30px rgba(0,240,255,0.12), inset 0 1px 0 rgba(0,240,255,0.2);
}

/* ── KPI metric cards ── */
.kpi-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px 24px;
    text-align: center;
    box-shadow: 0 0 20px rgba(0,240,255,0.08), inset 0 1px 0 rgba(255,255,255,0.05);
}
.kpi-value {
    font-family: 'Orbitron', monospace;
    font-size: 2.4rem;
    font-weight: 900;
    line-height: 1.1;
    text-shadow: 0 0 20px currentColor;
}
.kpi-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.72rem;
    letter-spacing: 3px;
    color: var(--silver);
    text-transform: uppercase;
    margin-top: 6px;
}
.kpi-sub {
    font-size: 0.75rem;
    color: var(--silver);
    margin-top: 4px;
}

/* ── Score badge ── */
.score-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 2px;
}
.badge-green  { background: rgba(0,255,148,0.15); color: var(--green);  border: 1px solid rgba(0,255,148,0.4);  }
.badge-amber  { background: rgba(255,184,0,0.15);  color: var(--amber);  border: 1px solid rgba(255,184,0,0.4);  }
.badge-red    { background: rgba(255,77,109,0.15);  color: var(--red);    border: 1px solid rgba(255,77,109,0.4); }

/* ── Section heading ── */
.section-heading {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.7rem;
    letter-spacing: 4px;
    color: var(--cyan);
    text-transform: uppercase;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(0,240,255,0.1);
}

/* ── Welcome banner ── */
.welcome-banner {
    background: linear-gradient(135deg, rgba(0,240,255,0.07) 0%, rgba(180,143,255,0.05) 100%);
    border: 1px solid rgba(0,240,255,0.2);
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.welcome-title {
    font-family: 'Orbitron', monospace;
    font-size: 1.7rem;
    font-weight: 900;
    color: var(--white);
}
.welcome-title span { color: var(--cyan); text-shadow: 0 0 20px var(--cyan); }
.welcome-sub {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.8rem;
    letter-spacing: 3px;
    color: var(--silver);
    margin-top: 6px;
}
.dot-pulse {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 8px var(--green);
    animation: pulse 2s infinite;
    vertical-align: middle;
    margin-right: 8px;
}
@keyframes pulse {
    0%,100% { opacity:1; transform:scale(1); }
    50%      { opacity:.4; transform:scale(1.6); }
}

/* ── Risk progress bar ── */
.risk-bar-wrap { background: rgba(255,255,255,0.06); border-radius: 4px; height: 6px; margin-top: 6px; }
.risk-bar-fill { height: 100%; border-radius: 4px; transition: width .6s ease; }

/* ── Inputs & Buttons ── */
div[data-testid="stRadio"] > label,
div[data-testid="stSelectbox"] label,
div[data-testid="stTextInput"] label,
div[data-testid="stPasswordInput"] label {
    color: var(--silver) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.78rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}
div[data-testid="stRadio"] div[role="radiogroup"] {
    display: flex; gap: 8px; flex-wrap: wrap;
}
.stButton > button {
    background: rgba(0,240,255,0.1) !important;
    border: 1px solid rgba(0,240,255,0.5) !important;
    color: var(--cyan) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    border-radius: 10px !important;
    padding: 10px 24px !important;
    transition: all .3s !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    background: rgba(0,240,255,0.2) !important;
    box-shadow: 0 0 20px rgba(0,240,255,0.25) !important;
    transform: translateY(-1px) !important;
}

/* ── Sidebar nav items ── */
.nav-item {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 16px; border-radius: 12px; cursor: pointer;
    border: 1px solid transparent; margin-bottom: 4px;
    font-family: 'Rajdhani', sans-serif; font-size: 0.82rem;
    font-weight: 600; letter-spacing: 2px; color: var(--silver);
    transition: all .3s;
}
.nav-item.active {
    background: rgba(0,240,255,0.1);
    border-color: rgba(0,240,255,0.35);
    color: var(--cyan);
}

/* ── Table ── */
.stDataFrame { background: var(--panel) !important; border-radius: 12px !important; }
thead tr th { background: rgba(0,240,255,0.08) !important; color: var(--cyan) !important; font-family: 'Rajdhani',sans-serif !important; letter-spacing: 2px !important; }

/* ── Divider ── */
hr { border-color: rgba(0,240,255,0.1) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: rgba(0,240,255,0.3); border-radius: 2px; }

/* ── Login card ── */
.login-wrap {
    max-width: 420px; margin: 60px auto;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(0,240,255,0.2);
    border-radius: 20px; padding: 40px;
    box-shadow: 0 0 60px rgba(0,240,255,0.1);
}

/* ── Question card ── */
.q-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 18px 22px; margin-bottom: 12px;
}
.q-number { font-family:'Orbitron',monospace; font-size:.65rem; color:var(--cyan); letter-spacing:3px; }
.q-text   { font-size:.95rem; color:var(--white); margin-top:4px; margin-bottom:12px; }
.q-weight { font-size:.7rem; color:var(--silver); }
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────────────────────────────
DB_PATH = "workstation_safety.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        username  TEXT UNIQUE NOT NULL,
        password  TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email     TEXT,
        dept      TEXT DEFAULT 'Engineering',
        role      TEXT DEFAULT 'user',
        created   TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS assessments (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER,
        username    TEXT,
        score       REAL,
        risk_level  TEXT,
        answers     TEXT,
        cat_scores  TEXT,
        notes       TEXT,
        created     TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS settings (
        key   TEXT PRIMARY KEY,
        value TEXT
    );
    """)
    # Seed admin
    admin_pw = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("""
        INSERT OR IGNORE INTO users (username,password,full_name,email,dept,role)
        VALUES ('admin',?,  'Administrator','admin@uet.edu.pk','IT','admin')
    """, (admin_pw,))
    # Seed demo user
    demo_pw = hashlib.sha256("demo123".encode()).hexdigest()
    c.execute("""
        INSERT OR IGNORE INTO users (username,password,full_name,email,dept,role)
        VALUES ('asnan',?,'Muhammad Asnan','asnan@uet.edu.pk','Engineering','user')
    """, (demo_pw,))
    conn.commit()
    conn.close()

init_db()

# ─────────────────────────────────────────────────────────────────────
# AUTH HELPERS
# ─────────────────────────────────────────────────────────────────────
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

def login_user(username, password):
    conn = get_conn()
    row = conn.execute(
        "SELECT id,username,full_name,dept,role FROM users WHERE username=? AND password=?",
        (username, hash_pw(password))
    ).fetchone()
    conn.close()
    if row:
        return {"id": row[0], "username": row[1], "full_name": row[2], "dept": row[3], "role": row[4]}
    return None

def register_user(username, password, full_name, email, dept):
    try:
        conn = get_conn()
        conn.execute(
            "INSERT INTO users (username,password,full_name,email,dept) VALUES (?,?,?,?,?)",
            (username, hash_pw(password), full_name, email, dept)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# ─────────────────────────────────────────────────────────────────────
# ASSESSMENT DATA
# ─────────────────────────────────────────────────────────────────────
QUESTIONS = [
    # (id, category, question_text, weight)
    (1,  "Chair & Posture",   "Is your chair height adjusted so your feet rest flat on the floor?",          15),
    (2,  "Chair & Posture",   "Does your chair provide adequate lumbar (lower-back) support?",              12),
    (3,  "Chair & Posture",   "Are your knees at approximately 90° while seated?",                         10),
    (4,  "Screen & Display",  "Is the top of your monitor at or slightly below eye level?",                 12),
    (5,  "Screen & Display",  "Is the viewing distance between 50–70 cm from your eyes?",                  10),
    (6,  "Screen & Display",  "Is the screen free from glare and reflections?",                            10),
    (7,  "Keyboard & Mouse",  "Are your wrists in a neutral (flat) position while typing?",                 12),
    (8,  "Keyboard & Mouse",  "Is your mouse within easy reach without stretching your arm?",               8),
    (9,  "Keyboard & Mouse",  "Are your elbows at roughly 90° and close to your body while typing?",        8),
    (10, "Lighting",          "Is ambient lighting adequate and not causing eye strain?",                   10),
    (11, "Lighting",          "Is direct sunlight or artificial light avoided on your screen?",              8),
    (12, "Environment",       "Is the room temperature comfortable (approx. 20–24 °C)?",                   8),
    (13, "Environment",       "Is background noise at an acceptable level for concentration?",              7),
    (14, "Work Habits",       "Do you take a short break every 45–60 minutes?",                            10),
    (15, "Work Habits",       "Do you perform light stretching or movement during breaks?",                  8),
    (16, "Work Habits",       "Do you blink regularly and look away from the screen periodically?",          7),
    (17, "Accessories",       "Do you use a document holder to avoid neck rotation when referencing?",       6),
    (18, "Accessories",       "Is a wrist rest available and used during keyboard/mouse use?",               6),
    (19, "Psychosocial",      "Do you feel comfortable with your current workload and stress level?",        8),
    (20, "Psychosocial",      "Is your workspace free from excessive clutter or disorganisation?",           5),
]

LIKERT = {
    "Never (0%)": 0,
    "Rarely (25%)": 1,
    "Sometimes (50%)": 2,
    "Often (75%)": 3,
    "Always (100%)": 4,
}

CATEGORIES = [
    "Chair & Posture", "Screen & Display", "Keyboard & Mouse",
    "Lighting", "Environment", "Work Habits", "Accessories", "Psychosocial",
]

CAT_ICONS = {
    "Chair & Posture":  "🪑",
    "Screen & Display": "🖥️",
    "Keyboard & Mouse": "⌨️",
    "Lighting":         "💡",
    "Environment":      "🌡️",
    "Work Habits":      "⏱️",
    "Accessories":      "🖱️",
    "Psychosocial":     "🧠",
}

CAT_COLORS = {
    "Chair & Posture":  "#00F0FF",
    "Screen & Display": "#B48FFF",
    "Keyboard & Mouse": "#00FF94",
    "Lighting":         "#FFB800",
    "Environment":      "#FF6B9D",
    "Work Habits":      "#7EB8FF",
    "Accessories":      "#FF9F43",
    "Psychosocial":     "#A29BFE",
}

RECOMMENDATIONS = {
    "Chair & Posture": [
        "Adjust chair height so feet are flat on the floor or on a footrest.",
        "Use a lumbar support cushion if your chair lacks built-in support.",
        "Set seat depth so there is a 2–3 finger gap behind your knees.",
    ],
    "Screen & Display": [
        "Position the monitor top at eye level — use a stand or adjust the arm.",
        "Maintain 50–70 cm distance; use larger font sizes if needed.",
        "Apply an anti-glare screen filter and angle the monitor away from windows.",
    ],
    "Keyboard & Mouse": [
        "Keep wrists straight and neutral — use a wrist rest only during pauses.",
        "Place the mouse directly beside the keyboard to minimise reaching.",
        "Consider a split or ergonomic keyboard if wrist discomfort persists.",
    ],
    "Lighting": [
        "Use indirect or diffused lighting; avoid overhead fluorescent directly above screen.",
        "Enable blue-light filtering software (e.g. f.lux) for evening work.",
        "Position desk perpendicular to windows to minimise glare.",
    ],
    "Environment": [
        "Use a space heater or fan to maintain 20–24 °C thermal comfort.",
        "Wear noise-cancelling headphones or use white-noise apps if noisy.",
        "Ensure adequate ventilation and periodic fresh-air circulation.",
    ],
    "Work Habits": [
        "Follow the 20-20-20 rule: every 20 min, look 20 ft away for 20 sec.",
        "Set a recurring 45-minute reminder to stand, stretch, and move.",
        "Perform shoulder rolls, neck tilts, and wrist circles during micro-breaks.",
    ],
    "Accessories": [
        "Use a document holder at the same height and distance as your monitor.",
        "A padded wrist rest reduces contact stress during mouse-intensive work.",
        "Consider a vertical mouse or trackball to reduce forearm rotation.",
    ],
    "Psychosocial": [
        "Use task-management tools (Trello, Notion) to reduce cognitive overload.",
        "Declutter your desk weekly; a tidy space reduces mental fatigue.",
        "Practice 5-minute mindfulness or breathing exercises between tasks.",
    ],
}

# ─────────────────────────────────────────────────────────────────────
# SCORING ENGINE
# ─────────────────────────────────────────────────────────────────────
def compute_scores(answers: dict):
    """answers = {question_id: likert_int (0-4)}"""
    total_weight = sum(q[3] for q in QUESTIONS)
    weighted_sum = sum(answers.get(q[0], 0) * q[3] for q in QUESTIONS)
    overall = round((weighted_sum / (4 * total_weight)) * 100, 1)

    cat_scores = {}
    for cat in CATEGORIES:
        qs = [q for q in QUESTIONS if q[1] == cat]
        w  = sum(q[3] for q in qs)
        s  = sum(answers.get(q[0], 0) * q[3] for q in qs)
        cat_scores[cat] = round((s / (4 * w)) * 100, 1) if w else 0

    return overall, cat_scores

def risk_label(score):
    if score >= 75: return "Low Risk",      "#00FF94", "✅"
    if score >= 50: return "Moderate Risk", "#FFB800", "⚠️"
    return           "High Risk",           "#FF4D6D", "🚨"

def risk_badge_class(score):
    if score >= 75: return "badge-green"
    if score >= 50: return "badge-amber"
    return "badge-red"

# ─────────────────────────────────────────────────────────────────────
# DATABASE I/O
# ─────────────────────────────────────────────────────────────────────
def save_assessment(user_id, username, score, risk, answers, cat_scores, notes=""):
    conn = get_conn()
    conn.execute(
        """INSERT INTO assessments (user_id,username,score,risk_level,answers,cat_scores,notes)
           VALUES (?,?,?,?,?,?,?)""",
        (user_id, username, score, risk,
         json.dumps(answers), json.dumps(cat_scores), notes)
    )
    conn.commit()
    conn.close()

def load_user_assessments(username):
    conn = get_conn()
    rows = conn.execute(
        "SELECT id,score,risk_level,cat_scores,notes,created FROM assessments WHERE username=? ORDER BY created DESC",
        (username,)
    ).fetchall()
    conn.close()
    return rows

def load_all_assessments():
    conn = get_conn()
    rows = conn.execute(
        "SELECT a.id,a.username,u.full_name,u.dept,a.score,a.risk_level,a.created "
        "FROM assessments a LEFT JOIN users u ON a.user_id=u.id ORDER BY a.created DESC"
    ).fetchall()
    conn.close()
    return rows

def load_all_users():
    conn = get_conn()
    rows = conn.execute(
        "SELECT id,username,full_name,email,dept,role,created FROM users ORDER BY created DESC"
    ).fetchall()
    conn.close()
    return rows

# ─────────────────────────────────────────────────────────────────────
# PDF REPORT GENERATOR
# ─────────────────────────────────────────────────────────────────────
def generate_pdf(user, score, risk, cat_scores, notes, timestamp):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ── Header ──
    pdf.set_fill_color(11, 15, 25)
    pdf.rect(0, 0, 210, 42, 'F')
    pdf.set_text_color(0, 240, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_xy(15, 10)
    pdf.cell(0, 8, "WORKSTATION SAFETY SCORER", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(160, 174, 192)
    pdf.set_x(15)
    pdf.cell(0, 6, "ICT in Health & Ergonomics  |  UET Taxila - Engineering", ln=True)
    pdf.set_x(15)
    pdf.cell(0, 5, f"Report Generated: {timestamp}", ln=True)

    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(15, 50)

    # ── User Info ──
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(235, 248, 255)
    pdf.cell(0, 8, "ASSESSMENT DETAILS", ln=True, fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_x(15)
    pdf.cell(60, 7, f"Name:       {user['full_name']}")
    pdf.cell(60, 7, f"Username:   {user['username']}", ln=True)
    pdf.set_x(15)
    pdf.cell(60, 7, f"Department: {user['dept']}")
    pdf.cell(60, 7, f"Date:       {timestamp[:10]}", ln=True)
    pdf.ln(4)

    # ── Overall Score ──
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(235, 248, 255)
    pdf.cell(0, 8, "OVERALL ERGONOMIC SCORE", ln=True, fill=True)
    pdf.set_font("Helvetica", "B", 28)
    r, g, b = (0,200,100) if score>=75 else (230,150,0) if score>=50 else (220,50,50)
    pdf.set_text_color(r, g, b)
    pdf.set_x(15)
    pdf.cell(0, 14, f"{score}%  —  {risk}", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)

    # ── Category Breakdown ──
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(235, 248, 255)
    pdf.cell(0, 8, "CATEGORY BREAKDOWN", ln=True, fill=True)
    pdf.set_font("Helvetica", "", 10)
    for cat, s in cat_scores.items():
        rl, _, _ = risk_label(s)
        pdf.set_x(15)
        pdf.cell(70, 7, f"{CAT_ICONS.get(cat,'')} {cat}")
        pdf.cell(20, 7, f"{s}%")
        pdf.cell(40, 7, rl, ln=True)

    pdf.ln(4)

    # ── Recommendations ──
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(235, 248, 255)
    pdf.cell(0, 8, "PERSONALISED RECOMMENDATIONS", ln=True, fill=True)
    pdf.set_font("Helvetica", "", 9)
    for cat, s in cat_scores.items():
        if s < 75:
            pdf.set_x(15)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 7, f"{CAT_ICONS.get(cat,'')} {cat}  ({s}%)", ln=True)
            pdf.set_font("Helvetica", "", 9)
            for rec in RECOMMENDATIONS.get(cat, []):
                pdf.set_x(20)
                pdf.multi_cell(0, 6, f"• {rec}")
            pdf.ln(2)

    # ── Notes ──
    if notes:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_fill_color(235, 248, 255)
        pdf.cell(0, 8, "ASSESSOR NOTES", ln=True, fill=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_x(15)
        pdf.multi_cell(0, 6, notes)

    # ── Footer ──
    pdf.set_y(-20)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(130, 130, 130)
    pdf.cell(0, 5, "Generated by Workstation Safety Scorer v3.0 | UET Taxila Engineering Dept", align="C")

    return bytes(pdf.output())

# ─────────────────────────────────────────────────────────────────────
# PLOTLY HELPERS
# ─────────────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Rajdhani, sans-serif", color="#A0AEC0"),
    margin=dict(l=20, r=20, t=30, b=20),
)

def radar_chart(cat_scores):
    cats  = list(cat_scores.keys())
    vals  = list(cat_scores.values())
    vals += vals[:1]; cats += cats[:1]
    fig = go.Figure(go.Scatterpolar(
        r=vals, theta=cats, fill="toself",
        fillcolor="rgba(0,240,255,0.1)",
        line=dict(color="#00F0FF", width=2),
        marker=dict(color="#00F0FF", size=6),
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0,100], gridcolor="rgba(0,240,255,0.15)", tickfont=dict(size=9)),
            angularaxis=dict(gridcolor="rgba(0,240,255,0.1)"),
        ),
        height=340,
    )
    return fig

def history_chart(rows):
    dates  = [r[5][:10] for r in rows][::-1]
    scores = [r[1] for r in rows][::-1]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=scores, mode="lines+markers",
        line=dict(color="#00F0FF", width=2.5, shape="spline"),
        marker=dict(color="#00F0FF", size=7, line=dict(width=2, color="#FFFFFF")),
        fill="tozeroy", fillcolor="rgba(0,240,255,0.07)",
        name="Score",
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=240,
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(range=[0,100], gridcolor="rgba(255,255,255,0.05)", ticksuffix="%"),
    )
    return fig

def category_bar(cat_scores):
    cats   = list(cat_scores.keys())
    vals   = list(cat_scores.values())
    colors = [CAT_COLORS.get(c, "#00F0FF") for c in cats]
    fig = go.Figure(go.Bar(
        x=vals, y=[f"{CAT_ICONS.get(c,'')} {c}" for c in cats],
        orientation="h",
        marker=dict(color=colors, opacity=0.85, line=dict(width=0)),
        text=[f"{v}%" for v in vals],
        textposition="outside",
        textfont=dict(color="#FFFFFF"),
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=360,
        xaxis=dict(range=[0,115], gridcolor="rgba(255,255,255,0.05)", ticksuffix="%"),
        yaxis=dict(autorange="reversed"),
    )
    return fig

def dept_bar(rows):
    df = pd.DataFrame(rows, columns=["id","username","name","dept","score","risk","created"])
    if df.empty: return None
    avg = df.groupby("dept")["score"].mean().reset_index()
    avg.columns = ["dept","avg_score"]
    fig = px.bar(avg, x="dept", y="avg_score",
        color="avg_score", color_continuous_scale=["#FF4D6D","#FFB800","#00FF94"],
        range_color=[0, 100], text_auto=".1f",
    )
    fig.update_traces(textfont_color="#FFFFFF")
    fig.update_layout(**PLOTLY_LAYOUT, height=300,
        coloraxis_showscale=False,
        xaxis_title="", yaxis=dict(range=[0,100], ticksuffix="%"),
    )
    return fig

# ─────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────────
for key, default in [
    ("logged_in", False), ("user", None),
    ("page", "dashboard"), ("answers", {}),
    ("assessment_done", False), ("last_score", None),
    ("last_cat_scores", None), ("last_risk", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────────────────────────────
# LOGIN / REGISTER PAGE
# ─────────────────────────────────────────────────────────────────────
def login_page():
    st.markdown("""
    <div style='text-align:center;margin-bottom:8px;'>
        <div style='font-family:Orbitron,monospace;font-size:1.6rem;font-weight:900;color:#00F0FF;text-shadow:0 0 30px #00F0FF;'>
            WSS
        </div>
        <div style='font-family:Rajdhani,sans-serif;font-size:.7rem;letter-spacing:4px;color:#A0AEC0;'>
            WORKSTATION SAFETY SCORER
        </div>
        <div style='font-family:Rajdhani,sans-serif;font-size:.62rem;letter-spacing:2px;color:#555;margin-top:4px;'>
            ICT IN HEALTH & ERGONOMICS · UET TAXILA
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_reg = st.tabs(["🔐  Sign In", "📝  Register"])

    with tab_login:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        uname = st.text_input("Username", placeholder="e.g. asnan", key="li_user")
        passw = st.text_input("Password", type="password", placeholder="••••••••", key="li_pass")
        col1, col2 = st.columns([2,1])
        with col1:
            if st.button("SIGN IN →", use_container_width=True):
                user = login_user(uname.strip(), passw)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.session_state.page = "dashboard"
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
        st.markdown("""
        <div style='margin-top:16px;padding:12px;background:rgba(0,240,255,0.05);
                    border:1px solid rgba(0,240,255,0.15);border-radius:10px;
                    font-family:Rajdhani,sans-serif;font-size:.78rem;color:#A0AEC0;'>
            <b style='color:#00F0FF;'>Demo accounts</b><br>
            User → <code>asnan</code> / <code>demo123</code><br>
            Admin → <code>admin</code> / <code>admin123</code>
        </div>
        """, unsafe_allow_html=True)

    with tab_reg:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        r_name = st.text_input("Full Name", key="r_name")
        r_user = st.text_input("Username", key="r_user")
        r_email= st.text_input("Email", key="r_email")
        r_dept = st.selectbox("Department", ["Engineering","Computer Science","Management","Sciences","Other"], key="r_dept")
        r_pw   = st.text_input("Password", type="password", key="r_pw")
        r_pw2  = st.text_input("Confirm Password", type="password", key="r_pw2")
        if st.button("CREATE ACCOUNT →", use_container_width=True):
            if not all([r_name,r_user,r_pw]):
                st.warning("Please fill in required fields.")
            elif r_pw != r_pw2:
                st.error("Passwords do not match.")
            elif len(r_pw) < 6:
                st.error("Password must be at least 6 characters.")
            elif register_user(r_user.strip(), r_pw, r_name.strip(), r_email.strip(), r_dept):
                st.success("Account created! Please sign in.")
            else:
                st.error("Username already exists.")

# ─────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────
def sidebar():
    u = st.session_state.user
    with st.sidebar:
        st.markdown(f"""
        <div style='padding:0 8px 20px;'>
            <div style='font-family:Orbitron,monospace;font-size:1.1rem;font-weight:900;
                        color:#00F0FF;text-shadow:0 0 20px #00F0FF;letter-spacing:2px;'>WSS</div>
            <div style='font-family:Rajdhani,sans-serif;font-size:.62rem;letter-spacing:3px;
                        color:#A0AEC0;'>ERGO·PLATFORM v3.0</div>
        </div>
        <div style='padding:12px 8px;border-top:1px solid rgba(0,240,255,0.1);
                    border-bottom:1px solid rgba(0,240,255,0.1);margin-bottom:16px;'>
            <div style='display:flex;align-items:center;gap:10px;'>
                <div style='width:38px;height:38px;border-radius:10px;
                            background:linear-gradient(135deg,rgba(0,240,255,0.3),rgba(180,143,255,0.2));
                            display:flex;align-items:center;justify-content:center;
                            font-size:1.1rem;border:1px solid rgba(0,240,255,0.3);'>
                    {u["full_name"][0].upper()}
                </div>
                <div>
                    <div style='font-weight:600;font-size:.88rem;color:#FFF;'>{u["full_name"]}</div>
                    <div style='font-size:.7rem;color:#A0AEC0;'>{u["dept"]} · {u["role"].upper()}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        pages = [
            ("dashboard",   "⬡", "Dashboard"),
            ("assessment",  "◈", "New Assessment"),
            ("history",     "📈", "My History"),
            ("analytics",   "◉", "Analytics"),
        ]
        if u["role"] == "admin":
            pages += [("admin", "🛡️", "Admin Panel")]

        for pid, icon, label in pages:
            active = "active" if st.session_state.page == pid else ""
            if st.button(f"{icon}  {label}", key=f"nav_{pid}",
                         use_container_width=True):
                st.session_state.page = pid
                st.session_state.assessment_done = False
                st.rerun()

        st.markdown("<div style='margin-top:auto;padding-top:20px;border-top:1px solid rgba(0,240,255,0.08);'>", unsafe_allow_html=True)
        if st.button("⏻  Sign Out", use_container_width=True):
            for k in ["logged_in","user","page","answers","assessment_done",
                      "last_score","last_cat_scores","last_risk"]:
                st.session_state[k] = False if k == "logged_in" else None if k == "user" else (
                    "dashboard" if k == "page" else {} if k == "answers" else False if k == "assessment_done" else None
                )
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────────────────────────────
def page_dashboard():
    u = st.session_state.user
    rows = load_user_assessments(u["username"])

    # ── Welcome Banner ──
    latest_score = rows[0][1] if rows else None
    risk_str, risk_color, risk_icon = risk_label(latest_score) if latest_score else ("No Data","#A0AEC0","📋")
    trend = ""
    if len(rows) >= 2:
        diff = rows[0][1] - rows[1][1]
        trend = f"<span style='color:{'#00FF94' if diff>=0 else '#FF4D6D'};font-size:.8rem;'>{'▲' if diff>=0 else '▼'} {abs(diff):.1f}% vs last</span>"

    st.markdown(f"""
    <div class='welcome-banner'>
        <div class='welcome-title'>Welcome, <span>{u['full_name'].split()[0]}</span> 👋</div>
        <div class='welcome-sub'>
            <span class='dot-pulse'></span>
            ICT IN HEALTH & ERGONOMICS: WORKSTATION SAFETY SCORER · {u['dept'].upper()}
        </div>
        <div style='margin-top:14px;display:flex;gap:24px;flex-wrap:wrap;'>
            <div style='font-size:.85rem;color:#A0AEC0;'>
                Latest Score: <b style='color:{risk_color};font-size:1.1rem;font-family:Orbitron,monospace;'>
                {f"{latest_score:.1f}%" if latest_score else "—"}</b>
                &nbsp;{trend}
            </div>
            <div style='font-size:.85rem;color:#A0AEC0;'>
                Risk: <span style='color:{risk_color};font-weight:700;'>{risk_icon} {risk_str}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Row ──
    c1, c2, c3, c4 = st.columns(4)
    total = len(rows)
    avg   = round(sum(r[1] for r in rows)/total, 1) if rows else 0
    best  = max((r[1] for r in rows), default=0)
    high_risk = sum(1 for r in rows if r[2] == "High Risk")

    for col, val, label, color, sub in [
        (c1, total, "Total Assessments", "#00F0FF", "All time"),
        (c2, f"{avg}%", "Average Score",  "#B48FFF", "All sessions"),
        (c3, f"{best}%", "Best Score",    "#00FF94", "Personal peak"),
        (c4, high_risk, "High Risk",      "#FF4D6D", "Needs action"),
    ]:
        col.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-value' style='color:{color};'>{val}</div>
            <div class='kpi-label'>{label}</div>
            <div class='kpi-sub'>{sub}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Charts Row ──
    if rows:
        col_l, col_r = st.columns([1, 1.4])
        with col_l:
            st.markdown("<div class='section-heading'>ERGONOMIC RADAR</div>", unsafe_allow_html=True)
            latest_cat = json.loads(rows[0][3]) if rows else {}
            if latest_cat:
                st.plotly_chart(radar_chart(latest_cat), use_container_width=True, config={"displayModeBar": False})
        with col_r:
            st.markdown("<div class='section-heading'>SCORE HISTORY</div>", unsafe_allow_html=True)
            if len(rows) >= 2:
                st.plotly_chart(history_chart(rows), use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Complete at least 2 assessments to see the trend chart.")

        # ── Latest Category Breakdown ──
        st.markdown("<div class='section-heading'>LATEST CATEGORY BREAKDOWN</div>", unsafe_allow_html=True)
        if latest_cat:
            cols = st.columns(4)
            for i, (cat, s) in enumerate(latest_cat.items()):
                rl, rc, ri = risk_label(s)
                cols[i % 4].markdown(f"""
                <div class='kpi-card' style='margin-bottom:8px;'>
                    <div style='font-size:1.4rem;margin-bottom:4px;'>{CAT_ICONS.get(cat,'')}</div>
                    <div style='font-size:1.3rem;font-family:Orbitron,monospace;font-weight:700;color:{CAT_COLORS.get(cat,"#00F0FF")};'>{s}%</div>
                    <div class='kpi-label'>{cat}</div>
                    <span class='score-badge {risk_badge_class(s)}'>{rl}</span>
                    <div class='risk-bar-wrap'><div class='risk-bar-fill' style='width:{s}%;background:{CAT_COLORS.get(cat,"#00F0FF")};'></div></div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No assessments yet. Go to **New Assessment** to get started!")
        if st.button("🚀  START FIRST ASSESSMENT"):
            st.session_state.page = "assessment"
            st.rerun()


def page_assessment():
    st.markdown("<div class='section-heading'>NEW ERGONOMIC ASSESSMENT</div>", unsafe_allow_html=True)

    if st.session_state.assessment_done and st.session_state.last_score is not None:
        score     = st.session_state.last_score
        cat_sc    = st.session_state.last_cat_scores
        risk_str, risk_color, risk_icon = risk_label(score)

        st.markdown(f"""
        <div class='glass-card' style='text-align:center;padding:36px;'>
            <div style='font-size:.7rem;letter-spacing:4px;color:#A0AEC0;font-family:Rajdhani,sans-serif;'>ASSESSMENT COMPLETE</div>
            <div style='font-family:Orbitron,monospace;font-size:4rem;font-weight:900;
                        color:{risk_color};text-shadow:0 0 30px {risk_color};line-height:1;margin:12px 0;'>{score}%</div>
            <div style='color:{risk_color};font-family:Rajdhani,sans-serif;font-size:1.1rem;
                        font-weight:700;letter-spacing:3px;'>{risk_icon} {risk_str}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Recs ──
        st.markdown("<div class='section-heading'>PERSONALISED RECOMMENDATIONS</div>", unsafe_allow_html=True)
        low_cats = {c: s for c, s in cat_sc.items() if s < 75}
        if low_cats:
            for cat, s in sorted(low_cats.items(), key=lambda x: x[1]):
                rl, rc, ri = risk_label(s)
                with st.expander(f"{CAT_ICONS.get(cat,'')} {cat} — {s}%  {ri} {rl}"):
                    for rec in RECOMMENDATIONS.get(cat, []):
                        st.markdown(f"- {rec}")
        else:
            st.success("🎉 Excellent! All categories are in the low-risk zone.")

        # ── PDF Export ──
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        notes = st.text_area("Add notes (optional)", placeholder="Additional observations…")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾  Save Assessment"):
                save_assessment(
                    st.session_state.user["id"], st.session_state.user["username"],
                    score, risk_label(score)[0], st.session_state.answers, cat_sc, notes
                )
                st.success("Assessment saved successfully!")
        with col2:
            pdf_bytes = generate_pdf(
                st.session_state.user, score, risk_label(score)[0], cat_sc, notes,
                datetime.now().strftime("%Y-%m-%d %H:%M")
            )
            st.download_button(
                "📄  Download PDF Report", data=pdf_bytes,
                file_name=f"WSS_Report_{st.session_state.user['username']}_{datetime.now():%Y%m%d}.pdf",
                mime="application/pdf", use_container_width=True,
            )

        if st.button("↩  New Assessment"):
            st.session_state.assessment_done = False
            st.session_state.answers = {}
            st.rerun()
        return

    # ── Questions ──
    answers = {}
    st.markdown(f"""
    <div style='font-family:Rajdhani,sans-serif;color:#A0AEC0;font-size:.8rem;margin-bottom:20px;'>
        Answer all <b style='color:#00F0FF;'>20 questions</b> honestly based on your typical daily workstation setup.
        Each answer is weighted by ergonomic importance.
    </div>
    """, unsafe_allow_html=True)

    current_cat = None
    for q in QUESTIONS:
        if q[1] != current_cat:
            current_cat = q[1]
            st.markdown(f"""
            <div style='font-family:Rajdhani,sans-serif;font-size:.68rem;letter-spacing:4px;
                        color:{CAT_COLORS.get(current_cat,"#00F0FF")};text-transform:uppercase;
                        padding:10px 0 4px;border-top:1px solid rgba(255,255,255,0.05);margin-top:8px;'>
                {CAT_ICONS.get(current_cat,'')} {current_cat}
            </div>
            """, unsafe_allow_html=True)

        with st.container():
            st.markdown(f"""
            <div class='q-card'>
                <div class='q-number'>Q{q[0]:02d}  ·  WEIGHT {q[3]}%</div>
                <div class='q-text'>{q[2]}</div>
            </div>
            """, unsafe_allow_html=True)
            choice = st.radio(
                label=f"q{q[0]}",
                options=list(LIKERT.keys()),
                horizontal=True,
                label_visibility="collapsed",
                key=f"q_{q[0]}",
            )
            answers[q[0]] = LIKERT[choice]

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    if st.button("🔬  CALCULATE ERGONOMIC SCORE", use_container_width=True):
        score, cat_sc = compute_scores(answers)
        st.session_state.last_score = score
        st.session_state.last_cat_scores = cat_sc
        st.session_state.last_risk = risk_label(score)[0]
        st.session_state.answers = answers
        st.session_state.assessment_done = True
        st.rerun()


def page_history():
    u = st.session_state.user
    rows = load_user_assessments(u["username"])
    st.markdown("<div class='section-heading'>MY ASSESSMENT HISTORY</div>", unsafe_allow_html=True)

    if not rows:
        st.info("No assessments yet.")
        return

    # ── Trend Chart ──
    if len(rows) >= 2:
        st.plotly_chart(history_chart(rows), use_container_width=True, config={"displayModeBar": False})

    # ── Table ──
    records = []
    for r in rows:
        rl, rc, ri = risk_label(r[1])
        records.append({
            "Date": r[5][:16],
            "Score": f"{r[1]:.1f}%",
            "Risk Level": f"{ri} {rl}",
            "Notes": r[4][:50] if r[4] else "—",
        })
    df = pd.DataFrame(records)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Per-assessment detail ──
    st.markdown("<div class='section-heading' style='margin-top:20px;'>CATEGORY DEEP-DIVE</div>", unsafe_allow_html=True)
    options = {f"Assessment {i+1} — {r[5][:16]} ({r[1]:.1f}%)": r for i, r in enumerate(rows)}
    chosen_label = st.selectbox("Select assessment to review", list(options.keys()))
    chosen = options[chosen_label]
    cat_sc = json.loads(chosen[3])

    col_l, col_r = st.columns(2)
    with col_l:
        st.plotly_chart(radar_chart(cat_sc), use_container_width=True, config={"displayModeBar": False})
    with col_r:
        st.plotly_chart(category_bar(cat_sc), use_container_width=True, config={"displayModeBar": False})

    # ── PDF export for historical record ──
    pdf_bytes = generate_pdf(
        u, chosen[1], chosen[2], cat_sc, chosen[4] or "",
        chosen[5]
    )
    st.download_button(
        "📄  Download PDF for This Assessment", data=pdf_bytes,
        file_name=f"WSS_{u['username']}_{chosen[5][:10]}.pdf",
        mime="application/pdf",
    )


def page_analytics():
    u = st.session_state.user
    rows = load_user_assessments(u["username"])
    st.markdown("<div class='section-heading'>PERSONAL ANALYTICS</div>", unsafe_allow_html=True)

    if not rows:
        st.info("No data yet — complete an assessment first.")
        return

    # ── Category progress over time ──
    if len(rows) >= 2:
        st.markdown("<div class='section-heading'>CATEGORY TRENDS OVER TIME</div>", unsafe_allow_html=True)
        cat_over_time = {cat: [] for cat in CATEGORIES}
        dates = []
        for r in reversed(rows):
            cat_sc = json.loads(r[3])
            dates.append(r[5][:10])
            for cat in CATEGORIES:
                cat_over_time[cat].append(cat_sc.get(cat, 0))

        fig = go.Figure()
        for cat in CATEGORIES:
            fig.add_trace(go.Scatter(
                x=dates, y=cat_over_time[cat], name=f"{CAT_ICONS.get(cat,'')} {cat}",
                mode="lines+markers",
                line=dict(color=CAT_COLORS.get(cat, "#00F0FF"), width=2, shape="spline"),
                marker=dict(size=5),
            ))
        fig.update_layout(**PLOTLY_LAYOUT, height=380,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=10)),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(range=[0,105], gridcolor="rgba(255,255,255,0.05)", ticksuffix="%"),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── Best vs Worst ──
    if rows:
        all_cats = json.loads(rows[0][3])
        best_cat  = max(all_cats, key=all_cats.get)
        worst_cat = min(all_cats, key=all_cats.get)
        c1, c2 = st.columns(2)
        c1.markdown(f"""
        <div class='kpi-card'>
            <div style='font-size:2rem;'>{CAT_ICONS.get(best_cat,'')}</div>
            <div class='kpi-value' style='color:#00FF94;font-size:1.6rem;'>{all_cats[best_cat]}%</div>
            <div class='kpi-label'>Strongest Area</div>
            <div class='kpi-sub'>{best_cat}</div>
        </div>""", unsafe_allow_html=True)
        c2.markdown(f"""
        <div class='kpi-card'>
            <div style='font-size:2rem;'>{CAT_ICONS.get(worst_cat,'')}</div>
            <div class='kpi-value' style='color:#FF4D6D;font-size:1.6rem;'>{all_cats[worst_cat]}%</div>
            <div class='kpi-label'>Priority Focus</div>
            <div class='kpi-sub'>{worst_cat}</div>
        </div>""", unsafe_allow_html=True)


def page_admin():
    if st.session_state.user["role"] != "admin":
        st.error("Access denied.")
        return

    st.markdown("<div class='section-heading'>🛡️ ADMIN PANEL</div>", unsafe_allow_html=True)

    tab_overview, tab_users, tab_assessments = st.tabs(["📊 Overview", "👥 Users", "📋 All Assessments"])

    all_rows  = load_all_assessments()
    all_users = load_all_users()

    with tab_overview:
        c1, c2, c3, c4 = st.columns(4)
        scores = [r[4] for r in all_rows]
        for col, val, label, color in [
            (c1, len(all_users),                    "Total Users",       "#00F0FF"),
            (c2, len(all_rows),                     "Total Assessments", "#B48FFF"),
            (c3, f"{sum(scores)/len(scores):.1f}%" if scores else "—","Platform Avg Score", "#00FF94"),
            (c4, sum(1 for r in all_rows if r[5]=="High Risk"),"High Risk Users", "#FF4D6D"),
        ]:
            col.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-value' style='color:{color};'>{val}</div>
                <div class='kpi-label'>{label}</div>
            </div>""", unsafe_allow_html=True)

        if all_rows:
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            fig = dept_bar(all_rows)
            if fig:
                st.markdown("<div class='section-heading'>AVERAGE SCORE BY DEPARTMENT</div>", unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            # Risk distribution pie
            risk_counts = pd.Series([r[5] for r in all_rows]).value_counts()
            fig_pie = go.Figure(go.Pie(
                labels=risk_counts.index, values=risk_counts.values,
                marker=dict(colors=["#00FF94","#FFB800","#FF4D6D"],
                            line=dict(color="#0B0F19", width=2)),
                textfont=dict(family="Rajdhani", color="#FFFFFF"),
            ))
            fig_pie.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=True)
            st.markdown("<div class='section-heading'>RISK DISTRIBUTION</div>", unsafe_allow_html=True)
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    with tab_users:
        df_users = pd.DataFrame(all_users, columns=["ID","Username","Full Name","Email","Dept","Role","Created"])
        st.dataframe(df_users, use_container_width=True, hide_index=True)

    with tab_assessments:
        df_all = pd.DataFrame(all_rows, columns=["ID","Username","Full Name","Dept","Score","Risk","Created"])
        df_all["Score"] = df_all["Score"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(df_all, use_container_width=True, hide_index=True)

        # CSV Export
        csv = df_all.to_csv(index=False).encode()
        st.download_button(
            "📥  Export as CSV", data=csv,
            file_name=f"WSS_AllAssessments_{datetime.now():%Y%m%d}.csv",
            mime="text/csv",
        )

# ─────────────────────────────────────────────────────────────────────
# MAIN ROUTER
# ─────────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.logged_in:
        login_page()
        return

    sidebar()
    page = st.session_state.page

    if   page == "dashboard":  page_dashboard()
    elif page == "assessment": page_assessment()
    elif page == "history":    page_history()
    elif page == "analytics":  page_analytics()
    elif page == "admin":      page_admin()

if __name__ == "__main__":
    main()
