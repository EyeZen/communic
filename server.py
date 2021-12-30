import socket
import pickle
import threading

import logging

TCP_IP = '127.0.0.1'
T_PORT = 12345
BUF_SIZE = 2048


class Buffer:
    def __init__(self):
        self.buffer = []
        self.lock = threading.Lock()
    def append(self, data):
        self.lock.acquire()
        self.buffer.append(data)
        self.lock.release()
    def remove(self, data):
        self.lock.acquire()
        self.buffer.remove(data)
        self.lock.release()
    def filter(self, predicate):
        self.lock.acquire()
        filtered_buf = filter(predicate, self.buffer)
        self.lock.release()
        return filtered_buf

class Server:
    def __init__(self, address=('127.0.0.1', 12345), buf_size = 2048):
        self.msg_buffer = Buffer()
        self.logger = logging.Log("Logs/server_log", True)
        self.buf_size = buf_size
        self.address = address
        self.isAlive = True
        self.lock = threading.Lock()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(address)

    def  has_msg_for(self, client):
        # lambda returns bool-> if msg.receiver == client
        return lambda smsg : smsg['receiver'] == client

    def handle_client(self, client):
        self.logger.log("Received request from client")
        # msg = (sender, receiver, msg_str)
        try:
            message = pickle.loads( client.recv(self.buf_size) )
        except EOFError:
            self.logger.log("EOFError, probably problem in data format")
            # TODO: need to change this so client knows that msg didn't get through
            empty = pickle.dumps([ False ])
            client.send(empty)
            client.close()
            return 
            
        self.logger.log(f"client >> {message}")
        # msg to itself is not stored on server
        if(message['sender'] != message['receiver']): # msg.receiver != msg.sender
            self.msg_buffer.append(message)
        # cId = data[0]
        # if any_msg.receiver == message.sender, send response (msg.sender, msg.msg_str)
        response = []
        msg_to_client = msg_buffer.filter(self.has_msg_for(message['sender']))
        for msg in msg_to_client:
            response.append(msg)

        if(len(response) > 0):
            # mark response as carrying new message(s)
            response.insert(0, True)
            # remove responses sent from msg-buffer
            for msg in msg_to_client:
                self.msg_buffer.remove(msg)
        else:
            response.append(False)

        self.logger.log(f"{message['sender']} << {response}")
        response = pickle.dumps(response)
        client.send(response)
        client.close()
        
        self.logger.log(f"Closed client: {message['sender']}")

    def start(self):

            self.logger.log(f"Server Started on : {self.address}")
            self.socket.listen(5)
            
            while self.alive():
                client, addr = self.socket.accept()

                self.logger.log(f"Connection Address is: {addr}")
                
                self.handle_client(client)     

    def alive(self):
        return self.isAlive
    
    def setAlive(self, is_alive):
        self.lock.acquire()
        self.isAlive = is_alive
        self.lock.release()

    def __del__(self):
        self.socket.close()


msg_buffer = Buffer()
logger = logging.Log("Logs/server_log")



# Main Code
server = Server()
server.start()