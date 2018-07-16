import socketserver
import threading
import logging
import socket
import select
import errno
import sys

if __package__:
    from .resolver import codes, connect
    from . import handler
    from .cryptor import cipher
else:
    from .resolver import codes, connect
    import handler
    from cryptor import cipher

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s- %(message)s")
logger = logging.getLogger(__name__)

# For handshake
magic_bytes = b"hello"

class myHandler(socketserver.BaseRequestHandler):
    # This is for forwarding packet
    def _forward_tcp(self):
        logger.info("Start forwarding from {}:{} to {}:{}".format(*self.request.getpeername(), *self._to_srv_soc.getpeername()))

        # Use epoll to fowarding packet
        epoll = select.epoll()
        epoll.register(self.request.fileno(), select.EPOLLIN)
        epoll.register(self._to_srv_soc.fileno(), select.EPOLLIN)

        try:
            while True:
                envents = epoll.poll(3)
                for fileno, event in envents:
                    if fileno == self._to_srv_soc.fileno():
                        if self.request.send(cipher.cryptor.decrypt(self._to_srv_soc.recv(4096))) <=0:
                            break
                    elif fileno == self.request.fileno():
                        if self._to_srv_soc.send(cipher.cryptor.encrypt(self.request.recv(4096))) <=0:
                            break
        except socket.error as err:
            if err.errno == errno.ECONNRESET:
                logger.debug("Connection Reset:\n{}, {}".format(self.request, self._to_srv_soc))
            else:
                raise
        finally:
            epoll.unregister(self.request.fileno())
            epoll.unregister(self._to_srv_soc.fileno())
            epoll.close()
            self.request.close()
            self._to_srv_soc.close()

    def _forward_udp(self):
        pass
    
    def _handle_tcp(self):
        logger.info("TCP connection received")


        self._to_srv_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._to_srv_soc.connect(self.server.proxy_addr)
        except socket.error as e:
            logger.error("Can't connect to Proxy Server[{}:{}] [{}]".format(*self.server.proxy_addr, e))
            sys.exit(1)
            
        # Hello handshake [Local -- Server]
        hello_srv_send_raw = self.server.cryptor.encrypt(magic_bytes)
        self._to_srv_soc.send(hello_srv_send_raw)
            # Verify process
        hello_srv_recv_raw = self._to_srv_soc.recv(4096)
        
            # ACCEPT
        if len(hello_srv_recv_raw) == 1 + len(hello_srv_send_raw)  and hello_srv_recv_raw[0] == 0:
            logger.info("Connect to Proxy server[{}:{}] successful".format(*self.server.proxy_addr))
        else:
            logger.warn("Verify Proxy Server failed")
            # Refuse client's request
            handler.negotiation_srv(None, self.request, codes.METHOD["REFUSE"])
            return

        # Negotiation [Local -- Client]
        nego_cli_recv_raw = self.request.recv(4096)
        is_verified_ok = handler.negotiation_srv(nego_cli_recv_raw, self.request)
        if not is_verified_ok:
            self._to_srv_soc.close()
            return # end request
        
        # Connection [Client -- Local -- Server]
            # Forward client's packet to Server
        connect_cli_recv_raw = self.request.recv(4096)
        self._to_srv_soc.send(self.server.cryptor.encrypt(connect_cli_recv_raw))
            # Forward Server to client
        connect_srv_recv_raw = self.server.cryptor.decrypt(self._to_srv_soc.recv(4096))
        self.request.send(connect_srv_recv_raw)
            # Check status
        connect_cli_send = connect.cli_decode(connect_srv_recv_raw)
        if not connect_cli_send[1] == codes.STATUS["SUCCESS"]:
            # Remote fail
            logger.debug("Connecting to {}:{} fail".format(*connect_cli_send[3]))
            self._to_srv_soc.close()
            return
        else:
            # TCP
            if self._to_srv_soc.type == socket.SOCK_STREAM or 2049:
                logger.info("Connected to {}:{}".format(*self._to_srv_soc.getpeername()))
                self._forward_tcp()
            # UDP: 2050
            else:
                self._forward_udp()
        
        # Close all fd
        self._to_srv_soc.close()

    def _handle_udp(self):
        pass
    
    def handle(self):
        logger.debug("Thread running {}".format(threading.current_thread().name))
        if self.server.socket_type == socket.SOCK_STREAM:
            self._isTcp = True
            self._handle_tcp()
        else:
            # UDP
            self._isTcp = False
            self._handle_udp()

class TCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

class SocksServer(object):

    def __init__(self, ip, port, handler, password, server_addr, server_port):
        self._server = TCPServer((ip, port), handler)
        # Init cipher
        self._server.cryptor = cipher.RC4(password)
        # Proxy server addr
        self._server.proxy_addr = (server_addr, server_port)
    def start(self):
        self._thread = threading.Thread(target=self._server.serve_forever())
        self._thread.start()
        self._thread.daemon = True
        self._thread.join()

    def shutdown(self):
        self._server.shutdown()
    
    def test_start(self):
        self._server.serve_forever()

if __name__ == "__main__":
    server = SocksServer("127.0.0.1", 6233, myHandler, "12314", "127.0.0.1", 8888)
    server.start()