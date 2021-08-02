This instructions show how to test static routing.

1)	Set every edge in ad-hoc mode for both control plane and data plane. The ad-hoc setting is written at /etc/network/interfaces in every edge.
2)	Check ping test for both control plane and data plane.
3)	Run edge*.sh file in edge*.  (for example, run edge1.sh in edge1, * is  from 1 to 6). Run edge*.sh file so that the ovs in edge* connect to the Ryu controller running in superedge.
4)	Check ping test again for both control plane and data plane. In this step, it won’t be successful because all the network interfaces are now under the ovs bridge. The ovs needs flowrules and commands from Ryu controller to set the route.
5)	Before running superedge.py in superedge to set up the Ryu controller, run the openflow state change handler (https://ryu.readthedocs.io/en/latest/ryu_app_api.html#ryu-controller-ofp-event-eventofpstatechange) in superedge to get the datapath-id of each edge.
6)	After getting the datapath-id of each edge, copy those datapath-id and paste at the datapath-id variables defined in the superedge.sh. 
7)	Run superedge.py in superedge by using the command 'ryu-manager superedge.py'
8)	Check the connectivity between ovs in every edge* and Ryu controller by using the command, sudo ovs-vsctl show. If the status is connected, check the Openflow rules are installed in ovs of the edge* by using the command, sudo ovs-ofctl dump-flows br# . ( # is 0 and 1, 0 is for control plane and 1 is for data plane)
9)	Do ping tests again that did in step2. In this step, ping tests will be successful.
## How to run a static routing with the preplaned re-routing scheme
* The network topology is used for the code in [this repo](https://github.com/TNatapon/Privacy_SDN_Edge_IoT/tree/main/flowrules) is shown in the figure below. 
 
 ![SDNEdge architecture](https://github.com/TNatapon/Privacy_SDN_Edge_IoT/blob/main/PlanB/Figure_Readme/SADEdge-Topology.png) 
 
* In this experiment, we have 6 edge nodes, ie., Edge\#1, Edge\#2,..., Edge\#6, and 1 super edge node, i.e., SE. 
### Manual setup
1. Set all edge nodes in the ad-hoc mode for the control plane and data plane. The setting of ad-hoc mode is written in all edge node in
    `/etc/network/interfaces/` <br/>
2. Check the connectivity of all edge nodes and the super edge node with`ping` command for both control plane and data plane. The expected result after running `ping` command is all edge nodes and super edge nodes can ping to each other.

3. Copy shell script `edge1.sh` file to Edge\#1, and change 1 to 2,...,6 for Edge\#2, Edge\#2,...,Edge\#6, respectively.

4. Set execute permission on script file`edge*.sh` by using command : <br/>
`sudo chmod +x edge*.sh` <br/>

5. Run script `edge1.sh` by command: 
`sudo ./edge1.sh`
Do for all edge nodes. After running 'edge1.sh' file, do ping test again as did in step2. In this step, ping tests wont be successful anymore.  By this time, the edge nodes and the super node cannot ping to each other because the network interfaces are under the OVS bridge. Hence, OVS needs the flowrules and commands from Ryu controller to set the route. 

6. Run the [OpenFlow state change handler](https://ryu.readthedocs.io/en/latest/ryu_app_api.html#ryu-controller-ofp-event-eventofpstatechange) in the super edge node to get the "datapath-id" of each edge. 

7. Copy python program `superedge.py` file to the super edge node to run the Ryu controller.

8. Then, use the command 'ryu-manager superedge.py' to run the Ryu controller in super edge.

9. Check the connectivity between OVS in all edge nodes and Ryu controller by command: <br/>
`sudo ovs-vsctl show`

10. If the status is "connected", then check whether the OpenFlow rules have been installed in ovs of all edge node or not by command: <br />
`sudo ovs-ofctl dump-flows br0`  for the control plane, and
`sudo ovs-ofctl dump-flows br1` for the data plane

11. Do ping tests again. In this step, ping tests will be successful.
