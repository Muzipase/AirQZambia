"""Zambia Air Quality Monitor — Streamlit command center entry point.

Uses st.navigation to power a clean, grouped sidebar rail instead of the
old mixed radio + auto-page navigation. Each screen lives under app/views/.
"""

import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from style_assets import _block, insert_style, topbar
from state import DATA_SOURCES, SOURCE_API_MAP, fetch_api_status, format_model_names

st.set_page_config(
    page_title="AirQ Zambia · Command Center",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

insert_style()

# ---- Global compact command header: brand + system status ----------------
status = fetch_api_status()
online = bool(status)
topbar(
    online=online,
    updated=datetime.now().strftime("%H:%M:%S"),
    sources="Open-Meteo + OpenAQ",
)

# ---- Sidebar brand --------------------------------------------------------
st.sidebar.markdown(
    _block(
        """
        <div class='side-brand'>
          <div class='side-logo'>🌿</div>
          <div>
            <div class='mark'>AIR Q ZAMBIA</div>
            <div class='sub'>Air Quality Intelligence</div>
          </div>
        </div>
        """
    ),
    unsafe_allow_html=True,
)

from views import evaluation, explainability, history, overview, predictions, progress, system  # noqa: E402

NAV = {
    "Situation": [
        st.Page(overview.render, title="Command Center", icon="🌿",
                url_path="overview", default=True),
    ],
    "Decision Support": [
        st.Page(predictions.render, title="Forecast & Scenarios", icon="🎯",
                url_path="predictions"),
        st.Page(history.render, title="Historical Data", icon="🗓️",
                url_path="history"),
        st.Page(evaluation.render, title="Model Performance", icon="📊",
                url_path="evaluation"),
        st.Page(explainability.render, title="Explainability", icon="🧠",
                url_path="explainability"),
    ],
    "Platform": [
        st.Page(progress.render, title="Pipeline Progress", icon="⏱️",
                url_path="pipeline-progress"),
        st.Page(system.render, title="System & Testing", icon="🛠️",
                url_path="system"),
    ],
}

pg = st.navigation(NAV)
pg.run()

# ---- Sidebar system status block ------------------------------------------
models = format_model_names(status)
st.sidebar.markdown(
    _block(
        f"""
        <div class='side-status'>
          <div class='h'>System status</div>
          <div class='row'>
            <span>Backend</span>
            <span><span class='dot {"on pulse" if online else "off"}'></span>
            <strong>{"Online" if online else "Offline"}</strong></span>
          </div>
          <div class='row'>
            <span>Data source</span>
            <span><span class='dot {"on" if online else "off"}'></span>
            <strong>{"Connected" if online else "Unavailable"}</strong></span>
          </div>
          <div class='row'>
            <span>Models</span>
            <span style='text-align:right; max-width:9rem;'>{models}
            {' · loaded' if models != "No model loaded" else ''}</span>
          </div>
        </div>
        """
    ),
    unsafe_allow_html=True,
)

with st.sidebar.expander("Data source", expanded=False):
    source_label = st.selectbox(
        "Stream feeds", DATA_SOURCES, index=0, key="data_source"
    )
    api_source = SOURCE_API_MAP[source_label]

    def _clear_feed():
        """Drop the cached API-status payload so the sidebar refresh re-probes."""
        fetch_api_status.clear()

    if st.button("Refresh status", key="refresh_status"):
        _clear_feed()
        st.rerun()

st.sidebar.markdown(
    _block(
        """
        <div class='side-foot'>
          Data from Open-Meteo &amp; OpenAQ<br/>
          Refreshes every 2 minutes · Classified by tuned hybrid SVM.
        </div>
        """
    ),
    unsafe_allow_html=True,
)

if __name__ == "__main__":
    pass