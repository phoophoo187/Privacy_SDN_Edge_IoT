Firstly,to run the network topology, run DesignSDNIoTEdge.py program by using the command "sudo python3 DesignSDNIoTEdge.py".
After that, open the console of the edges and host by using the command "xterm edge1 edge2 edge3 h1" ,etc.
If you want run the dynamic routing program by using the Option0, run Option0.py program, if Option1a, run Option1a.py program ,etc.
To run the dynamic routing program in Ryu controller, you need to run it in the host 'h1', so, firstly, type "xterm h1", then, 
in the console of h1, type "ryu-manager Option0.py".

For all the dynamic routing programs which need the CPU utilization values, you need to run the cpu_utilization_socket.py program by using 
the command "sudo python3 cpu_utilization_socket.py -e edge*" where * = 1,2,3,4,5,6 in all edges. 

Option1b_with_newCPU_calculation.py program is the new version of Option1b.py program where CPU utilization values are calculated by using the new method ( tx bytes + rx bytes with Sigmoid function).
