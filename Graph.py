import networkx as nx
import matplotlib.pyplot as plt


from classic import classic_TSP
def graph(coordinates):
    coordinates = coordinates.replace("-",None)
    G = nx.Graph()
    for city in coordinates.columns:
        G.add_node(city)
        #print(city)
    for i in coordinates.index:
        for j in coordinates.columns:
            weight = coordinates.loc[i, j]
            if weight is not None:
                G.add_edge(i, j, weight=float(weight))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2000, font_size=14)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
    #fig, ax = plt.subplots()
    #plt.show()
    return coordinates 

