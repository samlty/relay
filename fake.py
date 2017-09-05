from scapy.all import *
import sys
import threading
import time
import fcntl
import struct
import socket

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
        for i in range(45600,45700):
            pkt = IP(src=localIp, dst=remoteIp)/UDP(sport=500, dport=i)/"hello500"
            send(pkt)
            pkt = IP(src=localIp, dst=remoteIp) / UDP(sport=4500, dport=i) / "hello4500"
            send(pkt)

    
    time.sleep(10)

if __name__ == "__main__":
    if len(sys.argv)!=3:
        print("use interfaceName destip/hostname ")
        sys.exit(1)

    time.sleep(20)
    t = threading.Thread(target=sendToPorts, args=(sys.argv[1],sys.argv[2],))
    t.start()

    while True:
	time.sleep(10)
        
