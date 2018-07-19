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
    from resolver import codes, connect
    import handler
    from cryptor import cipher

logger = logging

# EmptyPacket Exception when socket recv an empty packet
class EmptyPacket(Exception):
    pass
# Thread kill itself
class ThreadExit(Exception):
    pass
# EPOLL Exception for exiting from EPOLL
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
            # logger.debug("Send: {}".format(data_raw))
            return socket_to.send(data_raw)
        
        except socket.error as err:
            if err.errno == errno.ECONNRESET:
                logger.debug("Connection Reset:\n{}".format(socket_to ))
            else:
                logger.debug("{}\n{}".format(err, socket_to))
            raise ThreadExit

    def _recv(self, socket_from, buf_size, decr=False):
        """
        The same as _send
        """
        try:
            data_raw = socket_from.recv(buf_size)
            if not data_raw:
                raise EmptyPacket("Recv zero packet")
            
            if decr:
                data_raw = self.server.cryptor.decrypt(data_raw)
            # logger.debug("Recv: {}".format(data_raw))
            return data_raw
        except EmptyPacket:
            raise
        except socket.error as err:
            if err.errno == errno.ECONNRESET:
                logger.debug("Connection Reset:\n{}".format(socket_from))
            else:
                logger.debug("{}\n{}".format(err, socket_from))
            raise ThreadExit

    # This is for forwarding packet
    def _forward_tcp(self, socket_a, socket_b, a_encr=False, b_encr=True):

        """
        Forward from a to b
        a_encr: data from socket a encr
        """
        try:
            logger.info("Forwarding from {}:{} to {}:{}".format(*socket_a.getpeername(), *socket_b.getpeername()))
        except socket.error as e:
            logger.warn(e)
            raise ThreadExit
        # Use epoll to fowarding packet
        epoll = select.epoll()
        epoll.register(socket_a.fileno(), select.EPOLLIN | select.EPOLLPRI)
        epoll.register(socket_b.fileno(), select.EPOLLIN | select.EPOLLPRI)
        
        try:
            # print("a:{}, b:{}".format(socket_a.fileno(), socket_b.fileno()))
            while True:
                events = epoll.poll(20)
                # logger.debug("Events: {}".format(events))
                if not events:
                    logger.debug("EPOLL timeout:{}, {}.Exit".format(socket_a.getpeername(), socket_b.getpeername()))
                    raise EPOLLEnd
                for fileno, event in events:
                    # Data recv
                    if event & select.EPOLLIN:
                        if fileno == socket_b.fileno():
                            self._send(socket_a, self._recv(socket_b, 4096, b_encr), a_encr)
                            # if self._send(socket_a, data_raw) <=0: raise EPOLLEnd
                        if fileno == socket_a.fileno():
                            self._send(socket_b, self._recv(socket_a, 4096, a_encr), b_encr)
                            # data_raw = self._recv(socket_a, 4096)
                            # if self._send(socket_b, data_raw)<=0: raise EPOLLEnd
                    elif event & select.EPOLLHUP:
                        raise EPOLLEnd
                    elif event & select.EPOLLERR:
                        logger.warn("EPOLL ERROR {}")
                        raise EPOLLEnd

        except (EPOLLEnd, EmptyPacket) as e:
            # For jumping out of the loop
            logger.debug("Fowarded {}".format(e))
        except ThreadExit:
            pass
        
        finally:
            if not socket_a.fileno() == -1:
                epoll.unregister(socket_a.fileno())
            if not socket_b.fileno() == -1:
                epoll.unregister(socket_b.fileno())
            epoll.close()
 
    def _forward_udp(self):
        pass

    def _handle_tcp(self):
        pass 

    def _handle_udp(self):
        pass
    
    def handle(self):
        logger.debug("Thread running")
        self._cryptor = self.server.cryptor

        try:
            if self.server.socket_type == socket.SOCK_STREAM:
                self._handle_tcp()
            else:
                # UDP
                self._handle_udp()
        except (EmptyPacket, ThreadExit):
            # It means socket exit
            pass
        except Exception as err:
            raise
        finally:
            self._close()

        logger.debug("Thread ending")