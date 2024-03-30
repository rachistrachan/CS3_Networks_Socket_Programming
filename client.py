# *** in order for two clients to exchange messages, each one needs to connect to the other ***
# STRRAC002
# Rachel Strachan
# CSC3002F
# remember to hardcode you IP address
import socket
import threading
import time

# flag to control flow of program
is_in_chat_mode = False

# Define the server address and port
SERVER = "192.168.1.57"  # enter in your IP address (hardcoded)
PORT = 9090
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
HEADER = 64
# Constants for message formatting and commands.
DISCONNECT_MESSAGE = "Exit"
LIST_CLIENTS_COMMAND = "List_Clients!"
REGISTER = "Enter nickname:"
QUERY_CLIENT = "Query:"

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listen_port = None
# Initialize the client TCP socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
has_requested_list = False  # flag so that client's need to list available clients before querying

# Send message to server using TCP.
# Message length first then actual message.
def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    try:
        client.send(send_length)
        client.send(message)
        response = client.recv(2048).decode(FORMAT)
        print(response)
    except socket.error as e:
        print("The server has stopped. Please try again later.")
        # Optionally, perform cleanup here, like closing the socket.
        client.close()


# Send message to server using TCP.
# Message length first then actual message. Returns value.
def send_and_return(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    try:
        client.send(send_length)
        client.send(message)
        response = client.recv(2048).decode(FORMAT)
        return response
    except socket.error as e:
        print("The server has stopped. Please try again later.")
        # Optionally, perform cleanup here, like closing the socket.
        client.close()


# Main loop for client to interact with server
def register_client_loop():
    pass


def query_client():
    pass


def start():
    global is_in_chat_mode, has_requested_list
    try:
        print(f"Connected to the server at {SERVER}.")
        register_client_loop()  # call register function

        while True:
            if not is_in_chat_mode:
                try:
                    msg = input("Menu: (1) List available clients (2) Query client (3) exit. \n").lower()

                    if msg == '1':
                        send(LIST_CLIENTS_COMMAND)
                        has_requested_list = True

                    elif msg == '2':
                        query_client()
                        # Wait for chat session to end before showing menu again
                        while is_in_chat_mode:
                            time.sleep(1)

                    elif msg == '3':
                        send(DISCONNECT_MESSAGE)
                        break

                    else:
                        print("Invalid option, please try again.")
                except Exception as e:
                    print(f"An error occurred while processing the command: {e}")
                    continue
    except Exception as e:
        print(f"An error occurred initializing the client loop: {e}")


if __name__ == "__main__":
    try:
        start()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.close()
        udp_socket.close()
