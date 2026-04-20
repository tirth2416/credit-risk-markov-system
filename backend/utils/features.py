import pandas as pd

def create_features(df):
    """Extract monthly financial features for Markov state assignment.
    
    Savings Ratio = (Income - Expense) / Income
    This represents the proportion of income saved, ranges [0, 1].
    Used to classify financial health states in the Markov chain.
    """
    df['month'] = df['date'].dt.to_period('M')

    features = []

    for m, group in df.groupby('month'):
        total_credit = group['credit'].sum()  # Income
        total_debit = group['debit'].sum()    # Expenses

        savings = total_credit - total_debit
        
        # Avoid division by zero: if income is 0, ratio defaults to 0
        if total_credit > 0:
            ratio = savings / total_credit
        else:
            ratio = 0.0

        features.append({
            "month": str(m),
            "income": total_credit,
            "expense": total_debit,
            "savings": savings,
            "savings_ratio": ratio
        })

    return pd.DataFrame(features)