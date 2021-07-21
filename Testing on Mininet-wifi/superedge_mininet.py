#testing on mininet-wifi by PPTLT
#program writing in progress !!!
#controller program 

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib import hub
import time
import os
edge1="192.168.10.1"
edge2="192.168.10.2"
edge3="192.168.10.3"
edge4="192.168.10.4"
edge5="192.168.10.5"
edge6="192.168.10.6"


class node_failure (app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self,*args,**kwargs):
        super(node_failure,self).__init__(*args,**kwargs)
        self.switch_table = {}
        self.datapaths = {}
		#self.monitor_thread = hub.spawn(self._monitor)
        #require to send configuration request message in every 8 seconds

#Define the funtion to add flow rules 
    def add_flow(self,datapath,table,priority,match,actions,hard):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
        mod = parser.OFPFlowMod(datapath=datapath,table_id=table,command=ofproto.OFPFC_ADD,
                                priority=priority,match=match,instructions=inst,hard_timeout=hard)
        datapath.send_msg(mod)

#Define the function to add flow rule with the action of gototable
    def add_gototable(self,datapath,table,n,priority,match,hard): #n is a number of table
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        inst = [parser.OFPInstructionGotoTable(n)]
        mod = parser.OFPFlowMod(datapath=datapath,table_id=table,command=ofproto.OFPFC_ADD,
                                priority=priority,match=match,hard_timeout=hard,instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):

        dp = ev.msg.datapath
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        self.logger.info("Switch_ID %s is connected,1",dp.id)

	if dp.id == 1:
	    match = parser.OFPMatch(in_port=2, eth_type=0x0806,arp_spa=edge1)
            #actions = [parser.OFPActionOutput(3)]
            #self.add_flow(datapath,0,160,match,actions,0)

            match = parser.OFPMatch(in_port=2,eth_type=0x0800,ipv4_src=edge1)
            #actions = [parser.OFPActionOutput(3)]
            #self.add_flow(datapath,0,160,match,actions,0)

	    match = parser.OFPMatch(in_port=3, eth_type=0x0806,arp_tpa=edge1)
            #actions = [parser.OFPActionOutput(2)]
            #self.add_flow(datapath,0,160,match,actions,0)

            match = parser.OFPMatch(in_port=3,eth_type=0x0800,ipv4_dst=edge1)
            #actions = [parser.OFPActionOutput(2)]
            #self.add_flow(datapath,0,160,match,actions,0)

#ToPreventInfinteLoopProblematAP
            match = parser.OFPMatch(in_port=3)
            self.add_flow(datapath,0,1,match,[],0)

	if dp.id == 2:
	    match = parser.OFPMatch(in_port=2, eth_type=0x0806,arp_spa=edge2)
            #actions = [parser.OFPActionOutput(3)]
            #self.add_flow(datapath,0,160,match,actions,0)

            match = parser.OFPMatch(in_port=2,eth_type=0x0800,ipv4_src=edge2)
            #actions = [parser.OFPActionOutput(3)]
            #self.add_flow(datapath,0,160,match,actions,0)

	    match = parser.OFPMatch(in_port=3, eth_type=0x0806,arp_tpa=edge2)
            #actions = [parser.OFPActionOutput(2)]
            #self.add_flow(datapath,0,160,match,actions,0)

            match = parser.OFPMatch(in_port=3,eth_type=0x0800,ipv4_dst=edge2)
            #actions = [parser.OFPActionOutput(2)]
            #self.add_flow(datapath,0,160,match,actions,0)

#ToPreventInfinteLoopProblematAP
            match = parser.OFPMatch(in_port=3)
            self.add_flow(datapath,0,1,match,[],0)

	if dp.id == 3:
	    match = parser.OFPMatch(in_port=2, eth_type=0x0806,arp_spa=edge3)
            #actions = [parser.OFPActionOutput(3)]
            #self.add_flow(datapath,0,160,match,actions,0)

            match = parser.OFPMatch(in_port=2,eth_type=0x0800,ipv4_src=edge3)
            #actions = [parser.OFPActionOutput(3)]
            #self.add_flow(datapath,0,160,match,actions,0)

	    match = parser.OFPMatch(in_port=3, eth_type=0x0806,arp_tpa=edge3)
            #actions = [parser.OFPActionOutput(2)]
            #self.add_flow(datapath,0,160,match,actions,0)

            match = parser.OFPMatch(in_port=3,eth_type=0x0800,ipv4_dst=edge3)
            #actions = [parser.OFPActionOutput(2)]
            #self.add_flow(datapath,0,160,match,actions,0)

#ToPreventInfinteLoopProblematAP
            match = parser.OFPMatch(in_port=3)
            self.add_flow(datapath,0,1,match,[],0)

	if dp.id == 4:
	    match = parser.OFPMatch(in_port=2, eth_type=0x0806,arp_spa=edge4)
            #actions = [parser.OFPActionOutput(3)]
            #self.add_flow(datapath,0,160,match,actions,0)

            match = parser.OFPMatch(in_port=2,eth_type=0x0800,ipv4_src=edge4)
            #actions = [parser.OFPActionOutput(3)]
            #self.add_flow(datapath,0,160,match,actions,0)

	    match = parser.OFPMatch(in_port=3, eth_type=0x0806,arp_tpa=edge4)
            #actions = [parser.OFPActionOutput(2)]
            #self.add_flow(datapath,0,160,match,actions,0)

            match = parser.OFPMatch(in_port=3,eth_type=0x0800,ipv4_dst=edge4)
            #actions = [parser.OFPActionOutput(2)]
            #self.add_flow(datapath,0,160,match,actions,0)

#ToPreventInfinteLoopProblematAP
            match = parser.OFPMatch(in_port=3)
            self.add_flow(datapath,0,1,match,[],0)

	if dp.id == 5:
	    match = parser.OFPMatch(in_port=2, eth_type=0x0806,arp_spa=edge5)
            #actions = [parser.OFPActionOutput(3)]
            #self.add_flow(datapath,0,160,match,actions,0)

            match = parser.OFPMatch(in_port=2,eth_type=0x0800,ipv4_src=edge5)
            #actions = [parser.OFPActionOutput(3)]
            #self.add_flow(datapath,0,160,match,actions,0)

	    match = parser.OFPMatch(in_port=3, eth_type=0x0806,arp_tpa=edge5)
            #actions = [parser.OFPActionOutput(2)]
            #self.add_flow(datapath,0,160,match,actions,0)

            match = parser.OFPMatch(in_port=3,eth_type=0x0800,ipv4_dst=edge5)
            #actions = [parser.OFPActionOutput(2)]
            #self.add_flow(datapath,0,160,match,actions,0)

#ToPreventInfinteLoopProblematAP
            match = parser.OFPMatch(in_port=3)
            self.add_flow(datapath,0,1,match,[],0)

	if dp.id == 6:
	    match = parser.OFPMatch(in_port=2, eth_type=0x0806,arp_spa=edge6)
            #actions = [parser.OFPActionOutput(3)]
            #self.add_flow(datapath,0,160,match,actions,0)

            match = parser.OFPMatch(in_port=2,eth_type=0x0800,ipv4_src=edge6)
            #actions = [parser.OFPActionOutput(3)]
            #self.add_flow(datapath,0,160,match,actions,0)

	    match = parser.OFPMatch(in_port=3, eth_type=0x0806,arp_tpa=edge6)
            #actions = [parser.OFPActionOutput(2)]
            #self.add_flow(datapath,0,160,match,actions,0)

            match = parser.OFPMatch(in_port=3,eth_type=0x0800,ipv4_dst=edge6)
            #actions = [parser.OFPActionOutput(2)]
            #self.add_flow(datapath,0,160,match,actions,0)

#ToPreventInfinteLoopProblematAP
            match = parser.OFPMatch(in_port=3)
            self.add_flow(datapath,0,1,match,[],0)

	