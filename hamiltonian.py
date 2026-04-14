import pandas as pd
from qiskit.quantum_info import SparsePauliOp
from coefficient import n2

def hamiltonian_n2(coeff, nqubit):
    I = ["I"] * nqubit
    pauli_list = I.copy()
    pauli_str = "".join(map(str, pauli_list))
    h_opt = SparsePauliOp(pauli_str, coeff[0])

    # 1st block of code for Z only
    for n in range(nqubit):
        pauli_list = I.copy()
        qubit_number = coeff[1][n][0]
        pauli_list[qubit_number] = "Z"
        pauli_str = "".join(map(str, pauli_list))
        pauli_str = pauli_str[::-1]
        h_opt += SparsePauliOp(pauli_str, coeff[1][n][1])

    # 2nd block of code for ZZ
    for (i,j) in coeff[2]: 
        pauli_list = I.copy()   
        pauli_list[i] , pauli_list[j]  = "Z","Z"
        pauli_str = "".join(map(str, pauli_list))
        pauli_str = pauli_str[::-1]
        h_opt += SparsePauliOp(pauli_str, coeff[2][(i , j)])
    #print(h_opt)
    return h_opt





coordinates = pd.read_excel(".\\data\\coordinates.xlsx", index_col = 0)
c = n2(coordinates )
hamiltonian_n2(c, 9)