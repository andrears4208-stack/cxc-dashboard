import streamlit as st

st.set_page_config(
    page_title="ARES PERU S.A.C. — Dashboard Financiero",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
/* ─── Reset page chrome ─── */
header { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stApp > header { display: none !important; }

/* ─── Card buttons ─── */
div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div.stButton {
    width: 100%;
}
div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div.stButton button {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    min-height: 230px !important;
    padding: 2rem 1.5rem !important;
    border-radius: 16px !important;
    background: #ffffff !important;
    border: 1px solid #e6e9ef !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
    transition: all 0.25s ease !important;
    cursor: pointer !important;
    text-align: center !important;
    line-height: 1.5 !important;
    color: inherit !important;
    font-family: inherit !important;
    font-size: 0.9rem !important;
}
div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div.stButton button:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 12px 28px rgba(0,0,0,0.1) !important;
    border-color: #1f77b4 !important;
    background: #f6faff !important;
}
div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div.stButton button:active {
    transform: translateY(-1px) !important;
    border-color: #155a8a !important;
    background: #eaf2fb !important;
}
div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div.stButton button p {
    margin: 0 !important;
    line-height: 1.4 !important;
}
div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div.stButton button p:first-of-type {
    font-size: 2.8rem !important;
    margin-bottom: 0.3rem !important;
}
div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div.stButton button p:nth-of-type(2) {
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    color: #1a1c23 !important;
}
div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div.stButton button p:nth-of-type(3) {
    font-size: 0.8rem !important;
    color: #6b7280 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

col_logo, col_title = st.columns([1, 7])
with col_logo:
    st.markdown(
        '<div style="font-size:2.8rem; line-height:1;">📊</div>',
        unsafe_allow_html=True,
    )
with col_title:
    st.markdown("### ARES PERU S.A.C.")
    st.markdown(
        '<span style="color:#6b7280; font-size:0.95rem;">Dashboard Financiero Integral</span>',
        unsafe_allow_html=True,
    )

st.markdown("---")

modules = [
    {
        "icon": "💰",
        "title": "CxC",
        "desc": "Cuentas por Cobrar",
        "page": "pages/01_cxc.py",
    },
    {
        "icon": "📄",
        "title": "CxP",
        "desc": "Cuentas por Pagar",
        "page": "pages/02_cxp.py",
    },
    {
        "icon": "📈",
        "title": "Comercial",
        "desc": "Gestión Comercial",
        "page": "pages/03_comercial.py",
    },
    {
        "icon": "🏦",
        "title": "Caja y Bancos",
        "desc": "Caja y Bancos",
        "page": "pages/04_caja_bancos.py",
    },
]

cols = st.columns(4, gap="medium")
for i, mod in enumerate(modules):
    with cols[i]:
        if st.button(f"{mod['icon']}\n\n**{mod['title']}**\n\n{mod['desc']}", key=f"card_{i}", use_container_width=True):
            st.switch_page(mod["page"])

st.markdown("---")
st.caption("Selecciona un módulo para comenzar")
