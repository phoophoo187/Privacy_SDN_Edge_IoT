import sys, getopt
import psutil
import socket
import time

def send_cpu_utilization(server_ip, server_port, send_time_interval, cpu_time_interval, edge):
    '''        
        current timestamp for comparing the time difference in ryu controller to dynamically update CPU utilization     
        send CPU utilization percentage every t second to ryu controller
    '''
    while True:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        server.connect((server_ip, server_port))        

        CPU_percent = psutil.cpu_percent(interval=float(cpu_time_interval))
        current_time = time.time()    
        send_data = edge + '$ ' + str(current_time) + '$ ' + str(CPU_percent)
        server.sendall(send_data.encode())
        print(send_data)        
        server.close()  
        time.sleep(float(send_time_interval))      

def main(argv):

    '''
        server_ip = ryu controller ip address
        server_port = port of ryu controller's socket server
        interval = collect cpu utilization percentage from edge in every interval second
        send_time_interval = send collected information to ryu controller in every send time interval
        edge is used only for emulated purpose since the mac address or ip address is the same in emulated environment                  
    '''
    cpu_time_interval = 1
    server_ip = "10.0.0.10"
    send_time_interval = 10
    server_port = 12345
    edge = None
    
    try:
        opts, args = getopt.getopt(argv, "h:t:c:s:p:e:", ["send-time-interval=", "cpu-time-interval=","server=", "port=", "edge="])
    except getopt.GetoptError:
        print('CPUUtilizationSocket.py -t <send_time_interval> -c <cpu_time_interval> -s <server_ip> -p <server_port> -e <edge>')
        print('Default send time interval = ', send_time_interval)
        print('Default cpu time interval = ', cpu_time_interval)
        print('Default server ip = ', server_ip)
        print('Default server port = ', server_port)        
        print('Edge information required (eg. edge1)')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('CPUUtilizationSocket.py -t <send_time_interval> -c <cpu_time_interval> -s <server_ip> -p <server_port> -e <edge>')
            print('Default send time interval = ', send_time_interval)
            print('Default cpu time interval = ', cpu_time_interval)
            print('Default server ip = ', server_ip)
            print('Default server port = ', server_port)
            print('Edge information required (eg. edge1)')
            sys.exit()
        elif opt in ("-t", "--send-time-interval"):
            send_time_interval = arg
        elif opt in ("-c", "--cpu-time-interval"):
            cpu_time_interval = arg
        elif opt in ("-s", "--server"):
            server_ip = arg
        elif opt in ('-p', "--port"):
            server_port = arg
        elif opt in ('-e', "--edge"):
            edge = arg
    
    if edge is not None:    
        #server =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #server.connect((server_ip, server_port))
        #server.sendall(edge.encode())

        #encoded_data = server.recv(1024)
        #data = encoded_data.decode() 
        #print("Im Herer")
        #print(data)
        #if 'is connected' in data:
        #    print("Conected")
        #    server.close()
        send_cpu_utilization(server_ip, server_port, send_time_interval, cpu_time_interval, edge)    
        #else:
        #    print('Error')             
    else:
        print("Please insert edge information with -e.")   

if __name__ == "__main__":
    main(sys.argv[1:])
