from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.utils.parser import parse_pdf
from backend.utils.cleaner import clean_data
from backend.utils.features import create_features
from backend.models.state_model import assign_state
from backend.models.markov import build_transition_matrix, predict_next

import numpy as np

app = FastAPI()

# Allow frontend access
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

    with open(path, "wb") as f:
        f.write(await file.read())

    df = parse_pdf(path)
    df = clean_data(df)

    features = create_features(df)
    features['state'] = features.apply(assign_state, axis=1)

    states = features['state'].tolist()
    matrix = build_transition_matrix(states)

    current_state = states[-1]
    prediction = predict_next(matrix, current_state)

    # ---- NEW DASHBOARD LOGIC ----
    avg_income = features['income'].mean()
    avg_expense = features['expense'].mean()
    savings_rate = (avg_income - avg_expense) / (avg_income + 1)

    credit_limit = avg_income * 0.3
    default_prob = prediction.get("Default", 0.05)

    # credit score logic
    score = 800
    if current_state == "Good":
        score = 700
    elif current_state == "Risky":
        score = 600
    elif current_state == "Default":
        score = 400

    # expected time to default
    expected_months = int(1 / (default_prob + 0.01))

    return {
        "current_state": current_state,
        "prediction": prediction,
        "credit_score": score,
        "default_probability": default_prob,
        "credit_limit": credit_limit,
        "expected_months": expected_months,
        "avg_income": avg_income,
        "avg_expense": avg_expense,
        "savings_rate": savings_rate,
        "features": features.to_dict(orient="records")
    }