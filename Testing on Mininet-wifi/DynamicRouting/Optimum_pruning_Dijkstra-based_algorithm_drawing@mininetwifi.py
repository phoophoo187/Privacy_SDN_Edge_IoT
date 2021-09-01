# written by PPTLT.
import networkx as nx
import matplotlib.pyplot as plt

def add_multi_link_attributes(G,attr1,attr2, attr3):
    """
    This funtion is to add the multiple link attributes to graph G
    input: G : graph
            attr1 : link attribute 1
            attr2 : link attribute 2
            attr3 : link attribute 3
    output : G
    """
    i = 0
    for (u, v) in G.edges():
        G.add_edge(u,v,w=attr1[i],c1=attr2[i], c2= attr3[i])
        i = i+1 
    return G

def draw_graph(G,pos):
    """
    This function is to draw a graph with the fixed position
    input : G : graph
            pos: postions of all nodes with the dictionary of coordinates (x,y)
    """
    edge_labels = {}  ## add edge lables from edge attribute
    for u, v, data in G.edges(data=True):
        edge_labels[u, v] = data

    nx.draw_networkx(G,pos)
    nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_labels)

G = nx.Graph()
edge_list = [('edge1', 'superedge'), ('edge2', 'superedge'), 
                    ('edge3', 'superedge'), ('edge1', 'edge2'), ('edge2', 'edge3'), 
                    ('edge4', 'edge1'), ('edge5', 'edge2'), ('edge6', 'edge3'), 
                    ('edge4', 'edge5'), ('edge5', 'edge6')]
pos = {'superedge': (50, 100), 'edge1': (0, 50), 'edge2': (50, 50), 'edge3': (100,50), 'edge4': (0, 0), 'edge5': (50, 0), 'edge6': (100, 0)}
Weight_edge_list = [2, 2, 3, 2, 1, 2, 2, 3, 1, 2]
Concave_edge_list = [1, 3, 3, 1, 4, 3, 1, 1, 2, 3] 
CPU_edge_list = [2, 1, 2, 2, 2, 3, 4, 4, 1, 1] 

G.add_edges_from(edge_list)
G = add_multi_link_attributes(G,Weight_edge_list,Concave_edge_list, CPU_edge_list)
draw_graph(G,pos)
plt.show()
