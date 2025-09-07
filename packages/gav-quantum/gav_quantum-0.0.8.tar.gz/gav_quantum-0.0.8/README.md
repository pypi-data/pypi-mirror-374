# gav-quantum

`gav-quantum` is a quantum information utility package developed by Emil Marinov and Gray Alien Ventures.

## Installation
`pip install gav-quantum`

## Usage

Sample import statement below: \
`from gav_quantum import X, Y, Z, operator_from_sparse_pauli`

## Objects

`ZERO` - A column vector representation of the 0-state, [1 0]^T.

`ONE` - A column vector representation of the 1-state, [0 1]^T.

`X`, `Y`, `Z` - Standard X, Y, and Z Pauli operators.

`PAULIS` - An array of the Pauli operators in standard quantum information convention.  Convenient for enumerations.

`BELL_STATES[PHI_PLUS | PHI_MINUS | PSI_PLUS | PSI_MINUS]` - The four maximally entangled Bell states.


## Functions

### `W(N)`

*Inputs*
* **N** - The number of qubits in the quantum state.

*Output*
* A vector corresponding to the maximally entangled N-qubit W-state.

### `GHZ(N)`

*Inputs*
* **N** - The number of qubits in the quantum state.

*Output*
* A vector corresponding to the maximally entangled N-qubit GHZ-state.

### `operator_from_sparse_pauli(N, nonidentities)` - Creates an operator from a list of tuples of qubits and the non-identity Pauli operators acting upon them.

*Inputs*
* **N** - The number of qubits in the quantum state.
* **nonidentities** - List of tuples specifying qubit number (indexed at 0) in ascending order and corresponding Pauli operator. Example: [(0,X),(2,Y)]

*Output*
* A 2^N by 2^N operator.

*Notes*
* Make sure to have also imported whichever Pauli operators (`X`, `Y`, `Z`) are used in the `nonidentities` argument

### `Paulis_N_k(N, k)`
Generates a list of the subset of operator bases over `N` qubits of weight less than or equal to `k`; it is a "tensor product of `N` operators, each of which is in {`I`, `X`, `Y`, `Z`} such that at most `k` are not `I`" [1].

*Inputs*
* **N** - The number of qubits in the quantum state.
* **k** - The maximum locality of Pauli operators acting upon the qubits.

*Output*
* A 2-tuple containing the set of operators where the first element is a list of the operators in matrix form and the second element is a verbose human-friendly list specifying qubit number (indexed at 0) in ascending order and corresponding Pauli operator. Example: [(0,X),(2,Y)]

*Notes*
* Returns the full operator basis if `k = N`

### `QMaxCutHamiltonian(N, k, mode="Ising")`
Generates a Quantum MaxCut Hamiltonian.

*Inputs*
* **N** - The number of qubits in the quantum state.
* **k** - The locality of qubit interations.
* **mode** - `"Ising"` | `"Heisenberg"`

*Output*
* A 2^N by 2^N matrix corresponding to a QMaxCut Hamiltonian.

### `moment_constraint_matrix(N, E, k)`
Generates the constraint matrix accompanying the moment matrix for a Lasserre semidefinite program assuming an anti-ferromagnetic state.  Entries correspond to a matrix with rows and columns indexed by the subset of operator bases (see `Paulis_N_k(N, k)`).  A row with adjacent edges with the same Pauli operator and a column with the same adjacent edges and Pauli operator between them are penalized with a `-0.5` weight for their anti-alignment.  For example, if the edges in question are 0 and 2, row `X_0 X_2` and column `X_0 X_2` are penalized for not exhibiting anti-alignment.

*Inputs*
* **N** - The number of qubits in the quantum state or nodes in the constraint graph.
* **E** - A 2-tuple corresponding to the edge of the constraint graph with constraint graph node numbers in ascending order as constraints.  Example: `(0, 2)`
* **k** - The locality of qubit interactions.

*Output*
* A $\gamma$ by $\gamma$ matrix where $\gamma$ is the size of the subset of operator bases corresponding to the inputted `N` and `k` and the entries are real.

### `rootsOfUnity(n)`
Returns a list of the $n$th roots of unity.

*Output*
* A list of the $n$th roots of unity i.e. [1, \omega, \omega^2, ..., \omega^{n-1}]

## References
[1] Parekh, O., & Thompson, K. (2021). Application of the Level-2 Quantum Lasserre Hierarchy in Quantum Approximation Algorithms. arXiv. [https://doi.org/10.48550/arXiv.2105.05698](https://doi.org/10.48550/arXiv.2105.05698)