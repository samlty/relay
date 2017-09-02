import os
import socket
import threading
import time

class socket2Client:
    def __init__(self, port=1194):
        self.__listenPort = port
        self.__init_socket(port)
        # item lists,
        # item = {"sourceAddr":(ip,port),"clientSession":sessionId,"serverSession":sessionId, "count":int}

        self.__AddrSessionList = []

        print ("start working server success")

    def __init_socket(self, port):
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.bind(('0.0.0.0', port))
        print ("bind 0.0.0.0:" + str(port) + "successful")


    def __get_list_item(self, address):
        for addr, value in self.__sourceAddrSocketMap.items():
            if addr == address:
                return value
        return None

    def __getAddrSessionItemWithClientSession(self, clientSession):
        for item in self.__AddrSessionList:
            if item.has_key("clientSession") and item["clientSession"]==clientSession:
                return Item

        return None

    def __getAddrSessionItemWithServerSession(self, serverSession):
        for item in self.__AddrSessionList:
            if item.has_key("serverSession") and item["serverSession"]==serverSession:
                return Item

        return None

    def __getLocalSessionId(self, data):
        if len(data)<9:
            return None
        sessionId = data[1:8]
        return sessionId

    def __getPeerSessionId(self, data):
        if len(data) < 22:
            return None

        sessionId = data[14:8]
        return sessionId
    def __handleMsgFromClient(self,data, clientAddr):
        opcode = data[0:1]
        opcode = opcode >> 3

        clientSession = self.__getLocalSessionId(data)
        addrSessionItem = self.__getAddrSessionItemWithClientSession(clientSession)



        if addrSessionItem is None:
            if opcode==7: #client reset
                print " not fount clientSession " + str(clientSession) + " new one"
                addrSessionItem = {}
                addrSessionItem["clientSession"] = clientSession
                addrSessionItem["sourceAddr"] = clientAddr
                addrSessionItem["count"] = 0
            else:
                print "recv known msg with known clientSession"
        else:
            addrSessionItem["count"] = 0


        self.__instance2Server.sendDataToDest(data)



    def handleMsgFromServer(self,data):
        opcode = data[0:1]
        opcode = opcode >> 3
        serverSession = self.__getLocalSessionId(data)

        if opcode==8: #server reset

            clientSession = self.__getPeerSessionId(data)

            addrSessionItem = self.__getAddrSessionItemWithClientSession(clientSession)
            if addrSessionItem is None:
                print "recv unkonw server reset msg, can not found clientSession list"
                return

            else:
                print " clientSession " + str(clientSession) + " existed, add remoteSession"
                addrSessionItem["serverSession"] = serverSession
                self.__sendData2Client(data, addrSessionItem["clientAddr"])

        else:
            addrSessionItem = self.__getAddrSessionItemWithServerSession(serverSession)
            if addrSessionItem is None:
                print " recv known server msg, can not found known serverSession"
            else:
                self.__sendData2Client(data, addrSessionItem["clientAddr"])






    def start(self,Instance2Server):

        #self.__destAddr = remoteAddr
        self.__instance2Server = Instance2Server
        while True:
            data, clientAddr = self.__sock.recvfrom(1024 * 10)
            self.__handleMsgFromClient(data, clientAddr)




    def __sendData2Client(self, data, address):
        self.__sock.sendto(data, address)



class socket2Server (threading.Thread):
    def __init__(self, port=8000):
        threading.Thread.__init__(self)

        print ("new a socker to recv/send data with server ")


        self.__localsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__localsock.bind(("0.0.0.0", port))
        print ("create localsock successful")

    def start(self, instance2Client):
        self.__instance2Client = instance2Client

        while True:
            data, address = self.__localsock.recvfrom(1024 * 10)

            if len(data)==5 and str(data)=="hello": # real

                self.__destAddr = address
                print "recv hello from " + str(address)


            elif (len(data)==4 and str(data)=="test"):
                print "recv test from " + str(address)
                self.__localsock.sendto("test", address)

            else:
                if self.__destAddr:
                    print ("recv data from server, send to client")

                    self.__instance2Client.handleMsgFromServer(data)


    def sendDataToDest(self, data):
        print "send data from " + str(self.__sourceAddr) + "to dest " + str(self.__destAddr)
        self.__localsock.sendto(data, self.__destAddr)






def getRemoteAddr(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    result = sock.bind(('0.0.0.0', port))
    print ("bind port %d succ and start recv" %port)
    data, address = sock.recvfrom(1024 * 10)
    sock.sendto("hello reply", address)
    print(" recv data from "+ str(address) + " so close socket")
    sock.close()
    return address



def main():
    clientInstance = socket2Client(1194)
    serverInstance = socket2Server(8000)
    clientInstance.start(serverInstance)
    serverInstance.start(clientInstance)

    while True:
        time.sleep(10)


main()

