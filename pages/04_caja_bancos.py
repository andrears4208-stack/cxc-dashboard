import streamlit as st

st.set_page_config(
    page_title="Caja y Bancos - Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏦 Caja y Bancos")
st.markdown("---")

with st.sidebar:
    st.page_link("app.py", label="⬅ Volver al inicio", icon="🏠")
    st.markdown("---")

st.info(
    "🚧 **Módulo en construcción**  \n\n"
    "Este módulo de **Caja y Bancos** estará disponible próximamente.  \n\n"
    "Funcionalidades planeadas:  \n"
    "- Saldos por cuenta y banco  \n"
    "- Movimientos de tesorería  \n"
    "- Conciliación bancaria  \n"
    "- Flujo de caja  \n"
    "- Proyecciones  \n\n"
    "Cuando tengas el Excel con la estructura de datos de caja y bancos, "
    "lo integramos rápidamente."
)
