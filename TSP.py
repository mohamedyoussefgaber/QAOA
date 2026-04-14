
import pandas as pd
import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt

from qiskit.quantum_info    import Statevector
from qiskit import QuantumCircuit, QuantumRegister,transpile
from qiskit_aer import Aer
from qiskit.circuit.library import PauliEvolutionGate

import coefficient 
import hamiltonian
import mixer
import optimizer

class TSP:
    def __init__(self, encoding , coordinates , Anzats , Best_optimum_value = None):
        if encoding not in ["n^2"]:
            raise NotImplementedError("Sorry, encoding should be 'n2'.")
        
        if Anzats  not in ["Vanilla"]:
            raise NotImplementedError("Sorry, encoding should be 'Vanilla'.")
        
        self.encoding = encoding
        self.coordinates = coordinates
        self.Anzats = Anzats
        self.Best_optimum_value = Best_optimum_value
        self.backend = Aer.get_backend("statevector_simulator")
        
        if encoding == "n^2":
            self.ncities = len( coordinates.index )
            self.nqubits = (self.ncities - 1)**2
            self.coeff_calclator = coefficient.n2
            self.hamiltonian_calclator = hamiltonian.hamiltonian_n2
            self.mixer_calculator = mixer.Rx
             
        """
        else: 
            for future implementation()
        """
    def generate_coeff(self):
        self.coeff = self.coeff_calclator (self.coordinates)
        self.hc = self.hamiltonian_calclator(self.coeff , self.nqubits)
        self.hm = self.mixer_calculator(self.nqubits)
        

    def UH(self, gamma):
        # Hamiltonian unitary
        evolution = PauliEvolutionGate(self.hc, gamma)
        evolution.label = r"$\exp(-i\gamma H_{P})$"
        return evolution

    def UM(self, beta):
        # Mixing unitary
        evolution = PauliEvolutionGate(self.hm, beta)
        evolution.label = r"$\exp(-i\beta H_{M})$"
        return evolution
    
    def execute_circuit(self, theta):
        n_layers = len(theta) // 2  # number of alternating unitaries
        beta = theta[:n_layers]
        gamma = theta[n_layers:]
        qreg = []

        for i in range(self.ncities - 1):
            qreg.append(QuantumRegister(self.ncities - 1, f"(T{i+2})"))
        qc = QuantumCircuit(*qreg)
        qc.h(range(self.nqubits))

        for layer_index in range(n_layers):
            # problem Hamiltonion
            #print("gamma :" ,layer_index, "->" , gamma[layer_index])
            qc.append(self.UH(gamma[layer_index]), range(self.nqubits))
            # mixing Hamiltonion
            qc.append(self.UM(beta[layer_index]), range(self.nqubits))

        #qc = self.create_qaoa_circ(theta)
        qc_transpiled = transpile(qc, self.backend)
        job = self.backend.run(qc_transpiled)
        result = job.result()
        state = result.get_statevector(qc) 
        counts = job.result().get_counts()
        
        return state

    def objective_layer(self, layer, resx):
        layer = layer
        resx = resx
        call_log = []  # track all calls

        def wrapper(theta):
            if layer == 0:
                res_list = theta
            else:
                res_list = np.zeros(2 * (layer + 1))
                res_list[slice(layer, len(res_list), layer + 1)] = theta
                for i in range(layer):
                    res_list[slice(i, len(res_list), layer + 1)] = resx[i]

            value = np.real(self.execute_circuit(res_list).expectation_value(self.hc))
            call_log.append({
                "gamma": res_list[0],
                "beta":  res_list[1],
                "fun":   value
            })
            #print("expected value is : ", value)
            return value

        wrapper.call_log = call_log  # expose log outside
        return wrapper


    def plot_optimization_results(self , call_log):
        import matplotlib.pyplot as plt

        calls  = list(range(1, len(call_log) + 1))
        gammas = [c["gamma"] for c in call_log]
        betas  = [c["beta"]  for c in call_log]
        funs   = [c["fun"]   for c in call_log]

        fig, ax1 = plt.subplots(figsize=(10, 5))

        ax1.plot(calls, gammas, marker='o', color='steelblue', label='gamma')
        ax1.plot(calls, betas,  marker='s', color='tomato',    label='beta')
        ax1.set_xlabel("Objective function call")
        ax1.set_ylabel("gamma / beta")

        ax2 = ax1.twinx()
        ax2.plot(calls, funs, marker='^', color='green', 
                linestyle='--', alpha=0.6, label='expected value')
        ax2.set_ylabel("expected value (res.fun)")

        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

        plt.title(f"Optimization calls — {len(call_log)} evaluations")
        plt.tight_layout()
        plt.show()


    def optimize_objective(
        self,
        nlayer=5,
        theta0=[0, 1],
        bounds=((0, 2 * np.pi), (0, 2 * np.pi)),
        niter=500,
        opt_type = "Basinhopping"
    ):
        if opt_type == "Basinhopping":
            return optimizer.Basinhopping(
            self,
            nlayer=nlayer,
            theta0=theta0,
            bounds=bounds,
            niter= niter,
            )
        elif opt_type == "COBYLA":
            return optimizer.COBYLA(
            self,
            nlayer=nlayer,
            theta0=theta0,
            bounds=bounds,
            niter= niter,

            )
    
   
    def get_best_route(self , resx , nlayer):
       
        #n_layers = len(resx) // 2  # number of alternating unitaries
        #print("len(resx)" , n)
        #beta = resx[:len(resx):2]
        #gamma = resx[1:len(resx):2]
        #print("resx" , resx)
        #print("gamma :" , gamma)
        #print("beta", beta)
        qreg = []

        for i in range(self.ncities - 1):
            qreg.append(QuantumRegister(self.ncities - 1, f"(T{i+2})"))
        qc = QuantumCircuit(*qreg)
        qc.h(range(self.nqubits))

        for layer_index in range(nlayer):
            # problem Hamiltonion
           # print("gamma :" ,layer_index, "->" , gamma[layer_index])
            qc.append(self.UH(resx[layer_index][1]), range(self.nqubits))
            # mixing Hamiltonion
            qc.append(self.UM(resx[layer_index][0]), range(self.nqubits))

        #qc = self.create_qaoa_circ(theta)
        qc_transpiled = transpile(qc, self.backend)
        job = self.backend.run(qc_transpiled)
        result = job.result()
        #state = np.real(result.get_statevector(qc).expectation_value(self.hc)) 

        state = result.get_statevector(qc)
        probs = np.abs(state) ** 2

        # index of highest probability state
        best_index = np.argmax(probs)

        # convert index to bitstring
        best_bitstring = format(best_index, f'0{self.nqubits}b')

        print(f"Best bitstring: {best_bitstring}")
        print(f"Probability:    {probs[best_index]:.4f}")






        


    

