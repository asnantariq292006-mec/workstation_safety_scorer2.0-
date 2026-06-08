"""
Workstation Safety Scorer
Bright Streamlit Version

Default login:
    admin / admin123
    demo  / demo123
"""

import base64
import hashlib
import io
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from fpdf import FPDF

# =========================================================
# PAGE SETUP
# =========================================================
st.set_page_config(
    page_title="Workstation Safety Scorer",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = "workstation_safety.db"

# =========================================================
# BRIGHT UI THEME
# =========================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');

:root{
  --bg:#F7FAFF;
  --panel:#FFFFFF;
  --panel2:#F0F9FF;
  --text:#0F172A;
  --muted:#64748B;
  --primary:#0EA5E9;
  --purple:#8B5CF6;
  --green:#10B981;
  --amber:#F59E0B;
  --red:#EF4444;
  --border:rgba(14,165,233,.20);
  --shadow:0 18px 50px rgba(15,23,42,.10);
}

html, body, [data-testid="stAppViewContainer"]{
  background:
    radial-gradient(circle at 12% 8%, rgba(14,165,233,.18), transparent 32%),
    radial-gradient(circle at 88% 10%, rgba(139,92,246,.14), transparent 30%),
    linear-gradient(180deg,#F7FAFF 0%,#ECF8FF 55%,#FFFFFF 100%) !important;
  color:var(--text)!important;
  font-family:'Inter',sans-serif;
}

[data-testid="stAppViewContainer"]::before{
  content:"";
  position:fixed;
  inset:0;
  background-image:
    linear-gradient(rgba(14,165,233,.045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(14,165,233,.045) 1px, transparent 1px);
  background-size:38px 38px;
  pointer-events:none;
  z-index:0;
}

.block-container{padding-top:1.4rem!important;max-width:1280px;}
[data-testid="stHeader"]{background:transparent!important;}
[data-testid="stToolbar"], [data-testid="stDecoration"]{display:none!important;}
[data-testid="stSidebar"]{
  background:rgba(255,255,255,.98)!important;
  border-right:1px solid var(--border)!important;
  box-shadow:10px 0 32px rgba(15,23,42,.06);
}

h1,h2,h3,.brand-title,.section-title,.kpi-label{font-family:'Outfit',sans-serif!important;}

.hero{
  background:linear-gradient(135deg,rgba(14,165,233,.13),rgba(139,92,246,.10),rgba(16,185,129,.10));
  border:1px solid var(--border);
  border-radius:30px;
  padding:34px 38px;
  margin-bottom:26px;
  box-shadow:var(--shadow);
  position:relative;
  overflow:hidden;
}
.hero:after{
  content:"";
  position:absolute;
  right:-70px;
  top:-80px;
  width:270px;
  height:270px;
  border-radius:50%;
  background:radial-gradient(circle,rgba(14,165,233,.24),transparent 65%);
}
.hero h1{font-size:2.2rem;margin:0 0 8px;font-weight:800;color:var(--text);position:relative;}
.hero h1 span{
  background:linear-gradient(135deg,#0284C7,#7C3AED);
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
}
.hero p{margin:0;color:var(--muted);font-weight:600;letter-spacing:.3px;position:relative;}

.card{
  background:rgba(255,255,255,.94);
  border:1px solid var(--border);
  border-radius:24px;
  padding:24px 28px;
  box-shadow:var(--shadow);
  margin-bottom:20px;
}
.card-soft{
  background:linear-gradient(135deg,#FFFFFF,#F0F9FF);
  border:1px solid var(--border);
  border-radius:22px;
  padding:22px;
  box-shadow:0 12px 32px rgba(15,23,42,.08);
}
.kpi-card{
  background:linear-gradient(135deg,#FFFFFF,#F0F9FF);
  border:1px solid var(--border);
  border-radius:22px;
  padding:22px 16px;
  text-align:center;
  box-shadow:0 14px 36px rgba(15,23,42,.08);
  min-height:135px;
}
.kpi-value{
  font-family:'JetBrains Mono',monospace;
  font-size:2rem;
  font-weight:800;
  line-height:1.1;
}
.kpi-label{
  color:var(--muted);
  text-transform:uppercase;
  letter-spacing:1.7px;
  font-size:.72rem;
  font-weight:800;
  margin-top:8px;
}
.kpi-sub{color:var(--muted);font-size:.78rem;margin-top:4px;}

.section-title{
  color:#0369A1;
  text-transform:uppercase;
  letter-spacing:2.2px;
  font-size:.82rem;
  font-weight:800;
  margin:8px 0 16px;
  padding-bottom:10px;
  border-bottom:1px solid rgba(14,165,233,.18);
}

.badge{
  display:inline-flex;
  padding:6px 13px;
  border-radius:999px;
  font-family:'Outfit',sans-serif;
  font-size:.75rem;
  font-weight:800;
  letter-spacing:.7px;
}
.badge.green{background:#D1FAE5;color:#047857;border:1px solid #A7F3D0;}
.badge.amber{background:#FEF3C7;color:#92400E;border:1px solid #FDE68A;}
.badge.red{background:#FEE2E2;color:#B91C1C;border:1px solid #FECACA;}

.question-card{
  background:#FFFFFF;
  border:1px solid rgba(14,165,233,.18);
  border-left:6px solid #0EA5E9;
  border-radius:20px;
  padding:20px 22px 8px;
  margin:18px 0 22px;
  box-shadow:0 12px 30px rgba(15,23,42,.07);
}
.question-number{
  font-family:'JetBrains Mono',monospace;
  font-size:.75rem;
  color:#0284C7;
  font-weight:800;
  letter-spacing:1.4px;
  margin-bottom:6px;
}
.question-text{
  color:var(--text);
  font-size:1rem;
  font-weight:700;
  line-height:1.5;
  margin-bottom:12px;
}
.helper-text{color:var(--muted);font-size:.85rem;margin-bottom:8px;}

div[data-testid="stRadio"]{
  background:#F8FBFF!important;
  border:1px solid rgba(14,165,233,.12);
  border-radius:16px;
  padding:10px 14px;
  margin-bottom:12px;
}
div[data-testid="stRadio"] label{
  color:#334155!important;
  font-size:.92rem!important;
  font-weight:500!important;
  padding:8px 10px!important;
  border-radius:12px!important;
}
div[data-testid="stRadio"] label:hover{background:#E0F2FE!important;color:#075985!important;}

.stButton>button, .stDownloadButton>button, div[data-testid="stFormSubmitButton"] button{
  background:linear-gradient(135deg,#0EA5E9,#8B5CF6)!important;
  color:white!important;
  border:0!important;
  border-radius:14px!important;
  padding:12px 20px!important;
  font-family:'Outfit',sans-serif!important;
  font-weight:800!important;
  letter-spacing:.8px!important;
  text-transform:uppercase!important;
  box-shadow:0 12px 28px rgba(14,165,233,.22)!important;
}
.stButton>button:hover, .stDownloadButton>button:hover, div[data-testid="stFormSubmitButton"] button:hover{
  transform:translateY(-2px)!important;
  box-shadow:0 18px 38px rgba(99,102,241,.24)!important;
}

input, textarea, div[data-testid="stSelectbox"]>div>div{
  background:#FFFFFF!important;
  border:1px solid var(--border)!important;
  border-radius:14px!important;
  color:var(--text)!important;
  box-shadow:0 8px 22px rgba(15,23,42,.05)!important;
}
label, div[data-testid="stSelectbox"] label{
  color:#334155!important;
  font-family:'Outfit',sans-serif!important;
  font-weight:800!important;
  letter-spacing:.8px!important;
}

.stTabs [data-baseweb="tab-list"]{
  background:rgba(255,255,255,.92)!important;
  border:1px solid var(--border)!important;
  border-radius:16px!important;
  padding:6px!important;
  box-shadow:var(--shadow);
}
.stTabs [data-baseweb="tab"]{
  border-radius:12px!important;
  color:var(--muted)!important;
  font-family:'Outfit',sans-serif!important;
  font-weight:800!important;
}
.stTabs [aria-selected="true"]{
  background:linear-gradient(135deg,#E0F2FE,#EDE9FE)!important;
  color:#075985!important;
}

.alert-success{background:#ECFDF5;border:1px solid #A7F3D0;color:#047857;border-radius:16px;padding:14px 16px;}
.alert-warn{background:#FFFBEB;border:1px solid #FDE68A;color:#92400E;border-radius:16px;padding:14px 16px;}
.alert-danger{background:#FEF2F2;border:1px solid #FECACA;color:#B91C1C;border-radius:16px;padding:14px 16px;}

.risk-bar-wrap{height:9px;background:#E2E8F0;border-radius:999px;overflow:hidden;margin-top:12px;}
.risk-bar-fill{height:100%;border-radius:999px;}

hr{border:none;border-top:1px solid rgba(14,165,233,.16);margin:22px 0;}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# QUESTION BANK
# score_direction:
#   normal  -> option index 0 is worst, last option is best
#   reverse -> option index 0 is best, last option is worst
# =========================================================
LIKERT_OPTIONS = [
    "Never / Not at all",
    "Rarely",
    "Sometimes",
    "Often",
    "Always / Fully yes",
]

QUESTIONS: List[Dict] = [
    {
        "id": 1,
        "category": "Chair & Posture",
        "type": "likert",
        "weight": 12,
        "text": "Are your feet fully supported by the floor or a footrest while seated?",
        "helper": "Good support reduces pressure on the legs and lower back.",
    },
    {
        "id": 2,
        "category": "Chair & Posture",
        "type": "likert",
        "weight": 10,
        "text": "Does your chair support the natural curve of your lower back?",
        "helper": "Lumbar support should touch the inward curve of your spine.",
    },
    {
        "id": 3,
        "category": "Chair & Posture",
        "type": "mcq",
        "weight": 9,
        "direction": "reverse",
        "text": "Which option best describes your sitting posture during most work sessions?",
        "helper": "Choose the posture you use most often, not the ideal posture.",
        "options": [
            "Upright with back supported",
            "Mostly upright but I lean forward sometimes",
            "I frequently slouch",
            "I lean to one side for long periods",
            "I sit in uncomfortable positions for most of the day",
        ],
    },
    {
        "id": 4,
        "category": "Chair & Posture",
        "type": "likert",
        "weight": 8,
        "text": "Is there a small gap between the seat edge and the back of your knees?",
        "helper": "A 2-3 finger gap helps avoid pressure behind the knees.",
    },
    {
        "id": 5,
        "category": "Screen & Display",
        "type": "likert",
        "weight": 11,
        "text": "Is the top of your screen at, or slightly below, eye level?",
        "helper": "This helps prevent neck bending and eye strain.",
    },
    {
        "id": 6,
        "category": "Screen & Display",
        "type": "mcq",
        "weight": 10,
        "direction": "reverse",
        "text": "How far is your main screen from your eyes?",
        "helper": "The usual safe range is about an arm's length away.",
        "options": [
            "50-70 cm / about arm's length",
            "40-50 cm",
            "70-90 cm",
            "Less than 40 cm",
            "I am not sure / it changes a lot",
        ],
    },
    {
        "id": 7,
        "category": "Screen & Display",
        "type": "likert",
        "weight": 9,
        "text": "Is your screen free from strong glare or reflections?",
        "helper": "Glare often comes from windows, overhead lights, or glossy screens.",
    },
    {
        "id": 8,
        "category": "Screen & Display",
        "type": "mcq",
        "weight": 8,
        "direction": "reverse",
        "text": "How many hours per day do you usually look at a screen for work or study?",
        "helper": "Include laptop, desktop, tablet, and phone screen time used for work.",
        "options": [
            "Less than 2 hours",
            "2-4 hours",
            "4-6 hours",
            "6-8 hours",
            "More than 8 hours",
        ],
    },
    {
        "id": 9,
        "category": "Keyboard & Mouse",
        "type": "likert",
        "weight": 11,
        "text": "Do your wrists stay straight and relaxed while typing?",
        "helper": "Avoid bending wrists upward, downward, or sideways.",
    },
    {
        "id": 10,
        "category": "Keyboard & Mouse",
        "type": "likert",
        "weight": 8,
        "text": "Is your mouse close enough that you do not need to stretch your arm?",
        "helper": "The mouse should sit close to the keyboard at a similar height.",
    },
    {
        "id": 11,
        "category": "Keyboard & Mouse",
        "type": "mcq",
        "weight": 8,
        "direction": "normal",
        "text": "Which setup do you mainly use for typing and pointing?",
        "helper": "Choose the closest match to your current workstation.",
        "options": [
            "Laptop keyboard only on a low desk",
            "Standard keyboard and mouse with no adjustment",
            "External keyboard with laptop raised",
            "Keyboard and mouse positioned at elbow height",
            "Ergonomic keyboard/mouse with correct positioning",
        ],
    },
    {
        "id": 12,
        "category": "Keyboard & Mouse",
        "type": "likert",
        "weight": 7,
        "text": "Are your elbows close to your body and roughly at a right angle while typing?",
        "helper": "Relaxed elbows reduce shoulder and wrist strain.",
    },
    {
        "id": 13,
        "category": "Lighting",
        "type": "likert",
        "weight": 9,
        "text": "Is your workspace lighting comfortable for reading and screen work?",
        "helper": "The room should be bright enough without causing eye discomfort.",
    },
    {
        "id": 14,
        "category": "Lighting",
        "type": "likert",
        "weight": 8,
        "text": "Do you avoid direct sunlight or bright lamps shining onto your screen?",
        "helper": "Direct light can create glare and force your eyes to work harder.",
    },
    {
        "id": 15,
        "category": "Lighting",
        "type": "mcq",
        "weight": 7,
        "direction": "normal",
        "text": "What do you usually do to reduce digital eye strain?",
        "helper": "Pick the method you use most consistently.",
        "options": [
            "Nothing specific",
            "Only lower screen brightness",
            "Use dark/reading mode sometimes",
            "Use blue-light filter or anti-glare settings regularly",
            "Use filters plus regular eye breaks",
        ],
    },
    {
        "id": 16,
        "category": "Environment",
        "type": "likert",
        "weight": 8,
        "text": "Is the room temperature comfortable during your work sessions?",
        "helper": "Too hot or too cold can reduce focus and increase fatigue.",
    },
    {
        "id": 17,
        "category": "Environment",
        "type": "likert",
        "weight": 7,
        "text": "Is background noise low enough for focused work?",
        "helper": "Consider nearby people, traffic, machines, or shared spaces.",
    },
    {
        "id": 18,
        "category": "Environment",
        "type": "likert",
        "weight": 6,
        "text": "Is your desk area clean, organized, and free from unnecessary clutter?",
        "helper": "A clear workspace helps movement, safety, and concentration.",
    },
    {
        "id": 19,
        "category": "Environment",
        "type": "mcq",
        "weight": 6,
        "direction": "reverse",
        "text": "How would you describe the air quality or ventilation in your workspace?",
        "helper": "Think about fresh air, stuffiness, dust, and odors.",
        "options": [
            "Fresh and well ventilated",
            "Mostly good",
            "Sometimes stuffy",
            "Often stuffy or dusty",
            "Poor ventilation most of the time",
        ],
    },
    {
        "id": 20,
        "category": "Work Habits",
        "type": "likert",
        "weight": 10,
        "text": "Do you take short movement breaks during long work sessions?",
        "helper": "A 5-10 minute break every 45-60 minutes is a good target.",
    },
    {
        "id": 21,
        "category": "Work Habits",
        "type": "likert",
        "weight": 9,
        "text": "Do you stretch your neck, shoulders, back, or wrists during breaks?",
        "helper": "Small movements can reduce stiffness and repetitive strain.",
    },
    {
        "id": 22,
        "category": "Work Habits",
        "type": "mcq",
        "weight": 8,
        "direction": "normal",
        "text": "How do you usually manage eye breaks while using screens?",
        "helper": "The 20-20-20 rule means looking 20 feet away for 20 seconds every 20 minutes.",
        "options": [
            "I do not take eye breaks",
            "I only stop when my eyes hurt",
            "I take occasional random breaks",
            "I take regular eye breaks most days",
            "I consistently follow a structured eye-break rule",
        ],
    },
    {
        "id": 23,
        "category": "Work Habits",
        "type": "mcq",
        "weight": 9,
        "direction": "reverse",
        "text": "How often do you feel neck, back, shoulder, or wrist pain after work?",
        "helper": "Choose the option that best matches the last few weeks.",
        "options": [
            "Never",
            "Rarely",
            "Sometimes",
            "Often",
            "Almost every day",
        ],
    },
    {
        "id": 24,
        "category": "Accessories",
        "type": "mcq",
        "weight": 7,
        "direction": "normal",
        "text": "Which ergonomic accessories do you currently use?",
        "helper": "Examples include monitor stand, footrest, wrist rest, document holder, or laptop stand.",
        "options": [
            "None",
            "One basic accessory",
            "Two useful accessories",
            "Several accessories used correctly",
            "A complete ergonomic setup used correctly",
        ],
    },
    {
        "id": 25,
        "category": "Accessories",
        "type": "likert",
        "weight": 6,
        "text": "If you use printed notes or documents, are they positioned to avoid neck twisting?",
        "helper": "A document holder can keep papers close to screen height.",
    },
    {
        "id": 26,
        "category": "Accessories",
        "type": "likert",
        "weight": 6,
        "text": "Do you have suitable wrist or forearm support during pauses?",
        "helper": "Wrist rests are for pauses, not for pressing wrists while actively typing.",
    },
    {
        "id": 27,
        "category": "Psychosocial",
        "type": "likert",
        "weight": 8,
        "text": "Do you feel your workload is manageable during a typical workday?",
        "helper": "A manageable workload reduces stress-related physical tension.",
    },
    {
        "id": 28,
        "category": "Psychosocial",
        "type": "likert",
        "weight": 7,
        "text": "Do you feel supported when you report discomfort, stress, or workstation issues?",
        "helper": "Support may come from teachers, supervisors, managers, or colleagues.",
    },
    {
        "id": 29,
        "category": "Psychosocial",
        "type": "mcq",
        "weight": 7,
        "direction": "reverse",
        "text": "How would you describe your mental wellbeing during most workdays?",
        "helper": "Consider stress, focus, mood, and feeling overwhelmed.",
        "options": [
            "Calm and focused",
            "Mostly positive",
            "Mixed / sometimes stressed",
            "Frequently stressed",
            "Overwhelmed most days",
        ],
    },
    {
        "id": 30,
        "category": "Psychosocial",
        "type": "mcq",
        "weight": 6,
        "direction": "normal",
        "text": "How well do you recover after long screen-work sessions?",
        "helper": "Think about tiredness, headaches, sleep, and ability to relax.",
        "options": [
            "I feel drained and do not recover well",
            "Recovery is slow",
            "Recovery is average",
            "I recover well after rest",
            "I recover very well with healthy routines",
        ],
    },
]

CATEGORIES = [
    "Chair & Posture",
    "Screen & Display",
    "Keyboard & Mouse",
    "Lighting",
    "Environment",
    "Work Habits",
    "Accessories",
    "Psychosocial",
]

CAT_ICONS = {
    "Chair & Posture": "🪑",
    "Screen & Display": "🖥️",
    "Keyboard & Mouse": "⌨️",
    "Lighting": "💡",
    "Environment": "🌡️",
    "Work Habits": "⏱️",
    "Accessories": "🧰",
    "Psychosocial": "🧠",
}

CAT_COLORS = {
    "Chair & Posture": "#0EA5E9",
    "Screen & Display": "#8B5CF6",
    "Keyboard & Mouse": "#10B981",
    "Lighting": "#F59E0B",
    "Environment": "#EF4444",
    "Work Habits": "#06B6D4",
    "Accessories": "#F97316",
    "Psychosocial": "#EC4899",
}

RECOMMENDATIONS = {
    "Chair & Posture": [
        "Adjust chair height so your feet rest flat or use a footrest.",
        "Use lumbar support at the curve of your lower back.",
        "Keep thighs roughly parallel to the floor and avoid long slouched sitting.",
    ],
    "Screen & Display": [
        "Raise your monitor so the top edge is near eye level.",
        "Keep the screen about 50-70 cm away from your eyes.",
        "Reduce glare by moving the screen away from direct window or lamp reflection.",
    ],
    "Keyboard & Mouse": [
        "Keep mouse close to the keyboard at the same height.",
        "Keep wrists straight and relaxed while typing.",
        "Use an external keyboard and mouse if working on a laptop for long periods.",
    ],
    "Lighting": [
        "Use soft, even room lighting instead of harsh direct light.",
        "Enable blue-light or reading mode during long screen sessions.",
        "Take regular eye breaks before discomfort begins.",
    ],
    "Environment": [
        "Improve ventilation by opening a window or using air circulation.",
        "Reduce noise with headphones, quiet zones, or white noise.",
        "Keep the desk clear so movement and posture are not restricted.",
    ],
    "Work Habits": [
        "Set a timer for a 5-minute movement break every hour.",
        "Stretch neck, shoulders, back, and wrists during breaks.",
        "Use the 20-20-20 eye rule for long screen work.",
    ],
    "Accessories": [
        "Use a monitor/laptop stand to raise screen height.",
        "Use a document holder if copying from papers.",
        "Consider a footrest, wrist rest, or ergonomic mouse if discomfort continues.",
    ],
    "Psychosocial": [
        "Break large tasks into smaller steps to reduce overload.",
        "Discuss workload or discomfort early instead of waiting until pain increases.",
        "Add screen-free recovery time after long work sessions.",
    ],
}

# =========================================================
# DATABASE
# =========================================================
def get_conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_db() -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT DEFAULT '',
            department TEXT DEFAULT 'Engineering',
            role TEXT DEFAULT 'user',
            age INTEGER DEFAULT 0,
            gender TEXT DEFAULT '',
            height_cm REAL DEFAULT 0,
            weight_kg REAL DEFAULT 0,
            bmi REAL DEFAULT 0,
            activity TEXT DEFAULT '',
            medical_history TEXT DEFAULT '',
            created TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            score REAL,
            risk_level TEXT,
            answers TEXT,
            cat_scores TEXT,
            notes TEXT DEFAULT '',
            created TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """
    )

    admin_pw = hash_password("admin123")
    demo_pw = hash_password("demo123")
    cur.execute(
        """
        INSERT OR IGNORE INTO users
        (username,password,full_name,email,department,role,age,gender,height_cm,weight_kg,activity)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """,
        ("admin", admin_pw, "Administrator", "admin@example.com", "IT", "admin", 30, "Prefer not to say", 175, 75, "Moderate"),
    )
    cur.execute(
        """
        INSERT OR IGNORE INTO users
        (username,password,full_name,email,department,role,age,gender,height_cm,weight_kg,activity)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """,
        ("demo", demo_pw, "Demo User", "demo@example.com", "Engineering", "user", 22, "Male", 175, 70, "Moderate"),
    )
    conn.commit()
    conn.close()


def login_user(username: str, password: str):
    conn = get_conn()
    row = conn.execute(
        """
        SELECT id, username, full_name, email, department, role, age, gender,
               height_cm, weight_kg, bmi, activity, medical_history
        FROM users
        WHERE username=? AND password=?
        """,
        (username.strip(), hash_password(password)),
    ).fetchone()
    conn.close()
    if not row:
        return None
    keys = [
        "id", "username", "full_name", "email", "department", "role", "age", "gender",
        "height_cm", "weight_kg", "bmi", "activity", "medical_history",
    ]
    return dict(zip(keys, row))


def register_user(username: str, password: str, full_name: str, email: str, department: str) -> Tuple[bool, str]:
    if not username.strip() or not password.strip() or not full_name.strip():
        return False, "Username, password, and full name are required."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."

    conn = get_conn()
    try:
        conn.execute(
            """
            INSERT INTO users (username,password,full_name,email,department)
            VALUES (?,?,?,?,?)
            """,
            (username.strip(), hash_password(password), full_name.strip(), email.strip(), department.strip() or "General"),
        )
        conn.commit()
        return True, "Account created successfully. You can log in now."
    except sqlite3.IntegrityError:
        return False, "That username already exists."
    finally:
        conn.close()


def save_profile(user_id: int, age: int, gender: str, height_cm: float, weight_kg: float, activity: str, history: str) -> float:
    bmi = round(weight_kg / ((height_cm / 100) ** 2), 1) if height_cm > 0 else 0
    conn = get_conn()
    conn.execute(
        """
        UPDATE users
        SET age=?, gender=?, height_cm=?, weight_kg=?, bmi=?, activity=?, medical_history=?
        WHERE id=?
        """,
        (age, gender, height_cm, weight_kg, bmi, activity, history, user_id),
    )
    conn.commit()
    conn.close()
    return bmi


def refresh_user(user_id: int):
    conn = get_conn()
    row = conn.execute(
        """
        SELECT id, username, full_name, email, department, role, age, gender,
               height_cm, weight_kg, bmi, activity, medical_history
        FROM users WHERE id=?
        """,
        (user_id,),
    ).fetchone()
    conn.close()
    if row:
        keys = [
            "id", "username", "full_name", "email", "department", "role", "age", "gender",
            "height_cm", "weight_kg", "bmi", "activity", "medical_history",
        ]
        st.session_state.user = dict(zip(keys, row))


def save_assessment(user_id: int, username: str, score: float, risk: str, answers: Dict, cat_scores: Dict, notes: str) -> None:
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO assessments (user_id, username, score, risk_level, answers, cat_scores, notes)
        VALUES (?,?,?,?,?,?,?)
        """,
        (user_id, username, score, risk, json.dumps(answers), json.dumps(cat_scores), notes),
    )
    conn.commit()
    conn.close()


def load_user_assessments(username: str):
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT id, score, risk_level, cat_scores, notes, created
        FROM assessments
        WHERE username=?
        ORDER BY created DESC
        """,
        (username,),
    ).fetchall()
    conn.close()
    return rows


def load_all_assessments():
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT a.id, a.username, u.full_name, u.department, a.score, a.risk_level, a.created
        FROM assessments a
        LEFT JOIN users u ON a.user_id=u.id
        ORDER BY a.created DESC
        """
    ).fetchall()
    conn.close()
    return rows


def load_all_users():
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT id, username, full_name, email, department, role, created
        FROM users
        ORDER BY created DESC
        """
    ).fetchall()
    conn.close()
    return rows


init_db()

# =========================================================
# SESSION STATE
# =========================================================
def init_session() -> None:
    defaults = {
        "logged_in": False,
        "user": None,
        "page": "Dashboard",
        "answers": {},
        "last_result": None,
        "assessment_saved": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session()

# =========================================================
# SCORING
# =========================================================
def option_score(question: Dict, selected_index: int) -> float:
    if question["type"] == "likert":
        return float(selected_index)

    options_count = len(question["options"])
    if options_count <= 1:
        return 0.0
    raw = selected_index / (options_count - 1) * 4
    if question.get("direction") == "reverse":
        raw = 4 - raw
    return round(raw, 2)


def compute_scores(answers: Dict[int, float]) -> Tuple[float, Dict[str, float]]:
    total_weight = sum(q["weight"] for q in QUESTIONS)
    weighted_sum = sum(answers.get(q["id"], 0) * q["weight"] for q in QUESTIONS)
    overall = round((weighted_sum / (4 * total_weight)) * 100, 1)

    cat_scores = {}
    for category in CATEGORIES:
        qs = [q for q in QUESTIONS if q["category"] == category]
        cat_weight = sum(q["weight"] for q in qs)
        cat_sum = sum(answers.get(q["id"], 0) * q["weight"] for q in qs)
        cat_scores[category] = round((cat_sum / (4 * cat_weight)) * 100, 1) if cat_weight else 0
    return overall, cat_scores


def risk_label(score: float) -> Tuple[str, str, str]:
    if score >= 75:
        return "Low Risk", "#10B981", "green"
    if score >= 50:
        return "Moderate Risk", "#F59E0B", "amber"
    return "High Risk", "#EF4444", "red"

# =========================================================
# CHARTS
# =========================================================
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#334155"),
    margin=dict(l=20, r=20, t=35, b=20),
)


def category_bar(cat_scores: Dict[str, float]):
    fig = go.Figure(
        go.Bar(
            x=list(cat_scores.values()),
            y=list(cat_scores.keys()),
            orientation="h",
            marker=dict(color=[CAT_COLORS.get(c, "#0EA5E9") for c in cat_scores]),
            text=[f"{v:.1f}%" for v in cat_scores.values()],
            textposition="outside",
        )
    )
    fig.update_layout(
        **PLOT_LAYOUT,
        height=390,
        xaxis=dict(range=[0, 110], ticksuffix="%", gridcolor="rgba(14,165,233,.14)"),
        yaxis=dict(autorange="reversed"),
        showlegend=False,
    )
    return fig


def radar_chart(cat_scores: Dict[str, float]):
    cats = list(cat_scores.keys())
    vals = list(cat_scores.values())
    fig = go.Figure(
        go.Scatterpolar(
            r=vals + vals[:1],
            theta=cats + cats[:1],
            fill="toself",
            fillcolor="rgba(14,165,233,.16)",
            line=dict(color="#0EA5E9", width=3),
            marker=dict(color="#8B5CF6", size=7),
        )
    )
    fig.update_layout(
        **PLOT_LAYOUT,
        height=390,
        polar=dict(
            bgcolor="rgba(255,255,255,.45)",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(14,165,233,.16)"),
            angularaxis=dict(gridcolor="rgba(14,165,233,.12)"),
        ),
        showlegend=False,
    )
    return fig


def history_chart(rows):
    dates = [r[5][:10] for r in rows][::-1]
    scores = [r[1] for r in rows][::-1]
    colors = [risk_label(s)[1] for s in scores]
    fig = go.Figure(
        go.Scatter(
            x=dates,
            y=scores,
            mode="lines+markers",
            line=dict(color="#0EA5E9", width=3, shape="spline"),
            marker=dict(size=10, color=colors, line=dict(width=2, color="#FFFFFF")),
            fill="tozeroy",
            fillcolor="rgba(14,165,233,.10)",
        )
    )
    fig.update_layout(
        **PLOT_LAYOUT,
        height=300,
        yaxis=dict(range=[0, 105], ticksuffix="%", gridcolor="rgba(14,165,233,.14)"),
        xaxis=dict(gridcolor="rgba(14,165,233,.10)"),
    )
    return fig

# =========================================================
# PDF REPORT
# =========================================================
def safe_text(value) -> str:
    text = str(value)
    return text.encode("latin-1", errors="replace").decode("latin-1")


def generate_pdf(user: Dict, score: float, risk: str, cat_scores: Dict[str, float], notes: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_fill_color(14, 165, 233)
    pdf.rect(0, 0, 210, 35, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 17)
    pdf.set_xy(14, 9)
    pdf.cell(0, 8, safe_text("WORKSTATION SAFETY SCORER"), ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.set_x(14)
    pdf.cell(0, 6, safe_text(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"), ln=True)

    pdf.set_text_color(15, 23, 42)
    pdf.set_xy(14, 45)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, safe_text("User Details"), ln=True)
    pdf.set_font("Arial", "", 10)
    details = [
        ("Name", user.get("full_name", "")),
        ("Username", user.get("username", "")),
        ("Department", user.get("department", "")),
        ("BMI", user.get("bmi", "")),
    ]
    for label, value in details:
        pdf.cell(42, 7, safe_text(label + ":"))
        pdf.cell(0, 7, safe_text(value), ln=True)

    pdf.ln(4)
    pdf.set_font("Arial", "B", 13)
    risk_color = (16, 185, 129) if score >= 75 else (245, 158, 11) if score >= 50 else (239, 68, 68)
    pdf.set_text_color(*risk_color)
    pdf.cell(0, 10, safe_text(f"Overall Score: {score:.1f}% - {risk}"), ln=True)

    pdf.set_fill_color(226, 232, 240)
    pdf.rect(14, pdf.get_y(), 180, 7, "F")
    pdf.set_fill_color(*risk_color)
    pdf.rect(14, pdf.get_y(), 180 * score / 100, 7, "F")
    pdf.ln(14)

    pdf.set_text_color(15, 23, 42)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, safe_text("Category Breakdown"), ln=True)
    pdf.set_font("Arial", "B", 9)
    pdf.set_fill_color(224, 242, 254)
    pdf.cell(85, 7, safe_text("Category"), fill=True)
    pdf.cell(35, 7, safe_text("Score"), fill=True)
    pdf.cell(55, 7, safe_text("Risk"), fill=True, ln=True)
    pdf.set_font("Arial", "", 9)

    for category, value in sorted(cat_scores.items(), key=lambda item: item[1]):
        r_label, _, _ = risk_label(value)
        pdf.cell(85, 7, safe_text(category))
        pdf.cell(35, 7, safe_text(f"{value:.1f}%"))
        pdf.cell(55, 7, safe_text(r_label), ln=True)

    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, safe_text("Priority Recommendations"), ln=True)
    pdf.set_font("Arial", "", 9)
    for category, value in sorted(cat_scores.items(), key=lambda item: item[1]):
        if value < 75:
            pdf.set_font("Arial", "B", 9)
            pdf.cell(0, 7, safe_text(f"{category} ({value:.1f}%)"), ln=True)
            pdf.set_font("Arial", "", 9)
            for rec in RECOMMENDATIONS.get(category, []):
                pdf.multi_cell(0, 5, safe_text("- " + rec))
            pdf.ln(2)

    if notes.strip():
        pdf.ln(3)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, safe_text("Notes"), ln=True)
        pdf.set_font("Arial", "", 9)
        pdf.multi_cell(0, 5, safe_text(notes))

    return bytes(pdf.output(dest="S"))

# =========================================================
# REUSABLE UI
# =========================================================
def hero(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="hero">
          <h1>{title}</h1>
          <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi(col, value: str, label: str, sub: str = "", color: str = "#0EA5E9") -> None:
    col.markdown(
        f"""
        <div class="kpi-card">
          <div class="kpi-value" style="color:{color};">{value}</div>
          <div class="kpi-label">{label}</div>
          <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_badge(score: float) -> str:
    label, _, cls = risk_label(score)
    return f'<span class="badge {cls}">{label}</span>'


def navigation() -> None:
    user = st.session_state.user
    with st.sidebar:
        st.markdown(
            f"""
            <div style="padding:18px 8px 10px;">
              <div style="font-family:Outfit,sans-serif;font-size:1.55rem;font-weight:800;color:#0284C7;">🏥 WSS</div>
              <div style="color:#64748B;font-size:.82rem;margin-top:4px;">Workstation Safety Scorer</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.caption(f"Signed in as **{user['full_name']}**")
        st.caption(f"Role: `{user['role']}`")

        pages = ["Dashboard", "Assessment", "History", "Analytics", "Profile"]
        if user["role"] == "admin":
            pages.append("Admin")

        # This fixes the dashboard open/close problem by keeping one source of truth.
        if st.session_state.page not in pages:
            st.session_state.page = "Dashboard"

        selected = st.radio(
            "Navigation",
            pages,
            index=pages.index(st.session_state.page),
            label_visibility="collapsed",
        )
        st.session_state.page = selected

        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            for key in ["logged_in", "user", "answers", "last_result", "assessment_saved"]:
                if key in st.session_state:
                    del st.session_state[key]
            init_session()
            st.rerun()

# =========================================================
# LOGIN PAGE
# =========================================================
def login_page() -> None:
    left, center, right = st.columns([1, 1.3, 1])
    with center:
        st.markdown(
            """
            <div style="text-align:center;padding:34px 0 14px;">
              <div style="font-family:Outfit,sans-serif;font-size:2.5rem;font-weight:800;
                          background:linear-gradient(135deg,#0284C7,#8B5CF6);
                          -webkit-background-clip:text;-webkit-text-fill-color:transparent;">WSS</div>
              <div style="font-family:Outfit,sans-serif;color:#64748B;font-weight:800;letter-spacing:2px;">
                WORKSTATION SAFETY SCORER
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        tab_login, tab_register = st.tabs(["Login", "Register"])

        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Username", value="demo")
                password = st.text_input("Password", type="password", value="demo123")
                submitted = st.form_submit_button("Login", use_container_width=True)
                if submitted:
                    user = login_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.page = "Dashboard"
                        st.success("Login successful.")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

            st.info("Demo login: `demo / demo123`  |  Admin login: `admin / admin123`")

        with tab_register:
            with st.form("register_form"):
                full_name = st.text_input("Full name")
                username = st.text_input("Choose username")
                email = st.text_input("Email")
                department = st.text_input("Department", value="Engineering")
                password = st.text_input("Choose password", type="password")
                submitted = st.form_submit_button("Create Account", use_container_width=True)
                if submitted:
                    ok, msg = register_user(username, password, full_name, email, department)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

# =========================================================
# DASHBOARD
# =========================================================
def page_dashboard() -> None:
    user = st.session_state.user
    hero(
        f"Welcome back, <span>{user['full_name'].split()[0]}</span>",
        "Review your workstation safety, track ergonomic risk, and download professional reports.",
    )

    rows = load_user_assessments(user["username"])
    latest = rows[0] if rows else None

    c1, c2, c3, c4 = st.columns(4)
    if latest:
        score = latest[1]
        risk, color, _ = risk_label(score)
        cat_scores = json.loads(latest[3])
        lowest_cat = min(cat_scores, key=cat_scores.get)
        kpi(c1, f"{score:.1f}%", "Latest Score", risk, color)
        kpi(c2, str(len(rows)), "Assessments", "Completed reports", "#8B5CF6")
        kpi(c3, lowest_cat, "Priority Area", f"{cat_scores[lowest_cat]:.1f}%", CAT_COLORS.get(lowest_cat, "#EF4444"))
        kpi(c4, latest[5][:10], "Last Check", "Assessment date", "#10B981")
    else:
        kpi(c1, "--", "Latest Score", "No assessment yet", "#0EA5E9")
        kpi(c2, "0", "Assessments", "Start your first one", "#8B5CF6")
        kpi(c3, "--", "Priority Area", "Unknown", "#EF4444")
        kpi(c4, "New", "Status", "Ready to begin", "#10B981")

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    if not latest:
        st.markdown(
            """
            <div class="card">
              <div class="section-title">GET STARTED</div>
              <p style="color:#334155;font-size:1rem;line-height:1.7;">
                You have not completed an ergonomic assessment yet. Start the assessment to calculate your workstation risk score,
                identify weak categories, and generate a PDF report.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Start Assessment", use_container_width=True):
            st.session_state.page = "Assessment"
            st.rerun()
        return

    cat_scores = json.loads(latest[3])
    col_a, col_b = st.columns([1.2, 1])
    with col_a:
        st.markdown("<div class='section-title'>CATEGORY PERFORMANCE</div>", unsafe_allow_html=True)
        st.plotly_chart(category_bar(cat_scores), use_container_width=True, config={"displayModeBar": False})
    with col_b:
        st.markdown("<div class='section-title'>RISK SNAPSHOT</div>", unsafe_allow_html=True)
        label, color, cls = risk_label(latest[1])
        st.markdown(
            f"""
            <div class="card-soft">
              <div style="font-size:3rem;font-family:JetBrains Mono,monospace;font-weight:800;color:{color};">{latest[1]:.1f}%</div>
              {risk_badge(latest[1])}
              <div class="risk-bar-wrap"><div class="risk-bar-fill" style="width:{latest[1]}%;background:{color};"></div></div>
              <p style="color:#64748B;margin-top:16px;line-height:1.6;">
                Your lowest categories should be improved first. Even small changes like monitor height,
                movement breaks, and wrist position can reduce risk.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if len(rows) > 1:
        st.markdown("<div class='section-title'>SCORE HISTORY</div>", unsafe_allow_html=True)
        st.plotly_chart(history_chart(rows), use_container_width=True, config={"displayModeBar": False})

# =========================================================
# ASSESSMENT
# =========================================================
def page_assessment() -> None:
    hero(
        "Ergonomic <span>Assessment</span>",
        "Answer each question carefully. Questions are separated clearly by category to avoid merging or confusion.",
    )

    st.markdown(
        """
        <div class="alert-warn">
          <b>Important:</b> All questions must be answered before results are calculated.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("assessment_form"):
        selected_answers = {}

        for category in CATEGORIES:
            cat_questions = [q for q in QUESTIONS if q["category"] == category]
            st.markdown(
                f"""
                <div class="card">
                  <div class="section-title">{CAT_ICONS.get(category,'')} {category}</div>
                """,
                unsafe_allow_html=True,
            )

            for q in cat_questions:
                options = LIKERT_OPTIONS if q["type"] == "likert" else q["options"]
                st.markdown(
                    f"""
                    <div class="question-card">
                      <div class="question-number">QUESTION {q['id']:02d}</div>
                      <div class="question-text">{q['text']}</div>
                      <div class="helper-text">{q.get('helper','')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                answer = st.radio(
                    "Choose one answer",
                    options,
                    index=None,
                    key=f"q_{q['id']}",
                    label_visibility="collapsed",
                )
                if answer is not None:
                    selected_index = options.index(answer)
                    selected_answers[q["id"]] = option_score(q, selected_index)

            st.markdown("</div>", unsafe_allow_html=True)

        notes = st.text_area("Optional notes", placeholder="Add any extra workstation observations here...", height=90)
        submitted = st.form_submit_button("Calculate Results", use_container_width=True)

    if submitted:
        if len(selected_answers) != len(QUESTIONS):
            missing = len(QUESTIONS) - len(selected_answers)
            st.error(f"Please answer all questions first. Missing answers: {missing}")
            return

        score, cat_scores = compute_scores(selected_answers)
        risk, _, _ = risk_label(score)
        st.session_state.last_result = {
            "score": score,
            "risk": risk,
            "cat_scores": cat_scores,
            "answers": selected_answers,
            "notes": notes,
        }
        st.session_state.assessment_saved = False
        st.rerun()

    if st.session_state.last_result:
        result = st.session_state.last_result
        score = result["score"]
        risk, color, _ = risk_label(score)

        st.markdown("<div class='section-title'>ASSESSMENT RESULT</div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="card">
              <div style="font-family:JetBrains Mono,monospace;font-size:3rem;font-weight:800;color:{color};">{score:.1f}%</div>
              {risk_badge(score)}
              <div class="risk-bar-wrap"><div class="risk-bar-fill" style="width:{score}%;background:{color};"></div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(category_bar(result["cat_scores"]), use_container_width=True, config={"displayModeBar": False})
        with col2:
            st.plotly_chart(radar_chart(result["cat_scores"]), use_container_width=True, config={"displayModeBar": False})

        st.markdown("<div class='section-title'>PERSONALIZED RECOMMENDATIONS</div>", unsafe_allow_html=True)
        for category, value in sorted(result["cat_scores"].items(), key=lambda item: item[1]):
            if value < 75:
                st.markdown(
                    f"""
                    <div class="card-soft" style="margin-bottom:14px;">
                      <b>{CAT_ICONS.get(category,'')} {category}</b> — {value:.1f}%<br>
                      <ul>
                        {''.join(f'<li>{rec}</li>' for rec in RECOMMENDATIONS.get(category, []))}
                      </ul>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        save_col, pdf_col = st.columns(2)
        with save_col:
            if st.button("Save Assessment", use_container_width=True, disabled=st.session_state.assessment_saved):
                user = st.session_state.user
                save_assessment(
                    user["id"],
                    user["username"],
                    result["score"],
                    result["risk"],
                    result["answers"],
                    result["cat_scores"],
                    result["notes"],
                )
                st.session_state.assessment_saved = True
                st.success("Assessment saved successfully.")
                st.rerun()

        with pdf_col:
            pdf_bytes = generate_pdf(
                st.session_state.user,
                result["score"],
                result["risk"],
                result["cat_scores"],
                result["notes"],
            )
            st.download_button(
                "Download PDF Report",
                data=pdf_bytes,
                file_name=f"workstation_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

# =========================================================
# HISTORY
# =========================================================
def page_history() -> None:
    hero("Assessment <span>History</span>", "View your previous ergonomic scores and progress over time.")
    rows = load_user_assessments(st.session_state.user["username"])
    if not rows:
        st.info("No saved assessments yet.")
        return

    df = pd.DataFrame(rows, columns=["ID", "Score", "Risk", "Category Scores", "Notes", "Created"])
    display_df = df.copy()
    display_df["Score"] = display_df["Score"].map(lambda x: f"{x:.1f}%")
    st.dataframe(display_df[["ID", "Score", "Risk", "Notes", "Created"]], use_container_width=True, hide_index=True)

    st.markdown("<div class='section-title'>TREND</div>", unsafe_allow_html=True)
    st.plotly_chart(history_chart(rows), use_container_width=True, config={"displayModeBar": False})

# =========================================================
# ANALYTICS
# =========================================================
def page_analytics() -> None:
    hero("Detailed <span>Analytics</span>", "Compare your ergonomic categories and identify the most urgent improvement areas.")
    rows = load_user_assessments(st.session_state.user["username"])
    if not rows:
        st.info("Complete and save an assessment first to see analytics.")
        return

    latest = rows[0]
    cat_scores = json.loads(latest[3])
    best = max(cat_scores, key=cat_scores.get)
    worst = min(cat_scores, key=cat_scores.get)

    c1, c2, c3 = st.columns(3)
    kpi(c1, best, "Strongest Area", f"{cat_scores[best]:.1f}%", CAT_COLORS.get(best, "#10B981"))
    kpi(c2, worst, "Weakest Area", f"{cat_scores[worst]:.1f}%", CAT_COLORS.get(worst, "#EF4444"))
    kpi(c3, f"{latest[1]:.1f}%", "Overall Score", latest[2], risk_label(latest[1])[1])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='section-title'>BAR BREAKDOWN</div>", unsafe_allow_html=True)
        st.plotly_chart(category_bar(cat_scores), use_container_width=True, config={"displayModeBar": False})
    with col2:
        st.markdown("<div class='section-title'>RADAR VIEW</div>", unsafe_allow_html=True)
        st.plotly_chart(radar_chart(cat_scores), use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div class='section-title'>PRIORITY TABLE</div>", unsafe_allow_html=True)
    priority = pd.DataFrame(
        [
            {
                "Category": c,
                "Score": f"{s:.1f}%",
                "Priority": "Urgent" if s < 50 else "Improve" if s < 75 else "Maintain",
            }
            for c, s in sorted(cat_scores.items(), key=lambda item: item[1])
        ]
    )
    st.dataframe(priority, use_container_width=True, hide_index=True)

# =========================================================
# PROFILE
# =========================================================
def page_profile() -> None:
    user = st.session_state.user
    hero("Health <span>Profile</span>", "Update your basic health profile for a more complete ergonomic record.")

    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        age = c1.number_input("Age", min_value=10, max_value=100, value=int(user.get("age") or 22))
        gender_options = ["Prefer not to say", "Male", "Female", "Non-binary / Other"]
        current_gender = user.get("gender") if user.get("gender") in gender_options else "Prefer not to say"
        gender = c2.selectbox("Gender", gender_options, index=gender_options.index(current_gender))

        c3, c4 = st.columns(2)
        height = c3.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=float(user.get("height_cm") or 170), step=0.5)
        weight = c4.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=float(user.get("weight_kg") or 70), step=0.5)

        bmi = round(weight / ((height / 100) ** 2), 1)
        bmi_status = "Normal" if 18.5 <= bmi < 25 else "Review"
        st.markdown(
            f"""
            <div class="card-soft">
              <b>Calculated BMI:</b> {bmi} — {bmi_status}
            </div>
            """,
            unsafe_allow_html=True,
        )

        activity_options = ["Sedentary", "Light", "Moderate", "Active", "Very Active"]
        current_activity = user.get("activity") if user.get("activity") in activity_options else "Moderate"
        activity = st.selectbox("Activity Level", activity_options, index=activity_options.index(current_activity))
        history = st.text_area("Medical History / Notes", value=user.get("medical_history") or "", height=100)

        if st.form_submit_button("Update Profile", use_container_width=True):
            save_profile(user["id"], age, gender, height, weight, activity, history)
            refresh_user(user["id"])
            st.success("Profile updated successfully.")
            st.rerun()

# =========================================================
# ADMIN
# =========================================================
def page_admin() -> None:
    if st.session_state.user["role"] != "admin":
        st.error("Access denied.")
        return

    hero("Admin <span>Dashboard</span>", "Monitor users, assessments, risk distribution, and platform performance.")
    users = load_all_users()
    assessments = load_all_assessments()

    scores = [row[4] for row in assessments]
    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, str(len(users)), "Total Users", "Registered accounts", "#0EA5E9")
    kpi(c2, str(len(assessments)), "Assessments", "Saved records", "#8B5CF6")
    kpi(c3, f"{sum(scores)/len(scores):.1f}%" if scores else "--", "Average Score", "All users", "#10B981")
    kpi(c4, str(sum(1 for row in assessments if row[5] == "High Risk")), "High Risk", "Needs attention", "#EF4444")

    tab1, tab2, tab3 = st.tabs(["Overview", "Users", "Assessments"])
    with tab1:
        if assessments:
            risk_counts = pd.Series([row[5] for row in assessments]).value_counts()
            fig = go.Figure(
                go.Pie(
                    labels=risk_counts.index,
                    values=risk_counts.values,
                    hole=0.45,
                    marker=dict(colors=["#10B981" if x == "Low Risk" else "#F59E0B" if x == "Moderate Risk" else "#EF4444" for x in risk_counts.index]),
                )
            )
            fig.update_layout(**PLOT_LAYOUT, height=360)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No assessments yet.")

    with tab2:
        df_users = pd.DataFrame(users, columns=["ID", "Username", "Full Name", "Email", "Department", "Role", "Created"])
        st.dataframe(df_users, use_container_width=True, hide_index=True)

    with tab3:
        df_assess = pd.DataFrame(assessments, columns=["ID", "Username", "Full Name", "Department", "Score", "Risk", "Created"])
        if not df_assess.empty:
            df_assess["Score"] = df_assess["Score"].map(lambda x: f"{x:.1f}%")
        st.dataframe(df_assess, use_container_width=True, hide_index=True)
        csv = df_assess.to_csv(index=False).encode("utf-8")
        st.download_button("Export CSV", data=csv, file_name="assessments.csv", mime="text/csv")

# =========================================================
# MAIN APP
# =========================================================
def main() -> None:
    if not st.session_state.logged_in:
        login_page()
        return

    navigation()
    page = st.session_state.page

    if page == "Dashboard":
        page_dashboard()
    elif page == "Assessment":
        page_assessment()
    elif page == "History":
        page_history()
    elif page == "Analytics":
        page_analytics()
    elif page == "Profile":
        page_profile()
    elif page == "Admin":
        page_admin()


if __name__ == "__main__":
    main()
