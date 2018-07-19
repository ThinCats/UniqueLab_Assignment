if __package__:
    from .Server import *
else:
    from Server import *


# For handshake
magic_byts = b"hello"
socket.setdefaulttimeout(10)
class SrvHandler(ProxyHandler):

    def _close(self):
        self.request.close()
        try:
            self._to_remote_soc.close()
        except (AttributeError, TypeError):
            pass # No attribute, ignore

    # This is for forwarding packet
    def _handle_tcp(self):

        logger.info("TCP connection received from {}:{}".format(*self.request.getpeername()))

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
            raise ThreadExit
        
        # Recv connection 
        connect_loc_recv_raw = self._recv(self.request, 8192, True)
        if not connect_loc_recv_raw:
            # Connection end
            logger.warn("Connection Reset by peers at connection progress")
            raise ThreadExit
        
        self._to_remote_soc, connect_loc_send_raw = handler.connection_srv(connect_loc_recv_raw)
        # self.request.sendall(self.server.cryptor.encrypt(connect_loc_send_raw))
        self._send(self.request, connect_loc_send_raw, True)
        
            # check status
        if self._to_remote_soc is None:
            raise ThreadExit
        else:
            # TCP
            if self._to_remote_soc.type == socket.SOCK_STREAM or 2049:
                logger.info("Connected to {}:{}".format(*self._to_remote_soc.getpeername()))
                self._forward_tcp(self._to_remote_soc, self.request, False, True)
            # UDP: 2050
            else:
                self._forward_udp()
        


class TCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

class SocksServer(object):
    def __init__(self, ip, port, password, ipv6, handler=SrvHandler):
        if ipv6:
            TCPServer.address_family = socket.AF_INET6
        self._server = TCPServer((ip, port), handler)
        # Init the cipher
        self._server.cryptor = cipher.RC4(password)

    def shutdown(self):
        self._server.shutdown()
    
    def start(self):
    
        self._server.serve_forever()


if __name__ == "__main__":
    server = SocksServer("127.0.0.1", 9899, "21431", False)
    server.start()


