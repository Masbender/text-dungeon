import socketserver

HOST = "127.0.0.1"
PORT = 1337

class makeServer(socketserver.BaseRequestHandler):
    def handle(self):
        


