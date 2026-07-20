import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    salidas = df[df["MVTO"] == "SALIDA"]

    total_ing_mn = ingresos["SALDO_MN"].sum()
    total_ing_me = ingresos["SALDO_ME"].sum()
    total_sal_mn = salidas["SALDO_MN"].sum()
    total_sal_me = salidas["SALDO_ME"].sum()
    saldo_neto_mn = df["SALDO_MN"].sum()
    saldo_neto_me = df["SALDO_ME"].sum()
    saldo_neto_soles = df["SALDO_NETO_SOLES"].sum()
    num_mvtos = len(df)

    kpi_cols = st.columns(6)
    with kpi_cols[0]:
        st.metric("Ingresos MN (Miles)", fmt_soles_miles(total_ing_mn))
    with kpi_cols[1]:
        st.metric("Ingresos ME (Miles)", fmt_dolares_miles(total_ing_me))
    with kpi_cols[2]:
        st.metric("Salidas MN (Miles)", fmt_soles_miles(abs(total_sal_mn)))
    with kpi_cols[3]:
        st.metric("Salidas ME (Miles)", fmt_dolares_miles(abs(total_sal_me)))
    with kpi_cols[4]:
        st.metric("Saldo Neto (Miles S/.)", fmt_soles_miles(saldo_neto_soles))
    with kpi_cols[5]:
        st.metric("Total Movimientos", fmt_num(num_mvtos))

    saldo_inicial = st.session_state.get("saldo_inicial_cb", 0)
    if saldo_inicial:
        st.metric(
            "Saldo Acumulado (Miles S/.)",
            fmt_soles_miles(saldo_inicial + saldo_neto_soles),
            delta=fmt_soles_miles(saldo_neto_soles),
        )

    st.markdown("---")
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Saldos por Banco")
        banco_agg = (
            df.groupby("BANCO")["SALDO_NETO_SOLES"]
            .sum()
            .sort_values(ascending=True)
            .reset_index()
        )
        banco_agg["texto"] = banco_agg["SALDO_NETO_SOLES"].apply(fmt_num_miles)
        fig = px.bar(
            banco_agg,
            x="SALDO_NETO_SOLES",
            y="BANCO",
            orientation="h",
            text="texto",
            color="SALDO_NETO_SOLES",
            color_continuous_scale="Blues",
            height=400,
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

    st.markdown("---")
    st.subheader("Flujo de Caja")

    periodo_opcion = st.radio(
        "Periodicidad",
        options=["Mensual", "Semanal"],
        horizontal=True,
        key="periodo_cb",
    )

    if periodo_opcion == "Mensual":
        df["PERIODO"] = df["PERIODO_MES"]
        sort_key = df["FECHA"].dt.to_period("M")
    else:
        df["PERIODO"] = df["FECHA"].dt.isocalendar().week.astype(int).astype(str)
        df["PERIODO"] = df["FECHA"].dt.year.astype(str) + "-S" + df["PERIODO"].str.zfill(2)
        sort_key = df["FECHA"].dt.isocalendar().week.astype(int)

    flow = (
        df.groupby(["PERIODO", "MVTO"])["SALDO_NETO_SOLES"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )

    for col in ["INGRESO", "SALIDA"]:
        if col not in flow.columns:
            flow[col] = 0

    flow["Salida"] = flow["SALIDA"].abs()
    flow["Neto"] = flow["INGRESO"] + flow["SALIDA"]

    saldo_acum = saldo_inicial
    acumulados = []
    for _, row in flow.iterrows():
        saldo_acum += row["Neto"]
        acumulados.append(saldo_acum)
    flow["Acumulado"] = acumulados

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Ingresos",
        x=flow["PERIODO"],
        y=flow["INGRESO"],
        marker_color="#1f77b4",
    ))
    fig.add_trace(go.Bar(
        name="Salidas",
        x=flow["PERIODO"],
        y=flow["Salida"],
        marker_color="#ff7f0e",
    ))
    fig.add_trace(go.Scatter(
        name="Acumulado",
        x=flow["PERIODO"],
        y=flow["Acumulado"],
        mode="lines+markers",
        marker_color="#2ca02c",
        yaxis="y2",
        line=dict(width=3),
    ))

    fig.update_layout(
        barmode="group",
        height=450,
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", y=-0.2),
        xaxis_title="Periodo",
        yaxis_title="Miles de Soles",
        yaxis2=dict(
            overlaying="y",
            side="right",
            title="Acumulado (Miles S/.)",
            showgrid=False,
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    col_down, col_right2 = st.columns(2)

    with col_down:
        st.subheader("Movimientos por Tipo")
        tipo_agg = df["MVTO"].value_counts().reset_index()
        tipo_agg.columns = ["MVTO", "Cantidad"]
        fig = px.pie(
            tipo_agg,
            values="Cantidad",
            names="MVTO",
            color="MVTO",
            color_discrete_map={"INGRESO": "#1f77b4", "SALIDA": "#ff7f0e"},
            hole=0.4,
            height=350,
        )
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col_right2:
        st.subheader("Top Cuentas Contables")
        desc_agg = (
            df.groupby("DESCCTAC")["SALDO_NETO_SOLES"]
            .sum()
            .abs()
            .sort_values(ascending=True)
            .tail(10)
            .reset_index()
        )
        desc_agg["texto"] = desc_agg["SALDO_NETO_SOLES"].apply(fmt_num_miles)
        fig = px.bar(
            desc_agg,
            x="SALDO_NETO_SOLES",
            y="DESCCTAC",
            orientation="h",
            text="texto",
            color="SALDO_NETO_SOLES",
            color_continuous_scale="Viridis",
            height=350,
        )
        fig.update_layout(
            xaxis_title="Miles de Soles",
            yaxis_title="",
            margin=dict(l=0, r=0, t=10, b=0),
        )
        fig.update_traces(textposition="auto")
        st.plotly_chart(fig, use_container_width=True)


def render_rankings(df):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Bancos por Saldo Neto")
        top_bancos = (
            df.groupby("BANCO")["SALDO_NETO_SOLES"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        for i, (_, row) in enumerate(top_bancos.iterrows(), 1):
            st.markdown(
                f"**#{i}** {row['BANCO'][:55]}  \n"
                f"{fmt_soles_miles(row['SALDO_NETO_SOLES'])}"
            )

    with col2:
        st.subheader("Top Anexos por Movimiento")
        if "ANEXO" in df.columns:
            anexo_agg = (
                df.groupby("ANEXO")["SALDO_NETO_SOLES"]
                .sum()
                .abs()
                .sort_values(ascending=False)
                .reset_index()
            )
            for i, (_, row) in enumerate(anexo_agg.iterrows(), 1):
                label = row["ANEXO"] if pd.notna(row["ANEXO"]) else "SIN ANEXO"
                st.markdown(
                    f"**#{i}** {label[:55]}  \n"
                    f"{fmt_soles_miles(row['SALDO_NETO_SOLES'])}"
                )
        else:
            st.info("Columna ANEXO no disponible")

    st.markdown("---")
    st.subheader("Ranking de Cuentas Contables (Mayor Movimiento)")

    has_anexo = "ANEXO" in df.columns
    group_cols = ["DESCCTAC"]
    if has_anexo:
        group_cols = ["DESCCTAC", "ANEXO"]

    cuentas_rank = (
        df.groupby(group_cols)
        .agg(
            Total_MN=("SALDO_MN", "sum"),
            Total_ME=("SALDO_ME", "sum"),
            Movimientos=("SECUENCIA", "count"),
        )
        .sort_values("Movimientos", ascending=False)
        .reset_index()
    )
    cuentas_rank.insert(0, "N", range(1, len(cuentas_rank) + 1))
    cuentas_rank["Total MN"] = cuentas_rank["Total_MN"].apply(fmt_soles_miles)
    cuentas_rank["Total ME"] = cuentas_rank["Total_ME"].apply(fmt_dolares_miles)

    display_cols = ["N", "DESCCTAC", "Total MN", "Total ME", "Movimientos"]
    if has_anexo:
        display_cols = ["N", "DESCCTAC", "ANEXO", "Total MN", "Total ME", "Movimientos"]

    st.dataframe(
        cuentas_rank[display_cols],
        column_config={
            "N": "N",
            "DESCCTAC": "Cuenta Contable",
            "ANEXO": "Anexo",
            "Total MN": "Total MN (Miles S/.)",
            "Total ME": "Total ME (Miles US$)",
            "Movimientos": "Mov.",
        },
        hide_index=True,
        use_container_width=True,
    )


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
    if "saldo_inicial_cb" not in st.session_state:
        st.session_state.saldo_inicial_cb = 0.0

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
        date_range = st.date_input(
            "Rango de fechas",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

        st.divider()
        st.markdown("**💰 Saldo Inicial**")
        saldo_inicial = st.number_input(
            "Saldo inicial (Soles)",
            value=st.session_state.saldo_inicial_cb,
            step=1000.0,
            format="%.2f",
            key="saldo_input_cb",
        )
        st.session_state.saldo_inicial_cb = saldo_inicial

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
    if len(date_range) == 2:
        d_start, d_end = date_range
        filtered = filtered[
            (filtered["FECHA"].dt.date >= d_start)
            & (filtered["FECHA"].dt.date <= d_end)
        ]

    st.markdown(f"## 🏦 Caja y Bancos")
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
