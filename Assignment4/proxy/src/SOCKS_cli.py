
import socket
import logging
import sys

if __package__:
    from .resolver import codes, nego, connect, udp
    from . import handler
else:
    from resolver import codes, nego, connect, udp
    import handler


logging.basicConfig(format='%(asctime)s %(levelname)-8s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# methods -> (, ,)
class Client(object):

    support_methods = (codes.METHOD["NONEED"], codes.METHOD["USERPASS"])

    def __init__(self, proxy_addr, proxy_port):
        self._is_connected = False

        self._cli_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._cli_soc.connect((proxy_addr, proxy_port))
        except socket.gaierror as err:
            logger.error("Can't connect to proxy server: {}".format(err))
            sys.exit(1)

    def _negotiation(self, methods):
        try:
            # Send nego packet
            self._cli_soc.sendall(nego.cli_encode(methods))
            # Get from server and handle it
            return handler.negotiation_cli(self._cli_soc.recv(2048), self._cli_soc)
        except socket.error as e:
            raise

    def _connection(self, addr_type, remote_addr, remote_port, request_type=codes.REQUEST["CONNECT"]):
        try:
            # Send connection packet
            self._cli_soc.sendall(connect.cli_encode(request_type, addr_type, remote_addr, remote_port))
            # Recv from server and handle
            return handler.connection_cli(self._cli_soc.recv(2048))
        except socket.error as err:
            raise

    def connect(self, addr_type, remote_addr, remote_port, request_type=codes.REQUEST["CONNECT"]):
        # Communication with server
        try:
            if not self._negotiation((codes.METHOD["USERPASS"],)):
                sys.exit(1)
            if not self._connection(addr_type, remote_addr, remote_port, request_type):
                sys.exit(1)
        except:
            raise

        self._is_connected = True
        self._remote_addr = (remote_addr, remote_port)
        logger.info("Connect to {}:{} Successfully".format(remote_addr, remote_port))

    def send_recv(self, raw_data):
        if not self._is_connected:
            logger.error("Not already connected to remoter server. Send failed")
            return
        else:
            logger.info("Connected to {}:{}. Start sending".format(*self._remote_addr))
            self._cli_soc.sendall(raw_data)
            print(self._cli_soc.recv(5096))



if __name__ == "__main__":
    # Connect to
    test = Client("127.0.0.1", 6233)
    test.connect(codes.ADDRESS["DOMAIN"],"4399.com", 80, codes.REQUEST["CONNECT"])
    test.send_recv(b"GET / HTTP/1.0\r\n\r\n")
