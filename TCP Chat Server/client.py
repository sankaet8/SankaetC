import sys
import socket
import threading
import datetime
import os

# python3 -u server.py <port> <password>

# python3 -u client.py <host> <port> <password> <name>

host = str(sys.argv[1])
port = int(sys.argv[2])
password = str(sys.argv[3])
name = str(sys.argv[4])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(f"Connecting to {host} on port {port}...")

sock.connect((host, port))
#-------------------- The connection to the server has now been established ---------------#

sock.send((password + '\n').encode("utf-8")) # sends the password to be verified by server

sock.send((name + '\n').encode("utf-8")) # sends the name to be used in server
try:
    greeting = sock.recv(1024).decode("utf-8")
except:
    #print("Password was incorrect")
    os._exit(1)

print(greeting, end="")
#-------------------- We have now joined the server properly---------------#

def receive_messages(socket):
    while not exitFlag.is_set():
        try:
            chatmessage = socket.recv(1024).decode("utf-8")
            if not chatmessage:
                os._exit(1)
            print(chatmessage, end="")
        except ConnectionResetError:
            #print("Connection lost")
            os._exit(1)
        except OSError as e:
            # this is bad file error
            if e.errno == 9:
                break

def send_messages(socket):
    while True:
        message = input()
        if message == ":Exit":
            break
        elif message == ":)":
            message = "[feeling happy]"
        elif message == ":(":
            message = "[feeling sad]"
        elif message == ":mytime":
            current_time = datetime.datetime.now().strftime("%H:%M on %a, %d %b, %Y")
            message = f"It's {current_time}."
        
        try:
            socket.send((message + '\n').encode("utf-8"))
        except:
            os._exit(1)
    exitFlag.set()
    socket.close()
    os._exit(0)

exitFlag = threading.Event()

receive_thread = threading.Thread(target=receive_messages, args=(sock,))

receive_thread.start()

send_messages(sock)

sock.close()

