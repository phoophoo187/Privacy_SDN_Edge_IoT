#This is the design Program for SDNIoTEdge Project @ Mininet-wifi written by PPTLT.

from mininet.node import Controller,RemoteController,OVSSwitch
from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd, mesh, adhoc
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference
from mn_wifi.node import UserAP
import os 
from time import sleep

class InbandController( RemoteController ):

    def checkListening( self ):
        "Overridden to do nothing."
        return

def topology():

    info("*** Emulated SDNIoTEdge Design! \n")
    net = Mininet_wifi(controller=InbandController,link=wmediumd,wmediumd_mode=interference,accessPoint=UserAP,switch=OVSSwitch)
    ip_c0 = '10.0.0.101'
    info("*** Installing UserAPs, Switch and Host  \n")
    h1 = net.addHost('h1',position='400,1000,0',ip=ip_c0)
    s1 = net.addSwitch('s1',mac='10:00:00:00:00:01',failMode='standalone',dpid='10')
    ap1 = net.addAccessPoint('edge1',mac='00:00:00:00:00:10',position='400,800,0',inNamespace=True,dpid='1')
    ap2 = net.addAccessPoint('edge2',mac='00:00:00:00:00:20',position='700,800,0',inNamespace=True,dpid='2',)
    ap3 = net.addAccessPoint('edge3',mac='00:00:00:00:00:30',position='1000,800,0',inNamespace=True,dpid='3')
    ap4 = net.addAccessPoint('edge4',mac='00:00:00:00:00:40',position='400,600,0',inNamespace=True,dpid='4')
    ap5 = net.addAccessPoint('edge5',mac='00:00:00:00:00:50',position='700,600,0',inNamespace=True,dpid='5')
    ap6 = net.addAccessPoint('edge6',mac='00:00:00:00:00:60',position='1000,600,0',inNamespace=True,dpid='6')
    gw1 = net.addAccessPoint('superedge',mac='00:00:00:00:00:70',position='700,950,0',inNamespace=True,dpid='7')

    c0 = net.addController('c0', controller=InbandController,port=6653,ip=ip_c0)
    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()
    info("*** Configuring wireless links\n")
    net.addLink(h1,s1,intfName1='h1-eth0')
    net.addLink(ap1,s1)
    net.addLink(ap2,s1)
    net.addLink(ap3,s1)
    net.addLink(ap4,s1)
    net.addLink(ap5,s1)
    net.addLink(ap6,s1)
    net.addLink(gw1,s1)

    net.addLink(ap1,intf='edge1-wlan1',cls=adhoc,ssid='mesh-ssid',channel=5, mode='g')
    net.addLink(ap2,intf='edge2-wlan1',cls=adhoc,ssid='mesh-ssid',channel=5, mode='g')
    net.addLink(ap3,intf='edge3-wlan1',cls=adhoc,ssid='mesh-ssid',channel=5, mode='g')
    net.addLink(ap4,intf='edge4-wlan1',cls=adhoc,ssid='mesh-ssid',channel=5, mode='g')
    net.addLink(ap5,intf='edge5-wlan1',cls=adhoc,ssid='mesh-ssid',channel=5, mode='g')
    net.addLink(ap6,intf='edge6-wlan1',cls=adhoc,ssid='mesh-ssid',channel=5, mode='g')
    net.addLink(gw1,intf='superedge-wlan1',cls=adhoc,ssid='mesh-ssid',channel=5, mode='g')

    net.plotGraph(max_x=2000, max_y=1500)
    net.build()
    c0.start()
    ap1.start([c0])
    ap2.start([c0])
    ap3.start([c0])
    ap4.start([c0])
    ap5.start([c0])
    ap6.start([c0])
    gw1.start([c0])
    s1.start([c0])

    sleep(3)
    ap1.cmd('ifconfig edge1-eth2 10.0.0.201')
    ap2.cmd('ifconfig edge2-eth2 10.0.0.202')
    ap3.cmd('ifconfig edge3-eth2 10.0.0.203')
    ap4.cmd('ifconfig edge4-eth2 10.0.0.204')
    ap5.cmd('ifconfig edge5-eth2 10.0.0.205')
    ap6.cmd('ifconfig edge6-eth2 10.0.0.206')
    gw1.cmd('ifconfig superedge-eth2 10.0.0.207')
    h1.cmd('ifconfig h1-eth1 10.0.0.102')

    ap1.setIP('192.168.1.1/24', intf="edge1-wlan1")
    ap2.setIP('192.168.1.2/24', intf="edge2-wlan1")
    ap3.setIP('192.168.1.3/24', intf="edge3-wlan1")
    ap4.setIP('192.168.1.4/24', intf="edge4-wlan1")
    ap5.setIP('192.168.1.5/24', intf="edge5-wlan1")
    ap6.setIP('192.168.1.6/24', intf="edge6-wlan1")
    gw1.setIP('192.168.1.8/24', intf="superedge-wlan1")

    s1.cmd('sysctl net.ipv4.ip_forward=1')
    s1.cmd('ifconfig s1-eth1 10.0.0.209')
    s1.cmd('ifconfig s1-eth2 10.0.0.210')
    s1.cmd('ifconfig s1-eth3 10.0.0.211')
    s1.cmd('ifconfig s1-eth4 10.0.0.212')
    s1.cmd('ifconfig s1-eth5 10.0.0.213')
    s1.cmd('ifconfig s1-eth6 10.0.0.214')
    s1.cmd('ifconfig s1-eth7 10.0.0.215')
   
    info("*** Running CLI\n")
    CLI(net)
    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()
