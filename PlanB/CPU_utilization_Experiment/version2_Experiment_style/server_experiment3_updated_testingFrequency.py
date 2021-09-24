import socket
import csv

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('10.0.0.10', 12345))
sock.listen(5)
table_header = ['edge_name','unix_timestamp','percentage_cpu_utilisation']
f1 = open('./Experiment3_updated_testingFrequency/Experiment3_fixedE4/Edge1_CPU/edge1CPUM20.csv', 'w')
f2 = open('./Experiment3_updated_testingFrequency/Experiment3_fixedE4/Edge4_CPU/edge4_M15_edge1_M20.csv', 'w')
writer1 = csv.writer(f1)
writer2 = csv.writer(f2)
writer1.writerow(table_header)
writer2.writerow(table_header)
while True:
    conn, addr = sock.accept()
    from_client = ''
    while True:
        encode_data = conn.recv(1024)
        if not encode_data:
            break
        else:
            data = encode_data.decode()
            if 'edge1' in data:
                formatted_data1 = data.split('$')
                writer1.writerow(formatted_data1)
                print(formatted_data1)
            elif 'edge4' in data:
                formatted_data2 = data.split('$')
                writer2.writerow(formatted_data2)
                print(formatted_data2)
    conn.close()
    print('Client disconnect')

