import socket
import hashlib

SERVER_IP = "127.0.0.1"
SERVER_PORT = 447
FIRST_LETTER_INDEX = 4
PARAMETERS_JOIN_KEY = ":"
ACCESS_GRANTED_IDENTIFIER = "209"
REQUESTS = {
    "albums": 101,
    "album songs": 102,
    "song length": 103,
    "song lyrics": 104,
    "song album": 105,
    "search song by name": 106,
    "search song lyrics": 107,
    "quit": 108,
    "password": 109
}
PROMPTS = {
    REQUESTS["album songs"]: "Enter album name: ",
    REQUESTS["song length"]: "Enter song name: ",
    REQUESTS["song lyrics"]: "Enter song name: ",
    REQUESTS["song album"]: "Enter song: ",
    REQUESTS["search song by name"]: "Enter text: ",
    REQUESTS["search song lyrics"]: "Enter text: "
}
BUFFER_SIZE = 4096
"""
I made an explanation of the different errors I catch in all of the codes:
    KeyboardInterrupt- when the user does something with his keyboard
      that makes the code crash like control + c or d.
      I learned about it while trying to make the server crash and investigated
      here: https://stackoverflow.com/questions/37887624/python-3-keyboardinterrupt-error
    ValueError- when the user enters something invalid for a function like entering a string
      for an int input. I learned about it from the presentation
    ConnectionRefusedError- when the client tries to connect to the server but the port is
      closed which is making ConnectionRefusedError rise. I learned about it here:
      https://www.pico.net/kb/what-is-a-tcp-connection-refused/#:~:text=In%20general%2C%20connection%20refused%20errors,port%20which%20is%20not%20open.
    AttributeError- when an action is being made on a variable that isn't the right type
      for example declaring x as "a" and then trying to use actions like .append() or .sort() on it.
      I learned it here: https://www.geeksforgeeks.org/python-attributeerror/
    TypeError- when trying to use a value that's not fitting for that variable type for example
      x = 4 + "a". I learned it here: https://last9.io/blog/types-of-errors-in-python/#:~:text=TypeError%3A%20Raised%20when%20an%20operation,dictionary%20that%20doesn't%20exist.
    IndexError- when trying to access an index that doesn't exist in a list, for example: list_a = [1, 2] and then print(list_a[3]). I learned
      it here: https://www.geeksforgeeks.org/python-list-index-out-of-range-indexerror/
    ConnectionResetError- when one of the sides in the tcp socket closes the connection and then the other side tries to receive or send messages. I learned
      it while trying to make the server and client crash
    EOFError: when reaching end of line before finishing reading input. I learned it here: https://www.geeksforgeeks.org/handling-eoferror-exception-in-python/Magsh1m!m#Magsh1m!m#
"""


def show_menu_and_get_action_input():
    """
    Displays the server's menu, gets an action input, and converts
    it to the valid format according to the Yoav protocol (7 -> 107)
    :return: The action input in the correct format
    :rtype: int
    """
    print("1 Get Albums")
    print("2 Get Album Songs")
    print("3 Get Song Length")
    print("4 Get Song Lyrics")
    print("5 Get Song Album")
    print("6 Search Song by Name")
    print("7 Search Song by Lyrics")
    print("8 Quit")
    try:
        action = int(input("Enter number: "))
        while action > 8 or action < 1:
            action = int(input("action not in menu!\nPlease choose again: "))
        action = 100 + action
        return action
    except (KeyboardInterrupt, ValueError, EOFError):
        print("\nError in input process")


def get_input_according_to_action_choice(action):
    """
    Gets input according to action choice
    :param action: the action choice
    :type action: int
    :return: the search parameters
    :rtype: str
    """
    try:
        parameters = ""
        # # There is no special input needed for 1 and 8
        # if action == REQUESTS["album songs"]:
        #     parameters = input("Enter album name: ")
        # # Same input for both "song length" and "song lyrics"
        # elif action == REQUESTS["song length"] or action == REQUESTS["song lyrics"]:
        #     parameters = input("Enter song name: ")
        # elif action == REQUESTS["song album"]:
        #     parameters = input("Enter song: ")
        # # Same input for both "search song by name" and "search song lyrics"
        # elif action == REQUESTS["search song by name"] or action == REQUESTS["search song lyrics"]:
        #     parameters = input("Enter text: ")
        # while not parameters:
        #     parameters = input("You didn't enter anything. Please try again: ")
        if action in PROMPTS:
            parameters = input(PROMPTS[action])
        return parameters
    except (KeyboardInterrupt, ValueError, EOFError):
        print("\nError in input process")


def check_recv_success(msg):
    """
    Checks if the recv function has managed to recover
    something
    :param msg: the msg to check
    :type msg: str
    :return: False if the msg is null (recv failed), True otherwise
    :rtype: bool
    """
    if msg:
        return True
    else:
        return False


def print_server_disconnected_msg():
    """
    Prints an error message in case the server disconnected
    :return: none
    """
    print("Server unexpectedly disconnected, closing the connection.")


def print_msg_without_identifier(msg):
    """
    Prints a server message without its action code prefix.
    :param msg: Full message received from the server
    :type msg: str
    """
    print(msg[FIRST_LETTER_INDEX:], "\n")


def get_password_and_hash(sock):
    """
    Receives a password from the user, hashes it with SHA256, and sends it to the server
    for authentication. Prints the server's response and returns whether access was granted.
    :param sock: The active socket connected to the server
    :type sock: socket.socket
    :return: True if access was granted, False otherwise
    :rtype: bool
    """
    try:
        password = input("Please enter the password: ")
        hashed_pass = hashlib.sha256(password.encode()).hexdigest()
        # In this line .encode() converts the password to bytes, sha256 creates
        # an object from the bytes and hex digest converts it back to str so
        # that we can use it
        # I learned it here: https://www.geeksforgeeks.org/sha-in-python/
    except (KeyboardInterrupt, ValueError, TypeError, ConnectionResetError, EOFError) as e:
        print("\nError in input process:", e)
        return False
    try:
        msg = build_msg(REQUESTS["password"], hashed_pass)
        sock.sendall(msg.encode())
        server_msg = sock.recv(BUFFER_SIZE)
        server_msg = server_msg.decode()
        if check_recv_success(server_msg):
            print_msg_without_identifier(server_msg)
            return ACCESS_GRANTED_IDENTIFIER in server_msg
    except ConnectionResetError:
        print_server_disconnected_msg()
        return False


def build_msg(action, parameters):
    """
    Builds a protocol message from the action and parameters.
    :param action: The action code to send
    :type action: int
    :param parameters: The parameters for the request
    :type parameters: str
    :return: A formatted message string
    :rtype: str
    """
    return str(action) + PARAMETERS_JOIN_KEY + parameters


def pink_floyd_server_conversation():
    """
    This is the main function of the code, it opens a socket with the server, retrieves
    and prints the welcome message, uses another function to get the action input and then
    sends it to the server, it will do it until the client has requested to stop.
    """
    # Connecting to the server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (SERVER_IP, SERVER_PORT)
    try:
        sock.connect(server_address)
    except ConnectionRefusedError:
        print("Error while trying to connect to the server")
        # I am using this return line to quit the function in case I didn't manage to connect
        # to the server because the function won't continue running after the return line
        return
    if not get_password_and_hash(sock):
        return
    welcome_msg = sock.recv(BUFFER_SIZE)
    welcome_msg = welcome_msg.decode()
    if check_recv_success(welcome_msg):
        print(welcome_msg)
    else:
        print_server_disconnected_msg()
        return
    action = 0
    while action != REQUESTS["quit"]:
        action = show_menu_and_get_action_input()
        # If there was an error while trying to get input the function will not
        # return anything which means action in null and in that case we need to get out of the function
        if not action:
            sock.close()
            break
        req_parameters = ""
        if action != REQUESTS["albums"] and action != REQUESTS["quit"]:
            req_parameters = get_input_according_to_action_choice(action)
            if not req_parameters:
                sock.close()
                break
        client_msg = build_msg(action, req_parameters)
        try:
            sock.sendall(client_msg.encode())
            server_msg = sock.recv(BUFFER_SIZE)
            server_msg = server_msg.decode()
            if check_recv_success(server_msg):
                print_msg_without_identifier(server_msg)
            else:
                print_server_disconnected_msg()
                sock.close()
                break
        except ConnectionResetError:
            print_server_disconnected_msg()
            sock.close()
            break
    sock.close()


pink_floyd_server_conversation()
