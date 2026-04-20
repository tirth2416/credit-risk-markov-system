def assign_state(row):
    """Classify financial health state based on savings ratio.
    
    Markov States (based on savings_ratio = (income - expense) / income):
    - Excellent: ratio > 0.70 (saving >70% of income, very healthy)
    - Good:      0.40 < ratio <= 0.70 (stable financial position)
    - Risky:     0.10 < ratio <= 0.40 (vulnerable, high risk)
    - Default:   ratio <= 0.10 (critical, likely to default)
    
    These states define the Markov chain's state space.
    """
    ratio = row["savings_ratio"]

    if ratio > 0.70:
        return "Excellent"
    elif ratio > 0.40:
        return "Good"
    elif ratio > 0.10:
        return "Risky"
    else:
        return "Default"