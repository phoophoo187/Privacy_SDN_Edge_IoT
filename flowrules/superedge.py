#This program is the static routing/rerouting program running at the northbound interface of Ryu controller for SDNIoTEdge project@NECTEC.
#written by PPTLT@NECTEC 
#program writing in progress !!!

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3, ofproto_v1_3_parser
from ryu.lib import hub
import time
from prettytable import PrettyTable

edge1_control_mac="98:48:27:e2:bf:04"
edge2_control_mac="98:48:27:e2:c1:00"
edge3_control_mac="98:48:27:e0:21:2a"
edge4_control_mac="98:48:27:e2:c2:f8"
edge5_control_mac="98:48:27:de:a8:99"
edge6_control_mac="98:48:27:e2:e8:c7"

edge1_data_mac="98:48:27:de:a2:ca"
edge2_data_mac="98:48:27:e0:1a:fe"
edge3_data_mac="98:48:27:de:8f:37"
edge4_data_mac="98:48:27:de:9e:2c"
edge5_data_mac="98:48:27:e0:22:92"
edge6_data_mac="98:48:27:e0:1d:f4"

superedge_control_mac="00:0f:00:14:91:d7"
superedge_data_mac="00:0f:00:10:10:23"


superedge_control_ip="10.0.0.10"
superedge_data_ip="192.168.2.10"

edge1_control_ip="10.0.0.1"
edge2_control_ip="10.0.0.2"
edge3_control_ip="10.0.0.3"
edge4_control_ip="10.0.0.4"
edge5_control_ip="10.0.0.5"
edge6_control_ip="10.0.0.6"
edge6_control_ip="10.0.0.6"

edge1_data_ip="192.168.2.1"
edge2_data_ip="192.168.2.2"
edge3_data_ip="192.168.2.3"
edge4_data_ip="192.168.2.4"
edge5_data_ip="192.168.2.5"
edge6_data_ip="192.168.2.6"

broadcast="ff:ff:ff:ff:ff:ff"

control_interface="wlan2"
data_interface="wlan1"

superedge_control_interface="wlx000f001491d7"
superedge_data_interface="wlx000f00101023"

#edge1_datapath_id_control=
#edge2_datapath_id_control=
#edge3_datapath_id_control=
#edge4_datapath_id_control=
#edge5_datapath_id_control=
#edge6_datapath_id_control=
#superedge_datapath_id_control=

#edge1_datapath_id_data=
#edge2_datapath_id_data=
#edge3_datapath_id_data=
#edge4_datapath_id_data=
#edge5_datapath_id_data=
#edge6_datapath_id_data=
#superedge_datapath_id_data=

def getDeviceName(datapath):
    if str(edge1_datapath_id_control) == datapath:
        return "edge1_control"
	elif str(edge1_datapath_id_data) == datapath:
        return "edge1_data"
    elif str(edge2_datapath_id_control) == datapath:
        return "edge2_control"
	elif str(edge2_datapath_id_data) == datapath:
        return "edge2_data"
    elif str(edge3_datapath_id_control) == datapath:
        return "edge3_control"
	elif str(edge3_datapath_id_data) == datapath:
        return "edge3_data"
    elif str(edge4_datapath_id_control) == datapath:
        return "edge4_control"
	elif str(edge4_datapath_id_data) == datapath:
        return "edge4_data"
    elif str(edge5_datapath_id_control) == datapath:
        return "edge5_control"
	elif str(edge5_datapath_id_data) == datapath:
        return "edge5_data"
    elif str(edge6_datapath_id_control) == datapath:
        return "edge6_control"
	elif str(edge6_datapath_id_data) == datapath:
        return "edge6_data"
    elif str(superedge_datapath_id_control) == datapath:
        return "superedge_control"
	elif str(superedge_datapath_id_data) == datapath:
        return "superedge_data"
    else:
        return "no device"

def getDeviceArr(arr):
    list = []
    for x in arr:
        list.append(getDeviceName(str(x)))
    return list

class link_failure (app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self,*args,**kwargs):
        super(link_failure,self).__init__(*args,**kwargs)
        self.switch_table = {}
        self.datapaths = {}        
     
        self.flow_stats = {}
        self.flow_stats_prev = {}
        
        self.monitor_thread = hub.spawn(self._monitor)
        self.link_down = []
        
    def _monitor(self):        
        while True:                                        
            for datapath in self.datapaths.values():
                self.send_flow_stats_request(datapath)    
            hub.sleep(18)
            self.print_monitor_status()
            self.link_down = []
            self.check_all_links()
            for datapath in self.datapaths.values():
                self.send_get_config_request(datapath)
            
    def print_monitor_status(self):
        if len(self.flow_stats) == 0:
            print('{:*^120}'.format(' Currently no flow stats data '))
        else:
            print('{:-^120}'.format(' Flow statistics reply '))
            flow_stats_table = PrettyTable(['name', 'dur_sec', 'dur_nsec', 'packet_cnt', 'byte_cnt', 'priority', 'idle', 'hard', 'flag', 'match', 'instructions'])
            for deviceName in self.flow_stats:
                for item in self.flow_stats[deviceName]:
                    flow_stats_table.add_row([deviceName, item.duration_sec, item.duration_nsec, item.packet_count, item.byte_count, item.priority, item.idle_timeout, item.hard_timeout, item.flags, item.match, item.instructions])
            print(flow_stats_table)

   
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

#Define the function to detect when wireless nodes connect to RYU controller or leave from RYU controller
    @set_ev_cls(ofp_event.EventOFPStateChange,[MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        current_time = time.asctime(time.localtime(time.time()))
        datapath = ev.datapath
        deviceName = getDeviceName(str(datapath.id))        
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.logger.info("%s IP address is connected %s in %s,1",deviceName,datapath.address,current_time)
                self.datapaths[datapath.id] = datapath                
                l = getDeviceArr(self.datapaths.keys())
                self.logger.info("Current Conneced edges to RYU controller are %s",l)
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                self.logger.info("%s IP address is leaved %s in %s,0", deviceName, datapath.address,current_time)
                del self.datapaths[datapath.id]
                l = getDeviceArr(self.datapaths.keys())
                self.logger.info("Current Conneced edges to RYU controller are %s", l)



    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        dp = ev.msg.datapath
        datapath = ev.msg.datapath
        deviceName = getDeviceName(str(datapath.id))
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        self.logger.info("%s (IP address %s) is connected,1",deviceName,dp.address)


    def send_port_desc_stats_request(self, datapath,port_num):
        ofp_parser = datapath.ofproto_parser
        req = ofp_parser.OFPPortDescStatsRequest(datapath,port_num)
        datapath.send_msg(req)
        
    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, MAIN_DISPATCHER)
    def port_desc_stats_reply_handler(self, ev):
        deviceName = getDeviceName(str(ev.msg.datapath.id))
        for p in ev.msg.body:
            self.port_desc_stats[deviceName] = p

    def send_port_stats_request(self, datapath, port_num):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        deviceName = getDeviceName(str(datapath.id))
        req = ofp_parser.OFPPortStatsRequest(datapath,port_num)
        return datapath.send_msg(req)


    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def port_stats_reply_handler(self, ev):
        deviceName = getDeviceName(str(ev.msg.datapath.id))
        for stat in ev.msg.body:
            self.port_stats[deviceName] = stat
        
    def send_flow_stats_request(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        cookie = cookie_mask = 0
        match = ofp_parser.OFPMatch(in_port=1)
        req = ofp_parser.OFPFlowStatsRequest(datapath, 0,
                                             ofp.OFPTT_ALL,
                                             ofp.OFPP_ANY, ofp.OFPG_ANY,
                                             cookie, cookie_mask,
                                             match)
        datapath.send_msg(req)
        
    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def flow_stats_reply_handler(self, ev):
        deviceName = getDeviceName(str(ev.msg.datapath.id))
        if deviceName in self.flow_stats:
            self.flow_stats_prev[deviceName] = self.flow_stats[deviceName]
        self.flow_stats[deviceName] = ev.msg.body
		
    def check_all_links(self):
        if len(self.flow_stats_prev) == 0 or len(self.flow_stats) == 0:
            self.logger.info('Currently no data')
        else:
            #check edge1 to superedge
            self.check_link('superedge_control', edge1_control_mac, superedge_control_ip, 'control:edge1->superedge')
			self.check_link('superedge_data', edge1_data_mac, superedge_data_ip, 'data:edge1->superedge')			
            #check edge2 to superedge
            self.check_link('superedge_control', edge2_control_mac, superedge_control_ip, 'control:edge2->superedge')
			self.check_link('superedge_data', edge2_data_mac, superedge_data_ip, 'data:edge2->superedge')
            #check edge3 to superedge
            self.check_link('superedge_control', edge3_control_mac, superedge_control_ip, 'control:edge3->superedge')
			self.check_link('superedge_data', edge3_data_mac, superedge_data_ip, 'data:edge3->superedge')
            #check edge1 to edge2
            self.check_link('edge1_control', edge1_control_mac, edge2_control_ip, 'control:edge1->edge2')
			self.check_link('edge1_data', edge1_data_mac, edge2_data_ip, 'data:edge1->edge2')
            #check edge2 to edge3
            self.check_link('edge2_control', edge2_control_mac, edge3_control_ip, 'control:edge2->edge3')
			self.check_link('edge2_data', edge2_data_mac, edge3_data_ip, 'data:edge2->edge3')
            #check edge4 to edge1
            self.check_link('edge1_control', edge4_control_mac, edge1_control_ip, 'control:edge4->edge1')
			self.check_link('edge1_data', edge4_data_mac, edge1_data_ip, 'data:edge4->edge1')
            #check edge4 to edge5
            self.check_link('edge5_control', edge4_control_mac, edge5_control_ip, 'control:edge4->edge5')
			self.check_link('edge5_data', edge4_data_mac, edge5_data_ip, 'data:edge4->edge5')
            #check edge5 to edge2
            self.check_link('edge2_control', edge5_control_mac, edge2_control_ip, 'control:edge5->edge2')
			self.check_link('edge2_data', edge5_data_mac, edge2_data_ip, 'data:edge5->edge2')
            #check edge5 to edge6
            self.check_link('edge6_control', edge5_control_mac, edge6_control_ip, 'control:edge5->edge6')
			self.check_link('edge6_data', edge5_data_mac, edge6_data_ip, 'data:edge5->edge6')
            #check edge6 to edge3
            self.check_link('edge3_control', edge6_control_mac, edge3_control_ip, 'control:edge6->edge3')
			self.check_link('edge3_data', edge6_data_mac, edge3_data_ip, 'data:edge6->edge3')

    def is_size_diff(self, curr, prev):
        if curr.packet_count == prev.packet_count:
            if curr.byte_count == prev.byte_count:
                return False
            return True
        return True

    def check_link(self, deviceName, from_mac, to_ip, linkName):        
        index = [i for i,_ in enumerate(self.flow_stats[deviceName]) if ('eth_src' in _.match) and (_.match['eth_src'] == from_mac) and ('arp_tpa' in _.match) and (_.match['arp_tpa'] == to_ip)]
        prev_index = [i for i,_ in enumerate(self.flow_stats_prev[deviceName]) if ('eth_src' in _.match) and (_.match['eth_src'] == from_mac) and ('arp_tpa' in _.match) and (_.match['arp_tpa'] == to_ip)]
        if (len(index) == 0) or (len(prev_index) == 0):
            self.loggger.info(' link not found ' + linkName + ' ')
            self.link_down.append(linkName)
        else:
            cur = self.flow_stats[deviceName][index[0]]
            prev = self.flow_stats_prev[deviceName][prev_index[0]]
            if self.is_size_diff(cur, prev) == False:                
                self.logger.info(' link blocked ' + linkName + ' dur: ' + str(cur.duration_sec) + "," + str(prev.duration_sec) +' p cnt: ' + str(cur.packet_count) + "," + str(prev.packet_count) + ' b cnt: ' + str(cur.byte_count) + "," + str(prev.byte_count))
                self.link_down.append(linkName)
            else:
                self.logger.info(' link ok ' + linkName + ' ')


    def send_get_config_request(self, datapath):
        ofp_parser = datapath.ofproto_parser
        req = ofp_parser.OFPGetConfigRequest(datapath)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPGetConfigReply, MAIN_DISPATCHER)
    def get_config_reply_handler(self,ev):
        current_time = time.asctime(time.localtime(time.time()))
        datapath = ev.msg.datapath
        parser = datapath.ofproto_parser
        self.logger.info('IP address %s sends OFPConfigReply message in %s', datapath.address, current_time)
        if 'control:edge1->superedge' in self.link_down:
            self.logger.info("When the control link between edge1 and superedge is down..........")
            if 'control:edge1->edge2' not in self.link_down and 'control:edge2->superedge' not in self.link_down:
                self.logger.info("Redirect with control:edge1->edge2->superedge")				
            elif 'control:edge1->edge4' not in self.link_down and 'control:edge4->edge5' not in self.link_down and 'control:edge5->edge2' not in self.link_down and 'control:edge2->superedge' not in self.link_down:
                self.logger.info("Redirect with control:edge1->edge4->edge5->edge2->superedge")	
            else:
                self.logger.info("All alternative control between edge 1 and superedge are down")
        if 'control:edge2->superedge' in self.link_down:
            self.logger.info("When the control link between edge2 and superedge is down..........")
            if 'control:edge2->edge1' not in self.link_down and 'control:edge1->superedge' not in self.link_down:
                self.logger.info("Redirect with control:edge2->edge1->superedge")
            elif 'control:edge2->edge3' not in self.link_down and 'control:edge3->superedge' not in self.link_down:
                self.logger.info("Redirect with control:edge2->edge3->superedge")
            elif 'control:edge2->edge5' not in self.link_down and 'control:edge5->edge4' not in self.link_down and 'control:edge4->edge1' not in self.link_down and 'control:edge1->superedge' not in self.link_down:
                self.logger.info("Redirect with control:edge2->edge5->edge4->edge1->superedge")
            elif 'control:edge2->edge5' not in self.link_down and 'control:edge5->edge6' not in self.link_down and 'control:edge6->edge3' not in self.link_down and 'control:edge3->superedge' not in self.link_down:
                self.logger.info("Redirect with control:edge2->edge5->edge6->edge3->superedge")            
            else:
                self.logger.info("All alternative control between edge 2 and superedge are down")
        if 'control:edge3->superedge' in self.link_down:
            self.logger.info("When the control link between edge3 and superedge is down..........")
            if 'control:edge3->edge2' not in self.link_down and 'control:edge2->superedge' not in self.link_down:
                self.logger.info("Redirect with control:edge3->edge2->superedge")
            elif 'control:edge3->edge2' not in self.link_down and 'control:edge2->edge1' not in self.link_down and 'control:edge1->superedge' not in self.link_down:
                self.logger.info("Redirect with control:edge3->edge2->edge1->superedge")
            elif 'control:edge3->edge6' not in self.link_down and 'control:edge6->edge5' not in self.link_down and 'control:edge5->edge2' not in self.link_down and 'control:edge2->superedge' not in self.link_down:
                self.logger.info("Redirect with control:edge3->edge6->edge5->edge2->superedge")
            else:
                self.logger.info("All alternative control routes between edge 3 and superedge are down")
        if 'control:edge4->edge1' in self.link_down and 'control:edge1->superedge' in self.link_down:
            self.logger.info("When the control links between edge4->edge1->superedge down..........")
            if 'control:edge4->edge1' not in self.link_down and 'control:edge1->edge2' not in self.link_down and 'control:edge2->superedge':
                self.logger.info("Redirect with control:edge4->edge1->edge2->superedge")
            elif 'control:edge4->edge5' not in self.link_down and 'control:edge5->edge2' not in self.link_down and 'control:edge2->superedge' not in self.link_down:
                self.logger.info("Redirect with control:edge4->edge5->edge2->superedge")
            elif 'control:edge4->edge5' not in self.link_down and 'control:edge5->edge6' not in self.link_down and 'control:edge6->edge3' not in self.link_down and 'control:edge3->superedge' not in self.link_down:
                self.logger.info("Redirect with control:edge4->edge5->edge6->edge3->superedge")
            else:
                self.logger.info("All alternative control routes between edge 4 and superedge are down")
        if 'control:edge5->edge2' in self.link_down and 'control:edge2->superedge' in self.link_down:
            self.logger.info("When the control links between edge5->edge2->superedge down..........")
            if 'control:edge5->edge2' not in self.link_down and 'control:edge2->edge1' not in self.link_down and 'control:edge1->superedge':
                self.logger.info("Redirect with control:edge5->edge2->edge1->superedge")
            elif 'control:edge5->edge2' not in self.link_down and 'control:edge2->edge3' not in self.link_down and 'control:edge3->superedge' not in self.link_down:
                self.logger.info("Redirect with control:edge5->edge2->edge3->superedge")
            elif 'control:edge5->edge4' not in self.link_down and 'control:edge4->edge1' not in self.link_down and 'control:edge1->superedge' not in self.link_down:
                self.logger.info("Redirect with control:edge5->edge4->edge1->superedge")
            elif 'control:edge5->edge6' not in self.link_down and 'control:edge6->edge3' not in self.link_down and 'control:edge3->superedge' not in self.link_down:
                self.logger.info("Redirect with control:edge5->edge6->edge3->superedge")
            else:
                self.logger.info("All alternative control routes between edge 5 and superedge are down")
        if 'control:edge6->edge3' in self.link_down and 'control:edge3->superedge' in self.link_down:
            self.logger.info("When the control links between edge6->edge3->superedge down..........")
            if 'control:edge6->edge3' not in self.link_down and 'control:edge3->edge2' not in self.link_down and 'control:edge2->superedge':
                self.logger.info("Redirect with control:edge6->edge3->edge2->superedge")
            elif 'control:edge6->edge5' not in self.link_down and 'control:edge5->edge2' not in self.link_down and 'control:edge2->superedge' not in self.link_down:
                self.logger.info("Redirect with control:edge6->edge5->edge2->superedge")
            elif 'control:edge6->edge5' not in self.link_down and 'control:edge5->edge4' not in self.link_down and 'control:edge4->edge1' not in self.link_down and 'control:edge1->superedge' not in self.link_down:
                self.logger.info("Redirect with control:edge6->edge5->edge4->edge1->superedge")
            else:
                self.logger.info("All alternative control routes between edge 6 and superedge are down")
				
				
		
		
		if 'data:edge1->superedge' in self.link_down:
            self.logger.info("When the data link between edge1 and superedge is down..........")
            if 'data:edge1->edge2' not in self.link_down and 'data:edge2->superedge' not in self.link_down:
                self.logger.info("Redirect with data:edge1->edge2->superedge")				
            elif 'data:edge1->edge4' not in self.link_down and 'data:edge4->edge5' not in self.link_down and 'data:edge5->edge2' not in self.link_down and 'data:edge2->superedge' not in self.link_down:
                self.logger.info("Redirect with data:edge1->edge4->edge5->edge2->superedge")	
            else:
                self.logger.info("All alternative data between edge 1 and superedge are down")
        if 'data:edge2->superedge' in self.link_down:
            self.logger.info("When the data link between edge2 and superedge is down..........")
            if 'data:edge2->edge1' not in self.link_down and 'data:edge1->superedge' not in self.link_down:
                self.logger.info("Redirect with data:edge2->edge1->superedge")
            elif 'data:edge2->edge3' not in self.link_down and 'data:edge3->superedge' not in self.link_down:
                self.logger.info("Redirect with data:edge2->edge3->superedge")
            elif 'data:edge2->edge5' not in self.link_down and 'data:edge5->edge4' not in self.link_down and 'data:edge4->edge1' not in self.link_down and 'data:edge1->superedge' not in self.link_down:
                self.logger.info("Redirect with data:edge2->edge5->edge4->edge1->superedge")
            elif 'data:edge2->edge5' not in self.link_down and 'data:edge5->edge6' not in self.link_down and 'data:edge6->edge3' not in self.link_down and 'data:edge3->superedge' not in self.link_down:
                self.logger.info("Redirect with data:edge2->edge5->edge6->edge3->superedge")            
            else:
                self.logger.info("All alternative data between edge 2 and superedge are down")
        if 'data:edge3->superedge' in self.link_down:
            self.logger.info("When the data link between edge3 and superedge is down..........")
            if 'data:edge3->edge2' not in self.link_down and 'data:edge2->superedge' not in self.link_down:
                self.logger.info("Redirect with data:edge3->edge2->superedge")
            elif 'data:edge3->edge2' not in self.link_down and 'data:edge2->edge1' not in self.link_down and 'data:edge1->superedge' not in self.link_down:
                self.logger.info("Redirect with data:edge3->edge2->edge1->superedge")
            elif 'data:edge3->edge6' not in self.link_down and 'data:edge6->edge5' not in self.link_down and 'data:edge5->edge2' not in self.link_down and 'data:edge2->superedge' not in self.link_down:
                self.logger.info("Redirect with data:edge3->edge6->edge5->edge2->superedge")
            else:
                self.logger.info("All alternative data routes between edge 3 and superedge are down")
        if 'data:edge4->edge1' in self.link_down and 'data:edge1->superedge' in self.link_down:
            self.logger.info("When the data links between edge4->edge1->superedge down..........")
            if 'data:edge4->edge1' not in self.link_down and 'data:edge1->edge2' not in self.link_down and 'data:edge2->superedge':
                self.logger.info("Redirect with data:edge4->edge1->edge2->superedge")
            elif 'data:edge4->edge5' not in self.link_down and 'data:edge5->edge2' not in self.link_down and 'data:edge2->superedge' not in self.link_down:
                self.logger.info("Redirect with data:edge4->edge5->edge2->superedge")
            elif 'data:edge4->edge5' not in self.link_down and 'data:edge5->edge6' not in self.link_down and 'data:edge6->edge3' not in self.link_down and 'data:edge3->superedge' not in self.link_down:
                self.logger.info("Redirect with data:edge4->edge5->edge6->edge3->superedge")
            else:
                self.logger.info("All alternative data routes between edge 4 and superedge are down")
        if 'data:edge5->edge2' in self.link_down and 'data:edge2->superedge' in self.link_down:
            self.logger.info("When the data links between edge5->edge2->superedge down..........")
            if 'data:edge5->edge2' not in self.link_down and 'data:edge2->edge1' not in self.link_down and 'data:edge1->superedge':
                self.logger.info("Redirect with data:edge5->edge2->edge1->superedge")
            elif 'data:edge5->edge2' not in self.link_down and 'data:edge2->edge3' not in self.link_down and 'data:edge3->superedge' not in self.link_down:
                self.logger.info("Redirect with data:edge5->edge2->edge3->superedge")
            elif 'data:edge5->edge4' not in self.link_down and 'data:edge4->edge1' not in self.link_down and 'data:edge1->superedge' not in self.link_down:
                self.logger.info("Redirect with data:edge5->edge4->edge1->superedge")
            elif 'data:edge5->edge6' not in self.link_down and 'data:edge6->edge3' not in self.link_down and 'data:edge3->superedge' not in self.link_down:
                self.logger.info("Redirect with data:edge5->edge6->edge3->superedge")
            else:
                self.logger.info("All alternative data routes between edge 5 and superedge are down")
        if 'data:edge6->edge3' in self.link_down and 'data:edge3->superedge' in self.link_down:
            self.logger.info("When the data links between edge6->edge3->superedge down..........")
            if 'data:edge6->edge3' not in self.link_down and 'data:edge3->edge2' not in self.link_down and 'data:edge2->superedge':
                self.logger.info("Redirect with data:edge6->edge3->edge2->superedge")
            elif 'data:edge6->edge5' not in self.link_down and 'data:edge5->edge2' not in self.link_down and 'data:edge2->superedge' not in self.link_down:
                self.logger.info("Redirect with data:edge6->edge5->edge2->superedge")
            elif 'data:edge6->edge5' not in self.link_down and 'data:edge5->edge4' not in self.link_down and 'data:edge4->edge1' not in self.link_down and 'data:edge1->superedge' not in self.link_down:
                self.logger.info("Redirect with data:edge6->edge5->edge4->edge1->superedge")
            else:
                self.logger.info("All alternative data routes between edge 6 and superedge are down")