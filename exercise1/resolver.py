import socket
import sys
import time

cache = {}

def create_socket(my_port, ip = ''):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # defining protocol IPV4 and UDP
    s.bind((ip, my_port))    # binding to my_port
    return s

def check_cache(domain):
    if domain in cache:
        ip, rtype, expiry = cache[domain]
        if time.time() <= expiry:
            return f"{domain},{ip},{rtype}"  # cache hit
        else:
            del cache[domain]  # expired
    return None

def send_request_to_server(domain, server_ip, server_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.sendto(domain.encode(), (server_ip, server_port))
    data, _ = server_socket.recvfrom(1024)
    return data.decode().strip()

def check_non_existence(answer):
    return answer == "non-existent domain"

def non_existent_domain_response(server_socket, addr):
    server_socket.sendto(b"non-existent domain", addr)


def server_logic(server_socket, parent_ip, parent_port, ttl):
    while True:
        data, addr = server_socket.recvfrom(1024) ## waits for message from client
        query_domain = data.decode().strip()
        cache_answer = check_cache(query_domain)
        # first we want to check if the answer is in our cache:
        if cache_answer:
            server_socket.sendto(cache_answer.encode(), addr)
        # if answer isn't in cache, we need to ask the parent server until we get the A record, and cache the result for future use:
        else:
            # asking parent server
            parent_answer = send_request_to_server(query_domain, parent_ip, parent_port)
            # if parent says it doesn't exist we send this message:
            if check_non_existence(parent_answer):
                non_existent_domain_response(server_socket, addr)
            # parent return A / NS record:
            else:
                _, value, record_type = parent_answer.split(",")
                ns_answer = None
            # if the parent server return record_type NS we need to ask the NS server for the answer until getting the A record
                while record_type == "NS":
                    ip, port = value.split(":")
                    ns_answer = send_request_to_server(query_domain, ip, int(port))
                    if check_non_existence(ns_answer):
                        non_existent_domain_response(server_socket, addr)
                        break
                    else:
                        _, value, record_type = ns_answer.split(",")
                # once we get the A record from NS server, we can return it to client and cache it
                if not check_non_existence(ns_answer):
                    cache[query_domain] = (value, record_type, time.time() + ttl)  # cache the result with expiry time
                    server_socket.sendto(f"{query_domain},{value},{record_type}".encode(), addr)

def main():
    my_port = int(sys.argv[1])
    parent_ip = sys.argv[2]
    parent_port = int(sys.argv[3])
    ttl  = int(sys.argv[4])
    server_socket = create_socket(my_port)
    server_logic(server_socket, parent_ip, parent_port, ttl)

if __name__ == "__main__":
    main()