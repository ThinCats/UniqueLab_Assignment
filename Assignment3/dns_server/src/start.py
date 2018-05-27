import multiprocessing
import os

from dns import server_ipv6

if __name__ == "__main__":

    # For saving diffrent ip_type and Transmission protocol
    server_args = []
    # ipv4, udp
    server_args.append((False, False))
    # ipv4, tcp
    server_args.append((False, True))
    # ipv6, udp
    server_args.append((True, False))
    # ipv6, tcp
    server_args.append((True, False))

    server_pool = multiprocessing.Pool(4)

    for i in range(4):
        server_pool.apply_async(server_ipv6.start_server, args=server_args[i])
    
    print("Start all server from parent {}".format(os.getpid()))
    server_pool.close()
    server_pool.join()
    print("Server all ends")
    