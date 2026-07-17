import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from utils.formatting import fmt_soles, fmt_dolares, fmt_num, fmt_soles_miles, fmt_dolares_miles, fmt_num_miles
from utils.data import process_cxp
from components.sidebar import render as render_sidebar

st.set_page_config(
    page_title="CxP — ARES PERU S.A.C.",
    page_icon="📄",
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
    total_mn = df[df["MONEDA"] == "MN"]["SALDO_NETO"].sum()
    total_me = df[df["MONEDA"] == "ME"]["SALDO_NETO"].sum()
    total_soles = df["SALDO_NETO_SOLES"].sum()
    proveedores_deuda = (
        df.groupby("PROVEEDOR")["SALDO_NETO_SOLES"].sum().gt(0).sum()
    )
    num_docs = len(df)

    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        st.metric("Total CxP MN (Miles)", fmt_soles_miles(total_mn))
    with kpi_cols[1]:
        st.metric("Total CxP ME (Miles)", fmt_dolares_miles(total_me))
    with kpi_cols[2]:
        st.metric("Proveedores con Deuda", fmt_num(proveedores_deuda))
    with kpi_cols[3]:
        st.metric("Total Documentos", fmt_num(num_docs))
    st.metric(
        "Saldo Total (Miles de Soles)",
        fmt_soles_miles(total_soles),
    )

    has_gasto = "GASTO" in df.columns
    if has_gasto:
        st.markdown("---")
        st.subheader("Resumen por Categoría de Gasto")
        resumen = {}
        for gasto in sorted(df["GASTO"].unique()):
            d = df[df["GASTO"] == gasto]
            resumen[gasto] = {
                "MN": d[d["MONEDA"] == "MN"]["SALDO_NETO"].sum(),
                "ME": d[d["MONEDA"] == "ME"]["SALDO_NETO"].sum(),
                "Proveedores": (
                    d.groupby("PROVEEDOR")["SALDO_NETO_SOLES"].sum() > 0
                ).sum(),
                "Neto": d["SALDO_NETO_SOLES"].sum(),
            }
        row_data = []
        labels = {
            "MN": "Total CxP MN",
            "ME": "Total CxP ME",
            "Proveedores": "Proveedores con Deuda",
            "Neto": "Saldo Neto",
        }
        formatters = {
            "MN": fmt_soles_miles,
            "ME": fmt_dolares_miles,
            "Proveedores": fmt_num,
            "Neto": fmt_soles_miles,
        }
        for key, label in labels.items():
            entry = {"Métrica": label}
            for gasto in sorted(df["GASTO"].unique()):
                entry[gasto[:25]] = formatters[key](resumen[gasto][key])
            row_data.append(entry)
        st.dataframe(
            pd.DataFrame(row_data),
            hide_index=True,
            use_container_width=True,
        )

    st.markdown("---")
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Cartera por Proveedor")
        prov_agg = (
            df.groupby("PROVEEDOR")["SALDO_NETO_SOLES"]
            .sum()
            .sort_values(ascending=True)
            .tail(20)
            .reset_index()
        )
        prov_agg["texto"] = prov_agg["SALDO_NETO_SOLES"].apply(fmt_num_miles)
        fig = px.bar(
            prov_agg,
            x="SALDO_NETO_SOLES",
            y="PROVEEDOR",
            orientation="h",
            text="texto",
            color="SALDO_NETO_SOLES",
            color_continuous_scale="Oranges",
            height=500,
        )
        fig.update_layout(
            xaxis_title="Miles de Soles",
            yaxis_title="",
            margin=dict(l=0, r=0, t=10, b=0),
        )
        fig.update_traces(textposition="auto")
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Distribucion por Moneda")
        curr_agg = df.groupby("MONEDA")["SALDO_NETO_SOLES"].sum().reset_index()
        curr_agg["LABEL"] = curr_agg["MONEDA"].map(
            {"MN": "Soles (MN)", "ME": "Dolares (ME)"}
        )
        fig = px.pie(
            curr_agg,
            values="SALDO_NETO_SOLES",
            names="LABEL",
            color="LABEL",
            color_discrete_map={"Soles (MN)": "#1f77b4", "Dolares (ME)": "#ff7f0e"},
            hole=0.4,
            height=400,
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=-0.1)
        )
        st.plotly_chart(fig, use_container_width=True)

    col_left2, col_right2 = st.columns(2)

    with col_left2:
        st.subheader("Antiguedad de Deuda")
        aging_order = [
            "No vencido",
            "1-30 dias",
            "31-60 dias",
            "61-90 dias",
            "90+ dias",
        ]
        aging_agg = (
            df.groupby("RANGO_VENCIMIENTO", observed=True)["SALDO_NETO_SOLES"]
            .sum()
            .reset_index()
        )
        aging_agg["texto"] = aging_agg["SALDO_NETO_SOLES"].apply(fmt_num_miles)
        fig = px.bar(
            aging_agg,
            x="RANGO_VENCIMIENTO",
            y="SALDO_NETO_SOLES",
            category_orders={"RANGO_VENCIMIENTO": aging_order},
            color="SALDO_NETO_SOLES",
            color_continuous_scale="Reds",
            text="texto",
            height=400,
        )
        fig.update_layout(
            xaxis_title="Rango",
            yaxis_title="Miles de Soles",
            margin=dict(l=0, r=0, t=10, b=0),
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with col_right2:
        st.subheader("Top 10 Acreedores")
        top10 = (
            df.groupby("PROVEEDOR")["SALDO_NETO_SOLES"]
            .sum()
            .sort_values(ascending=True)
            .tail(10)
            .reset_index()
        )
        top10["texto"] = top10["SALDO_NETO_SOLES"].apply(fmt_num_miles)
        fig = px.bar(
            top10,
            x="SALDO_NETO_SOLES",
            y="PROVEEDOR",
            orientation="h",
            text="texto",
            color="SALDO_NETO_SOLES",
            color_continuous_scale="Oranges",
            height=400,
        )
        fig.update_layout(
            xaxis_title="Miles de Soles",
            yaxis_title="",
            margin=dict(l=0, r=0, t=10, b=0),
        )
        fig.update_traces(textposition="auto")
        st.plotly_chart(fig, use_container_width=True)

    col_doc, col_gasto = st.columns(2)

    with col_doc:
        with st.expander("Desglose por Tipo de Documento", expanded=False):
            doc_agg = (
                df.groupby("TIPDOCU")["SALDO_NETO_SOLES"]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
            )
            doc_agg["texto"] = doc_agg["SALDO_NETO_SOLES"].apply(fmt_num_miles)
            fig = px.bar(
                doc_agg,
                x="TIPDOCU",
                y="SALDO_NETO_SOLES",
                color="SALDO_NETO_SOLES",
                color_continuous_scale="Viridis",
                text="texto",
                height=350,
            )
            fig.update_layout(
                xaxis_title="Tipo Doc",
                yaxis_title="Miles de Soles",
                margin=dict(l=0, r=0, t=10, b=0),
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_gasto:
        st.subheader("Distribucion por Gasto")
        if has_gasto:
            gasto_agg = (
                df.groupby("GASTO")["SALDO_NETO_SOLES"].sum().reset_index()
            )
            fig = px.pie(
                gasto_agg,
                values="SALDO_NETO_SOLES",
                names="GASTO",
                hole=0.4,
                height=350,
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Columna GASTO no disponible en los datos")




def render_rankings(df):
    col1, col2, col3 = st.columns(3)

    top_neto = (
        df.groupby("PROVEEDOR")["SALDO_NETO_SOLES"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    df_mn = df[df["MONEDA"] == "MN"]
    top_mn = (
        df_mn.groupby("PROVEEDOR")["SALDO_NETO"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    df_me = df[df["MONEDA"] == "ME"]
    top_me = (
        df_me.groupby("PROVEEDOR")["SALDO_NETO"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    with col1:
        st.subheader("Top 10 Neto (Miles de Soles)")
        for i, (_, row) in enumerate(top_neto.iterrows(), 1):
            st.markdown(
                f"**#{i}** {row['PROVEEDOR'][:55]}  \n"
                f"{fmt_soles_miles(row['SALDO_NETO_SOLES'])}"
            )

    with col2:
        st.subheader("Top 10 Soles MN (Miles)")
        for i, (_, row) in enumerate(top_mn.iterrows(), 1):
            st.markdown(
                f"**#{i}** {row['PROVEEDOR'][:55]}  \n"
                f"{fmt_soles_miles(row['SALDO_NETO'])}"
            )

    with col3:
        st.subheader("Top 10 Dólares ME (Miles)")
        for i, (_, row) in enumerate(top_me.iterrows(), 1):
            st.markdown(
                f"**#{i}** {row['PROVEEDOR'][:55]}  \n"
                f"{fmt_dolares_miles(row['SALDO_NETO'])}"
            )

    st.markdown("---")
    st.subheader("Cartera por Proveedor (Ranking)")
    prov_rank = (
        df.groupby("PROVEEDOR")
        .agg(
            Total_Saldo=("SALDO_NETO_SOLES", "sum"),
            Documentos=("DOCUMENTO", "count"),
        )
        .sort_values("Total_Saldo", ascending=False)
        .reset_index()
    )
    prov_rank.insert(0, "N", range(1, len(prov_rank) + 1))
    prov_rank["Total"] = prov_rank["Total_Saldo"].apply(fmt_soles_miles)

    st.dataframe(
        prov_rank[["N", "PROVEEDOR", "Total", "Documentos"]],
        column_config={
            "N": "N",
            "PROVEEDOR": "Proveedor",
            "Total": "Total Cartera (Miles S/.)",
            "Documentos": "Docs",
        },
        hide_index=True,
        use_container_width=True,
    )


def render_table(df):
    st.subheader("Detalle de Cuentas por Pagar")

    cols = [
        "RUC/CODIGO", "PROVEEDOR", "TIPDOCU", "DOCUMENTO",
        "FEMISION", "FVCMO", "DIASPAGO",
        "MONEDA", "SALDO (S/.)", "SALDO (US$)", "SALDO_NETO",
    ]
    display_df = df[cols].copy()

    display_df["FEMISION"] = display_df["FEMISION"].dt.strftime("%d/%m/%Y")
    display_df["FVCMO"] = display_df["FVCMO"].dt.strftime("%d/%m/%Y")
    display_df["SALDO (S/.)"] = display_df["SALDO (S/.)"].apply(fmt_soles)
    display_df["SALDO (US$)"] = display_df["SALDO (US$)"].apply(fmt_dolares)
    display_df["SALDO_NETO"] = display_df["SALDO_NETO"].apply(fmt_soles)

    display_df.columns = [
        "RUC", "Proveedor", "Tipo Doc", "Documento",
        "Emision", "Vcto", "Dias Venc.",
        "Moneda", "Saldo S/.", "Saldo US$", "Saldo Neto",
    ]

    search = st.text_input(
        "Buscar por proveedor o documento",
        placeholder="Escribe para filtrar...",
    )
    if search:
        mask = (
            display_df["Proveedor"].str.contains(search, case=False, na=False)
            | display_df["Documento"].str.contains(search, case=False, na=False)
        )
        display_df = display_df[mask]

    st.dataframe(display_df, hide_index=True, use_container_width=True, height=500)

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="Descargar CSV",
        data=csv,
        file_name=f"cxp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )


def main():
    render_sidebar("Cuentas por Pagar")

    if "df_cxp" not in st.session_state:
        st.session_state.df_cxp = None
    if "file_key_cxp" not in st.session_state:
        st.session_state.file_key_cxp = None
    if "file_name_cxp" not in st.session_state:
        st.session_state.file_name_cxp = None
    if "loaded_at_cxp" not in st.session_state:
        st.session_state.loaded_at_cxp = None

    with st.sidebar:
        st.markdown("**📁 Datos**")
        uploaded_file = st.file_uploader(
            "Cargar archivo Excel",
            type=["xlsx"],
            help="Sube tu archivo Excel de Cuentas por Pagar",
            key="cxp_uploader",
        )

        if uploaded_file:
            file_key = f"{uploaded_file.name}_{uploaded_file.size}"
            if st.session_state.file_key_cxp != file_key:
                with st.spinner("Procesando datos..."):
                    try:
                        st.session_state.df_cxp = process_cxp(uploaded_file)
                        st.session_state.file_key_cxp = file_key
                        st.session_state.file_name_cxp = uploaded_file.name
                        st.session_state.loaded_at_cxp = datetime.now()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al procesar el archivo: {e}")
                        st.stop()

        df = st.session_state.df_cxp

        if df is None:
            st.info(
                "Sube un archivo Excel de Cuentas por Pagar para comenzar.\n\n"
                "**Formato esperado:** columnas RUC/CODIGO, PROVEEDOR, TIPDOCU, "
                "DOCUMENTO, FEMISION, FVCMO, DIASPAGO, MONEDA, TC, "
                "SALDO (S/.), SALDO (US$)"
            )
            st.stop()

        st.caption(
            f"{len(df)} registros  ·  "
            f"{st.session_state.file_name_cxp or ''}  ·  "
            f"{st.session_state.loaded_at_cxp.strftime('%d/%m/%Y %H:%M') if st.session_state.loaded_at_cxp else ''}"
        )

        st.divider()
        st.markdown("**🔍 Filtros**")

        all_proveedores = sorted(df["PROVEEDOR"].unique())
        selected_proveedor = st.selectbox(
            "Proveedor", options=["Todos"] + all_proveedores
        )

        selected_currency = st.selectbox(
            "Moneda",
            options=["Todas", "MN (Soles)", "ME (Dolares)"],
        )

        all_tipos = sorted(df["TIPDOCU"].unique())
        selected_tipo = st.selectbox(
            "Tipo Documento", options=["Todos"] + all_tipos
        )

        has_gasto = "GASTO" in df.columns
        if has_gasto:
            all_gastos = sorted(df["GASTO"].unique())
            st.selectbox(
                "Categoria Gasto",
                options=["Todas"] + all_gastos,
                key="selected_gasto",
            )

        min_date = df["FVCMO"].min().date()
        max_date = df["FVCMO"].max().date()
        date_range = st.date_input(
            "Rango fecha vencimiento",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

        min_dias = int(df["DIASPAGO"].min())
        max_dias = int(df["DIASPAGO"].max())
        st.slider(
            "Dias vencidos",
            min_value=min_dias,
            max_value=max_dias,
            value=(min_dias, max_dias),
            key="dias_range_cxp",
        )

    currency_map = {"MN (Soles)": "MN", "ME (Dolares)": "ME"}
    filtered = df.copy()

    if selected_proveedor != "Todos":
        filtered = filtered[filtered["PROVEEDOR"] == selected_proveedor]
    if selected_currency != "Todas":
        filtered = filtered[filtered["MONEDA"] == currency_map[selected_currency]]
    if selected_tipo != "Todos":
        filtered = filtered[filtered["TIPDOCU"] == selected_tipo]
    if has_gasto and st.session_state.selected_gasto != "Todas":
        filtered = filtered[filtered["GASTO"] == st.session_state.selected_gasto]
    if len(date_range) == 2:
        d_start, d_end = date_range
        filtered = filtered[
            (filtered["FVCMO"].dt.date >= d_start)
            & (filtered["FVCMO"].dt.date <= d_end)
        ]
    dias_range = st.session_state.dias_range_cxp
    filtered = filtered[
        (filtered["DIASPAGO"] >= dias_range[0])
        & (filtered["DIASPAGO"] <= dias_range[1])
    ]

    st.markdown(f"## 📄 Cuentas por Pagar")
    tab1, tab2, tab3 = st.tabs(["Dashboard", "Rankings", "Tabla Detallada"])

    with tab1:
        render_dashboard(filtered)
    with tab2:
        render_rankings(filtered)
    with tab3:
        render_table(filtered)

    st.caption(
        f"{len(filtered)} registros de {len(df)} totales  ·  "
        f"Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    )


if __name__ == "__main__":
    main()
