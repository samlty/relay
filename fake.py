from scapy.all import *
import sys
import threading
import time
import fcntl
import struct
import socket
import ConfigParser

g_globalConfig={}

def getConfig(conf_file):
    global    g_globalConfig

    config = ConfigParser.RawConfigParser()
    config.read(conf_file)

    serverPorts = config.get("global", "serverPorts")
    serverPortList = serverPorts.strip().split(',')
    g_globalConfig["serverPorts"]=[]
    for port in serverPortList:
        g_globalConfig["serverPorts"].append(int(port))

    g_globalConfig["startProxyPort"] = int(config.get("global", "startPort"))
    g_globalConfig["endProxyPort"] = int(config.get("global", "endPort"))


def getIpFromInterface(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,
        struct.pack('512s', ifname[:15])
    )[20:24])


def sendToPorts(ifname, hostname):
    #data = "hello"

    localIp = getIpFromInterface(ifname)
    remoteIp = socket.gethostbyname(hostname)
    print "local ip is " + localIp + " remoteip is " + remoteIp

    while True:


        for i in range(g_globalConfig["startProxyPort"], g_globalConfig["endProxyPort"]):
            for port in g_globalConfig["serverPorts"]:
                pkt = IP(src=localIp, dst=remoteIp)/UDP(sport=port, dport=i)/("heLLo"+str(port))
                send(pkt)


    
    time.sleep(20)

if __name__ == "__main__":
    if len(sys.argv)!=3:
        print("use interfaceName destip/hostname ")
        sys.exit(1)

    getConfig("proxy.conf")
    t = threading.Thread(target=sendToPorts, args=(sys.argv[1],sys.argv[2],))
    t.start()

    while True:
	time.sleep(10)
        
