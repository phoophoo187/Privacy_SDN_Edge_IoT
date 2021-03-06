# Mininet-WiFi Beginer
- We will walk you through how to use mininet-wifi from a beginer to the advance labs. We provide the examples for many use cases. This tutorial is beased on [mininet-wifi](https://www.brianlinkletter.com/2016/04/mininet-wifi-software-defined-network-emulator-supports-wifi-networks/).

## Tutorial #1: One access point
One access point shows how to run the simplest Mininet-WiFi scenario, shows how to capture wireless traffic in a Mininet-Wifi network, and discusses the issues with OpenFlow and wireless LANs. 
- The simplest network is the default topology, which consists of a wireless access point with two wireless stations. The access point is a switch connected to a controller. The stations are hosts.
- This simple lab will allow us to demonstrate how to capture wireless control traffic and will demonstrate the way an OpenFlow-enabled access point handles WiFi traffic on the wlan interface.

### Capturing Wireless control traffic in Mininet-WiFi
 To view wireless control traffic we must first start Wireshark:

`$ sudo wireshark &` <br/>
Activate Mininet-WiFi. It will start with the default network scenario using the command below: <br/>
`$ sudo mn --wifi` <br/>
![wireshark_activate](./Figure/Tutorial_1/Activate_mininet-wifi.png) <br/>

After we up `hwsim0` interface by command <br/>
`$ sh ifconfig hwsim0 up`, <br/>
we let wireshark caputer `hwsim0` interface. <br/>
![hwsim0](./Figure/Tutorial_1/hwsim0.png) <br/>

To see the links, nodes, and network connectivity, we can use commands: <br/>
- `links`
- `nodes`
- `net` <br/>

To see the OpenFlow packets, you have to sniff the packets at local loopback interface, while we ping `sta1` to `sta2`. <br/>
![ping_station](./Figure/Tutorial_1/ping_two_stations.png) <br/>
![ping_loopback](./Figure/Tutorial_1/ping_loopback.png) <br/>
![openflow](./Figure/Tutorial_1/wireshark_loopback.png) <br/>
![openflow_packet](./Figure/Tutorial_1/openflow_packet.png) <br/>

To terminate mininet-wifi, we use command: <br/>
`$ exit` <br/>
After we exit mininet-wifi terminal, to clear the setting, we use command: <brr/>
`$ sudo mn -c` <br/>

## Tutorial #2 : Multiple access points
In this tutorial, we will create a linear topology with three access points, where one station is connected to each access point. 
Remember, you need to already know basic Mininet commands to appreciate how we create topologies using the Mininet command line.
Run Mininet-Wifi and create a linear topology with three access points:

`$ sudo mn --wifi --topo linear, 3`

From the output of the command, we can see how the network is set up and which stations are associated with which access points.
![creating_network](./Figure/Tutorial_2/create_linear_topology.png)

We can also verify the configuration using the Mininet CLI commands `net` and `dump`.
- Run command `net` to see the connectivity between nodes:
![net](./Figure/Tutorial_2/net.png)
- Run `dump` to see the IP addresses assigned to the access points and the stations. 
![dump](./Figure/Tutorial_2/dump.png)
- 