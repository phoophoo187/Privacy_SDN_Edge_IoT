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
