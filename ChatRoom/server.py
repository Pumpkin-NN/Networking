'''
Program name: ChatRoom
Server: provides a common chat room
'''
import socket
import threading
import argparse
import sys

def broadcast(clients, msg, name=""):
    for client in clients:
        message = name.encode('utf-8') + msg
        try:
            client.send(message)
        except BrokenPipeError:
            sys.exit(1)

def chat_room(c, clients):
    try:
        data = c.recv(4096).decode('utf-8')
        # JOIN method: client joining a chat room
        JOIN = f"""
CHAT/1.0 JOIN\r\n
Username: {data}\r\n
\r\n
        """
        print(JOIN)
        client = f"{data} has joined the chat room..."
        clients[c] = data
        broadcast(clients, client.encode('utf-8'))
        while True:
            msg = c.recv(4096) 
            bye = 'Gotta go, TTYL!'
            if msg != bye.encode('utf-8'):
                broadcast(clients, msg, data+": ")
                # TEXT method: client sending a message to chat room
                TEXT = f"""
CHAT/1.0 TEXT\r\n
Username: {data}\r\n
Msg-len: {len(msg.decode('utf-8'))}\r\n
Msg: {msg.decode('utf-8')}
\r\n
                """
                print(TEXT)
            else:
                broadcast(clients, msg, data+": ")
                # LEAVE method: client leaving a chat room
                LEAVE = f"""
CHAT/1.0 LEAVE\r\n
Username: {data}\r\n
\r\n
                """
                print(LEAVE)
                c.close()
                #print(f"before del: {clients}")
                del clients[c]
                #print(f"after del: {clients}")
                left = f"{data} has left the chat."
                broadcast(clients, left.encode('utf-8'))
                break
    except Exception as e:
        raise e
        sys.exit(1)


if __name__ == '__main__':
    # Use argparse method
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('server_port', nargs='?', default=8765)
    args = parser.parse_args()
    
    # Create TCP socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        print("Error: could not create socket")
        print("Description: " + str(msg))
        sys.exit()

    # Bind to listening port
    try:
        host=''  # Bind to all interfaces
        s.bind((host,args.server_port))
    except socket.error as msg:
        print("Error: unable to bind on port %d" % args.server_port)
        print("Description: " + str(msg))
        sys.exit()

    # Listen
    try:
        backlog=100  # Number of incoming connections that can wait
                    # to be accept()'ed before being turned away
        s.listen(backlog)
    except socket.error as msg:
        print("Error: unable to listen()")
        print("Description: " + str(msg))
        sys.exit()    
    print("Listening socket bound to port %d" % args.server_port)
    
    clients = {}
    while True:
        # Accept an incoming request
        try:
            (client_s, client_addr) = s.accept()
            # If successful, we now have TWO sockets
            #  (1) The original listening socket, still active
            #  (2) The new_connection socket connected to the client
        except socket.error as msg:
            print("Error: unable to accept()")
            print("Description: " + str(msg))
            sys.exit()

        print("Accepted incoming connection from client")
        client_ip, port = client_addr
        print(f"Client IP: {str(client_ip)} Port: {str(port)}")

        client_s.send("<TYPE 'Gotta go, TTYL!' to QUIT>".encode("utf8"))
        threading.Thread(target = chat_room, args = (client_s, clients)).start()