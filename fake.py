from scapy.all import *
import sys
import threading

def sendToPorts():
    data = "hello"
    while True:
        for i in range(45600,45700):
            pkt = IP(src=sys.argv[1], dst=sys.argv[2])/UDP(sport=1194, dport=i)/data
            send(pkt,inter=10,count=10000)

if __name__ == "__main__":
    if len(sys.argv)!=3:
        print("use sourip destip ")
        sys.exit(1)

    t = threading.Thread(target=sendToPorts)
    t.start()

    data = "hello"
    while True:

        pkt = IP(src=sys.argv[1], dst=sys.argv[2])/UDP(sport=1194, dport=8000)/data
        send(pkt,inter=10,count=10000)

