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
        self.datapaths = {}
        self.activedataplane = []

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
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                self.logger.info("(Switch ID %s),IP address is leaved %s in %s,0",
                                 datapath.id, datapath.address, current_time)
                del self.datapaths[datapath.id]
                self.logger.info(
                    "Current Conneced Switches to RYU controller are %s", self.datapaths.keys())

