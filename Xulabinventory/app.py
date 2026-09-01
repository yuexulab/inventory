import streamlit as st

st.set_page_config(page_title="Xulab Inventory", layout="wide")

st.markdown("""
<style>
.block-container {padding: 0 !important; max-width: 100% !important;}
iframe {display: block; width: 100%;}
</style>
""", unsafe_allow_html=True)

pages = {
    "Xulab Inventory": [
        st.Page("app_pages/home.py", title="Home", icon="🏠", default=True),
        st.Page("app_pages/chemical_inventory.py", title="Chemical Inventory", icon="🧪"),
        st.Page("app_pages/cell_inventory.py", title="Cell Inventory", icon="🧫"),
    ]
}

pg = st.navigation(pages)
pg.run()
