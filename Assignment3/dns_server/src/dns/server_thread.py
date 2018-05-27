# Use logging for logs
import logging
import socketserver
import threading
import socket
import time
import struct

if __package__ == None:
    from dnsresolve import dnsrecord
    from dnsresolve.field import codes
    from dnsresolve import dnsresolver
    import dnshandler
    from dnscache import dnscache
    from dnsauth import dnsauth

else:
    from .dnsresolve import dnsrecord
    from .dnsresolve.field import codes
    from .dnsresolve import dnsresolver
    from . import dnshandler
    from .dnscache import dnscache
    from .dnsauth import dnsauth

# logging config
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s- %(message)s")
logger = logging.getLogger(__name__)

# Handle both TCP/UDP by if-else
class myDNSHandler(socketserver.BaseRequestHandler):

    def handle(self):
        # ALL need two
        logger.debug("Thread running %s" %(threading.current_thread().name))
        # Judge whether it's TCP
        if self.server.socket_type == socket.SOCK_STREAM:
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
        self._handler = dnshandler.DNSHandler(self._isTcp, self._resolver, self._cli_sock, self.client_address, socket.AF_INET)
        
        # Zone handle
        if self._handler.auth_handle():
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
        logger.debug("Thread ending {}".format(threading.current_thread().name))





            
        


# For MixIn server
class myUDP(socketserver.ThreadingMixIn, socketserver.UDPServer):
    allow_reuse_address = True

class myTCP(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

# Main server
class myDNSServer(object):

    def __init__(self, isTcp, ip, port, handler):

        if isTcp:
            self._server = myTCP((ip, port), handler)
        else:
            self._server = myUDP((ip, port), handler)

    # Refer to Python Doc about socketserver
    # New a thread
    def start(self):
        self._thread = threading.Thread(target=self._server.serve_forever)
        self._thread.daemon = True
        self._thread.start()

        logger.info("Server loop running in Thread: %s" %(self._thread.name))        

    def test_start(self):
        self._server.serve_forever()

    def shutdown(self):
        self._server.shutdown()


if __name__ == "__main__":
    # server = myDNSServer(False, "127.0.0.1", 53, myDNSHandler)
    server = myDNSServer(False, "127.0.0.1", 53, myDNSHandler)
    # server.start()
    server.start()
    while(1):
        time.sleep(10000)
        
    
    