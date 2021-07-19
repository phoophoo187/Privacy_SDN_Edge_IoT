# Privacy_SDN_Edge_IoT
SDN Assisted Privacy Preserving in Distributed Edge Computing for IoT
- In this project, we deploy SDN to assist a distributed edge computing network to optimally forward IoT preserving messages to the computing node optimally.   
xxxxxxx

* [General Information](#general-information)
* [Technologies Used](#technologies-used)
* [Features](#features)
* [Screenshots](#screenshots)
* [Setup](#setup)
* [Usage](#usage)
* [Project Status](#project-status)
* [Room for Improvement](#room-for-improvement)
* [Acknowledgements](#acknowledgements)
* [Project contributors](#Project contributors)
* [Project contributors](#Project-contributors)
* [Contact](#contact)
<!-- * [License](#license) -->

## General Information
SADEdge is a part of "Privacy-Preserving as a Service for IoT" project. SADEdge mainly focuses on developing the network management techniques that can imporve the network reliability and efficiency of distributed edge computing for IoT. SDN has been seen a promising tool becasue the SDN framework can simplify the network management and make the distributed edge computing controlable. <br />
SADEdge is a part of "Privacy-Preserving as a Service for IoT" project. SADEdge mainly focuses on developing the network management techniques that can imporve the network reliability and efficiency of distributed edge computing for IoT. SDN has been seen a promising tool becasue the SDN framework can simplify the network management and can make the distributed edge computing controlable. <br />

SDNEdge consists of 3 main elements: 
* SDN controller : We use [Ryu controller](https://github.com/faucetsdn/ryu) as a SDN controller to manage the IoT packet flows.
* Virtual switch : We use [OvS](https://www.openvswitch.org/) as a virtual swich located in an edge computing node. 
* Wireless mesh ad-hoc network : We form a distributed edge computing network with a wireless mesh ad-hoc netowork where edge nodes rely the MQTT messages from IoT devices (i.e., Edge computing nodes) to the IoT gateway (i.e., Super Edge node) and forwords those MQTT messages to the IoT cloud. 
* Wireless mesh ad-hoc network : We form a distributed edge computing (DEC) network with a wireless mesh ad-hoc netowork where edge nodes rely the MQTT messages from IoT devices (i.e., Edge computing nodes) to the IoT gateway (i.e., Super Edge node) and forwords those MQTT messages to the IoT cloud. 

SDNEdge Architecture: 


![SDNEdge architecture](https://github.com/TNatapon/Privacy_SDN_Edge_IoT/blob/main/Figure/SADEdge-Architecture.png)

SADEdge network topology: 
* Here we present an example of SADEdge network topology

![SDNEdge network topology](https://github.com/TNatapon/Privacy_SDN_Edge_IoT/blob/main/Figure/SADEdge-Topology.png)


## Technologies Used
- [Ryu Controller](https://ryu-sdn.org/) 
- [OvS](https://www.openvswitch.org/download/)
- [MQTT broker](https://www.hivemq.com/blog/mqtt-toolbox-mqttbox/)
- Raspberry Pi 3 model B+ 
- Wireless antenna, i.e., one which is compatible with Raspberry Pi 3 model B+ is [TP-Link](https://www.tp-link.com/th/home-networking/adapter/archer-t2u-plus/)
- Raspberry Pi 3 model B+ with Raspbian OS
- Wireless antenna, i.e., one which is compatible with Raspberry Pi 3 model B+ is [TP-Link](https://www.tp-link.com/th/home-networking/adapter/archer-t2u-plus/) and its driver can be downloaded from [rtl8812au](https://github.com/aircrack-ng/rtl8812au) which supports the USB id your wifi adapters use.  For the Raspbian OS and they are available to download from [wifi-driver](http://downloads.fars-robotics.net/wifi-drivers/).


## Features
## Features (Under testing)
List the ready features here:
- Awesome feature 1
- Awesome feature 2
- Awesome feature 3
- Wireless ad-hoc mode
- [Maximum Throughput](https://github.com/TNatapon/Privacy_SDN_Edge_IoT/tree/main/PlanB) 
- [Static routing](https://github.com/TNatapon/Privacy_SDN_Edge_IoT/tree/main/flowrules)
- Dynamic routing





## Screenshots
![Example screenshot](./img/screenshot.png)
<!-- If you have screenshots you'd like to share, include them here. -->


@@ -51,10 +63,17 @@ Proceed to describe how to install / setup one's local environment / get started


## Usage
How does one go about using it?
Provide various use cases and code examples here.
How do we test the maximum througput of a link between a edge node pairs

`write-your-code-here`
`iperf3 -u -c 10.0.0.1 -b0 -n 20M -bidir`

How to test a static routing algorithm
1) Make all Raspberry Pis in ad-hoc mode <br />
2) Run `run.sh files` in all Raspberry Pis <br />
3) After running sh files , pi cant ping each other anymore <br />
4) Run [superedge.py](https://github.com/TNatapon/Privacy_SDN_Edge_IoT/blob/main/flowrules/superedge.py) file in superedge by using  <br />
`ryu-manager superedge.py` 
6) Rum ping commnad again in each Raspberry Pi <br />


## Project Status
@@ -94,19 +113,19 @@ SADEdge is a part of the Privacy-Preserving as a Service for IoT project was sup

* Koonlachat Meesublak <br />
   * Researcher <br />
   * CPS (Cyber-Physical Systems) Laboratory NECTEC, Thailand <br />
   * CPS (Cyber-Physical Systems) Laboratory, NECTEC, Thailand <br />

* Natapon Tansangworn <br />
   * Researcher <br />
   * CPS (Cyber-Physical Systems) Laboratory NECTEC, Thailand <br />
   * CPS (Cyber-Physical Systems) Laboratory, NECTEC, Thailand <br />

* Tawan Hohum <br />
   * Researche Assistant <br />
   * CPS (Cyber-Physical Systems) Laboratory NECTEC, Thailand <br />
   * CPS (Cyber-Physical Systems) Laboratory, NECTEC, Thailand <br />

* Phoo Phoo Thet Lyar Tun <br />
   * Researche Assistant <br />
   * CPS (Cyber-Physical Systems) Laboratory NECTEC, Thailand <br />
   * CPS (Cyber-Physical Systems) Laboratory, NECTEC, Thailand <br />


## Contact
