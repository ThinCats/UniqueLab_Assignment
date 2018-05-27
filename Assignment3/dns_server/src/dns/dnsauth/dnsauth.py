
import time
import json

if __package__ is None:
    import dnsauthsaver
else:
    from . import dnsauthsaver
# from ..dnsresolve.field import codes
# from ..dnsresolve import dnsrecord
# from ..dnsresolve.field import *
class SOA(object):
    
    def __init__(self, name, nameserver, mail, sn, refresh=1800, retry=900, expire=604800, ttl=86400, a_class=1):
        self.name = name
        self.nameserver = nameserver
        self.mail = mail
        self.sn = sn
        self.refresh = refresh
        self.retry = retry
        self.expire = expire
        self.ttl = ttl
        self.a_class = a_class

class DNSAuth(object):

    soa = SOA("dns.dns.", "localhost", "thincats.163.com", sn=time.time())
    def __init__(self):
        pass

    def getZone(self):
        return DNSAuth.soa.name

    def getZoneNS(self):
        return DNSAuth.soa.nameserver

    def addRecord(self, name, val, type_str):
        data = json.dumps((name, type_str, val))
        dnsauthsaver.saver.save_record(name, type_str, data)

    def getRecord(self, name, type_str):
        data = dnsauthsaver.saver.get_record(name, type_str)
        return json.loads(data) if(not data is None) else None

    def is_inZone(self, domain):
        if DNSAuth.soa.name[-1] != ".":
            DNSAuth.soa.name += "."
        if len(domain) == 0:
            return False
        if domain[-1] != ".":
            domain += "."
        # Bugs here
        return not domain.find(DNSAuth.soa.name) == -1
author = DNSAuth()
author.addRecord("dns.dns", "123.0.0.0", "A")
if __name__ == "__main__":
    auth = DNSAuth()

    auth.addRecord("baidu.com", "1232.123123.213.3", "A")
    print(auth.getRecord("baidu.com", "A"))

    auth.addRecord("Baidu.com", "4399.com", "CNAME")
    print(auth.getRecord("Baidu.com", "CNAME"))
    (a_name, a_type, a_val) = auth.getRecord("Baidu.com", "CNAME")
    print(a_name, a_type, a_val)
        
    print(auth.is_inZone("www.ddafdns.dns."))