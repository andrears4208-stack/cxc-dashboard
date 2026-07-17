import streamlit as st


def render(title="Dashboard Financiero"):
    with st.sidebar:
        st.markdown("### ARES PERU S.A.C.")
        st.markdown(
            f'<span style="color:#6b7280; font-size:0.8rem;">{title}</span>',
            unsafe_allow_html=True,
        )
        st.divider()

        st.page_link("app.py", label="Inicio", icon="🏠", use_container_width=True)
        st.page_link(
            "pages/01_cxc.py",
            label="CxC — Cuentas por Cobrar",
            icon="💰",
            use_container_width=True,
        )
        st.page_link(
            "pages/02_cxp.py",
            label="CxP — Cuentas por Pagar",
            icon="📄",
            use_container_width=True,
        )
        st.page_link(
            "pages/03_comercial.py",
            label="Comercial",
            icon="📈",
            use_container_width=True,
            disabled=True,
        )
        st.page_link(
            "pages/04_caja_bancos.py",
            label="Caja y Bancos",
            icon="🏦",
            use_container_width=True,
            disabled=True,
        )
        st.divider()
