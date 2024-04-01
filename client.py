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

# Client's registration process
# Starts a thread for listening to incoming UDP messagess
def register_client_loop():
    global listen_port
    while True:
        try:
            nickname = input("Enter nickname: ").lower()  # nickname to lower for consistency
            response = send_and_return(f"{REGISTER}{nickname}")  # return 'NAME_TAKEN' if not successful

            if "NAME_TAKEN" in response:
                print("Nickname is already taken, please choose another.")
                continue  # re-enter loop
            else:
                print(response)
                listen_port = int(response.split(':')[-1].strip())
                threading.Thread(target=listen_for_peers, daemon=True).start()
                break
        except Exception as e:
            print(f"An error occurred during registration: {e}")

# Listens for incoming UDP messages from peers and prints them
def listen_for_peers():
    global is_in_chat_mode
    if listen_port is not None:
        udp_socket.bind(("0.0.0.0", listen_port))  # Bind to the provided port
        print(f"Listening for messages on port {listen_port}...")
    while True:
        try:
            message, addr = udp_socket.recvfrom(1024)  # Buffer size is 1024 bytes
            print(f"Message from {addr}: {message.decode()}")
        except socket.error as e:
            print("Error receiving message: The server may have stopped.")
            is_in_chat_mode = False
            # Perform necessary cleanup
            client.close()
            break
# Sends a UDP message to a specified peer
def send_message_to_peer(ip, port, msg):  # send message to peer
    try:
        udp_socket.sendto(msg.encode(), (ip, int(port)))
    except socket.error as e:
        print(f"Failed to send message to {ip}:{port} due to socket error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while sending message to {ip}:{port}: {e}")


# Handles querying the server for a specific client's details
# Initiates P2P chat session and sending messages via UDP
def query_client():
    global has_requested_list, is_in_chat_mode
    try:
        if has_requested_list:  # Check the flag before allowing the query
            nickname = input("Input name of client you would like to connect with: \n").lower()
            response = send_and_return(f"{QUERY_CLIENT}{nickname}")
            if "Client not found" not in response:
                peer_ip, peer_port = response.split(":")
                print(f"Starting chat with *** {nickname} *** You can now send messages. Type 'Exit' to stop.")
                is_in_chat_mode = True
                while is_in_chat_mode:
                    message = input(">>> ")
                    if message.lower() == DISCONNECT_MESSAGE.lower():
                        is_in_chat_mode = False
                    else:
                        try:
                            send_message_to_peer(peer_ip, peer_port, message)
                        except Exception as e:
                            print(f"An error occurred while sending message: {e}")
                            break  # Exiting chat mode on error, but you can choose to handle this differently.
            else:
                print(response)
        else:
            print("Please request and view the list of available clients first.")
    except Exception as e:
        print(f"An error occurred during querying client: {e}")


# Main loop for client to interact with server
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
