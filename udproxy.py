import os
import socket
import threading
import time
import sys
import logging
import ConfigParser

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%m-%d %H:%M:%S',
                filename='myapp.log',
                filemode='w')

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)




g_sockAddrList = [] # {} sock:sock, clientAddr:client addr count:int port:port of socket, serverAddr: vpn server addr

g_globalConfig = {}
g_serverSockList = []


def init_socket(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.bind(('0.0.0.0', port))
    except Exception as ex:
        logging.error ("bind 0.0.0.0:" + str(port) + "failed")
        logging.error(str(ex))
        return None

    logging.info ("bind 0.0.0.0:" + str(port) + "successful")
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
            logging.debug("found existed item use " + str(clientAddr))
            return item
    logging.info(" not found existed item use " + str(clientAddr))
    return None

def handleMsgFromClient(selfSock, data, clientAddr, addrKey ): # serverAddr500 or serverAddr4500
    logging.debug("recv data from client " + str(clientAddr))
    global g_sockAddrList

    infoItem = getItemFromClientAddr(clientAddr)

    if infoItem is None:
        logging.info (" not found with clientAddr" + str(clientAddr))

        for item in g_sockAddrList:
            if not item.has_key("clientAddr"):
                logging.info("get an unused item with port " + str(item["port"]))

                item["clientAddr"] = clientAddr
                item["count"] = 0
                item["serverSock"]=selfSock
                infoItem = item

                break

        if infoItem is None:
            logging.error("sock is full pls reboot app")
            return


    if infoItem.has_key(addrKey):
        serverAddr = infoItem[addrKey]
        localport = infoItem["port"]
        sock = infoItem["sock"]

        logging.debug( "recv data from " + str(clientAddr) + " send to " + str(serverAddr) + " use localport " + str(localport))
        sock.sendto(data, serverAddr)

def getServerSockFromData(serverSockList, data):
    try:
        port = int(str(data[5:]))
        for item in serverSockList:
            if item["port"]==port:
                return item

        return None

    except Exception:
        logging.error("trans data hello from server with error data")
        return None

def getServerSockFromAddress(serverSockList, address):
    for item in serverSockList:
        if item.has_key("addr") and not cmp(address, item["addr"]):
            return item
    logging.error("not found address item " + str(address))
    return None

def proxySocketEntry(infoItem):
    # info Item is an dict item
    # sock: current Sock
    # port: bind port
    # to be add :
    #     clientAddr: clientAddr  added by main thread
    #     serverAddr: vpn server addr added by self thread
    global g_serverSockList


    serverSockItem = None

    localPort = infoItem["port"]
    proxySock = infoItem["sock"]


    while True: # if clientSocket Handle clean it, thread is over
        data, address = proxySock.recvfrom(1024 * 10)
        logging.debug("port " + str(localPort) + " recv data from target " + str(address))

        if str(data[0:5]) == "heLLo":  # real

            logging.debug("port " + str(localPort) + "recv an " + str(data) + " from " + str(address))
            serverSockItem = getServerSockFromData(g_serverSockList, data)
            if serverSockItem is None:
                logging.error( "port " + str(localPort) + " recv an unkonwn hello msg")
                continue

            serverPort = serverSockItem["port"]


            if not infoItem.has_key("serverAddr" + str(serverPort)):

                infoItem["serverAddr" + str(serverPort)] = address
                logging.info( "port " + str(localPort) + " add address to " + str(address))

            #print "port " + str(localPort) + " recv hello from " + str(address)
            elif cmp(infoItem["serverAddr" + str(serverPort)], address):
                logging.info( "port " + str(localPort) + "renew address from " + str(infoItem["serverAddr" + str(serverPort)]) + " to " + str(address))
                infoItem["serverAddr" + str(serverPort)] = address



        elif (len(data) == 4 and str(data) == "test"):
            logging.info(  "port " + str(localPort) + "recv test from " + str(address))
            proxySock.sendto("test", address)

        else:

            if infoItem.has_key("clientAddr") and infoItem.has_key("serverSock"):
                logging.debug( "port " + str(localPort) + "recv data from " + str(address) + " send to " + str(infoItem["clientAddr"]))
                infoItem["serverSock"].sendto(data, infoItem["clientAddr"])



def checkCount():
    global g_sockAddrList

    while True:
        for item in g_sockAddrList:
            if item.has_key("count") and item.has_key("clientAddr"):
                if item["count"] > 10:  # too old  , no traffic during 10*10s, clean it
                    logging.info( "addr " + str(item["clientAddr"]) + " and localport " + str(item["port"]) + " is too old, clean it")
                    del item["clientAddr"]
                    del item["count"]
                else:
                    item["count"] += 1

        time.sleep(10)

def serverSocketEntry(serverSock,addrKey):
    # handle msg from clients
    logging.critical("in " + addrKey)
    while True:
        data, clientAddr = serverSock.recvfrom(1024 * 10)
        handleMsgFromClient(serverSock, data, clientAddr, addrKey)


def bindServerPortsAndStartThread():
    global g_serverSockList
    portList = []
    if g_globalConfig.has_key("serverPorts"):
        portList = g_globalConfig["serverPorts"]
    else:
        logging.error(" get serverPorts failed")

    for port in portList: #port is int
        sock = init_socket(port)
        if sock is None:
            logging.error("bind server port" + str(port) + " failed")
            sys.exit(1)
        item = {}
        item["sock"]=sock
        item["port"]=port
        t = threading.Thread(target=serverSocketEntry, args=(sock,"serverAddr"+str(port),))
        t.start()
        item["thread"]=t
        g_serverSockList.append(item)

    logging.info("binding serverPort and start threading successful")


def startProxyThreading():
    global g_globalConfig

    for i in range(g_globalConfig["startProxyPort"], g_globalConfig["endProxyPort"]):
        sock = init_socket(i)
        if sock is None:
            logging.error("bind port %d failed continue" % i)
            continue

        item = {}
        item["sock"] = sock
        item["port"] = i
        g_sockAddrList.append(item)
        t = threading.Thread(target=proxySocketEntry, args=(item,))
        t.start()
        item["thread"]=t
        logging.info("bind port " + str(i) + " && start thread succ")


def main():

    global g_sockAddrList
    global g_globalConfig
    global g_serverSockList


    bindServerPortsAndStartThread()
    startProxyThreading()

    # start a thread to check too old client

    timeThead = threading.Thread(target=checkCount)
    timeThead.start()
    logging.info("start checkout thread successful")
    
    while True:
        time.sleep(10)

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





if __name__ == "__main__":
    getConfig("proxy.conf")
    main()

