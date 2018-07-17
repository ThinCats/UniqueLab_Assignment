import socketserver
import threading
import logging
import socket
import select
import errno
import sys

if __package__:
    from . import handler
    from . import Server
    from .cryptor import cipher
    from .resolver import codes, connect, nego

else:
    import handler
    import Server
    from cryptor import cipher
    from resolver import codes, connect, nego


socket.setdefaulttimeout(5)
# For handshake
magic_bytes = b"hello"

logger = logging
class EpollEnd(Exception):
    pass

class LocalHandler(Server.ProxyHandler):
    def _close(self):
        # For close socket
        self.request.close()
        self._to_srv_soc.close()
    
    def _handle_tcp(self):
        logger.info("TCP connection received")


        self._to_srv_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._to_srv_soc.connect(self.server.proxy_addr)
        except socket.error as e:
            logger.error("Can't connect to Proxy Server[{}:{}] [{}]".format(*self.server.proxy_addr, e))
            sys.exit(1)
            
        # Hello handshake [Local -- Server]
        self._send(self._to_srv_soc, magic_bytes, True)
            # Verify process
        hello_srv_recv_raw = self._to_srv_soc.recv(4096)
        
            # ACCEPT
        if len(hello_srv_recv_raw) == 1 + len(magic_bytes)  and hello_srv_recv_raw[0] == 0:
            logger.info("Connect to Proxy server[{}:{}] successful".format(*self.server.proxy_addr))
        else:
            logger.warn("Verify Proxy Server failed")
            # Refuse client's request
            handler.negotiation_srv(None, self.request, codes.METHOD["REFUSE"])
            self._to_srv_soc.close()
            return

        # Negotiation [Local -- Client]
        # nego_cli_recv_raw = handler.heartBeat_tcp(self.request.recv(4096), self.request)
        nego_cli_recv_raw = self._recv(self.request, 4096, False)

        is_verified_ok = handler.negotiation_srv(nego_cli_recv_raw, self.request)
        if not is_verified_ok:
            self._to_srv_soc.close()
            return # end request
        
        # Connection [Client -- Local -- Server]
            # Forward client's packet to Server
        # connect_cli_recv_raw = handler.heartBeat_tcp(self.request.recv(4096), self.request)
        connect_cli_recv_raw = self._recv(self.request, 4096, False)

        self._send(self._to_srv_soc, connect_cli_recv_raw, True) 
            # Forward Server to client
        connect_srv_recv_raw = self._recv(self._to_srv_soc, 4096, True)

        # self.request.send(connect_srv_recv_raw)
        self._send(self.request, connect_srv_recv_raw)
            # Check status
        connect_cli_send = connect.cli_decode(connect_srv_recv_raw)
        logger.debug("{}".format(connect_cli_send))
        if not connect_cli_send[1] == codes.STATUS["SUCCEED"]:
            # Remote fail   
            logger.debug("Connecting to {}:{} fail".format(*connect_cli_send[3]))
            self._to_srv_soc.close()
            return
        else:
            # TCP
            if self._to_srv_soc.type == socket.SOCK_STREAM or 2049:
                logger.info("Connected to {}:{}".format(*self._to_srv_soc.getpeername()))
                self._forward_tcp(self.request, self._to_srv_soc, False, True)
            # UDP: 2050True
            else:
                self._forward_udp()
        
        # Close all fd
        self._to_srv_soc.close()

class TCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

class SocksServer(object):

    def __init__(self, ip, port, handler, password, server_addr, server_port):
        self._server = TCPServer((ip, port), handler)
        # Init cipher
        self._server.cryptor = cipher.RC4(password)
        # Proxy server addr
        self._server.proxy_addr = (server_addr, server_port)

    def shutdown(self):
        self._server.shutdown()
    
    def start(self):
        self._server.serve_forever()

if __name__ == "__main__":
    server = SocksServer("127.0.0.1", 6233, LocalHandler, "2333", "127.0.0.1", 9899)
    server.start()