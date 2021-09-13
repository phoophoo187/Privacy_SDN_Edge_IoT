import socket
import csv

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('10.0.0.10', 12345))
sock.listen(5)
f1 = open('./Experiment3_fixedE4/edge1CPUM1.csv', 'w')
f2 = open('./Experiment3_fixedE4/edge4CPUM15_E1M1.csv', 'w')
writer1 = csv.writer(f1)
writer2 = csv.writer(f2)
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
            
            #writer.writerow([data])
            #print(data)
    conn.close()
    print('Client disconnect')

