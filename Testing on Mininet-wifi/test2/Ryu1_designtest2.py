#Ryu1 for designtest2

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
#Datapath ID of each wireless node

#MAC addresses of each wireless nodes

#IP addresses of each wireless node
gw1ip="192.168.1.8"
r1ip="192.168.1.1"
r2ip="192.168.1.2"
r3ip="192.168.1.3"
r4ip="192.168.1.4"
r5ip="192.168.1.5"
r6ip="192.168.1.6"
gw2ip="192.168.1.9"

gw1mac="00:00:00:00:00:70"
gw2mac="00:00:00:00:00:80"
r1mac="00:00:00:00:00:10"
r2mac="00:00:00:00:00:20"
r3mac="00:00:00:00:00:30"
r4mac="00:00:00:00:00:40"
r5mac="00:00:00:00:00:50"
r6mac="00:00:00:00:00:60"

gw1data = 'gw1-wlan1'
gw2data = 'gw2-wlan1'
ap1data = 'ap1-wlan1'
ap2data = 'ap2-wlan1'
ap3data = 'ap3-wlan1'
ap4data = 'ap4-wlan1'
ap5data = 'ap5-wlan1'
ap6data = 'ap6-wlan1'

gw1control = 'gw1-eth2'
gw2control = 'gw2-eth2'
ap1control = 'ap1-eth2'
ap2control = 'ap2-eth2'
ap3control = 'ap3-eth2'
ap4control = 'ap4-eth2'
ap5control = 'ap5-eth2'
ap6control = 'ap6-eth2'

dataplane=[gw1data,gw2data,ap1data,ap2data,ap3data,ap4data,ap5data,ap6data]
controlplane=[gw1control,gw2control,ap1control,ap2control,ap3control,ap4control,ap5control,ap6control]
current_dataplane=[]


class node_failure (app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self,*args,**kwargs):
        super(node_failure,self).__init__(*args,**kwargs)
        self.switch_table = {}
        self.datapaths = {}
        self.activedataplane = []
#        self.monitor_thread = hub.spawn(self._monitor)
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
        local = datapath.ofproto.OFPP_LOCAL
#        inport = datapath.ofproto.OFPP_INPORT
        self.logger.info("Switch_ID %s is connected,1",dp.id)

	if dp.id == 1:
            self.logger.info("MeshNode_1 is connected")
###Realy to Gateway1
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_dst=r1mac,arp_tpa=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r1mac),parser.OFPActionSetField(eth_dst=gw1mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)
###Relay to Raspi2
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_dst=r1mac,arp_tpa=r2ip)
            actions = [parser.OFPActionSetField(eth_src=r1mac),parser.OFPActionSetField(eth_dst=r2mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)
###Relay To Raspi3
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_dst=r1mac,arp_tpa=r3ip)
            actions = [parser.OFPActionSetField(eth_src=r1mac),parser.OFPActionSetField(eth_dst=r2mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)
##Relay To Gateway2
	    match = parser.OFPMatch(in_port=1,eth_type=0x0806,eth_dst=r1mac,arp_tpa=gw2ip)
            actions = [parser.OFPActionSetField(eth_src=r1mac),parser.OFPActionSetField(eth_dst=r2mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)
###Connect Raspi3
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_src=r1mac,arp_tpa=r3ip)
            actions = [parser.OFPActionSetField(eth_src=r1mac),parser.OFPActionSetField(eth_dst=r2mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,eth_src=r1mac,ipv4_dst=r3ip)
            actions = [parser.OFPActionSetField(eth_src=r1mac),parser.OFPActionSetField(eth_dst=r2mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)
##Connect Gateway2
	    match = parser.OFPMatch(in_port=1,eth_type=0x0806,eth_src=r1mac,arp_tpa=gw2ip)
            actions = [parser.OFPActionSetField(eth_src=r1mac),parser.OFPActionSetField(eth_dst=r2mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)

	    match = parser.OFPMatch(in_port=1,eth_type=0x0800,eth_src=r1mac,ipv4_dst=gw2ip)
            actions = [parser.OFPActionSetField(eth_src=r1mac),parser.OFPActionSetField(eth_dst=r2mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)

#################################
	    match = parser.OFPMatch(in_port=1,eth_type=0x0806,eth_dst="FF:FF:FF:FF:FF:FF",arp_tpa=r1ip)
            self.add_flow(datapath,0,170,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r1ip,arp_tpa=gw1ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r1ip,ipv4_dst=gw1ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r1ip,arp_tpa=r2ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r1ip,ipv4_dst=r2ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r2ip,arp_tpa=gw2ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r2ip,arp_tpa=r3ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r2ip,ipv4_dst=gw2ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r2ip,ipv4_dst=r3ip)
            self.add_flow(datapath,0,165,match,[],0)
###NewRule
	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,eth_src=r1mac,eth_dst=gw1mac,ipv4_src=r2ip,ipv4_dst=gw1ip)
            self.add_flow(datapath,0,165,match,[],0)



	if dp.id == 2:
            self.logger.info("MeshNode_2 is connected")

##Relay To Raspi 3
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_dst=r2mac,arp_tpa=r3ip)
            actions = [parser.OFPActionSetField(eth_src=r2mac),parser.OFPActionSetField(eth_dst=r3mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)
#######Relay To Raspi1
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_dst=r2mac,arp_tpa=r1ip)
            actions = [parser.OFPActionSetField(eth_src=r2mac),parser.OFPActionSetField(eth_dst=r1mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)
######Relay to Gateway 1
	    match = parser.OFPMatch(in_port=1,eth_type=0x0806,eth_dst=r2mac,arp_tpa=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r2mac),parser.OFPActionSetField(eth_dst=r1mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)
######Relay to Gateway 2
	    match = parser.OFPMatch(in_port=1,eth_type=0x0806,eth_dst=r2mac,arp_tpa=gw2ip)
            actions = [parser.OFPActionSetField(eth_src=r2mac),parser.OFPActionSetField(eth_dst=r3mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)

######Connect Gateway 1
	    match = parser.OFPMatch(in_port=1,eth_type=0x0800,eth_src=r2mac,ipv4_dst=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r2mac),parser.OFPActionSetField(eth_dst=r1mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)

	    match = parser.OFPMatch(in_port=1,eth_type=0x0806,eth_src=r2mac,arp_tpa=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r2mac),parser.OFPActionSetField(eth_dst=r1mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)

#######Connect Gateway2
	    match = parser.OFPMatch(in_port=1,eth_type=0x0800,eth_src=r2mac,ipv4_dst=gw2ip)
            actions = [parser.OFPActionSetField(eth_src=r2mac),parser.OFPActionSetField(eth_dst=r3mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)

	    match = parser.OFPMatch(in_port=1,eth_type=0x0806,eth_src=r2mac,arp_tpa=gw2ip)
            actions = [parser.OFPActionSetField(eth_src=r2mac),parser.OFPActionSetField(eth_dst=r3mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)

###########################################################################################

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_dst="FF:FF:FF:FF:FF:FF",arp_tpa=r2ip)
            self.add_flow(datapath,0,170,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r2ip,arp_tpa=r3ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r2ip,ipv4_dst=r3ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r2ip,arp_tpa=r1ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r2ip,ipv4_dst=r1ip)
            self.add_flow(datapath,0,165,match,[],0)


	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r1ip,arp_tpa=gw1ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r3ip,arp_tpa=gw2ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r1ip,ipv4_dst=gw1ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r3ip,ipv4_dst=gw2ip)
            self.add_flow(datapath,0,165,match,[],0)


	if dp.id == 3:
            self.logger.info("MeshNode_3 is connected")
###Relay To Gateway2
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_dst=r3mac,arp_tpa=gw2ip)
            actions = [parser.OFPActionSetField(eth_src=r3mac),parser.OFPActionSetField(eth_dst=gw2mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)
###Relay To Gateway1
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_dst=r3mac,arp_tpa=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r3mac),parser.OFPActionSetField(eth_dst=r2mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)
###Relay To Raspi1
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_dst=r3mac,arp_tpa=r1ip)
            actions = [parser.OFPActionSetField(eth_src=r3mac),parser.OFPActionSetField(eth_dst=r2mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)
###Relay To Raspi2
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_dst=r3mac,arp_tpa=r2ip)
            actions = [parser.OFPActionSetField(eth_src=r3mac),parser.OFPActionSetField(eth_dst=r2mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)
###Gateway1
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_src=r3mac,arp_tpa=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r3mac),parser.OFPActionSetField(eth_dst=r2mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,eth_src=r3mac,ipv4_dst=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r3mac),parser.OFPActionSetField(eth_dst=r2mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)

###Raspi1
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_src=r3mac,arp_tpa=r1ip)
            actions = [parser.OFPActionSetField(eth_src=r3mac),parser.OFPActionSetField(eth_dst=r2mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,150,match,actions,0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,eth_src=r3mac,ipv4_dst=r1ip)
            actions = [parser.OFPActionSetField(eth_src=r3mac),parser.OFPActionSetField(eth_dst=r2mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,150,match,actions,0)
#########################3

	    match = parser.OFPMatch(in_port=1,eth_type=0x0806,eth_dst="FF:FF:FF:FF:FF:FF",arp_tpa=r3ip)
            self.add_flow(datapath,0,170,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r3ip,ipv4_dst=gw2ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r3ip,arp_tpa=gw2ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r3ip,ipv4_dst=r2ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r3ip,arp_tpa=r2ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r2ip,arp_tpa=r1ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r2ip,arp_tpa=gw1ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r2ip,ipv4_dst=r1ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r2ip,ipv4_dst=gw1ip)
            self.add_flow(datapath,0,165,match,[],0)


	if dp.id == 7:
            self.logger.info("Gateway_1 is connected")
####Gateway2
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_src=gw1mac,arp_tpa=gw2ip)
            actions = [parser.OFPActionSetField(eth_src=gw1mac),parser.OFPActionSetField(eth_dst=r1mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,150,match,actions,0)


	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,eth_src=gw1mac,ipv4_dst=gw2ip)
            actions = [parser.OFPActionSetField(eth_src=gw1mac),parser.OFPActionSetField(eth_dst=r1mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,150,match,actions,0)

#######Raspi2
	    match = parser.OFPMatch(in_port=1,eth_type=0x0806,eth_src=gw1mac,arp_tpa=r2ip)
            actions = [parser.OFPActionSetField(eth_src=gw1mac),parser.OFPActionSetField(eth_dst=r1mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,150,match,actions,0)

	    match = parser.OFPMatch(in_port=1,eth_type=0x0800,eth_src=gw1mac,ipv4_dst=r2ip)
            actions = [parser.OFPActionSetField(eth_src=gw1mac),parser.OFPActionSetField(eth_dst=r1mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,150,match,actions,0)
#####Raspi3
	    match = parser.OFPMatch(in_port=1,eth_type=0x0806,eth_src=gw1mac,arp_tpa=r3ip)
            actions = [parser.OFPActionSetField(eth_src=gw1mac),parser.OFPActionSetField(eth_dst=r1mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)

	    match = parser.OFPMatch(in_port=1,eth_type=0x0800,eth_src=gw1mac,ipv4_dst=r3ip)
            actions = [parser.OFPActionSetField(eth_src=gw1mac),parser.OFPActionSetField(eth_dst=r1mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)


#######Raspi5
	    match = parser.OFPMatch(in_port=1,eth_type=0x0806,eth_src=gw1mac,arp_tpa=r5ip)
            actions = [parser.OFPActionSetField(eth_src=gw1mac),parser.OFPActionSetField(eth_dst=r4mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,150,match,actions,0)

	    match = parser.OFPMatch(in_port=1,eth_type=0x0800,eth_src=gw1mac,ipv4_dst=r5ip)
            actions = [parser.OFPActionSetField(eth_src=gw1mac),parser.OFPActionSetField(eth_dst=r4mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,150,match,actions,0)
#####Raspi6
	    match = parser.OFPMatch(in_port=1,eth_type=0x0806,eth_src=gw1mac,arp_tpa=r6ip)
            actions = [parser.OFPActionSetField(eth_src=gw1mac),parser.OFPActionSetField(eth_dst=r4mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)

	    match = parser.OFPMatch(in_port=1,eth_type=0x0800,eth_src=gw1mac,ipv4_dst=r6ip)
            actions = [parser.OFPActionSetField(eth_src=gw1mac),parser.OFPActionSetField(eth_dst=r4mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)



##To Prevent Looping
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_dst="FF:FF:FF:FF:FF:FF",arp_tpa=gw1ip)
            self.add_flow(datapath,0,170,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=gw1ip,ipv4_dst=r1ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=gw1ip,arp_tpa=r1ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=gw1ip,ipv4_dst=r4ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=gw1ip,arp_tpa=r4ip)
            self.add_flow(datapath,0,165,match,[],0)
##Not to relay other packets
	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r1ip,ipv4_dst=r2ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r1ip,ipv4_dst=r3ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r1ip,ipv4_dst=gw2ip)
            self.add_flow(datapath,0,165,match,[],0)


	if dp.id == 8:
            self.logger.info("Gateway_2 is connected")

####Gateway1
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_src=gw2mac,arp_tpa=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=gw2mac),parser.OFPActionSetField(eth_dst=r3mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,150,match,actions,0)


	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,eth_src=gw2mac,ipv4_dst=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=gw2mac),parser.OFPActionSetField(eth_dst=r3mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,150,match,actions,0)

#####Raspi1
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_src=gw2mac,arp_tpa=r1ip)
            actions = [parser.OFPActionSetField(eth_src=gw2mac),parser.OFPActionSetField(eth_dst=r3mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,150,match,actions,0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,eth_src=gw2mac,ipv4_dst=r1ip)
            actions = [parser.OFPActionSetField(eth_src=gw2mac),parser.OFPActionSetField(eth_dst=r3mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,150,match,actions,0)

#######Raspi2
	    match = parser.OFPMatch(in_port=1,eth_type=0x0806,eth_src=gw2mac,arp_tpa=r2ip)
            actions = [parser.OFPActionSetField(eth_src=gw2mac),parser.OFPActionSetField(eth_dst=r3mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)

	    match = parser.OFPMatch(in_port=1,eth_type=0x0800,eth_src=gw2mac,ipv4_dst=r2ip)
            actions = [parser.OFPActionSetField(eth_src=gw2mac),parser.OFPActionSetField(eth_dst=r3mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)

#####Raspi4
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_src=gw2mac,arp_tpa=r4ip)
            actions = [parser.OFPActionSetField(eth_src=gw2mac),parser.OFPActionSetField(eth_dst=r6mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,150,match,actions,0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,eth_src=gw2mac,ipv4_dst=r4ip)
            actions = [parser.OFPActionSetField(eth_src=gw2mac),parser.OFPActionSetField(eth_dst=r6mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,150,match,actions,0)

#######Raspi5
	    match = parser.OFPMatch(in_port=1,eth_type=0x0806,eth_src=gw2mac,arp_tpa=r5ip)
            actions = [parser.OFPActionSetField(eth_src=gw2mac),parser.OFPActionSetField(eth_dst=r6mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)

	    match = parser.OFPMatch(in_port=1,eth_type=0x0800,eth_src=gw2mac,ipv4_dst=r5ip)
            actions = [parser.OFPActionSetField(eth_src=gw2mac),parser.OFPActionSetField(eth_dst=r6mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)
############################################
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_dst="FF:FF:FF:FF:FF:FF",arp_tpa=gw2ip)
            self.add_flow(datapath,0,170,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=gw2ip,ipv4_dst=r3ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=gw2ip,arp_tpa=r3ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=gw2ip,ipv4_dst=r6ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=gw2ip,arp_tpa=r6ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r3ip,ipv4_dst=gw1ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r3ip,ipv4_dst=r1ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r3ip,ipv4_dst=r2ip)
            self.add_flow(datapath,0,165,match,[],0)

	if dp.id == 4:
            self.logger.info("MeshNode_4 is connected")
###Realy to Gateway1
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_dst=r4mac,arp_tpa=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r4mac),parser.OFPActionSetField(eth_dst=gw1mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)
###Relay to Raspi5
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_dst=r4mac,arp_tpa=r5ip)
            actions = [parser.OFPActionSetField(eth_src=r4mac),parser.OFPActionSetField(eth_dst=r5mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)
###Relay To Raspi6
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_dst=r4mac,arp_tpa=r6ip)
            actions = [parser.OFPActionSetField(eth_src=r4mac),parser.OFPActionSetField(eth_dst=r5mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)
##Relay To Gateway2
	    match = parser.OFPMatch(in_port=1,eth_type=0x0806,eth_dst=r4mac,arp_tpa=gw2ip)
            actions = [parser.OFPActionSetField(eth_src=r4mac),parser.OFPActionSetField(eth_dst=r5mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)
###Connect Raspi6
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_src=r4mac,arp_spa=r4ip,arp_tpa=r6ip)
            actions = [parser.OFPActionSetField(eth_src=r4mac),parser.OFPActionSetField(eth_dst=r5mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,eth_src=r4mac,ipv4_dst=r6ip)
            actions = [parser.OFPActionSetField(eth_src=r4mac),parser.OFPActionSetField(eth_dst=r5mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)
##Connect Gateway2
	    match = parser.OFPMatch(in_port=1,eth_type=0x0806,eth_src=r4mac,arp_spa=r4ip,arp_tpa=gw2ip)
            actions = [parser.OFPActionSetField(eth_src=r4mac),parser.OFPActionSetField(eth_dst=r5mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)

	    match = parser.OFPMatch(in_port=1,eth_type=0x0800,eth_src=r4mac,ipv4_src=r4ip,ipv4_dst=gw2ip)
            actions = [parser.OFPActionSetField(eth_src=r4mac),parser.OFPActionSetField(eth_dst=r5mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)


###To Prevent Duplicate Problem
	    match = parser.OFPMatch(in_port=1,eth_type=0x0806,eth_dst="FF:FF:FF:FF:FF:FF",arp_tpa=r4ip)
            self.add_flow(datapath,0,170,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r4ip,arp_tpa=gw1ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r4ip,ipv4_dst=gw1ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r4ip,arp_tpa=r5ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r4ip,ipv4_dst=r5ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r5ip,arp_tpa=gw2ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r5ip,arp_tpa=r6ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r5ip,ipv4_dst=gw2ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r5ip,ipv4_dst=r6ip)
            self.add_flow(datapath,0,165,match,[],0)



	if dp.id == 5:
            self.logger.info("MeshNode_5 is connected")

##Relay To Raspi 3
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_dst=r5mac,arp_tpa=r6ip)
            actions = [parser.OFPActionSetField(eth_src=r5mac),parser.OFPActionSetField(eth_dst=r6mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)
#######Relay To Raspi1
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_dst=r5mac,arp_tpa=r6ip)
            actions = [parser.OFPActionSetField(eth_src=r5mac),parser.OFPActionSetField(eth_dst=r6mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)
######Relay to Gateway 1
	    match = parser.OFPMatch(in_port=1,eth_type=0x0806,eth_dst=r5mac,arp_tpa=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r5mac),parser.OFPActionSetField(eth_dst=r4mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)
######Relay to Gateway 2
	    match = parser.OFPMatch(in_port=1,eth_type=0x0806,eth_dst=r5mac,arp_tpa=gw2ip)
            actions = [parser.OFPActionSetField(eth_src=r5mac),parser.OFPActionSetField(eth_dst=r6mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)

######Connect Gateway 1
	    match = parser.OFPMatch(in_port=1,eth_type=0x0806,eth_src=r5mac,arp_spa=r5ip,arp_tpa=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r5mac),parser.OFPActionSetField(eth_dst=r4mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)

	    match = parser.OFPMatch(in_port=1,eth_type=0x0800,eth_src=r5mac,ipv4_dst=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r5mac),parser.OFPActionSetField(eth_dst=r4mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)


#######Connect Gateway 2
	    match = parser.OFPMatch(in_port=1,eth_type=0x0800,eth_src=r5mac,ipv4_dst=gw2ip)
            actions = [parser.OFPActionSetField(eth_src=r5mac),parser.OFPActionSetField(eth_dst=r6mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)

	    match = parser.OFPMatch(in_port=1,eth_type=0x0806,eth_src=r5mac,arp_spa=r5ip,arp_tpa=gw2ip)
            actions = [parser.OFPActionSetField(eth_src=r5mac),parser.OFPActionSetField(eth_dst=r6mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)


####To Prevent Duplicate Problem
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_dst="FF:FF:FF:FF:FF:FF",arp_tpa=r5ip)
            self.add_flow(datapath,0,170,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r5ip,arp_tpa=r6ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r5ip,ipv4_dst=r6ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r5ip,arp_tpa=r4ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r5ip,ipv4_dst=r4ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r4ip,arp_tpa=gw1ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r6ip,arp_tpa=gw2ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r4ip,ipv4_dst=gw1ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r6ip,ipv4_dst=gw2ip)
            self.add_flow(datapath,0,165,match,[],0)


	if dp.id == 6:
            self.logger.info("MeshNode_6 is connected")
###Relay To Gateway2
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_dst=r6mac,arp_tpa=gw2ip)
            actions = [parser.OFPActionSetField(eth_src=r6mac),parser.OFPActionSetField(eth_dst=gw2mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)
###Relay To Gateway1
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_dst=r6mac,arp_tpa=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r6mac),parser.OFPActionSetField(eth_dst=r5mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)
###Relay To Raspi4
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_dst=r6mac,arp_tpa=r4ip)
            actions = [parser.OFPActionSetField(eth_src=r6mac),parser.OFPActionSetField(eth_dst=r5mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)
###Relay To Raspi5
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_dst=r6mac,arp_tpa=r5ip)
            actions = [parser.OFPActionSetField(eth_src=r6mac),parser.OFPActionSetField(eth_dst=r5mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,164,match,actions,0)
###Gateway1
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_src=r6mac,arp_spa=r6ip,arp_tpa=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r6mac),parser.OFPActionSetField(eth_dst=r5mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,eth_src=r6mac,ipv4_dst=gw1ip)
            actions = [parser.OFPActionSetField(eth_src=r6mac),parser.OFPActionSetField(eth_dst=r5mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,160,match,actions,0)
###Raspi4
	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,eth_src=r6mac,arp_spa=r6ip,arp_tpa=r4ip)
            actions = [parser.OFPActionSetField(eth_src=r6mac),parser.OFPActionSetField(eth_dst=r5mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,150,match,actions,0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,eth_src=r6mac,ipv4_dst=r4ip)
            actions = [parser.OFPActionSetField(eth_src=r6mac),parser.OFPActionSetField(eth_dst=r5mac),parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath,0,150,match,actions,0)
#########################

###To Prevent Duplicate
	    match = parser.OFPMatch(in_port=1,eth_type=0x0806,eth_dst="FF:FF:FF:FF:FF:FF",arp_tpa=r6ip)
            self.add_flow(datapath,0,170,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r6ip,ipv4_dst=gw2ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r6ip,arp_tpa=gw2ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r6ip,ipv4_dst=r5ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r6ip,arp_tpa=r5ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r5ip,arp_tpa=r4ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0806,arp_spa=r5ip,arp_tpa=r4ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r5ip,ipv4_dst=r4ip)
            self.add_flow(datapath,0,165,match,[],0)

	    match = parser.OFPMatch(in_port=1, eth_type=0x0800,ipv4_src=r5ip,ipv4_dst=gw1ip)
            self.add_flow(datapath,0,165,match,[],0)


    @set_ev_cls(ofp_event.EventOFPStateChange,[MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        current_time = time.asctime(time.localtime(time.time()))
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.logger.info("(Switch ID %s),IP address is connected %s in %s,1",datapath.id,datapath.address,current_time)
                self.datapaths[datapath.id] = datapath
                self.logger.info("Current Conneced Switches to RYU controller are %s",self.datapaths.keys())
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                self.logger.info("(Switch ID %s),IP address is leaved %s in %s,0", datapath.id, datapath.address,current_time)
                del self.datapaths[datapath.id]
                self.logger.info("Current Conneced Switches to RYU controller are %s", self.datapaths.keys())

#    def _monitor(self):
#        while True:
#            for datapath in self.datapaths.values():
#                self.initial()              
#                self.send_port_desc_stats_request(datapath)
#                current_dataplane = []
#            hub.sleep(5)

#    def send_port_stats_request(self, datapath):
#        self.logger.info('send stats request: %016x',datapath.id)
#        ofp = datapath.ofproto
#        ofp_parser = datapath.ofproto_parser
#        req = ofp_parser.OFPPortStatsRequest(datapath, 0, ofp.OFPP_ANY)
#        datapath.send_msg(req)

#    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
#    def port_stats_reply_handler(self, ev):
#        ports = []
#        for stat in ev.msg.body:
#            ports.append('port_no=%d'%stat.port_no)
#            self.logger.info('PortStats: %s', ports)

    def current_status(self):
        self.logger.info(current_dataplane)


    def initial(self):
        current_dataplane = []

    def send_port_desc_stats_request(self, datapath):
        ofp_parser = datapath.ofproto_parser
        req = ofp_parser.OFPPortDescStatsRequest(datapath, 0)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, MAIN_DISPATCHER)
    def port_desc_stats_reply_handler(self, ev):
        ports = []
        for p in ev.msg.body:
            ports.append(p.name)            
            if p.name in dataplane:
                self.logger.info(p.name)
                current_dataplane.append(p.name)
            if p.name in controlplane:
                self.logger.info(p.name)
#                current_dataplane.append(p.name)
#    print(current_dataplane)


#        current_dataplane.clear()         
#        if current_dataplane == dataplane:
#            self.logger.info["all data planes are working]




#            self.logger.info('OFPPortDescStatsReply received: %s', ports)
           


