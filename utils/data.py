import streamlit as st
import pandas as pd

from utils.formatting import AGING_BINS, AGING_LABELS


CXC_DOCS = {"FT", "BV", "ND"}
IGNORE_DOCS = {"VR"}

CXC_REQUIRED = [
    "CODIGOCLIENTE", "NOMBRECLIENTE", "TIPODOC", "NUMERO",
    "FECHAEMISION", "FECHAVCMTO", "DIAS_VENCIDOS",
    "VENDEDOR", "MONEDA", "SALDO (S/.)", "SALDO (US$)", "TIPOCAMBIO",
]

CXP_REQUIRED = [
    "RUC/CODIGO", "PROVEEDOR", "TIPDOCU", "DOCUMENTO",
    "FEMISION", "FVCMO", "DIASPAGO",
    "MONEDA", "TC", "SALDO (S/.)", "SALDO (US$)",
]

CXC_COL_MAP = {}
CXP_COL_MAP = {}


def validate_columns(df, required, module_name):
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(
            f"El archivo no tiene las columnas requeridas para {module_name}: "
            f"{', '.join(missing)}"
        )
        st.stop()
    return True


def add_aging_column(df, days_col="DIAS_VENCIDOS"):
    df["RANGO_VENCIMIENTO"] = pd.cut(
        df[days_col], bins=AGING_BINS, labels=AGING_LABELS, right=True
    )
    return df


def add_month_column(df, date_col="FECHAEMISION"):
    df["MES_EMISION"] = df[date_col].dt.month
    return df


@st.cache_data
def load_excel(file_buffer):
    return pd.read_excel(file_buffer)


def process_cxc(file_buffer):
    df = load_excel(file_buffer)
    df.columns = df.columns.str.strip()
    validate_columns(df, CXC_REQUIRED, "Cuentas por Cobrar")

    df = df[~df["TIPODOC"].isin(IGNORE_DOCS)].copy()

    es_mn = df["MONEDA"] == "MN"
    es_cxc = df["TIPODOC"].isin(CXC_DOCS)

    df["SALDO"] = df["SALDO (S/.)"].where(es_mn, df["SALDO (US$)"])
    df["SALDO_SOLES"] = df["SALDO (S/.)"].where(
        es_mn, df["SALDO (US$)"] * df["TIPOCAMBIO"]
    )
    df["SALDO_NETO"] = df["SALDO"].where(es_cxc, -df["SALDO"])
    df["SALDO_NETO_SOLES"] = df["SALDO_SOLES"].where(es_cxc, -df["SALDO_SOLES"])

    df["VENDEDOR"] = df["VENDEDOR"].str.strip()
    df["NOMBRECLIENTE"] = df["NOMBRECLIENTE"].str.strip()

    df = add_aging_column(df, "DIAS_VENCIDOS")
    df = add_month_column(df, "FECHAEMISION")

    return df


def process_cxp(file_buffer):
    df = load_excel(file_buffer)
    df.columns = df.columns.str.strip()
    validate_columns(df, CXP_REQUIRED, "Cuentas por Pagar")

    es_mn = df["MONEDA"] == "MN"

    df["SALDO"] = df["SALDO (S/.)"].where(es_mn, df["SALDO (US$)"])
    df["SALDO_SOLES"] = df["SALDO (S/.)"].where(
        es_mn, df["SALDO (US$)"] * df["TC"]
    )
    df["SALDO_NETO"] = df["SALDO"]
    df["SALDO_NETO_SOLES"] = df["SALDO_SOLES"]

    df["PROVEEDOR"] = df["PROVEEDOR"].str.strip()
    df["RUC"] = df["RUC/CODIGO"].astype(str).str.strip()

    df = add_aging_column(df, "DIASPAGO")
    df = add_month_column(df, "FEMISION")

    return df


CAJA_BANCOS_REQUIRED = [
    "CODBCO", "MVTO", "FECHA", "CB_N_MTOMN", "CB_N_MTOME", "BANCO",
    "DESCCTAC",
]


def process_caja_bancos(file_buffer):
    df = load_excel(file_buffer)
    df.columns = df.columns.str.strip()
    validate_columns(df, CAJA_BANCOS_REQUIRED, "Caja y Bancos")

    df["MONEDA"] = df["BANCO"].str.extract(r"(MN|ME)$", expand=False)

    sign = df["MVTO"].map({"INGRESO": 1, "SALIDA": -1}).fillna(1)

    df["SALDO_MN"] = df["CB_N_MTOMN"] * sign
    df["SALDO_ME"] = df["CB_N_MTOME"] * sign

    es_mn = df["MONEDA"] == "MN"
    df["SALDO_NETO"] = df["SALDO_MN"].where(es_mn, df["SALDO_ME"])
    df["SALDO_NETO_SOLES"] = df["SALDO_MN"]

    df["FECHA"] = pd.to_datetime(df["FECHA"], dayfirst=True)
    df["PERIODO_MES"] = df["FECHA"].dt.to_period("M").astype(str)
    df["PERIODO_SEMANA"] = df["FECHA"].dt.isocalendar().week.astype(str)
    df["MES_NOMBRE"] = df["FECHA"].dt.month_name().str.upper()
    df["BANCO"] = df["BANCO"].str.strip()
    df["DESCCTAC"] = df["DESCCTAC"].str.strip()

    return df
