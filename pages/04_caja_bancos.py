import streamlit as st

from components.sidebar import render as render_sidebar

st.set_page_config(
    page_title="Caja y Bancos — ARES PERU S.A.C.",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
[data-testid="stSidebarNav"] { display: none; }
[data-testid="stSidebar"] { background: #f7f8fa; }
</style>
""",
    unsafe_allow_html=True,
)

render_sidebar("Caja y Bancos")

with st.sidebar:
    st.info("Sube un archivo Excel de Caja y Bancos para comenzar.")

st.markdown("## 🏦 Caja y Bancos")
st.markdown("---")

col1, col2 = st.columns([2, 1])
with col1:
    st.info(
        "🚧 **Módulo en construcción**  \n\n"
        "Este módulo estará disponible próximamente.  \n\n"
        "**Funcionalidades planeadas:**  \n"
        "· Saldos por cuenta y banco  \n"
        "· Movimientos de tesorería  \n"
        "· Conciliación bancaria  \n"
        "· Flujo de caja  \n"
        "· Proyecciones  \n\n"
        "Cuando tengas el Excel con la estructura de datos de caja y bancos, "
        "lo integramos rápidamente."
    )
with col2:
    st.markdown(
        '<div style="font-size:6rem; text-align:center; opacity:0.3;">🏦</div>',
        unsafe_allow_html=True,
    )
