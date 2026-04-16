import pandas as pd

def create_features(df):
    df['month'] = df['date'].dt.to_period('M')

    features = []

    for m, group in df.groupby('month'):
        total_credit = group['credit'].sum()
        total_debit = group['debit'].sum()

        savings = total_credit - total_debit
        ratio = savings / (total_credit + 1)

        features.append({
            "month": str(m),
            "income": total_credit,
            "expense": total_debit,
            "savings": savings,
            "savings_ratio": ratio
        })

    return pd.DataFrame(features)