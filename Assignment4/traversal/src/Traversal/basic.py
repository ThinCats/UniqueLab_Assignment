if __package__:
    from . import error
else:
    import error

def send_encr(soc_to, data_raw, encr = False, cryptor=None):

    try:
        if not data_raw:
            raise error.EmptyData
        
        if encr:
            data_raw = cryptor.encrypt(data_raw)
            
        return soc_to.send(data_raw)
    except error.EmptyData:
        raise error.EmptyData

def recv_encr(soc_from, buf_size, encr=False, cryptor=None):

    try:
        data_raw =soc_from.recv(buf_size)
        if not data_raw:
            raise error.EmptyData
        if encr:
            data_raw = cryptor.decrypt(data_raw)
        return data_raw
    except Exception:
        raise

class Info_local(object):
    """
    This is for passing basic info to handler
    """
    def __init__(self, wanted_srv_port, wanted_local_port, request=None, address_family=None, socket_type=None, srv_ip=None, srv_port=None, local_ip="127.0.0.1", local_port=23333, password="2333"):
        self.wanted_srv_port = wanted_srv_port
        self.wanted_local_port = wanted_local_port
        self.address_family = address_family
        self.socket_type = socket_type
        self.srv_ip = srv_ip
        self.srv_port = srv_port
        self.request = request
        self.password = password
        self.local_ip = local_ip
        self.local_port = local_port

class Info_server(object):
    def __init__(self, srv_ip, srv_port, password, address_family=None, socket_type=None):
        self.address_family = address_family
        self.socket_type = socket_type
        self.srv_ip = srv_ip
        self.srv_port = srv_port
        self.password = password