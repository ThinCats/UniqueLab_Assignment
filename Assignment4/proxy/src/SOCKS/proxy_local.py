if __package__:
    from .Server import *
else:
    from Server import *


# For handshake
magic_bytes = b"hello"
socket.setdefaulttimeout(5)
logger = logging
class EpollEnd(Exception):
    pass

class LocalHandler(ProxyHandler):
    def _close(self):
        # For close socket
        self.request.close()
        try:
            self._to_srv_soc.close()
        except AttributeError:
            pass
    
    def _handle_tcp(self):
        logger.info("TCP connection received from {}:{}".format(*self.request.getpeername()))
        
        # Negotiation [Local -- Client]
        # nego_cli_recv_raw = handler.heartBeat_tcp(self.request.recv(4096), self.request)
        nego_cli_recv_raw = self._recv(self.request, 4096, False)

        is_verified_ok = handler.negotiation_srv(nego_cli_recv_raw, self.request)
        if not is_verified_ok:
            raise ThreadExit  # end request
        
        # Connect to Proxy Server
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
            raise ThreadExit

       
        # Connection [Client -- Local -- Server]
            # Forward client's packet to Server
        # connect_cli_recv_raw = handler.heartBeat_tcp(self.request.recv(4096), self.request)
        connect_cli_recv_raw = self._recv(self.request, 4096, False)

        # PAC MODE
        if self.server.pac_mode:
            connect_cli_recv = connect.srv_decode(connect_cli_recv_raw)
            if (connect_cli_recv[2]==codes.ADDRESS["DOMAIN"]):
                if handler.pac_filter(connect_cli_recv[3][0], self.server.pac_wordlist):
                    self._to_srv_soc.close()
                    logger.info("PAC mode: {}:{}".format(*connect_cli_recv[3]))
                    self._to_srv_soc, connect_send_raw = handler.connection_srv(connect_cli_recv_raw)
                    if not self._to_srv_soc:
                        raise ThreadExit
                    self._send(self.request, connect_send_raw, False)
                    if self._to_srv_soc.type == socket.SOCK_STREAM or 2049:
                        logger.info("Connected to {}:{}".format(*self._to_srv_soc.getpeername()))
                        self._forward_tcp(self._to_srv_soc, self.request, False, False)
                    else:
                        self._forward_udp()
                    raise ThreadExit
        # Exited PAC Mode
    
        self._send(self._to_srv_soc, connect_cli_recv_raw, True) 
        
            # Forward Server to client
        connect_srv_recv_raw = self._recv(self._to_srv_soc, 4096, True)

        # self.request.send(connect_srv_recv_raw)
        self._send(self.request, connect_srv_recv_raw, False)
            # Check status
        connect_cli_send = connect.cli_decode(connect_srv_recv_raw)
        logger.debug("{}".format(connect_cli_send))
        if not connect_cli_send[1] == codes.STATUS["SUCCEED"]:
            # Remote fail   
            logger.debug("Connecting to {}:{} fail".format(*connect_cli_send[3]))
            raise ThreadExit
        else:
            # TCP
            if self._to_srv_soc.type == socket.SOCK_STREAM or 2049:
                logger.info("Connected to {}:{}".format(*self._to_srv_soc.getpeername()))
                self._forward_tcp(self.request, self._to_srv_soc, False, True)
            # UDP: 2050True
            else:
                self._forward_udp()

class TCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

class SocksServer(object):

    def __init__(self, ip, port, password, server_addr, server_port, ipv6, pac_file=None, handler=LocalHandler):
        if ipv6:
            TCPServer.address_family = socket.AF_INET6
        
        self._server = TCPServer((ip, port), handler)
        # Init cipher
        self._server.cryptor = cipher.RC4(password)
        # Proxy server addr
        self._server.proxy_addr = (server_addr, server_port)
        # PAC File
        self._server.pac_wordlist = set()
        try:
            with open(pac_file, "r") as f:
                for line in f.readlines():
                    self._server.pac_wordlist.add(line.rstrip())
                self._server.pac_mode = True
        except Exception:
            logger.warn("PAC File open failed. Ignore")
            self._server.pac_mode = False

    def shutdown(self):
        self._server.shutdown()
    
    def start(self):
        self._server.serve_forever()

if __name__ == "__main__":
    server = SocksServer("127.0.0.1", 6233, "21431", "127.0.0.1", 9899, False)
    server.start()