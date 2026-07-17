import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from utils.formatting import fmt_soles, fmt_dolares, fmt_num, MONTH_NAMES
from utils.data import process_cxc

st.set_page_config(
    page_title="CxC - Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_dashboard(df, df_original):
    neto_mn = df[df["MONEDA"] == "MN"]["SALDO_NETO"].sum()
    neto_me = df[df["MONEDA"] == "ME"]["SALDO_NETO"].sum()
    neto_soles = df["SALDO_NETO_SOLES"].sum()
    clientes_deuda = (
        df.groupby("NOMBRECLIENTE")["SALDO_NETO_SOLES"].sum().gt(0).sum()
    )
    num_docs = len(df)

    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        st.metric("Total CxC MN", fmt_soles(neto_mn))
    with kpi_cols[1]:
        st.metric("Total CxC ME", fmt_dolares(neto_me))
    with kpi_cols[2]:
        st.metric("Clientes con Deuda", fmt_num(clientes_deuda))
    with kpi_cols[3]:
        st.metric("Total Documentos", fmt_num(num_docs))

    st.markdown("")
    st.metric(
        "Saldo Neto (convertido a Soles)",
        fmt_soles(neto_soles),
    )

    has_tipo = "TIPO" in df_original.columns
    if has_tipo:
        st.markdown("---")
        st.subheader("Resumen por Tipo")
        resumen = {}
        for tipo in sorted(df_original["TIPO"].unique()):
            d = df_original[df_original["TIPO"] == tipo]
            resumen[tipo] = {
                "MN": d[d["MONEDA"] == "MN"]["SALDO_NETO"].sum(),
                "ME": d[d["MONEDA"] == "ME"]["SALDO_NETO"].sum(),
                "Clientes": (
                    d.groupby("NOMBRECLIENTE")["SALDO_NETO_SOLES"].sum() > 0
                ).sum(),
                "Neto": d["SALDO_NETO_SOLES"].sum(),
            }

        row_data = []
        labels = {
            "MN": "Total CxC MN",
            "ME": "Total CxC ME",
            "Clientes": "Clientes con Deuda",
            "Neto": "Saldo Neto",
        }
        formatters = {
            "MN": fmt_soles,
            "ME": fmt_dolares,
            "Clientes": fmt_num,
            "Neto": fmt_soles,
        }
        for key, label in labels.items():
            entry = {"Métrica": label}
            for tipo in sorted(df_original["TIPO"].unique()):
                entry[tipo] = formatters[key](resumen[tipo][key])
            row_data.append(entry)
        tipo_df = pd.DataFrame(row_data)
        st.dataframe(
            tipo_df,
            column_config={"Métrica": "Métrica"},
            hide_index=True,
            use_container_width=True,
        )

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Cartera por Vendedor")
        vendor_agg = (
            df.groupby("VENDEDOR")["SALDO_NETO_SOLES"]
            .sum()
            .sort_values(ascending=True)
            .reset_index()
        )
        fig = px.bar(
            vendor_agg,
            x="SALDO_NETO_SOLES",
            y="VENDEDOR",
            orientation="h",
            text_auto=",.2f",
            color="SALDO_NETO_SOLES",
            color_continuous_scale="Blues",
            height=400,
        )
        fig.update_layout(
            xaxis_title="Saldo Neto (Soles)",
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
        fig = px.bar(
            aging_agg,
            x="RANGO_VENCIMIENTO",
            y="SALDO_NETO_SOLES",
            category_orders={"RANGO_VENCIMIENTO": aging_order},
            color="SALDO_NETO_SOLES",
            color_continuous_scale="Reds",
            text_auto=",.2f",
            height=400,
        )
        fig.update_layout(
            xaxis_title="Rango",
            yaxis_title="Saldo Neto (Soles)",
            margin=dict(l=0, r=0, t=10, b=0),
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with col_right2:
        st.subheader("Top 10 Deudores")
        top10 = (
            df.groupby("NOMBRECLIENTE")["SALDO_NETO_SOLES"]
            .sum()
            .sort_values(ascending=True)
            .tail(10)
            .reset_index()
        )
        fig = px.bar(
            top10,
            x="SALDO_NETO_SOLES",
            y="NOMBRECLIENTE",
            orientation="h",
            text_auto=",.2f",
            color="SALDO_NETO_SOLES",
            color_continuous_scale="Greens",
            height=400,
        )
        fig.update_layout(
            xaxis_title="Saldo Neto (Soles)",
            yaxis_title="",
            margin=dict(l=0, r=0, t=10, b=0),
        )
        fig.update_traces(textposition="auto")
        st.plotly_chart(fig, use_container_width=True)

    col_doc, col_tipo = st.columns(2)

    with col_doc:
        with st.expander("Desglose por Tipo de Documento", expanded=False):
            doc_agg = (
                df.groupby("TIPODOC")["SALDO_NETO_SOLES"]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
            )
            fig = px.bar(
                doc_agg,
                x="TIPODOC",
                y="SALDO_NETO_SOLES",
                color="SALDO_NETO_SOLES",
                color_continuous_scale="Viridis",
                text_auto=",.2f",
                height=350,
            )
            fig.update_layout(
                xaxis_title="Tipo Doc",
                yaxis_title="Saldo Neto (Soles)",
                margin=dict(l=0, r=0, t=10, b=0),
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_tipo:
        st.subheader("Distribucion por Tipo")
        if has_tipo:
            tipo_agg = (
                df.groupby("TIPO")["SALDO_NETO_SOLES"].sum().reset_index()
            )
            fig = px.pie(
                tipo_agg,
                values="SALDO_NETO_SOLES",
                names="TIPO",
                hole=0.4,
                height=350,
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Columna TIPO no disponible en los datos")

    st.markdown("### Evolucion de Emision por Mes")
    monthly = (
        df.groupby("MES_EMISION")["SALDO_NETO_SOLES"].sum().reset_index()
    )
    month_order = list(MONTH_NAMES.values())
    fig = px.bar(
        monthly,
        x="MES_EMISION",
        y="SALDO_NETO_SOLES",
        category_orders={"MES_EMISION": month_order},
        text_auto=",.2f",
        color="SALDO_NETO_SOLES",
        color_continuous_scale="Teal",
        height=400,
    )
    fig.update_layout(
        xaxis_title="Mes de Emision",
        yaxis_title="Saldo Neto (Soles)",
        margin=dict(l=0, r=0, t=10, b=0),
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


def render_rankings(df):
    col1, col2, col3 = st.columns(3)

    top_neto = (
        df.groupby("NOMBRECLIENTE")["SALDO_NETO_SOLES"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    df_mn = df[df["MONEDA"] == "MN"]
    top_mn = (
        df_mn.groupby("NOMBRECLIENTE")["SALDO_NETO"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    df_me = df[df["MONEDA"] == "ME"]
    top_me = (
        df_me.groupby("NOMBRECLIENTE")["SALDO_NETO"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    with col1:
        st.subheader("Top 10 Neto (Soles)")
        for i, (_, row) in enumerate(top_neto.iterrows(), 1):
            st.markdown(
                f"**#{i}** {row['NOMBRECLIENTE'][:55]}  \n"
                f"{fmt_soles(row['SALDO_NETO_SOLES'])}"
            )

    with col2:
        st.subheader("Top 10 Soles (MN)")
        for i, (_, row) in enumerate(top_mn.iterrows(), 1):
            st.markdown(
                f"**#{i}** {row['NOMBRECLIENTE'][:55]}  \n"
                f"{fmt_soles(row['SALDO_NETO'])}"
            )

    with col3:
        st.subheader("Top 10 Dolares (ME)")
        for i, (_, row) in enumerate(top_me.iterrows(), 1):
            st.markdown(
                f"**#{i}** {row['NOMBRECLIENTE'][:55]}  \n"
                f"{fmt_dolares(row['SALDO_NETO'])}"
            )

    st.markdown("---")
    st.subheader("Cartera por Vendedor (Ranking)")

    vendor_rank = (
        df.groupby("VENDEDOR")
        .agg(
            Total_Saldo=("SALDO_NETO_SOLES", "sum"),
            Clientes=("NOMBRECLIENTE", "nunique"),
            Documentos=("NUMERO", "count"),
        )
        .sort_values("Total_Saldo", ascending=False)
        .reset_index()
    )
    vendor_rank.insert(0, "N", range(1, len(vendor_rank) + 1))
    vendor_rank["Total"] = vendor_rank["Total_Saldo"].apply(fmt_soles)

    st.dataframe(
        vendor_rank[["N", "VENDEDOR", "Total", "Clientes", "Documentos"]],
        column_config={
            "N": "N",
            "VENDEDOR": "Vendedor",
            "Total": "Total Cartera",
            "Clientes": "Clientes",
            "Documentos": "Docs",
        },
        hide_index=True,
        use_container_width=True,
    )


def render_table(df):
    st.subheader("Detalle de Cuentas por Cobrar")

    cols = [
        "CODIGOCLIENTE", "NOMBRECLIENTE", "TIPODOC", "NUMERO",
        "FECHAEMISION", "FECHAVCMTO", "DIAS_VENCIDOS",
        "VENDEDOR", "MONEDA", "SALDO (S/.)", "SALDO (US$)", "SALDO_NETO",
    ]
    display_df = df[cols].copy()

    display_df["FECHAEMISION"] = display_df["FECHAEMISION"].dt.strftime("%d/%m/%Y")
    display_df["FECHAVCMTO"] = display_df["FECHAVCMTO"].dt.strftime("%d/%m/%Y")
    display_df["SALDO (S/.)"] = display_df["SALDO (S/.)"].apply(fmt_soles)
    display_df["SALDO (US$)"] = display_df["SALDO (US$)"].apply(fmt_dolares)
    display_df["SALDO_NETO"] = display_df["SALDO_NETO"].apply(fmt_soles)

    display_df.columns = [
        "RUC", "Cliente", "Tipo", "Numero",
        "Emision", "Vcto", "Dias Venc.",
        "Vendedor", "Moneda", "Saldo S/.", "Saldo US$", "Saldo Neto",
    ]

    search = st.text_input(
        "Buscar por cliente o documento",
        placeholder="Escribe para filtrar...",
    )
    if search:
        mask = (
            display_df["Cliente"].str.contains(search, case=False, na=False)
            | display_df["Numero"].str.contains(search, case=False, na=False)
        )
        display_df = display_df[mask]

    st.dataframe(display_df, hide_index=True, use_container_width=True, height=500)

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="Descargar CSV",
        data=csv,
        file_name=f"cxc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )


def main():
    st.title("💰 Cuentas por Cobrar")
    st.markdown("---")

    if "df_cxc" not in st.session_state:
        st.session_state.df_cxc = None
    if "file_key_cxc" not in st.session_state:
        st.session_state.file_key_cxc = None
    if "file_name_cxc" not in st.session_state:
        st.session_state.file_name_cxc = None
    if "loaded_at_cxc" not in st.session_state:
        st.session_state.loaded_at_cxc = None

    with st.sidebar:
        st.page_link("app.py", label="⬅ Volver al inicio", icon="🏠")
        st.markdown("---")

        st.header("Datos")

        uploaded_file = st.file_uploader(
            "Cargar archivo Excel",
            type=["xlsx"],
            help="Sube tu archivo Excel de Cuentas por Cobrar",
            key="cxc_uploader",
        )

        if uploaded_file:
            file_key = f"{uploaded_file.name}_{uploaded_file.size}"
            if st.session_state.file_key_cxc != file_key:
                with st.spinner("Procesando datos..."):
                    try:
                        st.session_state.df_cxc = process_cxc(uploaded_file)
                        st.session_state.file_key_cxc = file_key
                        st.session_state.file_name_cxc = uploaded_file.name
                        st.session_state.loaded_at_cxc = datetime.now()
                        st.success(
                            f"{len(st.session_state.df_cxc)} registros cargados"
                        )
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al procesar el archivo: {e}")
                        st.stop()

        df = st.session_state.df_cxc

        if df is None:
            st.warning("Sube un archivo Excel para comenzar.")
            st.markdown("---")
            st.info(
                "**Instrucciones:**\n"
                "1. Prepara tu archivo Excel de CxC\n"
                "2. Usa el boton de arriba para subirlo\n"
                "3. Solo tu veras tus datos"
            )
            st.stop()

        st.info(f"{len(df)} registros cargados")
        if st.session_state.loaded_at_cxc:
            st.caption(
                f"Archivo: {st.session_state.file_name_cxc} | "
                f"{st.session_state.loaded_at_cxc.strftime('%d/%m/%Y %H:%M')}"
            )

        st.markdown("---")
        st.header("Filtros")

        all_clients = sorted(df["NOMBRECLIENTE"].unique())
        selected_client = st.selectbox(
            "Cliente", options=["Todos"] + all_clients
        )

        selected_currency = st.selectbox(
            "Moneda", options=["Todas", "MN (Soles)", "ME (Dolares)"]
        )

        has_tipo = "TIPO" in df.columns
        if has_tipo:
            all_tipos = sorted(df["TIPO"].unique())
            selected_tipo = st.selectbox("Tipo", options=["Todas"] + all_tipos)
        else:
            selected_tipo = "Todas"

        all_vendors = sorted(df["VENDEDOR"].unique())
        selected_vendors = st.multiselect(
            "Vendedor(es)",
            options=all_vendors,
            placeholder="Selecciona vendedores...",
        )

        min_date = df["FECHAVCMTO"].min().date()
        max_date = df["FECHAVCMTO"].max().date()
        date_range = st.date_input(
            "Rango fecha vencimiento",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

        min_dias = int(df["DIAS_VENCIDOS"].min())
        max_dias = int(df["DIAS_VENCIDOS"].max())
        dias_range = st.slider(
            "Dias vencidos",
            min_value=min_dias,
            max_value=max_dias,
            value=(min_dias, max_dias),
        )

    currency_map = {"MN (Soles)": "MN", "ME (Dolares)": "ME"}
    filtered = df.copy()

    if selected_client != "Todos":
        filtered = filtered[filtered["NOMBRECLIENTE"] == selected_client]
    if selected_currency != "Todas":
        filtered = filtered[filtered["MONEDA"] == currency_map[selected_currency]]
    if selected_vendors:
        filtered = filtered[filtered["VENDEDOR"].isin(selected_vendors)]
    if len(date_range) == 2:
        d_start, d_end = date_range
        filtered = filtered[
            (filtered["FECHAVCMTO"].dt.date >= d_start)
            & (filtered["FECHAVCMTO"].dt.date <= d_end)
        ]
    filtered = filtered[
        (filtered["DIAS_VENCIDOS"] >= dias_range[0])
        & (filtered["DIAS_VENCIDOS"] <= dias_range[1])
    ]
    if "TIPO" in filtered.columns and selected_tipo != "Todas":
        filtered = filtered[filtered["TIPO"] == selected_tipo]

    tab1, tab2, tab3 = st.tabs(["Dashboard", "Rankings", "Tabla Detallada"])

    with tab1:
        render_dashboard(filtered, df)

    with tab2:
        render_rankings(filtered)

    with tab3:
        render_table(filtered)

    st.markdown("---")
    st.caption(
        f"{len(filtered)} registros de {len(df)} totales | "
        f"Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    )


if __name__ == "__main__":
    main()
