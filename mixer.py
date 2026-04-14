from qiskit.quantum_info import SparsePauliOp

def Rx(nqubit):
    identity_list = ["I"] * nqubit
    h_opt = SparsePauliOp("".join(map(str, identity_list)), 0)
    for qubit in range(nqubit):
        pauli_list = identity_list.copy()
        pauli_list[qubit] = "X"
        pauli_str = "".join(map(str, pauli_list))
        pauli_str = pauli_str[::-1]
        h_opt += SparsePauliOp(pauli_str)
    return h_opt