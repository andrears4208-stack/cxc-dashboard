import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from utils.formatting import fmt_soles, fmt_dolares, fmt_num, fmt_soles_miles, fmt_dolares_miles, fmt_num_miles
from utils.data import process_caja_bancos
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
[data-testid="stSidebar"] .stPageLink a {
    padding: 0.4rem 0.6rem !important;
    border-radius: 8px !important;
    transition: background 0.15s;
    font-size: 0.85rem !important;
}
[data-testid="stSidebar"] .stPageLink a:hover {
    background: #e8ecf1 !important;
}
</style>
""",
    unsafe_allow_html=True,
)


def render_dashboard(df):
    ingresos = df[df["MVTO"] == "INGRESO"]
    egresos = df[df["MVTO"] == "SALIDA"]

    ing_mn = ingresos[ingresos["MONEDA"] == "MN"]["MONTO_MN"].sum()
    ing_me = ingresos[ingresos["MONEDA"] == "ME"]["MONTO_ME"].sum()
    egr_mn = egresos[egresos["MONEDA"] == "MN"]["MONTO_MN"].sum()
    egr_me = egresos[egresos["MONEDA"] == "ME"]["MONTO_ME"].sum()

    cols1 = st.columns(4)
    with cols1[0]:
        st.metric("Ingresos MN (Miles)", fmt_soles_miles(ing_mn))
    with cols1[1]:
        st.metric("Ingresos ME (Miles)", fmt_dolares_miles(ing_me))
    with cols1[2]:
        st.metric("Egresos MN (Miles)", fmt_soles_miles(abs(egr_mn)))
    with cols1[3]:
        st.metric("Egresos ME (Miles)", fmt_dolares_miles(abs(egr_me)))

    cols2 = st.columns(3)
    with cols2[0]:
        st.metric("Total Movimientos", fmt_num(len(df)))
    with cols2[1]:
        st.metric("Total Ingresos", fmt_num(len(ingresos)))
    with cols2[2]:
        st.metric("Total Egresos", fmt_num(len(egresos)))

    st.markdown("---")
    st.subheader("Evolucion de Ingresos y Egresos")

    periodo_opcion = st.radio(
        "Periodicidad",
        options=["Mensual", "Semanal"],
        horizontal=True,
        key="periodo_cb",
    )

    df_linea = df.copy()
    if periodo_opcion == "Mensual":
        df_linea["PERIODO"] = df_linea["PERIODO_MES"]
    else:
        wk = df_linea["FECHA"].dt.isocalendar().week.astype(int)
        yr = df_linea["FECHA"].dt.year.astype(str)
        df_linea["PERIODO"] = yr + "-S" + wk.astype(str).str.zfill(2)

    flow = (
        df_linea.groupby(["PERIODO", "MONEDA", "MVTO"])["MONTO_REAL"]
        .sum()
        .reset_index()
    )

    flow_pivot = flow.pivot_table(
        index="PERIODO",
        columns=["MONEDA", "MVTO"],
        values="MONTO_REAL",
        fill_value=0,
    )
    flow_pivot.columns = [f"{c[0]}_{c[1]}" for c in flow_pivot.columns]
    flow_pivot = flow_pivot.reset_index()

    for col in ["MN_INGRESO", "MN_SALIDA", "ME_INGRESO", "ME_SALIDA"]:
        if col not in flow_pivot.columns:
            flow_pivot[col] = 0.0

    flow_pivot = flow_pivot.sort_values("PERIODO")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        name="Ingresos MN (S/.)",
        x=flow_pivot["PERIODO"],
        y=flow_pivot["MN_INGRESO"],
        mode="lines+markers",
        marker_color="#1f77b4",
        line=dict(width=3),
        yaxis="y",
    ))
    fig.add_trace(go.Scatter(
        name="Egresos MN (S/.)",
        x=flow_pivot["PERIODO"],
        y=flow_pivot["MN_SALIDA"].abs(),
        mode="lines+markers",
        marker_color="#ff7f0e",
        line=dict(width=3, dash="dash"),
        yaxis="y",
    ))
    fig.add_trace(go.Scatter(
        name="Ingresos ME (US$)",
        x=flow_pivot["PERIODO"],
        y=flow_pivot["ME_INGRESO"],
        mode="lines+markers",
        marker_color="#2ca02c",
        line=dict(width=3),
        yaxis="y2",
    ))
    fig.add_trace(go.Scatter(
        name="Egresos ME (US$)",
        x=flow_pivot["PERIODO"],
        y=flow_pivot["ME_SALIDA"].abs(),
        mode="lines+markers",
        marker_color="#d62728",
        line=dict(width=3, dash="dash"),
        yaxis="y2",
    ))

    fig.update_layout(
        height=450,
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", y=-0.25),
        xaxis_title="Periodo",
        yaxis=dict(
            title="Soles (S/.)",
            side="left",
            showgrid=True,
        ),
        yaxis2=dict(
            title="Dolares (US$)",
            side="right",
            overlaying="y",
            showgrid=False,
        ),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Ingresos por Banco")

    ingresos_df = df[df["MVTO"] == "INGRESO"]
    ing_mn_bank = (
        ingresos_df[ingresos_df["MONEDA"] == "MN"]
        .groupby("BANCO")["MONTO_MN"]
        .sum()
        .sort_values(ascending=True)
        .reset_index()
    )
    ing_me_bank = (
        ingresos_df[ingresos_df["MONEDA"] == "ME"]
        .groupby("BANCO")["MONTO_ME"]
        .sum()
        .sort_values(ascending=True)
        .reset_index()
    )

    col_b1, col_b2 = st.columns(2)

    with col_b1:
        if not ing_mn_bank.empty:
            ing_mn_bank["texto"] = ing_mn_bank["MONTO_MN"].apply(fmt_num_miles)
            fig_mn = px.bar(
                ing_mn_bank,
                x="MONTO_MN",
                y="BANCO",
                orientation="h",
                text="texto",
                color="MONTO_MN",
                color_continuous_scale="Blues",
                height=350,
            )
            fig_mn.update_layout(
                xaxis_title="Miles de Soles",
                yaxis_title="",
                margin=dict(l=0, r=0, t=10, b=0),
            )
            fig_mn.update_traces(textposition="auto")
            st.plotly_chart(fig_mn, use_container_width=True)
        else:
            st.info("Sin datos de ingresos MN")

    with col_b2:
        if not ing_me_bank.empty:
            ing_me_bank["texto"] = ing_me_bank["MONTO_ME"].apply(fmt_num_miles)
            fig_me = px.bar(
                ing_me_bank,
                x="MONTO_ME",
                y="BANCO",
                orientation="h",
                text="texto",
                color="MONTO_ME",
                color_continuous_scale="Greens",
                height=350,
            )
            fig_me.update_layout(
                xaxis_title="Miles de Dolares",
                yaxis_title="",
                margin=dict(l=0, r=0, t=10, b=0),
            )
            fig_me.update_traces(textposition="auto")
            st.plotly_chart(fig_me, use_container_width=True)
        else:
            st.info("Sin datos de ingresos ME")

    st.markdown("---")
    st.subheader("Distribucion por Tipo de Movimiento")
    tipo_agg = df["MVTO"].value_counts().reset_index()
    tipo_agg.columns = ["MVTO", "Cantidad"]
    tipo_agg["MVTO"] = tipo_agg["MVTO"].map({"INGRESO": "Ingresos", "SALIDA": "Egresos"})
    fig2 = go.Figure(data=[go.Pie(
        labels=tipo_agg["MVTO"],
        values=tipo_agg["Cantidad"],
        hole=0.4,
        marker_colors=["#1f77b4", "#ff7f0e"],
    )])
    fig2.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", y=-0.2),
    )
    st.plotly_chart(fig2, use_container_width=True)


def render_table(df):
    st.subheader("Detalle de Movimientos de Caja y Bancos")

    cols = [
        "BANCO", "FECHA", "MVTO", "CODCONCEPTO", "TDOC", "NRODOCUM",
        "REFERENCIA", "CB_N_MTOMN", "CB_N_MTOME", "DESCCTAC", "ANEXO",
    ]

    available = [c for c in cols if c in df.columns]
    display_df = df[available].copy()

    display_df["FECHA"] = display_df["FECHA"].dt.strftime("%d/%m/%Y")
    display_df["CB_N_MTOMN"] = display_df["CB_N_MTOMN"].apply(fmt_soles)
    display_df["CB_N_MTOME"] = display_df["CB_N_MTOME"].apply(fmt_dolares)
    display_df["MVTO"] = display_df["MVTO"].map({"INGRESO": "Ingreso", "SALIDA": "Egreso"})

    col_map = {
        "BANCO": "Banco",
        "FECHA": "Fecha",
        "MVTO": "Tipo",
        "CODCONCEPTO": "Cod. Concepto",
        "TDOC": "T.Doc",
        "NRODOCUM": "Documento",
        "REFERENCIA": "Referencia",
        "CB_N_MTOMN": "Monto MN",
        "CB_N_MTOME": "Monto ME",
        "DESCCTAC": "Descripcion Cuenta",
        "ANEXO": "Anexo",
    }
    display_df.columns = [col_map.get(c, c) for c in available]

    search = st.text_input(
        "Buscar por referencia, documento, banco o cuenta",
        placeholder="Escribe para filtrar...",
    )
    if search:
        mask = pd.Series(False, index=display_df.index)
        for col in display_df.columns:
            if display_df[col].dtype == "object":
                mask |= display_df[col].str.contains(search, case=False, na=False)
        display_df = display_df[mask]

    st.dataframe(display_df, hide_index=True, use_container_width=True, height=500)

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="Descargar CSV",
        data=csv,
        file_name=f"caja_bancos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )


def main():
    render_sidebar("Caja y Bancos")

    if "df_cb" not in st.session_state:
        st.session_state.df_cb = None
    if "file_key_cb" not in st.session_state:
        st.session_state.file_key_cb = None
    if "file_name_cb" not in st.session_state:
        st.session_state.file_name_cb = None
    if "loaded_at_cb" not in st.session_state:
        st.session_state.loaded_at_cb = None

    with st.sidebar:
        st.markdown("**📁 Datos**")
        uploaded_file = st.file_uploader(
            "Cargar archivo Excel",
            type=["xlsx"],
            help="Sube tu archivo Excel de Caja y Bancos",
            key="cb_uploader",
        )

        if uploaded_file:
            file_key = f"{uploaded_file.name}_{uploaded_file.size}"
            if st.session_state.file_key_cb != file_key:
                with st.spinner("Procesando datos..."):
                    try:
                        st.session_state.df_cb = process_caja_bancos(uploaded_file)
                        st.session_state.file_key_cb = file_key
                        st.session_state.file_name_cb = uploaded_file.name
                        st.session_state.loaded_at_cb = datetime.now()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al procesar el archivo: {e}")
                        st.stop()

        df = st.session_state.df_cb

        if df is None:
            st.info(
                "Sube un archivo Excel de Caja y Bancos para comenzar.\n\n"
                "**Formato esperado:** columnas CODBCO, MVTO, FECHA, "
                "CB_N_MTOMN, CB_N_MTOME, BANCO, DESCCTAC, etc."
            )
            st.stop()

        st.caption(
            f"{len(df)} registros  ·  "
            f"{st.session_state.file_name_cb or ''}  ·  "
            f"{st.session_state.loaded_at_cb.strftime('%d/%m/%Y %H:%M') if st.session_state.loaded_at_cb else ''}"
        )

        st.divider()
        st.markdown("**🔍 Filtros**")

        all_banks = sorted(df["BANCO"].unique())
        selected_bank = st.selectbox(
            "Banco", options=["Todos"] + all_banks
        )

        selected_mvto = st.selectbox(
            "Tipo Movimiento",
            options=["Todos", "INGRESO", "SALIDA"],
        )

        selected_currency = st.selectbox(
            "Moneda",
            options=["Todas", "MN (Soles)", "ME (Dolares)"],
        )

        has_anexo = "ANEXO" in df.columns
        if has_anexo:
            all_anexos = sorted(df["ANEXO"].dropna().unique())
            selected_anexo = st.selectbox(
                "Anexo", options=["Todos"] + all_anexos
            )
        else:
            selected_anexo = "Todos"

        min_date = df["FECHA"].min().date()
        max_date = df["FECHA"].max().date()
        st.date_input(
            "Rango de fechas",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="date_range_cb",
        )

    currency_map = {"MN (Soles)": "MN", "ME (Dolares)": "ME"}
    filtered = df.copy()

    if selected_bank != "Todos":
        filtered = filtered[filtered["BANCO"] == selected_bank]
    if selected_mvto != "Todos":
        filtered = filtered[filtered["MVTO"] == selected_mvto]
    if selected_currency != "Todas":
        filtered = filtered[filtered["MONEDA"] == currency_map[selected_currency]]
    if has_anexo and selected_anexo != "Todos":
        filtered = filtered[filtered["ANEXO"] == selected_anexo]
    date_range = st.session_state.get("date_range_cb", (min_date, max_date))
    if len(date_range) == 2:
        d_start, d_end = date_range
        filtered = filtered[
            (filtered["FECHA"].dt.date >= d_start)
            & (filtered["FECHA"].dt.date <= d_end)
        ]

    st.markdown("## 🏦 Caja y Bancos")
    tab1, tab2 = st.tabs(["Dashboard", "Tabla Detallada"])

    with tab1:
        render_dashboard(filtered)
    with tab2:
        render_table(filtered)

    st.caption(
        f"{len(filtered)} registros de {len(df)} totales  ·  "
        f"Actualizado: {datetime.now().strftime('%Y%m%d %H:%M')}"
    )


if __name__ == "__main__":
    main()
