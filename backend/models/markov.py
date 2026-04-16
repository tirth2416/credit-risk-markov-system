import pandas as pd

def build_transition_matrix(states):
    unique_states = list(set(states))
    matrix = {s: {s2: 0 for s2 in unique_states} for s in unique_states}

    for i in range(len(states) - 1):
        matrix[states[i]][states[i+1]] += 1

    # normalize
    for s in matrix:
        total = sum(matrix[s].values())
        if total > 0:
            for s2 in matrix[s]:
                matrix[s][s2] /= total

    return matrix

def predict_next(matrix, current_state):
    return matrix.get(current_state, {})