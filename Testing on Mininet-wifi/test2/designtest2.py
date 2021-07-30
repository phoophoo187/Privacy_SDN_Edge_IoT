from mininet.node import Controller, RemoteController
from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd, mesh, adhoc
from mn_wifi.cli import CLI_wifi
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference
from mn_wifi.node import UserAP
import os 

def topology():

    "Create a network."
    net = Mininet_wifi(controller=RemoteController,link=wmediumd,wmediumd_mode=interference,accessPoint=UserAP)
    info("*** test3 for SDN-IoT-Edge project \n")
    info("*** Creating Access Point\n")

    sta1 = net.addStation('sta1',position='350,400,0')
    sta2 = net.addStation('sta2',position='700,350,0')
    sta3 = net.addStation('sta3',position='1050,400,0')
    sta4 = net.addStation('sta4',position='350,1000,0')
    sta5 = net.addStation('sta5',position='700,1050,0')
    sta6 = net.addStation('sta6',position='1050,1000,0')
    stag1 = net.addStation('stag1',position='50,700,0')
    stag2 = net.addStation('stag2',position='1400,700,0')



    ap1 = net.addAccessPoint('ap1',position='400,600,0',dpid='000000000001')
    ap2 = net.addAccessPoint('ap2',position='700,600,0',dpid='000000000002')
    ap3 = net.addAccessPoint('ap3',position='1000,600,0',dpid='000000000003')

    ap4 = net.addAccessPoint('ap4',position='400,800,0',dpid='000000000004')
    ap5 = net.addAccessPoint('ap5',position='700,800,0',dpid='000000000005')
    ap6 = net.addAccessPoint('ap6',position='1000,800,0',dpid='000000000006')

    gw1 = net.addAccessPoint('gw1',position='200,700,0',dpid='000000000007')
    gw2 = net.addAccessPoint('gw2',position='1250,700,0',dpid='000000000008')

    c0 = net.addController('c0')



    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Associating Stations\n")

    sta1.cmd('sudo ifconfig sta1-wlan0 down')
    sta2.cmd('sudo ifconfig sta2-wlan0 down')
    sta3.cmd('sudo ifconfig sta3-wlan0 down')
    sta4.cmd('sudo ifconfig sta4-wlan0 down')
    sta5.cmd('sudo ifconfig sta5-wlan0 down')
    sta6.cmd('sudo ifconfig sta6-wlan0 down')
    stag1.cmd('sudo ifconfig stag1-wlan0 down')
    stag2.cmd('sudo ifconfig stag2-wlan0 down')

    net.addLink(sta1,ap1,link='wired')
    net.addLink(sta2,ap2,link='wired')
    net.addLink(sta3,ap3,link='wired')
    net.addLink(sta4,ap4,link='wired')
    net.addLink(sta5,ap5,link='wired')
    net.addLink(sta6,ap6,link='wired')
    net.addLink(stag1,gw1,link='wired')
    net.addLink(stag2,gw2,link='wired')


    net.addLink(ap1,intf='ap1-wlan1',cls=adhoc,ssid='mesh-ssid',channel=5, mode='g')
    net.addLink(ap2,intf='ap2-wlan1',cls=adhoc,ssid='mesh-ssid',channel=5, mode='g')
    net.addLink(ap3,intf='ap3-wlan1',cls=adhoc,ssid='mesh-ssid',channel=5, mode='g')
    net.addLink(ap4,intf='ap4-wlan1',cls=adhoc,ssid='mesh-ssid',channel=5, mode='g')
    net.addLink(ap5,intf='ap5-wlan1',cls=adhoc,ssid='mesh-ssid',channel=5, mode='g')
    net.addLink(ap6,intf='ap6-wlan1',cls=adhoc,ssid='mesh-ssid',channel=5, mode='g')
    net.addLink(gw1,intf='gw1-wlan1',cls=adhoc,ssid='mesh-ssid',channel=5, mode='g')
    net.addLink(gw2,intf='gw2-wlan1',cls=adhoc,ssid='mesh-ssid',channel=5, mode='g')

    info("*** Starting network\n")
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
    gw2.start([c0])

    sta1.setIP('192.168.10.1/24', intf="sta1-eth1")
    sta2.setIP('192.168.10.2/24', intf="sta2-eth1")
    sta3.setIP('192.168.10.3/24', intf="sta3-eth1")
    sta4.setIP('192.168.10.4/24', intf="sta4-eth1")
    sta5.setIP('192.168.10.5/24', intf="sta5-eth1")
    sta6.setIP('192.168.10.6/24', intf="sta6-eth1")
    stag1.setIP('192.168.10.8/24', intf="stag1-eth1")
    stag2.setIP('192.168.10.9/24', intf="stag2-eth1")

    ap1.setIP('192.168.10.11/24', intf="ap1-eth2")
    ap2.setIP('192.168.10.12/24', intf="ap2-eth2")
    ap3.setIP('192.168.10.13/24', intf="ap3-eth2")
    ap4.setIP('192.168.10.14/24', intf="ap4-eth2")
    ap5.setIP('192.168.10.15/24', intf="ap5-eth2")
    ap6.setIP('192.168.10.16/24', intf="ap6-eth2")
    gw1.setIP('192.168.10.18/24', intf="gw1-eth2")
    gw2.setIP('192.168.10.19/24', intf="gw2-eth2")

    ap1.setIP('10.0.0.1/8', intf="ap1-wlan1")
    ap2.setIP('10.0.0.2/8', intf="ap2-wlan1")
    ap3.setIP('10.0.0.3/8', intf="ap3-wlan1")
    ap4.setIP('10.0.0.4/8', intf="ap4-wlan1")
    ap5.setIP('10.0.0.5/8', intf="ap5-wlan1")
    ap6.setIP('10.0.0.6/8', intf="ap6-wlan1")
    gw1.setIP('10.0.0.8/8', intf="gw1-wlan1")
    gw2.setIP('10.0.0.9/8', intf="gw2-wlan1")

    ap1.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')
    ap2.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')
    ap3.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')
    ap4.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')
    ap5.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')
    ap6.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')
    gw1.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')
    gw2.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')

    info("*** Running CLI\n")
    CLI_wifi(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()