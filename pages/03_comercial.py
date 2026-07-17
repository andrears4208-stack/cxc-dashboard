import streamlit as st

st.set_page_config(
    page_title="Comercial - Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📈 Gestión Comercial")
st.markdown("---")

with st.sidebar:
    st.page_link("app.py", label="⬅ Volver al inicio", icon="🏠")
    st.markdown("---")

st.info(
    "🚧 **Módulo en construcción**  \n\n"
    "Este módulo de **Gestión Comercial** estará disponible próximamente.  \n\n"
    "Funcionalidades planeadas:  \n"
    "- Ventas por vendedor y cliente  \n"
    "- Cumplimiento de metas  \n"
    "- Comisiones  \n"
    "- Productos más vendidos  \n"
    "- Tendencia de ventas mensual  \n\n"
    "Cuando tengas el Excel con la estructura de datos comerciales, "
    "lo integramos rápidamente."
)
