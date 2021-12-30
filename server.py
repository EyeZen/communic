import socket
import pickle
import threading

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


msg_buffer = Buffer()


def  has_msg_for(client):
    # lambda returns bool-> if msg.receiver == client
    return lambda smsg : smsg[1] == client

def handle_client(client):
    global msg_buffer
    print("Received request from client:", client)

    # msg = (sender, receiver, msg_str)
    data = pickle.loads( client.recv(BUF_SIZE) )
    print(f"client >> {data}")
    # msg to itself not allowed
    if(data[0] != data[1]): # msg.receiver != msg.sender
        msg_buffer.append(data)
    cId = data[0]
    response = []
    msg_to_client =msg_buffer.filter(has_msg_for(cId))
    for msg in msg_to_client:
        # if any msg.receiver == cId, send response (msg.sender, msg.msg_str)
        response.append((msg[0], msg[2]))

    if(len(response) > 0):
        # mark response as carrying new msges
        response.insert(0, True)
        # remove responses sent from msg-buffer
        for msg in msg_to_client:
            msg_buffer.remove(msg)
    else:
        response.append(False)

    print(f"{cId} << {response}")
    response = pickle.dumps(response)
    client.send(response)
    client.close()
    
    print("Closed client:", cId)



# Main Code
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:

    server.bind((TCP_IP, T_PORT))

    print("Server Started on port: ", T_PORT)

    server.listen(5)
    
    while True:
        client, addr = server.accept()

        print("Connection Address is: ", addr)
        
        handle_client(client)