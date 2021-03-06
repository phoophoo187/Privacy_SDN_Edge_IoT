#This rules are written by PPTLT@NECTEC for SDNIOTEDGE project 
#@edge4#
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


superedge_control_ip="10.0.0.8"
superedge_data_ip="10.0.0.8"

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



sleep 3
sudo ovs-vsctl --if-exist del-br br0
sudo ovs-vsctl --if-exist del-br br1

sudo ovs-vsctl add-br br0
sudo ovs-vsctl add-br br1

sudo ovs-vsctl set bridge br0 other-config:datapath-id=1000000000000001
sudo ovs-vsctl set bridge br1 other-config:datapath-id=1000000000000010

sudo ovs-vsctl set bridge br0 datapath_type=netdev
sudo ovs-vsctl set bridge br1 datapath_type=netdev

sudo ovs-vsctl add-port br0 $control_interface -- set Interface $control_interface ofport_request=1
sudo ovs-vsctl add-port br1 $data_interface -- set Interface $data_interface ofport_request=2


sudo ifconfig $control_interface 0
sudo ifconfig $data_interface 0
sudo ifconfig br0 $edge1_control_ip netmask 255.255.255.0 up
sudo ifconfig br1 $edge1_data_ip netmask 255.255.255.0 up
sudo iptables -A INPUT -i $control_interface -j DROP #Required to do only OpenVswitch in userspace mode
sudo iptables -A FORWARD -i $control_interface -j DROP #Required to do only OpenVswitch in userspace mode
sudo iptables -A INPUT -i $data_interface -j DROP #Required to do only OpenVswitch in userspace mode
sudo iptables -A FORWARD -i $data_interface -j DROP #Required to do only OpenVswitch in userspace mode

#Connect to RYU controller
sudo ovs-vsctl set-controller br0 tcp:$sdncloud_ip:6633
sudo ovs-vsctl set controller br0 connection-mode=out-of-band
sudo ovs-vsctl set-fail-mode br0 secure
sudo ovs-vsctl set bridge br0 stp_enable=true

sudo ovs-vsctl set-controller br1 tcp:$sdncloud_ip:6633
sudo ovs-vsctl set controller br1 connection-mode=out-of-band
sudo ovs-vsctl set-fail-mode br1 secure
sudo ovs-vsctl set bridge br1 stp_enable=true

#Receive the incoming control traffic to edge4 from edge1 and edge5 
sudo ovs-ofctl add-flow br0 arp,priority=100,in_port=1,dl_src=$edge1_control_mac,arp_tpa=$edge4_control_ip,actions=LOCAL
sudo ovs-ofctl add-flow br0 arp,priority=100,in_port=1,dl_src=$edge5_control_mac,arp_tpa=$edge4_control_ip,actions=LOCAL
sudo ovs-ofctl add-flow br0 ip,priority=100,in_port=1,dl_src=$edge1_control_mac,nw_dst=$edge4_control_ip,actions=LOCAL
sudo ovs-ofctl add-flow br0 ip,priority=100,in_port=1,dl_src=$edge5_control_mac,nw_dst=$edge4_control_ip,actions=LOCAL


#Receive the incoming data traffic to edge4 from edge4 and edge5
sudo ovs-ofctl add-flow br1 arp,priority=100,in_port=2,dl_src=$edge1_data_mac,arp_tpa=$edge4_data_ip,actions=LOCAL
sudo ovs-ofctl add-flow br1 arp,priority=100,in_port=2,dl_src=$edge5_data_mac,arp_tpa=$edge4_data_ip,actions=LOCAL
sudo ovs-ofctl add-flow br1 ip,priority=100,in_port=2,dl_src=$edge1_data_mac,nw_dst=$edge4_data_ip,actions=LOCAL
sudo ovs-ofctl add-flow br1 ip,priority=100,in_port=2,dl_src=$edge5_data_mac,nw_dst=$edge4_data_ip,actions=LOCAL


#send the control packet from edge4 to edge1 and edge5
sudo ovs-ofctl add-flow br0 arp,priority=100,in_port=LOCAL,arp_spa=$superedge_control_ip,actions="resubmit(,1)"
sudo ovs-ofctl add-flow br0 ip,priority=100,in_port=LOCAL,nw_dst=$edge1_control_ip,actions=output:1
sudo ovs-ofctl add-flow br0 ip,priority=100,in_port=LOCAL,nw_dst=$edge5_control_ip,actions=output:1


#send the data packet from edge4 to edge1 and edge5
sudo ovs-ofctl add-flow br1 arp,priority=100,in_port=LOCAL,arp_spa=$superedge_data_ip,actions="resubmit(,1)"
sudo ovs-ofctl add-flow br1 ip,priority=100,in_port=LOCAL,nw_dst=$edge1_data_ip,actions=output:2
sudo ovs-ofctl add-flow br1 ip,priority=100,in_port=LOCAL,nw_dst=$edge5_data_ip,actions=output:2




#Relay the incoming  control traffic for edge1 @edge4 

sudo ovs-ofctl add-flow br0 ip,priority=100,in_port=1,dl_src=$superedge_control_mac,nw_dst=$edge1_control_ip,actions="resubmit(,2)" #e1
sudo ovs-ofctl add-flow br0 ip,priority=100,in_port=1,dl_src=$edge1_control_mac,nw_dst=$superedge_control_ip,actions="resubmit(,4)" #e5

#Relay the incoming data traffic for edge1 @edge4 

sudo ovs-ofctl add-flow br1 ip,priority=100,in_port=2,dl_src=$superedge_data_mac,nw_dst=$edge1_data_ip,actions="resubmit(,2)" #e1
sudo ovs-ofctl add-flow br1 ip,priority=100,in_port=2,dl_src=$edge1_data_mac,nw_dst=$superedge_data_ip,actions="resubmit(,4)" #e5

#Relay the incoming  control traffic for edge2 @edge4 

sudo ovs-ofctl add-flow br0 ip,priority=100,in_port=1,dl_src=$superedge_control_mac,nw_dst=$edge2_control_ip,actions="resubmit(,4)" #e5
sudo ovs-ofctl add-flow br0 ip,priority=100,in_port=1,dl_src=$edge2_control_mac,nw_dst=$superedge_control_ip,actions="resubmit(,2)" #e1

#Relay the incoming data traffic for edge2 @edge4 

sudo ovs-ofctl add-flow br1 ip,priority=100,in_port=2,dl_src=$superedge_data_mac,nw_dst=$edge2_data_ip,actions="resubmit(,4)" #e5
sudo ovs-ofctl add-flow br1 ip,priority=100,in_port=2,dl_src=$edge2_data_mac,nw_dst=$superedge_data_ip,actions="resubmit(,2)" #e1

#Relay the incoming  control traffic for edge5 @edge4 

sudo ovs-ofctl add-flow br0 ip,priority=100,in_port=1,dl_src=$superedge_control_mac,nw_dst=$edge5_control_ip,actions="resubmit(,4)" #e5
sudo ovs-ofctl add-flow br0 ip,priority=100,in_port=1,dl_src=$edge5_control_mac,nw_dst=$superedge_control_ip,actions="resubmit(,2)" #e1

#Relay the incoming data traffic for edge5 @edge4 

sudo ovs-ofctl add-flow br1 ip,priority=100,in_port=2,dl_src=$superedge_data_mac,nw_dst=$edge5_data_ip,actions="resubmit(,4)" #e5
sudo ovs-ofctl add-flow br1 ip,priority=100,in_port=2,dl_src=$edge5_data_mac,nw_dst=$superedge_data_ip,actions="resubmit(,2)" #e1

#Relay the incoming  control traffic for edge6 @edge4 

sudo ovs-ofctl add-flow br0 ip,priority=100,in_port=1,dl_src=$superedge_control_mac,nw_dst=$edge6_control_ip,actions="resubmit(,4)" #e5
sudo ovs-ofctl add-flow br0 ip,priority=100,in_port=1,dl_src=$edge6_control_mac,nw_dst=$superedge_control_ip,actions="resubmit(,2)" #e1

#Relay the incoming data traffic for edge6 @edge4 

sudo ovs-ofctl add-flow br1 ip,priority=100,in_port=2,dl_src=$superedge_data_mac,nw_dst=$edge6_data_ip,actions="resubmit(,4)" #e5
sudo ovs-ofctl add-flow br1 ip,priority=100,in_port=2,dl_src=$edge6_data_mac,nw_dst=$superedge_data_ip,actions="resubmit(,2)" #e1





#Table 1 is to rewrite the destination MAC address into broadcast MAC address @ control plane
sudo ovs-ofctl add-flow br0 table=1,actions=mod_dl_dst:$broadcast,"resubmit(,5)"
#Table 1 is to rewrite the destination MAC address into broadcast MAC address @ data plane
sudo ovs-ofctl add-flow br1 table=1,actions=mod_dl_dst:$broadcast,"resubmit(,5)"

#Table 2 is to rewrite the destination MAC address into edge1 MAC address @ control plane
sudo ovs-ofctl add-flow br0 table=2,actions=mod_dl_dst:$edge1_control_mac,"load:0->OXM_OF_IN_PORT[],resubmit(,5)"
#Table 2 is to rewrite the destination MAC address into edge1 MAC address @ data plane
sudo ovs-ofctl add-flow br1 table=2,actions=mod_dl_dst:$edge1_data_mac,"load:0->OXM_OF_IN_PORT[],resubmit(,5)"


#Table 4 is to rewrite the destination MAC address into edge5 MAC address @ control plane
sudo ovs-ofctl add-flow br0 table=4,actions=mod_dl_dst:$edge5_control_mac,"load:0->OXM_OF_IN_PORT[],resubmit(,5)"
#Table 4 is to rewrite the destination MAC address into edge5 MAC address @ data plane
sudo ovs-ofctl add-flow br1 table=4,actions=mod_dl_dst:$edge5_data_mac,"load:0->OXM_OF_IN_PORT[],resubmit(,5)"

#Table 5 is to forward to wireless interface @ control plane
sudo ovs-ofctl add-flow br0 table=5,actions=output:1
#Table 5 is to forward to wireless interface @ data plane
sudo ovs-ofctl add-flow br1 table=5,actions=output:2

#To prevent the infinite loop @ control plane
sudo ovs-ofctl add-flow br0 priority=1,in_port=1,actions=drop
#To prevent the infinite loop @ data plane
sudo ovs-ofctl add-flow br1 priority=1,in_port=2,actions=drop


sudo route add -host $superedge_control_ip gw $edge2_control_ip
sudo route add -host $superedge_data_ip gw $edge2_data_ip
sudo sysctl -p
