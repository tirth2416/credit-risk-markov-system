from backend.utils.parser import parse_pdf
from backend.utils.cleaner import clean_data
from backend.utils.features import create_features
from backend.models.state_model import assign_state
from backend.models.markov import build_transition_matrix, predict_next

df = parse_pdf("backend/data/sample.pdf")
df = clean_data(df)

features = create_features(df)
features['state'] = features.apply(assign_state, axis=1)

print("\nFEATURES:\n", features)

states = features['state'].tolist()

matrix, state_labels = build_transition_matrix(states)

print("\nTRANSITION MATRIX:\n", matrix)
print("\nSTATE LABELS:", state_labels)

current_state = states[-1]
prediction = predict_next(matrix, current_state, state_labels)

print("\nCURRENT STATE:", current_state)
print("\nNEXT STATE PREDICTION:", prediction)