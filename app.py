import streamlit as st

st.set_page_config(
    page_title="Dashboard Financiero",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .card-link {
        text-decoration: none !important;
        display: block;
    }
    .card-link:hover {
        text-decoration: none;
    }
    .card-link button, .card-link a {
        text-decoration: none !important;
    }
    .card-box {
        padding: 2rem 1.5rem;
        border-radius: 16px;
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        text-align: center;
        transition: all 0.2s ease;
        margin-bottom: 1rem;
        cursor: pointer;
        height: 200px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .card-box:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        border-color: #1f77b4;
        background: #f0f4ff;
    }
    .card-icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1f77b4;
        margin-bottom: 0.25rem;
    }
    .card-desc {
        font-size: 0.85rem;
        color: #6c757d;
        line-height: 1.4;
    }
    .stPageLink {
        text-decoration: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 Dashboard Financiero Integral")
st.markdown("Selecciona un módulo para comenzar:")
st.markdown("---")

modules = [
    {
        "icon": "💰",
        "title": "CxC",
        "desc": "Cuentas por Cobrar<br>Clientes, facturación y cobranzas",
        "page": "pages/01_cxc.py",
    },
    {
        "icon": "📄",
        "title": "CxP",
        "desc": "Cuentas por Pagar<br>Proveedores, vencimientos y pagos",
        "page": "pages/02_cxp.py",
    },
    {
        "icon": "📈",
        "title": "Comercial",
        "desc": "Gestión Comercial<br>Ventas, metas y comisiones",
        "page": "pages/03_comercial.py",
    },
    {
        "icon": "🏦",
        "title": "Caja y Bancos",
        "desc": "Tesorería<br>Movimientos, saldos y conciliación",
        "page": "pages/04_caja_bancos.py",
    },
]

cols = st.columns(4)
for i, mod in enumerate(modules):
    with cols[i]:
        st.markdown(
            f'<div class="card-box">'
            f'<div class="card-icon">{mod["icon"]}</div>'
            f'<div class="card-title">{mod["title"]}</div>'
            f'<div class="card-desc">{mod["desc"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.page_link(mod["page"], label=f"Ingresar", use_container_width=True)

st.markdown("---")
st.caption("Carga tu archivo Excel en cada módulo para visualizar los datos.")
