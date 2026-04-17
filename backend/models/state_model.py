def assign_state(row):
    """
    Assign financial state based on savings behavior
    """

    savings_ratio = row.get("savings_ratio", 0)
    income = row.get("income", 0)
    expense = row.get("expense", 0)

    # Extra safety
    if income == 0:
        return "Risky"

    # Core logic (tuned for better variation)
    if savings_ratio >= 0.75:
        return "Excellent"
    elif savings_ratio >= 0.55:
        return "Good"
    elif savings_ratio >= 0.35:
        return "Risky"
    else:
        return "Default"