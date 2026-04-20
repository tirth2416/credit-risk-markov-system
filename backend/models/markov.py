import numpy as np

def build_transition_matrix(states):
    """Build Markov transition probability matrix from observable state sequence.
    
    A Markov chain is defined by: x_{t+1} = f(x_t) stochastically
    The transition matrix M where M[i,j] = P(X_{t+1} = state_j | X_t = state_i)
    
    Each row sums to 1 (forms a probability distribution over next states).
    This matrix is estimated from historical state transitions in the data.
    
    Args:
        states: Sequence of observed states over time
        
    Returns:
        tuple: (transition_matrix, state_labels) where matrix is normalized probabilities
    """
    # Ensure consistent state ordering (alphabetical for reproducibility)
    unique_states = sorted(list(set(states)))
    state_to_idx = {s: i for i, s in enumerate(unique_states)}

    # Count transitions: count[i,j] = number of times we went from state_i to state_j
    count_matrix = np.zeros((len(unique_states), len(unique_states)))

    for t in range(len(states) - 1):
        current_idx = state_to_idx[states[t]]
        next_idx = state_to_idx[states[t + 1]]
        count_matrix[current_idx, next_idx] += 1

    # Normalize each row to get probability distributions
    # P[i,j] = count[i,j] / sum_k(count[i,k])
    transition_matrix = np.zeros_like(count_matrix, dtype=float)
    for i in range(len(unique_states)):
        row_sum = count_matrix[i].sum()
        if row_sum > 0:
            transition_matrix[i] = count_matrix[i] / row_sum
        else:
            # If no observed transitions from state i, assume self-loop
            transition_matrix[i, i] = 1.0

    return transition_matrix, unique_states


def predict_next(matrix, current_state, state_labels):
    """Predict next state probabilities using Markov transition matrix.
    
    One-step ahead prediction: P(X_{t+1} = j | X_t = i) = M[i,j]
    
    Args:
        matrix: Transition probability matrix
        current_state: Current financial state
        state_labels: List of all possible states (sorted)
    
    Returns:
        Dict mapping each state to one-step ahead transition probability
    """
    if current_state not in state_labels:
        return {current_state: 1.0}
    
    idx = state_labels.index(current_state)
    probabilities = matrix[idx]
    
    return {state: float(prob) for state, prob in zip(state_labels, probabilities)}