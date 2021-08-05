import netifaces as ni
import subprocess as sp

# Create a new bridge named br0 and add port eth0 to it.

## delete the specific bridge.
def delBridge(brName):

    sp.run(['ovs-vsctl --if-exists del-br', brName])
