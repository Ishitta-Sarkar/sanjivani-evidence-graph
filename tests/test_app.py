"""The Streamlit entry point renders every page and scores a real path."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"

PAGES = [
    "Home",
    "Search Entity",
    "Drug Recommendations",
    "Path Explorer",
    "Knowledge Graph",
    "Graph Analytics",
    "About",
]


def test_every_page_renders_and_scores_a_path():
    app = AppTest.from_file(str(APP), default_timeout=60)
    app.run()

    for page in PAGES:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception, page

    app.sidebar.radio[0].set_value("Path Explorer").run()
    app.selectbox(key="path_start_entity").set_value("Metformin")
    app.selectbox(key="path_end_entity").set_value("Type 2 Diabetes")
    app.button[0].click().run()
    assert not app.exception

    metrics = {metric.label: metric.value for metric in app.metric}
    assert metrics["Confidence Score"] == "15/15"
    assert metrics["Confidence Level"] == "🟢 High"
    assert metrics["Path Length"] == "3"

    app.sidebar.radio[0].set_value("Drug Recommendations").run()
    app.selectbox[0].set_value("Breast Cancer").run()
    assert not app.exception
    shown = " ".join(block.value for block in app.markdown)
    assert "5/5 (High)" in shown
    assert any(block.value == "💊 Olaparib" for block in app.subheader)
