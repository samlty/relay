import os
import socket
import threading
import time
import sys

g_sockUsedList = [] # {} sock:sock, addr:addr count or sock:None
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



def clientSocketEntry(clientSock):

    while True:
        data, clientAddr = clientSock.recvfrom(1024 * 10)
        handleMsgFromClient(data, clientAddr)


def getSockFromClientAddr(clientAddr):
    for item in g_sockUsedList:
        if item.has_key("addr") and not cmp(item["addr"],clientAddr):
            print "successful"
            return item["sock"]

    return None

def handleMsgFromClient(data, clientAddr):

    global g_sockUsedList

    sock2Server = getSockFromClientAddr(clientAddr)
    if sock2Server is None:

        for item in g_sockUsedList:
            if not item.has_key("addr"):

                item["addr"] = clientAddr
                item["count"] = 0
                print "new a thread for addr " + str(clientAddr)

                sock2Server = item["sock"]
                t = threading.Thread(target=serverSocketEntry, args=(sock2Server, clientAddr,))
                t.start()
                break

        if sock2Server is None:
            print "sock is full pls reboot app"
            return


    if g_serverAddr:
        sock2Server.sendto(data, g_serverAddr)

def serverSocketEntry(serverSock, clientAddr):
    global g_serverAddr
    while True:
        data, address = serverSock.recvfrom(1024 * 10)

        if len(data) == 5 and str(data) == "hello":  # real
            if g_serverAddr is None:
                g_serverAddr = address
            print "recv hello from " + str(address)


        elif (len(data) == 4 and str(data) == "test"):
            print "recv test from " + str(address)
            self.__serverSock.sendto("test", address)

        else:
            if clientAddr:
                g_clientSock.sendto(data, clientAddr)


def main():

    global g_clientSock
    global g_sockUsedList
    g_clientSock = init_socket(1194)
    descovery_sock = init_socket(8000)
    if g_clientSock is None or descovery_sock is None:
        print "bind 1194 or 8000 failed"
        sys.exit(1)

    t = threading.Thread(target=serverSocketEntry, args=(descovery_sock, None))
    t.start()

    for i in range(45600,45700):
        sock = init_socket(i)
        if sock is None:
            print "bind port %d failed continue" %i
            continue
        item={}
        item["sock"]=sock
        g_sockUsedList.append(item)





    clientSocketEntry(g_clientSock)




    while True:
        time.sleep(10)


main()

