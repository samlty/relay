import os
import socket
import threading
import time
import sys

g_sockAddrList = [] # {} sock:sock, addr:client addr count:int port:port of socket
g_clientSock = None
g_serverAddr = None


def init_socket(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.bind(('0.0.0.0', port))
    except Exception:
        print ("bind 0.0.0.0:" + str(port) + "failed")
        return None

    print ("bind 0.0.0.0:" + str(port) + "successful")
    return sock


def getLocalPortFromClientAddr(clientAddr):
    for item in g_sockAddrList:
        if item.has_key("addr") and not cmp(item["addr"], clientAddr):
            # print "successful"
            return item["port"]

    return None
def getSockFromClientAddr(clientAddr):
    for item in g_sockAddrList:
        if item.has_key("addr") and not cmp(item["addr"],clientAddr):
            #print "successful"
            return item["sock"]

    return None

def handleMsgFromClient(data, clientAddr):

    global g_sockAddrList

    sock2Server = getSockFromClientAddr(clientAddr)

    if sock2Server is None:

        for item in g_sockAddrList:
            if not item.has_key("addr"):

                item["addr"] = clientAddr
                item["count"] = 0
                print "new a thread for addr " + str(clientAddr)

                sock2Server = item["sock"]
                t = threading.Thread(target=serverSocketEntry, args=(sock2Server, clientAddr, item["port"],))
                t.start()


                break

        if sock2Server is None:
            print "sock is full pls reboot app"
            return


    if g_serverAddr:
        localport = getLocalPortFromClientAddr(clientAddr)
        if localport:
            print "recv data from " + str(clientAddr) + " send to " + str(g_serverAddr) + " use localport " + str(localport)
        sock2Server.sendto(data, g_serverAddr)

def serverSocketEntry(serverSock, clientAddr, localPort):
    global g_serverAddr
    while getSockFromClientAddr(clientAddr): # if clientSocket Handle clean it, thread is over
        data, address = serverSock.recvfrom(1024 * 10)

        if len(data) == 5 and str(data) == "hello":  # real
            if g_serverAddr is None:
                g_serverAddr = address
            print "port " + str(localPort) + " recv hello from " + str(address)


        elif (len(data) == 4 and str(data) == "test"):
            print  "port " + str(localPort) + "recv test from " + str(address)
            serverSock.sendto("test", address)

        else:
            if clientAddr:
                g_clientSock.sendto(data, clientAddr)
    print ("thread with port " + str(localPort) + " exited")


def checkCount():
    global g_sockAddrList

    while True:
        for item in g_sockAddrList:
            if item.has_key("count") and item.has_key("addr"):
                if item["count"] > 10:  # too old  , no traffic during 10*10s, clean it
                    print "addr " + str(item["addr"]) + " and localport " + str(item("port")) + " is too old, clean it"
                    del item["addr"]
                    del item["count"]
                else:
                    item["count"] += 1

        time.sleep(10)

def main():

    global g_clientSock
    global g_sockAddrList
    g_clientSock = init_socket(1194)
    descovery_sock = init_socket(8000)
    if g_clientSock is None or descovery_sock is None:
        print "bind 1194 or 8000 failed"
        sys.exit(1)

    # start 8000 socket to recv package to get WAN addr of vpn server
    t = threading.Thread(target=serverSocketEntry, args=(descovery_sock, None, 8000))
    t.start()

    # start 100 socket to use, per client use one
    for i in range(45600,45700):
        sock = init_socket(i)
        if sock is None:
            print "bind port %d failed continue" %i
            continue
        item={}
        item["sock"]=sock
        item["port"]=i
        g_sockAddrList.append(item)

    # start a thread to check too old client
    timeThead = threading.Thread(target=checkCount)
    timeThead.start()

    # handle msg from clients
    while True:
        data, clientAddr = g_clientSock.recvfrom(1024 * 10)
        handleMsgFromClient(data, clientAddr)

if __name__ == "__main__":
    main()

