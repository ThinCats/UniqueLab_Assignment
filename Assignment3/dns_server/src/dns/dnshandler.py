
import socket
import logging
import struct
import time

# logging config
logging.basicConfig(level=logging.DEBUG, format="-%(levelname)s %(message)s")
logger = logging.getLogger(__name__)
if not __package__:
    from dnsresolve import dnsrecord
    from dnsresolve import dnsresolver
    from dnsresolve.field import codes
    from dnscache import dnscache
    from dnscache import dnscache_LRU
    from dnsauth import dnsauth
    
else:
    from .dnsresolve import dnsrecord
    from .dnsresolve.field import codes
    from .dnsresolve import dnsresolver
    from .dnscache import dnscache
    from .dnscache import dnscache_LRU
    from .dnsauth import dnsauth

class DNSHandler(object):

    root_servers_ipv4 = ("192.5.5.241", )
    root_servers_ipv6 = ("2001:500:2f::f",)


    # handle function dict

    def __init__(self, istcp, resolver, cli_socket, client_address, addr_family):
        self._isTcp = istcp
        self._resolver = resolver
        self._cli_socket = cli_socket
        # For socket timeout
        self._cli_socket.settimeout(2)

        self._client_address = client_address
        self._addr_family = addr_family

        # Cache
        self._cache = dnscache_LRU.cache_ipv4 if(addr_family is socket.AF_INET) else dnscache_LRU.cache_ipv6

    def recursive_query(self):
        """
        Just change the header that received from and then send back
        """
        # Get data from parent_dns
        # if ipv4
        if self._addr_family == socket.AF_INET:
            dns_server = ("202.114.0.131", 53)
        else:

            dns_server = ("2001:da8:202:10::36", 53)

        # connect to parent dns
        # Resolve client querys
        self._resolver.unpack_header_raw()
        # TODO: Judge THE TC

        # Not change the id because will reuse the id
        self._resolver.record.modify_header(rd=1)
        query_data = self._resolver.pack_just_header()
        
        # print(query_data)

        # Connect to parent DNS to get response
        dns_sock = None
        is_timeout = False
        is_failed = False
        # if TCP:
        if self._isTcp:
            dns_sock = socket.socket(self._addr_family, socket.SOCK_STREAM)
            try:
                dns_sock.connect(dns_server)
                query_data = struct.pack("!H", len(query_data)) + query_data
                dns_sock.sendall(query_data)
            except OSError as e:
                print(e)
                is_failed = True
        else:
            dns_sock = socket.socket(self._addr_family, socket.SOCK_DGRAM)
            dns_sock.sendto(query_data, dns_server)
        # Set default timeout
        dns_sock.settimeout(2)
        try: 
            if not is_failed: # Connection not failed
                receive_data = dns_sock.recv(8192)
            else:
                receive_data = None
                is_timeout = True

        except socket.timeout as e:
            try:
                receive_data = dns_sock.recv(8192)
            except socket.timeout:
                logger.error("Parent Dns Server query failed")
                is_timeout = True
        
        if not is_timeout:
        # adding timeout handling
            # TCP
            if self._isTcp:
                length = struct.unpack("!H", receive_data[:2])[0]
             # Sending not finished
                if len(receive_data) < length + 2:
                    receive_data += dns_sock.recv(8192)
            
                receive_data = receive_data[2:]
            # UDP
            else:
                pass
            # Server_dns socket close
            dns_sock.close

            res = dnsresolver.DNSResolver(receive_data)
            logger.debug(receive_data)
            # Put into cache
            question = res.unpack_question_raw()
            answer = res.unpack_answers_raw()
            if not answer.is_empty():
                for ques in question.rrlist:
                    print("save in cache")
                    logger.info("Resolving {}".format(ques.name))
                    self.save_in_cache(ques.name, codes.TYPE_val[ques.qtype], receive_data, answer.rrlist[0].ttl)
        
        else:
            # TIMEOUT
            self._resolver.record.modify_header(rcode=codes.RCODE["ServFail"], qr=1)
            receive_data = self._resolver.pack_just_header()
            
        # UDP
        if not self._isTcp:
            self._cli_socket.sendto(receive_data, self._client_address)
        # TCP
        else:
            receive_data = struct.pack("!H", len(receive_data)) + receive_data
            self._cli_socket.sendall(receive_data)
    
    def iterative_query(self):
        """
        Iterative query to get domain
        Use UDP and ipv4 to communicate with remote server
        """
        # TODO: Save the root server in another place


        header = self._resolver.unpack_header_raw()
        logger.debug(header)
        question_cli = self._resolver.unpack_question_raw()
        question_result = question_cli.rrlist[0].unpacked_data
        ques_type = question_result[1]
        ques_name = question_result[0]
        # UDP CONNECTION
        dns_sock = socket.socket(self._addr_family, socket.SOCK_DGRAM)
        
        # Loop start to iter all autho to gen the domain info
        
        # Will query for
        authority_addr = self.root_servers_ipv4

        # logger.debug(record_query.data)
        # Errorcode = rcode
        error_code = 0
        resolver_needed = None
        # Firstly get the root server
        a_query_name = "."
        a_query_type = codes.TYPE["NS"]
        while True:
            isOut = False

            # Gen the query dns packet
            record_query = dnsrecord.DNSRecord()
            record_query.add_header(0, 0, 0, 0, 0, 0, 1, 0, id=header.id)
            record_query.add_question(a_query_name, a_query_type)
            logger.debug(record_query.question)
            record_query.update_header()
            record_query.pack()

            # Send to auth addr
            # for addr in authority_addr:
            logger.debug("Authority_addr %s" %(authority_addr))
            # Iter to send to all server
            for addr in authority_addr:
                dns_sock.sendto(record_query.data, (addr, 53))

            # recv first data no matter the ip
            receive_data = dns_sock.recv(8192)
            resolver = dnsresolver.DNSResolver(receive_data)
            header = resolver.unpack_header_raw()

            # judge Something error
            error_code = header.read_flag("rcode")
            if not error_code == 0:
                logger.debug("%s dns query faied %s" %(self._client_address, codes.RCODE_val[error_code]))
                break
    
            answer = resolver.unpack_answers_raw()
            # ip list that will then as the dnsserver:
            ip_list = []
            # Iter the answer to handle it
            for i in answer.rrlist:
                ans_result = i.unpacked_data
                ans_type = ans_result[1] # type
                ans_name = ans_result[0]
                ans_data = ans_result[5]
                logger.debug("Ans result %s" %(str(ans_result)))
                logger.debug("Ans name %s" %(ans_name))
                # FIND OUT
                if ans_name in [ques_name, ques_name+"."] and ans_type == ques_type:
                    # REMAIN all data from server exclude the header
                    # Put it in outter resolver
                    resolver_needed = resolver
                    logger.debug("We are in break")
                    isOut = True
                    break
                # Get the NS record and then query for the NS ip
                elif ans_type == codes.TYPE["NS"]:
                    logger.debug("We are IN NS")
                    # put the ip in it
                    a_query_name = ans_data
                    a_query_type = codes.TYPE["A"]
                    ip_list.append(authority_addr[0])
                
                # It's the authorities ip
                elif ans_type == codes.TYPE["A"]:
                    logger.debug("We are in A")
                    ip_list.append(ans_data)
                    a_query_name = ques_name
            # Change to new authority addr to iter
            authority_addr = ip_list
            if isOut:
                break

        data_to_sent = None 
        if not error_code == 0:
            record_resp = dnsrecord.DNSRecord()
            record_resp.add_header(1, 0, 0, 0, 0, 0, 1, error_code)
            record_resp.pack()
            data_to_sent = record_resp.data
        # No error
        else:
            # TODO
            resolver_needed.unpack_all()
            # Tell client we can use recursive query!
            resolver_needed.record.modify_header(qr=1,ra=1,aa=0)
            resolver_needed.pack_just_header()
            # Save in cache
            # TODO
            
        # UDP:
        if not self._isTcp:
            # TODO: resend when timeout 
            self._cli_socket.sendto(data_to_sent, self._client_address)
        else:
            self._cli_socket.sendall(data_to_sent)
            
    def handleA(self):
        pass
    
    def handleCNAME(self):
        pass

    def handleNS(self, ip_list):
        pass

    def save_in_cache(self, name, a_type, a_data, a_ttl):
        # return dnscache.cache.set_cache(name, a_type, a_data, a_ttl)
        return self._cache.set(name, codes.TYPE[a_type], codes.CLASS["IN"], a_data, a_ttl)

    def cache_handle(self):

        logger.info("Reading from cache\n")
        header = self._resolver.unpack_header_raw()
        question = self._resolver.unpack_question_raw()

        # TODO: MANY question condition
        for ques in question.rrlist:
            # Get cache
            # ans = dnscache.cache.get_cache(ques.name, codes.TYPE_val[ques.qtype])
            ans = self._cache.get(ques.name, ques.qtype, codes.CLASS["IN"])
            # logger.debug(ans) 
            # No cache
            if not ans:
                logger.debug("No cache found")
                return False
            else:
                logger.info("Find cache\n")
                logger.info("Resolving from cache {}".format(ques.name))
                a_resolver = dnsresolver.DNSResolver(ans)
                a_resolver.unpack_all()
                a_resolver.record.modify_header(id=header.id, qr=1, aa=0, ad=0)
                data = a_resolver.pack_just_header()
                # Sent to client
                # UDP
                if not self._isTcp:
                    self._cli_socket.sendto(data, self._client_address)

                else:
                    data = struct.pack("!H", len(data)) + data
                    self._cli_socket.sendall(data)
                
                return True


    # For authoritive Record
    def auth_handle(self):

        logger.info("Try to resolving from Zone file")
        logger.info("Reading from cache\n")

        header = self._resolver.unpack_header_raw()
        question = self._resolver.unpack_question_raw()

        # Judge whether it's in Zone

        # TODO: MANY question condition
        for ques in question.rrlist:
            if not dnsauth.author.is_inZone(ques.name):
                return False
            ans = dnsauth.author.getRecord(ques.name, ques.type_str)
            if not ans:
                logger.debug("No Record found")
                return True
            else:
                logger.info("Find Record\n")
                logger.info("Resolving from Zone File {}".format(ques.name))
                (a_name, a_type_str, a_val) = ans

                reply = dnsrecord.DNSRecord()
                reply.add_header_class(header)
                reply.add_question_class(ques)
                reply.modify_header(id=header.id, qr=1, aa=0, ad=0)
                reply.add_answer(a_name, codes.TYPE[a_type_str], 200, a_val)
                data = reply.pack()
                # Sent to client
                # UDP
                if not self._isTcp:
                    self._cli_socket.sendto(data, self._client_address)

                else:
                    data = struct.pack("!H", len(data)) + data
                    self._cli_socket.sendall(data)
                
                return True        