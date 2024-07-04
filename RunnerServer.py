import select
import socket
import threading
import atexit
import time

class RunnerServer:
    def __init__(self, ip='0.0.0.0', port=9876):
        self.server_ip = ip
        self.server_port = port
        self.server_socket = None
        self.client_socket = None
        self.active = False
        

    def start(self):
        self.active = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_ip, self.server_port))
        self.server_socket.listen(1)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        #self.client_socket.connect(())
        pass

    def stop(self):
        if self.active:
            self.active = False
            self.server_socket.close()

    def handle_client(self):
        self.client_socket, client_address = self.server_socket.accept()
        
