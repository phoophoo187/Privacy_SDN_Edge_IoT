import csv
byte_list = [1,2,3,6,12,15,20,25,30,33,35]
edge_list = [1,2]
newlist = []
for i in byte_list:
    with open('edge1CPUM'+str(i)+'.csv', 'r') as csvfile:
        for row in csvfile:
            data = row.split(',')[2]
            print(data)
            newlist.append(data)
print(newlist)
