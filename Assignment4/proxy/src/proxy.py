
import argparse, sys, logging, socketserver

from SOCKS import proxy_local, proxy_srv
from SOCKS.config import Config

def arg_parse():
    # Argparse
    arg_parser = argparse.ArgumentParser(description="Simple SOCKS5 Proxy")
        # Local or Server    
    mutual_group_type = arg_parser.add_mutually_exclusive_group()
    mutual_group_type.add_argument("-s", "--server", help="Server mode", action="store_true")
    mutual_group_type.add_argument("-l", "--local", help="Local mode", action="store_true")
        # Config file set
    arg_parser.add_argument("-c", "--config", metavar="FILE_PATH", help="Set the config file[JSON]", default="./config.json")
        # Verbose mode
    mutual_group_verbose = arg_parser.add_mutually_exclusive_group()
    mutual_group_verbose.add_argument("-d", "--debug", help="Verbose DEBUG", action="store_true")
    mutual_group_verbose.add_argument("-q", "--quiet", help="Verbose QUEIT", action="store_true")
        # PAC Mode
    arg_parser.add_argument("--no-pac", help="Close PAC Mode", action="store_true")
    # Settle the args
    args = arg_parser.parse_args()
    if not (args.server or args.local):
        print("Must specify a mode[Local/Server]")
        arg_parser.print_help()
        sys.exit(0)
    proxy_type = ("server" if(args.server) else "local")
    if args.debug:
        proxy_verbos = logging.DEBUG
    elif args.quiet:
        proxy_verbos = logging.ERROR
    else:
        proxy_verbos = logging.INFO
    return (proxy_type, proxy_verbos, args.config, args.no_pac)


if __name__ == "__main__":
    out = arg_parse()
    logging.basicConfig(level=out[1], format='%(asctime)s %(threadName)s %(levelname)-8s: %(message)s')

    # Config file
    config_parser = Config.Config(out[0])
    info = config_parser.load(out[2])

    # PAC
    if out[3]:
        info.pac_file = None
    
    if out[0] == "server":
        server = proxy_srv.SocksServer(info.server_ip, info.server_port, info.password, info.ipv6)
    if out[0] == "local":
        server = proxy_local.SocksServer(info.local_ip, info.local_port, info.password, info.proxy_server, info.server_port, info.ipv6, info.pac_file, info.userpass_file)

    # Start server
    server.start()
