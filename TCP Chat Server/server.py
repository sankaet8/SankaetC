import socket
import sys
import threading

# python3 -u server.py <port> <password>

# python3 -u client.py <host> <port> <password> <name>

client_dict = {}
port = int(sys.argv[1])
password = str(sys.argv[2])

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.bind(("localhost", port))
sock.listen()
print(f"Server started on port {port}. Accepting connections...")

def handle_client(socket):
    incoming = socket.recv(1024).decode()
    incoming_list = incoming.split('\n')
    
    if len(incoming_list) == 2:
        client_password = incoming_list[0]
        client_name = socket.recv(1024).decode()
        if client_name in client_dict.keys() or " " in client_name:
            socket.close()
            return
    elif len(incoming_list) == 3:
        client_password = incoming_list[0]
        client_name = incoming_list[1]
        if client_name in client_dict.keys() or " " in client_name:
            socket.close()
            return
    
    if password != client_password:
        socket.close()
        return
        
    #---------- if this part has been reached, name and password are valid ------------#
    socket.send(b"Welcome!\n")
    
    message = f"{client_name} joined the chatroom\n"
    broadcast(message)
    
    client_dict[client_name] = socket
    
    while True:
        try:
            message = socket.recv(1024).decode("utf-8")
            if message:
                if message[:3] != ":dm":
                    message = f"{client_name}: {message}"
                    broadcast(message)
                else:
                    split_message = message.split(" ")
                    destination = split_message[1]
                    destination_socket = client_dict[destination]
                    source_socket = client_dict[client_name]
                    text = " ".join(split_message[2:])
                    message = f"{client_name} -> {destination}: {text}"
                    print(message, end="")
                    sys.stdout.flush()
                    destination_socket.sendall(message.encode("utf-8"))
                    source_socket.sendall(message.encode("utf-8"))
            else:
                remove_client(client_name, socket)
                break
        except:
            remove_client(client_name, socket)
            break

def remove_client(name, socket):
    if name in client_dict:
        client_dict.pop(name)
        message = f"{name} left the chatroom\n"
        broadcast(message)
        socket.close()
    
def broadcast(message):
    print(message, end="")
    sys.stdout.flush()

    for name, socket in client_dict.items():
        try:
            socket.sendall(message.encode("utf-8"))
        except:
            remove_client(name, socket)


while True:
    connSock, addr = sock.accept()
        
    client_thread = threading.Thread(target=handle_client, args=(connSock,), daemon=True)
    client_thread.start()
