import sympy as sp
import pandas as pd
import numpy as np

def n2(coordinates):
    coordinates = coordinates.replace("-",None)
    cities = coordinates.index 
    city_encoding = {i : city for i, city in enumerate(cities)}
    n = len(cities)
    #print(cities)
    #print(city_encoding)
    
    W = np.empty((n, n)) 
    for i in range(n):
        for j in range(n):
            if i == j:
                W[i][j] = 0.0
            else:
                if coordinates.iloc[i,j] is not None:
                    W[i][j] =  float(coordinates.iloc[i,j])
                else:
                    W[i][j] = 0.0 
                

    #print(W)

    X = np.empty((n, n), dtype=object)

    # colomns are the T
    # Rows are the Cities
    for i in range(1, n):
        for j in range(1, n):
            X[i, j] = sp.Symbol(f"x_{i}{j}")
    X[0, :] = 0
    X[:, 0] = 0
    X[0, 0] = 1
    #print(X)
    Z = np.empty(((n - 1) ** 2), dtype=object)
    for i in range(len(Z)):
        Z[i] = sp.Symbol(f"z_{i}")

    # Distance Term
    term = sp.Integer(0)
    for u in range(1,n):
        for v in range(1,n):
            for i in range(1,n - 1):
                term += W[u][v]* X[u, i] * X[v, i + 1]
    
    for i in range(1,n):        
        term += W[0][i]* (X[i,1] + X[i, n-1])


    # A is a wieght for the penalties
    #print(coordinates.max().max())
    A = 100 * coordinates.max().max()


    # Panelties Terms
    # 1st Penalty to check that at each T there is only one cites visited only
    term1 = sp.Integer(0)
    for i in range(1 , n):
        term1 += sp.expand((1 - np.sum(X[i, :])) ** 2)
    term1 = A * term1

    # 2nd Penalty to check that at each city is visited once and only once
    term2 = sp.Integer(0)
    for j in range(n):
        term2 += sp.expand((1 - np.sum(X[:, j])) ** 2)
    term2 = A * term2

    #replacing any x squared with x
    H = sp.expand(term + term1 + term2)
    
    for i , x in enumerate(X[1:,1:].flat):
     #   print(x, "   " , Z[i])

        H = H.subs(x**2, x)
        H = H.subs(x, 0.5*(1 - Z[i]))
    H = sp.expand(H)
    #print(H)
    # the coeff shape is list of 
    # 1- number --> the absolute term 
    # 2- list   --> the terms of one Z only
    # 3- dict   --> the terms of two zz 
    
    coeff = []
    # 1st element is the  is the absolute term
    coeff.append( sp.Poly(H).coeffs()[-1])
    coeff.append([])
    for i in range(len(Z)):
        coeff_z = sp.Poly(H.coeff(Z[i])).coeffs()[-1]
        coeff[1].append([i, coeff_z]) 
    
    coeff.append({})
    for i in range(len(Z)):
        for j in range(i+1 , len(Z)):
            coeff[-1][( i , j )] = H.coeff(Z[i] * Z[j])
    #print(coeff)
    return coeff

coordinates = pd.read_excel(".\\data\\coordinates.xlsx",index_col = 0)
n2(coordinates)


