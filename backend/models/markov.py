def build_transition_matrix(states):
    matrix = {}

    for i in range(len(states) - 1):
        curr = states[i]
        nxt = states[i + 1]

        if curr not in matrix:
            matrix[curr] = {}

        if nxt not in matrix[curr]:
            matrix[curr][nxt] = 0

        matrix[curr][nxt] += 1

    # normalize
    for curr in matrix:
        total = sum(matrix[curr].values())
        for nxt in matrix[curr]:
            matrix[curr][nxt] /= total

    return matrix


def predict_next(matrix, current_state):
    if current_state not in matrix:
        return {}

    return matrix[current_state]