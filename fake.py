from scapy.all import *
import sys
import threading
import time

def sendToPorts():
    data = "hello"
    while True:
        for i in range(45600,45700):
            pkt = IP(src=sys.argv[1], dst=sys.argv[2])/UDP(sport=1194, dport=i)/data
            send(pkt)
    
    time.sleep(10)

if __name__ == "__main__":
    if len(sys.argv)!=3:
        print("use sourip destip ")
        sys.exit(1)

    t = threading.Thread(target=sendToPorts)
    t.start()

    while True:
	time.sleep(10)
        
