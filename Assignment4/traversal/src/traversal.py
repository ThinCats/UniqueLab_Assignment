
import argparse, logging, json, socket, sys

from Traversal import tra_local, tra_server, basic, resolver

def arg_parse():
    # Argparse
    arg_parser = argparse.ArgumentParser(description="Simple Traversal Server")
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
    return (proxy_type, proxy_verbos, args.config)

def config(a_type, filepath):
    if not filepath:
        filepath = "config.json"
    with open(filepath, "r") as f:
        js_read = json.load(f)

    a_type = a_type.lower()
    try:
        if a_type == "server":
            return basic.Info_server(**js_read["server"])
        elif a_type == "local":
            return basic.Info_local(**js_read["local"])
    except Exception:
        raise

if __name__ == "__main__":
    out = arg_parse()
    logging.basicConfig(level=out[1], format='%(asctime)s %(threadName)s %(levelname)-8s: %(message)s')

    # Config file
    info = config(out[0], out[2])

    info.socket_type = socket.SOCK_STREAM
    info.address_family = socket.AF_INET
    info.request = resolver.codes.REQUEST["FORWARD"]

    if out[0] == "server":
        server = tra_server.TraServer(info.srv_ip, info.srv_port, info.password, info)
    if out[0] == "local":
        server = tra_local.LocalServer(info.local_ip, info.local_port, info.password, info)

    # Start server
    server.start()
