# TCP with Multithreading
# Group 35 Server
# remember to hardcode you IP address
import socket
import threading

# specifying length of next message that will be sent
HEADER = 64
# PORT = 5050
PORT = 9090
# At the top of your server script
BASE_LISTEN_PORT = 55000  # Starting port for P2P connections
current_port = BASE_LISTEN_PORT
# get IP address of this computer
SERVER = "192.168.1.57"  # enter in your IP address (hardcoded)
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
# commands that server recognizes for specific actions
DISCONNECT_MESSAGE = "Exit"
LIST_CLIENTS_COMMAND = "List_Clients!"
REGISTER = "Enter nickname:"
QUERY_CLIENT = "Query:"
# directory to store client information
clients = {}  # clients by nickname

# create server object
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bound socket to address
server.bind(ADDR)

# Handles incoming messages from clients
# Processes commands (register, disconnect, query client, list clients)
def handle_client(conn, addr):
    print(f"New client {addr} connected.")
    connected = True
    nickname = None

    while connected:
        try:
            # Attempt to read the message length and then the message itself
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)

                if msg.startswith(REGISTER): # user input
                    nickname = register_client(msg, conn, addr)
                    if nickname is None:  # Registration failed
                        continue

                elif msg == DISCONNECT_MESSAGE: # user input
                    disconnect_clients(conn, addr, nickname)
                    connected = False

                elif msg.startswith(QUERY_CLIENT): # user input
                    query_client(msg, conn)

                elif msg == LIST_CLIENTS_COMMAND: # user input
                    list_clients(conn)
        except socket.timeout:
            print(f"Timeout: Client {addr} did not send data in time.")
            break  # Exit the loop and close the connection

    # After the loop is exited, either due to an error or a disconnect message
    if nickname:
        print(f"Client {nickname} ({addr}) disconnected.")
    else:
        print(f"Client {addr} disconnected.")
    conn.close()


# Registers new client with server
# If name already taken, prompts for new one and adds to dictionary
def register_client(msg, conn, addr):
    global current_port
    try:
        nickname = msg[len(REGISTER):]
        if nickname in clients:
            # Inform client nickname is in use
            conn.send("NAME_TAKEN".encode(FORMAT))
            # Registration failed, return None to indicate failure
            return None
        else:
            # Register the client
            clients[nickname] = (addr[0], addr[1], conn)  # Map nickname to address
            conn.send(f"*** {nickname} *** registered successfully. Listening port: {addr[1]}".encode(FORMAT))
            return nickname  # Return registered nickname
    except Exception as e:
        print(f"An error occurred during client registration: {e}")
        # Attempt to inform the client about the registration error
        try:
            conn.send("REGISTRATION_ERROR".encode(FORMAT))
        except Exception as send_error:
            print(f"Failed to send registration error message to client: {send_error}")
        return None  # Return None to indicate that registration failed


# Disconnects a client from the server
# Removes the client from the clients dictionary and closes the connection
def disconnect_clients(conn, addr, nickname=None):
    if nickname:
        print(f"{nickname} disconnected.")
        # Safely attempt to remove the client, checking if the nickname exists
        if nickname in clients:
            del clients[nickname]  # Remove client from clients list on disconnect
        else:
            print(f"Attempted to disconnect non-existing client with nickname: {nickname}")
    else:
        print(f"{addr} disconnected.")

    # Attempt to close the connection
    conn.close()
# Sends a list of all connected clients to the requesting client
def list_clients(conn):
    try:
        list_of_clients = "\n ".join([f"{nickname} ({addr[0]}:{addr[1]})" for nickname, addr in clients.items()])
        # Send back the list of connected clients with their nicknames and addresses
        conn.send(f"Connected Clients: \n {list_of_clients}".encode(FORMAT))
    except socket.error as e:
        print(f"Failed to send list of clients due to socket error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while sending list of clients: {e}")

# main function that starts the server listening for incoming connections
# Accepts connections: starting a new thread to handle each client
def start():
    try:
        server.listen()
        print(f"Server is listening on {SERVER}")

        while True:
            try:
                # Waiting for a new connection to the server
                conn, addr = server.accept()

                # Create a new thread for each client connection
                try:
                    thread = threading.Thread(target=handle_client, args=(conn, addr))
                    thread.start()
                    print(f"Active connections {threading.activeCount() - 1}")
                except Exception as e:
                    print(f"Failed to start a thread for client {addr}: {e}")
                    conn.close()  # Ensure the connection is closed if thread couldn't start

            except socket.error as e:
                print(f"Socket error occurred while accepting a connection: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

    except Exception as e:
        print(f"An error occurred when starting the server: {e}")


print("Server is starting...")
# Attempt to start the server
try:
    start()
except KeyboardInterrupt:
    print("Server shutdown requested. Closing...")
    # Add any cleanup here before exiting
    server.close()  # Close the listening socket
    # Optionally, inform connected clients about the shutdown
    # and perform any additional cleanup needed.
    print("Server has been shut down.")
