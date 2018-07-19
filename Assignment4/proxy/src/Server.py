import socketserver
import threading
import logging
import socket
import select
import errno
import sys

socket.setdefaulttimeout(5)
if __package__:
    from .resolver import codes, connect
    from . import handler
    from .cryptor import cipher
else:
    from resolver import codes, connect
    import handler
    from cryptor import cipher

logger = logging

# EPOLL Exception
class EPOLLEnd(Exception):
    pass

class ProxyHandler(socketserver.BaseRequestHandler):
    """
    This class is a parent class for proxy_srv and proxy_local
    It defines tcp_forward and other public methods
    """
    def _close(self):
        pass
    
    def _send(self, socket_to, data_raw, encr=False):
        """
        This is for different socket_send use
        For non-encryption and encryption
        """
        try:
            if encr:
                data_raw = self.server.cryptor.encrypt(data_raw)
            return socket_to.send(data_raw)
        except socket.timeout:
            logger.error("Timeout: {}".format(socket_to))
            socket_to.close()
            self._close()
            raise
    def _recv(self, socket_from, buf_size, decr=False):
        """
        The same as _send
        """
        try:
            data_raw = socket_from.recv(buf_size)
            # if not data_raw:
                # Empty packet:
                # raise ValueError("Empty packet")
            if decr:
                data_raw = self.server.cryptor.decrypt(data_raw)
            return data_raw
        except socket.timeout:
            logger.error("[{}]Timeout: {}".format(threading.current_thread().name, socket_from))
            socket_from.close()
            self._close()
            raise
        except socket.error as e:
            logger.error(e)
            socket_from.close()
            raise

    # This is for forwarding packet
    def _forward_tcp(self, socket_a, socket_b, a_encr=False, b_encr=True):
        """
        Forward from a to b
        a_encr: data from socket a encr
        logger.info("Start forwarding from {}:{} to {}:{}".format(*socket_a.getpeername(), *socket_b.getpeername()))
        """
        # Use epoll to fowarding packet
        epoll = select.epoll()
        epoll.register(socket_a.fileno(), select.EPOLLIN)
        epoll.register(socket_b.fileno(), select.EPOLLIN)
        
        logger.debug("EPOLL")
        try:
            while True:
                envents = epoll.poll(3)
                logger.debug(envents)
                for fileno, event in envents:
                    if fileno == socket_b.fileno():
                        if self._send(socket_a, self._recv(socket_b, 4096, b_encr), a_encr) <=0:
                            raise EPOLLEnd
                    elif fileno == socket_a.fileno():
                        if self._send(socket_b, self._recv(socket_a, 4096, a_encr), b_encr) <=0:
                            raise EPOLLEnd
        except socket.error as err:
            if err.errno == errno.ECONNRESET:
                logger.debug("Connection Reset:\n{}, {}".format(socket_a, socket_b))
            else:
                raise
        except EPOLLEnd:
            # Loop end
            logger.info("Fowarding end")
        finally:
            if socket_a.fileno() != -1:
                epoll.unregister(socket_a.fileno())
            if socket_b.fileno() != -1:
                epoll.unregister(socket_b.fileno())
            epoll.close()
            socket_a.close()
            socket_b.close()
 
    def _forward_udp(self):
        pass

    def handle_tcp(self):
        pass 

    def handle_udp(self):
        pass
    
    def handle(self):
        logger.debug("Thread running {}".format(threading.current_thread().name))
        if self.server.socket_type == socket.SOCK_STREAM:
            self.handle_tcp()
        else:
            # UDP
            self.handle_udp()
        logger.debug("Thread ending")