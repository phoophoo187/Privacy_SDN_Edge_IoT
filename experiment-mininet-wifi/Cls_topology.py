"""
" The Topology class responed for 
"  - creating a network topology which specified in a JSON format file
"  - adding and removing nodes and edges from a network
"  - showing a current network topology
"""
import networkx as nx
from networkx.readwrite import json_graph
import json
import matplotlib.pyplot as plt

class Cls_topology:
    
    def __init__(self):
        pass
        
    
    def create_g_from_json(self,jsonfile):
        # Read in a JSON formatted graph file.
        # return the networkx Graph
        gnl = json.load(open(jsonfile))
        return json_graph.node_link_graph(gnl)
        
    def show_network(self,G):
        # Show basic node and link info
        print("Network nodes: {}".format(G.nodes()))
        print("Network links: {}".format(G.edges()))
        
        # Node and Link with extra data properties
        print("Network nodes: {}".format(G.nodes(data=True)))
        print("Network links: {}".format(G.edges(data=True)))
        
        
    def draw_graph(self,G):
        #This function is to draw a graph with the fixed position
        edge_labels = {}  # dict for edge label {(src,dst):{key:value,key:value}}
        node_pos={} # dict for node posttion {'node':(x,y),'node':(x,y)}
        for n, data in G.nodes(data=True):
            node_pos[n] = data['x'], data['y']
            
        for u, v, data in G.edges(data=True):
            edge_labels[u, v] = {'w':data['weight'],'c':data['cost'],'c1':data['c1'],'c2':data['c2']}
        nx.draw_networkx(G,node_pos)
        nx.draw_networkx_edge_labels(G,node_pos,edge_labels=edge_labels)
            
    def show_node_position(self,G):
        node_pos={}
        for n, data in G.nodes(data=True):
            node_pos[n] = data['x'], data['y']
        print(node_pos)
        
    def show_edge_labels(self,G):
        edge_labels={}
        for u, v, data in G.edges(data=True):
            edge_labels[u, v] = {'w':data['weight'],'c':data['cost'],'c1':data['c1'],'c2':data['c2']}
        print(edge_labels)