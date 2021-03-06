# This is Ryu controller program running @ Mininet-wifi for SDNIoTEdge Progect @ NECTEC.
# written by PPTLT.

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto.ofproto_v1_3_parser import NXActionRegLoad2
from ryu.lib import hub
from ryu.ofproto import nicira_ext
import networkx as nx
import matplotlib.pyplot as plt
import time
import os

r1ip = "192.168.1.1"
r2ip = "192.168.1.2"
r3ip = "192.168.1.3"
r4ip = "192.168.1.4"
r5ip = "192.168.1.5"
r6ip = "192.168.1.6"
gw1ip= "192.168.1.8"

gw1mac = "00:00:00:00:00:70"
gw2mac = "00:00:00:00:00:80"
r1mac = "00:00:00:00:00:10"
r2mac = "00:00:00:00:00:20"
r3mac = "00:00:00:00:00:30"
r4mac = "00:00:00:00:00:40"
r5mac = "00:00:00:00:00:50"
r6mac = "00:00:00:00:00:60"

class node_failure (app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(node_failure, self).__init__(*args, **kwargs)
        self.switch_table = {}
        self.G = nx.Graph()
        self.datapaths = {}
        self.activedataplane = []
        self.edge_list = []
        self.weight_edge_list = [2, 2, 3, 2, 1, 2, 2]
        self.concave_edge_list = [1, 3, 3, 1, 4, 3, 1]        
        self.CPU_edge_list = [2, 1, 2, 2, 2, 3, 4]  
        self.monitor_thread = hub.spawn(self._monitor)
    
    def add_multi_link_attributes(self, attr1,attr2, attr3):
        """
        This funtion is to add the multiple link attributes to graph G
        input: G : graph
                attr1 : link attribute 1
                attr2 : link attribute 2
                attr3 : link attribute 3
        output : G
        """
        i = 0
        for (u, v) in self.G.edges():
            self.G.add_edge(u,v,w=attr1[i],c1=attr2[i], c2=attr3[i])
            i = i+1 
        return self.G

    def remove_Edge(self, rm_edge_list):
        """
        This function is to remove edges in the rm_edge_list from G
        """
        self.G.remove_edges_from(rm_edge_list)
        self.G.edges()
        return self.G

    def compare_path(self, path1,path2):
        
        if collections.Counter(path1) == collections.Counter(path2):
            self.logger.info("The lists l1 and l2 are the same") 
            flag = True
        else: 
            self.logger.info("The lists l1 and l2 are not the same") 
            flag = False
        return flag

    def additive_path_cost(self, path, attr):
        """
        This function is to find the path cost based on the additive costs
        : Path_Cost = sum_{edges in the path}attr[edge]
        Input : G : graph
                path : path is a list of nodes in the path
                attr : attribute of edges
        output : path_cost
        """           
        return sum([self.G[path[i]][path[i+1]][attr] for i in range(len(path)-1)])

    ## Calculate concave path cost from attr
    def max_path_cost(self, path, attr):
        """
        This function is to find the path cost based on the additive costs
        : Path_Cost = max{edges in the path}attr[edge]
        Input : G : graph
                path : path is a list of nodes in the path
                attr : attribute of edges
        output : path_cost
        """        
        return max([self.G[path[i]][path[i+1]][attr] for i in range(len(path)-1)])

    def calculate_path_cost_with_weighted_sum(self, path, attr1, attr2):
        """
        This function is to find the weighted sum based on two concave matrics
        : c(e) = ac1(e) + bc2(e)
        a = (1-c2(e)) / (2-c(e)-c2(e))
        b = (1-c(e)) / (2-c(e)-c2(e)))
        Input : G : graph
                path : path is a list of nodes in the path
                attr1 : c1 of edges
                attr2 : c2 of edges
        output : path_costs
        """         
        costs = []       
        for i in range(len(path) - 1):
            a = (1- self.G[path[i]][path[i+1]][attr2]) / (2 - self.G[path[i]][path[i+1]][attr1] - self.G[path[i]][path[i+1]][attr2]) 
            b = (1- self.G[path[i]][path[i+1]][attr1]) / (2 - self.G[path[i]][path[i+1]][attr1] - self.G[path[i]][path[i+1]][attr2]) 
            costs.append(a * self.G[path[i]][path[i+1]][attr1] + b * self.G[path[i]][path[i+1]][attr2]) 
        return max(costs)

    def calculate_path_cost_with_concave_function(self, path, attr1, attr2):
        """
        This function is to find the path cost based on the concave function
        : Path_Cost = max{c1(edge), c2(edge)}
        Input : G : graph
                path : path is a list of nodes in the path
                attr1 : c1 of edges
                attr2 : c2 of edges
        output : path_cost
        """                
        costs = []       
        for i in range(len(path) - 1):
            c1 = self.G[path[i]][path[i+1]][attr1]
            c2 = self.G[path[i]][path[i+1]][attr2]
            costs.append(max(c1, c2)) 
        return max(costs)
        
    def rm_edge_constraint(self,Cons):
        rm_edge_list = []
        for u, v, data in self.G.edges(data=True):
            e = (u,v)
            cost = self.G.get_edge_data(*e)
            #self.logger.info(cost)
            if cost['c1'] >= Cons:
                rm_edge_list.append(e)
                #self.logger.info(rm_edge_list)    
        self.remove_Edge(rm_edge_list)
        return self.G

    def has_path(self, source, target):
        """Return True if G has a path from source to target, False otherwise.

        Parameters
        ----------
        G : NetworkX graph

        source : node
        Starting node for path

        target : node
        Ending node for path
        """
        try:
            sp = nx.shortest_path(self.G, source, target)
        except nx.NetworkXNoPath:
            return False
        return True

    def Optimum_prun_based_routing(self, S, D, L):
        """
        This function is to find the optimal path from S to D with constraint L 
        Input : G : graph
                S : Source
                D : Destination
                L : constraint
        """
        if self.has_path(S, D):
            
            Shortest_path = nx.dijkstra_path(self.G, S, D, weight='w')                           
            Opt_path = Shortest_path
            PathConcave_cost  = self.max_path_cost(Shortest_path, 'c1')                    
            while len(Shortest_path) != 0:
                path_cost = self.additive_path_cost(Shortest_path, 'w') 
                #self.logger.info('Path cost - %d', path_cost)
                if path_cost <= L:
                    """go to concave cost"""
                    PathConcave_cost  = self.max_path_cost(Shortest_path, 'c1')                    
                    self.G = self.rm_edge_constraint(PathConcave_cost) # remove all links where the concave link is greater than PathConcave_cost
                
                    Opt_path = Shortest_path
                    if self.has_path(S, D):
                        Shortest_path = nx.dijkstra_path(self.G, S, D, weight='w')
                    else:
                        Shortest_path = []                
                else:
                    break 
        else:
            self.logger.info('No path from %s to %s', S, D)
            PathConcave_cost  = 0
            Opt_path = []
        return PathConcave_cost, Opt_path

    def Option2_routing(self, S, D, L):
        """
        This function is to find the optimal path from S to D with constraint L by combining two concave matrics with weighted sum
        Input : G : graph
                S : Source
                D : Destination
                L : constraint
        """
        if self.has_path(S, D):            
            Shortest_path = nx.dijkstra_path(self.G, S, D, weight='w')                           
            Opt_path = Shortest_path
            path_cost_with_weighted_sum  = self.calculate_path_cost_with_weighted_sum(Shortest_path, 'c1', 'c2')
            return path_cost_with_weighted_sum, Opt_path

            while len(Shortest_path) != 0:
                path_cost = self.additive_path_cost(Shortest_path, 'w') 
                #self.logger.info('Path cost - %d', path_cost)
                if path_cost <= L:
                    """go to path cost with weighted sum"""
                    path_cost_with_weighted_sum  = self.calculate_path_cost_with_weighted_sum(Shortest_path, 'c1', 'c2')
                    self.G = self.rm_edge_constraint(path_cost_with_weighted_sum) # remove all links where the concave link is greater than PathConcave_cost                    
                    Opt_path = Shortest_path
                    if self.has_path(S, D):
                        Shortest_path = nx.dijkstra_path(self.G, S, D, weight='w')
                    else:
                        Shortest_path = []                
                else:
                    break 
        else:
            self.logger.info('No path from %s to %s', S, D)
            Opt_path = []
            path_cost_with_weighted_sum  = 0
        return path_cost_with_weighted_sum, Opt_path

    def Option3_routing(self, S, D, L):
        """
        This function is to find the optimal path from S to D with constraint L by combining two concave matrics with concave function
        Input : G : graph
                S : Source
                D : Destination
                L : constraint
        """
        if self.has_path(S, D):            
            Shortest_path = nx.dijkstra_path(self.G, S, D, weight='w')                           
            Opt_path = Shortest_path
            path_cost_with_concave_function  = self.calculate_path_cost_with_concave_function(Shortest_path, 'c1', 'c2')
            return path_cost_with_concave_function, Opt_path
            while len(Shortest_path) != 0:
                path_cost = self.additive_path_cost(Shortest_path, 'w') 
                #self.logger.info('Path cost - %d', path_cost)
                if path_cost <= L:
                    """go to path cost with weighted sum"""
                    path_cost_with_concave_function  = self.calculate_path_cost_with_concave_function(Shortest_path, 'c1', 'c2')
                    self.G = self.rm_edge_constraint(path_cost_with_concave_function) # remove all links where the concave link is greater than PathConcave_cost                    
                    Opt_path = Shortest_path
                    if self.has_path(S, D):
                        Shortest_path = nx.dijkstra_path(self.G, S, D, weight='w')
                    else:
                        Shortest_path = []                
                else:
                    break 
        else:
            self.logger.info('No path from %s to %s', S, D)
            Opt_path = []
            path_cost_with_concave_function = 0
        return path_cost_with_concave_function, Opt_path
    
    def _monitor(self):     
        while True:   
            if len(self.datapaths.keys()) == 7:      
                current_time = time.asctime(time.localtime(time.time()))  
                source = 'S'
                dest = 'D'
                L = 4.5                
                self.logger.info("%s Source %s Destination %s Constraint %s", current_time, source, dest, L)            

                self.G = nx.Graph()
                self.G.add_edges_from(self.edge_list) 
                self.G = self.add_multi_link_attributes(self.weight_edge_list, self.concave_edge_list, self.CPU_edge_list)   
                self.logger.info("Option 1 - Discard one of the concave metrics")                            
                optimal_cost, optimal_path = self.Optimum_prun_based_routing(source, dest, L)
                self.logger.info("Path cost - %s, Optimal path - %s", optimal_cost, optimal_path)

                self.G = nx.Graph()
                self.G.add_edges_from(self.edge_list) 
                self.G = self.add_multi_link_attributes(self.weight_edge_list, self.concave_edge_list, self.CPU_edge_list)   
                self.logger.info("Option 2 - Combine two concave metrics with weighted sum")            
                optimal_cost, optimal_path = self.Option2_routing(source, dest, L) 
                self.logger.info("Path cost - %s, Optimal path - %s", optimal_cost, optimal_path)

                self.G = nx.Graph()
                self.G.add_edges_from(self.edge_list) 
                self.G = self.add_multi_link_attributes(self.weight_edge_list, self.concave_edge_list, self.CPU_edge_list)   
                self.logger.info("Option 3 - Combine two concave metric with concave function")            
                optimal_cost, optimal_path = self.Option3_routing(source, dest, L)
                self.logger.info("Path cost - %s, Optimal path - %s", optimal_cost, optimal_path)

            hub.sleep(10)

    def add_flow(self, datapath, table, priority, match, actions, hard):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(
            ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, table_id=table, command=ofproto.OFPFC_ADD,
                                priority=priority, match=match, instructions=inst, hard_timeout=hard)
        datapath.send_msg(mod)

    def add_gototable(self, datapath, table, n, priority, match, hard): 
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        inst = [parser.OFPInstructionGotoTable(n)]
        mod = parser.OFPFlowMod(datapath=datapath, table_id=table, command=ofproto.OFPFC_ADD,
                                priority=priority, match=match, hard_timeout=hard, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        dp = ev.msg.datapath
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        local = datapath.ofproto.OFPP_LOCAL

        self.logger.info("Switch_ID %s is connected,1", dp.id)

        if dp.id == 1:
            self.logger.info("MeshNode_1 is connected")
# Relay to superedge
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=r1mac, arp_tpa=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r1mac), parser.OFPActionSetField(
                eth_dst=gw1mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)
# Relay to edge2
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=r1mac, arp_tpa=r2ip)
            actions = [parser.OFPActionSetField(eth_src=r1mac), parser.OFPActionSetField(
                eth_dst=r2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)
# Relay To edge3
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=r1mac, arp_tpa=r3ip)
            actions = [parser.OFPActionSetField(eth_src=r1mac), parser.OFPActionSetField(
                eth_dst=r2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

# Relay To edge4
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=r1mac, arp_tpa=r4ip)
            actions = [parser.OFPActionSetField(eth_src=r1mac), parser.OFPActionSetField(
                eth_dst=r4mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=r1mac, ipv4_dst=r4ip)
            actions = [parser.OFPActionSetField(eth_src=r1mac), parser.OFPActionSetField(
                eth_dst=r4mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 160, match, actions, 0)


# Connect edge3
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_src=r1mac, arp_tpa=r3ip)
            actions = [parser.OFPActionSetField(eth_src=r1mac), parser.OFPActionSetField(
                eth_dst=r2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 160, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=r1mac, ipv4_dst=r3ip)
            actions = [parser.OFPActionSetField(eth_src=r1mac), parser.OFPActionSetField(
                eth_dst=r2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 160, match, actions, 0)


#################################
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst="FF:FF:FF:FF:FF:FF", arp_tpa=r1ip)
            self.add_flow(datapath, 0, 170, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=r1ip, arp_tpa=gw1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=r1ip, ipv4_dst=gw1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=r1ip, arp_tpa=r2ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=r1ip, ipv4_dst=r2ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=r1ip, arp_tpa=r4ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=r1ip, ipv4_dst=r4ip)
            self.add_flow(datapath, 0, 165, match, [], 0)


            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=r2ip, arp_tpa=r3ip)
            self.add_flow(datapath, 0, 165, match, [], 0)


            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=r2ip, ipv4_dst=r3ip)
            self.add_flow(datapath, 0, 165, match, [], 0)
# NewRule
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=r1mac, eth_dst=gw1mac, ipv4_src=r2ip, ipv4_dst=gw1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=r1mac, eth_dst=r4mac, ipv4_src=gw1ip, ipv4_dst=r4ip)
            self.add_flow(datapath, 0, 165, match, [], 0)


        if dp.id == 2:
            self.logger.info("MeshNode_2 is connected")

# Relay To edge3
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=r2mac, arp_tpa=r3ip)
            actions = [parser.OFPActionSetField(eth_src=r2mac), parser.OFPActionSetField(
                eth_dst=r3mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

# Relay To edge5
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=r2mac, arp_tpa=r5ip)
            actions = [parser.OFPActionSetField(eth_src=r2mac), parser.OFPActionSetField(
                eth_dst=r5mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

# Relay To edge1
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=r2mac, arp_tpa=r1ip)
            actions = [parser.OFPActionSetField(eth_src=r2mac), parser.OFPActionSetField(
                eth_dst=r1mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)
# Relay to superedge
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=r2mac, arp_tpa=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r2mac), parser.OFPActionSetField(
                eth_dst=gw1mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

###########################################################################################

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst="FF:FF:FF:FF:FF:FF", arp_tpa=r2ip)
            self.add_flow(datapath, 0, 170, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=r2ip, arp_tpa=r3ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=r2ip, ipv4_dst=r3ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=r2ip, arp_tpa=r1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=r2ip, ipv4_dst=r1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=r1ip, arp_tpa=gw1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=r1ip, ipv4_dst=gw1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

           
        if dp.id == 3:
            self.logger.info("MeshNode_3 is connected")

# Relay To superedge
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=r3mac, arp_tpa=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r3mac), parser.OFPActionSetField(
                eth_dst=gw1mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)
# Relay To edge1
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=r3mac, arp_tpa=r1ip)
            actions = [parser.OFPActionSetField(eth_src=r3mac), parser.OFPActionSetField(
                eth_dst=r2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)
# Relay To edge2
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=r3mac, arp_tpa=r2ip)
            actions = [parser.OFPActionSetField(eth_src=r3mac), parser.OFPActionSetField(
                eth_dst=r2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

# Relay To edge6
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=r3mac, arp_tpa=r6ip)
            actions = [parser.OFPActionSetField(eth_src=r3mac), parser.OFPActionSetField(
                eth_dst=r6mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

# connect to edge1
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_src=r3mac, arp_tpa=r1ip)
            actions = [parser.OFPActionSetField(eth_src=r3mac), parser.OFPActionSetField(
                eth_dst=r2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 150, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=r3mac, ipv4_dst=r1ip)
            actions = [parser.OFPActionSetField(eth_src=r3mac), parser.OFPActionSetField(
                eth_dst=r2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 150, match, actions, 0)
# connect to edge3

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst="FF:FF:FF:FF:FF:FF", arp_tpa=r3ip)
            self.add_flow(datapath, 0, 170, match, [], 0)

           
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=r3ip, ipv4_dst=r2ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=r3ip, arp_tpa=r2ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=r2ip, arp_tpa=r1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=r2ip, arp_tpa=gw1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=r2ip, ipv4_dst=r1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=r2ip, ipv4_dst=gw1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

        if dp.id == 7:
            self.logger.info("SuperEdge is connected")

# edge4
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_src=gw1mac, arp_tpa=r4ip)
            actions = [parser.OFPActionSetField(eth_src=gw1mac), parser.OFPActionSetField(
                eth_dst=r1mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 150, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=gw1mac, ipv4_dst=r4ip)
            actions = [parser.OFPActionSetField(eth_src=gw1mac), parser.OFPActionSetField(
                eth_dst=r1mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 150, match, actions, 0)


# edge5
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_src=gw1mac, arp_tpa=r5ip)
            actions = [parser.OFPActionSetField(eth_src=gw1mac), parser.OFPActionSetField(
                eth_dst=r2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 150, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=gw1mac, ipv4_dst=r5ip)
            actions = [parser.OFPActionSetField(eth_src=gw1mac), parser.OFPActionSetField(
                eth_dst=r2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 150, match, actions, 0)

# edge6
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_src=gw1mac, arp_tpa=r6ip)
            actions = [parser.OFPActionSetField(eth_src=gw1mac), parser.OFPActionSetField(
                eth_dst=r3mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 150, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=gw1mac, ipv4_dst=r6ip)
            actions = [parser.OFPActionSetField(eth_src=gw1mac), parser.OFPActionSetField(
                eth_dst=r3mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 150, match, actions, 0)




# To Prevent Looping
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst="FF:FF:FF:FF:FF:FF", arp_tpa=gw1ip)
            self.add_flow(datapath, 0, 170, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=gw1ip, ipv4_dst=r1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=gw1ip, arp_tpa=r1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)




# Not to relay other packets
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=r1ip, ipv4_dst=r2ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=r1ip, ipv4_dst=r3ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

        if dp.id == 4:
            self.logger.info("MeshNode_4 is connected")
# Relay to SuperEdge
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=r4mac, arp_tpa=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r4mac), parser.OFPActionSetField(
                eth_dst=r1mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

# Relay to edge5
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=r4mac, arp_tpa=r5ip)
            actions = [parser.OFPActionSetField(eth_src=r4mac), parser.OFPActionSetField(
                eth_dst=r5mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

# Relay To edge6
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=r4mac, arp_tpa=r6ip)
            actions = [parser.OFPActionSetField(eth_src=r4mac), parser.OFPActionSetField(
                eth_dst=r5mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

# Connect Raspi6
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_src=r4mac, arp_spa=r4ip, arp_tpa=r6ip)
            actions = [parser.OFPActionSetField(eth_src=r4mac), parser.OFPActionSetField(
                eth_dst=r5mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 160, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=r4mac, ipv4_dst=r6ip)
            actions = [parser.OFPActionSetField(eth_src=r4mac), parser.OFPActionSetField(
                eth_dst=r5mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 160, match, actions, 0)

# Connect SuperEdge
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_src=r4mac, arp_spa=r4ip, arp_tpa=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r4mac), parser.OFPActionSetField(
                eth_dst=r1mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 160, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=r4mac, ipv4_dst=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r4mac), parser.OFPActionSetField(
                eth_dst=r1mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 160, match, actions, 0)

# To Prevent Duplicate Problem
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst="FF:FF:FF:FF:FF:FF", arp_tpa=r4ip)
            self.add_flow(datapath, 0, 170, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=r4ip, arp_tpa=r1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=r4ip, ipv4_dst=r1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=r4ip, arp_tpa=r5ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=r4ip, ipv4_dst=r5ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=r5ip, arp_tpa=r6ip)
            self.add_flow(datapath, 0, 165, match, [], 0)



            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=r5ip, ipv4_dst=r6ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

        if dp.id == 5:
            self.logger.info("MeshNode_5 is connected")

# Relay To edge 3
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=r5mac, arp_tpa=r6ip)
            actions = [parser.OFPActionSetField(eth_src=r5mac), parser.OFPActionSetField(
                eth_dst=r6mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

# Relay To edge 4
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=r5mac, arp_tpa=r4ip)
            actions = [parser.OFPActionSetField(eth_src=r5mac), parser.OFPActionSetField(
                eth_dst=r4mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

# Relay To edge1
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=r5mac, arp_tpa=r6ip)
            actions = [parser.OFPActionSetField(eth_src=r5mac), parser.OFPActionSetField(
                eth_dst=r6mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)
# Relay to  superedge
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=r5mac, arp_tpa=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r5mac), parser.OFPActionSetField(
                eth_dst=r4mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

# Connect superedge
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_src=r5mac, arp_spa=r5ip, arp_tpa=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r5mac), parser.OFPActionSetField(
                eth_dst=r2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 160, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=r5mac, ipv4_dst=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r5mac), parser.OFPActionSetField(
                eth_dst=r2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 160, match, actions, 0)

# To Prevent Duplicate Problem
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst="FF:FF:FF:FF:FF:FF", arp_tpa=r5ip)
            self.add_flow(datapath, 0, 170, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=r5ip, arp_tpa=r6ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=r5ip, ipv4_dst=r6ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=r5ip, arp_tpa=r2ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=r5ip, ipv4_dst=r2ip)
            self.add_flow(datapath, 0, 165, match, [], 0)


            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=r5ip, arp_tpa=r4ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=r5ip, ipv4_dst=r4ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=r4ip, arp_tpa=gw1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

           
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=r4ip, ipv4_dst=gw1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

           

        if dp.id == 6:
            self.logger.info("MeshNode_6 is connected")
# Relay To edge6
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=r6mac, arp_tpa=r4ip)
            actions = [parser.OFPActionSetField(eth_src=r6mac), parser.OFPActionSetField(
                eth_dst=r5mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)
# Relay To edge5
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=r6mac, arp_tpa=r5ip)
            actions = [parser.OFPActionSetField(eth_src=r6mac), parser.OFPActionSetField(
                eth_dst=r5mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)
# superedge
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_src=r6mac, arp_spa=r6ip, arp_tpa=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r6mac), parser.OFPActionSetField(
                eth_dst=r3mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 160, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=r6mac, ipv4_dst=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r6mac), parser.OFPActionSetField(
                eth_dst=r3mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 160, match, actions, 0)

# edge4
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_src=r6mac, arp_spa=r6ip, arp_tpa=r4ip)
            actions = [parser.OFPActionSetField(eth_src=r6mac), parser.OFPActionSetField(
                eth_dst=r5mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 150, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=r6mac, ipv4_dst=r4ip)
            actions = [parser.OFPActionSetField(eth_src=r6mac), parser.OFPActionSetField(
                eth_dst=r5mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 150, match, actions, 0)
#########################

# To Prevent Duplicate
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst="FF:FF:FF:FF:FF:FF", arp_tpa=r6ip)
            self.add_flow(datapath, 0, 170, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=r6ip, ipv4_dst=r5ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=r6ip, arp_tpa=r5ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=r5ip, arp_tpa=r4ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=r5ip, arp_tpa=r4ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=r5ip, ipv4_dst=r4ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=r5ip, ipv4_dst=gw1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        current_time = time.asctime(time.localtime(time.time()))
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.logger.info("(Switch ID %s),IP address is connected %s in %s,1",
                                 datapath.id, datapath.address, current_time)
                self.datapaths[datapath.id] = datapath
                self.logger.info(
                    "Current Conneced Switches to RYU controller are %s", self.datapaths.keys())
                if len(self.datapaths.keys()) == 7:
                    #self.edge_list = [('edge1', 'superedge'), ('edge2', 'superedge'), 
                    #('edge3', 'superedge'), ('edge1', 'edge2'), ('edge2', 'edge3'), 
                    #('edge4', 'edge1'), ('edge5', 'edge2'), ('edge6', 'edge3'), 
                    #('edge4', 'edge5'), ('edge5', 'edge6')]
                    self.edge_list = [('S','B'), ('S','A'), ('S','E'), ('B','A'), ('B','D'), ('A','D'), ('E','D')]
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                self.logger.info("(Switch ID %s),IP address is leaved %s in %s,0",
                                 datapath.id, datapath.address, current_time)
                del self.datapaths[datapath.id]
                self.logger.info(
                    "Current Conneced Switches to RYU controller are %s", self.datapaths.keys())

