def load_dns_file(filename ):
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
        return f"{domain}, {records[domain]['value']}, {records[domain]['type']}"

    # CHECK FOR NS RECORDS
    for key, value in records.items():
        if domain.endswith(key) and value["type"] == "NS":
            return f"{key}, {value['value']}, {value['type']}"

    return None
import socket

def create_socket(myPort):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # defining protocol IPV4 and UDP
    s.bind(('', myPort))    # binding to myPort
    return s

def server_logic(socket, records):
    while True:
        data, addr = socket.recvfrom(1024)
        answer = check_dns_record(data.decode().strip(), records) # the data comes as bytes, so we need to decode it to string and strip any whitespace
        if answer:
            socket.sendto(answer.encode(), addr)
        else:
            socket.sendto(b"Error: Host not found", addr)


import sys
def main():
    myPort = int(sys.argv[1])
    zoneFileName = sys.argv[2]
    records = load_dns_file(zoneFileName)
    s = create_socket(myPort)
    server_logic(s, records)

if __name__ == "__main__":
    main()




