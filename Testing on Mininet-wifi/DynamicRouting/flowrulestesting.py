### edge1 to superedge via e1 e2 e3 and superedge @e1
### e1->e2 -> e3-> superedge 

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_src=e1mac, arp_spa=e1ip, arp_tpa=superEdgeip)
            actions = [parser.OFPActionSetField(eth_src=e1mac), parser.OFPActionSetField(
                eth_dst=e2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 180, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=e1mac, ipv4_dst=superEdgeip)
            actions = [parser.OFPActionSetField(eth_src=e1mac), parser.OFPActionSetField(
                eth_dst=e2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 180, match, actions, 0)


### edge1 to superedge via e1 e2 e3 and superedge @e2 #relay to superedge

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e2mac, arp_tpa=superEdgeip)
            actions = [parser.OFPActionSetField(eth_src=e2mac), parser.OFPActionSetField(
                eth_dst=e3mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 180, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=e2mac, ipv4_dst=superedgeip)
            actions = [parser.OFPActionSetField(eth_src=e2mac), parser.OFPActionSetField(
                eth_dst=e3mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 180, match, actions, 0)

### edge1 to superedge via e1 e2 e3 and superedge @e2 #relay to e1

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e2mac, arp_tpa=e1ip)
            actions = [parser.OFPActionSetField(eth_src=e2mac), parser.OFPActionSetField(
                eth_dst=e1mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 180, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=e2mac, ipv4_dst=e1ip)
            actions = [parser.OFPActionSetField(eth_src=e2mac), parser.OFPActionSetField(
                eth_dst=e1mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 180, match, actions, 0)




# edge1 to superedge via e1 e2 e3 and superedge @e3 relay to e1
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e3mac, arp_tpa=superEdgeip)
            actions = [parser.OFPActionSetField(eth_src=e3mac), parser.OFPActionSetField(
                eth_dst=superEdgemac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 180, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=e3mac, ipv4_dst=superEdgeip)
            actions = [parser.OFPActionSetField(eth_src=e3mac), parser.OFPActionSetField(
                eth_dst=superEdgemac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 180, match, actions, 0)


# edge1 to superedge via e1 e2 e3 and superedge @e3 # relay to e1
            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_dst=e3mac, arp_tpa=e1ip)
            actions = [parser.OFPActionSetField(eth_src=e3mac), parser.OFPActionSetField(
                eth_dst=e2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 180, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=e3mac, ipv4_dst=e1ip)
            actions = [parser.OFPActionSetField(eth_src=e3mac), parser.OFPActionSetField(
                eth_dst=e2mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 180, match, actions, 0)


# edge1 to superedge via e1 e2 e3 and superedge @superedge

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0806, eth_src=superEdgeMac, arp_tpa=e1ip)
            actions = [parser.OFPActionSetField(eth_src=superEdgeMac), parser.OFPActionSetField(
                eth_dst=e3mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 180, match, actions, 0)

            match = parser.OFPMatch(
                in_port=1, eth_type=0x0800, eth_src=superEdgeMac, ipv4_dst=e1ip)
            actions = [parser.OFPActionSetField(eth_src=superEdgeMac), parser.OFPActionSetField(
                eth_dst=e3mac), parser.OFPActionOutput(datapath.ofproto.OFPP_IN_PORT)]
            self.add_flow(datapath, 0, 180, match, actions, 0)






