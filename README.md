TCP and UDP Socket Programming

This project includes a server and a client for setting up and managing peer-to-peer (P2P) chat connections. It is designed to allow multiple clients to register with the server, discover other available clients, and communicate directly via UDP messaging.


Installation

To run this prject you need Python3.


Configuration

The IP address for both the server and client scripts is hardcoded. Please update the SERVER variable in both the server.py and client.py files to match the IP address of the machine where the server will be running.


Port Configuration

The server listens on a specified port, and clients will use this port for the initial TCP connection. The default port is set to 9090 but can be changed if necessary.


Running the Server

To start the server, run the server.py script. This will start listening for incoming client connections.


Running the Client

Run the client.py script on a separate terminal or machine (with network access to the server).


Features

Registration

Clients must register with the server upon connection by providing a unique nickname. If the nickname is already taken, the server will request a new one.


Client Discovery

Clients can request a list of all connected clients from the server. This list includes nicknames and the address information necessary for establishing a P2P connection.


P2P Messaging

After discovering available clients, a user can initiate a P2P chat by querying the server for a specific client's details and then sending messages directly using UDP.
Note that a querying client is immediately able to send messages to the queried client once it has connected. However, if the queried client wants to send messages back, it must also connect to said querying client. Once both clients have explicitly connected to each other, they can exchange messages.


Commands

List Clients: Retrieve and display all currently connected clients.
Query Client: Request the connection details for a specific client to start a P2P chat.
Exit: Disconnect from the server cleanly.


Example Usage

Start the server.
Connect multiple clients.
Register each client with a unique nickname.
List clients to see who is online.
Query a client and start a P2P chat session.


CLosing Connections

To exit the chat or the application, type Exit in the client script, which will notify the server and close the connection properly.

