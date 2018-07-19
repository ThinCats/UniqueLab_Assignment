
import json

TYPE = {
    "SERVER": 0,
    "LOCAL": 1,
}

class Server_info(object):
    def __init__(self, *, server_ip, server_port, password, ipv6):
        self.server_ip = server_ip
        self.server_port = server_port
        self.password = password
        self.ipv6 = ipv6

        

class Local_info(object):
    def __init__(self, *, proxy_server, server_port, local_ip, local_port, password, pac_file, userpass_file, ipv6):
        self.proxy_server = proxy_server
        self.server_port = server_port
        self.local_ip = local_ip
        self.local_port = local_port
        self.password = password
        self.pac_file = pac_file
        self.userpass_file = userpass_file
        self.ipv6 = ipv6

class Config(object):
    
    def __init__(self, a_type="server"):
        
        if type(a_type) is str:
            try:
                self._type = TYPE[a_type.upper()]
            except Exception:
                raise
        elif type(a_type) is int:
            self._type = a_type
        else:
            raise TypeError("Error config type")

    def load(self, filepath="config.json"):
        """
        Load config file from path
        """
        if not filepath:
            filepath = "config.json"

        with open(filepath, "r") as f_in:
            js_read = json.load(f_in)

            try:
                if self._type == TYPE["SERVER"]:
                    return Server_info(**js_read["server"])
                elif self._type == TYPE["LOCAL"]:
                    return Local_info(**js_read["local"])
                    
            except Exception:
                raise



            
