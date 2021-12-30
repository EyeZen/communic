import pickle
import socket
import time

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send_msg(cId, receiver, msg_str):
    global client

    TCP_IP = '127.0.0.1'
    T_PORT = 12345
    BUF_SIZE = 2048

    new_msg = None
    
    # connect to server
    client.connect((TCP_IP, T_PORT))
    # send msg = [ sender, receiver, msg_str ]
    client.send( pickle.dumps([ cId, receiver, msg_str ]) )
    print("sent:", [ cId, receiver, msg_str ])
    
    # receive response= [ hasMsg, (sender, msg_str), ... ]
    response = pickle.loads(client.recv(BUF_SIZE))
    print("received:", response)

    # if response.hasMsg
    if(response[0] == True):
        # load all new msg's
        new_msg = [ response[i] for i in range(1, len(response)) ]
        
    return new_msg


# Main Code
cId = input("Who are you? ")
try:
    while True:
        receiver = input("Enter receipient: ")
        msg = input(">> ")

        new_msg = send_msg(cId, receiver, msg)

        if(new_msg):
            for msg in new_msg:
                # print (sender, msg)
                print( f"<< {msg[0]}: {msg[1]} >>" )
        else:
            print("No new msg!")
finally:
    client.close()