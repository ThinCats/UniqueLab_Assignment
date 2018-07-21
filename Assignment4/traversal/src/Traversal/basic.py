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

