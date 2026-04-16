import pandas as pd

def clean_data(df):
    df.columns = [col.lower().strip() for col in df.columns]

    column_map = {
        "date": "date",
        "narration": "description",
        "description": "description",
        "debit (n)": "debit",
        "debit": "debit",
        "credit (n)": "credit",
        "credit": "credit",
        "balance (n)": "balance",
        "balance": "balance"
    }

    df = df.rename(columns=column_map)

    for col in ["debit", "credit", "balance"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df["debit"] = df["debit"].fillna(0)
    df["credit"] = df["credit"].fillna(0)

    df["date"] = pd.to_datetime(df["date"], errors='coerce')
    df = df.dropna(subset=["date"])

    return df