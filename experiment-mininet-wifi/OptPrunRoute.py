import networkx as nx
class OptPrunRoute:
    
    C_HopCount = 0 #Hop-count
    C_OCP_BW = 1 # C1: Occupied BW
    C_Node_CPU = 2 # C2: Node CPU Utilization
    C_BW_CPU = 3 # combined C1 and C2
    C_Max = 4 # select max(C1 and C2)
    
    #column of weight and cost in the Graph
    g_weight = "weight"
    g_cost = "cost"
    def __init__(self):
        pass
    
    
    def has_path(self,G, source, target):
        """ Return True if G has a path from source to target, False otherwise.
        Parameters
        G : NetworkX graph
        source : node (Starting node for path)
        target : node (Ending node for path)
        """
        try:
            sp = nx.shortest_path(G,source, target)
        except nx.NetworkXNoPath:
            return False
        return True

    def additive_path_cost(self,G, path, attr):
        """
        This function is to find the path cost based on the additive costs
        : Path_Cost = sum_{edges in the path}attr[edge]
        Input : G : graph
                path : path is a list of nodes in the path
                attr : attribute of edges
        output : path_cost
        """
        return sum([G[path[i]][path[i+1]][attr] for i in range(len(path)-1)])

        ## Calculate concave path cost from attr
    def max_path_cost(self, G, path, attr):
        """
        This function is to find the path cost based on the Concave costs
        : Path_Cost = max{edges in the path}attr[edge]
        Input : G : graph
                path : path is a list of nodes in the path
                attr : attribute of edges
                option: selecting how to create cost 
        output : path_cost
        """
        return max([G[path[i]][path[i+1]][attr] for i in range(len(path)-1)])
    
    def remove_Edge(self,G,rm_edge_list):
        """ This function is to remove edges in the rm_edge_list from G
        """
        G.remove_edges_from(rm_edge_list)
        G.edges()
        return G
    
    def rm_edge_constraint(self, G,Cons):
        rm_edge_list = []
        for u, v, data in G.edges(data=True):
            e = (u,v)
            cost = G.get_edge_data(*e)
            #print(cost)
        
        if cost[self.g_cost] >= Cons:
            rm_edge_list.append(e)
            #print(rm_edge_list)
        
        self.remove_Edge(G,rm_edge_list)
        return G
    
    def setcost(self, G, Opt):
        """ set cost for all edges correspond to the selected Opt
        """
        c_map = {self.C_OCP_BW:'c1',self.C_Node_CPU:'c2'}
        #Set cost to c1 or c2 by a selected option
        if Opt in [self.C_OCP_BW, self.C_Node_CPU]:
            for u,v in G.edges():
                G.edges[u,v][self.g_cost]=G.edges[u,v][c_map[Opt]]
        elif Opt in [self.C_BW_CPU,self.C_Max] :
            #set cost to the combined of c1 and c2
            for u,v in G.edges():
                c1 = G.edges[u,v]['c1']
                c2 = G.edges[u,v]['c2']
                alpha = (1-c1)/(2-c1-c2)
                beta = (1-c2)/(2-c1-c2)
                G.edges[u,v][g_cost]=(alpha*c1)+(beta*c2)
        elif Opt == C_Max:
            #set cost to the max of c1 and c2
            for u,v in G.edges():
                G.edges[u,v][self.g_cost]=max(G.edges[u,v]['c1'],G.edges[u,v]['c2'])
                
    
    def Optimum_prun_based_routing(self,G,S,D,L,O=0):
        """
        This function is to find the optimal path from S to D with constraint L 
        Input : G : Topology
                S : Source
                D : Destination
                L : constraint
                O : Option
                Option: 
                  0: hop-count
                  1: Occupied BW (c1)
                  2: Node CPU (c2)
                  3: combine the two cost, c1 and c2 ( weighted sum)
                  4: select max between c1 and c2
        Note: this method will modify the original graph. 
              Need to backup the original graph before passing to this function
        """
        
        #set cost for all edge correspond to Opt
        self.setcost(G,O)
        
        Opt_path=[]
        find_route_flag = True
        
        while find_route_flag:
            if self.has_path(G,S,D):
                Shortest_path = nx.dijkstra_path(G, S, D, weight= self.g_weight)
                path_cost = self.additive_path_cost(G, Shortest_path, self.g_weight)
                Opt_path = Shortest_path
            else:
                Shortest_path=[]
                
            
            if(len(Shortest_path)!=0) and (path_cost <= L):
                # there is a path but its path cost less then constraint
                # then prun the greah before
                # tring to find a new route in the next round
                """go to concave cost"""
                # find the max cost in the path
                PathConcave_cost  = self.max_path_cost(G, Shortest_path, self.g_cost)
                
                # remove all links where the concave link is greater than PathConcave_cost
                G = self.rm_edge_constraint(G,PathConcave_cost)
            else:
                # there is a path that meet the condition
                # or no path between source and destination
                # exit the loop
                find_route_flag = False
            
            return Opt_path
            
