
"""
Workstation Safety Scorer v3.0
ICT in Health & Ergonomics | UET Taxila Engineering
"""
 
import streamlit as st
import sqlite3
import hashlib
import json
import os
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
import io
import base64
 
# ---------------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Workstation Safety Scorer",
    page_icon="WSS",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# ---------------------------------------------------------------------
# GLOBAL CSS
# ---------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');
 
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0B0F19 !important;
    color: #FFFFFF !important;
    font-family: 'Inter', sans-serif;
}
[data-testid="stSidebar"] {
    background: rgba(11,15,25,0.97) !important;
    border-right: 1px solid rgba(0,240,255,0.18) !important;
}
[data-testid="stHeader"]  { background: transparent !important; }
[data-testid="stToolbar"] { display: none; }
 
h1,h2,h3 { font-family: 'Orbitron', monospace !important; }
 
.glass-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(0,240,255,0.18);
    border-radius: 16px;
    padding: 24px;
    backdrop-filter: blur(20px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(0,240,255,0.1);
    margin-bottom: 16px;
}
.kpi-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(0,240,255,0.18);
    border-radius: 14px;
    padding: 20px 24px;
    text-align: center;
    box-shadow: 0 0 20px rgba(0,240,255,0.08);
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
    color: #A0AEC0;
    text-transform: uppercase;
    margin-top: 6px;
}
.kpi-sub { font-size: 0.75rem; color: #A0AEC0; margin-top: 4px; }
 
.badge-green { display:inline-block;padding:4px 14px;border-radius:20px;font-family:'Rajdhani',sans-serif;font-size:.75rem;font-weight:700;letter-spacing:2px;background:rgba(0,255,148,0.15);color:#00FF94;border:1px solid rgba(0,255,148,0.4); }
.badge-amber { display:inline-block;padding:4px 14px;border-radius:20px;font-family:'Rajdhani',sans-serif;font-size:.75rem;font-weight:700;letter-spacing:2px;background:rgba(255,184,0,0.15);color:#FFB800;border:1px solid rgba(255,184,0,0.4); }
.badge-red   { display:inline-block;padding:4px 14px;border-radius:20px;font-family:'Rajdhani',sans-serif;font-size:.75rem;font-weight:700;letter-spacing:2px;background:rgba(255,77,109,0.15);color:#FF4D6D;border:1px solid rgba(255,77,109,0.4); }
 
.section-heading {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.7rem;
    letter-spacing: 4px;
    color: #00F0FF;
    text-transform: uppercase;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(0,240,255,0.1);
}
.welcome-banner {
    background: linear-gradient(135deg,rgba(0,240,255,0.07),rgba(180,143,255,0.05));
    border: 1px solid rgba(0,240,255,0.2);
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 24px;
}
.welcome-title { font-family:'Orbitron',monospace;font-size:1.7rem;font-weight:900;color:#FFFFFF; }
.welcome-title span { color:#00F0FF;text-shadow:0 0 20px #00F0FF; }
.welcome-sub { font-family:'Rajdhani',sans-serif;font-size:.8rem;letter-spacing:3px;color:#A0AEC0;margin-top:6px; }
 
.risk-bar-wrap { background:rgba(255,255,255,0.06);border-radius:4px;height:6px;margin-top:6px; }
.risk-bar-fill { height:100%;border-radius:4px;transition:width .6s ease; }
 
.stButton > button {
    background: rgba(0,240,255,0.1) !important;
    border: 1px solid rgba(0,240,255,0.5) !important;
    color: #00F0FF !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    border-radius: 10px !important;
    padding: 10px 24px !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    background: rgba(0,240,255,0.2) !important;
    box-shadow: 0 0 20px rgba(0,240,255,0.25) !important;
}
div[data-testid="stRadio"] > label,
div[data-testid="stSelectbox"] label,
div[data-testid="stTextInput"] label,
div[data-testid="stPasswordInput"] label {
    color: #A0AEC0 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.78rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}
.q-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 12px;
}
.q-number { font-family:'Orbitron',monospace;font-size:.65rem;color:#00F0FF;letter-spacing:3px; }
.q-text   { font-size:.95rem;color:#FFFFFF;margin-top:4px;margin-bottom:12px; }
 
::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-thumb { background:rgba(0,240,255,0.3);border-radius:2px; }
</style>
""", unsafe_allow_html=True)
 
# ---------------------------------------------------------------------
# DATABASE
# ---------------------------------------------------------------------
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
        email     TEXT DEFAULT '',
        dept      TEXT DEFAULT 'Engineering',
        role      TEXT DEFAULT 'user',
        created   TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS assessments (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER,
        username   TEXT,
        score      REAL,
        risk_level TEXT,
        answers    TEXT,
        cat_scores TEXT,
        notes      TEXT DEFAULT '',
        created    TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)
    admin_pw = hashlib.sha256("admin123".encode()).hexdigest()
    demo_pw  = hashlib.sha256("demo123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (username,password,full_name,email,dept,role) VALUES (?,?,?,?,?,?)",
              ("admin", admin_pw, "Administrator", "admin@uet.edu.pk", "IT", "admin"))
    c.execute("INSERT OR IGNORE INTO users (username,password,full_name,email,dept,role) VALUES (?,?,?,?,?,?)",
              ("asnan", demo_pw,  "Muhammad Asnan", "asnan@uet.edu.pk", "Engineering", "user"))
    conn.commit()
    conn.close()
 
init_db()
 
# ---------------------------------------------------------------------
# AUTH
# ---------------------------------------------------------------------
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()
 
def login_user(username, password):
    conn = get_conn()
    row = conn.execute(
        "SELECT id,username,full_name,dept,role FROM users WHERE username=? AND password=?",
        (username, hash_pw(password))
    ).fetchone()
    conn.close()
    return {"id":row[0],"username":row[1],"full_name":row[2],"dept":row[3],"role":row[4]} if row else None
 
def register_user(username, password, full_name, email, dept):
    try:
        conn = get_conn()
        conn.execute("INSERT INTO users (username,password,full_name,email,dept) VALUES (?,?,?,?,?)",
                     (username, hash_pw(password), full_name, email, dept))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
 
# ---------------------------------------------------------------------
# ASSESSMENT DATA
# ---------------------------------------------------------------------
QUESTIONS = [
    (1,  "Chair & Posture",   "Is your chair height adjusted so your feet rest flat on the floor?",     15),
    (2,  "Chair & Posture",   "Does your chair provide adequate lumbar (lower-back) support?",          12),
    (3,  "Chair & Posture",   "Are your knees at approximately 90 degrees while seated?",              10),
    (4,  "Screen & Display",  "Is the top of your monitor at or slightly below eye level?",             12),
    (5,  "Screen & Display",  "Is the viewing distance between 50-70 cm from your eyes?",              10),
    (6,  "Screen & Display",  "Is the screen free from glare and reflections?",                        10),
    (7,  "Keyboard & Mouse",  "Are your wrists in a neutral (flat) position while typing?",             12),
    (8,  "Keyboard & Mouse",  "Is your mouse within easy reach without stretching your arm?",            8),
    (9,  "Keyboard & Mouse",  "Are your elbows at roughly 90 degrees and close to your body?",          8),
    (10, "Lighting",          "Is ambient lighting adequate and not causing eye strain?",               10),
    (11, "Lighting",          "Is direct sunlight or artificial light avoided on your screen?",          8),
    (12, "Environment",       "Is the room temperature comfortable (approx. 20-24 degrees C)?",         8),
    (13, "Environment",       "Is background noise at an acceptable level for concentration?",           7),
    (14, "Work Habits",       "Do you take a short break every 45-60 minutes?",                        10),
    (15, "Work Habits",       "Do you perform light stretching or movement during breaks?",              8),
    (16, "Work Habits",       "Do you blink regularly and look away from the screen periodically?",      7),
    (17, "Accessories",       "Do you use a document holder when referencing papers?",                   6),
    (18, "Accessories",       "Is a wrist rest available and used during keyboard/mouse use?",           6),
    (19, "Psychosocial",      "Do you feel comfortable with your current workload and stress level?",    8),
    (20, "Psychosocial",      "Is your workspace free from excessive clutter or disorganisation?",       5),
]
 
LIKERT = {
    "Never (0%)":     0,
    "Rarely (25%)":   1,
    "Sometimes (50%)":2,
    "Often (75%)":    3,
    "Always (100%)":  4,
}
 
CATEGORIES = [
    "Chair & Posture","Screen & Display","Keyboard & Mouse",
    "Lighting","Environment","Work Habits","Accessories","Psychosocial",
]
 
CAT_ICONS = {
    "Chair & Posture":  "[Chair]",
    "Screen & Display": "[Screen]",
    "Keyboard & Mouse": "[Keyboard]",
    "Lighting":         "[Light]",
    "Environment":      "[Env]",
    "Work Habits":      "[Habits]",
    "Accessories":      "[Access]",
    "Psychosocial":     "[Psych]",
}
 
CAT_ICONS_UI = {
    "Chair & Posture":  "Chair",
    "Screen & Display": "Screen",
    "Keyboard & Mouse": "Keyboard",
    "Lighting":         "Lighting",
    "Environment":      "Environment",
    "Work Habits":      "Work Habits",
    "Accessories":      "Accessories",
    "Psychosocial":     "Psychosocial",
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
        "Set seat depth so there is a 2-3 finger gap behind your knees.",
    ],
    "Screen & Display": [
        "Position the monitor top at eye level using a stand or adjustable arm.",
        "Maintain 50-70 cm viewing distance and use larger font sizes if needed.",
        "Apply an anti-glare screen filter and angle the monitor away from windows.",
    ],
    "Keyboard & Mouse": [
        "Keep wrists straight and neutral; use a wrist rest only during pauses.",
        "Place the mouse directly beside the keyboard to minimise reaching.",
        "Consider a split or ergonomic keyboard if wrist discomfort persists.",
    ],
    "Lighting": [
        "Use indirect or diffused lighting; avoid overhead fluorescent directly above screen.",
        "Enable blue-light filtering software for evening work.",
        "Position desk perpendicular to windows to minimise glare.",
    ],
    "Environment": [
        "Use a space heater or fan to maintain 20-24 degrees C thermal comfort.",
        "Wear noise-cancelling headphones or use white-noise apps if noisy.",
        "Ensure adequate ventilation and periodic fresh-air circulation.",
    ],
    "Work Habits": [
        "Every 20 minutes, look 20 feet away for 20 seconds to reduce eye strain.",
        "Set a recurring 45-minute reminder to stand, stretch, and move.",
        "Perform shoulder rolls, neck tilts, and wrist circles during micro-breaks.",
    ],
    "Accessories": [
        "Use a document holder at the same height and distance as your monitor.",
        "A padded wrist rest reduces contact stress during mouse-intensive work.",
        "Consider a vertical mouse or trackball to reduce forearm rotation.",
    ],
    "Psychosocial": [
        "Use task-management tools to reduce cognitive overload.",
        "Declutter your desk weekly; a tidy space reduces mental fatigue.",
        "Practice 5-minute mindfulness or breathing exercises between tasks.",
    ],
}
 
# ---------------------------------------------------------------------
# SCORING ENGINE
# ---------------------------------------------------------------------
def compute_scores(answers):
    total_weight = sum(q[3] for q in QUESTIONS)
    weighted_sum = sum(answers.get(q[0], 0) * q[3] for q in QUESTIONS)
    overall = round((weighted_sum / (4 * total_weight)) * 100, 1)
    cat_scores = {}
    for cat in CATEGORIES:
        qs = [q for q in QUESTIONS if q[1] == cat]
        w  = sum(q[3] for q in qs)
        s  = sum(answers.get(q[0], 0) * q[3] for q in qs)
        cat_scores[cat] = round((s / (4 * w)) * 100, 1) if w else 0.0
    return overall, cat_scores
 
def risk_label(score):
    if score >= 75: return "Low Risk",      "#00FF94", "Low"
    if score >= 50: return "Moderate Risk", "#FFB800", "Moderate"
    return                 "High Risk",     "#FF4D6D", "High"
 
def risk_badge_class(score):
    if score >= 75: return "badge-green"
    if score >= 50: return "badge-amber"
    return "badge-red"
 
# ---------------------------------------------------------------------
# DATABASE I/O
# ---------------------------------------------------------------------
def save_assessment(user_id, username, score, risk, answers, cat_scores, notes=""):
    conn = get_conn()
    conn.execute(
        "INSERT INTO assessments (user_id,username,score,risk_level,answers,cat_scores,notes) VALUES (?,?,?,?,?,?,?)",
        (user_id, username, score, risk, json.dumps(answers), json.dumps(cat_scores), notes)
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
 
# ---------------------------------------------------------------------
# PDF GENERATOR  -- 100% ASCII / Latin-1 safe
# ---------------------------------------------------------------------
def _safe(text):
    """Convert any string to Latin-1 safe ASCII -- no exceptions possible."""
    if not isinstance(text, str):
        text = str(text)
    return text.encode("ascii", errors="replace").decode("ascii")
 
def generate_pdf(user, score, risk, cat_scores, notes, timestamp):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
 
    # -- Header bar --
    pdf.set_fill_color(20, 30, 55)
    pdf.rect(0, 0, 210, 44, "F")
    pdf.set_text_color(0, 200, 220)
    pdf.set_font("Helvetica", "B", 17)
    pdf.set_xy(15, 10)
    pdf.cell(0, 8, _safe("WORKSTATION SAFETY SCORER"), ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(160, 174, 192)
    pdf.set_x(15)
    pdf.cell(0, 6, _safe("ICT in Health & Ergonomics  |  UET Taxila - Engineering"), ln=True)
    pdf.set_x(15)
    pdf.cell(0, 5, _safe("Report Generated: " + timestamp), ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(15, 52)
 
    # -- Section heading helper --
    def section(title):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_fill_color(225, 240, 255)
        pdf.set_text_color(20, 40, 100)
        pdf.set_x(15)
        pdf.cell(0, 8, _safe(title), ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
 
    # -- Assessment Details --
    section("ASSESSMENT DETAILS")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_x(15)
    pdf.cell(65, 7, _safe("Name:        " + user["full_name"]))
    pdf.cell(65, 7, _safe("Username:    " + user["username"]), ln=True)
    pdf.set_x(15)
    pdf.cell(65, 7, _safe("Department:  " + user["dept"]))
    pdf.cell(65, 7, _safe("Date:        " + str(timestamp)[:10]), ln=True)
    pdf.ln(4)
 
    # -- Overall Score --
    section("OVERALL ERGONOMIC SCORE")
    r_c, g_c, b_c = (0,180,90) if score >= 75 else (210,140,0) if score >= 50 else (210,50,50)
    pdf.set_font("Helvetica", "B", 26)
    pdf.set_text_color(r_c, g_c, b_c)
    pdf.set_x(15)
    pdf.cell(0, 14, _safe(str(score) + "%  -  " + risk), ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)
 
    # score bar
    bx, by, bw, bh = 15, pdf.get_y(), 180, 7
    pdf.set_fill_color(220, 230, 240)
    pdf.rect(bx, by, bw, bh, "F")
    pdf.set_fill_color(r_c, g_c, b_c)
    pdf.rect(bx, by, bw * score / 100, bh, "F")
    pdf.ln(bh + 6)
 
    # -- Category Breakdown --
    section("CATEGORY BREAKDOWN")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(200, 220, 240)
    pdf.set_x(15)
    pdf.cell(80, 7, _safe("Category"),   fill=True)
    pdf.cell(25, 7, _safe("Score"),      fill=True)
    pdf.cell(55, 7, _safe("Risk Level"), fill=True, ln=True)
    pdf.set_font("Helvetica", "", 9)
    for idx, (cat, s) in enumerate(cat_scores.items()):
        rl, _, _ = risk_label(s)
        fill = (idx % 2 == 0)
        pdf.set_fill_color(245, 250, 255)
        pdf.set_x(15)
        pdf.cell(80, 7, _safe(cat),       fill=fill)
        pdf.cell(25, 7, _safe(str(s) + "%"), fill=fill)
        pdf.cell(55, 7, _safe(rl),        fill=fill, ln=True)
        sc_r, sc_g, sc_b = (0,180,90) if s>=75 else (210,140,0) if s>=50 else (210,50,50)
        bx2, by2, bw2, bh2 = 15, pdf.get_y(), 155, 3
        pdf.set_fill_color(220, 230, 240)
        pdf.rect(bx2, by2, bw2, bh2, "F")
        pdf.set_fill_color(sc_r, sc_g, sc_b)
        pdf.rect(bx2, by2, bw2 * s / 100, bh2, "F")
        pdf.ln(bh2 + 3)
    pdf.ln(4)
 
    # -- Recommendations --
    section("PERSONALISED RECOMMENDATIONS")
    any_rec = False
    for cat, s in cat_scores.items():
        if s < 75:
            any_rec = True
            pdf.set_x(15)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(30, 70, 160)
            pdf.cell(0, 7, _safe(cat + "  (" + str(s) + "%)"), ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", 9)
            for rec in RECOMMENDATIONS.get(cat, []):
                pdf.set_x(20)
                pdf.multi_cell(0, 6, _safe("- " + rec))
            pdf.ln(2)
    if not any_rec:
        pdf.set_x(15)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(0, 150, 80)
        pdf.cell(0, 7, _safe("All categories are in the low-risk zone. Excellent work!"), ln=True)
        pdf.set_text_color(0, 0, 0)
 
    # -- Notes --
    if notes and notes.strip():
        pdf.ln(2)
        section("ASSESSOR NOTES")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_x(15)
        pdf.multi_cell(0, 6, _safe(notes))
 
    # -- Footer --
    pdf.set_y(-18)
    pdf.set_draw_color(0, 200, 220)
    pdf.set_line_width(0.3)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(130, 130, 130)
    pdf.cell(0, 5, _safe("Generated by Workstation Safety Scorer v3.0  |  UET Taxila Engineering Dept"), align="C")
 
    return bytes(pdf.output())
 
# ---------------------------------------------------------------------
# PLOTLY CHARTS
# ---------------------------------------------------------------------
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Rajdhani, sans-serif", color="#A0AEC0"),
    margin=dict(l=20, r=20, t=30, b=20),
)
 
def radar_chart(cat_scores):
    cats = list(cat_scores.keys())
    vals = list(cat_scores.values())
    cats_r = cats + cats[:1]
    vals_r = vals + vals[:1]
    fig = go.Figure(go.Scatterpolar(
        r=vals_r, theta=cats_r, fill="toself",
        fillcolor="rgba(0,240,255,0.1)",
        line=dict(color="#00F0FF", width=2),
        marker=dict(color="#00F0FF", size=6),
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT, height=340,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0,100],
                            gridcolor="rgba(0,240,255,0.15)", tickfont=dict(size=9)),
            angularaxis=dict(gridcolor="rgba(0,240,255,0.1)"),
        ),
    )
    return fig
 
def history_chart(rows):
    dates  = [r[5][:10] for r in rows][::-1]
    scores = [r[1]       for r in rows][::-1]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=scores, mode="lines+markers",
        line=dict(color="#00F0FF", width=2.5, shape="spline"),
        marker=dict(color="#00F0FF", size=7, line=dict(width=2, color="#FFFFFF")),
        fill="tozeroy", fillcolor="rgba(0,240,255,0.07)",
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT, height=240,
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(range=[0,100], gridcolor="rgba(255,255,255,0.05)", ticksuffix="%"),
    )
    return fig
 
def category_bar(cat_scores):
    cats   = list(cat_scores.keys())
    vals   = list(cat_scores.values())
    colors = [CAT_COLORS.get(c,"#00F0FF") for c in cats]
    fig = go.Figure(go.Bar(
        x=vals, y=cats, orientation="h",
        marker=dict(color=colors, opacity=0.85),
        text=[str(v)+"%" for v in vals], textposition="outside",
        textfont=dict(color="#FFFFFF"),
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT, height=360,
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
        color="avg_score",
        color_continuous_scale=["#FF4D6D","#FFB800","#00FF94"],
        range_color=[0,100], text_auto=".1f",
    )
    fig.update_traces(textfont_color="#FFFFFF")
    fig.update_layout(
        **PLOTLY_LAYOUT, height=300,
        coloraxis_showscale=False,
        xaxis_title="",
        yaxis=dict(range=[0,100], ticksuffix="%"),
    )
    return fig
 
# ---------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------
defaults = {
    "logged_in": False, "user": None, "page": "dashboard",
    "answers": {}, "assessment_done": False,
    "last_score": None, "last_cat_scores": None, "last_risk": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v
 
# ---------------------------------------------------------------------
# LOGIN PAGE
# ---------------------------------------------------------------------
def login_page():
    st.markdown("""
    <div style='text-align:center;margin-bottom:24px;'>
        <div style='font-family:Orbitron,monospace;font-size:1.6rem;font-weight:900;
                    color:#00F0FF;text-shadow:0 0 30px #00F0FF;'>WSS</div>
        <div style='font-family:Rajdhani,sans-serif;font-size:.7rem;
                    letter-spacing:4px;color:#A0AEC0;'>WORKSTATION SAFETY SCORER</div>
        <div style='font-family:Rajdhani,sans-serif;font-size:.62rem;
                    letter-spacing:2px;color:#555;margin-top:4px;'>
            ICT IN HEALTH AND ERGONOMICS | UET TAXILA
        </div>
    </div>
    """, unsafe_allow_html=True)
 
    tab_login, tab_reg = st.tabs(["Sign In", "Register"])
 
    with tab_login:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        uname = st.text_input("Username", placeholder="e.g. asnan", key="li_user")
        passw = st.text_input("Password", type="password", placeholder="Enter password", key="li_pass")
        if st.button("SIGN IN", use_container_width=True):
            user = login_user(uname.strip(), passw)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.error("Invalid username or password.")
        st.markdown("""
        <div style='margin-top:16px;padding:12px;background:rgba(0,240,255,0.05);
                    border:1px solid rgba(0,240,255,0.15);border-radius:10px;
                    font-family:Rajdhani,sans-serif;font-size:.8rem;color:#A0AEC0;'>
            <b style='color:#00F0FF;'>Demo Accounts</b><br>
            User &nbsp;: asnan &nbsp;/ demo123<br>
            Admin : admin / admin123
        </div>
        """, unsafe_allow_html=True)
 
    with tab_reg:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        r_name = st.text_input("Full Name", key="r_name")
        r_user = st.text_input("Username",  key="r_user")
        r_email= st.text_input("Email",     key="r_email")
        r_dept = st.selectbox("Department",
            ["Engineering","Computer Science","Management","Sciences","Other"], key="r_dept")
        r_pw   = st.text_input("Password",         type="password", key="r_pw")
        r_pw2  = st.text_input("Confirm Password", type="password", key="r_pw2")
        if st.button("CREATE ACCOUNT", use_container_width=True):
            if not all([r_name, r_user, r_pw]):
                st.warning("Name, username and password are required.")
            elif r_pw != r_pw2:
                st.error("Passwords do not match.")
            elif len(r_pw) < 6:
                st.error("Password must be at least 6 characters.")
            elif register_user(r_user.strip(), r_pw, r_name.strip(), r_email.strip(), r_dept):
                st.success("Account created! Please sign in.")
            else:
                st.error("Username already exists.")
 
# ---------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------
def sidebar():
    u = st.session_state.user
    with st.sidebar:
        st.markdown(f"""
        <div style='padding:0 8px 20px;'>
            <div style='font-family:Orbitron,monospace;font-size:1.1rem;font-weight:900;
                        color:#00F0FF;text-shadow:0 0 20px #00F0FF;letter-spacing:2px;'>WSS</div>
            <div style='font-family:Rajdhani,sans-serif;font-size:.62rem;
                        letter-spacing:3px;color:#A0AEC0;'>ERGO PLATFORM v3.0</div>
        </div>
        <div style='padding:12px 8px;border-top:1px solid rgba(0,240,255,0.1);
                    border-bottom:1px solid rgba(0,240,255,0.1);margin-bottom:16px;'>
            <div>
                <div style='font-weight:600;font-size:.88rem;color:#FFF;'>
                    {u["full_name"]}
                </div>
                <div style='font-size:.7rem;color:#A0AEC0;'>
                    {u["dept"]} | {u["role"].upper()}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
 
        pages = [
            ("dashboard",  "Dashboard"),
            ("assessment", "New Assessment"),
            ("history",    "My History"),
            ("analytics",  "Analytics"),
        ]
        if u["role"] == "admin":
            pages.append(("admin", "Admin Panel"))
 
        for pid, label in pages:
            if st.button(label, key=f"nav_{pid}", use_container_width=True):
                st.session_state.page = pid
                st.session_state.assessment_done = False
                st.rerun()
 
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True):
            for k, v in defaults.items():
                st.session_state[k] = v
            st.rerun()
 
# ---------------------------------------------------------------------
# PAGE: DASHBOARD
# ---------------------------------------------------------------------
def page_dashboard():
    u    = st.session_state.user
    rows = load_user_assessments(u["username"])
 
    latest_score = rows[0][1] if rows else None
    risk_str, risk_color, _ = risk_label(latest_score) if latest_score is not None else ("No Data","#A0AEC0","")
    trend = ""
    if len(rows) >= 2:
        diff  = rows[0][1] - rows[1][1]
        arrow = "up" if diff >= 0 else "down"
        col   = "#00FF94" if diff >= 0 else "#FF4D6D"
        trend = f"<span style='color:{col};font-size:.8rem;'>({'+' if diff>=0 else ''}{diff:.1f}% vs last)</span>"
 
    st.markdown(f"""
    <div class='welcome-banner'>
        <div class='welcome-title'>Welcome, <span>{u['full_name'].split()[0]}</span></div>
        <div class='welcome-sub'>
            ICT IN HEALTH AND ERGONOMICS: WORKSTATION SAFETY SCORER | {u['dept'].upper()}
        </div>
        <div style='margin-top:14px;display:flex;gap:24px;flex-wrap:wrap;'>
            <div style='font-size:.85rem;color:#A0AEC0;'>
                Latest Score:
                <b style='color:{risk_color};font-size:1.1rem;font-family:Orbitron,monospace;'>
                {(str(latest_score)+'%') if latest_score is not None else '--'}
                </b> {trend}
            </div>
            <div style='font-size:.85rem;color:#A0AEC0;'>
                Risk: <span style='color:{risk_color};font-weight:700;'>{risk_str}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
 
    # KPI row
    c1, c2, c3, c4 = st.columns(4)
    total     = len(rows)
    avg       = round(sum(r[1] for r in rows)/total, 1) if rows else 0
    best      = max((r[1] for r in rows), default=0)
    high_risk = sum(1 for r in rows if r[2] == "High Risk")
 
    for col, val, label, color, sub in [
        (c1, total,      "Total Assessments", "#00F0FF", "All time"),
        (c2, f"{avg}%",  "Average Score",     "#B48FFF", "All sessions"),
        (c3, f"{best}%", "Best Score",        "#00FF94", "Personal peak"),
        (c4, high_risk,  "High Risk Count",   "#FF4D6D", "Needs action"),
    ]:
        col.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-value' style='color:{color};'>{val}</div>
            <div class='kpi-label'>{label}</div>
            <div class='kpi-sub'>{sub}</div>
        </div>
        """, unsafe_allow_html=True)
 
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
 
    if rows:
        latest_cat = json.loads(rows[0][3]) if rows[0][3] else {}
        col_l, col_r = st.columns([1, 1.4])
        with col_l:
            st.markdown("<div class='section-heading'>ERGONOMIC RADAR</div>", unsafe_allow_html=True)
            if latest_cat:
                st.plotly_chart(radar_chart(latest_cat), use_container_width=True,
                                config={"displayModeBar": False})
        with col_r:
            st.markdown("<div class='section-heading'>SCORE HISTORY</div>", unsafe_allow_html=True)
            if len(rows) >= 2:
                st.plotly_chart(history_chart(rows), use_container_width=True,
                                config={"displayModeBar": False})
            else:
                st.info("Complete at least 2 assessments to see the trend chart.")
 
        st.markdown("<div class='section-heading'>LATEST CATEGORY BREAKDOWN</div>",
                    unsafe_allow_html=True)
        if latest_cat:
            cols = st.columns(4)
            for i, (cat, s) in enumerate(latest_cat.items()):
                rl, rc, _ = risk_label(s)
                cols[i % 4].markdown(f"""
                <div class='kpi-card' style='margin-bottom:8px;'>
                    <div style='font-size:1.3rem;font-family:Orbitron,monospace;
                                font-weight:700;color:{CAT_COLORS.get(cat,"#00F0FF")};'>{s}%</div>
                    <div class='kpi-label'>{cat}</div>
                    <span class='{risk_badge_class(s)}'>{rl}</span>
                    <div class='risk-bar-wrap'>
                        <div class='risk-bar-fill'
                             style='width:{s}%;background:{CAT_COLORS.get(cat,"#00F0FF")};'>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No assessments yet. Click 'New Assessment' in the sidebar to get started.")
 
# ---------------------------------------------------------------------
# PAGE: ASSESSMENT
# ---------------------------------------------------------------------
def page_assessment():
    st.markdown("<div class='section-heading'>NEW ERGONOMIC ASSESSMENT</div>",
                unsafe_allow_html=True)
 
    if st.session_state.assessment_done and st.session_state.last_score is not None:
        score  = st.session_state.last_score
        cat_sc = st.session_state.last_cat_scores
        risk_str, risk_color, _ = risk_label(score)
 
        st.markdown(f"""
        <div class='glass-card' style='text-align:center;padding:36px;'>
            <div style='font-size:.7rem;letter-spacing:4px;color:#A0AEC0;
                        font-family:Rajdhani,sans-serif;'>ASSESSMENT COMPLETE</div>
            <div style='font-family:Orbitron,monospace;font-size:4rem;font-weight:900;
                        color:{risk_color};text-shadow:0 0 30px {risk_color};
                        line-height:1;margin:12px 0;'>{score}%</div>
            <div style='color:{risk_color};font-family:Rajdhani,sans-serif;font-size:1.1rem;
                        font-weight:700;letter-spacing:3px;'>{risk_str}</div>
        </div>
        """, unsafe_allow_html=True)
 
        # Recommendations
        st.markdown("<div class='section-heading'>PERSONALISED RECOMMENDATIONS</div>",
                    unsafe_allow_html=True)
        low_cats = {c: s for c, s in cat_sc.items() if s < 75}
        if low_cats:
            for cat, s in sorted(low_cats.items(), key=lambda x: x[1]):
                rl, _, _ = risk_label(s)
                with st.expander(f"{cat} - {s}% ({rl})"):
                    for rec in RECOMMENDATIONS.get(cat, []):
                        st.markdown(f"- {rec}")
        else:
            st.success("Excellent! All categories are in the low-risk zone.")
 
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        notes = st.text_area("Add notes (optional)", placeholder="Additional observations...")
 
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save Assessment", use_container_width=True):
                save_assessment(
                    st.session_state.user["id"],
                    st.session_state.user["username"],
                    score, risk_str,
                    st.session_state.answers, cat_sc, notes
                )
                st.success("Assessment saved successfully!")
 
        with col2:
            pdf_bytes = generate_pdf(
                st.session_state.user, score, risk_str, cat_sc,
                notes, datetime.now().strftime("%Y-%m-%d %H:%M")
            )
            st.download_button(
                "Download PDF Report", data=pdf_bytes,
                file_name=f"WSS_Report_{st.session_state.user['username']}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf", use_container_width=True,
            )
 
        if st.button("Start New Assessment", use_container_width=True):
            st.session_state.assessment_done = False
            st.session_state.answers = {}
            st.rerun()
        return
 
    # Questions
    st.markdown("""
    <div style='font-family:Rajdhani,sans-serif;color:#A0AEC0;font-size:.85rem;margin-bottom:20px;'>
        Answer all <b style='color:#00F0FF;'>20 questions</b> honestly based on
        your typical daily workstation setup. Each answer is weighted by ergonomic importance.
    </div>
    """, unsafe_allow_html=True)
 
    answers = {}
    current_cat = None
    for q in QUESTIONS:
        if q[1] != current_cat:
            current_cat = q[1]
            st.markdown(f"""
            <div style='font-family:Rajdhani,sans-serif;font-size:.68rem;letter-spacing:4px;
                        color:{CAT_COLORS.get(current_cat,"#00F0FF")};text-transform:uppercase;
                        padding:12px 0 4px;border-top:1px solid rgba(255,255,255,0.05);
                        margin-top:10px;'>{current_cat}</div>
            """, unsafe_allow_html=True)
 
        st.markdown(f"""
        <div class='q-card'>
            <div class='q-number'>Q{q[0]:02d} | WEIGHT {q[3]}%</div>
            <div class='q-text'>{q[2]}</div>
        </div>
        """, unsafe_allow_html=True)
        choice = st.radio(
            label=f"Answer for Q{q[0]}",
            options=list(LIKERT.keys()),
            horizontal=True,
            label_visibility="collapsed",
            key=f"q_{q[0]}",
        )
        answers[q[0]] = LIKERT[choice]
 
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    if st.button("CALCULATE ERGONOMIC SCORE", use_container_width=True):
        score, cat_sc = compute_scores(answers)
        st.session_state.last_score      = score
        st.session_state.last_cat_scores = cat_sc
        st.session_state.last_risk       = risk_label(score)[0]
        st.session_state.answers         = answers
        st.session_state.assessment_done = True
        st.rerun()
 
# ---------------------------------------------------------------------
# PAGE: HISTORY
# ---------------------------------------------------------------------
def page_history():
    u    = st.session_state.user
    rows = load_user_assessments(u["username"])
    st.markdown("<div class='section-heading'>MY ASSESSMENT HISTORY</div>",
                unsafe_allow_html=True)
 
    if not rows:
        st.info("No assessments yet.")
        return
 
    if len(rows) >= 2:
        st.plotly_chart(history_chart(rows), use_container_width=True,
                        config={"displayModeBar": False})
 
    records = []
    for r in rows:
        rl, _, _ = risk_label(r[1])
        records.append({
            "Date":       r[5][:16],
            "Score":      f"{r[1]:.1f}%",
            "Risk Level": rl,
            "Notes":      (r[4] or "")[:50] or "--",
        })
    st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
 
    st.markdown("<div class='section-heading' style='margin-top:20px;'>CATEGORY DEEP-DIVE</div>",
                unsafe_allow_html=True)
    options = {
        f"Assessment {i+1} | {r[5][:16]} | {r[1]:.1f}%": r
        for i, r in enumerate(rows)
    }
    chosen_label = st.selectbox("Select an assessment to review", list(options.keys()))
    chosen = options[chosen_label]
    cat_sc = json.loads(chosen[3]) if chosen[3] else {}
 
    if cat_sc:
        col_l, col_r = st.columns(2)
        with col_l:
            st.plotly_chart(radar_chart(cat_sc), use_container_width=True,
                            config={"displayModeBar": False})
        with col_r:
            st.plotly_chart(category_bar(cat_sc), use_container_width=True,
                            config={"displayModeBar": False})
 
    pdf_bytes = generate_pdf(
        u, chosen[1], chosen[2], cat_sc,
        chosen[4] or "", chosen[5]
    )
    st.download_button(
        "Download PDF for This Assessment", data=pdf_bytes,
        file_name=f"WSS_{u['username']}_{chosen[5][:10]}.pdf",
        mime="application/pdf",
    )
 
# ---------------------------------------------------------------------
# PAGE: ANALYTICS
# ---------------------------------------------------------------------
def page_analytics():
    u    = st.session_state.user
    rows = load_user_assessments(u["username"])
    st.markdown("<div class='section-heading'>PERSONAL ANALYTICS</div>",
                unsafe_allow_html=True)
 
    if not rows:
        st.info("No data yet. Complete an assessment first.")
        return
 
    if len(rows) >= 2:
        st.markdown("<div class='section-heading'>CATEGORY TRENDS OVER TIME</div>",
                    unsafe_allow_html=True)
        cat_over_time = {cat: [] for cat in CATEGORIES}
        dates = []
        for r in reversed(rows):
            cat_sc = json.loads(r[3]) if r[3] else {}
            dates.append(r[5][:10])
            for cat in CATEGORIES:
                cat_over_time[cat].append(cat_sc.get(cat, 0))
 
        fig = go.Figure()
        for cat in CATEGORIES:
            fig.add_trace(go.Scatter(
                x=dates, y=cat_over_time[cat],
                name=cat,
                mode="lines+markers",
                line=dict(color=CAT_COLORS.get(cat,"#00F0FF"), width=2, shape="spline"),
                marker=dict(size=5),
            ))
        fig.update_layout(
            **PLOTLY_LAYOUT, height=380,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=10)),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(range=[0,105], gridcolor="rgba(255,255,255,0.05)", ticksuffix="%"),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
 
    if rows:
        all_cats = json.loads(rows[0][3]) if rows[0][3] else {}
        if all_cats:
            best_cat  = max(all_cats, key=all_cats.get)
            worst_cat = min(all_cats, key=all_cats.get)
            c1, c2 = st.columns(2)
            c1.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-value' style='color:#00FF94;font-size:1.6rem;'>
                    {all_cats[best_cat]}%
                </div>
                <div class='kpi-label'>Strongest Area</div>
                <div class='kpi-sub'>{best_cat}</div>
            </div>""", unsafe_allow_html=True)
            c2.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-value' style='color:#FF4D6D;font-size:1.6rem;'>
                    {all_cats[worst_cat]}%
                </div>
                <div class='kpi-label'>Priority Focus Area</div>
                <div class='kpi-sub'>{worst_cat}</div>
            </div>""", unsafe_allow_html=True)
 
# ---------------------------------------------------------------------
# PAGE: ADMIN
# ---------------------------------------------------------------------
def page_admin():
    if st.session_state.user["role"] != "admin":
        st.error("Access denied.")
        return
 
    st.markdown("<div class='section-heading'>ADMIN PANEL</div>", unsafe_allow_html=True)
 
    all_rows  = load_all_assessments()
    all_users = load_all_users()
 
    tab_ov, tab_users, tab_ass = st.tabs(["Overview", "Users", "All Assessments"])
 
    with tab_ov:
        scores = [r[4] for r in all_rows]
        c1, c2, c3, c4 = st.columns(4)
        for col, val, label, color in [
            (c1, len(all_users), "Total Users",        "#00F0FF"),
            (c2, len(all_rows),  "Total Assessments",  "#B48FFF"),
            (c3, f"{sum(scores)/len(scores):.1f}%" if scores else "--", "Platform Avg", "#00FF94"),
            (c4, sum(1 for r in all_rows if r[5]=="High Risk"), "High Risk Users", "#FF4D6D"),
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
                st.markdown("<div class='section-heading'>AVG SCORE BY DEPARTMENT</div>",
                            unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
 
            risk_counts = pd.Series([r[5] for r in all_rows]).value_counts()
            fig_pie = go.Figure(go.Pie(
                labels=risk_counts.index, values=risk_counts.values,
                marker=dict(colors=["#00FF94","#FFB800","#FF4D6D"],
                            line=dict(color="#0B0F19", width=2)),
                textfont=dict(family="Rajdhani", color="#FFFFFF"),
            ))
            fig_pie.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=True)
            st.markdown("<div class='section-heading'>RISK DISTRIBUTION</div>",
                        unsafe_allow_html=True)
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
 
    with tab_users:
        df_u = pd.DataFrame(all_users,
            columns=["ID","Username","Full Name","Email","Dept","Role","Created"])
        st.dataframe(df_u, use_container_width=True, hide_index=True)
 
    with tab_ass:
        if all_rows:
            df_a = pd.DataFrame(all_rows,
                columns=["ID","Username","Full Name","Dept","Score","Risk","Created"])
            df_a["Score"] = df_a["Score"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(df_a, use_container_width=True, hide_index=True)
            csv = df_a.to_csv(index=False).encode()
            st.download_button(
                "Export as CSV", data=csv,
                file_name=f"WSS_AllAssessments_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
        else:
            st.info("No assessments recorded yet.")
 
# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------
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
 
