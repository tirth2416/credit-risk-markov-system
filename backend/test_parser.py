from utils.parser import parse_pdf
from utils.cleaner import clean_data
from utils.features import create_features
from models.state_model import assign_state
from models.markov import build_transition_matrix, predict_next

df = parse_pdf("data/sample.pdf")
df = clean_data(df)

features = create_features(df)

features['state'] = features.apply(assign_state, axis=1)

print("\nFEATURES:\n", features)

states = features['state'].tolist()

matrix = build_transition_matrix(states)

print("\nTRANSITION MATRIX:\n", matrix)

current_state = states[-1]

prediction = predict_next(matrix, current_state)

print("\nCURRENT STATE:", current_state)
print("\nNEXT STATE PROBABILITY:", prediction)