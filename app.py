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
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700;800&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
    box-sizing: border-box;
}

/* ── GLOBAL BACKGROUND ── */
.stApp {
    background: radial-gradient(ellipse at 10% 20%, #0d1f35 0%, #0B0F19 40%, #080c14 100%) !important;
}
.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 2rem !important;
    background: transparent !important;
    max-width: 1400px !important;
}
#MainMenu, footer, header { visibility: hidden; }

/* ── PARTICLES BACKGROUND ── */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        radial-gradient(1px 1px at 15% 25%, rgba(0,240,255,0.4) 0%, transparent 100%),
        radial-gradient(1px 1px at 75% 15%, rgba(0,240,255,0.3) 0%, transparent 100%),
        radial-gradient(1px 1px at 45% 65%, rgba(0,240,255,0.35) 0%, transparent 100%),
        radial-gradient(1px 1px at 85% 55%, rgba(99,102,241,0.4) 0%, transparent 100%),
        radial-gradient(1px 1px at 30% 85%, rgba(0,240,255,0.25) 0%, transparent 100%),
        radial-gradient(1px 1px at 60% 40%, rgba(99,102,241,0.3) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 90% 80%, rgba(0,240,255,0.45) 0%, transparent 100%),
        radial-gradient(1px 1px at 20% 50%, rgba(99,102,241,0.25) 0%, transparent 100%);
    pointer-events: none;
    z-index: 0;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #06090f 0%, #0a1220 60%, #060810 100%) !important;
    border-right: 1px solid rgba(0,240,255,0.1) !important;
    box-shadow: 4px 0 40px rgba(0,0,0,0.6) !important;
}
[data-testid="stSidebar"] > div { background: transparent !important; }
[data-testid="stSidebar"] * { color: #e2eaf4 !important; }
[data-testid="stSidebar"] .stRadio > div > label {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(0,240,255,0.06) !important;
    border-radius: 10px !important;
    padding: 9px 14px !important;
    margin: 3px 0 !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: #A0AEC0 !important;
    transition: all 0.25s ease !important;
    display: block !important;
}
[data-testid="stSidebar"] .stRadio > div > label:hover {
    background: rgba(0,240,255,0.06) !important;
    border-color: rgba(0,240,255,0.2) !important;
    color: #00F0FF !important;
}
[data-testid="stSidebar"] hr {
    border: none !important;
    border-top: 1px solid rgba(0,240,255,0.08) !important;
    margin: 0.8rem 0 !important;
}

/* ── KEYFRAME ANIMATIONS ── */
@keyframes pulseGlow {
    0%, 100% { opacity: 0.5; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.08); }
}
@keyframes ripple {
    0% { transform: scale(1); opacity: 0.8; }
    100% { transform: scale(3); opacity: 0; }
}
@keyframes countUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes slideIn {
    from { opacity: 0; transform: translateX(-12px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes glowPulse {
    0%, 100% { box-shadow: 0 0 8px rgba(0,240,255,0.3), 0 0 20px rgba(0,240,255,0.1); }
    50% { box-shadow: 0 0 16px rgba(0,240,255,0.6), 0 0 40px rgba(0,240,255,0.2); }
}
@keyframes borderGlow {
    0%, 100% { border-color: rgba(0,240,255,0.12); }
    50% { border-color: rgba(0,240,255,0.28); }
}
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-4px); }
}
@keyframes spinSlow {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
@keyframes navPulse {
    0%, 100% { opacity: 0.6; }
    50% { opacity: 1; }
}

/* ── HERO BANNER ── */
.hero-banner {
    background:
        radial-gradient(ellipse at 15% 50%, rgba(0,240,255,0.05) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 20%, rgba(99,102,241,0.07) 0%, transparent 50%),
        rgba(255,255,255,0.025);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(0,240,255,0.14);
    border-radius: 22px;
    padding: 2.2rem 2.8rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    box-shadow:
        0 24px 64px rgba(0,0,0,0.55),
        0 0 0 1px rgba(255,255,255,0.03),
        inset 0 1px 0 rgba(255,255,255,0.07);
    animation: borderGlow 4s ease-in-out infinite;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -120px; right: -120px;
    width: 450px; height: 450px;
    background: radial-gradient(circle, rgba(0,240,255,0.07) 0%, transparent 65%);
    border-radius: 50%;
    animation: pulseGlow 5s ease-in-out infinite;
}
.hero-banner::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(0,240,255,0.4) 50%, transparent 100%);
}
.hero-eyebrow {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #00F0FF;
    opacity: 0.8;
    margin-bottom: 0.5rem;
}
.hero-title {
    font-size: 2.3rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.8px;
    margin: 0 0 0.3rem;
    line-height: 1.15;
    text-shadow: 0 0 60px rgba(0,240,255,0.25), 0 2px 8px rgba(0,0,0,0.6);
}
.hero-title .glow-text {
    background: linear-gradient(90deg, #00F0FF 0%, #a5b4fc 60%, #00F0FF 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 4s linear infinite;
}
@keyframes shimmer {
    0% { background-position: 0% center; }
    100% { background-position: 200% center; }
}
.hero-sub {
    font-size: 0.85rem;
    color: #A0AEC0;
    font-weight: 400;
    letter-spacing: 0.2px;
    margin-top: 0.15rem;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(0,240,255,0.07);
    border: 1px solid rgba(0,240,255,0.18);
    color: #00F0FF;
    font-size: 0.66rem;
    font-weight: 700;
    padding: 4px 14px;
    border-radius: 20px;
    margin-top: 1rem;
    letter-spacing: 1.2px;
    text-transform: uppercase;
}

/* ── METRIC TILES ── */
.metric-tile {
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(0,240,255,0.1);
    border-radius: 16px;
    padding: 1.4rem 1.2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow:
        0 8px 32px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.05);
    transition: all 0.3s ease;
    animation: borderGlow 5s ease-in-out infinite, float 6s ease-in-out infinite;
}
.metric-tile::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,240,255,0.35), transparent);
}
.metric-tile:hover {
    border-color: rgba(0,240,255,0.3);
    box-shadow: 0 12px 40px rgba(0,0,0,0.5), 0 0 20px rgba(0,240,255,0.08);
    transform: translateY(-3px);
}
.metric-tile .icon {
    font-size: 1.5rem;
    margin-bottom: 6px;
    filter: drop-shadow(0 0 8px rgba(0,240,255,0.5));
}
.metric-tile .val {
    font-size: 2.1rem;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1;
    text-shadow: 0 0 20px rgba(0,240,255,0.4), 0 2px 4px rgba(0,0,0,0.5);
    animation: countUp 0.8s ease-out both;
}
.metric-tile .lbl {
    font-size: 0.7rem;
    color: #A0AEC0;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 5px;
}

/* ── SECTION CARDS ── */
.section-card {
    background: rgba(255,255,255,0.025);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(0,240,255,0.1);
    border-radius: 18px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
    box-shadow:
        0 8px 32px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.05);
    animation: borderGlow 6s ease-in-out infinite;
}
.section-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,240,255,0.25), transparent);
}
.section-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 1rem;
    letter-spacing: 0.3px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(0,240,255,0.2), transparent);
}

/* ── SCORE BADGES ── */
.score-badge {
    font-size: 3.8rem;
    font-weight: 800;
    padding: 0.6rem 1.8rem;
    border-radius: 16px;
    letter-spacing: -2px;
    display: inline-block;
    position: relative;
}
.badge-excellent {
    background: rgba(5,150,105,0.15);
    color: #34d399;
    border: 1px solid rgba(52,211,153,0.3);
    box-shadow: 0 0 30px rgba(52,211,153,0.15), inset 0 1px 0 rgba(255,255,255,0.06);
    text-shadow: 0 0 20px rgba(52,211,153,0.5);
}
.badge-good {
    background: rgba(0,240,255,0.08);
    color: #00F0FF;
    border: 1px solid rgba(0,240,255,0.25);
    box-shadow: 0 0 30px rgba(0,240,255,0.12), inset 0 1px 0 rgba(255,255,255,0.06);
    text-shadow: 0 0 20px rgba(0,240,255,0.5);
}
.badge-moderate {
    background: rgba(245,158,11,0.1);
    color: #fbbf24;
    border: 1px solid rgba(251,191,36,0.25);
    box-shadow: 0 0 30px rgba(251,191,36,0.12), inset 0 1px 0 rgba(255,255,255,0.06);
    text-shadow: 0 0 20px rgba(251,191,36,0.5);
}
.badge-poor {
    background: rgba(239,68,68,0.1);
    color: #f87171;
    border: 1px solid rgba(248,113,113,0.25);
    box-shadow: 0 0 30px rgba(248,113,113,0.12), inset 0 1px 0 rgba(255,255,255,0.06);
    text-shadow: 0 0 20px rgba(248,113,113,0.5);
}

/* ── QUESTION CARDS ── */
.q-card {
    background: rgba(0,240,255,0.03);
    border-left: 3px solid rgba(0,240,255,0.5);
    border-radius: 0 12px 12px 0;
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.8rem;
    position: relative;
    transition: all 0.2s ease;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
}
.q-card:hover {
    background: rgba(0,240,255,0.05);
    border-left-color: rgba(0,240,255,0.8);
    box-shadow: 0 0 20px rgba(0,240,255,0.05);
}
.q-label {
    font-size: 0.88rem;
    color: #FFFFFF;
    font-weight: 600;
    line-height: 1.45;
}
.q-weight {
    font-size: 0.72rem;
    color: #00F0FF;
    font-weight: 600;
    margin-top: 3px;
    opacity: 0.75;
}

/* ── RISK TAGS ── */
.risk-high {
    background: rgba(239,68,68,0.15);
    color: #f87171;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    border: 1px solid rgba(248,113,113,0.3);
    text-shadow: 0 0 8px rgba(248,113,113,0.4);
}
.risk-medium {
    background: rgba(245,158,11,0.12);
    color: #fbbf24;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    border: 1px solid rgba(251,191,36,0.3);
    text-shadow: 0 0 8px rgba(251,191,36,0.4);
}
.risk-low {
    background: rgba(16,185,129,0.12);
    color: #34d399;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    border: 1px solid rgba(52,211,153,0.3);
    text-shadow: 0 0 8px rgba(52,211,153,0.4);
}

/* ── REC CARD ── */
.rec-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(0,240,255,0.08);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.7rem;
    transition: all 0.2s ease;
    position: relative;
}
.rec-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,240,255,0.15), transparent);
}
.rec-card:hover {
    border-color: rgba(0,240,255,0.18);
    background: rgba(0,240,255,0.03);
}
.rec-text {
    font-size: 0.88rem;
    color: #e2e8f0;
    font-weight: 500;
    margin-top: 5px;
    line-height: 1.5;
}
.rec-cat {
    font-size: 0.74rem;
    color: #A0AEC0;
    font-weight: 600;
    margin-top: 2px;
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, rgba(0,240,255,0.12) 0%, rgba(99,102,241,0.12) 100%) !important;
    color: #00F0FF !important;
    border: 1px solid rgba(0,240,255,0.3) !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.25s ease !important;
    letter-spacing: 0.3px !important;
    box-shadow: 0 0 20px rgba(0,240,255,0.08), inset 0 1px 0 rgba(255,255,255,0.05) !important;
    text-shadow: 0 0 10px rgba(0,240,255,0.5) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(0,240,255,0.2) 0%, rgba(99,102,241,0.2) 100%) !important;
    border-color: rgba(0,240,255,0.5) !important;
    box-shadow: 0 0 30px rgba(0,240,255,0.2), 0 4px 20px rgba(0,0,0,0.3) !important;
    transform: translateY(-2px) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px !important;
    background: rgba(255,255,255,0.03) !important;
    padding: 5px !important;
    border-radius: 12px !important;
    border: 1px solid rgba(0,240,255,0.08) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    color: #A0AEC0 !important;
    padding: 7px 16px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(0,240,255,0.1) !important;
    color: #00F0FF !important;
    border: 1px solid rgba(0,240,255,0.2) !important;
    box-shadow: 0 0 15px rgba(0,240,255,0.1) !important;
}

/* ── FORM INPUTS ── */
.stTextInput input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(0,240,255,0.15) !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.9rem !important;
}
.stTextInput input:focus {
    border-color: rgba(0,240,255,0.4) !important;
    box-shadow: 0 0 0 3px rgba(0,240,255,0.08) !important;
}
.stSelectbox > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(0,240,255,0.15) !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
}
label {
    color: #A0AEC0 !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    text-transform: uppercase !important;
}

/* ── SELECT SLIDER ── */
.stSlider > div > div > div {
    background: rgba(0,240,255,0.2) !important;
}
[data-testid="stThumbValue"] {
    background: rgba(0,240,255,0.15) !important;
    border: 1px solid rgba(0,240,255,0.3) !important;
    color: #00F0FF !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    border: 1px solid rgba(0,240,255,0.1) !important;
    overflow: hidden !important;
}

/* ── ALERTS ── */
.stSuccess > div {
    background: rgba(16,185,129,0.08) !important;
    border: 1px solid rgba(52,211,153,0.2) !important;
    border-radius: 10px !important;
    color: #34d399 !important;
}
.stError > div {
    background: rgba(239,68,68,0.08) !important;
    border: 1px solid rgba(248,113,113,0.2) !important;
    border-radius: 10px !important;
    color: #f87171 !important;
}
.stInfo > div {
    background: rgba(0,240,255,0.05) !important;
    border: 1px solid rgba(0,240,255,0.15) !important;
    border-radius: 10px !important;
    color: #00F0FF !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb {
    background: rgba(0,240,255,0.2);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(0,240,255,0.4); }

/* ── RESULTS SECTION HEADING ── */
.results-heading {
    font-size: 1.4rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.3px;
    margin-bottom: 1rem;
    text-shadow: 0 0 30px rgba(0,240,255,0.2);
}

/* ── SCORE PANEL ── */
.score-panel {
    background: rgba(0,240,255,0.03);
    border: 1px solid rgba(0,240,255,0.12);
    border-radius: 18px;
    padding: 2rem 1rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04);
    animation: glowPulse 3s ease-in-out infinite;
}
.score-panel::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,240,255,0.4), transparent);
}
.score-label {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #A0AEC0;
    margin-bottom: 0.8rem;
}
.score-risk {
    font-size: 1rem;
    font-weight: 700;
    color: #FFFFFF;
    margin-top: 0.7rem;
    text-shadow: 0 0 15px rgba(0,240,255,0.3);
}
.score-out-of {
    font-size: 0.75rem;
    color: #A0AEC0;
    margin-top: 0.2rem;
    font-weight: 500;
}

/* ── PULSING DOT ── */
.pulse-dot {
    display: inline-block;
    width: 10px; height: 10px;
    border-radius: 50%;
    background: #00F0FF;
    box-shadow: 0 0 8px rgba(0,240,255,0.8);
    position: relative;
    animation: glowPulse 2s ease-in-out infinite;
}
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
        conn.execute(
            "INSERT INTO users (username,password,full_name,department) VALUES (?,?,?,?)",
            (username, hash_pw(password), full_name, department)
        )
        conn.commit(); return True
    except sqlite3.IntegrityError: return False
    finally: conn.close()

def login_user(username, password):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_pw(password))
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def login_admin(username, password):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM admin_users WHERE username=? AND password=?",
        (username, hash_pw(password))
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def save_assessment(user_id, username, department, scores, total, risk, recs):
    conn = get_db()
    conn.execute(
        "INSERT INTO assessments (user_id,username,department,scores_json,total_score,risk_level,recommendations_json) VALUES (?,?,?,?,?,?,?)",
        (user_id, username, department, json.dumps(scores), total, risk, json.dumps(recs))
    )
    conn.commit(); conn.close()

def get_user_history(user_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM assessments WHERE user_id=? ORDER BY created_at DESC", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_assessments():
    conn = get_db()
    rows = conn.execute("SELECT * FROM assessments ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_users():
    conn = get_db()
    rows = conn.execute(
        "SELECT id,username,full_name,department,created_at FROM users"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── ASSESSMENT FRAMEWORK ──────────────────────
CATEGORIES = {
    "🪑 Seating & Posture": {
        "color": "#00F0FF", "icon": "🪑",
        "questions": [
            {"id": "seat_height",  "text": "Chair height allows feet flat on floor / footrest",       "weight": 8},
            {"id": "lumbar",       "text": "Chair provides adequate lumbar (lower back) support",       "weight": 9},
            {"id": "seat_depth",   "text": "Seat depth supports thighs without pressure behind knees", "weight": 7},
            {"id": "armrests",     "text": "Armrests allow relaxed shoulders (90° elbow angle)",       "weight": 6},
            {"id": "back_upright", "text": "Back remains upright (90–110° recline) during work",      "weight": 8},
        ]
    },
    "🖥️ Monitor & Display": {
        "color": "#818cf8", "icon": "🖥️",
        "questions": [
            {"id": "monitor_dist",   "text": "Monitor at arm's length (50–70 cm) from eyes",           "weight": 8},
            {"id": "monitor_height", "text": "Top of screen at or slightly below eye level",            "weight": 9},
            {"id": "monitor_glare",  "text": "Screen free from glare and reflections",                 "weight": 7},
            {"id": "refresh_rate",   "text": "Display refresh rate ≥ 60 Hz; resolution clear",         "weight": 5},
            {"id": "dual_monitor",   "text": "If dual monitors: primary centred, secondary same height","weight": 4},
        ]
    },
    "⌨️ Keyboard & Mouse": {
        "color": "#34d399", "icon": "⌨️",
        "questions": [
            {"id": "kb_position", "text": "Keyboard positioned so wrists are straight (neutral)",      "weight": 8},
            {"id": "mouse_close", "text": "Mouse adjacent to keyboard, same surface level",            "weight": 7},
            {"id": "wrist_rest",  "text": "Wrist rest used only during pauses, not while typing",      "weight": 5},
            {"id": "kb_tilt",     "text": "Keyboard tilt is low / flat to avoid wrist extension",      "weight": 6},
        ]
    },
    "💡 Lighting & Environment": {
        "color": "#fbbf24", "icon": "💡",
        "questions": [
            {"id": "ambient_light", "text": "Ambient lighting adequate (300–500 lux for office work)", "weight": 7},
            {"id": "no_flicker",    "text": "No flickering lights; lighting uniform across workspace", "weight": 6},
            {"id": "noise_level",   "text": "Background noise below 55 dB (acceptable for ICT work)", "weight": 6},
            {"id": "temperature",   "text": "Room temperature comfortable (20–24 °C) & ventilated",   "weight": 6},
            {"id": "air_quality",   "text": "Air quality good; no dust, fumes, or stale air",         "weight": 5},
        ]
    },
    "📐 Desk & Workspace Layout": {
        "color": "#f87171", "icon": "📐",
        "questions": [
            {"id": "desk_height",   "text": "Desk height allows 90° elbow angle when typing",         "weight": 8},
            {"id": "reach_zone",    "text": "Frequently used items within primary reach zone (30 cm)", "weight": 7},
            {"id": "leg_clearance", "text": "Adequate leg clearance under desk (no obstructions)",    "weight": 6},
            {"id": "cable_mgmt",    "text": "Cables managed; no trip/entanglement hazards",           "weight": 5},
            {"id": "documents",     "text": "Document holder used for reference material (if needed)", "weight": 4},
        ]
    },
    "🧘 Work Habits & Breaks": {
        "color": "#38bdf8", "icon": "🧘",
        "questions": [
            {"id": "micro_breaks",  "text": "Micro-breaks taken every 30–45 min (stand/stretch)",     "weight": 9},
            {"id": "eye_breaks",    "text": "20-20-20 rule followed (every 20 min, look 20 ft, 20 s)","weight": 8},
            {"id": "posture_aware", "text": "Worker aware of posture and self-corrects during day",   "weight": 8},
            {"id": "hydration",     "text": "Water available and regularly consumed at workstation",   "weight": 5},
            {"id": "exercise",      "text": "Regular physical activity / ergonomic exercises practised","weight": 7},
        ]
    },
    "🧠 Psychosocial Factors": {
        "color": "#e879f9", "icon": "🧠",
        "questions": [
            {"id": "workload",          "text": "Workload is manageable within working hours",         "weight": 8},
            {"id": "job_control",       "text": "Worker has control over task pace and method",       "weight": 7},
            {"id": "social_support",    "text": "Good social support from colleagues/supervisors",    "weight": 6},
            {"id": "stress_level",      "text": "Stress levels are low to moderate (self-reported)",  "weight": 8},
            {"id": "digital_wellbeing", "text": "Digital screen time managed; no tech-induced fatigue","weight": 7},
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

# ── CHART DEFAULTS ─────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans, Inter, sans-serif", size=12, color="#A0AEC0"),
    margin=dict(l=20, r=20, t=50, b=20),
)

def compute_scores(responses):
    cat_scores = {}
    total_w = total_wt = 0
    for cat, data in CATEGORIES.items():
        cw = cwt = 0
        for q in data["questions"]:
            v = responses.get(q["id"], 3)
            cw  += v * q["weight"]
            cwt += q["weight"]
        cat_scores[cat] = round((cw / (cwt * 5)) * 100, 1)
        total_w  += cw
        total_wt += cwt
    return round((total_w / (total_wt * 5)) * 100, 1), cat_scores

def get_risk_level(score):
    if score >= 80: return "Excellent", "badge-excellent", "🟢"
    if score >= 65: return "Good",      "badge-good",      "🔵"
    if score >= 45: return "Moderate",  "badge-moderate",  "🟡"
    return "Poor", "badge-poor", "🔴"

def bar_color(v):
    if v >= 80: return "#34d399"
    if v >= 65: return "#00F0FF"
    if v >= 45: return "#fbbf24"
    return "#f87171"

def generate_recommendations(cat_scores, responses):
    recs = []
    THRESH = {
        "🪑 Seating & Posture": {
            "seat_height":  ("Adjust chair height so feet rest flat on floor or use a footrest.", "High"),
            "lumbar":       ("Add lumbar support cushion or adjust built-in lumbar support.", "High"),
            "back_upright": ("Set posture correction reminders every 30 minutes.", "Medium"),
        },
        "🖥️ Monitor & Display": {
            "monitor_height":("Raise monitor so top of screen aligns with eye level.", "High"),
            "monitor_dist":  ("Move monitor to arm's-length distance (50–70 cm).", "High"),
            "monitor_glare": ("Reposition monitor perpendicular to windows; add anti-glare filter.", "Medium"),
        },
        "⌨️ Keyboard & Mouse": {
            "kb_position": ("Place keyboard so forearms are parallel to floor, wrists neutral.", "High"),
            "mouse_close": ("Move mouse adjacent to keyboard to reduce shoulder reach.", "Medium"),
        },
        "💡 Lighting & Environment": {
            "ambient_light": ("Install task lighting (300–500 lux) or adjust blinds.", "Medium"),
            "noise_level":   ("Use acoustic panels or noise-cancelling headphones.", "Medium"),
            "temperature":   ("Adjust HVAC within 20–24 °C comfort range.", "Low"),
        },
        "📐 Desk & Workspace Layout": {
            "desk_height": ("Use height-adjustable desk or keyboard/monitor risers.", "High"),
            "reach_zone":  ("Keep mouse, phone, stationery within 30 cm primary reach zone.", "Medium"),
            "cable_mgmt":  ("Use cable trays to eliminate trip hazards.", "Low"),
        },
        "🧘 Work Habits & Breaks": {
            "micro_breaks": ("Set timer every 30–45 min to stand, stretch, or walk briefly.", "High"),
            "eye_breaks":   ("Follow 20-20-20 rule; use reminder app.", "High"),
            "exercise":     ("Add 10-min desk stretches and 30-min walk to daily routine.", "Medium"),
        },
        "🧠 Psychosocial Factors": {
            "workload":         ("Discuss workload with supervisor; use task prioritisation matrix.", "High"),
            "stress_level":     ("Practice mindfulness, limit after-hours emails, consider counselling.", "High"),
            "digital_wellbeing":("Set digital detox periods; enable blue-light filter after 6 PM.", "Medium"),
        },
    }
    for cat, qmap in THRESH.items():
        for qid, (advice, priority) in qmap.items():
            if responses.get(qid, 5) <= 2:
                recs.append({"category": cat, "advice": advice, "priority": priority})
    for cat, score in cat_scores.items():
        if score < 50 and not any(r["category"] == cat for r in recs):
            recs.append({
                "category": cat,
                "advice": f"Overall {cat.split(' ',1)[1]} score is low ({score}%). Schedule an ergonomic review.",
                "priority": "Medium"
            })
    recs.sort(key=lambda x: {"High":0,"Medium":1,"Low":2}.get(x["priority"], 3))
    return recs

# ── PDF REPORT ────────────────────────────────
def build_pdf_report(username, department, total_score, risk_level, cat_scores, recs, date_str):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_s = ParagraphStyle('T', parent=styles['Title'], fontSize=18,
                              textColor=colors.HexColor('#0f172a'),
                              fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=2)
    sub_s   = ParagraphStyle('S', parent=styles['Normal'], fontSize=10,
                              textColor=colors.HexColor('#334155'), alignment=TA_CENTER, spaceAfter=4)
    h2_s    = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12,
                              textColor=colors.HexColor('#1e3a8a'),
                              fontName='Helvetica-Bold', spaceBefore=14, spaceAfter=4)
    sm_s    = ParagraphStyle('Sm', parent=styles['Normal'], fontSize=8,
                              textColor=colors.HexColor('#475569'))
    RC = {"Excellent": colors.HexColor('#064e3b'), "Good": colors.HexColor('#1e3a8a'),
          "Moderate": colors.HexColor('#78350f'), "Poor": colors.HexColor('#7f1d1d')}
    rc = RC.get(risk_level, colors.black)
    story = []
    story.append(Paragraph("ICT in Health and Ergonomics", title_s))
    story.append(Paragraph("Workstation Safety Scorer — Assessment Report", sub_s))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1d4ed8')))
    story.append(Spacer(1, 0.4*cm))
    mt = Table([["Assessor:", username, "Date:", date_str],
                ["Department:", department, "Risk Level:", risk_level]],
               colWidths=[3*cm, 6*cm, 3*cm, 5*cm])
    mt.setStyle(TableStyle([
        ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
        ('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),
        ('FONTNAME',(2,0),(2,-1),'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,-1),9),
        ('TEXTCOLOR',(3,1),(3,1),rc),
        ('FONTNAME',(3,1),(3,1),'Helvetica-Bold'),
        ('TOPPADDING',(0,0),(-1,-1),5),
        ('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#f8fafc')),
        ('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#e2e8f0')),
    ]))
    story.append(mt); story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Overall Safety Score", h2_s))
    st2 = Table([[f"{total_score:.1f} / 100", risk_level]], colWidths=[4*cm, 6*cm])
    st2.setStyle(TableStyle([
        ('FONTNAME',(0,0),(0,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(0,0),26),
        ('TEXTCOLOR',(0,0),(0,0),rc),
        ('FONTNAME',(1,0),(1,0),'Helvetica-Bold'),('FONTSIZE',(1,0),(1,0),14),
        ('TEXTCOLOR',(1,0),(1,0),rc),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10),
        ('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#eff6ff')),
        ('GRID',(0,0),(-1,-1),1,colors.HexColor('#93c5fd')),
    ]))
    story.append(st2); story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Category Breakdown", h2_s))
    cd = [["Category","Score (%)","Status"]]
    for cat, score in cat_scores.items():
        s = "Excellent" if score>=80 else "Good" if score>=65 else "Moderate" if score>=45 else "Needs Attention"
        cd.append([cat, f"{score:.1f}%", s])
    ct = Table(cd, colWidths=[8*cm,3.5*cm,5.5*cm])
    ct.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,-1),9),
        ('TEXTCOLOR',(0,1),(-1,-1),colors.HexColor('#0f172a')),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f8fafc'),colors.white]),
        ('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#e2e8f0')),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),8),
    ]))
    story.append(ct); story.append(Spacer(1, 0.5*cm))
    if recs:
        story.append(Paragraph("Prioritised Recommendations", h2_s))
        rd = [["#","Priority","Category","Recommended Action"]]
        PC = {"High":colors.HexColor('#fef2f2'),"Medium":colors.HexColor('#fffbeb'),"Low":colors.HexColor('#f0fdf4')}
        for i, r in enumerate(recs[:15], 1):
            rd.append([str(i), r["priority"], r["category"].split(" ",1)[1][:20], r["advice"]])
        rt = Table(rd, colWidths=[0.7*cm,2*cm,4.3*cm,10*cm])
        sc = [
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
            ('FONTSIZE',(0,0),(-1,-1),8),
            ('TEXTCOLOR',(0,1),(-1,-1),colors.HexColor('#0f172a')),
            ('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#e2e8f0')),
            ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
            ('LEFTPADDING',(0,0),(-1,-1),5),('VALIGN',(0,0),(-1,-1),'TOP'),
        ]
        for i, r in enumerate(recs[:15], 1):
            sc.append(('BACKGROUND',(1,i),(1,i),PC.get(r["priority"],colors.white)))
        rt.setStyle(TableStyle(sc))
        story.append(rt)
    story.append(Spacer(1, 0.6*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "Generated by ICT in Health and Ergonomics: Workstation Safety Scorer | ISO 9241 & OSHA Guidelines",
        sm_s))
    doc.build(story)
    buf.seek(0)
    return buf

# ── SESSION STATE ─────────────────────────────
for k, v in [("user",None),("admin",None),("responses",{}),("result",None)]:
    if k not in st.session_state: st.session_state[k] = v

# ── SIDEBAR ───────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1.5rem 0 1rem;'>
        <div style='position:relative;display:inline-block;'>
            <div style='font-size:2.4rem;filter:drop-shadow(0 0 12px rgba(0,240,255,0.6));
                        animation:float 4s ease-in-out infinite;display:inline-block;'>🖥️</div>
        </div>
        <div style='font-size:0.95rem;font-weight:800;color:#FFFFFF;line-height:1.4;margin-top:8px;
                    text-shadow:0 0 20px rgba(0,240,255,0.3);letter-spacing:-0.3px;'>
            ICT in Health<br>and Ergonomics
        </div>
        <div style='font-size:0.65rem;color:#A0AEC0;margin-top:6px;font-weight:600;
                    letter-spacing:1.2px;text-transform:uppercase;'>
            Workstation Safety Scorer
        </div>
        <div style='width:50px;height:1px;
                    background:linear-gradient(90deg,transparent,rgba(0,240,255,0.5),transparent);
                    margin:12px auto 0;'></div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.user:
        u = st.session_state.user
        st.markdown(f"""
        <div style='background:rgba(0,240,255,0.05);border:1px solid rgba(0,240,255,0.12);
                    border-radius:12px;padding:0.8rem 1rem;margin-bottom:0.8rem;'>
            <div style='font-size:0.65rem;color:#00F0FF;font-weight:700;
                        text-transform:uppercase;letter-spacing:0.8px;'>Logged in as</div>
            <div style='font-size:0.92rem;font-weight:700;color:#FFFFFF;margin-top:3px;'>{u['full_name']}</div>
            <div style='font-size:0.75rem;color:#A0AEC0;'>{u['department']}</div>
        </div>""", unsafe_allow_html=True)
        nav = st.radio("", [
            "🏠  Dashboard",
            "📋  New Assessment",
            "📊  My History",
            "⬇️  Download Report"
        ])
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("⏏  Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.result = None
            st.rerun()
    elif st.session_state.admin:
        st.markdown("""
        <div style='background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.15);
                    border-radius:12px;padding:0.7rem 1rem;margin-bottom:0.8rem;'>
            <div style='font-size:0.78rem;color:#f87171;font-weight:700;'>🛡️  Admin Panel</div>
        </div>""", unsafe_allow_html=True)
        nav = st.radio("", ["📊  Overview", "👥  Users", "📋  All Assessments"])
        if st.button("⏏  Admin Logout", use_container_width=True):
            st.session_state.admin = None
            st.rerun()
    else:
        nav = st.radio("Navigation", ["🏠  Home", "🔑  Login", "📝  Register", "🛡️  Admin"], label_visibility="collapsed")

    st.markdown("""
    <div style='position:absolute;bottom:1rem;left:0;right:0;text-align:center;'>
        <div style='font-size:0.62rem;color:#475569;line-height:1.8;'>
            <span style='color:rgba(0,240,255,0.5);'>━━━━━━━━━━━━</span><br>
            ISO 9241 · OSHA Standards<br>
            <span style='color:rgba(0,240,255,0.4);'>ICT Health & Ergonomics</span>
        </div>
    </div>""", unsafe_allow_html=True)

# ── HELPER: BANNER ────────────────────────────
def render_banner(title_html, subtitle):
    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-eyebrow">⬡ ICT Health & Ergonomics Platform</div>
        <div class="hero-title">{title_html}</div>
        <div class="hero-sub">{subtitle}</div>
        <div class="hero-badge">
            <span class="pulse-dot"></span>
            ISO 9241 · OSHA Aligned · Evidence-Based
        </div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  PUBLIC PAGES
# ══════════════════════════════════════════════
if not st.session_state.user and not st.session_state.admin and "Home" in nav:
    render_banner(
        'ICT in Health and Ergonomics<br><span class="glow-text">Workstation Safety Scorer</span>',
        "Advanced Assessment Platform · ISO 9241 Compliant · OSHA Aligned"
    )
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

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-card"><div class="section-title">🎯 Assessment Domains</div>', unsafe_allow_html=True)
        for cat, data in CATEGORIES.items():
            st.markdown(f"""
            <div style='padding:6px 0;font-size:0.88rem;color:#e2e8f0;font-weight:500;
                        border-bottom:1px solid rgba(0,240,255,0.06);display:flex;align-items:center;gap:8px;'>
                <span style='color:{data["color"]};'>{data["icon"]}</span>
                <span>{cat.split(" ",1)[1]}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="section-card"><div class="section-title">⚙️ Platform Features</div>', unsafe_allow_html=True)
        feats = [
            ("#00F0FF","📊","Weighted 5-point Likert scale scoring"),
            ("#34d399","📈","Real-time glowing radar + bar visualisation"),
            ("#818cf8","🎯","Priority-ranked smart recommendations"),
            ("#fbbf24","📅","Trend spline tracking across sessions"),
            ("#f87171","📄","Downloadable professional PDF report"),
            ("#38bdf8","🛡️","Admin analytics & benchmarking dashboard"),
        ]
        for clr, ic, txt in feats:
            st.markdown(f"""
            <div style='background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.06);
                        border-radius:8px;padding:8px 12px;margin-bottom:6px;
                        font-size:0.85rem;color:#e2e8f0;font-weight:500;
                        display:flex;align-items:center;gap:8px;'>
                <span style='color:{clr};font-size:1rem;'>{ic}</span>
                {txt}
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif not st.session_state.user and not st.session_state.admin and "Login" in nav:
    render_banner(
        'Sign <span class="glow-text">In</span>',
        "ICT in Health and Ergonomics: Workstation Safety Scorer"
    )
    col, _ = st.columns([1.1, 1])
    with col:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

elif not st.session_state.user and not st.session_state.admin and "Register" in nav:
    render_banner(
        'Create <span class="glow-text">Account</span>',
        "ICT in Health and Ergonomics: Workstation Safety Scorer"
    )
    col, _ = st.columns([1.1, 1])
    with col:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        with st.form("reg_form"):
            fn   = st.text_input("Full Name")
            un   = st.text_input("Username")
            dept = st.selectbox("Department", ["ICT / IT","Administration","Healthcare",
                                               "Education","Engineering","Finance","HR","Other"])
            pw1  = st.text_input("Password", type="password")
            pw2  = st.text_input("Confirm Password", type="password")
            sub  = st.form_submit_button("Create Account →", use_container_width=True)
        if sub:
            if pw1 != pw2:          st.error("Passwords do not match.")
            elif len(pw1) < 6:      st.error("Password must be at least 6 characters.")
            elif not fn or not un:  st.error("All fields are required.")
            elif register_user(un, pw1, fn, dept): st.success("Account created! Please log in.")
            else: st.error("Username already taken.")
        st.markdown('</div>', unsafe_allow_html=True)

elif not st.session_state.user and not st.session_state.admin and "Admin" in nav:
    render_banner(
        'Admin <span class="glow-text">Portal</span>',
        "ICT in Health and Ergonomics: Workstation Safety Scorer"
    )
    col, _ = st.columns([1.1, 1])
    with col:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  AUTHENTICATED USER
# ══════════════════════════════════════════════
elif st.session_state.user:
    user = st.session_state.user

    # ── DASHBOARD ──
    if "Dashboard" in nav:
        fname = user['full_name'].split()[0]
        render_banner(
            f'Welcome, <span class="glow-text">{fname}</span> 👋',
            f"ICT in Health and Ergonomics: Workstation Safety Scorer · {user['department']}"
        )
        history = get_user_history(user["id"])
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"""
        <div class="metric-tile">
            <div class="icon">📋</div>
            <div class="val">{len(history)}</div>
            <div class="lbl">Total Assessments</div>
        </div>""", unsafe_allow_html=True)
        if history:
            ls = history[0]["total_score"]
            rl, _, ri = get_risk_level(ls)
            c2.markdown(f"""
            <div class="metric-tile">
                <div class="icon">📊</div>
                <div class="val">{ls:.0f}%</div>
                <div class="lbl">Latest Score</div>
            </div>""", unsafe_allow_html=True)
            c3.markdown(f"""
            <div class="metric-tile">
                <div class="icon">{ri}</div>
                <div class="val" style="font-size:1.4rem;">{rl}</div>
                <div class="lbl">Risk Level</div>
            </div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            df = pd.DataFrame([{
                "Date": h["created_at"][:10],
                "Score": h["total_score"]
            } for h in reversed(history)])

            fig = go.Figure()
            # Gradient fill
            fig.add_trace(go.Scatter(
                x=df["Date"], y=df["Score"],
                mode="lines",
                line=dict(color="rgba(0,240,255,0)", width=0),
                fill="tozeroy",
                fillcolor="rgba(0,240,255,0.04)",
                showlegend=False, hoverinfo="skip"
            ))
            # Main spline
            fig.add_trace(go.Scatter(
                x=df["Date"], y=df["Score"],
                mode="lines+markers",
                line=dict(color="#00F0FF", width=2.5, shape="spline", smoothing=1.2),
                marker=dict(
                    size=[14 if s == df["Score"].max() else 8 for s in df["Score"]],
                    color=["#00F0FF" if s == df["Score"].max() else "rgba(0,240,255,0.6)" for s in df["Score"]],
                    line=dict(color="#0B0F19", width=2),
                    symbol="circle"
                ),
                name="Safety Score",
                hovertemplate="<b>%{x}</b><br>Score: <b>%{y:.1f}%</b><extra></extra>",
            ))
            fig.add_hline(y=80, line=dict(color="rgba(52,211,153,0.4)", width=1, dash="dot"),
                          annotation_text="Excellent threshold",
                          annotation_font=dict(color="#34d399", size=10))
            fig.add_hline(y=65, line=dict(color="rgba(251,191,36,0.4)", width=1, dash="dot"),
                          annotation_text="Good threshold",
                          annotation_font=dict(color="#fbbf24", size=10))
            fig.update_layout(
                title=dict(text="Score History · Spline Trend", font=dict(size=14, color="#FFFFFF"), x=0.01),
                yaxis=dict(
                    range=[0, 115], title="Score (%)",
                    title_font=dict(color="#A0AEC0", size=11),
                    tickfont=dict(color="#A0AEC0", size=11),
                    gridcolor="rgba(255,255,255,0.04)",
                    zerolinecolor="rgba(255,255,255,0.06)",
                ),
                xaxis=dict(
                    title="", tickfont=dict(color="#A0AEC0", size=11),
                    gridcolor="rgba(255,255,255,0.04)",
                    linecolor="rgba(255,255,255,0.06)",
                ),
                height=300,
                showlegend=False,
                **CHART_LAYOUT
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            c2.markdown("""<div class="metric-tile"><div class="icon">📊</div><div class="val">—</div><div class="lbl">Latest Score</div></div>""", unsafe_allow_html=True)
            c3.markdown("""<div class="metric-tile"><div class="icon">⚠️</div><div class="val">—</div><div class="lbl">Risk Level</div></div>""", unsafe_allow_html=True)
            st.info("No assessments yet. Go to **New Assessment** to get started!")

    # ── NEW ASSESSMENT ──
    elif "Assessment" in nav and "New" in nav or "New" in nav:
        render_banner(
            '📋 New <span class="glow-text">Assessment</span>',
            "ICT in Health and Ergonomics · Rate each criterion: 1 (Never) → 5 (Always)"
        )
        with st.form("assessment_form"):
            all_responses = {}
            tabs = st.tabs([f"{data['icon']}  {name.split(' ',1)[1]}" for name, data in CATEGORIES.items()])
            for tab, (cat_name, cat_data) in zip(tabs, CATEGORIES.items()):
                with tab:
                    st.markdown(f"""
                    <div style='padding:0.5rem 0 1rem;font-size:0.78rem;color:{cat_data["color"]};
                                font-weight:700;letter-spacing:1px;text-transform:uppercase;'>
                        {cat_data["icon"]} {cat_name.split(" ",1)[1]} · {len(cat_data["questions"])} criteria
                    </div>""", unsafe_allow_html=True)
                    for q in cat_data["questions"]:
                        st.markdown(f"""
                        <div class="q-card">
                            <div class="q-label">{q['text']}</div>
                            <div class="q-weight">⚖ Weight: {q['weight']}/10</div>
                        </div>""", unsafe_allow_html=True)
                        val = st.select_slider(
                            " ",
                            options=list(SCALE_LABELS.keys()),
                            format_func=lambda x: f"{x} — {SCALE_LABELS[x]}",
                            value=3, key=f"q_{q['id']}"
                        )
                        all_responses[q["id"]] = val
            submitted = st.form_submit_button("🚀  Calculate Safety Score", use_container_width=True)

        if submitted:
            total, cat_scores = compute_scores(all_responses)
            rl, badge_cls, ri = get_risk_level(total)
            recs = generate_recommendations(cat_scores, all_responses)
            save_assessment(user["id"], user["username"], user["department"],
                            all_responses, total, rl, recs)
            st.session_state.result = {
                "total": total, "cat_scores": cat_scores,
                "risk": rl, "recs": recs, "responses": all_responses
            }
            st.success("✅  Assessment saved successfully!")
            st.rerun()

        if st.session_state.result:
            r = st.session_state.result
            rl, badge_cls, _ = get_risk_level(r["total"])
            ri = "🟢" if rl=="Excellent" else "🔵" if rl=="Good" else "🟡" if rl=="Moderate" else "🔴"

            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            st.markdown('<div class="results-heading">📊  Assessment Results</div>', unsafe_allow_html=True)

            c1, c2 = st.columns([1, 2.2])
            with c1:
                st.markdown(f"""
                <div class="score-panel">
                    <div class="score-label">Overall Score</div>
                    <div class="score-badge {badge_cls}">{r['total']:.1f}</div>
                    <div class="score-risk">{ri}  {rl}</div>
                    <div class="score-out-of">out of 100 points</div>
                </div>""", unsafe_allow_html=True)

            with c2:
                cats = list(r["cat_scores"].keys())
                vals = list(r["cat_scores"].values())
                cat_colors = [CATEGORIES[c]["color"] for c in cats]

                fig = go.Figure()
                # Background fill
                fig.add_trace(go.Scatterpolar(
                    r=vals + [vals[0]],
                    theta=[c.split(" ",1)[1] for c in cats] + [cats[0].split(" ",1)[1]],
                    fill="toself",
                    fillcolor="rgba(0,240,255,0.04)",
                    line=dict(color="rgba(0,0,0,0)", width=0),
                    showlegend=False, hoverinfo="skip"
                ))
                # Glowing neon line
                fig.add_trace(go.Scatterpolar(
                    r=vals + [vals[0]],
                    theta=[c.split(" ",1)[1] for c in cats] + [cats[0].split(" ",1)[1]],
                    fill="none",
                    line=dict(color="#00F0FF", width=2.5),
                    marker=dict(
                        size=8,
                        color=cat_colors,
                        line=dict(color="#00F0FF", width=1.5),
                        symbol="circle"
                    ),
                    name="Score",
                    hovertemplate="<b>%{theta}</b><br>%{r:.1f}%<extra></extra>",
                ))
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            range=[0, 100],
                            tickfont=dict(size=10, color="#A0AEC0"),
                            gridcolor="rgba(0,240,255,0.1)",
                            linecolor="rgba(0,240,255,0.15)",
                            tickvals=[20,40,60,80,100],
                        ),
                        angularaxis=dict(
                            tickfont=dict(size=10, color="#FFFFFF"),
                            linecolor="rgba(0,240,255,0.15)",
                            gridcolor="rgba(0,240,255,0.08)",
                        ),
                        bgcolor="rgba(0,0,0,0)",
                    ),
                    title=dict(text="Category Radar · Neon Filament View",
                               font=dict(size=13, color="#FFFFFF"), x=0.5, xanchor="center"),
                    showlegend=False,
                    height=380,
                    margin=dict(l=40, r=40, t=50, b=40),
                    **CHART_LAYOUT
                )
                st.plotly_chart(fig, use_container_width=True)

            # Bar chart
            fig2 = go.Figure(go.Bar(
                x=[c.split(" ",1)[1] for c in cats],
                y=vals,
                marker=dict(
                    color=[f"rgba({int(bar_color(v)[1:3],16)},{int(bar_color(v)[3:5],16)},{int(bar_color(v)[5:7],16)},0.7)"
                           for v in vals],
                    line=dict(
                        color=[bar_color(v) for v in vals],
                        width=1.5
                    ),
                    opacity=0.9,
                ),
                text=[f"<b>{v:.0f}%</b>" for v in vals],
                textposition="outside",
                textfont=dict(size=12, color="#FFFFFF"),
            ))
            fig2.update_layout(
                title=dict(text="Category Score Breakdown",
                           font=dict(size=13, color="#FFFFFF"), x=0.01),
                yaxis=dict(
                    range=[0, 125],
                    title="Score (%)",
                    title_font=dict(color="#A0AEC0", size=11),
                    tickfont=dict(color="#A0AEC0", size=11),
                    gridcolor="rgba(255,255,255,0.04)",
                    zerolinecolor="rgba(255,255,255,0.06)",
                ),
                xaxis=dict(
                    tickfont=dict(color="#FFFFFF", size=10),
                    tickangle=-25,
                    linecolor="rgba(255,255,255,0.06)",
                ),
                height=320,
                bargap=0.38,
                margin=dict(l=20, r=20, t=50, b=110),
                **CHART_LAYOUT
            )
            st.plotly_chart(fig2, use_container_width=True)

            if r["recs"]:
                st.markdown("""
                <div style='font-size:1.1rem;font-weight:800;color:#FFFFFF;margin:0.8rem 0;
                            text-shadow:0 0 20px rgba(0,240,255,0.2);letter-spacing:-0.2px;'>
                    🎯  Prioritised Recommendations
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

    # ── MY HISTORY ──
    elif "History" in nav:
        render_banner(
            '📊  My <span class="glow-text">History</span>',
            "ICT in Health and Ergonomics: Workstation Safety Scorer"
        )
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
                dfc = pd.DataFrame([{
                    "Date": h["created_at"][:10],
                    "Score": h["total_score"]
                } for h in reversed(history)])
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dfc["Date"], y=dfc["Score"],
                    mode="lines",
                    line=dict(color="rgba(0,240,255,0)", width=0),
                    fill="tozeroy", fillcolor="rgba(0,240,255,0.04)",
                    showlegend=False, hoverinfo="skip"
                ))
                fig.add_trace(go.Scatter(
                    x=dfc["Date"], y=dfc["Score"],
                    mode="lines+markers",
                    line=dict(color="#00F0FF", width=2.5, shape="spline", smoothing=1.2),
                    marker=dict(size=8, color="#00F0FF", line=dict(color="#0B0F19", width=2)),
                    name="Score",
                    hovertemplate="<b>%{x}</b><br>Score: <b>%{y:.1f}%</b><extra></extra>",
                ))
                fig.update_layout(
                    title=dict(text="All Assessment Scores · Spline View",
                               font=dict(size=13, color="#FFFFFF"), x=0.01),
                    yaxis=dict(range=[0,115], title="Score (%)",
                               title_font=dict(color="#A0AEC0", size=11),
                               tickfont=dict(color="#A0AEC0", size=11),
                               gridcolor="rgba(255,255,255,0.04)"),
                    xaxis=dict(tickfont=dict(color="#A0AEC0", size=11), tickangle=-30,
                               gridcolor="rgba(255,255,255,0.04)"),
                    height=320, showlegend=False,
                    **CHART_LAYOUT
                )
                st.plotly_chart(fig, use_container_width=True)

    # ── DOWNLOAD REPORT ──
    elif "Download" in nav:
        render_banner(
            '⬇️  Download <span class="glow-text">Report</span>',
            "ICT in Health and Ergonomics: Workstation Safety Scorer"
        )
        history = get_user_history(user["id"])
        if not history:
            st.info("No assessments found. Complete an assessment first.")
        else:
            options = {
                f"{h['created_at'][:16]} — Score: {h['total_score']:.1f}% ({h['risk_level']})": h
                for h in history
            }
            choice = st.selectbox("Select Assessment", list(options.keys()))
            chosen = options[choice]
            responses = json.loads(chosen["scores_json"])
            _, cat_scores = compute_scores(responses)
            recs = json.loads(chosen["recommendations_json"])
            if st.button("📄  Generate PDF Report"):
                with st.spinner("Building PDF report..."):
                    buf = build_pdf_report(
                        user["full_name"], user["department"],
                        chosen["total_score"], chosen["risk_level"],
                        cat_scores, recs, chosen["created_at"][:10]
                    )
                st.download_button(
                    "⬇️  Download PDF", data=buf,
                    file_name=f"ICT_Ergonomics_Report_{chosen['created_at'][:10]}.pdf",
                    mime="application/pdf"
                )

# ══════════════════════════════════════════════
#  ADMIN
# ══════════════════════════════════════════════
elif st.session_state.admin:
    if "Overview" in nav:
        render_banner('🛡️  Admin <span class="glow-text">Overview</span>',
                      "ICT in Health and Ergonomics: Workstation Safety Scorer")
        all_a = get_all_assessments()
        all_u = get_all_users()
        avg = sum(a["total_score"] for a in all_a) / len(all_a) if all_a else 0
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"""<div class="metric-tile"><div class="icon">👥</div><div class="val">{len(all_u)}</div><div class="lbl">Registered Users</div></div>""", unsafe_allow_html=True)
        c2.markdown(f"""<div class="metric-tile"><div class="icon">📋</div><div class="val">{len(all_a)}</div><div class="lbl">Total Assessments</div></div>""", unsafe_allow_html=True)
        c3.markdown(f"""<div class="metric-tile"><div class="icon">📈</div><div class="val">{avg:.1f}%</div><div class="lbl">Platform Avg Score</div></div>""", unsafe_allow_html=True)
        if all_a:
            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            df = pd.DataFrame([{"Risk": a["risk_level"], "Dept": a["department"], "Score": a["total_score"]} for a in all_a])
            col1, col2 = st.columns(2)
            with col1:
                rc = df["Risk"].value_counts().reset_index()
                rc.columns = ["Risk Level","Count"]
                fig = px.pie(rc, values="Count", names="Risk Level",
                             color="Risk Level",
                             color_discrete_map={"Excellent":"#34d399","Good":"#00F0FF",
                                                 "Moderate":"#fbbf24","Poor":"#f87171"},
                             hole=0.45,
                             title="Risk Level Distribution")
                fig.update_traces(
                    textfont=dict(size=12, color="#FFFFFF"),
                    marker=dict(line=dict(color="#0B0F19", width=2))
                )
                fig.update_layout(
                    title=dict(font=dict(size=13, color="#FFFFFF")),
                    legend=dict(font=dict(color="#A0AEC0", size=11)),
                    height=340, **CHART_LAYOUT
                )
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                da = df.groupby("Dept")["Score"].mean().reset_index()
                da.columns = ["Department","Average Score"]
                fig2 = go.Figure(go.Bar(
                    x=da["Department"], y=da["Average Score"],
                    marker=dict(
                        color=da["Average Score"],
                        colorscale=[[0,"#f87171"],[0.45,"#fbbf24"],[0.65,"#00F0FF"],[1,"#34d399"]],
                        line=dict(color="rgba(255,255,255,0.1)", width=1),
                        showscale=False,
                    ),
                    text=[f"<b>{v:.1f}%</b>" for v in da["Average Score"]],
                    textposition="outside",
                    textfont=dict(color="#FFFFFF", size=11),
                ))
                fig2.update_layout(
                    title=dict(text="Avg Score by Department", font=dict(size=13, color="#FFFFFF"), x=0.01),
                    yaxis=dict(range=[0,115], title_font=dict(color="#A0AEC0"),
                               tickfont=dict(color="#A0AEC0", size=11),
                               gridcolor="rgba(255,255,255,0.04)"),
                    xaxis=dict(tickfont=dict(color="#FFFFFF", size=10), tickangle=-20),
                    height=340, bargap=0.4,
                    **CHART_LAYOUT
                )
                st.plotly_chart(fig2, use_container_width=True)

    elif "Users" in nav:
        render_banner('👥  <span class="glow-text">Users</span>',
                      "ICT in Health and Ergonomics: Workstation Safety Scorer")
        users = get_all_users()
        df = pd.DataFrame(users)[["username","full_name","department","created_at"]]
        df.columns = ["Username","Full Name","Department","Registered"]
        st.dataframe(df, use_container_width=True, hide_index=True)

    elif "Assessments" in nav:
        render_banner('📋  All <span class="glow-text">Assessments</span>',
                      "ICT in Health and Ergonomics: Workstation Safety Scorer")
        all_a = get_all_assessments()
        if all_a:
            df = pd.DataFrame([{
                "User": a["username"], "Dept": a["department"],
                "Score": f"{a['total_score']:.1f}%", "Risk": a["risk_level"],
                "Date": a["created_at"][:16]
            } for a in all_a])
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button("⬇️  Export CSV", df.to_csv(index=False),
                               "ICT_Ergonomics_Assessments.csv", "text/csv")
        else:
            st.info("No assessments yet.")

else:
    render_banner(
        'ICT in Health and <span class="glow-text">Ergonomics</span>',
        "Workstation Safety Scorer — Please log in or register to continue."
    )
    st.info("Use the sidebar to **Login** or **Register**.")
