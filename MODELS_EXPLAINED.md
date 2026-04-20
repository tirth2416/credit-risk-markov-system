# Models Overview & Work Breakdown

## All Models in This Project

---

## 1. State Classification Model

**File:** `backend/models/state_model.py`  
**Function:** `assign_state(row)`  
**Type:** Rule-based Classifier (not ML, but mathematical model)

### What It Does
Classifies your financial health into one of 4 states based on your savings ratio.

### How It Works

**Input:** A row with `savings_ratio` column (decimal between 0 and 1)

**Logic:**
```
IF savings_ratio > 0.70:
    STATE = "Excellent"        (You save more than 70%)
    
ELSE IF savings_ratio > 0.40:
    STATE = "Good"             (You save 40-70%)
    
ELSE IF savings_ratio > 0.10:
    STATE = "Risky"            (You save 10-40%)
    
ELSE:
    STATE = "Default"          (You save 10% or less)
```

### The 4 States Explained

| State | Savings Ratio | Meaning | Risk Level |
|-------|---|---|---|
| **Excellent** | > 70% | Saving most of income | Very Low |
| **Good** | 40-70% | Stable balance | Low |
| **Risky** | 10-40% | Tight budget | High |
| **Default** | ≤ 10% | Critical situation | Critical |

### Why This Model Matters
- **Simple but powerful** - One number (savings ratio) tells us everything
- **Meaningful states** - Each state represents real financial health
- **Threshold-based** - Easy to understand and adjust thresholds if needed
- **No training needed** - Rules are fixed, not learned from data

### Example
```
You earn ₹50,000/month
You spend ₹20,000/month
Savings = 50,000 - 20,000 = ₹30,000
Ratio = 30,000 / 50,000 = 0.60 = 60%

Check: 60% is between 40% and 70%
Result: STATE = "Good"
```

### Work Done by This Model
1. Takes monthly savings ratio
2. Compares against 4 thresholds
3. Assigns one of 4 states
4. Output used by Markov model

---

## 2. Markov Chain Model (Core Model)

**File:** `backend/models/markov.py`  
**Functions:** 
- `build_transition_matrix(states)`
- `predict_next(matrix, current_state, state_labels)`

**Type:** Stochastic (Probability-based) Model

### What It Does
Creates a probability matrix showing how likely you are to move between financial states. Then uses that matrix to predict your next month's financial state.

### How It Works - Part A: Building the Transition Matrix

**Input:** Sequence of states over time
```
["Good", "Good", "Excellent", "Good", "Risky", "Good", ...]
```

**Step 1: Count All Transitions**
```
How many times did we go from each state to each state?

Count Matrix:
           Excellent  Good  Risky  Default
Excellent      3      2      1       0        (3+2+1+0 = 6 total)
Good           5     15      3       0        (5+15+3+0 = 23 total)
Risky          1      2      4       1        (1+2+4+1 = 8 total)
Default        0      0      0       2        (0+0+0+2 = 2 total)

Reading: From Excellent, we went to Good 2 times
         From Good, we went to Good 15 times
         etc.
```

**Step 2: Convert Counts to Probabilities**
```
Divide each row by its sum to get probabilities that add to 1.0

Probability Matrix (Transition Matrix):
           Excellent  Good  Risky  Default
Excellent    0.50    0.33  0.17   0.00     (50% + 33% + 17% + 0% = 100%)
Good         0.22    0.65  0.13   0.00     (22% + 65% + 13% + 0% = 100%)
Risky        0.13    0.25  0.50   0.12     (13% + 25% + 50% + 12% = 100%)
Default      0.00    0.00  0.00   1.00     (Always stays in Default)

Reading: From Good state, 65% chance we stay in Good next month!
         From Good state, 22% chance we improve to Excellent
         From Good state, 13% chance we fall to Risky
```

**Output:** Transition matrix (2D array) + State labels (sorted list)

### How It Works - Part B: Making Predictions

**Input:**
- Current state: "Good"
- Transition matrix (from above)
- State labels: ["Default", "Excellent", "Good", "Risky"]

**Process:**
```
1. Find which row in matrix matches "Good"
2. Extract that entire row
3. That row IS the probability distribution for next month

If current state = "Good"
Look at Good row: [0.22, 0.22, 0.65, 0.13]
(These map to Default, Excellent, Good, Risky respectively)

So next month probabilities are:
  Default: 22% chance
  Excellent: 22% chance
  Good: 65% chance
  Risky: 13% chance
```

**Output:** Dictionary with probabilities for each state
```json
{
  "Default": 0.22,
  "Excellent": 0.22,
  "Good": 0.65,
  "Risky": 0.13
}
```

### Mathematical Formula

**Transition Matrix Definition:**
```
P[i,j] = P(X_{t+1} = state_j | X_t = state_i)

Where:
  X_t = Your financial state at time t (current)
  X_{t+1} = Your financial state at time t+1 (next month)
  P[i,j] = Probability of moving from state i to state j
```

**Calculation:**
```
P[i,j] = (Count of transitions from state_i to state_j) 
         / (Total transitions from state_i)
```

### Why This Model Matters
- **Empirical** - Built from your actual data history
- **Predictive** - Uses patterns to forecast future states
- **Probabilistic** - Shows uncertainty (multiple outcomes possible)
- **Markov Property** - Future depends only on present, not entire history
- **Time-Homogeneous** - Same rules apply every month

### Example Scenario
```
Your financial states over 12 months:
Good → Good → Excellent → Good → Risky → Good → Good → Good → Risky → Good → Good → Good

Build transition matrix:
  From Excellent: went to Good only (100%)
  From Good: stayed Good 8 times, went to Excellent 1 time, went to Risky 1 time
  From Risky: went to Good both times

Current state: Good

Prediction:
  We see from history that when in Good state:
  80% chance stay in Good
  10% chance go to Excellent
  10% chance go to Risky
  0% chance go to Default

So next month probabilities:
  Good: 80%
  Excellent: 10%
  Risky: 10%
  Default: 0%
```

### Work Done by This Model
1. Analyzes historical state transitions
2. Builds probability matrix
3. Makes one-step ahead predictions
4. Forecasts next month's likely state
5. Calculates default probability (used for credit scoring)

---

## 3. Credit Scoring Model

**File:** `backend/app.py`  
**Logic:** Risk-adjusted based on state and default probability  
**Type:** Formula-based Model

### What It Does
Calculates your credit score (300-800) based on:
- Your current financial state
- Your risk of defaulting

### How It Works

**Step 1: Base Score by State**
```
"Excellent" state  → Base score = 800
"Good" state       → Base score = 700
"Risky" state      → Base score = 550
"Default" state    → Base score = 300
```

**Step 2: Risk Adjustment**
```
Default probability from Markov prediction
= P(X_{t+1} = Default | X_t = current_state)

Risk adjustment = default_probability × 300

This means:
- If 0% default risk: no adjustment (subtract 0)
- If 5% default risk: subtract 15 points (0.05 × 300)
- If 10% default risk: subtract 30 points (0.10 × 300)
- If 100% default risk: subtract 300 points (1.0 × 300)
```

**Step 3: Final Score**
```
Credit Score = Base Score - Risk Adjustment

Example:
  Current state = "Good" (base 700)
  Default probability = 5% (0.05)
  Risk adjustment = 0.05 × 300 = 15
  Credit Score = 700 - 15 = 685
```

### Score Scale Interpretation
```
800+        → Excellent credit (almost impossible, requires "Excellent" state + 0% default risk)
750-800     → Very Good (Excellent or Good state, minimal risk)
700-750     → Good (Good state, low risk)
650-700     → Fair (Good state with moderate risk, or Risky state with low risk)
600-650     → Poor (Risky state)
300-600     → Very Poor / Default (Critical state)
```

### Why This Model Matters
- **Risk-aware** - Not just based on current state, but future default risk
- **Fair** - Rewards low-risk states, penalizes high-risk
- **Dynamic** - Changes month-to-month as your financial situation changes
- **Transparent** - Clear formula, easy to understand

### Example
```
Month 1:
  State: Good
  Default prob: 2% (from Markov)
  Score = 700 - (0.02 × 300) = 700 - 6 = 694

Month 2:
  State: Still Good
  But default prob: 8% (your expenses increased)
  Score = 700 - (0.08 × 300) = 700 - 24 = 676
  (Score dropped even though state is same, because risk increased)

Month 3:
  State: Risky (savings ratio dropped)
  Default prob: 15%
  Score = 550 - (0.15 × 300) = 550 - 45 = 505
  (Much lower score due to worse state)
```

### Work Done by This Model
1. Identifies current financial state
2. Gets default probability from Markov model
3. Determines base score
4. Calculates risk adjustment
5. Outputs credit score (300-800 range)

---

## 4. Credit Limit Model

**File:** `backend/app.py`  
**Logic:** Income-based with risk adjustment  
**Type:** Formula-based Model

### What It Does
Calculates how much money you can borrow, based on your average income and default risk.

### How It Works

**Formula:**
```
Credit Limit = (Average Monthly Income × 0.3) × (1 - Default Probability)

Where:
  0.3 = Standard lending practice (30% of income)
  (1 - Default Probability) = Risk adjustment factor
```

**Breaking It Down:**

**Part 1: Base Limit (30% of income)**
```
Standard lending allows 30% of monthly income as credit
If you earn ₹50,000/month:
Base limit = ₹50,000 × 0.3 = ₹15,000
```

**Part 2: Risk Adjustment**
```
The higher your default risk, the lower the amount you can borrow

Factor = (1 - Default Probability)

Examples:
  If default prob = 0% (no risk):  factor = 1.0  (no reduction)
  If default prob = 5%:            factor = 0.95 (5% reduction)
  If default prob = 20%:           factor = 0.80 (20% reduction)
  If default prob = 50%:           factor = 0.50 (50% reduction)
  If default prob = 100%:          factor = 0.0  (no credit)
```

**Final Calculation:**
```
Credit Limit = ₹15,000 × 0.95 = ₹14,250 (if default prob = 5%)
Credit Limit = ₹15,000 × 0.80 = ₹12,000 (if default prob = 20%)
Credit Limit = ₹15,000 × 0.50 = ₹7,500  (if default prob = 50%)
```

### Examples

**Example 1: Excellent Financial Health**
```
Average income: ₹100,000/month
Current state: Excellent
Default probability: 1% (from Markov)

Base limit = 100,000 × 0.3 = ₹30,000
Risk factor = 1 - 0.01 = 0.99
Credit Limit = 30,000 × 0.99 = ₹29,700
```

**Example 2: Good Financial Health with Some Risk**
```
Average income: ₹60,000/month
Current state: Good
Default probability: 5% (from Markov)

Base limit = 60,000 × 0.3 = ₹18,000
Risk factor = 1 - 0.05 = 0.95
Credit Limit = 18,000 × 0.95 = ₹17,100
```

**Example 3: Risky Financial State**
```
Average income: ₹40,000/month
Current state: Risky
Default probability: 25% (from Markov)

Base limit = 40,000 × 0.3 = ₹12,000
Risk factor = 1 - 0.25 = 0.75
Credit Limit = 12,000 × 0.75 = ₹9,000
(Can only borrow ₹9,000 instead of ₹12,000 due to risk)
```

### Why This Model Matters
- **Fair lending** - Amount adjusts based on actual risk
- **Income-based** - Proportional to what you can afford
- **Risk-aware** - Protects both lender and borrower
- **Simple** - Easy to understand and transparent

### Adjustability
```
To be more/less lenient, change the 0.3 multiplier:

0.2 = Conservative (20% of income)   → More careful lending
0.3 = Standard (30% of income)       → Balanced approach
0.4 = Generous (40% of income)       → More lending
0.5 = Very generous (50% of income)  → Aggressive lending

Example with 0.2:
Limit = 50,000 × 0.2 × (1 - 0.05) = 10,000 × 0.95 = ₹9,500 (less than ₹14,250)

Example with 0.4:
Limit = 50,000 × 0.4 × (1 - 0.05) = 20,000 × 0.95 = ₹19,000 (more than ₹14,250)
```

### Work Done by This Model
1. Calculates average monthly income
2. Applies 30% multiplier
3. Gets default probability from Markov model
4. Applies risk adjustment
5. Outputs approved credit limit in INR

---

## 5. Savings Ratio Model

**File:** `backend/utils/features.py`  
**Function:** Implicit in `create_features()`  
**Type:** Feature Engineering Model

### What It Does
Calculates what percentage of your income you actually save each month.

### How It Works

**Formula:**
```
Savings Ratio = (Income - Expense) / Income

Where:
  Income = Total money coming in (credits in statement)
  Expense = Total money spent (debits in statement)
  Savings = Income - Expense
  Ratio = Savings / Income (as decimal, 0 to 1.0)
```

**Examples:**
```
Person A:
  Income: ₹100,000
  Expense: ₹30,000
  Savings: ₹70,000
  Ratio: 70,000 / 100,000 = 0.70 = 70% savings
  State: Excellent (ratio > 70%)

Person B:
  Income: ₹100,000
  Expense: ₹60,000
  Savings: ₹40,000
  Ratio: 40,000 / 100,000 = 0.40 = 40% savings
  State: Good (ratio between 40-70%)

Person C:
  Income: ₹100,000
  Expense: ₹95,000
  Savings: ₹5,000
  Ratio: 5,000 / 100,000 = 0.05 = 5% savings
  State: Default (ratio ≤ 10%)
```

### Edge Cases Handled
```
If Income = 0:
  Set Ratio = 0.0 (can't save percent of zero)
  State = Default (assumed critical)

If Expense > Income:
  Still calculates correctly
  Example: Income ₹50,000, Expense ₹70,000
  Savings = 50,000 - 70,000 = -₹20,000 (negative!)
  Ratio = -20,000 / 50,000 = -0.40 = -40%
  State = Default (ratio ≤ 10%, so defaults)
```

### Why This Model Matters
- **Core metric** - Everything else depends on this
- **Simple** - Single number captures financial health
- **Historical** - Calculated for every month
- **Trackable** - Shows improvement/decline over time

### Work Done by This Model
1. Sums all income for the month
2. Sums all expenses for the month
3. Calculates net savings
4. Divides savings by income
5. Outputs ratio (0 to 1.0)
6. This ratio becomes input to State Classification Model

---

## Summary: All Models Work Together

```
                    ┌─────────────────────────────────┐
                    │  SAVINGS RATIO MODEL             │
                    │  (Calculates monthly savings)    │
                    │  Output: savings_ratio (0-1.0)   │
                    └────────────────┬──────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │  STATE CLASSIFICATION MODEL      │
                    │  (Assigns Excellent/Good/...) │
                    │  Output: current_state          │
                    └────────────────┬──────────────────┘
                                     │
                    ┌────────────────┴──────────────────┐
                    │                                  │
                    ▼                                  ▼
      ┌──────────────────────┐      ┌──────────────────────────┐
      │  MARKOV MODEL        │      │  MARKOV MODEL            │
      │  (Build Matrix)      │      │  (Predict Next State)    │
      │  Input: all states   │      │ Input: current state     │
      │  Output: matrix      │      │ Output: probabilities    │
      └──────────────────────┘      └────────────┬─────────────┘
                                                  │
                   ┌──────────────────────────────┼─────────────────────────────┐
                   │                              │                             │
                   ▼                              ▼                             ▼
      ┌──────────────────────┐   ┌──────────────────────────┐  ┌──────────────────────────┐
      │  CREDIT SCORE MODEL  │   │  CREDIT LIMIT MODEL      │  │  USER DASHBOARD          │
      │  Input: state        │   │  Input: income, default  │  │  Shows all results to    │
      │         default_prob │   │  Output: limit amount    │  │  user via frontend       │
      │  Output: 300-800     │   └──────────────────────────┘  └──────────────────────────┘
      └──────────────────────┘
```

---

## Model Statistics

| Model | Type | Input | Output | Used For |
|-------|------|-------|--------|----------|
| **Savings Ratio** | Feature | Income, Expense | Ratio (0-1) | Classification |
| **State Classification** | Rules | Savings Ratio | State (4 values) | Markov input |
| **Markov Chain** | Probability | State sequence | Matrix + predictions | All forecasts |
| **Credit Score** | Formula | State, default_prob | Score (300-800) | User dashboard |
| **Credit Limit** | Formula | Income, default_prob | Amount (INR) | User dashboard |

---

## Key Points

1. **5 Models Total** - Each does specific work
2. **Chained Together** - Output of one becomes input for next
3. **Mathematical** - All based on formulas, not AI/ML
4. **Transparent** - You can see exactly why you got your score
5. **Risk-Aware** - Every model accounts for financial risk
6. **Empirical** - Markov model built from YOUR actual history

---

## Model Complexity

- **Simple to understand:** Savings Ratio, State Classification
- **Medium complexity:** Markov Chain (probability math)
- **Simple formulas:** Credit Score, Credit Limit

**Overall:** Understandable by anyone with basic math knowledge

---

**Last Updated:** April 17, 2026
