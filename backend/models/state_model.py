def assign_state(row):
    ratio = row['savings_ratio']

    if ratio > 0.75:
        return "Excellent"
    elif ratio > 0.55:
        return "Good"
    elif ratio > 0.35:
        return "Risky"
    else:
        return "Default"