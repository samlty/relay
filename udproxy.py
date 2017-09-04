import os
import socket
import threading
import time
import sys



g_sockAddrList = [] # {} sock:sock, clientAddr:client addr count:int port:port of socket, serverAddr: vpn server addr
g_clientSock = None



def init_socket(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.bind(('0.0.0.0', port))
    except Exception:
        print ("bind 0.0.0.0:" + str(port) + "failed")
        return None

    print ("bind 0.0.0.0:" + str(port) + "successful")
    return sock


# def getLocalPortFromClientAddr(clientAddr):
#     for item in g_sockAddrList:
#         if item.has_key("clientAddr") and not cmp(item["clientAddr"], clientAddr):
#             # print "successful"
#             return item["port"]
#
#     return None
# def getSockFromClientAddr(clientAddr):
#     for item in g_sockAddrList:
#         if item.has_key("clientAddr") and not cmp(item["clientAddr"],clientAddr):
#             #print "successful"
#             return item["sock"]
#
#     return None



def getItemFromClientAddr(clientAddr):
    for item in g_sockAddrList:
        if item.has_key("clientAddr") and not cmp(item["clientAddr"], clientAddr):
            # print "successful"
            return item

    return None

def handleMsgFromClient(data, clientAddr):

    global g_sockAddrList

    infoItem = getItemFromClientAddr(clientAddr)

    if infoItem is None:
        print (" not found with clientAddr" + str(clientAddr))

        for item in g_sockAddrList:
            if not item.has_key("clientAddr"):

                item["clientAddr"] = clientAddr
                item["count"] = 0
                infoItem = item

                break

        if infoItem is None:
            print "sock is full pls reboot app"
            return


    if infoItem.has_key("serverAddr"):
        serverAddr = infoItem["serverAddr"]
        localport = infoItem["port"]
        sock = infoItem["sock"]

        print "recv data from " + str(clientAddr) + " send to " + str(serverAddr) + " use localport " + str(localport)
        sock.sendto(data, serverAddr)

def serverSocketEntry(infoItem):
    # info Item is an dict item
    # sock: current Sock
    # port: bind port
    # to be add :
    #     clientAddr: clientAddr  added by main thread
    #     serverAddr: vpn server addr added by self thread

    localPort = infoItem["port"]
    serverSock = infoItem["sock"]

    while True: # if clientSocket Handle clean it, thread is over
        data, address = serverSock.recvfrom(1024 * 10)

        if len(data) == 5 and str(data) == "hello":  # real
            if not infoItem.has_key("serverAddr"):
                infoItem["serverAddr"] = address
                print "port " + str(localPort) + " add address " + str(address) + " to infoItem[\"serverAddr\"]"
            print "port " + str(localPort) + " recv hello from " + str(address)


        elif (len(data) == 4 and str(data) == "test"):
            print  "port " + str(localPort) + "recv test from " + str(address)
            serverSock.sendto("test", address)

        else:
            if infoItem.has_key("clientAddr"):
                print "port " + str(localPort) + "recv data from " + str(address) + " send to " + str(infoItem["clientAddr"])
                g_clientSock.sendto(data, infoItem["clientAddr"])


def checkCount():
    global g_sockAddrList

    while True:
        for item in g_sockAddrList:
            if item.has_key("count") and item.has_key("clientAddr"):
                if item["count"] > 10:  # too old  , no traffic during 10*10s, clean it
                    print "addr " + str(item["clientAddr"]) + " and localport " + str(item["port"]) + " is too old, clean it"
                    del item["clientAddr"]
                    del item["count"]
                else:
                    item["count"] += 1

        time.sleep(10)

def main():

    global g_clientSock
    global g_sockAddrList
    g_clientSock = init_socket(1194)

    if g_clientSock is None:
        print "bind 1194  failed"
        sys.exit(1)



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
        t = threading.Thread(target=serverSocketEntry, args=(item,))
        t.start()

    # start a thread to check too old client
    timeThead = threading.Thread(target=checkCount)
    timeThead.start()

    # handle msg from clients
    while True:
        data, clientAddr = g_clientSock.recvfrom(1024 * 10)
        handleMsgFromClient(data, clientAddr)

if __name__ == "__main__":
    main()

