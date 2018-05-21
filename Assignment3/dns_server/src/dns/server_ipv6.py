
import socket
import logging
import threading
import struct

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

    def __init__(self, addr_family):
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

    def _handle_udp(self, sock, addr, data):
        request = (data, sock)
        client_addr = addr
        handler = myDNSHandler(request, client_addr, socket.SOCK_DGRAM, self._addr_family)
        handler.handle()
        logger.debug("Thread ends {}".format(threading.current_thread().name))

    def _udp_server(self):
        a_socket = socket.socket(self._addr_family, socket.SOCK_DGRAM)
        a_socket.bind((self._ip, self._port))
        while True:
            a_socket.settimeout(20)
            try:
                data, addr = a_socket.recvfrom(1024)
            except socket.timeout:
                data, addr = a_socket.recvfrom(1024)
            
            thread_udp = threading.Thread(target=self._handle_udp, args=(a_socket, addr, data))
            logger.debug("Thread starts {}".format(thread_udp.name))
            
            thread_udp.start()


    def start_server(self, isTcp=False, ip="localhost", port=53):
        self._ip = ip
        self._port = port
        self._isTcp = isTcp

        if isTcp:
            self._tcp_server()
        else:
            self._udp_server()


if __name__ == "__main__":

    server = myServer(socket.AF_INET)
    server.start_server(False)
