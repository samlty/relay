import os
import socket
import threading
import time

class udp_work_server:
    def __init__(self, port):
        self.__listenPort = port
        self.__init_socket(port)
        self.__sourceAddrSocketMap = {}
        print ("start working server success")




    def __init_socket(self, port):
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.bind(('0.0.0.0', port))
        print ("bind 0.0.0.0:" + port + "successful")

    def __get_list_item(self, address):
        for addr, value in self.__sourceAddrSocketMap.items():
            if addr == address:
                return value
        return None

    def start(self,remoteAddr):

        self.__destAddr = remoteAddr
        while True:
            data, clientAddr = self.__sock.recvfrom(1024 * 10)
            item = self.__get_list_item(clientAddr)
            if item is None:
                print ("clientaddr " + str(clientAddr) + " not existed new one instance")
                transInstance = udp_threading(self.__sock, clientAddr, self.__destAddr)
                transInstance.start()
                self.__sourceAddrSocketMap[clientAddr] =transInstance
            else:
                transInstance = item

            transInstance.sendDataToDest(data)


class udp_threading (threading.Thread):
    def __init__(self, mainSock, sourceAddr, destAddr):
        threading.Thread.__init__(self)
        self.__mainSock = mainSock
        self.__sourceAddr = sourceAddr
        self.__destAddr = destAddr
        print ("new a socker to recv/send data with soureAddr ")
        print (self.__sourceAddr)
        print ("start new thread")

        self.__localsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print ("create localsock successful")

    def run(self):

        while True:
            data, address = self.__localsock.recvfrom(1024 * 10)
            print ("recv data from dest")
            print (address)
            self.__sendDataBackSourceUseMainSock(data)


    def __sendDataBackSourceUseMainSock(self, data):
        print "send data back to source " + self.__sourceAddr
        self.__mainSock.sendto(data, self.__sourceAddr)

    def sendDataToDest(self, data):
        print "send data from " + str(self.__sourceAddr) + "to dest " + str(self.__destAddr)
        self.__localsock.sendto(data, self.__destAddr)





def getRemoteAddr(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    result = sock.bind(('0.0.0.0', port))
    print ("bind port %d succ and start recv" %port)
    data, address = sock.recvfrom(1024 * 10)
    sock.close()
    return address


def main():
    workInstance = udp_work_server(1194)
    remoteAddr = getRemoteAddr(8000)


    workInstance.start(remoteAddr)
    while True:
        time.sleep(10)


main()

