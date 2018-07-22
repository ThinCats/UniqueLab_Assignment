import threading
import time
if __package__:
    from .Server import *
    from .resolver import forward
else:
    from Server import *
    from resolver import forward

class ServerHandler(Handler):

    def _handle_tcp(self):
        remotecli_recv_raw = recv_encr(self.request, 4096)
        self._traverse_soc = socket.socket(self.server.server_info.address_family, socket.SOCK_STREAM)
        # Random bind a port
        self._traverse_soc.bind(("0.0.0.0", 0))
        binded_port = self._traverse_soc.getsockname()[1]
        self._traverse_soc.listen(1)

        # Send the port to localTra<function recv_encr at 0x7fecd61a06a8>
        self._local_traver = None
        try:
            send_encr(self.server.to_local_soc, forward.encode_srv(binded_port), True, self.cryptor)
            self._check_valid(self.server.to_local_soc)
            self._local_traver, addr = self._traverse_soc.accept()
            self._traverse_soc.close()
            # TODO: Identification Check
                # Send previous data to it
            send_encr(self._local_traver, remotecli_recv_raw, True, self.cryptor)
                # Start forwarding
            self._forward_tcp(self._local_traver, self.request, True, False, self.cryptor)
        except socket.error as e:
            logger.error("Disconnected from local proxy. Close {}".format(e))
            raise error.ServerExit
        finally:
            self._close(self._traverse_soc)

    def _check_valid(self, soc):
        try:
            soc.getpeername()
        except socket.error as e:
            logger.error("Disconnected {}".format(e))
            raise

    def handle(self):
        logger.debug("Start traversing")
        self._server_info = self.server.server_info
        self.cryptor = self.server.cryptor

        try:
            self._handle_tcp()
        except error.ServerExit:
            self.server.shutdown()
            self.server.server_close()
        except error.EmptyData:
            pass
        finally:
            self._close(self._local_traver, self.request)
        logger.debug("End Traversing thread")
        
class NegoHandler(socketserver.BaseRequestHandler):
    """
    This handler is for recving localTraversal request
    server_info transfered by self.server
    """

    def _handle_tcp(self):
        # Update cryptor
        is_verified, self._cryptor = handler.handshake_srv(self.request, self._cryptor)
        if not is_verified:
            logger.error("Handshake with local failed")
            raise error.ThreadExit

        # binded_server is for accepting remoteCli connection and handle
        self._binded_server = handler.connect_srv(self.request, self._server_info, self._cryptor, ServerHandler)
        if not self._binded_server:
            logger.error("Failed in Connect process")
            raise error.ThreadExit
        # Give info to the server
        self._binded_server.to_local_soc = self.request
        # Give it server_info
        self._binded_server.server_info = self._server_info
        self._binded_server.cryptor = self._cryptor

        # Heatbeat detact
        # self._heart_beat_thread = threading.Thread(target=self._heart_beat(self.request))
        # self._heart_beat_thread.daemon = True
        # self._heart_beat_thread.start()
        # Server loop
        self._thread = threading.Thread(target=self._binded_server.serve_forever)
        self._thread.start()
        self._thread.join()
    
    def _heart_beat(self, soc):
        epoll = select.epoll()
        epoll.register(soc.fileno(), select.EPOLLIN)
        while True:
            events = epoll.poll(6)
            print (events)
            try:
                if not events:
                    logger.warn("Not recv clients heartbeat packet")
                    raise error.ConnectionLost
                for fd, event in events:
                    if event & select.EPOLLHUP:
                        raise error.ConnectionLost
                    data = soc.recv(4096)
                    # TODO: There is a bug
                    # Whenever I operate on bytes
                    # Server will send an empty packet
                    
                    # if (soc.recv(4096)) <=0:
                        # raise error.ConnectionLost
            except error.ConnectionLost:
                self._binded_server.shutdown()
                self._binded_server.server_close()

    def handle(self):
        self._cryptor = self.server.server_info.cryptor
        self._server_info = self.server.server_info

        # thread.start()
        logger.debug("Thread Start")
        try:
            self._handle_tcp()
        except error.ThreadExit:
            pass
        finally:
            self.request.close()
            try:
                self._binded_server.shutdown()
                self._binded_server.server_close()
            except AttributeError as e:
                logger.error("THIS FIXED ATTRIBUTEERRO {}".format(e))
            except Exception as e:
                traceback.print_exc()
        # thread.join()
        logger.debug("Thread Exit")


class TraServer(object):
    def __init__(self, ip, port, password, server_info, handler=NegoHandler):

        TCPServer.address_family = server_info.address_family
        self._server = TCPServer((ip, port), handler)
        self._password = password
        
        self._cryptor = cipher.RC4(password)
        self._server.server_info = server_info
        self._server.server_info.cryptor = self._cryptor

        self._server_info = server_info 

    def shutdown(self):
        self._server.shutdown()

    def start(self):
            # Main Thread
        self._server.serve_forever()



if __name__ == "__main__":
    server_info = Info_server(socket.AF_INET, socket.SOCK_STREAM)

    server = TraServer("127.0.0.1", 9899, "2333", server_info)
    server.start()


