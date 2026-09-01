import os
import streamlit as st
import pandas as pd
import json
import re
import streamlit.components.v1 as components
from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "chemical_template.html")


@st.cache_data(ttl=60)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1Vw0FgVxmjveS0k6KJYtrh0G5pVIMIqE_6unkUcSXNIg/export?format=csv&gid=1293947143"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    return pd.read_csv(sheet_url, storage_options=headers).fillna("")


def smiles_to_svg(smiles):
    if not smiles or str(smiles).strip() == "":
        return "<svg viewBox='0 0 250 160'></svg>"
    try:
        mol = Chem.MolFromSmiles(str(smiles).strip())
        if mol:
            drawer = rdMolDraw2D.MolDraw2DSVG(250, 160)
            drawer.drawOptions().clearBackground = False
            drawer.DrawMolecule(mol)
            drawer.FinishDrawing()
            svg = drawer.GetDrawingText()
            return svg[svg.find("<svg"):]
    except Exception:
        pass
    return "<svg viewBox='0 0 250 160'></svg>"


try:
    df = load_data()

    df.columns = [str(c).strip().lower() for c in df.columns]
    rename_map = {"quantity": "qty", "cat#": "cat", "car#": "cat", "cas#": "cas"}
    df = df.rename(columns=rename_map)

    required_cols = ["name", "cas", "qty", "vendor", "position", "cat", "box", "smiles"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""

    df = df.astype(str)

    records = df.to_dict('records')
    for r in records:
        r['svg'] = smiles_to_svg(r.get('smiles', ''))
        if not r['box'] or r['box'].lower() == 'nan':
            r['box'] = 'Unknown Box'

    js_data = json.dumps(records)

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html_template = f.read()

    final_html = re.sub(
        r'const DATA\s*=\s*\[.*?\];',
        lambda _: f'const DATA = {js_data};',
        html_template,
        flags=re.DOTALL
    )
    final_html = final_html.replace('const DATA = {DATA_PLACEHOLDER};', f'const DATA = {js_data};')
    final_html = final_html.replace('{DATA_PLACEHOLDER}', js_data)

    final_html = re.sub(
        r'showing<strong id="tally">\d+</strong>of \d+',
        f'showing<strong id="tally">{len(df)}</strong>of {len(df)}',
        final_html
    )

    components.html(final_html, height=1000, scrolling=False)

except Exception as e:
    st.error(f"An error occurred while loading the application: {e}")
