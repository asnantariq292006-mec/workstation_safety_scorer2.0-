import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Workstation Safety Scorer",
    page_icon="💻",
    layout="wide"
)

# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp{
    background: #0B0F19;
    color: white;
}

.glass{
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 25px;
    padding: 25px;
    box-shadow:
    0 8px 32px rgba(0,240,255,0.15),
    inset 0 0 1px rgba(255,255,255,0.6);
}

.metric-card{
    background: rgba(255,255,255,0.05);
    border-radius: 25px;
    padding: 25px;
    text-align:center;
    border:1px solid rgba(0,240,255,0.2);
    box-shadow:0 0 25px rgba(0,240,255,0.2);
}

.metric-number{
    font-size:40px;
    font-weight:800;
    color:#00F0FF;
    text-shadow:0 0 15px #00F0FF;
}

.metric-label{
    color:#A0AEC0;
    font-size:15px;
}

.title{
    font-size:42px;
    font-weight:800;
    color:white;
}

.subtitle{
    color:#A0AEC0;
    margin-top:-10px;
}

.sidebar-icon{
    color:#00F0FF;
    font-size:22px;
    margin-bottom:20px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:

    st.markdown(
        "<h2 style='color:#00F0FF'>⚡ Navigation</h2>",
        unsafe_allow_html=True
    )

    st.markdown("### 📊 Dashboard")
    st.markdown("### ➕ New Assessment")
    st.markdown("### 📈 Analytics")
    st.markdown("### ⚙ Settings")

# -----------------------------
# HEADER
# -----------------------------
st.markdown(
    """
    <div class='glass'>
        <div class='title'>
            Welcome, Asnan 👋
        </div>

        <div class='subtitle'>
        ICT in Health and Ergonomics:
        Workstation Safety Scorer • Engineering
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")

# -----------------------------
# SUMMARY CARDS
# -----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class='metric-card'>
            <div class='metric-number'>35</div>
            <div class='metric-label'>Assessments</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class='metric-card'>
            <div class='metric-number'>60%</div>
            <div class='metric-label'>Safety Score</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class='metric-card'>
            <div class='metric-number'>Medium</div>
            <div class='metric-label'>Risk Level</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")

# -----------------------------
# RADAR CHART
# -----------------------------
left, right = st.columns([1,1])

with left:

    categories = [
        "Chair",
        "Monitor",
        "Keyboard & Mouse",
        "Lighting",
        "Posture",
        "Breaks"
    ]

    values = [75, 55, 70, 80, 50, 65]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            line=dict(color="#00F0FF", width=3),
            fillcolor='rgba(0,240,255,0.25)'
        )
    )

    fig.update_layout(
        title="Ergonomic Category Analysis",
        paper_bgcolor="#0B0F19",
        polar=dict(
            bgcolor="#0B0F19",
            radialaxis=dict(
                visible=True,
                range=[0,100],
                color="white"
            )
        ),
        font=dict(color="white")
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# HISTORY CHART
# -----------------------------
with right:

    scores = [35,42,47,50,54,58,60]

    fig2 = go.Figure()

    fig2.add_trace(
        go.Scatter(
            y=scores,
            mode='lines+markers',
            line=dict(color="#00F0FF", width=4),
            marker=dict(size=12)
        )
    )

    fig2.update_layout(
        title="Safety Score History",
        paper_bgcolor="#0B0F19",
        plot_bgcolor="#0B0F19",
        font=dict(color="white"),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True)
    )

    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# ASSESSMENT FORM
# -----------------------------
st.markdown("## 📝 New Assessment")

chair = st.slider("Chair Ergonomics",0,100,70)
monitor = st.slider("Monitor Position",0,100,60)
keyboard = st.slider("Keyboard & Mouse",0,100,75)
lighting = st.slider("Lighting",0,100,80)
posture = st.slider("Posture",0,100,55)
breaks = st.slider("Break Frequency",0,100,65)

if st.button("Calculate Safety Score"):

    score = round(
        np.mean(
            [
                chair,
                monitor,
                keyboard,
                lighting,
                posture,
                breaks
            ]
        )
    )

    if score >= 80:
        risk = "Low Risk ✅"

    elif score >= 60:
        risk = "Medium Risk ⚠"

    else:
        risk = "High Risk ❌"

    st.success(
        f"Safety Score: {score}% | {risk}"
    )

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")

st.markdown(
    """
    <center>
    <span style='color:#A0AEC0'>
    Workstation Safety Scorer © 2026
    </span>
    </center>
    """,
    unsafe_allow_html=True
)
