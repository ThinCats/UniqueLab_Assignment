import socketserver
import threading
import logging
import socket
import select
import errno

# socket.setdefaulttimeout(5)
if __package__:
    from . import handler
    from . import Server
    from .cryptor import cipher

else:
    import handler
    import Server
    from cryptor import cipher

logger = logging.getLogger(__name__)

# For handshake
magic_byts = b"hello"

class myHandler(socketserver.BaseRequestHandler):
    # This is for forwarding packet
    def _forward_tcp(self):
        logger.info("Forwarding from {}:{} to {}:{}".format(*self.request.getpeername(), *self._to_remote_soc.getpeername()))
        # Use epoll to fowarding packet
        epoll = select.epoll()
        epoll.register(self.request.fileno(), select.EPOLLIN)
        epoll.register(self._to_remote_soc.fileno(), select.EPOLLIN)

        try:
            while True:
                envents = epoll.poll(3)
                for fileno, event in envents:
                    if fileno == self._to_remote_soc.fileno():
                        if self.request.send(self.server.cryptor.encrypt(self._to_remote_soc.recv(4096))) <=0:
                            break
                    elif fileno == self.request.fileno():
                        if self._to_remote_soc.send(self.server.cryptor.decrypt(self.request.recv(4096))) <=0:
                            break
        except socket.error as err:
            if err.errno == errno.ECONNRESET:
                logger.debug("Connection Reset:\n{}, {}".format(self.request, self._to_remote_soc))
            else:
                raise
        finally:
            epoll.unregister(self.request.fileno())
            epoll.unregister(self._to_remote_soc.fileno())
            epoll.close()
            self.request.close()
            self._to_remote_soc.close()

    def _forward_udp(self):
        pass
    
    def _handle_tcp(self):

        logger.info("TCP connection received")

        # Hello handshake process
        is_verified_ok = True
        hello_recv_raw = self.request.recv(4096)
            # Verify packet
        if self.server.cryptor.decrypt(hello_recv_raw) == magic_byts:
            hello_send_raw = b"\x00"
        else:
            hello_send_raw = b"\x01"
            is_verified_ok = False
            logger.warn("Handshake Verify failed")

        self.request.send(hello_send_raw + hello_recv_raw)
        # End connection
        if not is_verified_ok:
            return
        
        # Recv connection 
        connect_loc_recv_raw = self.server.cryptor.decrypt(self.request.recv(8192))
        if not connect_loc_recv_raw:
            # Connection end
            logger.warn("Connection Reset by peers at connection progress")
            return
        
        self._to_remote_soc, connect_loc_send_raw = handler.connection_srv(connect_loc_recv_raw)
        self.request.sendall(self.server.cryptor.encrypt(connect_loc_send_raw))
        
            # check status
        if self._to_remote_soc is None:
            return
        else:
            # TCP
            if self._to_remote_soc.type == socket.SOCK_STREAM or 2049:
                logger.info("Connected to {}:{}".format(*self._to_remote_soc.getpeername()))
                self._forward_tcp()
            # UDP: 2050
            else:
                self._forward_udp()
        
        # Close all fd
        self._to_remote_soc.close()

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
    def __init__(self, ip, port, handler, password):
        self._server = TCPServer((ip, port), handler)
        # Init the cipher
        self._server.cryptor = cipher.RC4(password)
    
    def start(self):
        self._thread = threading.Thread(target=self._server.serve_forever())
        self._thread.start()
        self._thread.daemon = True
        self._thread.join()

    def shutdown(self):
        self._server.shutdown()

if __name__ == "__main__":
    server = SocksServer("127.0.0.1", 9899, myHandler, "2333")
    server.start()


