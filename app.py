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

# ── PAGE CONFIGURATION ──
st.set_page_config(
    page_title="ICT in Health and Ergonomics: Workstation Safety Scorer",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── INJECT ADVANCED UI CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700;800&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
    box-sizing: border-box;
}

/* GLOBAL BACKGROUND */
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

/* METRIC TILES */
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
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05);
}

/* SECTION CARDS */
.section-card {
    background: rgba(255,255,255,0.025);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(0,240,255,0.1);
    border-radius: 18px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.2rem;
}

/* SCORE BADGES */
.score-badge {
    font-size: 3.8rem;
    font-weight: 800;
    padding: 0.6rem 1.8rem;
    border-radius: 16px;
    letter-spacing: -2px;
    display: inline-block;
}
.badge-excellent { background: rgba(5,150,105,0.15); color: #34d399; border: 1px solid rgba(52,211,153,0.3); }
.badge-good { background: rgba(0,240,255,0.08); color: #00F0FF; border: 1px solid rgba(0,240,255,0.25); }
.badge-moderate { background: rgba(245,158,11,0.1); color: #fbbf24; border: 1px solid rgba(251,191,36,0.25); }
.badge-poor { background: rgba(239,68,68,0.1); color: #f87171; border: 1px solid rgba(248,113,113,0.25); }

/* SIDEBAR FIX */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #06090f 0%, #0a1220 60%, #060810 100%) !important;
    border-right: 1px solid rgba(0,240,255,0.1) !important;
}
</style>
""", unsafe_allow_html=True)

# ── DATABASE CONTROL LAYER ──
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

def hash_pw(pw): 
    return hashlib.sha256(pw.encode()).hexdigest()

# ── FIXED PLOTLY CHART IMPLEMENTATIONS ──
def render_radar_chart(categories, values):
    """Generates a stable, high-performance responsive Radar visualization."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]] if values else [],
        theta=categories + [categories[0]] if categories else [],
        fill='toself',
        fillcolor='rgba(0, 240, 255, 0.15)',
        line=dict(color='#00F0FF', width=2.5),
        marker=dict(color='#00F0FF', size=7),
        name='Current Assessment'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor='rgba(255, 255, 255, 0.1)',
                angle=45,
                tickfont=dict(color='#A0AEC0', size=9)
            ),
            angularaxis=dict(
                gridcolor='rgba(255, 255, 255, 0.1)',
                tickfont=dict(color='#FFFFFF', size=11, family='Plus Jakarta Sans')
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=30, b=30),
        showlegend=False,
        height=320
    )
    return fig

def render_bar_chart(categories, values):
    """Generates a perfectly structured distribution bar visualization."""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        marker=dict(
            color=values,
            colorscale=[[0.0, '#fbbf24'], [0.5, '#00F0FF'], [1.0, '#34d399']],
            line=dict(color='rgba(255,255,255,0.1)', width=1)
        ),
        text=values,
        textposition='outside',
        textfont=dict(color='#FFFFFF', size=10)
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=35, b=10),
        height=280,
        showlegend=False,
        xaxis=dict(
            gridcolor='rgba(0,0,0,0)',
            tickfont=dict(color='#A0AEC0', size=10)
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.05)',
            tickfont=dict(color='#A0AEC0', size=10),
            range=[0, 115]
        )
    )
    return fig

# ── PLACEHOLDER APP NAVIGATION ROUTING ──
def main():
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Go to", ["Dashboard Demo", "Documentation"])
    
    if app_mode == "Dashboard Demo":
        st.markdown("""
        <div class="section-card">
            <h2 style='color:#FFF; margin-bottom:4px;'>Workstation Safety Assessment</h2>
            <p style='color:#A0AEC0; font-size:14px;'>Real-time metrics visual engine compiled successfully.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample structured evaluation metrics data
        cats = ['Seating', 'Monitor Layout', 'Input Devices', 'Environment', 'Work Breaks']
        vals = [75, 60, 85, 50, 65]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h3 style='color:#FFF;font-size:16px;'>Ergonomic Vector Radar</h3>", unsafe_allow_html=True)
            st.plotly_chart(render_radar_chart(cats, vals), use_container_width=True)
        with col2:
            st.markdown("<h3 style='color:#FFF;font-size:16px;'>Category Scores Bar Graph</h3>", unsafe_allow_html=True)
            st.plotly_chart(render_bar_chart(cats, vals), use_container_width=True)

if __name__ == "__main__":
    main()
