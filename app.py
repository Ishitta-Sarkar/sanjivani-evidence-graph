"""SANJIVANI Evidence Graph — Streamlit entry point.

Page bodies live in ``src/ui``. This file only sets up the window and
dispatches the sidebar selection.
"""

import streamlit as st

st.set_page_config(
    page_title="SANJIVANI Evidence Graph",
    page_icon="🧬",
    layout="wide",
)

from src.ui.about import render as render_about
from src.ui.analytics import render as render_analytics
from src.ui.drugs import render as render_drugs
from src.ui.graph import render as render_graph
from src.ui.home import render as render_home
from src.ui.paths import render as render_paths
from src.ui.search import render as render_search
from src.version import __version__

PAGES = {
    "Home": render_home,
    "Search Entity": render_search,
    "Drug Recommendations": render_drugs,
    "Path Explorer": render_paths,
    "Knowledge Graph": render_graph,
    "Graph Analytics": render_analytics,
    "About": render_about,
}

st.sidebar.title("🧬 SANJIVANI")

page = st.sidebar.radio(
    "Navigate",
    list(PAGES),
)

st.sidebar.divider()

st.sidebar.caption(
    "Explainable biomedical evidence-graph prototype"
)

PAGES[page]()

st.caption(
    f"🧬 SANJIVANI v{__version__} | "
    "Explainable Biomedical Knowledge Graph Platform"
)

st.caption("Developed by Ishitta Sarkar")

st.caption("© 2026 Ishitta Sarkar. Released under the MIT License.")
