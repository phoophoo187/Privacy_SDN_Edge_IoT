1> Set edge1,edge2, edge4 and superedge in ad-hoc mode.

2> Do ping tests to check connectivities in ad-hoc network. ( In this stage, all ping tests should be successful.) 
Since all edges are close to each other in indoor testing, edge4 will reach to superedge with one hop.
But in the real environment, edge4 cannot reach to superedge with one hop. The primary route for edge4 to superedge is edge4->edge1->superedge.

3> To test primary route, Run edge1_pretest.sh in edge1. Run edge2_pretest.sh in edge2. Run edge4_pretest.sh in edge4. Run se_pretest.sh in superedge.
Ping edge4 to superedge, Ping test will be successful. But, if you check with tcpdump or wireshark, you will see that the packets from edge4 goes 
to edge1 first and edge1 relays that packet to superedge. The Openflow rules written in script files do that primary route.

4> Now, the primary routes are established.Then, so that the ovs in the edges connect to the Ryu controller running in superedge, run monitor_test.py
in superedge by using the command "ryu-manager monitor_test.py".   

5> Then, type the command "sudo ovs-vsctl show"  in edges and superedge to check whether the ovs in the edges and superedge are connected to Ryu 
controller or not. If the result of "sudo ovs-vsctl show" replies the status " is connected : true" , then, all the ovs are connected to Ryu controller.

6> After running monitor_test.py, it will give the datapath-ids of the ovs-bridges and the Openflow port-stats-replies. Copy those datapath-ids and paste
it in the superedge.py in the flowrules folder. 

7> Do the above steps for edge3,edge5 and edge6 also.


Static Predefined Routing 
-	Ryu controller doesn’t have information about the topology ( such as hop counts, Link information ,bandwidth, delay, information of neighboring nodes, etc)
-	Since the topology is small and fixed, the programmer knows the hop counts in the topology. So, based on the minimum hop counts in the topology, the predefined primary routes are written in the script files of the edges and the alternative routes used after the link fails are written at northbound interface of the Ryu controller. If the topology is large and not fixed, it is so much overloaded for the programmer to predefine all the alternative routes based on the hop counts. – one of the weaknesses of static predefined routing
Based on the above two facts, we call it “static predefined routing”.

-	Ryu controller can only detect the failures of the links, not the information of the link costs. After one link is failed, Ryu controller assigns the flowrules to the respective edges based on the predefined alternative routes no matter the selected alternative route has a lot of delay or less bandwidth (  because the Ryu controller doesn’t have the information of link costs). – main weakness of static predefined routing


How the Ryu controller detects the link failure?

Ryu controller sends the Openflow flowstats request messages to the edges. Then, the edges reply the Openflow flowstats reply messages to the Ryu controller. Ryu controller now gets the information about the packet counts and byte counts in each respective flow from the Openflow flowstats reply messages. Ryu controller does that procedure in each defined time interval. Then, Ryu controller knows that each link is failed or not based on number of the packet counts and byte counts in each flow. If the packet count and byte count are still the same in the previous time period and in the current time period in the flow even though the packets are still generating, then, the Ryu controller knows that that link is failed. 

How to verify that our static predefined routing program works?

We need to simulate traffic and simulate link failure cases by ourselves to verify the functionalities of our static predefined routing program. The reason why we need to simulate traffic and simulate link failures is that we are testing only in the small room in our lab where there are no link blocks that can happen link failures and we are not using the real traffic yet (later we use IoT data). 
To generate traffic, we use Iperf3.
To simulate link failures, we manually shutdown the wireless interfaces of the edges so that there will be no traffic receiving in the respective flow and Ryu controller sees it as it is link failure.
After link failures are happened, Ryu controller assigns the flowrules to the respective edges to establish the predefined alternative routes.

What kind of results we expect from static predefined routing?

1>	Predefined alternative routes work.  ( can be verified just by Ping results)
2>	The selected alternative route is not the optimum route every time because Ryu controller just chooses the predefined alternative route written by the programmer based on the hop counts in the topology. ( can be proved by using Ping result’s RTT values, we just simulate more traffic on the selected alternative route and shows that this alternative route cannot be the best route every time.)
It is not like Ryu controller knows all the link information of the topology dynamically and periodically and decides the optimum route based on the learnt link information –thus why, later, we use what we call “dynamic routing”.

