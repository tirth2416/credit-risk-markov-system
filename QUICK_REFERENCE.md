# Quick Reference - Credit Risk Markov Analyzer

## What This System Does

Analyzes bank statements using **Markov Chain theory** to predict credit default risk.

```
PDF Statement → Extract Transactions → Calculate Monthly Savings Ratio 
→ Classify States (Excellent/Good/Risky/Default) → Build Transition Matrix 
→ Predict Next-Period Default Risk → Calculate Credit Score & Limits
```

---

## Getting Started

### Start Everything (Recommended)
```bash
python run.py
```
Opens http://localhost:8080 automatically with backend on http://localhost:8000

### Manual Start
```bash
# Terminal 1: Backend
python -m uvicorn backend.app:app --reload

# Terminal 2: Frontend  
cd frontend && python -m http.server 8080
```

---

## How to Use

1. **Open** http://localhost:8080 in browser
2. **Select** a PDF bank statement
3. **Click** ANALYZE button
4. **View** Results:
   - Markov transition matrix (heatmap table)
   - Current financial state
   - Credit score (300-800)
   - Default probability (%)
   - Approved credit limit
   - State transition forecast chart
   - Monthly cash flow analysis

---

## Financial States

Based on **Savings Ratio** = (Income - Expenses) / Income

| State | Criteria | Color | Meaning |
|-------|----------|-------|---------|
| **Excellent** | ratio > 70% | Green | Very healthy, high savings |
| **Good** | 40% < ratio ≤ 70% | Blue | Stable financial position |
| **Risky** | 10% < ratio ≤ 40% | Orange | Vulnerable, high risk |
| **Default** | ratio ≤ 10% | Red | Critical, likely to default |

---

## Understanding Results

### Current State
Your financial health classifier - determines baseline credit score

### Credit Score (300-800)
- **Base score** depends on current state
- **Penalty** applied based on default probability
- Higher default risk = lower score
- Formula: `score = base - (default_prob × 300)`

### Default Probability
- Probability of entering "Default" state in next month
- Calculated from transition matrix
- Used to adjust credit limit
- Formula: From row of transition matrix matching current state

### Transition Matrix
- Shows P(next_state | current_state) for each combination
- Each row sums to 1.0 (probability distribution)
- **Color coding**:
  - Red (1.0) = Will definitely transition to this state
  - Yellow (0.75) = High probability
  - Green (0.50) = Balanced
  - Blue (0.25) = Low probability
  - Gray (0.0) = No transitions observed

### Credit Limit
- **Formula**: Avg_Income × 0.3 × (1 - Default_Probability)
- **30% baseline**: Standard lending practice
- **Risk adjustment**: High default probability reduces available credit
- **Example**: ₹50,000/month income, 5% default probability = ₹14,250 limit

### Savings Rate
- What percentage of income you save
- Formula: (Income - Expenses) / Income
- Used to classify financial state
- Range: 0% to 100%

---

## PDF Requirements

Your PDF must contain a table with these columns (case-insensitive):
- **Date** - Transaction date
- **Debit / Debit (N)** - Money out (expenses)
- **Credit / Credit (N)** - Money in (income)  
- **Balance / Balance (N)** - Account balance

System automatically handles:
- Different column name variations
- Missing values (filled with 0)
- Non-numeric data (converted or removed)
- Multiple tables (extracts from all pages)

---

## Markov Chain Concepts

### What is it?
A stochastic process where the next state depends **only** on the current state:

```
P(X_{t+1} = j | X_t = i, history) = P(X_{t+1} = j | X_t = i)
```

### Transition Matrix
```
P = [p_ij]  where p_ij = P(X_{t+1} = j | X_t = i)

Example 4x4 matrix:
     Default  Excellent  Good  Risky
D  [   1.0      0.0      0.0    0.0  ]  (Default: absorbing state)
E  [   0.0      0.6      0.4    0.0  ]  (Excellent: 60% stay, 40% → Good)
G  [   0.0      0.0      0.5    0.5  ]  (Good: 50% stay, 50% → Risky)
R  [   0.5      0.0      0.0    0.5  ]  (Risky: 50% → Default, 50% stay)
```

### One-Step Ahead Prediction
Given current state, the transition matrix row tells you:
```
P(next state | current state) = row of P matrix
```

---

## Interpreting Your Analysis

### If You See:
- **State: Excellent** → Secure financial position, low risk
- **State: Good** → Stable, manageable debt
- **State: Risky** → Need to improve savings
- **State: Default** → Critical, high default probability

### Good Signs:
- Default Probability < 5%
- Credit Score > 700
- Savings Rate > 40%
- Staying in Good/Excellent state

### Warning Signs:
- Default Probability > 20%
- Credit Score < 600
- Savings Rate < 10%
- Transitioning toward Risky/Default state

---

## API Endpoint

### POST /analyze
Upload a PDF for analysis

**Request:**
```bash
curl -X POST -F "file=@statement.pdf" http://localhost:8000/analyze
```

**Response:**
```json
{
  "current_state": "Good",
  "credit_score": 685.5,
  "default_probability": 0.0450,
  "credit_limit": 24850.50,
  "expected_months": 22,
  "avg_income": 83091.67,
  "avg_expense": 49673.89,
  "savings_rate": 0.4023,
  "state_labels": ["Default", "Excellent", "Good", "Risky"],
  "transition_matrix": [[1.0, 0, 0, 0], ...],
  "prediction": {
    "Default": 0.045,
    "Excellent": 0.05,
    "Good": 0.85,
    "Risk": 0.055
  },
  "features": [
    {
      "month": "2024-01",
      "income": 7500.0,
      "expense": 4200.0,
      "savings": 3300.0,
      "savings_ratio": 0.44,
      "state": "Good"
    },
    ...
  ]
}
```

---

## Files You Can Edit

### Change State Thresholds
Edit `backend/models/state_model.py`:
```python
if ratio > 0.70:        # Change 0.70 for Excellent boundary
    return "Excellent"
elif ratio > 0.40:      # Change 0.40 for Good boundary
    return "Good"
elif ratio > 0.10:      # Change 0.10 for Risky boundary
    return "Risky"
```

### Change Credit Score Formula
Edit `backend/app.py`:
```python
base_scores = {
    "Excellent": 800,   # Change these
    "Good": 700,
    "Risky": 550,
    "Default": 300
}
```

### Change Credit Limit Formula
Edit `backend/app.py`:
```python
credit_limit = avg_income * 0.3 * (1 - default_prob)
# Change 0.3 for different income multiple
# Change formula structure for different risk adjustment
```

---

## Troubleshooting

### PDF Not Reading
- Make sure it's a valid PDF
- Ensure table has Date + Amount columns
- Check for text (not images/scans)

### Port Already in Use
Change in run.py or terminal:
```bash
# Different frontend port
cd frontend && python -m http.server 8081

# Different backend port
python -m uvicorn backend.app:app --port 8001
```

### Weird Calculation Results
- Need at least 2 months of data
- Large expenses can create negative ratio
- Zero income defaults ratio to 0.0

### Module Not Found
```bash
pip install -r requirements.txt
```

---

## Key Formulas

| Metric | Formula | Range |
|--------|---------|-------|
| Savings Ratio | (Income - Expense) / Income | 0 to 1 |
| Credit Score | base - (default_prob × 300) | 300 to 800 |
| Credit Limit | income × 0.3 × (1 - default_prob) | 0 to (income × 0.3) |
| Default Probability | P[state, "Default"] | 0 to 1 |
| Months to Default | 1 / (default_prob + 0.01) | ~1 to 100+ |

---

## For Academics

**Course**: Stochastic Processes  
**Method**: Markov Chains (Time-Homogeneous, Discrete-Time, Finite-State)  
**Key Matrix**: Transition Probability Matrix P where ∑_j P[i,j] = 1  
**Prediction**: One-step ahead using matrix powers (P^n for n steps ahead)  
**Application Domain**: Credit Risk / Financial Stability Analysis  

---

## Common Questions

**Q: Can I predict 2+ months ahead?**  
A: Yes, use matrix powers: P^2 for 2-step, P^3 for 3-step, etc.

**Q: What if a state never appears in data?**  
A: Transition matrix will have zero columns for that state

**Q: Can I model Default as absorbing?**  
A: Currently it can transition out. Modify to: `matrix[3, 3] = 1.0`

**Q: How accurate are the predictions?**  
A: Limited by data - more months = better estimates

---

**System Status**: ✅ Ready to Use  
**Last Updated**: April 17, 2026
