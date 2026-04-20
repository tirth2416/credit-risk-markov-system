# Credit Risk Markov Chain Analyzer

A professional full-stack application analyzing bank statements using **Markov Chain theory** (stochastic processes) to predict financial health states and credit default risk.

## Overview

```
PDF Bank Statement 
    ↓
[Extract & Clean Data]
    ↓
[Calculate Monthly Savings Patterns]
    ↓
[Classify Financial Health States]
    ↓
[Build Markov Transition Matrix]
    ↓
[Predict Next-Period Default Risk]
    ↓
[Generate Credit Score & Limits]
```

---

## Key Features

### Financial Analysis
- **PDF Extraction**: Tables from bank statements (Date, Debit, Credit, Balance)
- **Savings Ratio**: Monthly (Income - Expense) / Income analysis
- **State Classification**: 4-state financial health model (Excellent/Good/Risky/Default)

### Markov Chain Modeling
- **Transition Matrix**: P(next_state | current_state) from historical data
- **Heatmap Visualization**: Color-coded probability matrix
- **State Sequence Timeline**: Track financial health trajectory
- **One-Step Prediction**: Forecast next-period state distribution

### Credit Assessment
- **Dynamic Credit Score** (300-800): Based on current state + default risk
- **Risk-Adjusted Credit Limit**: Income × 0.3 × (1 - default_probability)
- **Default Probability**: Next-period probability from Markov matrix

### Professional Dashboard
- **Metric Cards**: State, Score, Risk %, Limit, Income, Savings Rate
- **Interactive Charts**: Transition probabilities, cash flow, state timeline
- **Transaction Matrix**: Visual heatmap with color intensity
- **Loading Indicators**: Real-time feedback during processing

---

## Installation & Usage

### Quick Start (Recommended)
```bash
python run.py
```
- Automatically starts backend and frontend
- Opens http://localhost:8080 in browser
- Installs dependencies if needed

### Manual Start
```bash
# Terminal 1: Backend API
python -m uvicorn backend.app:app --reload

# Terminal 2: Frontend Server
cd frontend && python -m http.server 8080
```

### Using the Application
1. Open **http://localhost:8080**
2. Click "ANALYZE" button
3. Select a PDF bank statement
4. View complete Markov analysis with visualizations

---

## Financial States

Classification based on **Savings Ratio = (Income - Expense) / Income**

| State | Criteria | Color | Interpretation |
|-------|----------|-------|-----------------|
| **Excellent** | ratio > 70% | Green | Excellent financial health, >70% savings rate |
| **Good** | 40%-70% | Blue | Stable, healthy financial position |
| **Risky** | 10%-40% | Orange | Vulnerable, tight budget, high risk |
| **Default** | ratio ≤ 10% | Red | Critical condition, high default risk |

---

## Mathematical Foundation

### Markov Chain
A stochastic process where next state depends only on current state:
```
P(X_{t+1} = j | X_t = i, history) = P(X_{t+1} = j | X_t = i)
```

### Transition Matrix
```
P[i,j] = P(X_{t+1} = j | X_t = i)

Estimated from observed transitions:
P[i,j] = (# transitions from state_i to state_j) / (# times in state_i)

Each row sums to 1.0 (probability distribution)
```

### Credit Indicators
```
Credit Score = Base_Score - (Default_Prob × 300)
Credit Limit = Avg_Income × 0.3 × (1 - Default_Prob)
Default Prob = P[current_state, "Default"]  (from transition matrix)
```

---

## API Reference

### POST /analyze

Upload PDF bank statement for analysis

**Request:**
```bash
curl -X POST -F "file=@statement.pdf" http://localhost:8000/analyze
```

**Response:**
```json
{
  "current_state": "Good",
  "credit_score": 685.5,
  "default_probability": 0.045,
  "credit_limit": 24850.50,
  "avg_income": 83091.67,
  "avg_expense": 49673.89,
  "savings_rate": 0.4023,
  "state_labels": ["Default", "Excellent", "Good", "Risky"],
  "transition_matrix": [[1.0, 0, 0, 0], ...],
  "prediction": {
    "Default": 0.045,
    "Excellent": 0.05,
    "Good": 0.85,
    "Risky": 0.055
  },
  "features": [{...}]
}
```

---

## PDF Requirements

Your bank statement PDF must contain a **table** with:
- **Date** column (transaction date)
- **Debit/Debit (N)** or equivalent (money out)
- **Credit/Credit (N)** or equivalent (money in)
- **Balance/Balance (N)** (optional but helpful)

System automatically:
- Handles multiple table formats
- Maps varying column names
- Converts to numeric types
- Fills missing values
- Extracts from all pages

---

## Project Structure

```
credit-risk-markov-system/
├── README.md                          (This file)
├── TECHNICAL_DOCUMENTATION.md         (Math & architecture)
├── IMPROVEMENTS.md                    (All fixes & changes)
├── QUICK_REFERENCE.md                 (User guide)
├── requirements.txt
├── run.py                            (Start everything)
│
├── backend/
│   ├── app.py                        (FastAPI server)
│   ├── test_parser.py                (Test suite)
│   ├── models/
│   │   ├── markov.py                 (Transition matrix builder)
│   │   └── state_model.py            (State classifier)
│   ├── utils/
│   │   ├── parser.py                 (PDF extraction)
│   │   ├── cleaner.py                (Data cleaning)
│   │   └── features.py               (Feature engineering)
│   └── data/                         (Sample PDFs)
│
└── frontend/
    └── index.html                     (Professional dashboard)
```

---

## Technology Stack

### Backend
- **FastAPI**: REST API framework
- **Python 3.13+**: Core language
- **NumPy**: Matrix operations (Markov)
- **Pandas**: Data analysis & aggregation
- **pdfplumber**: PDF table extraction

### Frontend
- **HTML5**: Modern semantic markup
- **CSS3**: Responsive design with gradients
- **JavaScript**: Interactive visualizations
- **Chart.js**: Professional charts & graphs

---

## Error Handling

The system validates data at every step:
- ✓ PDF must contain extractable table data
- ✓ Minimum 2 months of history required (for state transitions)
- ✓ Required columns: date, debit, credit
- ✓ Clear error messages for invalid data
- ✓ Temporary files cleaned up after processing

---

## Example Workflow

1. **Export** bank statement as PDF from your bank
2. **Upload** via the web interface
3. **View** Markov analysis:
   - Current financial state
   - Transition matrix (what states you could move to)
   - Credit score & approved limit
   - Monthly cash flow trend
   - State trajectory visualization

4. **Interpret Results**:
   - High default probability? Need to improve savings
   - Excellent state? Good credit terms available
   - Watch the monthly trends for financial health patterns

---

## Understanding Results

### Good Signs
- Default Probability < 5%
- Credit Score > 700
- Savings Rate > 40%
- Staying in Good/Excellent states

### Warning Signs
- Default Probability > 20%
- Credit Score < 600
- Savings Rate < 10%
- Frequent transitions to Risky/Default

### What Each Metric Means

**Current State**: Your financial health classification right now

**Credit Score**: 300-800 scale reflecting creditworthiness (higher = better)

**Default Probability**: Likelihood of entering Default state next month (0-100%)

**Credit Limit**: How much credit you can receive based on income & risk

**Savings Rate**: What % of income you're saving (target: >40%)

---

## Technical Notes

- **Markov Property**: Future depends only on present, not history
- **Time-Homogeneous**: Transition probabilities don't change with time
- **Empirical Estimation**: Matrix built from observed transitions in your data
- **One-Step Prediction**: Formula uses matrix row matching current state

For academic details, see `TECHNICAL_DOCUMENTATION.md` and `QUICK_REFERENCE.md`

---

## Recent Improvements

✅ Clean, professional UI without emoji symbols
✅ Markov transition matrix visualization (heatmap)
✅ State sequence timeline chart
✅ Fixed mathematical calculations
✅ Proper error handling & validation
✅ Responsive design for mobile
✅ Complete documentation

See `IMPROVEMENTS.md` for full changelog.

---

## Testing

Run the test suite to validate the pipeline:
```bash
python backend/test_parser.py
```

Expected output shows:
- Extracted features with savings ratios
- Transition matrix from state sequence
- Current state prediction
- Next-state probability distribution

---

## License & Attribution

**Purpose**: Educational - Stochastic Processes course project  
**Subject**: Credit Default Risk Analysis using Markov Chains  
**Date**: April 2026

---

## Support

For issues or questions:
1. Check `QUICK_REFERENCE.md` for common questions
2. Review `TECHNICAL_DOCUMENTATION.md` for math details
3. Look at `IMPROVEMENTS.md` for known fixes
4. Run `python backend/test_parser.py` to validate setup

---

**Status**: ✅ Production Ready | **Last Updated**: April 17, 2026
    "Default": 0.05
  },
  "features": [...]
}
```

## 🔧 Data Requirements

PDF must contain table with columns:
- `Date` - Transaction date
- `Debit/Debit (N)` - Money out
- `Credit/Credit (N)` - Money in
- `Balance/Balance (N)` - Account balance

Alternative column names supported with automatic mapping.

## 📈 Sample Workflow

1. Export bank statement as PDF
2. Upload via web UI
3. View results:
   - Current financial state
   - Next period probabilities
   - Credit score & limit
   - Monthly cash flow chart
   - State transition forecast

## 🐛 Error Handling

- Missing required columns → Detailed error message
- Empty data after cleaning → Validation error
- < 2 months of history → Rejected (need trends)
- Invalid PDF → Graceful error response

## 🔐 Security Notes

- CORS enabled for localhost development
- PDF temporarily stored, deleted after analysis
- No data persistence by default
- All processing server-side

## 🚀 Future Enhancements

- Multiple PDF uploads for comparison
- Export analysis reports
- User authentication & data storage
- Advanced ML predictions beyond Markov
- Real-time portfolio monitoring
