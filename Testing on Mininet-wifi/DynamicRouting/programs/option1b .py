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
from prettytable import PrettyTable
import socket
import requests
import datetime

e1ip = "192.168.1.1"
e2ip = "192.168.1.2"
e3ip = "192.168.1.3"
e4ip = "192.168.1.4"
e5ip = "192.168.1.5"
e6ip = "192.168.1.6"
superEdgeip= "192.168.1.8"

superEdgeMac = "00:00:00:00:00:70"
e1mac = "00:00:00:00:00:10"
e2mac = "00:00:00:00:00:20"
e3mac = "00:00:00:00:00:30"
e4mac = "00:00:00:00:00:40"
e5mac = "00:00:00:00:00:50"
e6mac = "00:00:00:00:00:60"


socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
'''
    host = ip address of h1 (ryu controller)
'''
host = '10.0.0.101'
port = 12345

try:
    socket_server.bind((host, port))
except socket.error as e:
    print(e)
print('Waiting for connection. Server Started')

socket_server.listen()

class node_failure (app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(node_failure, self).__init__(*args, **kwargs)
        self.priority = 180
        self.hard_timeout = 10
        self.switch_table = {}
        self.G = nx.MultiDiGraph()
        self.datapaths = {}
        self.reroute_path = []
        self.activedataplane = []
        self.edge_list = [('edge1', 'superedge'), ('edge2', 'superedge'), ('edge3', 'superedge'),
            ('edge1', 'edge2'), ('edge1', 'edge4'),
            ('edge2', 'edge1'), ('edge2', 'edge3'), ('edge2', 'edge5'),
            ('edge3', 'edge2'), ('edge3', 'edge6'),
            ('edge4', 'edge1'), ('edge4', 'edge5'),
            ('edge5', 'edge2'), ('edge5', 'edge4'), ('edge5', 'edge6'),
            ('edge6', 'edge3'), ('edge6', 'edge5')
            ]
        '''
            weight of every edge is 1 because hop count between edges is one.            
        '''
        self.weight_edge_list = {('edge1', 'superedge'): 1, ('edge2', 'superedge'): 1, ('edge3', 'superedge'): 1,
            ('edge1', 'edge2'): 1, ('edge1', 'edge4'): 1,
            ('edge2', 'edge1'): 1, ('edge2', 'edge3'): 1, ('edge2', 'edge5'): 1,
            ('edge3', 'edge2'): 1, ('edge3', 'edge6'): 1,
            ('edge4', 'edge1'): 1, ('edge4', 'edge5'): 1,
            ('edge5', 'edge2'): 1, ('edge5', 'edge4'): 1, ('edge5', 'edge6'): 1,
            ('edge6', 'edge3'): 1, ('edge6', 'edge5'): 1
        }
        self.concave_edge_list = {('edge1', 'superedge'): 0, ('edge2', 'superedge'): 0, ('edge3', 'superedge'): 0,
            ('edge1', 'edge2'): 0, ('edge1', 'edge4'): 0,
            ('edge2', 'edge1'): 0, ('edge2', 'edge3'): 0, ('edge2', 'edge5'): 0,
            ('edge3', 'edge2'): 0, ('edge3', 'edge6'): 0,
            ('edge4', 'edge1'): 0, ('edge4', 'edge5'): 0,
            ('edge5', 'edge2'): 0, ('edge5', 'edge4'): 0, ('edge5', 'edge6'): 0,
            ('edge6', 'edge3'): 0, ('edge6', 'edge5'): 0
        }
        self.CPU_edge_list = {('edge1', 'superedge'): 0, ('edge2', 'superedge'): 0, ('edge3', 'superedge'): 0,
            ('edge1', 'edge2'): 0, ('edge1', 'edge4'): 0,
            ('edge2', 'edge1'): 0, ('edge2', 'edge3'): 0, ('edge2', 'edge5'): 0,
            ('edge3', 'edge2'): 0, ('edge3', 'edge6'): 0,
            ('edge4', 'edge1'): 0, ('edge4', 'edge5'): 0,
            ('edge5', 'edge2'): 0, ('edge5', 'edge4'): 0, ('edge5', 'edge6'): 0,
            ('edge6', 'edge3'): 0, ('edge6', 'edge5'): 0
        }
        self.CPU_list = {
            'edge1':0,
            'edge2':0,
            'edge3':0,
            'edge4':0,
            'edge5':0,
            'edge6':0            
        }        
        
        self.monitor_thread = hub.spawn(self._monitor)
        self.monitor_client_conn = hub.spawn(self._monitor_client_conn)
        self.interval_time = 10
        
    def get_datapath_id(self, edgeName):
        if edgeName == 'edge1': return 1
        elif edgeName == 'edge2': return 2
        elif edgeName == 'edge3': return 3
        elif edgeName == 'edge4': return 4
        elif edgeName == 'edge5': return 5
        elif edgeName == 'edge6': return 6
        elif edgeName == 'superedge': return 7
    
    def getIPFromName(self, edgeName):
        if edgeName == 'edge1': return e1ip
        elif edgeName == 'edge2': return e2ip
        elif edgeName == 'edge3': return e3ip
        elif edgeName == 'edge4': return e4ip
        elif edgeName == 'edge5': return e5ip
        elif edgeName == 'edge6': return e6ip
        elif edgeName == 'superedge': return superEdgeip
    
    def getMacFromName(self, edgeName):
        if edgeName == 'edge1': return e1mac
        elif edgeName == 'edge2': return e2mac
        elif edgeName == 'edge3': return e3mac
        elif edgeName == 'edge4': return e4mac
        elif edgeName == 'edge5': return e5mac
        elif edgeName == 'edge6': return e6mac
        elif edgeName == 'superedge': return superEdgeMac
    
    def getDeviceNameFromMac(self, mac):
        if mac == e1mac: return 'edge1'
        elif mac == e2mac: return 'edge2'
        elif mac == e3mac: return 'edge3'
        elif mac == e4mac: return 'edge4'
        elif mac == e5mac: return 'edge5'
        elif mac == e6mac: return 'edge6'
        elif mac == superEdgeMac: return 'superedge'
        
    def getDeviceNameFromIPAddress(self, ip):
        if ip == e1ip: return 'edge1'
        elif ip == e2ip: return 'edge2'
        elif ip == e3ip: return 'edge3'
        elif ip == e4ip: return 'edge4'
        elif ip == e5ip: return 'edge5'
        elif ip == e6ip: return 'edge6'
        elif ip == superEdgeip : return 'superedge'
    
    def _monitor_client_conn(self):
        while True:
            m_conn, addr = socket_server.accept()            
            self.logger.debug('Connected by', addr)
            while True:
                encoded_data = m_conn.recv(1024)
                if not encoded_data:
                    break
                else: 
                    data = encoded_data.decode()                                   
                    if '$' not in data:                    
                        if 'edge1' == data or 'edge2' == data or 'edge3' == data or 'edge4' == data or 'edge5' == data or 'edge6' == data : 
                            m_conn.sendall((data + ' is connected').encode())                                        
                            self.logger.debug('%s is connected', data) 
                    else:                        
                        formatted_data = data.split('$')
                        self.CPU_list[formatted_data[0]] = formatted_data[2]                        
            m_conn.close()             

    def add_multi_link_attributes(self):
        """
        This funtion is to add the multiple link attributes to graph G
                self.G : graph
                self.weight_edge_list : link attribute 1
                self.CPU_edge_list : link attribute 2        
        """                  
        for (u, v) in self.G.edges():
            # update CPU edge list
            self.CPU_edge_list[(u, v)] = float(self.CPU_list[u]) / 100
            self.G.add_edge(u, v, w = self.weight_edge_list[(u,v)], 
                            c2= self.CPU_edge_list[(u,v)])        

    def remove_Edge(self, rm_edge_list):
        """
        This function is to remove edges in the rm_edge_list from G
        """
        self.G.remove_edges_from(rm_edge_list)
        self.G.edges()
        return self.G

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

    def rm_edge_constraint(self,Cons):
        rm_edge_list = []
        for u, v, data in self.G.edges(data=True):
            e = (u,v)
            cost = self.G.get_edge_data(*e)
            #self.logger.info(cost)
            if cost['c2'] >= Cons:
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

    def option1b_routing(self, S, D, L):
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
            while len(Shortest_path) != 0:
                path_cost = self.additive_path_cost(Shortest_path, 'w')                                 
                if path_cost <= L:
                    """go to concave cost"""
                    PathConcave_cost  = self.max_path_cost(Shortest_path, 'c2')                    
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
        return Opt_path

    def edge_monitor_routing(self, source, dest, L):                                                  
        self.G = nx.DiGraph()                                
        self.G.add_edges_from(self.edge_list)                 
        self.add_multi_link_attributes()  
        optimal_path = self.option1b_routing(source, dest, L)            
        return optimal_path    
        
    def _monitor(self):     
        while True:   
            if len(self.datapaths.keys()) == 7:       
                current_time = time.asctime(time.localtime(time.time()))          
                L = 6
                src = 'edge1'
                dest = 'superedge'
                self.G = nx.DiGraph()                                
                self.G.add_edges_from(self.edge_list)                 
                self.add_multi_link_attributes()                    
                
                self.logger.info("%s, Constraint %s", current_time, L)   
                network_table = PrettyTable(['link', 'weight', 'c2'])
                for i in range(len(self.edge_list)):
                    network_table.add_row([self.edge_list[i], self.weight_edge_list[self.edge_list[i]], self.CPU_edge_list[self.edge_list[i]]])
                print(network_table)
                                
                routing_table = PrettyTable(['source', 'dest', 'optimal path'])                                                     
                optimal_path = self.edge_monitor_routing(src, dest, L)                  
                routing_table.add_row([src, dest, optimal_path])              
                self.reroute_path.append(optimal_path)                
                
                optimal_path = self.edge_monitor_routing('edge2', dest, L)            
                routing_table.add_row(['edge2', dest, optimal_path])              
                self.reroute_path.append(optimal_path)
                
                optimal_path = self.edge_monitor_routing('edge3', dest, L)                  
                routing_table.add_row(['edge3', dest, optimal_path])              
                self.reroute_path.append(optimal_path)
                
                optimal_path = self.edge_monitor_routing('edge4', dest, L)                  
                routing_table.add_row(['edge4', dest, optimal_path])              
                self.reroute_path.append(optimal_path)
                
                optimal_path = self.edge_monitor_routing('edge5', dest, L)                  
                routing_table.add_row(['edge5', dest, optimal_path])              
                self.reroute_path.append(optimal_path)
                
                optimal_path = self.edge_monitor_routing('edge6', dest, L)                  
                routing_table.add_row(['edge6', dest, optimal_path])              
                self.reroute_path.append(optimal_path)
                                
                print(routing_table)                            
                                
                for datapath in self.datapaths.values():
                    self.send_get_config_request(datapath)
                                
            hub.sleep(self.interval_time)    

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
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                self.logger.info("(Switch ID %s),IP address is leaved %s in %s,0",
                                datapath.id, datapath.address, current_time)
                del self.datapaths[datapath.id]
                self.logger.info(
                    "Current Conneced Switches to RYU controller are %s", self.datapaths.keys())

    def write_dynamic_flowrules(self, datapath, parser, route, prioirtyControl):
        source = route[0]
        dest = route[len(route)-1]
    
        source_ip = self.getIPFromName(source)
        source_mac = self.getMacFromName(source)
    
        dest_ip = self.getIPFromName(dest)
        dest_mac = self.getMacFromName(dest)
        
        priority = self.priority - prioirtyControl
        
        if datapath.id == self.get_datapath_id(source):            
            hop = route[1]
            hop_mac = self.getMacFromName(hop)
            match = parser.OFPMatch(in_port=1, eth_type=0x0806, eth_src=source_mac, arp_spa=source_ip, arp_tpa=dest_ip)
            actions = [parser.OFPActionSetField(eth_src=source_mac), parser.OFPActionSetField(eth_dst=hop_mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, priority, match, actions, self.hard_timeout)
            
            match = parser.OFPMatch(in_port=1, eth_type=0x0800, eth_src=source_mac, ipv4_dst=dest_ip)
            actions = [parser.OFPActionSetField(eth_src=source_mac), parser.OFPActionSetField(eth_dst=hop_mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, priority, match, actions, self.hard_timeout)
        
        relay_list = route[1:-1]    
        for i in range(len(relay_list)):        
            if datapath.id == self.get_datapath_id(relay_list[i]):
                relay_ip = self.getIPFromName(relay_list[i])
                relay_mac = self.getMacFromName(relay_list[i])
                hop = route[2 + i]
                hop_mac = self.getMacFromName(hop)
                
                match = parser.OFPMatch(in_port=1, eth_type=0x0806, eth_dst=relay_mac, arp_tpa=dest_ip)
                actions = [parser.OFPActionSetField(eth_src=relay_mac), parser.OFPActionSetField(eth_dst=hop_mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
                self.add_flow(datapath, 0, priority, match, actions, self.hard_timeout)
                
                match = parser.OFPMatch(in_port=1, eth_type=0x0800, eth_dst=relay_mac, ipv4_dst=dest_ip)
                actions = [parser.OFPActionSetField(eth_src=relay_mac), parser.OFPActionSetField(eth_dst=hop_mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
                self.add_flow(datapath, 0, priority, match, actions, self.hard_timeout)
                
                reverse_hop = route[i]
                reverse_hop_mac = self.getMacFromName(reverse_hop)            
                match = parser.OFPMatch(in_port=1, eth_type=0x0806, eth_dst=relay_mac, arp_tpa=source_ip)
                actions = [parser.OFPActionSetField(eth_src=relay_mac), parser.OFPActionSetField(eth_dst=reverse_hop_mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
                self.add_flow(datapath, 0, priority, match, actions, self.hard_timeout)
                
                match = parser.OFPMatch(in_port=1, eth_type=0x0800, eth_dst=relay_mac, ipv4_dst=source_ip)
                actions = [parser.OFPActionSetField(eth_src=relay_mac), parser.OFPActionSetField(eth_dst=reverse_hop_mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
                self.add_flow(datapath, 0, priority, match, actions, self.hard_timeout)
        
        if datapath.id == self.get_datapath_id(dest):            
            hop = route[len(route)-2]
            hop_mac = self.getMacFromName(hop)
            match = parser.OFPMatch(in_port=1, eth_type=0x0806, eth_src=dest_mac, arp_tpa=source_ip)
            actions = [parser.OFPActionSetField(eth_src=dest_mac), parser.OFPActionSetField(eth_dst=hop_mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, priority, match, actions, self.hard_timeout)
            
            match = parser.OFPMatch(in_port=1, eth_type=0x0800, eth_src=dest_mac, ipv4_dst=source_ip)
            actions = [parser.OFPActionSetField(eth_src=dest_mac), parser.OFPActionSetField(eth_dst=hop_mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, priority, match, actions, self.hard_timeout)

    def send_get_config_request(self, datapath):
        ofp_parser = datapath.ofproto_parser
        req = ofp_parser.OFPGetConfigRequest(datapath)
        datapath.send_msg(req)
    
    @set_ev_cls(ofp_event.EventOFPGetConfigReply, MAIN_DISPATCHER)
    def get_config_reply_handler(self,ev):        
        datapath = ev.msg.datapath
        parser = datapath.ofproto_parser     
        index = 1   
        for route in self.reroute_path:            
            self.write_dynamic_flowrules(datapath, parser, route, index)
            index = index + 1


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
                in_port=1, eth_type=0x0806, eth_dst=e1mac, arp_tpa=superEdgeip)
            actions = [parser.OFPActionSetField(eth_src=e1mac), parser.OFPActionSetField(
                eth_dst=superEdgeMac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)
# Relay to edge2
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e1mac, arp_tpa=e2ip)
            actions = [parser.OFPActionSetField(eth_src=e1mac), parser.OFPActionSetField(
                eth_dst=e2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)
# Relay To edge3
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e1mac, arp_tpa=e3ip)
            actions = [parser.OFPActionSetField(eth_src=e1mac), parser.OFPActionSetField(
                eth_dst=e2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

# Relay To edge4
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e1mac, arp_tpa=e4ip)
            actions = [parser.OFPActionSetField(eth_src=e1mac), parser.OFPActionSetField(
                eth_dst=e4mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=e1mac, ipv4_dst=e4ip)
            actions = [parser.OFPActionSetField(eth_src=e1mac), parser.OFPActionSetField(
                eth_dst=e4mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 160, match, actions, 0)


# Connect edge3
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_src=e1mac, arp_tpa=e3ip)
            actions = [parser.OFPActionSetField(eth_src=e1mac), parser.OFPActionSetField(
                eth_dst=e2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 160, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=e1mac, ipv4_dst=e3ip)
            actions = [parser.OFPActionSetField(eth_src=e1mac), parser.OFPActionSetField(
                eth_dst=e2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 160, match, actions, 0)


#################################
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst="FF:FF:FF:FF:FF:FF", arp_tpa=e1ip)
            self.add_flow(datapath, 0, 170, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=e1ip, arp_tpa=superEdgeip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e1ip, ipv4_dst=superEdgeip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=e1ip, arp_tpa=e2ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e1ip, ipv4_dst=e2ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=e1ip, arp_tpa=e4ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e1ip, ipv4_dst=e4ip)
            self.add_flow(datapath, 0, 165, match, [], 0)


            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=e2ip, arp_tpa=e3ip)
            self.add_flow(datapath, 0, 165, match, [], 0)


            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e2ip, ipv4_dst=e3ip)
            self.add_flow(datapath, 0, 165, match, [], 0)
# NewRule
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=e1mac, eth_dst=superEdgeMac, ipv4_src=e2ip, ipv4_dst=superEdgeip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=e1mac, eth_dst=e4mac, ipv4_src=superEdgeip, ipv4_dst=e4ip)
            self.add_flow(datapath, 0, 165, match, [], 0)


        if dp.id == 2:
            self.logger.info("MeshNode_2 is connected")

# Relay To edge3
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e2mac, arp_tpa=e3ip)
            actions = [parser.OFPActionSetField(eth_src=e2mac), parser.OFPActionSetField(
                eth_dst=e3mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

# Relay To edge5
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e2mac, arp_tpa=e5ip)
            actions = [parser.OFPActionSetField(eth_src=e2mac), parser.OFPActionSetField(
                eth_dst=e5mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

# Relay To edge1
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e2mac, arp_tpa=e1ip)
            actions = [parser.OFPActionSetField(eth_src=e2mac), parser.OFPActionSetField(
                eth_dst=e1mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)
# Relay to superedge
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e2mac, arp_tpa=superEdgeip)
            actions = [parser.OFPActionSetField(eth_src=e2mac), parser.OFPActionSetField(
                eth_dst=superEdgeMac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

###########################################################################################

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst="FF:FF:FF:FF:FF:FF", arp_tpa=e2ip)
            self.add_flow(datapath, 0, 170, match, [], 0)


            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=e2ip, arp_tpa=superEdgeip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e2ip, ipv4_dst=superEdgeip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=e2ip, arp_tpa=e3ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e2ip, ipv4_dst=e3ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=e2ip, arp_tpa=e1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e2ip, ipv4_dst=e1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)


           
        if dp.id == 3:
            self.logger.info("MeshNode_3 is connected")

# Relay To superedge
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e3mac, arp_tpa=superEdgeip)
            actions = [parser.OFPActionSetField(eth_src=e3mac), parser.OFPActionSetField(
                eth_dst=superEdgeMac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)
# Relay To edge1
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e3mac, arp_tpa=e1ip)
            actions = [parser.OFPActionSetField(eth_src=e3mac), parser.OFPActionSetField(
                eth_dst=e2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)
# Relay To edge2
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e3mac, arp_tpa=e2ip)
            actions = [parser.OFPActionSetField(eth_src=e3mac), parser.OFPActionSetField(
                eth_dst=e2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

# Relay To edge6
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e3mac, arp_tpa=e6ip)
            actions = [parser.OFPActionSetField(eth_src=e3mac), parser.OFPActionSetField(
                eth_dst=e6mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

# connect to edge1
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_src=e3mac, arp_tpa=e1ip)
            actions = [parser.OFPActionSetField(eth_src=e3mac), parser.OFPActionSetField(
                eth_dst=e2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 150, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=e3mac, ipv4_dst=e1ip)
            actions = [parser.OFPActionSetField(eth_src=e3mac), parser.OFPActionSetField(
                eth_dst=e2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 150, match, actions, 0)
# connect to edge3

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst="FF:FF:FF:FF:FF:FF", arp_tpa=e3ip)
            self.add_flow(datapath, 0, 170, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=e3ip, arp_tpa=superEdgeip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e3ip, ipv4_dst=superEdgeip)
            self.add_flow(datapath, 0, 165, match, [], 0)


            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e3ip, ipv4_dst=e2ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=e3ip, arp_tpa=e2ip)
            self.add_flow(datapath, 0, 165, match, [], 0)


            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e3ip, ipv4_dst=e6ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=e3ip, arp_tpa=e6ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=e2ip, arp_tpa=e1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e2ip, ipv4_dst=e1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)


        if dp.id == 7:
            self.logger.info("SuperEdge is connected")

# edge4
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_src=superEdgeMac, arp_tpa=e4ip)
            actions = [parser.OFPActionSetField(eth_src=superEdgeMac), parser.OFPActionSetField(
                eth_dst=e1mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 150, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=superEdgeMac, ipv4_dst=e4ip)
            actions = [parser.OFPActionSetField(eth_src=superEdgeMac), parser.OFPActionSetField(
                eth_dst=e1mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 150, match, actions, 0)


# edge5
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_src=superEdgeMac, arp_tpa=e5ip)
            actions = [parser.OFPActionSetField(eth_src=superEdgeMac), parser.OFPActionSetField(
                eth_dst=e2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 150, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=superEdgeMac, ipv4_dst=e5ip)
            actions = [parser.OFPActionSetField(eth_src=superEdgeMac), parser.OFPActionSetField(
                eth_dst=e2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 150, match, actions, 0)

# edge6
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_src=superEdgeMac, arp_tpa=e6ip)
            actions = [parser.OFPActionSetField(eth_src=superEdgeMac), parser.OFPActionSetField(
                eth_dst=e3mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 150, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=superEdgeMac, ipv4_dst=e6ip)
            actions = [parser.OFPActionSetField(eth_src=superEdgeMac), parser.OFPActionSetField(
                eth_dst=e3mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 150, match, actions, 0)

# To Prevent Looping
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst="FF:FF:FF:FF:FF:FF", arp_tpa=superEdgeip)
            self.add_flow(datapath, 0, 170, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=superEdgeip, ipv4_dst=e1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=superEdgeip, arp_tpa=e1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

# Not to relay other packets
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e1ip, ipv4_dst=e2ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e1ip, ipv4_dst=e3ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

        if dp.id == 4:
            self.logger.info("MeshNode_4 is connected")
# Relay to SuperEdge
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e4mac, arp_tpa=superEdgeip)
            actions = [parser.OFPActionSetField(eth_src=e4mac), parser.OFPActionSetField(
                eth_dst=e1mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

# Relay to edge5
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e4mac, arp_tpa=e5ip)
            actions = [parser.OFPActionSetField(eth_src=e4mac), parser.OFPActionSetField(
                eth_dst=e5mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

# Relay To edge6
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e4mac, arp_tpa=e6ip)
            actions = [parser.OFPActionSetField(eth_src=e4mac), parser.OFPActionSetField(
                eth_dst=e5mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

# Connect Raspi6
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_src=e4mac, arp_spa=e4ip, arp_tpa=e6ip)
            actions = [parser.OFPActionSetField(eth_src=e4mac), parser.OFPActionSetField(
                eth_dst=e5mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 160, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=e4mac, ipv4_dst=e6ip)
            actions = [parser.OFPActionSetField(eth_src=e4mac), parser.OFPActionSetField(
                eth_dst=e5mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 160, match, actions, 0)

# Connect SuperEdge
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_src=e4mac, arp_spa=e4ip, arp_tpa=superEdgeip)
            actions = [parser.OFPActionSetField(eth_src=e4mac), parser.OFPActionSetField(
                eth_dst=e1mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 160, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=e4mac, ipv4_dst=superEdgeip)
            actions = [parser.OFPActionSetField(eth_src=e4mac), parser.OFPActionSetField(
                eth_dst=e1mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 160, match, actions, 0)

# To Prevent Duplicate Problem
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst="FF:FF:FF:FF:FF:FF", arp_tpa=e4ip)
            self.add_flow(datapath, 0, 170, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=e4ip, arp_tpa=e1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e4ip, ipv4_dst=e1ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=e4ip, arp_tpa=e5ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e4ip, ipv4_dst=e5ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=e5ip, arp_tpa=e6ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e5ip, ipv4_dst=e6ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

        if dp.id == 5:
            self.logger.info("MeshNode_5 is connected")

# Relay To edge 3
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e5mac, arp_tpa=e6ip)
            actions = [parser.OFPActionSetField(eth_src=e5mac), parser.OFPActionSetField(
                eth_dst=e6mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

# Relay To edge 4
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e5mac, arp_tpa=e4ip)
            actions = [parser.OFPActionSetField(eth_src=e5mac), parser.OFPActionSetField(
                eth_dst=e4mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

# Relay To edge1
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e5mac, arp_tpa=e6ip)
            actions = [parser.OFPActionSetField(eth_src=e5mac), parser.OFPActionSetField(
                eth_dst=e6mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)
# Relay to  superedge
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e5mac, arp_tpa=superEdgeip)
            actions = [parser.OFPActionSetField(eth_src=e5mac), parser.OFPActionSetField(
                eth_dst=e4mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)

# Connect superedge
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_src=e5mac, arp_spa=e5ip, arp_tpa=superEdgeip)
            actions = [parser.OFPActionSetField(eth_src=e5mac), parser.OFPActionSetField(
                eth_dst=e2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 160, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=e5mac, ipv4_dst=superEdgeip)
            actions = [parser.OFPActionSetField(eth_src=e5mac), parser.OFPActionSetField(
                eth_dst=e2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 160, match, actions, 0)

# To Prevent Duplicate Problem
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst="FF:FF:FF:FF:FF:FF", arp_tpa=e5ip)
            self.add_flow(datapath, 0, 170, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=e5ip, arp_tpa=e6ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e5ip, ipv4_dst=e6ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=e5ip, arp_tpa=e2ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e5ip, ipv4_dst=e2ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=e5ip, arp_tpa=e4ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e5ip, ipv4_dst=e4ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=e4ip, arp_tpa=superEdgeip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e4ip, ipv4_dst=superEdgeip)
            self.add_flow(datapath, 0, 165, match, [], 0)


        if dp.id == 6:
            self.logger.info("MeshNode_6 is connected")
# Relay To edge6
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e6mac, arp_tpa=e4ip)
            actions = [parser.OFPActionSetField(eth_src=e6mac), parser.OFPActionSetField(
                eth_dst=e5mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)
# Relay To edge5
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e6mac, arp_tpa=e5ip)
            actions = [parser.OFPActionSetField(eth_src=e6mac), parser.OFPActionSetField(
                eth_dst=e5mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 164, match, actions, 0)
# superedge
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_src=e6mac, arp_spa=e6ip, arp_tpa=superEdgeip)
            actions = [parser.OFPActionSetField(eth_src=e6mac), parser.OFPActionSetField(
                eth_dst=e3mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 160, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=e6mac, ipv4_dst=superEdgeip)
            actions = [parser.OFPActionSetField(eth_src=e6mac), parser.OFPActionSetField(
                eth_dst=e3mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 160, match, actions, 0)

# edge4
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_src=e6mac, arp_spa=e6ip, arp_tpa=e4ip)
            actions = [parser.OFPActionSetField(eth_src=e6mac), parser.OFPActionSetField(
                eth_dst=e5mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 150, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=e6mac, ipv4_dst=e4ip)
            actions = [parser.OFPActionSetField(eth_src=e6mac), parser.OFPActionSetField(
                eth_dst=e5mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 150, match, actions, 0)
#########################

# To Prevent Duplicate
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst="FF:FF:FF:FF:FF:FF", arp_tpa=e6ip)
            self.add_flow(datapath, 0, 170, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e6ip, ipv4_dst=e5ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=e6ip, arp_tpa=e5ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e6ip, ipv4_dst=e3ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=e6ip, arp_tpa=e3ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=e5ip, arp_tpa=e4ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, arp_spa=e5ip, arp_tpa=e4ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e5ip, ipv4_dst=e4ip)
            self.add_flow(datapath, 0, 165, match, [], 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, ipv4_src=e5ip, ipv4_dst=superEdgeip)
            self.add_flow(datapath, 0, 165, match, [], 0)



