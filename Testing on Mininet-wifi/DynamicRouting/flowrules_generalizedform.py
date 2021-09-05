def getMacFromName(edgeName):
    if edgeName == 'edge1':
        return 'e1mac'
    elif edgeName == 'edge2':
        return 'e2mac'
    elif edgeName == 'edge3':
        return 'e3mac'
    elif edgeName == 'edge4':
        return 'e4mac'
    elif edgeName == 'edge5':
        return 'e5mac'
    elif edgeName == 'edge6':
        return 'e6mac'
    elif edgeName == 'superedge':
        return 'superEdgeMac'

def getIPFromName(edgeName):
    if edgeName == 'edge1':
        return 'e1ip'
    elif edgeName == 'edge2':
        return 'e2ip'
    elif edgeName == 'edge3':
        return 'e3ip'
    elif edgeName == 'edge4':
        return 'e4ip'
    elif edgeName == 'edge5':
        return 'e5ip'
    elif edgeName == 'edge6':
        return 'e6ip'
    elif edgeName == 'superedge':
        return 'superEdgeip'

def get_datapath_id(edgeName):
    if edgeName == 'edge1': return 1
    elif edgeName == 'edge2': return 2
    elif edgeName == 'edge3': return 3
    elif edgeName == 'edge4': return 4
    elif edgeName == 'edge5': return 5
    elif edgeName == 'edge6': return 6
    elif edgeName == 'superedge': return 7
    
def write_dynamic_flowrules(datapath_id, optimal_path):
    #source
    source = optimal_path[0]
    dest = optimal_path[len(optimal_path)-1]
    
    source_ip = getIPFromName(source)
    source_mac = getMacFromName(source)
    
    dest_ip = getIPFromName(dest)
    dest_mac = getMacFromName(dest)
        
    if datapath_id == get_datapath_id(source):
        print('source')
        hop = optimal_path[1]
        hop_mac = getMacFromName(hop)
        print('match = parser.OFPMatch(in_port=1, eth_type=0x0806, eth_src=%s, arp_spa=%s, arp_tpa=%s)' %(source_mac, source_ip, dest_ip))        
        print('actions = [parser.OFPActionSetField(eth_src=%s), parser.OFPActionSetField(eth_dst=%s), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]' %(source_mac, hop_mac))        
        print('match = parser.OFPMatch(in_port=1, eth_type=0x0800, eth_src=%s, ipv4_dst=%s)' %(source_mac, dest_ip))        
        print('actions = [parser.OFPActionSetField(eth_src=%s), parser.OFPActionSetField(eth_dst=%s), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]' %(source_mac, hop_mac))         
        print('--------------------------------')

    relay_list = optimal_path[1:-1]    
    for i in range(len(relay_list)):        
        if datapath_id == get_datapath_id(relay_list[i]):
            relay_ip = getIPFromName(relay_list[i])
            relay_mac = getMacFromName(relay_list[i])
            hop = optimal_path[2 + i]
            hop_mac = getMacFromName(hop)
            print('relay at %s' % (relay_list[i]))
            print('forward')
            print('match = parser.OFPMatch(in_port=1, eth_type=0x0806, eth_dst=%s, arp_tpa=%s)' %(relay_mac, dest_ip))
            print('actions = [parser.OFPActionSetField(eth_src=%s), parser.OFPActionSetField(eth_dst=%s), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]' %(relay_mac, hop_mac))
            print('match = parser.OFPMatch(in_port=1, eth_type=0x0800, eth_dst=%s, ipv4_dst=%s)' %(relay_mac, dest_ip))
            print('actions = [parser.OFPActionSetField(eth_src=%s), parser.OFPActionSetField(eth_dst=%s), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]' %(relay_mac, hop_mac))
            print('--------------------------------')
            
            reverse_hop = optimal_path[i]
            reverse_hop_mac = getMacFromName(reverse_hop)            
            print('backward')
            print('match = parser.OFPMatch(in_port=1, eth_type=0x0806, eth_dst=%s, arp_tpa=%s)' %(relay_mac, source_ip))
            print('actions = [parser.OFPActionSetField(eth_src=%s), parser.OFPActionSetField(eth_dst=%s), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]' %(relay_mac, reverse_hop_mac))
            print('match = parser.OFPMatch(in_port=1, eth_type=0x0800, eth_dst=%s, ipv4_dst=%s)' %(relay_mac, source_ip))
            print('actions = [parser.OFPActionSetField(eth_src=%s), parser.OFPActionSetField(eth_dst=%s), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]' %(relay_mac, reverse_hop_mac))
            print('--------------------------------')
            print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
            
    if datapath_id == get_datapath_id(dest):
        print('dest')
        hop = optimal_path[len(optimal_path)-2]
        hop_mac = getMacFromName(hop)
        print('match = parser.OFPMatch(in_port=1, eth_type=0x0806, eth_src=%s, arp_tpa=%s)' %(dest_mac, source_ip))
        print('actions = [parser.OFPActionSetField(eth_src=%s), parser.OFPActionSetField(eth_dst=%s), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]' %(dest_mac, hop_mac))
        print('match = parser.OFPMatch(in_port=1, eth_type=0x0800, eth_src=%s, ipv4_dst=%s)' %(dest_mac, source_ip))
        print('actions = [parser.OFPActionSetField(eth_src=%s), parser.OFPActionSetField(eth_dst=%s), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]' %(dest_mac, hop_mac))

res_path = ['edge4', 'edge1', 'edge2', 'superedge']
#res_path = ['edge4', 'edge1', 'edge2','edge3', 'superedge']
#res_path = ['edge5', 'edge6', 'edge3','edgee2','edge1', 'superedge']
print(res_path)
write_dynamic_flowrules(1, res_path)
write_dynamic_flowrules(2, res_path)
write_dynamic_flowrules(3, res_path)
write_dynamic_flowrules(4, res_path)
write_dynamic_flowrules(5, res_path)
write_dynamic_flowrules(6, res_path)
write_dynamic_flowrules(7, res_path)