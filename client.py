import pickle
import socket
import time
import logging

class Client:
    def __init__(self, address=('127.0.0.1', 12345), buf_size=2048):
        self.address = address
        self.buf_size = buf_size
        self.message = {'sender': None, 'receiver': None, 'msg': None}
        self.logger = logging.Log("Logs/client_log", True)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()

    def connect(self):
        try:
            self.client.connect(self.address)
            self.logger.log("connected")
        # if connection timed out, wait a little longer, then reconnect
        except TimeoutError:
            self.logger.log("Timeout, wait for 20s")
            time.sleep(20)
            self.connect()
        # if connection aborted due to network failure, wait then reconnect
        except ConnectionAbortedError:
            self.logger.log("connection aborted! wait for 10s")
            time.sleep(10)
            self.connect()

    def send(self):
        # assumption: message to send passed in Client::message
        data = pickle.dumps(self.message)
        try:
            # keep looping until data sent
            while True:
                # send msg = [ sender, receiver, msg_str ]
                datasent = self.client.send( data )
                if datasent:
                    self.logger.log(f"sent: {self.message}")
                    break
        except ConnectionError:
            # shutdown and wait
            self.client.shutdown(socket.SHUT_RDWR)
            self.client.close()
            self.logger.log("Connection reset error! wait for 10s")
            time.sleep(10)
            # restart socket
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect()
            # resend
            self.send()
        
    def recv(self, dummy = False):
        new_msg = []

        if dummy:
            self.message['receiver'] = self.message['sender']

        try:
            response = self.client.recv(self.buf_size)
            response = pickle.loads(response)
            if response[0] == True:
                new_msg = [ response[i] for i in range(1, len(response)) ]
            self.logger.log(f"received: {response}")
        except ConnectionError:
            # shutdown and wait
            self.client.shutdown(socket.SHUT_RDWR)
            self.client.close()
            self.logger.log("Connection Error while fetching response! wait for 10s")
            time.sleep(10)
            # restart socket
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect()
            # send a dummy msg to fetch response
            self.message['receiver'] = self.message['sender']
            self.send()

    def start(self):
        self.message['sender'] = input("Who are you? ")


        while True:
            self.message['receiver'] = input("Enter receipient: ")
            self.message['msg'] = input(">> ")
            self.send()
            new_msg = self.recv()    
            if(new_msg):
                for msg in new_msg:
                    print( f"<< {msg['sender']}: {msg['msg']} >>" )
            else:
                print("No new msg!")            
            
    def __del__(self):
        try:
            self.client.close()
        finally:
            self.logger.log("Connection Closed")


client = Client()

client.start()