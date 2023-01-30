'''
SIMPLE CONNECT: The disconnect function will only work locally as, in testing it didnt make sense to have the client determine
when the server's tcp socket would close. 
'''
import socket

ipAddr = input("Connect to what IP?: ")
port = 1337

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ipAddr, port))

while(True):
    try:
        cmd = input("Send a Command: ")
        client_socket.send(cmd.encode())
        if(cmd == "close"):
            client_socket.send(cmd.encode())
            break
        svrRAW = client_socket.recv(1024)
        svrDATA = svrRAW.decode()
        print(svrDATA)
    except:
        print("TCP Connection closed!")
    
client_socket.close()
