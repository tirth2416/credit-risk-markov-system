from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

from backend.utils.parser import parse_pdf
from backend.utils.cleaner import clean_data
from backend.utils.features import create_features
from backend.models.state_model import assign_state
from backend.models.markov import build_transition_matrix, predict_next

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Backend running"}

@app.post("/analyze")
async def analyze(file: UploadFile):
    path = "temp.pdf"
    try:
        with open(path, "wb") as f:
            f.write(await file.read())

        df = parse_pdf(path)
        if df is None or df.empty:
            raise HTTPException(status_code=400, detail="PDF contains no data")

        df = clean_data(df)
        if df.empty:
            raise HTTPException(status_code=400, detail="No valid data after cleaning")

        features = create_features(df)
        if features.empty or len(features) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 months of data")

        if 'savings_ratio' not in features.columns:
            raise HTTPException(status_code=400, detail="Missing savings_ratio column")

        features['state'] = features.apply(assign_state, axis=1)

        states = features['state'].tolist()
        matrix, state_labels = build_transition_matrix(states)

        current_state = states[-1]
        prediction = predict_next(matrix, current_state, state_labels)

        avg_income = features['income'].mean()
        avg_expense = features['expense'].mean()
        
        # Savings rate: proportion of income saved
        if avg_income > 0:
            savings_rate = (avg_income - avg_expense) / avg_income
        else:
            savings_rate = 0.0

        # Credit Score Calculation (based on financial health and risk)
        default_prob = prediction.get("Default", 0)
        base_scores = {"Excellent": 800, "Good": 700, "Risky": 550, "Default": 300}
        base_score = base_scores.get(current_state, 650)
        # Penalize based on default probability
        risk_adjustment = default_prob * 300
        credit_score = max(300, base_score - risk_adjustment)
        
        # Credit Limit: based on income and risk adjusted
        if default_prob < 1.0:
            credit_limit = max(0, avg_income * 0.3 * (1 - default_prob))
        else:
            credit_limit = 0
            
        # Expected time to default (in months)
        expected_months = int(1 / (default_prob + 0.01)) if default_prob > 0 else 999

        # Convert matrix to list for JSON serialization
        matrix_list = matrix.tolist()

        return {
            "current_state": current_state,
            "prediction": prediction,
            "credit_score": round(credit_score, 2),
            "default_probability": round(default_prob, 4),
            "credit_limit": round(credit_limit, 2),
            "expected_months": expected_months,
            "avg_income": round(avg_income, 2),
            "avg_expense": round(avg_expense, 2),
            "savings_rate": round(savings_rate, 4),
            "state_labels": state_labels,
            "transition_matrix": matrix_list,
            "features": features.to_dict(orient="records")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Analysis failed: {str(e)}")
    finally:
        if os.path.exists(path):
            os.remove(path)