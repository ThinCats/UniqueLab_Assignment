"""
This is for handling building connections REQUEST in SOCKS5

Just handle request.
Clients sending packet function will not be included here
"""

import socket
import logging
import errno


logging.basicConfig(format='%(asctime)s %(levelname)-8s: %(message)s')
logger = logging.getLogger()
if __package__:
    from .resolver import nego, connect, support, codes, udp, userpass
else:
    from resolver import nego, connect, support, codes, udp, userpass

def negotiation_srv(nego_recv_raw, srv_soc, user_method=None):

    # NEW ADDED
    # USER-SET
    if not user_method:
        srv_soc.sendall(nego.srv_encode(user_method))
        return not user_method == codes.METHOD["REFUSE"]
    ## END
    
    nego_recv = nego.srv_decode(nego_recv_raw)
    # print("Nego recv data: {}".format(nego_recv))

    # Reply
    srv_method = codes.METHOD["REFUSE"]
    is_verify_ok = True
    # Version check
    if nego_recv[0] == codes.VERSION["SOCKS5"]:
        # Assign method
        for method in nego_recv[1]:
            # TODO: Algorithms for assigning methods
            if method in support.methods:
                srv_method = method
                break
    else:
        logger.warn("Client SOCKS Version Invalid. {}".format(nego_recv[0]))
        is_verify_ok = False
    
    reply_raw = nego.srv_encode(srv_method)
    # print("Nego reply raw data: {}".format(reply_raw))
    srv_soc.sendall(reply_raw)

    # Userpass subnegotation
    if is_verify_ok and srv_method == codes.METHOD["USERPASS"]:
        is_verify_ok = userpass_srv(srv_soc)
    
    return is_verify_ok

def connection_srv(connect_recv_raw):

    connect_recv = connect.srv_decode(connect_recv_raw)
    # print("Connect recv data: {}".format(connect_recv))
    
    # Remote socket
    remote_soc = None
    srv_status = None
    # Now only support connect:
    # request type:
    if connect_recv[1] == codes.REQUEST["CONNECT"]:
        srv_status, remote_soc = _remote_connect(connect_recv[2], connect_recv[3][0], connect_recv[3][1])

    elif connect_recv[1] == codes.REQUEST["BIND"]:
        # TODO: Handle BIND
        pass
    elif connect_recv[1] == codes.REQUEST["UDP"]:
        # TODO: Handle UDP connection
        srv_status, remote_soc = _remote_connect(connect_recv[2], connect_recv[3][0], connect_recv[3][1], socket.SOCK_DGRAM)
    else:
        logger.error("Unknown Request Type: {}".format(connect_recv[1]))
        srv_status = codes.STATUS["COMMAND"]

    # Pack reply
    connect_rep_raw = connect.srv_encode(srv_status, connect_recv[2], *connect_recv[3])
    # print("Connect reply raw data: {}".format(connect_rep_raw))
    return (remote_soc, connect_rep_raw)


def userpass_srv(srv_soc):
    # TODO: Password list!!!
    # Status: 0 means success
    status = 1
    userpass_recv_raw = srv_soc.recv(4096)
    version, username, password = userpass.srv_decode(userpass_recv_raw)
    if not version == codes.SUBVERSION["USERPASS"]:
        logger.error("Client USERPASS version unsupport. {}".format(version))
        status = 1

    # TODO: ...
    elif username == "brody" and password == "123":
        status = 0
    else:
        logger.error("Client USERPASS: user or password invalid")
        status = 1
    srv_soc.sendall(userpass.srv_encode(status))
    return status == 0



"""
Use false or True to determine whether terminate the connection
It's only for TCP
"""
def negotiation_cli(nego_recv_raw, cli_soc):
    nego_recv = nego.cli_decode(nego_recv_raw)
    # print("Nego recv data: {}".format(nego_recv))

    # Version mismatch or Server refused
    if not nego_recv[0] == codes.VERSION["SOCKS5"] or nego_recv[1] == codes.METHOD["REFUSE"]:
        logger.critical("Server Refuse Connection. Terminated")
        return False
    # No need to auth
    elif nego_recv[1] == codes.METHOD["NONEED"]:
        return True
    elif nego_recv[1] == codes.METHOD["GSSAPI"]:
        logger.critical("Now not support GSSAPI")
        return False
    elif nego_recv[1] == codes.METHOD["USERPASS"]:
        # TODO: Use another way to get username and password
        username = input("Your username:")
        password = input("Your password:")
        return userpass_cli(username, password, cli_soc)


def userpass_cli(username, password, cli_soc):
    userpass_rep_raw = userpass.cli_encode(username, password)

    cli_soc.sendall(userpass_rep_raw)
    userpass_recv_raw = cli_soc.recv(2048)

    # print("Client userpass recv raw data: {}".format(userpass_recv_raw))
    userpass_recv = userpass.cli_decode(userpass_recv_raw)
    # print("Client userpass recv data: {}".format(userpass_recv))

    # Version check and verify USERPASS
    if not userpass_recv[0] == codes.SUBVERSION["USERPASS"]:
        logger.error("NOT USERPASS Protocol Version: {}".format(userpass_recv[0]))    
        return False
    elif userpass_recv[1] == 0:
        logger.info("USERPASS Verified")
        return True
    elif not userpass_recv[1] == 0:
        logger.error("Username or Password is invalid")
        return False
    
"""
If false, just return false
If True, return (addr_type, (addr, port))
"""
def connection_cli(connect_recv_raw):
    connect_recv = connect.cli_decode(connect_recv_raw)
    # print("Client connect recv data: {}".format(connect_recv))

    if connect_recv[0] == codes.VERSION["SOCKS5"] and connect_recv[1] == codes.STATUS["SUCCEED"]:
        return connect_recv[2:]
    else:
        return False



"""
This is For creating remote socket, easily monitoring
and handling its errors
For connection and UDP process
"""
def _remote_connect(addr_type, addr, port, sock_type=socket.SOCK_STREAM, domain_AF=socket.AF_INET):
    
    remote_soc = None
    try:
        if addr_type == codes.ADDRESS["IPV4"]:
            remote_soc = socket.socket(socket.AF_INET, sock_type)
        elif addr_type == codes.ADDRESS["IPV6"]:
            remote_soc = socket.socket(socket.AF_INET6, sock_type)
        elif addr_type == codes.ADDRESS["DOMAIN"]:
            # Here use IPV4 For default
            remote_soc = socket.socket(domain_AF, sock_type)
        else:
            logger.warn("Adress Type unknown {}".format(addr_type))
            return (codes.STATUS["ADDRESS"], None)

    except socket.error as err:
        logger.error("Error creating remote socket: {}".format(err))
        if err.errno == errno.ENETUNREACH:
            return (codes.STATUS["NETWORK"], None)
    
    # default timeout
    remote_soc.settimeout(3)
    # TCP:
    if sock_type == socket.SOCK_STREAM:
        try:
            remote_soc.connect((addr, port))

        except socket.timeout as err:
            logger.error("Connect Timeout: {}".format(err))
            remote_soc.close()

            return (codes.STATUS["HOST"], None)
        except socket.error as err:
            logger.error("Error connect to remote server: {}".format(err))
            remote_soc.close()

            if err.errno == errno.ECONNREFUSED:
                return (codes.STATUS["CONNECTION"], None)
            elif err.errno == errno.EHOSTUNREACH:
                return (codes.STATUS["HOST"], None)

    """
    # Try to send data
    try:
        if sock_type == socket.SOCK_STREAM:
            remote_soc.sendall(b"GET / HTTP/1.0\r\n\r\n")
        else:
            remote_soc.sendto(b"GET / HTTP/1.0\r\n\r\n", (addr, port))
    except socket.error as err:
        logger.error("Sending data: {}".format(err))
        remote_soc.close()
        if err.errno == errno.EHOSTUNREACH:
            return (codes.STATUS["HOST"], None)

    # try receive data
    try:
        buffer = remote_soc.recv(2048)
    except socket.error as err:
        # remote_soc.close()
        print(remote_soc.type)
        logger.error("Receiving data: {}".format(err))
    """
    # Successful
    return (codes.STATUS["SUCCEED"], remote_soc)



if __name__ == "__main__":
    # _remote_connect(codes.ADDRESS["IPV4"], "118.184.184.70", 80)
    raw = connect.cli_encode(codes.REQUEST["CONNECT"], codes.ADDRESS["IPV4"], "118.184.184.70", 80)
    connection_srv(raw)
    cli_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # userpass_cli("brody", "123", cli_soc)
    nego_raw = nego.srv_encode(codes.METHOD["GSSAPI"])
    # print(negotiation_cli(nego_raw, cli_soc))