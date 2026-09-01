import os
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "home_template.html")

CHEM_CSV = "https://docs.google.com/spreadsheets/d/1Vw0FgVxmjveS0k6KJYtrh0G5pVIMIqE_6unkUcSXNIg/export?format=csv&gid=1293947143"
CELL_CSV = "https://docs.google.com/spreadsheets/d/1Ezga1klNnOzxdRa-8rgWEQhAqDztvxok_qHcyuqu0MY/export?format=csv"
_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


@st.cache_data(ttl=60, show_spinner=False)
def _counts():
    """(chemical_rows, cell_rows) from the live sheets; None for either on failure."""
    chem = cell = None
    try:
        chem = len(pd.read_csv(CHEM_CSV, storage_options=_HEADERS))
    except Exception:
        pass
    try:
        df = pd.read_csv(CELL_CSV, storage_options=_HEADERS, skiprows=1)
        df.columns = [str(c).strip().lower() for c in df.columns]
        # real records have a numeric "#" — summary/subtotal rows don't
        cell = int(pd.to_numeric(df.get("#"), errors="coerce").notna().sum())
    except Exception:
        pass
    return chem, cell


def _fill(html, prefix, value):
    if value is None:
        html = html.replace("{{%s_COUNT}}" % prefix, "open")
        html = html.replace("{{%s_COUNT_UNIT}}" % prefix, "&rarr;")
        html = html.replace("{{%s_COUNT_CLASS}}" % prefix, "empty")
    else:
        html = html.replace("{{%s_COUNT}}" % prefix, f"{value:,}")
        html = html.replace("{{%s_COUNT_UNIT}}" % prefix, "in stock")
        html = html.replace("{{%s_COUNT_CLASS}}" % prefix, "")
    return html


try:
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    chem, cell = _counts()
    html = _fill(html, "CHEM", chem)
    html = _fill(html, "CELL", cell)

    components.html(html, height=900, scrolling=False)
except Exception as e:
    st.error(f"An error occurred while loading the home page: {e}")
