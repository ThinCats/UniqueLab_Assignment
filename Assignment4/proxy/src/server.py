import socketserver
import threading
import logging
import socket
import select
import errno

logging.basicConfig(format='%(asctime)s %(levelname)-8s: %(message)s')
if __package__:
    from .resolver import codes, connect, nego, udp, support
    from . import handler
else:
    from resolver import codes, connect, nego, udp, support
    import handler

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s- %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
class myHandler(socketserver.BaseRequestHandler):
    
    # This is for forwarding packet
    def _forward_tcp(self):
        logger.info("Start forwarding from {}:{} to {}:{}".format(*self.request.getpeername(), *self._remote_soc.getpeername()))
        # Use epoll to fowarding packet
        epoll = select.epoll()
        epoll.register(self.request.fileno(), select.EPOLLIN)
        epoll.register(self._remote_soc.fileno(), select.EPOLLIN)

        try:
            while True:
                envents = epoll.poll(3)
                for fileno, envent in envents:
                    if fileno == self._remote_soc.fileno():
                        if self.request.send(self._remote_soc.recv(4096)) <=0:
                            break
                    elif fileno == self.request.fileno():
                        if self._remote_soc.send(self.request.recv(4096)) <=0:
                            break
        except socket.error as err:
            if err.errno == errno.ECONNRESET:
                logger.debug("Connection Reset:\n{}, {}".format(self.request, self._remote_soc))
            else:
                raise
        finally:
            epoll.unregister(self.request.fileno())
            epoll.unregister(self._remote_soc.fileno())
            epoll.close()
            self.request.close()
            self._remote_soc.close()

    def _forward_udp(self):
        pass
    
    def _handle_tcp(self):
        logger.info("TCP connection received")

        # negotiation
        nego_recv_raw = self.request.recv(8192)
            # debug

        # print("Nego recv raw data: {}".format(nego_recv_raw))
        is_verified_ok = handler.negotiation_srv(nego_recv_raw, self.request)
        # It means verify failed
        if not is_verified_ok:
            return
        
        # Connection
        connect_recv_raw = self.request.recv(8192)
        self._remote_soc, connect_rep_raw = handler.connection_srv(connect_recv_raw)
        self.request.sendall(connect_rep_raw)
        
            # check status
        if self._remote_soc is None:
            return
        else:
            # TCP
            print(self._remote_soc.type)
            if self._remote_soc.type == socket.SOCK_STREAM or 2049:
                logger.info("Connected to {}:{}".format(*self._remote_soc.getpeername()))
                self._remote_tcp = True
                self._forward_tcp()
            # UDP: 2050
            else:
                self._remote_tcp = False
                self._forward_udp()
        
        # Close all fd
        self._remote_soc.close()
        self.request.close()

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

        


class UDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    allow_reuse_address = True

class TCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

class SocksServer(object):

    def __init__(self, isTcp, ip, port, handler):
        if isTcp:
            self._server = TCPServer((ip, port), handler)
        else:
            self._server = UDPServer((ip, port), handler)
    
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
    server = SocksServer(True, "127.0.0.1", 6233, myHandler)
    server.start()


