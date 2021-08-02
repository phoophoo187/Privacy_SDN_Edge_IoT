This instructions show how to test static routing.

1)	Set every edge in ad-hoc mode for both control plane and data plane. The ad-hoc setting is written at /etc/network/interfaces in every edge.
2)	Check ping test for both control plane and data plane.
3)	Run edge*.sh file in edge*.  (for example, run edge1.sh in edge1, * is  from 1 to 6). Run edge*.sh file so that the ovs in edge* connect to the Ryu controller running in superedge.
4)	Check the connectivity between ovs in every edge* and Ryu controller by using the command, sudo ovs-vsctl show. If the status is connected, check the Openflow rules are installed in ovs of the edge* by using the command, sudo ovs-ofctl dump-flows br# . ( # is 0 and 1, 0 is for control plane and 1 is for data plane)
5)	Check ping test again for both control plane and data plane. In this step, it won’t be successful because all the network interfaces are now under the ovs bridge. The ovs needs flowrules and commands from Ryu controller to set the route.
6)	Before running superedge.sh in superedge to set up the Ryu controller, run the openflow state change handler (https://ryu.readthedocs.io/en/latest/ryu_app_api.html#ryu-controller-ofp-event-eventofpstatechange) in superedge to get the datapath-id of each edge.
7)	After getting the datapath-id of each edge, copy those datapath-id and paste at the datapath-id variables defined in the superedge.sh. 
8)	Run superedge.sh in superedge.

## How to run a static routing with preplaned re-routing scheme.
* The network topology is used for the code in [this repo](https://github.com/TNatapon/Privacy_SDN_Edge_IoT/tree/main/flowrules) is shown in the figure below. 
 
 ![SDNEdge architecture](https://github.com/TNatapon/Privacy_SDN_Edge_IoT/blob/main/PlanB/Figure_Readme/SADEdge-Topology.png) 