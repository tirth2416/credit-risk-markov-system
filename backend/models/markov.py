import pandas as pd

def build_transition_matrix(states):
    unique_states = list(set(states))

    matrix = pd.DataFrame(0, index=unique_states, columns=unique_states)

    for i in range(len(states)-1):
        matrix.loc[states[i], states[i+1]] += 1

    matrix = matrix.div(matrix.sum(axis=1), axis=0).fillna(0)
    return matrix

def predict_next(matrix, current_state):
    return matrix.loc[current_state].to_dict()