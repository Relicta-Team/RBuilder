import select
import socket
import threading
import atexit
import time
import logging
from queue import Queue

class Message:
    def __init__(self, cmd, args):
        self.command = cmd
        self.args = args

class ServerThread(threading.Thread):
    lock = threading.Lock()
    def run(self) -> None:
        self.name = "RunnerServer"
        return super().run()

class RunnerServer:
    def __init__(self, ip='127.0.0.1', port=9897):
        self.queue = Queue()
        
        self.callbackQueue = Queue()

        self.logger = logging.getLogger("SRV")
        self.logger.setLevel(logging.DEBUG)
        self.server_ip = ip
        self.server_port = port
        self.server_socket = None
        self.client_socket = None
        self.active = False
        self.clientConnected = False
        self.thread = ServerThread(target=self.handle_client)

    def isClientConnected(self):
        with self.thread.lock:
            return self.clientConnected
        
    def setClientConnected(self,value):
        with self.thread.lock:
            self.clientConnected = value
        
    def addCallback(self, callback:str):
        self.callbackQueue.put(callback)

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_ip, self.server_port))
        self.server_socket.listen(1)
        self.active = True
        self.logger.debug("Started")
        self.thread.start()

    def stop(self):
        with self.thread.lock:
            if self.active:
                self.active = False
                self.server_socket.close()
                self.clientConnected = False
                self.logger.debug("Stopped")
                

    def handle_client(self):
        try:
            while self.active:
                self.client_socket, client_address = self.server_socket.accept()
                self.client_socket.setblocking(False)
                self.setClientConnected(True)
                
                buff = b''
                while self.active and not self.client_socket._closed:
                    try:
                        rread, wwrite, _ = select.select([self.client_socket], [self.client_socket], [], 0)
                        if rread:
                            dat = self.client_socket.recv(1024)
                            if not dat:
                                break
                            buff += dat
                            while b'\0' in buff:
                                dt,buff = buff.split(b'\0', 1)
                                self.handle_client_message(dt.decode('utf-8'))
                        if wwrite:
                            if not self.callbackQueue.empty():
                                dt = self.callbackQueue.get()
                                self.client_socket.sendall(dt.encode('utf-8'))
                    except BlockingIOError:
                        pass
                    except ConnectionResetError:
                        break

                self.client_socket.close()
                self.setClientConnected(False)
        except OSError:
            print("server closed")
            pass
        except Exception as e:
            print(f"UNKNOWN SERVER ERROR <{e.__class__.__name__}>: {e}")

        
    def handle_client_message(self, message):
        if not message.startswith('m:'):
            return
        message = message[2:]
        cmd,args = message.split(';',1)
        if (cmd == "print"):
            self.logger.info(args.replace('',";"))
            return
        self.queue.put(Message(cmd,args))
        self.logger.debug("Received: {} with args: {}".format(cmd,args))