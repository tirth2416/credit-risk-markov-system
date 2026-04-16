def assign_state(row):
    if row['savings_ratio'] > 0.4:
        return "Excellent"
    elif row['savings_ratio'] > 0.2:
        return "Good"
    elif row['savings_ratio'] > 0:
        return "Risky"
    else:
        return "Default"