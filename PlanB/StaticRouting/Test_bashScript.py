import netifaces as ni
import subprocess as sp

def getIPaddress(interfaceName):
    """
    This function is to get the IP address from the interface.
    :param interfaceName: string of the interface name
    :return: ip : IP address of that interface
    """
    ni.ifaddresses(interfaceName)
    ip = ni.ifaddresses(interfaceName) [ni.AF_INET][0]['addr']
    return ip

def getMACaddress(interfaceName):
    """
    This function is to get MAC address from the interface.

    :param interfaceName: string of the interface name
    :return: mac_add : MAC address of that interface
    """

    addrs = ni.ifaddresses(interfaceName)
    mac_add = addrs[ni.AF_LINK][0]['addr']

    return mac_add

def getBroadcast(interfaceName):
    """
    This function is to get the broadcast IP address form the interface
    :param interfaceName: string of the interface name
    :return: broadcast IP address
    """


    addrs = ni.ifaddresses(interfaceName)
    broadcast_add = addrs[ni.AF_INET][0]['broadcast']

    return broadcast_add


## Test
print(getIPaddress('en0'))
print(getMACaddress('en0'))
print(getBroadcast('en0'))