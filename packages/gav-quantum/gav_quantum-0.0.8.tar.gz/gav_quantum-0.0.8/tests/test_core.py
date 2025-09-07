from gav_quantum.core import Paulis_N_k

def test_Pauli_3_2():
    Ps, Ps_verbose = Paulis_N_k(3, 2)
    assert(len(Ps) == 37)

def test_Pauli_4_2():
    Ps, Ps_verbose = Paulis_N_k(4, 2)
    assert(len(Ps) == 67)

def test():
    Ps, Ps_verbose = Paulis_N_k(4, 2)
    print(Ps)