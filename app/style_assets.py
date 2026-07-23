import streamlit as st

STYLE_SHEET = """
<style>
body, .stApp {
    background: #f8fafc !important;
    color: #111827 !important;
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
}

.stApp {
    padding: 1rem 2rem 2rem !important;
}

.sidebar .sidebar-content {
    background: #eef6fb !important;
}

.sidebar-content .stRadio > div {
    gap: 8px !important;
}

.stMarkdown, .stTextArea, .stButton>button {
    font-family: 'Inter', sans-serif !important;
}

.page-header {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 18px;
    align-items: flex-start;
    margin-bottom: 24px;
}

.page-header h1 {
    margin: 0;
    font-size: 36px;
    line-height: 1.05;
}

.page-subtitle {
    color: #475569;
    margin: 8px 0 0;
    max-width: 680px;
}

.eyebrow {
    color: #0f766e;
    font-size: 12px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 10px;
    font-weight: 700;
}

.header-status {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.status-chip,
.city-chip {
    background: #ffffff;
    padding: 12px 18px;
    border-radius: 18px;
    border: 1px solid rgba(15, 23, 42, 0.12);
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04);
    font-weight: 700;
}

.city-chip {
    background: #e0f2fe;
    color: #1d4ed8;
    border-color: rgba(59, 130, 246, 0.18);
}

.dashboard-card {
    background: #ffffff;
    border-radius: 24px;
    border: 1px solid rgba(15, 23, 42, 0.10);
    box-shadow: 0 14px 30px rgba(15, 23, 42, 0.05);
    padding: 28px;
    margin-bottom: 22px;
}

.card-title {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 10px;
}

.card-copy {
    color: #475569;
    line-height: 1.8;
    margin-bottom: 0;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 18px;
    margin-bottom: 24px;
}

.metric-box {
    background: #ffffff;
    border-radius: 20px;
    padding: 22px;
    border: 1px solid rgba(15, 23, 42, 0.10);
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04);
}

.metric-box strong {
    display: block;
    margin-bottom: 12px;
    font-size: 14px;
    color: #334155;
}

.metric-value {
    font-size: 28px;
    font-weight: 700;
    color: #111827;
}

.status-list {
    margin: 16px 0 0;
    padding-left: 18px;
    color: #475569;
}

.status-list li {
    margin-bottom: 10px;
}

.forecast-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;
    margin-top: 18px;
}

.forecast-tile {
    background: #ffffff;
    border-radius: 18px;
    padding: 18px;
    text-align: center;
    border: 1px solid rgba(15, 23, 42, 0.10);
}

.forecast-tile strong {
    display: block;
    margin-bottom: 10px;
    font-size: 14px;
}

.forecast-tile div {
    font-size: 18px;
    font-weight: 700;
    color: #0f172a;
}

.status-panel {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 16px;
    margin-top: 18px;
}

.status-panel div {
    background: #ffffff;
    border-radius: 20px;
    padding: 18px;
    border: 1px solid rgba(15, 23, 42, 0.08);
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
}

.status-panel strong {
    display: block;
    margin-bottom: 10px;
    font-size: 13px;
    color: #475569;
}

.status-panel div div {
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
}

.stButton>button {
    background: linear-gradient(135deg, #0891b2, #0f766e) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 10px 30px rgba(2, 132, 199, 0.24);
}

.stButton>button:hover {
    opacity: 0.95 !important;
}

input, textarea, select {
    border-radius: 14px !important;
}

@media (max-width: 1000px) {
    .metric-grid,
    .forecast-grid,
    .status-panel {
        grid-template-columns: 1fr;
    }
}
</style>
"""


def insert_style():
    st.markdown(STYLE_SHEET, unsafe_allow_html=True)
