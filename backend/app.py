from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from utils.parser import parse_pdf
from utils.cleaner import clean_data
from utils.features import create_features
from models.state_model import assign_state
from models.markov import build_transition_matrix, predict_next

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

    return {
        "current_state": current_state,
        "prediction": prediction,
        "states": states
    }