import pandas as pd

MONTH_NAMES = {
    1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
    5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
    9: "SETIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE",
}

AGING_LABELS = ["No vencido", "1-30 dias", "31-60 dias", "61-90 dias", "90+ dias"]
AGING_BINS = [-1, 0, 30, 60, 90, float("inf")]


def fmt_soles(val):
    if pd.isna(val) or val == 0:
        return "S/ 0"
    return f"S/ {val:,.2f}"


def fmt_dolares(val):
    if pd.isna(val) or val == 0:
        return "US$ 0"
    return f"US$ {val:,.2f}"


def fmt_num(val):
    if pd.isna(val):
        return "0"
    return f"{val:,.0f}"


def fmt_soles_miles(val):
    if pd.isna(val) or val == 0:
        return "S/ 0"
    return f"S/ {val/1000:,.2f}"


def fmt_dolares_miles(val):
    if pd.isna(val) or val == 0:
        return "US$ 0"
    return f"US$ {val/1000:,.2f}"


def fmt_num_miles(val):
    if pd.isna(val):
        return "0"
    return f"{val/1000:,.2f}"
