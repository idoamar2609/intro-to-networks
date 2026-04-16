import socket
import sys

### Parent server code
### this server responsible for:
### 1. loading mapping host : IP records from the file
### 2. listening for incoming  queries from clients like "what is the IP address for www.google.com?"
### 3. responding to clients with the correct IP address for the requested domain, or "non-existent domain" if the domain is not found in the records.

def load_records_from_file(filename ):

    records = {}
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            domain, value, record_type = line.split(",")

            records[domain] = {
                "value": value,
                "type": record_type
            }

    return records

def check_dns_record(domain, records):
    if domain in records:
        return f"{domain},{records[domain]['value']},{records[domain]['type']}"

    # CHECK FOR NS RECORDS
    for key, value in records.items():
        if domain.endswith(key) and value["type"] == "NS":
            return f"{key},{value['value']},{value['type']}"
    return None

def create_socket(my_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # defining protocol IPV4 and UDP
    s.bind(('', my_port))    # binding to myPort
    return s

def server_logic(server_socket, records):
    while True:
        data, addr = server_socket.recvfrom(1024) ## stops here until message from client arrives
        answer = check_dns_record(data.decode().strip(), records) # the data comes as bytes, so we need to decode it to string and strip any whitespace
        if answer:
            server_socket.sendto(answer.encode(), addr)
        else:
            server_socket.sendto(b"non-existent domain", addr)


def main():
    # the server should receive 2 arguments: the port number to listen on, and the name of the file containing the DNS records
    my_port = int(sys.argv[1])
    filename = sys.argv[2]
    # load the mapping records from the file into a dictionary
    records = load_records_from_file(filename)
    # create a socket and bind it to the specified port to listen for incoming queries from clients
    s = create_socket(my_port)
    # dilling with incoming queries
    server_logic(s, records)

if __name__ == "__main__":
    main()




