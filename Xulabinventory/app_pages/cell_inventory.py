import os
import streamlit as st
import pandas as pd
import json
import re
import streamlit.components.v1 as components

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "cell_template.html")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1Ezga1klNnOzxdRa-8rgWEQhAqDztvxok_qHcyuqu0MY/export?format=csv"


@st.cache_data(ttl=60)
def load_data():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    # row 0 is a merged title row ("ATCC Cell Line Order List"); the real header is row 1
    return pd.read_csv(SHEET_URL, storage_options=headers, skiprows=1).fillna("")


try:
    df = load_data()

    df.columns = [str(c).strip().lower() for c in df.columns]
    rename_map = {
        "#": "num",
        "cell line": "name",
        "atcc cat. no.": "cat",
        "atcc product link": "link_raw",
        "organism / background": "organism",
        "tissue / disease": "tissue",
        "key feature or marker": "feature",
        "recommended base medium": "medium",
        "role in project": "role",
        "unit price (usd)": "price",
        "line total (usd)": "total",
    }
    df = df.rename(columns=rename_map)

    required_cols = ["num", "program", "name", "cat", "organism", "tissue",
                      "feature", "medium", "role", "qty", "price", "total"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""

    # the sheet's summary/subtotal rows have a blank "#" column - drop them
    df["num"] = pd.to_numeric(df["num"], errors="coerce")
    df = df[df["num"].notna()].copy()
    df["num"] = df["num"].astype(int)
    df["qty"] = pd.to_numeric(df["qty"], errors="coerce").fillna(0).astype(int)
    df = df.astype(str)

    records = df.to_dict('records')
    for r in records:
        cat = r.get('cat', '').strip()
        r['link'] = f"https://www.atcc.org/products/{cat}" if cat else ""

    js_data = json.dumps(records)

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html_template = f.read()

    final_html = html_template.replace('{DATA_PLACEHOLDER}', js_data)

    final_html = re.sub(
        r'showing<strong id="tally">\d+</strong>of \d+',
        f'showing<strong id="tally">{len(df)}</strong>of {len(df)}',
        final_html
    )

    components.html(final_html, height=1000, scrolling=False)

except Exception as e:
    st.error(f"An error occurred while loading the application: {e}")
