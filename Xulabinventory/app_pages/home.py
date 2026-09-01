import os
import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "home_template.html")

try:
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html = f.read()
    components.html(html, height=900, scrolling=False)
except Exception as e:
    st.error(f"An error occurred while loading the home page: {e}")
