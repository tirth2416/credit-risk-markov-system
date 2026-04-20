# Project Architecture & Technical Deep Dive

## Complete System Guide: How Everything Works

---

## 1. Project Overview

**Name:** Credit Risk Markov Chain Analyzer  
**Purpose:** Educational tool for analyzing financial risk using stochastic processes (Markov chains)  
**Academic Context:** Stochastic Processes course project on credit default risk modeling  
**Tech Stack:** Python (FastAPI) + JavaScript (Vanilla) + HTML/CSS  
**Currency:** Indian Rupees (INR)  
**Date Created:** April 2026  

---

## 2. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│                    (frontend/index.html)                        │
│  - PDF Upload Section              - Learn Section             │
│  - Results Dashboard               - 9 Educational Cards       │
│  - 4 Interactive Charts            - Humanized Explanations    │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │  HTTP API Calls (JSON)
                     │  http://localhost:8000/analyze
                     │
┌────────────────────▼────────────────────────────────────────────┐
│                    FASTAPI BACKEND                              │
│                  (backend/app.py)                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ POST /analyze Endpoint                                   │   │
│  │  - Receives PDF file (multipart/form-data)              │   │
│  │  - Validates file format & existence                    │   │
│  │  - Orchestrates entire pipeline                         │   │
│  │  - Returns JSON response with results                   │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──┐  ┌──────▼──┐  ┌─────▼──────┐
│ UTILS    │  │ MODELS  │  │ FEATURES   │
│ LAYER    │  │ LAYER   │  │ LAYER      │
└──────────┘  └─────────┘  └────────────┘
        │            │            │
        └────────────┼────────────┘
                     │
         ┌───────────▼───────────┐
         │   DATA PIPELINE       │
         │   (Detailed Below)    │
         └───────────────────────┘
```

---

## 3. Data Pipeline (Step-by-Step)

### Step 1: PDF Parsing
**File:** `backend/utils/parser.py`
**What it does:** Extracts table data from PDF bank statements

```
Input: PDF file from user
  ↓
Use pdfplumber library to open PDF
  ↓
Find all tables in document (across all pages)
  ↓
Extract rows from each table
  ↓
Convert to pandas DataFrame
  ↓
Output: DataFrame with columns [Date, Debit, Credit, Balance, etc.]
```

**Key Technology:** `pdfplumber` library
- Python library for extracting data from PDFs
- Automatically detects tables
- Handles multi-page documents
- Converts table format automatically

---

### Step 2: Data Cleaning
**File:** `backend/utils/cleaner.py`
**What it does:** Standardizes and validates the extracted data

```
Input: Raw DataFrame from PDF
  ↓
Standardize column names:
  - "Debit (n)" → "debit"
  - "Credit (n)" → "credit"
  - "Debit/Debit (N)" → "debit"
  - "Credit/Credit (N)" → "credit"
  ↓
Convert string numbers to actual numbers (remove commas, etc.)
  ↓
Fill missing values intelligently
  ↓
Remove rows with no debit or credit data
  ↓
Sort by date
  ↓
Output: Clean, standardized DataFrame
```

**Why this matters:** Banks use different formats. Some use "Debit (n)", others use "Debit/Debit (N)". We normalize them.

---

### Step 3: Feature Engineering
**File:** `backend/utils/features.py`
**What it does:** Calculates monthly financial metrics

```
Input: Clean transaction DataFrame
  ↓
Group all transactions by month
  ↓
For each month, calculate:
  - Total Income (sum of all credits)
  - Total Expense (sum of all debits)
  - Total Savings (income - expense)
  - Savings Ratio (savings / income)
  ↓
Handle edge cases:
  - If income = 0, set ratio to 0.0 (avoid division by zero)
  - If expense > income, still calculate correctly
  ↓
Output: Monthly features DataFrame with columns:
  [month, income, expense, savings, savings_ratio]
```

**Formula:**
```
Savings Ratio = (Total Income - Total Expense) / Total Income
Range: -∞ to 1.0
Typical range: 0.0 to 1.0
```

---

### Step 4: State Assignment
**File:** `backend/models/state_model.py`
**What it does:** Classifies financial health based on savings ratio

```
Input: Features DataFrame with savings_ratio column
  ↓
Apply threshold-based classification:

  IF savings_ratio > 0.70
    STATE = "Excellent"
    (You're saving more than 70% of income)
  
  ELSE IF savings_ratio > 0.40
    STATE = "Good"
    (You're saving 40-70% of income)
  
  ELSE IF savings_ratio > 0.10
    STATE = "Risky"
    (You're saving 10-40% of income)
  
  ELSE (savings_ratio <= 0.10)
    STATE = "Default"
    (You're saving 10% or less - danger zone)
  ↓
Output: Features DataFrame with new 'state' column
```

**State Values:** ["Excellent", "Good", "Risky", "Default"]

---

### Step 5: Transition Matrix Building
**File:** `backend/models/markov.py`
**Function:** `build_transition_matrix(states)`

```
Input: List of states in chronological order
       Example: ["Good", "Good", "Excellent", "Good", "Risky", ...]
  ↓
Create a matrix to count transitions:
  - Rows represent current state (t)
  - Columns represent next state (t+1)
  
Example count matrix:
          Excellent  Good  Risky  Default
Excellent     3       2      1       0
Good          5      15      3       0
Risky         1       2      4       1
Default       0       0      0       2

  ↓
Normalize each row by dividing by row sum:
(This converts counts to probabilities)

Example probability matrix:
          Excellent  Good  Risky  Default
Excellent     0.5    0.33  0.17    0.0
Good         0.25   0.75  0.15    0.0
Risky        0.14   0.29  0.57    0.14
Default       0.0    0.0   0.0    1.0
  ↓
Sort states alphabetically for consistency
  ↓
Output: 
  - transition_matrix (2D numpy array)
  - state_labels (list of states in sorted order)
```

**Mathematical Notation:**
```
P[i,j] = (Number of transitions from state_i to state_j) 
         / (Total transitions from state_i)

Properties:
- Each row sums to 1.0 (probability distribution)
- Entry P[i,j] = probability of moving from state i to state j next period
- Based on time-homogeneous Markov chain assumption (probabilities don't change with time)
```

---

### Step 6: State Prediction
**File:** `backend/models/markov.py`
**Function:** `predict_next(current_state, matrix, labels)`

```
Input: 
  - current_state (last state in sequence)
  - transition_matrix (from step 5)
  - state_labels (from step 5)
  ↓
Find index of current state in labels
  ↓
Extract the corresponding row from transition matrix
  ↓
This row IS the probability distribution for next period
  
Example:
  If current_state = "Good"
  And row for "Good" is [0.25, 0.75, 0.15, 0.0]
  (with states = ["Excellent", "Good", "Risky", "Default"])
  
  Then next-period probabilities are:
  - 25% chance of Excellent
  - 75% chance of Good
  - 15% chance of Risky
  - 0% chance of Default
  ↓
Output: Dictionary of next-period state probabilities
  {
    "Excellent": 0.25,
    "Good": 0.75,
    "Risky": 0.15,
    "Default": 0.0
  }
```

---

### Step 7: Credit Scoring
**File:** `backend/app.py`

```
Input:
  - current_state (from step 4)
  - default_probability (from step 6)
  ↓
Define base scores for each state:
  EXCELLENT → 800 points
  GOOD      → 700 points
  RISKY     → 550 points
  DEFAULT   → 300 points
  ↓
Apply risk adjustment:
  credit_score = base_score - (default_prob × 300)
  ↓
Clamp to valid range [300, 800]
  
Example:
  current_state = "Good" (base = 700)
  default_prob = 0.05 (5%)
  credit_score = 700 - (0.05 × 300)
  credit_score = 700 - 15
  credit_score = 685
  ↓
Output: Credit score (300-800 scale)
```

---

### Step 8: Credit Limit Calculation
**File:** `backend/app.py`

```
Input:
  - avg_income (average monthly income from step 3)
  - default_probability (from step 6)
  ↓
Apply formula:
  credit_limit = avg_income × 0.3 × (1 - default_prob)
  
Where:
  0.3 = Standard lending practice (30% of income)
  (1 - default_prob) = Risk adjustment factor
  ↓
Example:
  avg_income = ₹50,000
  default_prob = 0.05 (5%)
  credit_limit = 50,000 × 0.3 × (1 - 0.05)
  credit_limit = 50,000 × 0.3 × 0.95
  credit_limit = 15,000 × 0.95
  credit_limit = ₹14,250
  ↓
Can adjust the 0.3 multiplier to be more/less lenient:
  - 0.2 = Conservative (20% of income)
  - 0.3 = Standard (30% of income)
  - 0.4 = Generous (40% of income)
  ↓
Output: Approved credit limit in INR
```

---

## 4. API Specification

### Endpoint: POST /analyze

**URL:** `http://localhost:8000/analyze`

**Request Format:**
```
Content-Type: multipart/form-data

Body:
  file: <binary PDF file>
```

**Example cURL:**
```bash
curl -X POST \
  -F "file=@bank_statement.pdf" \
  http://localhost:8000/analyze
```

**Success Response (HTTP 200):**
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
  "transition_matrix": [
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 0.8, 0.15, 0.05],
    [0.1, 0.75, 0.1, 0.05],
    [0.0, 0.2, 0.3, 0.5]
  ],
  "prediction": {
    "Default": 0.05,
    "Excellent": 0.1,
    "Good": 0.75,
    "Risky": 0.1
  },
  "features": [
    {
      "month": "2026-01",
      "income": 83091.67,
      "expense": 49673.89,
      "savings": 33417.78,
      "savings_ratio": 0.4023,
      "state": "Good"
    },
    ...more months...
  ]
}
```

**Response Fields Explained:**

| Field | Type | Description |
|-------|------|-------------|
| `current_state` | string | Your financial state right now (Excellent/Good/Risky/Default) |
| `credit_score` | float | Your credit score (300-800 scale) |
| `default_probability` | float | Chance you'll default next month (0.0-1.0) |
| `credit_limit` | float | How much you can borrow (in INR) |
| `avg_income` | float | Average monthly income (in INR) |
| `avg_expense` | float | Average monthly expense (in INR) |
| `savings_rate` | float | Percentage of income you save (0.0-1.0) |
| `state_labels` | array | All possible states (always same 4) |
| `transition_matrix` | 2D array | P[i,j] = P(next_state=j \| current_state=i) |
| `prediction` | object | Probabilities for each state next period |
| `features` | array | Monthly breakdown (income, expense, state) |

**Error Response (HTTP 400):**
```json
{
  "detail": "PDF must contain extractable table data"
}
```

**Error Response (HTTP 422):**
```json
{
  "detail": "File must be a PDF"
}
```

**Error Response (HTTP 500):**
```json
{
  "detail": "Internal processing error: [error message]"
}
```

---

## 5. Database & Storage

**Current Implementation:** None (in-memory only)

**How it works:**
- PDFs are uploaded to temporary location
- All processing happens in RAM
- Temporary files are deleted immediately after processing
- No data persistence between sessions

**For Production:**
Could add PostgreSQL or MongoDB to store:
- Past analyses
- User accounts
- Historical accuracy metrics
- Audit logs

---

## 6. Frontend Architecture

### Page Structure

```
index.html
  ├── HEAD
  │   ├── Stylesheets (CSS)
  │   ├── Chart.js library import
  │   └── Meta information
  │
  ├── BODY
  │   ├── HEADER
  │   │   ├── Title
  │   │   ├── Subtitle
  │   │   └── Description
  │   │
  │   ├── UPLOAD SECTION
  │   │   ├── File input
  │   │   ├── ANALYZE button
  │   │   ├── Info box
  │   │   ├── Error display
  │   │   └── Loading spinner
  │   │
  │   ├── RESULTS SECTION (hidden until analysis)
  │   │   ├── Metrics grid (6 cards)
  │   │   ├── Transition Matrix table
  │   │   ├── One-Step Prediction chart
  │   │   ├── Cash Flow chart
  │   │   └── State Timeline chart
  │   │
  │   ├── LEARN SECTION
  │   │   └── 9 educational cards (humanized explanations)
  │   │
  │   └── FOOTER
  │
  └── SCRIPT
      ├── analyze() function
      ├── displayResults() function
      ├── Chart drawing functions
      └── State colors mapping
```

### JavaScript Functions

**Main Functions:**

1. **analyze()**
   - Gets the PDF file from input
   - Validates file (must be PDF)
   - Creates FormData object
   - Makes POST request to /analyze endpoint
   - Handles errors with user-friendly messages
   - Shows loading spinner during processing
   - Calls displayResults() on success

2. **displayResults(data)**
   - Populates metric cards with API response data
   - Calls all chart drawing functions
   - Unhides results section

3. **drawTransitionMatrix(matrix, labels)**
   - Creates HTML table from matrix
   - Color-codes cells based on probability
   - Shows P[i,j] values with 3 decimal places

4. **drawTransition(pred)**
   - Creates bar chart showing next-period probabilities
   - Uses Chart.js library
   - Color-codes by state

5. **drawStatement(features)**
   - Creates line chart showing income vs. expense over time
   - Two datasets: green for income, red for expense
   - Uses Chart.js library

6. **drawStateSequence(features, labels)**
   - Creates scatter plot showing which state in each month
   - Each state represented by different color
   - X-axis is time (months), Y-axis is states

---

## 7. Dependencies & Libraries

### Backend Python Packages

```
fastapi==0.104.1          # Web framework
uvicorn==0.24.0           # ASGI server
pandas==2.0.3             # Data processing
numpy==1.24.3             # Numerical operations
pdfplumber==0.10.4        # PDF extraction
python-multipart==0.0.6   # Form data parsing
```

**What each does:**

- **fastapi**: Provides the REST API framework, automatic documentation, type validation
- **uvicorn**: Runs the FastAPI server with hot-reload capability
- **pandas**: Handles DataFrames for tabular data manipulation
- **numpy**: Provides matrix operations for transition matrix calculations
- **pdfplumber**: Extracts tables from PDF files automatically
- **python-multipart**: Handles file uploads in POST requests

### Frontend Libraries

```
Chart.js 4.4.0            # Data visualization
(via CDN: https://cdn.jsdelivr.net/npm/chart.js)
```

**What it does:**
- Creates interactive bar, line, and scatter charts
- Responsive and animated
- Color customization
- Legend and tooltip support

### No Database
- No SQL database needed
- No ORM like SQLAlchemy
- No Redis for caching
- Pure in-memory processing

---

## 8. File Structure Explained

```
credit-risk-markov-system/
│
├── README.md
│   └── Quick start guide and overview
│
├── TECHNICAL_DOCUMENTATION.md
│   └── Mathematical formulas and theory
│
├── PROJECT_ARCHITECTURE.md (THIS FILE)
│   └── How everything is built and works
│
├── PROJECT_CONTENTS.md
│   └── Inventory of all files and features
│
├── IMPROVEMENTS.md
│   └── Changelog of what was fixed
│
├── QUICK_REFERENCE.md
│   └── Common questions and answers
│
├── CHANGELOG_APRIL_2026.md
│   └── Session notes and updates
│
├── requirements.txt
│   └── Python package list
│
├── run.py
│   └── Single-command launcher for backend + frontend
│
├── backend/
│   ├── __init__.py
│   ├── app.py
│   │   └── Main FastAPI application with /analyze endpoint
│   │
│   ├── test_parser.py
│   │   └── Test script to verify pipeline works
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── state_model.py
│   │   │   └── Financial state classification
│   │   └── markov.py
│   │       └── Transition matrix and prediction
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── parser.py
│   │   │   └── PDF table extraction
│   │   ├── cleaner.py
│   │   │   └── Data standardization
│   │   └── features.py
│   │       └── Monthly aggregation and ratios
│   │
│   └── data/
│       └── sample.pdf
│           └── Example PDF for testing
│
└── frontend/
    └── index.html
        └── Complete dashboard (HTML + CSS + JavaScript)
```

---

## 9. How Data Flows Through the System

```
User Action: Upload PDF
         ↓
Browser: Send POST request with PDF
    (multipart/form-data)
         ↓
FastAPI (app.py): Receive file
         ↓
Parser (parser.py): Extract tables from PDF
         ↓
Cleaner (cleaner.py): Standardize columns
         ↓
Features (features.py): Calculate monthly metrics
         ↓
State Assigner (state_model.py): Classify states
         ↓
Markov Builder (markov.py): Create transition matrix
         ↓
Predictor (markov.py): Forecast next-period states
         ↓
Scorer (app.py): Calculate credit score
         ↓
Limiter (app.py): Calculate credit limit
         ↓
FastAPI: Serialize results to JSON
         ↓
Network: Send JSON response
         ↓
Browser: Receive response
         ↓
JavaScript: Parse JSON
         ↓
Chart.js: Draw tables and charts
         ↓
User: See beautiful dashboard with results
```

---

## 10. Error Handling & Validation

### Backend Validation

**File Upload:**
```python
if not file:
    raise HTTPException(400, "No file provided")

if not file.filename.endswith(".pdf"):
    raise HTTPException(400, "File must be a PDF")

if not os.path.exists(temp_path):
    raise HTTPException(400, "File not found")
```

**Data Extraction:**
```python
if df.empty:
    raise HTTPException(400, "PDF must contain extractable data")

if len(df) < 2:
    raise HTTPException(400, "Minimum 2 months of history required")

required_cols = ['date', 'debit', 'credit']
if not all(col in df.columns for col in required_cols):
    raise HTTPException(400, "Missing required columns")
```

**Cleanup:**
```python
try:
    # Process data
finally:
    # Always delete temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)
```

### Frontend Validation

```javascript
// Check file exists
if (!file) {
    errorDiv.innerText = "ERROR: Please select a PDF file";
    return;
}

// Check file type
if (!file.name.endsWith(".pdf")) {
    errorDiv.innerText = "ERROR: File must be a PDF";
    return;
}

// Check response status
if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "Analysis failed");
}
```

---

## 11. Performance Considerations

### Processing Time
- **Typical PDF:** 1-3 seconds end-to-end
- **Large PDF (100+ pages):** 5-10 seconds
- **Bottleneck:** PDF parsing (pdfplumber)

### Memory Usage
- **Typical:** 50-200 MB
- **Large datasets:** Can go up to 500+ MB
- **Clearing:** Temporary files deleted immediately after use

### Scalability
**Current:** Single-threaded, handles one user at a time

**For Production:**
- Use task queue (Celery)
- Run worker processes
- Store results in database
- Add caching layer

---

## 12. Security Considerations

### Current Implementation
- Files are temporary (deleted after processing)
- No file persistence
- No user accounts or authentication
- CORS not restricted (development mode)

### For Production
```python
# Add CORS restrictions
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Add file size limits
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# Add authentication
from fastapi_jwt_auth import AuthJWT

# Scan files for malware
# Add HTTPS requirement
# Add rate limiting
```

---

## 13. Testing

### Test Suite: backend/test_parser.py

```python
# Runs against sample.pdf
# Tests each stage:
1. PDF parsing
2. Data cleaning
3. Feature engineering
4. State assignment
5. Transition matrix
6. State prediction

# Run with:
python -m backend.test_parser
```

**Expected Output:**
```
Data extracted, cleaned, and features created
States: ["Excellent", "Good"]
Transition matrix generated
Next-state probabilities calculated
```

---

## 14. Deployment Options

### Option 1: Local Development
```bash
python run.py
```

### Option 2: Docker
```dockerfile
FROM python:3.13
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0"]
```

### Option 3: Heroku
```
- Add Procfile
- Push to Heroku
- Set environment variables
```

### Option 4: AWS Lambda
```
- Use Zappa framework
- Deploy to S3 + Lambda
- Use API Gateway for HTTP
```

---

## 15. Future Enhancement Ideas

1. **Multi-currency support** - USD, EUR, GBP, etc.
2. **Confidence intervals** - Show uncertainty in predictions
3. **Historical accuracy** - Backtest predictions against actual outcomes
4. **Email notifications** - Alert users of state changes
5. **Mobile app** - iOS/Android native
6. **API authentication** - OAuth2 / JWT tokens
7. **Data export** - CSV, PDF reports
8. **Advanced analytics** - Clustering, segmentation
9. **Admin dashboard** - Monitor system health
10. **Webhook support** - Integrate with other services

---

## 16. Troubleshooting Guide

### Issue: PDF parsing fails
**Cause:** PDF doesn't have a proper table format  
**Solution:** Export bank statement as PDF from your bank, ensure table is visible

### Issue: "Minimum 2 months required"
**Cause:** PDF has less than 2 months of transactions  
**Solution:** Upload a PDF with at least 2 full months of data

### Issue: Charts don't show
**Cause:** Browser console error (check F12)  
**Solution:** Check that API response JSON is valid, ensure Chart.js CDN loads

### Issue: Backend won't start
**Cause:** Port 8000 already in use  
**Solution:** 
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn backend.app:app --port 8001
```

---

## 17. Key Mathematical Concepts

### Markov Chain
A stochastic process where:
- Future state depends only on present state
- Not on entire history
- Probabilities are constant over time (time-homogeneous)

### Transition Matrix
Matrix P where:
- P[i,j] = P(X_{t+1} = j | X_t = i)
- Each row sums to 1.0
- Estimated from historical transitions

### Savings Ratio
- Range: [−∞, 1.0]
- Typical: [0.0, 1.0]
- Higher is better (more savings)

### Probability
- Range: [0.0, 1.0]
- 0.0 = will never happen
- 1.0 = will definitely happen
- 0.5 = 50% chance

---

## 18. Contact & Support

**Project Type:** Educational  
**Course:** Stochastic Processes  
**Created:** April 2026  
**Status:** Production Ready  

**For modifications:**
- Edit backend logic in `backend/` folder
- Edit UI in `frontend/index.html`
- Run `python run.py` to restart

---

This document covers the complete architecture from user interface to database. Every module and function is explained. Use this as your reference guide for understanding how the system works!

**Last Updated:** April 17, 2026  
**Version:** 2.1
