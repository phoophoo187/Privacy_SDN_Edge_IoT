#This rules are written by PPTLT@NECTEC for SDNIOTEDGE project 
#@edge3#
edge1_control_mac="98:48:27:e1:32:ad"
edge2_control_mac="98:48:27:e2:c6:5b"
edge3_control_mac="98:48:27:e0:21:2a"
edge4_control_mac="98:48:27:e2:c2:0f"
edge5_control_mac="98:48:27:de:a8:99"
edge6_control_mac="98:48:27:e2:e8:c7"

edge1_data_mac="98:48:27:e2:bf:82"
edge2_data_mac="98:48:27:e2:e7:dc"
edge3_data_mac="98:48:27:de:8f:37"
edge4_data_mac="98:48:27:e1:39:b9"
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



sleep 3
sudo ovs-vsctl --if-exist del-br br0
sudo ovs-vsctl --if-exist del-br br1

sudo ovs-vsctl add-br br0
sudo ovs-vsctl add-br br1

sudo ovs-vsctl set bridge br0 other-config:datapath-id=1000000000000003
sudo ovs-vsctl set bridge br1 other-config:datapath-id=1000000000000030

sudo ovs-vsctl set bridge br0 datapath_type=netdev
sudo ovs-vsctl set bridge br1 datapath_type=netdev

sudo ovs-vsctl add-port br0 $control_interface -- set Interface $control_interface ofport_request=1
sudo ovs-vsctl add-port br1 $data_interface -- set Interface $data_interface ofport_request=2


sudo ifconfig $control_interface 0
sudo ifconfig $data_interface 0
sudo ifconfig br0 $edge3_control_ip netmask 255.255.255.0 up
sudo ifconfig br1 $edge3_data_ip netmask 255.255.255.0 up
sudo iptables -A INPUT -i $control_interface -j DROP #Required to do only OpenVswitch in userspace mode
sudo iptables -A FORWARD -i $control_interface -j DROP #Required to do only OpenVswitch in userspace mode
sudo iptables -A INPUT -i $data_interface -j DROP #Required to do only OpenVswitch in userspace mode
sudo iptables -A FORWARD -i $data_interface -j DROP #Required to do only OpenVswitch in userspace mode

#Connect to RYU controller
sudo ovs-vsctl set-controller br0 tcp:$superedge_control_ip:6633
sudo ovs-vsctl set controller br0 connection-mode=out-of-band
sudo ovs-vsctl set-fail-mode br0 secure
sudo ovs-vsctl set bridge br0 stp_enable=true

sudo ovs-vsctl set-controller br1 tcp:$superedge_control_ip:6633
sudo ovs-vsctl set controller br1 connection-mode=out-of-band
sudo ovs-vsctl set-fail-mode br1 secure
sudo ovs-vsctl set bridge br1 stp_enable=true

#Receive the incoming control traffic to edge3 from edge6 and superedge


sudo ovs-ofctl add-flow br0 arp,priority=100,in_port=1,dl_src=$edge6_control_mac,arp_tpa=$edge3_control_ip,actions=LOCAL
sudo ovs-ofctl add-flow br0 arp,priority=100,in_port=1,dl_src=$superedge_control_mac,arp_tpa=$edge3_control_ip,actions=LOCAL
sudo ovs-ofctl add-flow br0 ip,priority=100,in_port=1,dl_src=$edge6_control_mac,nw_dst=$edge3_control_ip,actions=LOCAL
sudo ovs-ofctl add-flow br0 ip,priority=100,in_port=1,dl_src=$superedge_control_mac,nw_dst=$edge3_control_ip,actions=LOCAL

#Receive the incoming data traffic to edge3 from edge6 and superedge

sudo ovs-ofctl add-flow br1 arp,priority=100,in_port=2,dl_src=$edge6_data_mac,arp_tpa=$edge3_data_ip,actions=LOCAL
sudo ovs-ofctl add-flow br1 arp,priority=100,in_port=2,dl_src=$superedge_data_mac,arp_tpa=$edge3_data_ip,actions=LOCAL
sudo ovs-ofctl add-flow br1 ip,priority=100,in_port=2,dl_src=$edge6_data_mac,nw_dst=$edge3_data_ip,actions=LOCAL
sudo ovs-ofctl add-flow br1 ip,priority=100,in_port=2,dl_src=$superedge_data_mac,nw_dst=$edge3_data_ip,actions=LOCAL


#send the data packet from edge3 to edge6 and superedge

sudo ovs-ofctl add-flow br1 arp,priority=100,in_port=LOCAL,arp_tpa=$superedge_data_ip,actions=output:2
sudo ovs-ofctl add-flow br1 ip,priority=100,in_port=LOCAL,nw_dst=$superedge_data_ip,actions=output:2
sudo ovs-ofctl add-flow br1 arp,priority=100,in_port=LOCAL,arp_tpa=$edge6_data_ip,actions=output:2
sudo ovs-ofctl add-flow br1 ip,priority=100,in_port=LOCAL,nw_dst=$edge6_data_ip,actions=output:2

#send the control packet from edge3 to edge6 and superedge

sudo ovs-ofctl add-flow br0 arp,priority=100,in_port=LOCAL,arp_tpa=$superedge_control_ip,actions=output:1
sudo ovs-ofctl add-flow br0 ip,priority=100,in_port=LOCAL,nw_dst=$superedge_control_ip,actions=output:1
sudo ovs-ofctl add-flow br0 arp,priority=100,in_port=LOCAL,arp_tpa=$edge6_control_ip,actions=output:1
sudo ovs-ofctl add-flow br0 ip,priority=100,in_port=LOCAL,nw_dst=$edge6_control_ip,actions=output:1


#Relay the control and data traffic for edge6 @edge3

sudo ovs-ofctl add-flow br1 arp,priority=100,in_port=2,arp_sha=$superedge_data_mac,arp_tpa=$edge6_data_ip,actions="resubmit(,3)" #e6
sudo ovs-ofctl add-flow br1 arp,priority=100,in_port=2,arp_sha=$edge6_data_mac,arp_tpa=$superedge_data_ip,actions="resubmit(,4)" #se

sudo ovs-ofctl add-flow br0 arp,priority=100,in_port=1,arp_sha=$superedge_control_mac,arp_tpa=$edge6_control_ip,actions="resubmit(,3)" #e6
sudo ovs-ofctl add-flow br0 arp,priority=100,in_port=1,arp_sha=$edge6_control_mac,arp_tpa=$superedge_control_ip,actions="resubmit(,4)" #se

sudo ovs-ofctl add-flow br0 ip,priority=100,in_port=1,dl_src=$superedge_control_mac,nw_dst=$edge6_control_ip,actions="resubmit(,3)" #e6
sudo ovs-ofctl add-flow br0 ip,priority=100,in_port=1,dl_src=$edge6_control_mac,nw_dst=$superedge_control_ip,actions="resubmit(,4)" #se

sudo ovs-ofctl add-flow br1 ip,priority=100,in_port=2,dl_src=$superedge_data_mac,nw_dst=$edge6_data_ip,actions="resubmit(,3)" #e6
sudo ovs-ofctl add-flow br1 ip,priority=100,in_port=2,dl_src=$edge6_data_mac,nw_dst=$superedge_data_ip,actions="resubmit(,4)" #se


#Table 3 is to rewrite the destination MAC address into edge6 MAC address @ control plane
sudo ovs-ofctl add-flow br0 table=3,actions=mod_dl_dst:$edge6_control_mac,"load:0->OXM_OF_IN_PORT[],resubmit(,5)"
#Table 3 is to rewrite the destination MAC address into edge6 MAC address @ data plane
sudo ovs-ofctl add-flow br1 table=3,actions=mod_dl_dst:$edge6_data_mac,"load:0->OXM_OF_IN_PORT[],resubmit(,5)"

#Table 4 is to rewrite the destination MAC address into superedge MAC address @ control plane
sudo ovs-ofctl add-flow br0 table=4,actions=mod_dl_dst:$superedge_control_mac,"load:0->OXM_OF_IN_PORT[],resubmit(,5)"
#Table 4 is to rewrite the destination MAC address into superedge MAC address @ data plane
sudo ovs-ofctl add-flow br1 table=4,actions=mod_dl_dst:$superedge_data_mac,"load:0->OXM_OF_IN_PORT[],resubmit(,5)"

#Table 5 is to forward to wireless interface @ control plane
sudo ovs-ofctl add-flow br0 table=5,actions=output:1
#Table 5 is to forward to wireless interface @ data plane
sudo ovs-ofctl add-flow br1 table=5,actions=output:2

#To prevent the infinite loop @ control plane
sudo ovs-ofctl add-flow br0 priority=1,in_port=1,actions=drop
#To prevent the infinite loop @ data plane
sudo ovs-ofctl add-flow br1 priority=1,in_port=2,actions=drop

sudo sysctl -p

