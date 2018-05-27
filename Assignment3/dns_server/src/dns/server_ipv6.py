
import socket
import logging
import threading
import struct

import multiprocessing
import os

logger = logging

if __package__:
    from . import dnshandler
    from .dnsresolve import dnsresolver

else:
    import dnshandler
    from dnsresolve import dnsresolver

class myDNSHandler(object):

    def __init__(self, request, client_addr, socket_type, addr_family):
        self.request = request
        self.client_address = client_addr
        self.socket_type = socket_type
        self._addr_family = addr_family
    
    def handle(self):
        # ALL need two
        logger.debug("Thread running %s" %(threading.current_thread().name))
        # Judge whether it's TCP
        if self.socket_type == socket.SOCK_STREAM:
            self._isTcp = True
            logger.info("TCP connection received")

            data = self.request.recv(8192)
            length = struct.unpack("!H", data[:2])[0]
            # Not finishing recving
            if len(data) < length + 2:
                data += self.request.recv(8192)
            data = data[2:]
            self._cli_sock = self.request
        
        # UDP
        else:
            self._isTcp = False
            logger.info("UDP connection received")
            data, self._cli_sock = self.request
            # logger.debug(data)
            # logger.debug(cli_sock)
            # Process
            # logger.debug("Data: %s" %(data))

        # Create the resolver 
        self._resolver = dnsresolver.DNSResolver(data)
        header = self._resolver.unpack_header_raw()
        # Call different functions
        # New the handler functions
        self._handler = dnshandler.DNSHandler(self._isTcp, self._resolver, self._cli_sock, self.client_address, self._addr_family)

        # Zone handle
        if self._handler.auth_handle():
            # Successful
            return

        # cache handle
        if self._handler.cache_handle():
            # Successful
            return 

        # recursive desire
        if header.read_flag("rd") == 1:
            self._handler.recursive_query()
            
        # Iter
        else:
            print(header.read_flag("rd"))
            self._handler.iterative_query()
            print("Temp do not support iter")

        # Close socketf
        # self._cli_sock.close()

class myServer(object):

    def __init__(self, addr_family, is_tcp=False, ip="localhost", port=53):
        self._ip = ip
        self._port = port
        self._isTcp = is_tcp
        self._addr_family = addr_family


    def _handle_tcp(self, sock, addr):
        request = sock
        client_addr = addr
        handler = myDNSHandler(request, client_addr, socket.SOCK_STREAM, self._addr_family)
        handler.handle()
        logger.debug("Thread ends {}".format(threading.current_thread().name))
        sock.close()

    def _tcp_server(self):
        a_socket = socket.socket(self._addr_family, socket.SOCK_STREAM)
        a_socket.bind((self._ip, self._port))
        a_socket.listen(20)

        while True:
            a_socket.settimeout(100000)
            sock, addr = a_socket.accept()
            
            thread_tcp = threading.Thread(target=self._handle_tcp, args=(sock, addr))
            logger.debug("Thread starts {}".format(thread_tcp.name))
            thread_tcp.start()

        a_socket.close()
    
    def _handle_udp(self, sock, addr, data):
        request = (data, sock)
        client_addr = addr
        handler = myDNSHandler(request, client_addr, socket.SOCK_DGRAM, self._addr_family)
        handler.handle()
        logger.debug("Thread ends {}".format(threading.current_thread().name))

    def _udp_server(self):
        a_socket = socket.socket(self._addr_family, socket.SOCK_DGRAM)
        a_socket.bind((self._ip, self._port))
        a_socket.setblocking(False)
        while True:
            a_socket.settimeout(200000)
            data, addr = a_socket.recvfrom(1024)
            
            thread_udp = threading.Thread(target=self._handle_udp, args=(a_socket, addr, data))
            logger.debug("Thread starts {}".format(thread_udp.name))
            
            thread_udp.start()

        a_socket.close()


    def start_server(self):
        if self._isTcp:
            self._tcp_server()
        else:
            self._udp_server()

def start_server(is_ipv6, is_tcp, ip="localhost", port=53):

    ipv6_str_dic = {"True":"IPV6", "False":"IPV4"}
    tcp_str_dic = {"True":"TCP", "False":"UDP"}
    # Indicate message (server type info)
    print("{} with {} Server is starting".format(ipv6_str_dic[str(is_ipv6)], tcp_str_dic[str(is_tcp)]))
    if is_ipv6:
        server = myServer(socket.AF_INET6, is_tcp, ip, port)  
    else:
        server = myServer(socket.AF_INET, is_tcp, ip, port)

    server.start_server()

def start_server_multi():
    server_list = []
    # ipv4, udp
    server_list.append(myServer(socket.AF_INET, False))
    # ipv4, tcserver_list[i].start_server()p
    server_list.append(myServer(socket.AF_INET, True))
    # ipv6, tcp
    server_list.append(myServer(socket.AF_INET6, True))
    # ipv6, udp
    server_list.append(myServer(socket.AF_INET6, False))

    print("Start all server from parent process {}".format(os.getpid()))
    # server_pool = multiprocessing.Pool(4)
    process_list = []
    for i in range(4):
        # start server in pool
        print("server starts")
        # server_pool.apply_async(server_list[i].start_server())
        p = multiprocessing.Process(target=test_)
        p.start()
        process_list.append(0)
    # process_list[0].join()
    print("Server end")
    # server_pool.close()
    # Wait for all server shutdown
    # server_pool.join()

    print("Server all close")


def test_():
    print("Test {}".format(os.getpid()))
    while True:
        pass

    

if __name__ == "__main__":

    start_server_multi()
