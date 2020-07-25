import socket
import select


def run_server():
    """
    Start a server to facilitate the chat between clients.
    The server uses a single socket to accept incoming connections
    which are then added to a list (socket_list) and are listened to
    to recieve incoming messages. Messages are then stored in a database
    and are transmitted back out to the clients.
    """

    # Define where the server is running. 127.0.0.1 is the loopback address,
    # meaning it is running on the local machine.
    host = "127.0.0.1"
    port = 5000
  
    # Create a socket for the server to listen for connecting clients
    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(10)

    # Create a list to manage all of the sockets
    socket_list = []
    # Add the server socket to this list
    socket_list.append(server_socket)

    # create nickname dictionary of sockets to user nicknames
    nicknames = {}


    print("Server running on port: %i" % (port))

    # Start listening for input from both the server socket and the clients
    while True:

        # Monitor all of the sockets in socket_list until something happens
        ready_to_read, ready_to_write, in_error = select.select(socket_list, [], [], 0)

        # When something happens, check each of the ready_to_read sockets
        for sock in ready_to_read:
            # A new connection request recieved
            if sock == server_socket:
                # Accept the new socket request
                sockfd, addr = server_socket.accept()
                # Add the socket to the list of sockets to monitor
                socket_list.append(sockfd)
                nicknames.update({sockfd.getpeername()[1] : None})
                # Log what has happened on the server
                print ("Client (%s, %s) connected" % (addr[0], addr[1]))
                # send back a welcome message
                msg = ("SERVER: Welcome to the Python Chat Service. For help and commands type '/HELP'")
                sockfd.send(msg.encode())

            # A message from a client has been recieved
            else:
                # Extract the data from the socket and iterate over the socket_list
                # to send the data to each of the connected clients.
                data = sock.recv(1024).decode()
                if(len(data) == 0):
                    break
                else:
                    print("%s sent msg : %s" % (sock.getpeername()[1], data))

                # format a message
                msg = ("%s" % (str(data)))
                message = ""

                # checking for input commands
                words = data.split()
                first_word = words[0].upper()
                # checking a second input word exists
                if(len(words) < 2):
                    second_word = None
                else:
                    second_word = words[1]
                    # record the message
                    for word in words[2:]:
                        message += word

                # CHECKING FOR INPUT COMMANDS
                # Help command will return a simple help message
                if(str(first_word) == "/HELP"):
                    help_msg = ("SERVER: welcome to the python chat system, simply type " +
                                 "and send messages to the chat room and see the responces" +
                                  "\n commands; /Help, /Who, /Nick <name>, /MSG <recipient_nickname>")
                    # send message back to client and break
                    sock.send(help_msg.encode())
                    break
                # Exit command will disconnect the client
                if(str(first_word) == "/EXIT"):
                    name = sock.getpeername()[1]
                    sock.send("Disconnecting...".encode())
                    # TO-DO: implement socket disconnection
                    # sock.close()
                    print("socket: " + str(name) + " disconnected by client")
                    break
                # Msg command is used for private messaging other users
                if(str(first_word) == "/MSG"):
                    priv_msg = ""
                    if(second_word == None):
                        # error message if name parameter not present/entered
                        priv_msg = ("SERVER: command must be in format: /MSG <recipient_nickname> message... ")
                    else:
                        if(second_word not in nicknames.values()):
                            # error message if the nickname cant be found
                            priv_msg = ("SERVER: recipient_nickname entered does not exit on server")
                        else:
                            priv_port = 0
                            #find the port of the message recipient
                            for key in nicknames:
                                # nickname matches entered name
                                if(str(nicknames[key]) == str(second_word)):
                                    priv_port = key
                            #find the recipient socket
                            for soc in socket_list:
                                # dont sent to server_socket
                                if(soc != socket_list[0]):
                                    # only send the message to the recipient
                                    if(soc.getpeername()[1] == priv_port):
                                        # format the private message
                                        name = nicknames[priv_port]
                                        message = ("Private message from %s: %s" % (name, message))
                                        soc.send(message.encode())
                    # send a confirm message back to the client then break
                    sock.send(priv_msg.encode())
                    break
                # Who command returns a list of all connected clients
                if(str(first_word) == "/WHO"):
                    who_msg = "SERVER: List of all users nicknames; "
                    count = 0
                    # iterate over all nicknames in server
                    for key, val in nicknames.items():
                        if(val is not None):
                            # add nick names to message
                            who_msg += (val + " ")
                        else:
                            # count unnamed users
                            count += 1
                    if(count > 0):
                        who_msg += (": %i unnamed user(s) " % (count))
                    # send message back to client and break
                    sock.send(who_msg.encode())
                    break
                # Nick command is used for setting a clients nickname on the server
                if(str(first_word) == "/NICK"):
                    nick_msg = ""
                    if(second_word == None):
                        # error message if name parameter not present
                        nick_msg = ("SERVER: command must be in format: /NICK <nickname> ... ")
                    else:
                        # get user socket port
                        sock_id = sock.getpeername()[1]
                        # update nicknames to include users nickname
                        nicknames.update({ sock_id : second_word })
                        nick_msg = ("SERVER: Nickname now set to %s " % (second_word))
                    # send message back to client and break
                    sock.send(nick_msg.encode())
                    break

                # adding user nickname to outgoing message
                for key, val in nicknames.items():
                    if key == sock.getpeername()[1]:
                        if(val is not None):
                            msg = str(val + ": " + msg)
                        else:
                            msg = str("unnamed" + str(key) + ": " + msg)


                # send the message to all connected clients except the sender
                for res_soc in socket_list:
                    if(res_soc != socket_list[0] and res_soc != sock):
                        res_soc.send(msg.encode())

# main method starts running the server
if __name__ == '__main__':
    run_server()