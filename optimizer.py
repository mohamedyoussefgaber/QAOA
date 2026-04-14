import scipy.optimize as opt
import numpy as np
from qiskit.quantum_info    import Statevector

def Basinhopping(
    self,
    nlayer=5,
    theta0=[0, 1],
    bounds=((0, 2 * np.pi), (0, 2 * np.pi)),
    niter=500,
):
    self.binary_numbers = []
    for i in range(2**self.nqubits):
        binary_str = format(i, f"0{self.nqubits}b")
        self.binary_numbers.append(binary_str)
    full_states = Statevector.from_label(self.binary_numbers[0])
    for i in range(1, len(self.binary_numbers)):
        full_states += Statevector.from_label(self.binary_numbers[i])
    full_states = (1 / np.sqrt(len(self.binary_numbers))) * full_states


    resx = [] # theata to be optimized
    resfun = [np.real(full_states.expectation_value(self.hc))] # expected value to be minimized
    self.call_log = []
    print("niter value:", niter)
    #print("number of layers ;" , nlayer)
    def basinhopping_callback(x, f, accepted):
            print(f"hop -> gamma: {x[0]:.4f}, beta: {x[1]:.4f}, fun: {f:.4f}, accepted: {accepted}")
            if accepted:
                self.call_log.append({
                    "gamma": x[0],
                    "beta":  x[1],
                    "fun":   f
                })
    for layer in range(nlayer):
        print("Layer " + str(layer + 1) + " started")
        
        res = opt.basinhopping(
            self.objective_layer(layer, resx),
            theta0,
            minimizer_kwargs={"bounds": bounds},
            niter=niter,
            callback=basinhopping_callback
        )
        print("Layer Message: " + str(res.message))

        resx += [list(res.x)]
        resfun += [res.fun]
        self.plot_optimization_results(self.call_log)
        print(layer , ':' , resx)
    return resx

def COBYLA(self,
    nlayer=5,
    theta0=[0, 1],
    bounds=((0, 2 * np.pi), (0, 2 * np.pi)),
    niter=500,):
    self.binary_numbers = []
    for i in range(2**self.nqubits):
        binary_str = format(i, f"0{self.nqubits}b")
        self.binary_numbers.append(binary_str)
    full_states = Statevector.from_label(self.binary_numbers[0])
    for i in range(1, len(self.binary_numbers)):
        full_states += Statevector.from_label(self.binary_numbers[i])
    full_states = (1 / np.sqrt(len(self.binary_numbers))) * full_states


    resx = [] # theata to be optimized
    resfun = [np.real(full_states.expectation_value(self.hc))] # expected value to be minimized
    self.call_log = []
    print("niter value:", niter)
    #print("number of layers ;" , nlayer)
    def COBYLA_callback(x):
    
            f = self.objective_layer(layer, resx)(x)
            self.call_log.append({
                    "gamma": x[0],
                    "beta":  x[1],
                    "fun" : f
                })
    for layer in range(nlayer):
        print("Layer " + str(layer + 1) + " started")
        
        res = opt.minimize(self.objective_layer(layer, resx),
            theta0,
            bounds= bounds,
            method = "COBYLA",
            options={"maxiter": 10000},
            #niter=niter,
            callback=COBYLA_callback)
        print("Layer Message: " + str(res.message))

        resx += [list(res.x)]
        resfun += [res.fun]
        self.plot_optimization_results(self.call_log)
        #print(layer , ':' , resx)
    return resx
     