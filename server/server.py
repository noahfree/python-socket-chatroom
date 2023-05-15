import os
import socket
import threading

# NAME: Noah Free
# DATE: 2/24/2023
# DESCRIPTION: This is the server code for a socket chat room application. This server allows clients to connect to it by using the server and port
#              information below. It then accepts commands from each client to create a new user, login with an existing user, log out, send messages
#              in the chat room, send direct messages to other users in the room, and see who all is in the chat room. All possible input errors are
#              taken care of, so only valid requests are processed.

# constants are defined for the server information
HEADER = 64
PORT =  14934
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

# a socket is created and binded to the server information above when the program is started
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# a list of users and a dictionary of connections are created to keep track of the created users and the current client connections
users = []
connections = {}

# send function called to send a message to a client
def send(conn, msg):
  # encode the message
  message = msg.encode(FORMAT)
  # get the length of the message
  msgLength = len(message)
  # encode the message length
  sendLength = str(msgLength).encode(FORMAT)
  # pad message length with spaces
  sendLength += b' ' * (HEADER - len(sendLength))
  # send both message and message length
  conn.send(sendLength)
  conn.send(message)

# handleClient handles message sent from each client
def handleClient(conn, addr):
  # currentUser shows whether a user is logged in or not
  currentUser = None

  while True:
    # first receive the length of the message from the client
    msgLength = conn.recv(HEADER).decode(FORMAT)
    if msgLength:
      # next use the message length to receive the entire message from the client
      msg = conn.recv(int(msgLength)).decode(FORMAT)
      # if the message equals the disconnect message, handle the client disconnecting and break out of the while True loop
      if msg == DISCONNECT_MESSAGE:
        # remove current connection from connections list
        connections.pop(addr)
        # if user was sign in, send logout/leaving messages to themself and anyone logged in
        if currentUser:
          send(conn, f"{currentUser} logout.")
          for connection in connections:
            if connections[connection][1]:
              send(connections[connection][0], f"{username} left.")
          print(f"{currentUser} logout.")
        send(conn, "\n\nDisconnected from server.\n")
        break;

      try:
        # split the received string by spaces
        splitMsg = msg.split(" ")
        # set command equal to the first item in the list
        command = splitMsg[0]

        # handle the newuser command
        if command == "newuser":
          # validate that the number of items in the message is correct
          if len(splitMsg) != 3:
            raise Exception()
          # unable to create a current user while logged in
          elif currentUser:
            send(conn, "Please logout to create a new user.")
          else:
            try:
              # get username and password from split message
              username = splitMsg[1]
              password = splitMsg[2]
              usernameExists = False
              # for loop sets usernameExists to true if the given username already exists
              for user in users:
                if user[0] == username:
                  usernameExists = True
                  break
              # handle username exists
              if usernameExists:
                send(conn, "Denied. User account already exists.")
              # handle success case
              else:
                # append username and password to users list
                users.append((username, password))
                # send/print success messages
                send(conn, "New user account created. Please login.")
                print("New user account created.")
            # handle error
            except:
              send(conn, f"Error parsing command.")

        # handle the login command
        elif command == "login":
          # validate that the number of items in the message is correct
          if len(splitMsg) != 3:
            raise Exception()
          # unable to login when user is already logged in
          elif currentUser:
            if splitMsg[1] == currentUser:
              send(conn, "Denied. Already signed in.")
            else:
              send(conn, "Denied. Please sign out to switch to a different user.")
          else:
            try:
              # get username and password from split message
              username = splitMsg[1]
              password = splitMsg[2]
              userFound = False
              # use a for loop to search for the user in the users list
              for user in users:
                if user[0] == username:
                  if user[1] == password:
                    # send/print success messages
                    send(conn, "login confirmed")
                    # send the joined message to each client that is logged in
                    for connection in connections:
                      if connections[connection][1]:
                        send(connections[connection][0], f"{username} joined.")
                    # if username and password match, set current user in both places
                    currentUser = user[0]
                    connections[addr][1] = user[0]
                    print(f"{currentUser} login.")
                    userFound = True
                  # handle incorrect password
                  else:
                    send(conn, "Denied. User name or password incorrect.")
                    userFound = True
              # handle username not found
              if not userFound:
                  send(conn, "Denied. User name or password incorrect.")
            # handle error
            except:
              send(conn, f"Error parsing command.")

        # handle the send command
        elif command == "send":
          # handle user not being logged in
          if not currentUser:
            send(conn, "Denied. Please login first.")
          else:
            # get all text after the 'send' commang
            text = msg.split(" ", 1)[1]
            sendTo = text.split(" ", 1)[0]
            content = text.split(" ", 1)[1]

            if sendTo == 'all':
              # construct output string using current user and text
              output = f"{currentUser}: {content}"
              # send the message to each client that is logged in and not the currentUser
              for connection in connections:
                if connections[connection][1] and connections[connection][1] != currentUser:
                  send(connections[connection][0], output)
              # print output to server terminal
              print(output)
            else:
              # construct output string using current user and text
              output = f"{currentUser}: {content}"
              userFound = False
              # for every connection, look for the user specified in the command
              for connection in connections:
                if connections[connection][1] == sendTo:
                  # in case the user is logged in multiple times, only print the server message once
                  if not userFound:
                    print(f"{currentUser} (to {connections[connection][1]}): {content}")
                  # toggle userFound
                  userFound = True
                  # send the message to the specified user
                  send(connections[connection][0], output)
              # if the user was not found, return Denied message to user who sent the request
              if not userFound:
                send(conn, f"Denied. User {sendTo} is not in the chat room.")

        # handle the who command
        elif command == "who":
          # handle user not being logged in
          if not currentUser:
            send(conn, "Denied. Please login first.")
          else:
            # first set who to None
            who = None
            for connection in connections:
              # for each addr, if the second value at the addr in the dictionary exists, then that user is logged in
              if connections[connection][1]:
                # set who equal to the username, or append to the string
                if who == None:
                  who = f"{connections[connection][1]}"
                else:
                  who += f", {connections[connection][1]}"
            # send the who string back to the user who requested it
            send(conn, who)

        # handle the logout command
        elif command == "logout":
          # validate that the number of items in the message is correct
          if len(splitMsg) != 1:
            raise Exception()
          # unable to log out when already logged out
          if not currentUser:
            send(conn, "Denied. Already logged out.")
          else:
            connections[addr][1] = None
            # send the logout message to each client that is logged in
            for connection in connections:
              if connections[connection][1]:
                send(connections[connection][0], f"{username} left.")
            # send/print success messages
            send(conn, "logged out")
            print(f"{currentUser} logout.")
            # set current user back to None
            currentUser = None

        # handle an unrecognized command
        else:
          send(conn, "Denied. Unrecognized request.")

      # handle error
      except:
        send(conn, f"Error parsing command.")

  # close the connection when the client sends the disconnect message
  conn.close()

def start():
  # the server is listening for clients
  server.listen()
  while True:
    # each time a client connects to the server, it is first accepted and the given conn and addr are saved in variables
    conn, addr = server.accept()
    # the given conn and addr are added to the connections dictionary to; None shows that no user is logged in for the given connection
    connections[addr] = [conn, None]
    # a thread is created for the given client, passing the given conn and addr to the handle function
    thread = threading.Thread(target=handleClient, args=(conn, addr))
    # start the client thread
    thread.start()

def main():
  # if the text file 'users.txt' exists, then open the file, read the lines, and for each item in the file parse the data
  if os.path.exists("users.txt"):
    with open("users.txt", "r") as file:
      userStrings = file.readlines()
      for user in userStrings:
        try:
          # the username and password are parsed and then added to the users list as a tuple
          userNameAndPassword = user.strip("()\n ").split(", ")
          username = userNameAndPassword[0]
          password = userNameAndPassword[1]
          users.append((username, password))
        except:
          continue
      file.close()
  try:
    print("\nMy chat room server. Version Two.\n")
    # start the server, allowing it to listen for clients
    start()

  finally:
    # when the server is terminated, if there is at least one user present in the list, then loop through the users and write each user to the text file 'users.txt'
    if len(users):
      with open("users.txt", "w") as file:
        for user in users:
          file.write(f"({user[0]}, {user[1]})\n")
        file.close()

# call main
main()
