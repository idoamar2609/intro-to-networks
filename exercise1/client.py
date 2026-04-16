import socket
import sys

### this is a client. he waits for input from uer and sends the resolver server the domain query in order to gets the appropriate IP address.

def main():
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) ## defining protocol IPV4 and UDP
    while True:
        message = input("") ## waits for user input
        s.sendto(message.encode(), (server_ip, server_port)) # the message is encoded to bytes before sending to the resolver server
        data, addr = s.recvfrom(1024) ## waits for response from resolver server, the response is in bytes, so we need to decode it to string before printing
        if data.decode() == "non-existent domain": ## if the response is "non-existent domain" we print it and continue to wait for next user input
            print("non-existent domain")
        else:
            domain, value, record_type = data.decode().split(",") ## the response is in the format of "domain, value, record_type"
            print(value)

if __name__ == "__main__":
    main()