import threading
import time
import select

if __package__:
    from .Server import *
    from .resolver import forward
else:
    from Server import *
    from resolver import forward

class LocalHandler(Handler):

    def __init__(self, request, local_info):
        self._local_info = local_info
        self.request = request

    def _handle_tcp(self):
        # Connect to local client, ready for sending packet
        self._to_cli_soc= socket.socket(self._local_info.address_family, self._local_info.socket_type)
        self._to_cli_soc.connect(("localhost", self._local_info.wanted_local_port))

        # Forwarding
        if self._local_info.socket_type == socket.SOCK_STREAM:
            self._forward_tcp(self._to_cli_soc, self.request, False, True, self._local_info.cryptor)
        else:
            pass
        
    def handle(self):
        logger.debug("Thread Start")
        try:
            self._handle_tcp()
        except error.ThreadExit:
            logger.debug("Thread Exit")
        finally:
            self._close(self.request, self._to_cli_soc)

class LocalServer(object):
    def __init__(self, ip, port, password, local_info, handler=LocalHandler):

        TCPServer.address_family = local_info.address_family
        self._server = TCPServer((ip, port), handler)
        self._password = password
        
        self._cryptor_old = cipher.RC4(password) # Not change
        self._cryptor = self._cryptor_old
        self._local_info = local_info

    def _connect_to_server(self):
        try:
            self._to_srv_soc = socket.socket(self._local_info.address_family, self._local_info.socket_type)
            self._to_srv_soc.connect((self._local_info.srv_ip, self._local_info.srv_port))
        except socket.error as e:
            logger.error("Connect to Server failed {}".format(e))

        # handshake

        self._cryptor = handler.handshake_cli(handshake.cli_encode(), self._to_srv_soc, self._cryptor)
        
        # Connect
        connect_send_raw = connect.cli_encode(codes.VERSION["V1"], self._local_info.request, self._local_info.wanted_srv_port)
            # Send request <version, request, port>
        send_encr(self._to_srv_soc, connect_send_raw, True, self._cryptor)
            # Recv response <version, status, port>
        connect_recv_raw = recv_encr(self._to_srv_soc, 4096, True, self._cryptor)
            # Check status
        is_ok, status = handler.connect_cli(connect_recv_raw)
        if not is_ok:
            logger.error("Connect to SRV Failed. {}".format(status))
            raise error.ThreadExit
        else:
            return True

    def _connect_to_port(self, port):
        try:
            request = socket.socket(self._local_info.address_family, self._local_info.socket_type)
            print(self._local_info.srv_ip, port)
            request.connect((self._local_info.srv_ip, port))
        except socket.error as e:
            logger.error("Recv Request form server failed {}".format(e))

        local_handler = LocalHandler(request, self._local_info)
        local_handler.handle()
        
    def _get_request(self):
        while True:
            events = self._epoll.poll()
            for fd, event in events:
                print(events)
                try:
                    if event & select.EPOLLIN:
                        if fd == self._to_srv_soc.fileno():
                            data_raw = recv_encr(self._to_srv_soc, 2, True, self._cryptor)
                            thread = threading.Thread(target=self._connect_to_port(forward.decode_cli(data_raw)))
                            thread.start()
                    if event & select.EPOLLHUP:
                        raise error.ConnectionLost
                except (error.ConnectionLost, error.EmptyData, socket.error):
                    logger.warn("Remote Server disconnected")
                    self._supervisor()
                    logger.info("Reconnect to Server")

    def _heart_beat(self, soc):
        while True:
            try:
                soc.send(b"233")
                logger.debug("Sending")
                time.sleep(5)
            except socket.error as e:
                logger.debug("Hearbeat exit {}".format(e)) 
                break
    
    def shutdown(self):
        self._server.shutdown()

    def _supervisor(self):
        times = 3
        try:
            self._to_srv_soc.send(b"233")
            self._to_srv_soc.getpeername()
        except socket.error as e:
            while True:
                logger.warn("Server disconnected. Retry [{}s] {}".format(times, e))
                try:
                    self._cryptor = self._cryptor_old
                    self._connect_to_server()
                    self._local_info.cryptor = self._cryptor
                    self._epoll.register(self._to_srv_soc.fileno(), select.EPOLLIN)
                    # self._heart_beat_thread = threading.Thread(target=self._heart_beat(self._to_srv_soc))
                    # self._heart_beat_thread.start()
                    break
                except (error.ThreadExit, socket.error):
                    times += 1
                    times = (0 if (times > 15) else times)
                except error.HandshakeFailed:
                    times += 1
                    if times > 5:
                        raise error.ServerExit
                finally:
                    time.sleep(times)
            

    def start(self):
        try:
            self._connect_to_server()
           # Epoll init
            self._epoll = select.epoll()
            self._epoll.register(self._to_srv_soc.fileno(), select.EPOLLIN)
            # Update Its cryptor
            self._local_info.cryptor = self._cryptor 
            # Heartbeat
            # self._heart_beat_thread = threading.Thread(target=self._heart_beat, args=(self._to_srv_soc, ))
            # self._heart_beat_thread.daemon = True
            # self._heart_beat_thread.start()
            # Main Thread
            logger.info("Connect to Server")
            self._get_request()
        except error.ThreadExit:
            logger.debug("Thread Exit")

if __name__ == "__main__":
    local_info = Info_local(8888, 1081, codes.REQUEST["FORWARD"], socket.AF_INET, socket.SOCK_STREAM, "47.106.22.242", 1080)
    server = LocalServer("127.0.0.1", 23333, "2333", local_info)
    server.start()


