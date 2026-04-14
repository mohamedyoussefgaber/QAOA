import pandas as pd
from itertools import permutations

def classic_TSP(coordinates):
    #coordinates = pd.read_excel(".\\data\\coordinates.xlsx", index_col=0)
    #coordinates = coordinates.replace("-",None)
    mp  = {
    row: {col: coordinates.loc[row, col] for col in coordinates.columns
        if pd.notna(coordinates.loc[row, col])} for row in coordinates.index
    }
#print(mp)

    start = next(iter(mp))  # 'Alex'
    others = [city for city in mp if city != start]

    def path_cost(path):
        total = 0
        for i in range(len(path) - 1):
            a, b = path[i], path[i+1]
            if b not in mp[a]:
                return None  # no direct edge
            total += mp[a][b]
        return total

    routes = {}
    for perm in permutations(others):
        path = (start,) + perm
        cost = path_cost(path) 
        if cost is not None:  # skip infeasible routes
            routes[cost] = path
    # we didn't inclue the last path to the first city
    #print(min(routes), routes[min(routes)])
    return min(routes), routes[min(routes)]
            
#classic_TSP()

#print(classic_TSP(coordinates ))