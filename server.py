'''
TO ADD: Selection system between local network and port-forwarded games using ngrok

DISCUSSING POINTS: What data should be sent between client and server beside positional information?

'''
import socket

host = '0.0.0.0' #
port = 1337

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))

while True:
    server_socket.listen(5)
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address}")
    client_socket.sendall(b"Hello, client!\n")
    client_socket.sendall(b"For a list of commands, type [help]!")
    clientRAW = client_socket.recv(1024)
    clientCMD = clientRAW.decode()
    if(clientCMD == 'help'):
        client_socket.send(b"TEMPORARY HELP MESSAGE: FILL WITH LIST OF COMMANDS IN THE FUTURE")
    else:
        print("Sorry, please try again")

server_socket.close()
