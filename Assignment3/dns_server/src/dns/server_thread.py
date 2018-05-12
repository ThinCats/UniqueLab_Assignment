# Use logging for logs
import logging
import socketserver
import threading
import socket

if __package__ == None:
    from dnsresolve import dnsrecord
    from dnsresolve.field import codes
    from dnsresolve import packet_resolve

else:
    from .dnsresolve import dnsrecord
    from .dnsresolve.field import codes
    from .dnsresolve import packet_resolve

# logging config
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s-%(name)s-%(levelname)s-%(message)s")
logger = logging.getLogger(__name__)

# Handle both TCP/UDP by if-else
class myDNSHandler(socketserver.BaseRequestHandler):

    def handle(self):
        
        # Judge whether it's TCP
        if self.server.socket_type == socket.SOCK_STREAM:
            self._isTcp = True
            logger.info("TCP connection received")
            data = self.request.recv(8192)
            print(data)
        
        # UDP
        else:
            self._isTcp = False
            logger.info("UDP connection received")
            data, cli_sock = self.request
            # logger.debug(data)
            # logger.debug(cli_sock)
            # Process

            record = dnsrecord.DNSRecord()
            # record.add_header(1, codes.OPCODE["query"], 1, 1, 1, 1, 1, codes.RCODE["NoError"])
            header = packet_resolve.packet_split(data)[0]
            logger.debug("Header: %s" %(header))
            record.add_header_raw(header)
            record.modify_header(qr=codes.QR["response"], aa=1, RA=1)

            record.add_answer("baidu.com", codes.TYPE["A"], 655, "127.0.0.1")
            record.add_auth("baidu.com", 444, "dns.baidu.com")
            record.add_addi("baidu.com", 3334, codes.TYPE["A"], "128.1.1.1")
            record.pack()
            logger.debug("Sent data {}".format(record.data))
            cli_sock.sendto(record.data, self.client_address)

# For MixIn server
class myUDP(socketserver.UDPServer, socketserver.ThreadingMixIn):
    allow_reuse_address = True

class myTCP(socketserver.TCPServer, socketserver.ThreadingMixIn):
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
        self._server.server_close()


if __name__ == "__main__":
    server = myDNSServer(False, "127.0.0.1", 53, myDNSHandler)
    # server.start()
    server.test_start()
    