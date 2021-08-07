Instructions to run SDNIoTEdgeProject on Mininet-wifi
-------------------------------------------------

1> Install mininet-wifi 
https://github.com/intrig-unicamp/mininet-wifi

2> Install SDN switch: ofsoftswitch13 on Mininet-wifi by using the command "sudo util/install.sh -3f"

3> Install Ryu controller
https://ryu.readthedocs.io/en/latest/getting_started.html

4> To setup the topology for SDNIoTEdgeProject , run Design_SDNIoTEdge.py

5> Then, xterm h1 ( which is the host that the Ryu controller runs on ).

6> On h1, run the Ryu controller code , RyuProgram@SuperEdge@Mininet-wifi.py 

Note***
Run all programs with python3

# Mininet-WiFi Environment
Here we present the setting of Mininet-WiFi for the experiments.
## Wireless Mesh Network Topology
- There are 6 edge nodes and 1 super edge node in the network.
- The distance between an edge nodes and its neighbor are <b style='color:red'> XX </b> meters.
- The radio range of each node is  <b style='color:red'> XX </b> meters.
- All edge nodes and super node have 2 wireless interfaces, i.e., `wlan0` and `wlan1`, which support the ad hoc mode
of IEEE 802.11.
- The transmission power is <b style='color:red'> XX </b> dBm. 
- The radio frequency is 2.412 GHz. 
- MAC addresses of all nodes are as follows.  
** Edge\#1 : <b style='color:red'> XXXXX </b>
