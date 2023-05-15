import socket
import threading

# NAME: Noah Free
# DATE: 2/24/2023
# DESCRIPTION: This is the client code for a socket chat room application. This client automatically connects to the given server and then allows the user
#              to input commands to create a new user, login with an existing user, log out, send messages in the chat room, send direct messages, and see
#              who is in the chat room. Username and password lengths are validated on the client as well as message lengths. The client is constantly listening
#              for message to print from the server

# constants are defined for the server information
HEADER = 64
PORT =  14934
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)

# a socket is created and connected to the given ADDR from the constants defined above when the program is started
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

# function receive receives from the server first the length of a message being received followed by the message itself
def receive():
  msgLength = client.recv(HEADER).decode(FORMAT)
  if msgLength:
    msg = client.recv(int(msgLength)).decode(FORMAT)
    print(msg)

# listener does nothing else besides listen for messages from the server, calling the function above
def listener():
  while True:
    receive()

# the send function accepts a string, encodes it, and sends both the length of the string and the string itself to the server
def send(msg):
  # encode the message
  message = msg.encode(FORMAT)
  # get the length of the message
  msgLength = len(message)
  # encode the message length
  sendLength = str(msgLength).encode(FORMAT)
  # pad message length with spaces
  sendLength += b' ' * (HEADER - len(sendLength))
  # send both message and message length
  client.send(sendLength)
  client.send(message)

# the main function accepts inputs from the user and calls the methods above
def main():
  print("\nMy chat room client. Version Two.\n")

  try:
    # a thread is created in order to listen for and print messages from the server
    thread = threading.Thread(target=listener)
    thread.start()

    # a while True loop is used to continually accept input from the user
    while True:
      # string is set equal to what the user inputs in the terminal
      string = input()
      # splitMsg splits the string by spaces
      splitMsg = string.split(" ")
      # command is set to the first item in the inputted string
      command = splitMsg[0]

      # if the user is creating a new user, then the username and password need to be validated
      if command == 'newuser':
        if len(splitMsg) != 3:
          print("Denied. Error parsing request.")
          continue
        elif len(splitMsg[1]) < 3:
          print("Denied. Username is too short.")
          continue
        elif len(splitMsg[1]) > 32:
          print("Denied. Username is too long.")
          continue
        elif len(splitMsg[2]) < 4:
          print("Denied. Password is too short.")
          continue
        elif len(splitMsg[2]) > 8:
          print("Denied. Password is too long.")
          continue

      # if the user is logging in, then the number of items in the inputted string should be 3
      elif command == 'login':
        if len(splitMsg) != 3:
          print("Denied. Error parsing request.")
          continue

      # if the user is sending a message, then the number of items should be 2 or greater, and the message length needs to be validated
      elif command == 'send':
        if len(splitMsg) < 3:
          print("Denied. Error parsing request.")
          continue
        text = string.split(" ", 2)[2]
        if len(text) < 1:
          print("Denied. Message is too short.")
          continue
        if len(text) > 256:
          print("Denied. Message is too long.")
          continue

      # if the user is requesting who, then the number of items should be 1
      elif command == 'who':
        if len(splitMsg) != 1:
          print("Denied. Error parsing request.")
          continue

      # if the user is logging out, then the number of items should be 1
      elif command == 'logout':
        if len(splitMsg) != 1:
          print("Denied. Error parsing request.")
          continue

      # else is a catch all which prints out a message for any command not recognized
      else:
        print("Denied. Unrecognized request.")
        continue

      send(string)

  # when the client program terminates, a disconnect message is sent to the server to disconnect the given client
  finally:
    send(DISCONNECT_MESSAGE)

# call main
main()
