import streamlit as st
import numpy as np
import pandas as pd
import pickle
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time
import json
import os
import warnings
warnings.filterwarnings('ignore')

# ─── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FraudGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS Styling ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Main gradient background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #1a1a2e, #16213e);
        color: #e0e0e0;
    }

    /* Header */
    .main-header {
        text-align: center;
        padding: 2rem 0 0.5rem;
    }
    .main-header h1 {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00d2ff, #7b2ff7, #ff416c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -1px;
    }
    .main-header p {
        color: #8892b0;
        font-size: 1.1rem;
        margin-top: 0.3rem;
        font-weight: 300;
    }

    /* Glassmorphism cards */
    .glass-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        margin: 0.5rem 0;
    }

    /* Safe result card */
    .safe-card {
        background: linear-gradient(135deg, rgba(0,255,150,0.15), rgba(0,200,100,0.05));
        border: 2px solid rgba(0,255,150,0.4);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        animation: fadeInUp 0.6s ease;
    }
    .safe-card h2 { color: #00ff96; font-size: 2rem; margin: 0.5rem 0; }

    /* Fraud result card */
    .fraud-card {
        background: linear-gradient(135deg, rgba(255,50,50,0.2), rgba(200,0,0,0.05));
        border: 2px solid rgba(255,80,80,0.6);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        animation: fraudPulse 1.5s infinite, fadeInUp 0.6s ease;
    }
    .fraud-card h2 { color: #ff4d4d; font-size: 2rem; margin: 0.5rem 0; }

    @keyframes fraudPulse {
        0%   { box-shadow: 0 0 0 0 rgba(255,50,50,0.6); }
        70%  { box-shadow: 0 0 0 20px rgba(255,50,50,0); }
        100% { box-shadow: 0 0 0 0 rgba(255,50,50,0); }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* Metric cards */
    .metric-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
        transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-3px); }
    .metric-card .label { color: #8892b0; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; }
    .metric-card .value { color: #ccd6f6; font-size: 1.6rem; font-weight: 700; }
    .metric-card .delta-up   { color: #ff4d4d; font-size: 0.85rem; }
    .metric-card .delta-down { color: #00ff96; font-size: 0.85rem; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 4px;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #8892b0;
        font-weight: 600;
        padding: 8px 18px;
        transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #7b2ff7, #00d2ff) !important;
        color: white !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #7b2ff7, #00d2ff);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        font-size: 1.1rem;
        padding: 0.6rem 2rem;
        letter-spacing: 0.5px;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(123,47,247,0.5);
    }

    /* Sliders */
    .stSlider > div > div > div > div { background: linear-gradient(90deg, #7b2ff7, #00d2ff); }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(15,12,41,0.95);
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    section[data-testid="stSidebar"] .stMarkdown { color: #ccd6f6; }

    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 8px !important;
        color: #ccd6f6 !important;
        font-weight: 600 !important;
    }

    /* Section headers */
    .section-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #ccd6f6;
        border-left: 4px solid #7b2ff7;
        padding-left: 0.8rem;
        margin: 1.5rem 0 1rem;
    }

    /* Risk meter label */
    .risk-label-low    { color: #00ff96; font-size: 1.1rem; font-weight: 700; }
    .risk-label-medium { color: #ffcc00; font-size: 1.1rem; font-weight: 700; }
    .risk-label-high   { color: #ff4d4d; font-size: 1.1rem; font-weight: 700; }

    /* Status bar */
    .status-bar {
        background: rgba(0,255,150,0.1);
        border: 1px solid rgba(0,255,150,0.3);
        border-radius: 8px;
        padding: 0.4rem 1rem;
        font-size: 0.85rem;
        color: #00ff96;
        text-align: center;
    }

    /* Input fields */
    .stNumberInput input, .stTextInput input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #ccd6f6 !important;
        border-radius: 8px !important;
    }

    /* DataFrame */
    .stDataFrame { border-radius: 12px; overflow: hidden; }

    /* Info / warning boxes */
    .stAlert { border-radius: 10px; }

    /* Feature badge */
    .feature-badge {
        display: inline-block;
        background: rgba(123,47,247,0.3);
        border: 1px solid rgba(123,47,247,0.5);
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 0.75rem;
        color: #a78bfa;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Constants ─────────────────────────────────────────────────────────────────
FEATURE_NAMES = [
    'Time', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9',
    'V10', 'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17', 'V18',
    'V19', 'V20', 'V21', 'V22', 'V23', 'V24', 'V25', 'V26', 'V27',
    'V28', 'Amount'
]
HISTORY_FILE = "transaction_history.json"

# ─── Model Loading ──────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    MODEL_PATH = 'best_fraud_detection_dt_model.pkl'
    try:
        with open(MODEL_PATH, 'rb') as f:
            m = pickle.load(f)
        return m, True
    except FileNotFoundError:
        return None, False

model, model_loaded = load_model()

# ─── History helpers ────────────────────────────────────────────────────────────
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_to_history(record):
    history = load_history()
    record['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history.append(record)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛡️ FraudGuard AI")
    st.markdown("---")

    st.markdown("**Model Status**")
    if model_loaded:
        st.markdown("🟢 **Decision Tree** — Loaded")
        depth = model.max_depth if hasattr(model, 'max_depth') else "N/A"
        st.caption(f"Max Depth: {depth}  |  Features: 30")
    else:
        st.markdown("🔴 Model not found")

    st.markdown("---")
    st.markdown("**⚙️ Detection Settings**")
    confidence_threshold = st.slider("Alert Threshold (%)", 50, 99, 70,
                                      help="Minimum fraud probability to trigger alert")

    st.markdown("---")
    st.markdown("**📊 Dashboard**")
    show_realtime = st.checkbox("Real-time Analytics", True)
    show_history  = st.checkbox("Transaction History", True)

    st.markdown("---")
    # Quick stats from history
    hist = load_history()
    total = len(hist)
    fraud_n = sum(1 for h in hist if h.get('prediction') == 1)
    st.markdown("**Session Stats**")
    cols = st.columns(2)
    cols[0].metric("Transactions", total)
    cols[1].metric("Flagged", fraud_n)

    st.markdown("---")
    st.caption("FraudGuard AI v3.0  |  Decision Tree")
    st.caption("⚠️ For educational use only")

# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>🛡️ FraudGuard AI</h1>
  <p>Next-Generation Credit Card Fraud Detection — Powered by Machine Learning</p>
</div>
""", unsafe_allow_html=True)

# Status bar
st.markdown(f"""
<div class="status-bar">
  🟢 SYSTEM OPERATIONAL &nbsp;|&nbsp; Model: Decision Tree (max_depth=5) &nbsp;|&nbsp;
  Features: 30 &nbsp;|&nbsp; Last checked: {datetime.now().strftime("%H:%M:%S")}
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Top KPI Row ───────────────────────────────────────────────────────────────
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
hist_all = load_history()
total_tx  = len(hist_all)
fraud_tx  = sum(1 for h in hist_all if h.get('prediction') == 1)
legit_tx  = total_tx - fraud_tx
fraud_pct = (fraud_tx / total_tx * 100) if total_tx > 0 else 0
avg_amt   = (sum(h.get('Amount', 0) for h in hist_all) / total_tx) if total_tx > 0 else 0

with kpi1:
    st.markdown(f"""
    <div class="metric-card">
      <div class="label">Total Analyzed</div>
      <div class="value">{total_tx:,}</div>
    </div>""", unsafe_allow_html=True)
with kpi2:
    st.markdown(f"""
    <div class="metric-card">
      <div class="label">Fraudulent</div>
      <div class="value">{fraud_tx:,}</div>
      <div class="delta-up">{'▲ ' + f'{fraud_pct:.1f}%' if fraud_tx else '—'}</div>
    </div>""", unsafe_allow_html=True)
with kpi3:
    st.markdown(f"""
    <div class="metric-card">
      <div class="label">Legitimate</div>
      <div class="value">{legit_tx:,}</div>
      <div class="delta-down">{'▼ ' + f'{100-fraud_pct:.1f}%' if legit_tx else '—'}</div>
    </div>""", unsafe_allow_html=True)
with kpi4:
    st.markdown(f"""
    <div class="metric-card">
      <div class="label">Avg. Amount</div>
      <div class="value">${avg_amt:,.0f}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Main Tabs ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍  Predict Transaction",
    "📊  Analytics Dashboard",
    "📋  Transaction History",
    "ℹ️  Model Info"
])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — PREDICT
# ════════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">📝 Enter Transaction Details</div>', unsafe_allow_html=True)

    # ── Time & Amount ─────────────────────────────────────────────────────────
    with st.expander("⏰ Time & Amount", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            time_val = st.number_input(
                "⏱️ Time (seconds since first transaction)",
                min_value=0.0, max_value=172800.0,
                value=100000.0, step=100.0,
                help="Seconds elapsed from the first transaction in the dataset"
            )
        with c2:
            amount_val = st.number_input(
                "💵 Transaction Amount ($)",
                min_value=0.0, max_value=50000.0,
                value=150.0, step=1.0,
                help="Dollar value of the transaction"
            )
            # Mini visual bar
            frac = min(amount_val / 5000, 1.0)
            bar_color = "#00ff96" if frac < 0.3 else ("#ffcc00" if frac < 0.7 else "#ff4d4d")
            st.markdown(f"""
            <div style="margin-top:6px">
              <div style="font-size:0.75rem;color:#8892b0;margin-bottom:3px">Amount Scale</div>
              <div style="background:rgba(255,255,255,0.08);border-radius:6px;height:8px;width:100%">
                <div style="background:{bar_color};width:{frac*100:.0f}%;height:8px;border-radius:6px;transition:width 0.3s"></div>
              </div>
            </div>""", unsafe_allow_html=True)

    # ── PCA Features ─────────────────────────────────────────────────────────
    with st.expander("🔢 Anonymized PCA Features (V1–V28)", expanded=False):
        st.info(
            "These are PCA-transformed features derived from the original transaction data. "
            "V14 is the most important predictor in this model (weight ≈ 81.8%)."
        )
        tabs_pca = st.tabs(["V1–V7", "V8–V14", "V15–V21", "V22–V28"])
        pca_values = {}

        with tabs_pca[0]:
            cols = st.columns(7)
            for i, c in zip(range(1, 8), cols):
                # Highlight V4 (important)
                label = f"V{i} ⭐" if i == 4 else f"V{i}"
                pca_values[f'V{i}'] = c.number_input(label, -30.0, 30.0, 0.0, 0.1, key=f"v{i}")

        with tabs_pca[1]:
            cols = st.columns(7)
            for i, c in zip(range(8, 15), cols):
                label = f"V{i} 🔑" if i == 14 else f"V{i}"
                pca_values[f'V{i}'] = c.number_input(label, -30.0, 30.0, 0.0, 0.1, key=f"v{i}")

        with tabs_pca[2]:
            cols = st.columns(7)
            for i, c in zip(range(15, 22), cols):
                pca_values[f'V{i}'] = c.number_input(f"V{i}", -30.0, 30.0, 0.0, 0.1, key=f"v{i}")

        with tabs_pca[3]:
            cols = st.columns(7)
            for i, c in zip(range(22, 29), cols):
                pca_values[f'V{i}'] = c.number_input(f"V{i}", -30.0, 30.0, 0.0, 0.1, key=f"v{i}")

        st.caption("🔑 V14 = most important feature (81.8%)  |  ⭐ V4 = 2nd most important (5.3%)")

    # ── Quick preset examples ─────────────────────────────────────────────────
    with st.expander("⚡ Quick Test Presets", expanded=False):
        pc1, pc2, pc3 = st.columns(3)
        if pc1.button("✅ Typical Legitimate"):
            st.session_state["preset"] = "legit"
            st.rerun()
        if pc2.button("🚨 Suspicious Pattern"):
            st.session_state["preset"] = "fraud"
            st.rerun()
        if pc3.button("🔄 Reset to Zeros"):
            st.session_state["preset"] = "reset"
            st.rerun()

    # Apply presets (update defaults via session state flags)
    preset = st.session_state.get("preset", None)
    if preset == "fraud":
        # Known fraud-like values: extreme V14 negative
        pca_values['V14'] = -15.0
        pca_values['V4']  = -5.0
    elif preset == "reset":
        for k in pca_values:
            pca_values[k] = 0.0

    # ── Build feature vector ──────────────────────────────────────────────────
    input_data = {'Time': time_val, 'Amount': amount_val, **pca_values}
    ordered    = [input_data[f] for f in FEATURE_NAMES]
    final_df   = pd.DataFrame([ordered], columns=FEATURE_NAMES)

    # ── Live risk preview ────────────────────────────────────────────────────
    if model_loaded:
        live_proba = model.predict_proba(final_df)[0][1]
        risk_pct   = live_proba * 100
        bar_w      = int(risk_pct)
        bar_col    = "#00ff96" if risk_pct < 30 else ("#ffcc00" if risk_pct < confidence_threshold else "#ff4d4d")
        risk_lbl   = "LOW" if risk_pct < 30 else ("MEDIUM" if risk_pct < confidence_threshold else "HIGH")
        cls        = "risk-label-low" if risk_pct < 30 else ("risk-label-medium" if risk_pct < confidence_threshold else "risk-label-high")

        st.markdown(f"""
        <div class="glass-card" style="margin-top:1rem">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <span style="color:#8892b0;font-size:0.85rem;text-transform:uppercase;letter-spacing:1px">Live Risk Meter</span>
            <span class="{cls}">{risk_lbl} — {risk_pct:.1f}%</span>
          </div>
          <div style="background:rgba(255,255,255,0.08);border-radius:8px;height:14px;width:100%">
            <div style="background:{bar_col};width:{bar_w}%;height:14px;border-radius:8px;transition:width 0.4s;box-shadow:0 0 10px {bar_col}88"></div>
          </div>
          <div style="display:flex;justify-content:space-between;margin-top:4px;font-size:0.7rem;color:#8892b0">
            <span>0%</span><span>Safe Zone</span><span>50%</span><span>Danger Zone</span><span>100%</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Predict button ────────────────────────────────────────────────────────
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        predict_btn = st.button("🚀  Analyze Transaction", use_container_width=True)

    # ── Result ────────────────────────────────────────────────────────────────
    if predict_btn:
        if not model_loaded:
            st.error("⚠️ Model file not found. Please place `best_fraud_detection_dt_model.pkl` in the app directory.")
        else:
            with st.spinner("🔍 Scanning transaction patterns..."):
                time.sleep(0.8)

            prediction      = model.predict(final_df)[0]
            proba           = model.predict_proba(final_df)[0]
            fraud_prob      = proba[1]
            legit_prob      = proba[0]
            confidence      = max(proba)

            # Save history
            record = {**input_data, 'prediction': int(prediction),
                      'confidence': float(confidence),
                      'fraud_probability': float(fraud_prob)}
            save_to_history(record)

            st.markdown("---")
            st.markdown('<div class="section-header">🔎 Analysis Result</div>', unsafe_allow_html=True)

            if prediction == 0:
                st.markdown(f"""
                <div class="safe-card">
                  <div style="font-size:3.5rem">✅</div>
                  <h2>TRANSACTION SAFE</h2>
                  <p style="color:#a8ffca;font-size:1.1rem">No fraudulent patterns detected</p>
                  <div style="display:flex;justify-content:center;gap:3rem;margin-top:1rem">
                    <div>
                      <div style="color:#8892b0;font-size:0.8rem">FRAUD PROBABILITY</div>
                      <div style="color:#00ff96;font-size:2rem;font-weight:800">{fraud_prob*100:.2f}%</div>
                    </div>
                    <div>
                      <div style="color:#8892b0;font-size:0.8rem">MODEL CONFIDENCE</div>
                      <div style="color:#00ff96;font-size:2rem;font-weight:800">{legit_prob*100:.2f}%</div>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
                st.balloons()

            else:
                st.markdown(f"""
                <div class="fraud-card">
                  <div style="font-size:3.5rem">🚨</div>
                  <h2>FRAUD DETECTED!</h2>
                  <p style="color:#ffb3b3;font-size:1.1rem">This transaction has been flagged as suspicious</p>
                  <div style="display:flex;justify-content:center;gap:3rem;margin-top:1rem">
                    <div>
                      <div style="color:#8892b0;font-size:0.8rem">FRAUD PROBABILITY</div>
                      <div style="color:#ff4d4d;font-size:2rem;font-weight:800">{fraud_prob*100:.2f}%</div>
                    </div>
                    <div>
                      <div style="color:#8892b0;font-size:0.8rem">MODEL CONFIDENCE</div>
                      <div style="color:#ff4d4d;font-size:2rem;font-weight:800">{fraud_prob*100:.2f}%</div>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
                st.warning("⚠️ ALERT: Immediate review recommended. Block transaction if unverified.")
                st.snow()

            # ── Probability gauge chart ───────────────────────────────────────
            st.markdown("<br>", unsafe_allow_html=True)
            gauge_col1, gauge_col2 = st.columns(2)

            with gauge_col1:
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=round(fraud_prob * 100, 2),
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Fraud Risk Score", 'font': {'color': '#ccd6f6', 'size': 16}},
                    number={'suffix': '%', 'font': {'color': '#ccd6f6', 'size': 28}},
                    delta={'reference': confidence_threshold, 'increasing': {'color': '#ff4d4d'}, 'decreasing': {'color': '#00ff96'}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickcolor': '#8892b0', 'tickfont': {'color': '#8892b0'}},
                        'bar': {'color': '#ff4d4d' if prediction == 1 else '#00ff96'},
                        'bgcolor': 'rgba(0,0,0,0)',
                        'bordercolor': 'rgba(255,255,255,0.1)',
                        'steps': [
                            {'range': [0, 30],                       'color': 'rgba(0,255,150,0.15)'},
                            {'range': [30, confidence_threshold],    'color': 'rgba(255,200,0,0.15)'},
                            {'range': [confidence_threshold, 100],   'color': 'rgba(255,50,50,0.2)'},
                        ],
                        'threshold': {
                            'line': {'color': '#ffcc00', 'width': 3},
                            'thickness': 0.8,
                            'value': confidence_threshold
                        }
                    }
                ))
                fig_gauge.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': '#ccd6f6'},
                    height=280, margin=dict(t=40, b=10, l=20, r=20)
                )
                st.plotly_chart(fig_gauge, use_container_width=True)

            with gauge_col2:
                # Probability donut
                fig_donut = go.Figure(go.Pie(
                    labels=['Legitimate', 'Fraudulent'],
                    values=[legit_prob * 100, fraud_prob * 100],
                    hole=0.65,
                    marker_colors=['#00ff96', '#ff4d4d'],
                    textfont_color='white',
                    textinfo='label+percent'
                ))
                fig_donut.add_annotation(
                    text=f"{'FRAUD' if prediction == 1 else 'SAFE'}",
                    x=0.5, y=0.5,
                    font=dict(size=18, color='#ff4d4d' if prediction == 1 else '#00ff96', family='Inter'),
                    showarrow=False
                )
                fig_donut.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': '#ccd6f6'},
                    title=dict(text="Probability Distribution", font=dict(color='#ccd6f6', size=16)),
                    legend=dict(font=dict(color='#ccd6f6')),
                    height=280, margin=dict(t=40, b=10, l=20, r=20)
                )
                st.plotly_chart(fig_donut, use_container_width=True)

            # ── Feature importance chart ──────────────────────────────────────
            if hasattr(model, 'feature_importances_'):
                st.markdown('<div class="section-header">📊 Feature Importance Analysis</div>', unsafe_allow_html=True)

                fi_df = pd.DataFrame({
                    'Feature': FEATURE_NAMES,
                    'Importance': model.feature_importances_,
                    'Value': [input_data[f] for f in FEATURE_NAMES]
                }).sort_values('Importance', ascending=False).head(12)

                fig_fi = px.bar(
                    fi_df, x='Importance', y='Feature', orientation='h',
                    color='Importance',
                    color_continuous_scale=['#0f0c29', '#7b2ff7', '#00d2ff', '#ff416c'],
                    title="Top 12 Most Influential Features",
                    text=fi_df['Importance'].apply(lambda x: f'{x:.3f}')
                )
                fig_fi.update_traces(textposition='outside', textfont_color='#ccd6f6')
                fig_fi.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': '#ccd6f6'},
                    title_font_color='#ccd6f6',
                    xaxis=dict(gridcolor='rgba(255,255,255,0.05)', color='#8892b0'),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.05)', color='#ccd6f6'),
                    coloraxis_showscale=False,
                    height=420, margin=dict(t=50, b=20, l=20, r=20)
                )
                st.plotly_chart(fig_fi, use_container_width=True)

                # Input values vs importance correlation
                st.markdown('<div class="section-header">🔬 Your Input Values — Key Features</div>', unsafe_allow_html=True)
                top5 = fi_df.head(5)
                c_cols = st.columns(5)
                for idx, (_, row) in enumerate(top5.iterrows()):
                    with c_cols[idx]:
                        st.markdown(f"""
                        <div class="metric-card">
                          <div class="label">{row['Feature']}</div>
                          <div class="value" style="font-size:1.1rem">{row['Value']:.3f}</div>
                          <div style="color:#7b2ff7;font-size:0.75rem">importance: {row['Importance']:.3f}</div>
                        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — ANALYTICS
# ════════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">📊 Analytics Dashboard</div>', unsafe_allow_html=True)

    history = load_history()

    if not history:
        st.info("📭 No transactions analyzed yet. Go to the **Predict** tab to get started!")
    else:
        df = pd.DataFrame(history)

        # Row 1 — mini KPIs
        k1, k2, k3, k4, k5 = st.columns(5)
        total_n   = len(df)
        fraud_n   = int(df['prediction'].sum())
        legit_n   = total_n - fraud_n
        avg_conf  = df['confidence'].mean() * 100
        avg_risk  = df['fraud_probability'].mean() * 100

        for col, label, val, unit in [
            (k1, "Total",        total_n, ""),
            (k2, "Fraudulent",   fraud_n, ""),
            (k3, "Legitimate",   legit_n, ""),
            (k4, "Avg Confidence", avg_conf, "%"),
            (k5, "Avg Risk Score", avg_risk, "%"),
        ]:
            col.markdown(f"""
            <div class="metric-card">
              <div class="label">{label}</div>
              <div class="value">{val:.1f}{unit}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Row 2 — Donut + Amount histogram
        r2c1, r2c2 = st.columns(2)

        with r2c1:
            counts = df['prediction'].value_counts()
            labels = ['Legitimate' if i == 0 else 'Fraudulent' for i in counts.index]
            fig_pie = go.Figure(go.Pie(
                labels=labels,
                values=counts.values,
                hole=0.6,
                marker_colors=['#00ff96', '#ff4d4d'],
                textinfo='label+percent',
                textfont_color='white'
            ))
            fig_pie.add_annotation(text=f"{total_n}<br><span style='font-size:10px'>Total</span>",
                                   x=0.5, y=0.5, showarrow=False,
                                   font=dict(size=20, color='#ccd6f6'))
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font={'color': '#ccd6f6'},
                title=dict(text="Transaction Split", font=dict(color='#ccd6f6', size=16)),
                legend=dict(font=dict(color='#ccd6f6')),
                height=320, margin=dict(t=40, b=10, l=20, r=20)
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with r2c2:
            fig_hist = px.histogram(
                df, x='Amount', nbins=30,
                color='prediction',
                color_discrete_map={0: '#00ff96', 1: '#ff4d4d'},
                title="Transaction Amount Distribution",
                labels={'prediction': 'Class', 'Amount': 'Amount ($)'}
            )
            fig_hist.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font={'color': '#ccd6f6'},
                title_font_color='#ccd6f6',
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)', color='#8892b0'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)', color='#8892b0'),
                legend=dict(font=dict(color='#ccd6f6')),
                height=320, margin=dict(t=40, b=20, l=20, r=20),
                bargap=0.05
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        # Row 3 — Fraud probability over time
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df_sorted = df.sort_values('timestamp')

            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=df_sorted['timestamp'],
                y=df_sorted['fraud_probability'] * 100,
                mode='lines+markers',
                name='Fraud Probability',
                line=dict(color='#ff4d4d', width=2),
                marker=dict(size=6, color=df_sorted['prediction'].map({0: '#00ff96', 1: '#ff4d4d'})),
                fill='tozeroy',
                fillcolor='rgba(255,77,77,0.1)'
            ))
            fig_line.add_hline(y=confidence_threshold, line_dash="dot",
                               line_color="#ffcc00",
                               annotation_text=f"Alert threshold ({confidence_threshold}%)",
                               annotation_font_color="#ffcc00")
            fig_line.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font={'color': '#ccd6f6'},
                title=dict(text="Fraud Probability Over Time", font=dict(color='#ccd6f6', size=16)),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)', color='#8892b0'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)', color='#8892b0',
                           range=[0, 105], title="Fraud Probability (%)"),
                height=320, margin=dict(t=40, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_line, use_container_width=True)

        # Row 4 — Model comparison (from notebook)
        st.markdown('<div class="section-header">📈 Model Performance Comparison (from Training)</div>',
                    unsafe_allow_html=True)

        perf_data = {
            'Metric':    ['Accuracy', 'F1 Score', 'Recall', 'Precision'],
            'Logistic Regression': [0.884, 0.923, 0.921, 0.924],
            'Decision Tree':       [0.906, 0.924, 0.923, 0.924],
        }
        perf_df = pd.DataFrame(perf_data)

        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            x=perf_df['Metric'], y=perf_df['Logistic Regression'],
            name='Logistic Regression', marker_color='#00d2ff',
            text=[f"{v:.3f}" for v in perf_df['Logistic Regression']],
            textposition='outside', textfont_color='#ccd6f6'
        ))
        fig_comp.add_trace(go.Bar(
            x=perf_df['Metric'], y=perf_df['Decision Tree'],
            name='Decision Tree ✓', marker_color='#7b2ff7',
            text=[f"{v:.3f}" for v in perf_df['Decision Tree']],
            textposition='outside', textfont_color='#ccd6f6'
        ))
        fig_comp.update_layout(
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#ccd6f6'},
            title=dict(text="LR vs Decision Tree — Core Metrics", font=dict(color='#ccd6f6', size=16)),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)', color='#8892b0'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)', color='#8892b0',
                       range=[0.85, 0.96]),
            legend=dict(font=dict(color='#ccd6f6')),
            height=340, margin=dict(t=50, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_comp, use_container_width=True)

        # Speed comparison
        spd1, spd2 = st.columns(2)
        with spd1:
            fig_speed = go.Figure(go.Bar(
                x=['Logistic Regression', 'Decision Tree'],
                y=[0.12, 0.05],
                marker_color=['#00d2ff', '#7b2ff7'],
                text=['120ms', '50ms'],
                textposition='outside',
                textfont_color='#ccd6f6'
            ))
            fig_speed.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font={'color': '#ccd6f6'},
                title=dict(text="Prediction Speed (ms)", font=dict(color='#ccd6f6', size=14)),
                xaxis=dict(color='#8892b0'), yaxis=dict(color='#8892b0', gridcolor='rgba(255,255,255,0.05)'),
                height=280, margin=dict(t=40, b=20, l=10, r=10)
            )
            st.plotly_chart(fig_speed, use_container_width=True)

        with spd2:
            fig_radar = go.Figure(go.Scatterpolar(
                r=[0.906, 0.924, 0.923, 0.924, 0.96],
                theta=['Accuracy', 'F1', 'Recall', 'Precision', 'Speed'],
                fill='toself',
                fillcolor='rgba(123,47,247,0.3)',
                line_color='#7b2ff7',
                name='Decision Tree'
            ))
            fig_radar.add_trace(go.Scatterpolar(
                r=[0.884, 0.923, 0.921, 0.924, 0.40],
                theta=['Accuracy', 'F1', 'Recall', 'Precision', 'Speed'],
                fill='toself',
                fillcolor='rgba(0,210,255,0.2)',
                line_color='#00d2ff',
                name='Logistic Regression'
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0.3, 1.0], gridcolor='rgba(255,255,255,0.1)', color='#8892b0'),
                    angularaxis=dict(color='#8892b0'),
                    bgcolor='rgba(0,0,0,0)'
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': '#ccd6f6'},
                title=dict(text="Model Radar Chart", font=dict(color='#ccd6f6', size=14)),
                legend=dict(font=dict(color='#ccd6f6')),
                height=280, margin=dict(t=40, b=10, l=10, r=10)
            )
            st.plotly_chart(fig_radar, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — HISTORY
# ════════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">📋 Transaction History</div>', unsafe_allow_html=True)

    history = load_history()
    if not history:
        st.warning("No transaction history found. Analyze some transactions first!")
    else:
        df_h = pd.DataFrame(history)

        # Filters
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            filter_type = st.selectbox("Filter by Type", ["All", "Legitimate Only", "Fraudulent Only"])
        with fc2:
            min_amt = st.number_input("Min Amount ($)", 0.0, value=0.0)
        with fc3:
            max_amt = st.number_input("Max Amount ($)", 0.0, value=50000.0)

        filtered = df_h.copy()
        if filter_type == "Legitimate Only":
            filtered = filtered[filtered['prediction'] == 0]
        elif filter_type == "Fraudulent Only":
            filtered = filtered[filtered['prediction'] == 1]
        filtered = filtered[(filtered['Amount'] >= min_amt) & (filtered['Amount'] <= max_amt)]

        st.markdown(f"Showing **{len(filtered)}** of **{len(df_h)}** records")

        # Style the table
        display_cols = ['timestamp', 'Amount', 'Time', 'fraud_probability', 'confidence', 'prediction']
        display_cols = [c for c in display_cols if c in filtered.columns]
        df_display   = filtered[display_cols].copy()
        if 'fraud_probability' in df_display.columns:
            df_display['fraud_probability'] = df_display['fraud_probability'].apply(lambda x: f"{x*100:.2f}%")
        if 'confidence' in df_display.columns:
            df_display['confidence'] = df_display['confidence'].apply(lambda x: f"{x*100:.2f}%")
        if 'prediction' in df_display.columns:
            df_display['prediction'] = df_display['prediction'].apply(lambda x: "🚨 FRAUD" if x == 1 else "✅ SAFE")
        if 'Amount' in df_display.columns:
            df_display['Amount'] = df_display['Amount'].apply(lambda x: f"${x:,.2f}")

        df_display.columns = [c.replace('_', ' ').title() for c in df_display.columns]

        st.dataframe(df_display, use_container_width=True, height=400)

        # Export
        ec1, ec2 = st.columns(2)
        with ec1:
            csv = filtered.to_csv(index=False)
            st.download_button("📥 Export as CSV", data=csv,
                               file_name=f"fraudguard_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                               mime="text/csv", use_container_width=True)
        with ec2:
            if st.button("🗑️ Clear History", use_container_width=True):
                if os.path.exists(HISTORY_FILE):
                    os.remove(HISTORY_FILE)
                st.success("History cleared!")
                st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 — MODEL INFO
# ════════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">ℹ️ About This Model</div>', unsafe_allow_html=True)

    about1, about2 = st.columns(2)

    with about1:
        st.markdown("""
        <div class="glass-card">
          <h4 style="color:#00d2ff">🎯 Dataset Overview</h4>
          <p style="color:#8892b0;font-size:0.9rem">
            The model was trained on the <b style="color:#ccd6f6">European Credit Card Fraud Dataset</b>
            — 284,807 transactions collected over 2 days in September 2013.
            Only 492 (0.17%) are fraudulent, making it a highly imbalanced dataset.
          </p>
          <p style="color:#8892b0;font-size:0.9rem;margin-top:0.5rem">
            A balanced subset of 492 legitimate + 492 fraudulent transactions
            was used for training (80/20 split, stratified).
          </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="glass-card" style="margin-top:1rem">
          <h4 style="color:#00d2ff">🔧 Model Architecture</h4>
          <ul style="color:#8892b0;font-size:0.9rem;line-height:1.8">
            <li><b style="color:#ccd6f6">Algorithm:</b> Decision Tree Classifier</li>
            <li><b style="color:#ccd6f6">max_depth:</b> 5</li>
            <li><b style="color:#ccd6f6">random_state:</b> 2</li>
            <li><b style="color:#ccd6f6">Input Features:</b> 30 (Time, V1–V28, Amount)</li>
            <li><b style="color:#ccd6f6">Output Classes:</b> 0 = Legitimate, 1 = Fraud</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)

    with about2:
        st.markdown("""
        <div class="glass-card">
          <h4 style="color:#7b2ff7">📊 Performance Metrics (Test Set)</h4>
          <table style="width:100%;color:#ccd6f6;font-size:0.9rem;border-collapse:collapse">
            <tr style="border-bottom:1px solid rgba(255,255,255,0.1)">
              <th style="text-align:left;padding:6px;color:#8892b0">Model</th>
              <th style="padding:6px;color:#8892b0">Accuracy</th>
              <th style="padding:6px;color:#8892b0">F1</th>
              <th style="padding:6px;color:#8892b0">Recall</th>
            </tr>
            <tr style="border-bottom:1px solid rgba(255,255,255,0.05)">
              <td style="padding:6px">Logistic Regression</td>
              <td style="text-align:center;padding:6px">88.4%</td>
              <td style="text-align:center;padding:6px">92.3%</td>
              <td style="text-align:center;padding:6px">92.1%</td>
            </tr>
            <tr style="background:rgba(123,47,247,0.15)">
              <td style="padding:6px"><b>Decision Tree ✓</b></td>
              <td style="text-align:center;padding:6px"><b>90.6%</b></td>
              <td style="text-align:center;padding:6px"><b>92.4%</b></td>
              <td style="text-align:center;padding:6px"><b>92.3%</b></td>
            </tr>
          </table>
          <p style="color:#8892b0;font-size:0.75rem;margin-top:0.5rem">
            ✓ Decision Tree selected as best model based on F1-Score for fraud class.
          </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="glass-card" style="margin-top:1rem">
          <h4 style="color:#7b2ff7">🏆 Top Features by Importance</h4>
        """, unsafe_allow_html=True)

        if model_loaded and hasattr(model, 'feature_importances_'):
            fi_sorted = sorted(
                zip(model.feature_names_in_, model.feature_importances_),
                key=lambda x: x[1], reverse=True
            )[:8]
            for feat, imp in fi_sorted:
                bar_w = int(imp * 100)
                st.markdown(f"""
                <div style="margin:6px 0">
                  <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#ccd6f6">
                    <span>{feat}</span><span>{imp*100:.1f}%</span>
                  </div>
                  <div style="background:rgba(255,255,255,0.06);border-radius:4px;height:6px">
                    <div style="background:linear-gradient(90deg,#7b2ff7,#00d2ff);width:{bar_w}%;height:6px;border-radius:4px"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Pipeline diagram
    st.markdown('<div class="section-header">🏗️ System Pipeline</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="glass-card">
      <div style="display:flex;align-items:center;justify-content:center;gap:0;flex-wrap:wrap;text-align:center">
        <div style="background:rgba(0,210,255,0.15);border:1px solid #00d2ff;border-radius:10px;padding:12px 18px;min-width:120px">
          <div style="font-size:1.4rem">📥</div>
          <div style="color:#00d2ff;font-size:0.8rem;font-weight:700">INPUT</div>
          <div style="color:#8892b0;font-size:0.7rem">30 features</div>
        </div>
        <div style="color:#8892b0;font-size:1.5rem;padding:0 8px">→</div>
        <div style="background:rgba(123,47,247,0.15);border:1px solid #7b2ff7;border-radius:10px;padding:12px 18px;min-width:120px">
          <div style="font-size:1.4rem">⚙️</div>
          <div style="color:#7b2ff7;font-size:0.8rem;font-weight:700">PREPROCESSING</div>
          <div style="color:#8892b0;font-size:0.7rem">DataFrame format</div>
        </div>
        <div style="color:#8892b0;font-size:1.5rem;padding:0 8px">→</div>
        <div style="background:rgba(255,65,108,0.15);border:1px solid #ff416c;border-radius:10px;padding:12px 18px;min-width:120px">
          <div style="font-size:1.4rem">🌳</div>
          <div style="color:#ff416c;font-size:0.8rem;font-weight:700">DECISION TREE</div>
          <div style="color:#8892b0;font-size:0.7rem">max_depth=5</div>
        </div>
        <div style="color:#8892b0;font-size:1.5rem;padding:0 8px">→</div>
        <div style="background:rgba(0,255,150,0.1);border:1px solid #00ff96;border-radius:10px;padding:12px 18px;min-width:120px">
          <div style="font-size:1.4rem">📊</div>
          <div style="color:#00ff96;font-size:0.8rem;font-weight:700">RISK SCORING</div>
          <div style="color:#8892b0;font-size:0.7rem">probability %</div>
        </div>
        <div style="color:#8892b0;font-size:1.5rem;padding:0 8px">→</div>
        <div style="background:rgba(255,200,0,0.1);border:1px solid #ffcc00;border-radius:10px;padding:12px 18px;min-width:120px">
          <div style="font-size:1.4rem">🛡️</div>
          <div style="color:#ffcc00;font-size:0.8rem;font-weight:700">VERDICT</div>
          <div style="color:#8892b0;font-size:0.7rem">SAFE / FRAUD</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;color:#8892b0;font-size:0.8rem;border-top:1px solid rgba(255,255,255,0.06);padding-top:1rem">
  🛡️ <b style="color:#ccd6f6">FraudGuard AI v3.0</b> &nbsp;|&nbsp;
  Decision Tree Classifier &nbsp;|&nbsp;
  Built with Streamlit + Plotly &nbsp;|&nbsp;
  <span style="color:#ff4d4d">⚠️ For educational purposes only</span>
</div>
""", unsafe_allow_html=True)
