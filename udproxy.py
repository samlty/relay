#coding:utf-8
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

# g_proxyInfoList是列表对象，其中的每个
# 每个Item是一个Dict对象，Dict对象保存proxy转发所需要的：
# proxySock:sock, 这是指proxySock线程所拥有的sock对象，与target通信，初始化赋值
# ProxyPort:port of socket, proxySock的绑定Port，初始化赋值

# clientAddr:记录原始客户端的地址，1，处理客户端报文时，根据clientAddr寻找proxySock和target addr， server线程赋值
# 2，处理target报文时，用于填写转发目标地址
# originalServerPort：原始服务端口，比如500，比如4500， server线程赋值
# serverSock：与client通信用的socket对象 server线程赋值
# count:用于统计是否长时间没有收发数据，如果长时间没有收发数据，就置为空闲状态 server线程赋值

# serverAddr＋str(serverPort): 可能有一个或多个。 proxySock转发多个服务器端口，每个端口都有一个addr 比如对于500端口，有serverAddr500，
# 对于4500端口有serverAddr4500 server线程转发数据时使用其中一个  proxy线程赋值，在收到hello报文后

g_proxyInfoList = []
g_globalConfig = {}


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


# 根据clientAddr和原始serverport查找记录
# 同一个client可能用同一个原端口发送到多个目标端口

def getItemFromClientAddr(clientAddr, originalServerPort):
    for item in g_proxyInfoList:
        if item.has_key("clientAddr") and not cmp(item["clientAddr"], clientAddr) and \
                item.has_key("originalServerPort") and item["originalServerPort"]==originalServerPort:
            # print "successful"
            logging.debug("found existed item use " + str(clientAddr) + " and original port " + str(originalServerPort))
            return item
    logging.info(" not found existed item use " + str(clientAddr) + " and original port " + str(originalServerPort))
    return None

def handleMsgFromClient(selfSock, data, clientAddr, selfPort ): # serverAddr500 or serverAddr4500
    logging.debug("selfPort " + str(selfPort) +"recv data from client " + str(clientAddr))
    global g_proxyInfoList

    infoItem = getItemFromClientAddr(clientAddr, selfPort)

    if infoItem is None:
        logging.info (" not found with clientAddr" + str(clientAddr) + " and original port " + str(selfPort))

        for item in g_proxyInfoList:
            if not item.has_key("clientAddr"):
                logging.info("get an unused item with port " + str(item["proxyPort"]))

                item["clientAddr"] = clientAddr
                item["count"] = 0
                item["serverSock"]=selfSock
                item["originalServerPort"] = selfPort
                infoItem = item

                break

        if infoItem is None:
            logging.error("sock is full pls reboot app")
            return

    infoItem["count"] = 0
    addrKey = "serverAddr" + str(selfPort)
    if infoItem.has_key(addrKey):

        serverAddr = infoItem[addrKey]
        proxyPort = infoItem["proxyPort"]
        proxySock = infoItem["proxySock"]

        logging.debug( "clientAddr " + str(clientAddr) + " -> " + str(selfPort) + " : " + str(proxyPort) + " -> " + str(serverAddr) )
        proxySock.sendto(data, serverAddr)




def proxySocketEntry(infoItem):
    # info Item is an dict item
    # sock: current Sock
    # port: bind port
    # to be add :
    #     clientAddr: clientAddr  added by main thread
    #     serverAddr: vpn server addr added by self thread

    localPort = infoItem["proxyPort"]
    proxySock = infoItem["proxySock"]

    while True: # if clientSocket Handle clean it, thread is over
        data, address = proxySock.recvfrom(1024 * 10)
        logging.debug("port " + str(localPort) + " recv data from target " + str(address))

        if str(data[0:5]) == "heLLo":  # real
            originServerPort = 0
            logging.debug("port " + str(localPort) + "recv an " + str(data) + " from " + str(address))

            try:

                originServerPort = int(data[5:])
            except Exception as e:
                logging.error(" recv invalid heLLo+ msg " + str(data))
                return

            if not infoItem.has_key("serverAddr" + str(originServerPort)):

                infoItem["serverAddr" + str(originServerPort)] = address
                logging.info( "proxy port " + str(localPort) + " bind address to " + str(address))

            #print "port " + str(localPort) + " recv hello from " + str(address)
            elif cmp(infoItem["serverAddr" + str(originServerPort)], address):
                logging.info( "port " + str(localPort) + "rebind address from " + str(infoItem["serverAddr" + str(originServerPort)]) + " to " + str(address))
                infoItem["serverAddr" + str(originServerPort)] = address



        elif (len(data) == 4 and str(data) == "test"):
            logging.info(  "port " + str(localPort) + "recv test from " + str(address))
            proxySock.sendto("test", address)

        else:

            if infoItem.has_key("clientAddr") and infoItem.has_key("serverSock"):
                logging.debug( "targetAddr " + str(address)  + " -> " + str(localPort) \
                               + " : " + str(infoItem["originServerPort"]) + " -> " + str(infoItem["clientAddr"]))
                infoItem["serverSock"].sendto(data, infoItem["clientAddr"])
            else:
                logging.error("proxySock " + str(localPort) + " has no clientAddr or serverSock")



def checkCount():
    global g_proxyInfoList

    while True:
        for item in g_proxyInfoList:
            if item.has_key("count") and item.has_key("clientAddr"):
                if item["count"] > 10:  # too old  , no traffic during 10*10s, clean it
                    logging.info( "addr " + str(item["clientAddr"]) + " and localport " + str(item["port"]) + " is too old, clean it")
                    del item["clientAddr"]
                    del item["count"]
                    del item["originServerPort"]
                    del item["serverSock"]
                else:
                    item["count"] += 1

        time.sleep(10)

def serverSocketEntry(serverSock,port):
    # handle msg from clients

    while True:
        data, clientAddr = serverSock.recvfrom(1024 * 10)
        handleMsgFromClient(serverSock, data, clientAddr, port)


def bindServerPortsAndStartThread():
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

        t = threading.Thread(target=serverSocketEntry, args=(sock,port,))
        t.start()

    logging.info("binding serverPort and start threading successful")


def startProxyThreading():
    global g_globalConfig

    for i in range(g_globalConfig["startProxyPort"], g_globalConfig["endProxyPort"]):
        sock = init_socket(i)
        if sock is None:
            logging.error("bind port %d failed continue" % i)
            continue

        item = {}
        item["proxySock"] = sock
        item["proxyPort"] = i
        g_proxyInfoList.append(item)

        t = threading.Thread(target=proxySocketEntry, args=(item,))
        t.start()

        logging.info("bind port " + str(i) + " && start thread succ")


def main():

    global g_proxyInfoList
    global g_globalConfig



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

