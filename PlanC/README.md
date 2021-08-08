1> Set edge1,edge2, edge4 and superedge in ad-hoc mode.

2> Do ping tests to check connectivities in ad-hoc network. ( In this stage, all ping tests should be successful.) 
Since all edges are close to each other in indoor testing, edge4 will reach to superedge with one hop.
But in the real environment, edge4 cannot reach to superedge with one hop. The primary route for edge4 to superedge is edge4->edge1->superedge.

3> To test primary route, Run edge1_pretest.sh in edge1. Run edge2_pretest.sh in edge2. Run edge4_pretest.sh in edge4. Run se.sh in superedge.
Ping edge4 to superedge, Ping test will be successful. But, if you check with tcpdump or wireshark, you will see that the packets from edge4 goes 
to edge1 first and edge1 relays that packet to superedge. The Openflow rules written in script files do that primary route.

4> Now, the primary routes are established.Then, so that the ovs in the edges connect to the Ryu controller running in superedge, run monitor_test.py
in superedge by using the command "ryu-manager monitor_test.py".   

5> Then, type the command "sudo ovs-vsctl show"  in edges and superedge to check whether the ovs in the edges and superedge are connected to Ryu 
controller or not. If the result of "sudo ovs-vsctl show" replies the status " is connected : true" , then, all the ovs are connected to Ryu controller.

6> After running monitor_test.py, it will give the datapath-ids of the ovs-bridges and the Openflow port-stats-replies. Copy those datapath-ids and paste
it in the superedge.py in the flowrules folder. 

7> Do the above steps for edge3,edge5 and edge6 also.
