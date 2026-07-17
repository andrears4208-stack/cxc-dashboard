import streamlit as st

from components.sidebar import render as render_sidebar

st.set_page_config(
    page_title="Comercial — ARES PERU S.A.C.",
    page_icon="📈",
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

render_sidebar("Gestión Comercial")

with st.sidebar:
    st.info("Sube un archivo Excel de Gestión Comercial para comenzar.")

st.markdown("## 📈 Gestión Comercial")
st.markdown("---")

col1, col2 = st.columns([2, 1])
with col1:
    st.info(
        "🚧 **Módulo en construcción**  \n\n"
        "Este módulo estará disponible próximamente.  \n\n"
        "**Funcionalidades planeadas:**  \n"
        "· Ventas por vendedor y cliente  \n"
        "· Cumplimiento de metas  \n"
        "· Comisiones  \n"
        "· Productos más vendidos  \n"
        "· Tendencia de ventas mensual  \n\n"
        "Cuando tengas el Excel con la estructura de datos comerciales, "
        "lo integramos rápidamente."
    )
with col2:
    st.markdown(
        '<div style="font-size:6rem; text-align:center; opacity:0.3;">📈</div>',
        unsafe_allow_html=True,
    )
