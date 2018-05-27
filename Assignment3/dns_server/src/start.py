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
    server_args.append((True, True))

    server_pool = multiprocessing.Pool(4)

    for arg in server_args:
        server_pool.apply_async(server_ipv6.start_server, args=arg)
    
    print("Start all server from parent {}".format(os.getpid()))
    server_pool.close()
    try:
        server_pool.join()
    except KeyboardInterrupt as e:
        print(e)
        server_pool.terminate()
    
    print("Server all ends")
    