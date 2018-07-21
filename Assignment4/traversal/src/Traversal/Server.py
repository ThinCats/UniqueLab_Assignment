
import socket
import socketserver
import threading
import select
import logging
import traceback

if not __package__:
    from cryptor import cipher
    from resolver import codes, connect, handshake, forward
    import handler, error
    from basic import *
else:
    from .cryptor import cipher
    from .resolver import codes, connect,  handshake, forward
    from . import handler, error
    from .basic import *

logger = logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(threadName)s %(levelname)-8s: %(message)s')

class Info_local(object):
    """
    This is for passing basic info to handler
    """
    def __init__(self, wanted_srv_port, wanted_local_port, request, address_family, socket_type, srv_ip, srv_port):
        self.wanted_srv_port = wanted_srv_port
        self.wanted_local_port = wanted_local_port
        self.address_family = address_family
        self.socket_type = socket_type
        self.srv_ip = srv_ip
        self.srv_port = srv_port
        self.request = request

class Info_server(object):
    def __init__(self, address_family, socket_type):
        self.address_family = address_family
        self.socket_type = socket_type

class Handler(socketserver.BaseRequestHandler):

    def _close(self, *socs):
        for ch in socs:
            try:
                ch.close()
            except (IOError, AttributeError):
                pass
    def _forward_tcp(self, soc_from, soc_to, encr_from, encr_to, cryptor):
        
        try:
            logger.info("Frowarding {}:{} To {}:{}".format(*soc_from.getpeername(), *soc_to.getpeername()))
        except socket.error as e:
            logger.warn(e)
            raise error.ThreadExit

        epoll = select.epoll()
        epoll.register(soc_to.fileno(), select.EPOLLIN)
        epoll.register(soc_from.fileno(), select.EPOLLIN)

        try:
            while True:
                events = epoll.poll(20)
                if not events:
                    logger.warn("EPOLL Timeout. Exit")
                    raise error.ThreadExit

                for fd, event in events:
                    if event & select.EPOLLIN:
                        if fd == soc_to.fileno():
                            send_encr(soc_from, recv_encr(soc_to, 4096, encr_to, cryptor), encr_from, cryptor)
                        elif fd == soc_from.fileno():
                            send_encr(soc_to, recv_encr(soc_from, 4096, encr_from, cryptor), encr_to, cryptor)
                        
                    elif event & select.EPOLLHUP:
                        raise error.EPOLLEnd
                    elif event & select.EPOLLERR:
                        logger.error("EPOLL ERR") 
                        raise error.EPOLLEnd
        except error.EPOLLEnd:
            logger.info("Forwarding End")
        finally:
            if soc_to.fileno() != -1:
                epoll.unregister(soc_to.fileno())
            if soc_from.fileno() != -1:
                epoll.unregister(soc_from.fileno())
            self._close(soc_to, soc_from)

    def _handle_tcp(self):
        pass
    def _handle_udp(self):
        pass
    
    def handle(self):
        # First use cryptor by init password
        # self._cryptor = cipher.RC4(self.server.crypt_pass)
        try:
            if self.server.socket_type == socket.SOCK_STREAM:
                logger.debug("TCP Connection Accept")
                self._handle_tcp() 
            else:
                self._handle_udp()
        except error.ThreadExit:
            logger.debug("Thread Exit")

        finally:
            self._close(self.request)


class TCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True