import numpy as np
from itertools import combinations, product


ZERO = np.array([1, 0])
ONE = np.array([0,1])
X = np.array([[0, 1], [1, 0]])
Y = np.array([[0, -1j],[1j, 0]])
Z = np.array([[1, 0], [0, -1]])
PAULIS = np.array([np.eye(2), X, Y, Z])


def bell_states():
    bell_states = {
        'PHI_PLUS': np.kron(ZERO, ZERO) + np.kron(ONE, ONE),
        'PHI_MINUS': np.kron(ZERO, ZERO) - np.kron(ONE, ONE),
        'PSI_PLUS': np.kron(ZERO, ONE) + np.kron(ONE, ZERO),
        'PSI_MINUS': np.kron(ZERO, ONE) - np.kron(ONE, ZERO)
    }
    bell_states = {k: v * 1/np.sqrt(2) for k, v in bell_states.items()}
    return bell_states
BELL_STATES = bell_states()


# Returns W-state of N qubits
def W(N):
    ret_state = np.zeros(2**N)
    for basis in np.identity(N):
        for index, entry in enumerate(basis):
            state = ZERO if entry == 0 else ONE
            if(index == 0):
                kron_state = ZERO if entry == 0 else ONE
            else:
                kron_state = np.kron(kron_state, state)

        ret_state += kron_state
    return ret_state/ np.sqrt(N)


# Returns GHZ-state of N qubits
def GHZ(N):
    ret_state = np.zeros(2**N)
    ret_state[0] = ret_state[-1] = 1
    return ret_state / np.sqrt(2)


# Returns the operator specified via tensor notation
# INPUTS
#     N - Number of qubits
#     nonidentities - List of tuples specifying qubit number (indexed at 0) in ascending order and Pauli operator 
#         Example: [(0,X),(2,'Y')]
def operator_from_sparse_pauli(N, nonidentities):
    tup = lambda value, tuples: next(((first, second) for first, second in tuples if first == value), 0)
    
    for iter in range(N):
        result = tup(iter, nonidentities)
        if(iter == 0):
            ret_arr = np.identity(2) if (result == 0) else result[1]
        else:
            ret_arr = np.kron(ret_arr, np.identity(2)) if result == 0 else np.kron(ret_arr, result[1])

    return ret_arr


# Generates a list of the subset of operator bases over N qubits of weight less than or equal to k
# It is a tensor product of N operators, each of which is in {I, X, Y, Z} such that at most k are not I
# INPUTS
#     N - Number of qubits
#     k - Maximum locality of Pauli operators acting upon qubits
def Paulis_N_k(N, k):
    retset = []
    retset_verbose = []
    retset.append(np.eye(2**N))
    retset_verbose.append([])
    for k_index in range(k):
        combos = combinations(range(N), k_index+1)
        sigmas = [p for p in product([X,Y,Z], repeat=(k_index+1))]
        sigmas_verbose = [p for p in product(['X','Y','Z'], repeat=(k_index+1))]
        for c in combos:
            for (sv_index, sv) in enumerate(sigmas_verbose):
                paulis = []
                paulis_verbose = []
                for (tup_index, tup) in enumerate(c):
                    paulis_verbose.append((tup, sv[tup_index]))
                    paulis.append((tup, sigmas[sv_index][tup_index]))
                retset_verbose.append(paulis_verbose)
                retset.append(operator_from_sparse_pauli(N, paulis))
            
    return retset, retset_verbose


# INPUTS:
#     N - Number of qubits
#     k - Locality of qubit interactions
#     mode - Ising (default) or Heisenberg
def QMaxCutHamiltonian(N, k, mode="Ising"):
    combos = combinations(range(N), k)

    hamiltonian = np.zeros((2**N, 2**N), dtype=complex)
    for c in combos:
        X_nonidentities = [(c[i], X) for i in range(k)]
        Y_nonidentities = [(c[i], Y) for i in range(k)]
        Z_nonidentities = [(c[i], Z) for i in range(k)]
        
        h_e = operator_from_sparse_pauli(N, Z_nonidentities)
        if(mode == "Heisenberg"):
            h_e = h_e.astype(complex)
            h_e += operator_from_sparse_pauli(N, Y_nonidentities)
            h_e += operator_from_sparse_pauli(N, X_nonidentities)

        h_e = np.identity(2**N) - h_e
        h_e = 0.5 * h_e if mode == "Ising" else 0.25 * h_e
        hamiltonian += h_e

    return hamiltonian


# INPUTS
#     N - The number of qubits in the quantum state or nodes in the constraint graph.
#     E - A 2-tuple corresponding to the edge of the constraint graph with constraint graph node numbers in ascending order as constraints.  Example: `(0, 2)`
#     k - The locality of qubit interactions.
def moment_cost_matrix(N, E, k):
    _, pauli_ops_verbose = Paulis_N_k(N, k)
    retmat = np.zeros((len(pauli_ops_verbose), len(pauli_ops_verbose)))
    A = E[0]
    B = E[1]
    for index_row, pauli_op_row in enumerate(pauli_ops_verbose):
        for index_col, pauli_op_col in enumerate(pauli_ops_verbose):
            if(len(pauli_ops_verbose[index_row]) > 1 and len(pauli_ops_verbose[index_col]) > 1):
                reference_pauli = next((p for i, p in pauli_ops_verbose[index_row] if i == A), [])

                valid = False
                for tup in pauli_ops_verbose[index_row]:
                    if(tup[0] == B and tup[1] == reference_pauli):
                        valid = True
                if(valid):
                    valid_A = False
                    valid_B = False
                    for tup in pauli_ops_verbose[index_col]:
                        if(tup[0] == A and tup[1] == reference_pauli):
                            valid_A = True
                        if(tup[0] == B and tup[1] == reference_pauli):
                            valid_B = True
                    if(valid_A and valid_B):
                        retmat[index_row][index_col] = -0.5
                        retmat[index_col][index_row] = -0.5    

    return retmat


# Returns list of the nth roots of unity, [1, \omega, \omega^2, ...]
def rootsOfUnity(n):
    return np.array([np.exp(2*np.pi*1j*ns/n) for ns in range(n)])