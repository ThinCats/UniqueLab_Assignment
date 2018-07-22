import logging
import socket
import socketserver

if __package__:
    from .resolver import codes, connect, handshake
    from .cryptor import cipher
    from . import error
    from .basic import *
else:
    from resolver import codes, connect, handshake
    from cryptor import cipher
    import error
    from basic import *

def handshake_cli(data_raw, cli_soc, cryptor):
    # Handshake
    send_encr(cli_soc, data_raw, True, cryptor)
        # This will verify. Give up encryption
    handshake_recv_raw = recv_encr(cli_soc, 4096, False, None)
    handshake_recv = handshake.cli_decode(handshake_recv_raw)
    if handshake_recv[0] == codes.VERIFY["YES"]:
        cryptor = cipher.RC4(cryptor.user_key, str(handshake_recv[1]))
    else:
        logging.error("Handshake with Server Failed.")
        raise error.HandshakeFailed
    return cryptor

"""
| Version | Request | Port
"""
def connect_srv(to_cli_soc, server_info, cryptor, handler):
    connect_recv_raw = recv_encr(to_cli_soc, 4096, True, cryptor)
    data_decoded = connect.srv_decode(connect_recv_raw)
    print(data_decoded)

    status = codes.STATUS["GENERAL"]
    binded_server = None
    if data_decoded[0] != codes.VERSION["V1"]:
        logging.error("VERSION Not support {}".format(data_decoded[0]))
    else:
        # Handle request:
        is_ok = True
        if data_decoded[1] == codes.REQUEST["FORWARD"]:
            # New a tunnel Server
            try:
                socketserver.ThreadingTCPServer.address_family = server_info.address_family
                if server_info.socket_type == socket.SOCK_STREAM:
                    binded_server = socketserver.ThreadingTCPServer(("0.0.0.0", data_decoded[2]), handler)
                elif server_info.socket_type == socket.SOCK_DGRAM:
                    binded_server = socketserver.ThreadingUDPServer(("0.0.0.0", data_decoded[2]), handler)
                else:
                    logging.error("Unsupport addr_family {}".format(server_info.address_family))
            except socket.error as e:
                logging.error("Failed {}".format(e))
                binded_server = None
                status = codes.STATUS["PORT"]
                is_ok = False
            # OK
            if is_ok:
                status = codes.STATUS["OK"]
                logging.info("Port[{}] Open".format(data_decoded[2]))

        elif data_decoded[1] ==  codes.REQUEST["STUN"]:
            logging.warn("Temp not support STUN")
            status = codes.STATUS["GENERAL"]
        else:
            logging.warn("Request Not Support {}".format(data_decoded[1]))
            status = codes.STATUS["REQUEST"]
        
        connect_send_raw = connect.srv_encode(codes.VERSION["V1"], status, data_decoded[2])
        send_encr(to_cli_soc, connect_send_raw, True, cryptor)
        return binded_server 
        
def connect_cli(data_raw):
    data_decoded = connect.cli_decode(data_raw)

    if data_decoded[1] == codes.STATUS["OK"]:
        return (True, data_decoded[1])
    else:
        return (False, data_decoded[1])


def handshake_srv(cli_soc, cryptor):
    handshake_recv_raw = recv_encr(cli_soc, 4096, True, cryptor)
    if handshake.srv_decode(handshake_recv_raw) == codes.magic_str.encode("ascii"):
        is_verified = True
    else:
        is_verified = False
    
    # Send to cli
    handshake_send_raw, ran_num = handshake.srv_encode(is_verified)
    cryptor_tmp = cipher.RC4(cryptor.user_key, str(ran_num))
    send_encr(cli_soc, handshake_send_raw, False, None)
    return (is_verified, cryptor_tmp)
