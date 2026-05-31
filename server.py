import socket
import data

REQUESTS = {
    "albums": 101,
    "album songs": 102,
    "song length": 103,
    "song lyrics": 104,
    "song album": 105,
    "search title by word": 106,
    "search song lyrics": 107,
    "quit": 108,
    "password": 109
}
PASS_AUTHENTICATION_STATE = {
    "WRONG": 0,
    "RIGHT": 1,
    "CLIENT_DISCONNECTED": 2
}
LISTEN_PORT = 447
CLIENT_MSG_SPLIT_KEY = ":"
REQUEST_IDENTIFIER_INDEX = 0
REQUEST_PARAMETERS_INDEX = 1
CLIENT_QUIT_REQ = 108
CLIENT_ALBUM_REQ = 101
FILE_PATH = "Pink_Floyd_DB.txt"
HASHED_PASSWORD = "698d60ae40ad03bb179010488d33089a757aaa1f8e62e425b097eadab917d8fd"
FILE_OPEN_ERR_MSG = "Couldn't open file"
UNREACHABLE_DB_MSG = "Unable to reach database file"
RECOVER_SIZE = 4096


def check_password(client_soc):
    """
    Gets the password from the client and checks if it's correct
    :param client_soc: the socket to use in order to talk with the client
    :type client_soc: socket
    :return: if the password is correct the function will return 1, if it's incorrect it
    will return 0 and if the client disconnected during the function it will return 2. It
    will also return the code representing the client's request
    """
    success_state = PASS_AUTHENTICATION_STATE["CLIENT_DISCONNECTED"]
    req_code = 0
    try:
        client_msg = client_soc.recv(RECOVER_SIZE)
        client_msg = client_msg.decode()
        req_code, parameters = identify_client_msg(client_msg)
    except (ConnectionResetError, TypeError):
        print_client_disconnected_msg()
        client_soc.close()
        return success_state, req_code
    if not check_recv_success(client_msg):
        print_client_disconnected_msg()
        client_soc.close()
        return success_state, req_code
    print(client_msg)
    if parameters == HASHED_PASSWORD:
        success_state = PASS_AUTHENTICATION_STATE["RIGHT"]
    else:
        success_state = PASS_AUTHENTICATION_STATE["WRONG"]
    return success_state, req_code


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


def print_client_disconnected_msg():
    """
    Prints an error message in case the client unexpectedly
    disconnected
    """
    print("\nClient unexpectedly disconnected\nListening for new incoming calls\n")


def call_functions_according_to_client_req(action, parameters, file_data):
    """
    Calls functions in data.py according to the client's request with his request parameters
    and the database's data
    :param action: the client's choice on which action he wants to perform
    :type action: int
    :param parameters: the parameters in the client's request
    :type parameters: str
    :param file_data: the data structure built from the database
    :type file_data: list
    :return: returns the message the function in data.py returned
    :rtype: str
    """
    server_msg = ''
    if action == REQUESTS["albums"]:
        server_msg = data.get_albums(file_data)
    elif action == REQUESTS["album songs"]:
        server_msg = data.get_album_songs(file_data, parameters)
    elif action == REQUESTS["song length"]:
        server_msg = data.get_song_duration(file_data, parameters)
    elif action == REQUESTS["song lyrics"]:
        server_msg = data.get_song_lyrics(file_data, parameters)
    elif action == REQUESTS["song album"]:
        server_msg = data.get_song_album(file_data, parameters)
    elif action == REQUESTS["search title by word"]:
        server_msg = data.search_song_by_name(file_data, parameters)
    elif action == REQUESTS["search song lyrics"]:
        server_msg = data.search_song_by_lyrics(file_data, parameters)
    return server_msg


def process_request_loop(client_soc, file_data):
    """
    Keeps receiving the client's requests and handles them until the client
    requests to quit or one of the sides in the tcp sockets unexpectedly closes
    the connection
    :param client_soc: the socket to use in order to talk to the client
    :type client_soc: socket
    :param file_data: the data structure that contains all the db's information
    :type file_data: list
    :return: if the client unexpectedly disconnected the function will return
    True, otherwise False
    """
    client_unexpectedly_disconnected = True
    while True:
        try:
            client_msg = client_soc.recv(RECOVER_SIZE)
            client_msg = client_msg.decode()
            if check_recv_success(client_msg):
                print(client_msg)
                req_code, req_parameters = identify_client_msg(client_msg)
                try:
                    if req_code == CLIENT_QUIT_REQ:
                        final_goodbye_msg = data.build_return_msg(req_code, "")
                        print(final_goodbye_msg)
                        client_soc.sendall(final_goodbye_msg.encode())
                        client_unexpectedly_disconnected = False
                        break
                    server_msg = call_functions_according_to_client_req(req_code, req_parameters, file_data)
                    print(server_msg)
                    client_soc.sendall(server_msg.encode())

                except ConnectionResetError:
                    print_client_disconnected_msg()
                    return True
            else:
                print_client_disconnected_msg()
                client_unexpectedly_disconnected = True
                break
        except ConnectionResetError:
            print("Error: ConnectionResetError")
            client_unexpectedly_disconnected = True
            break
        except KeyboardInterrupt:
            print("Error: KeyboardInterrupt")
            break
    return client_unexpectedly_disconnected


def pink_floyd_client_conversation(listening_sock, file_data):
    """
    This is the main function of the code, it listens for incoming calls, sends
    a welcome message, retrieves the client's request, uses another function to identify
    what the client requested, calls function in data.py to get answers and then
    sends them back to the client
    :param file_data: the data structure
    :type file_data: list
    :param listening_sock: the socket where the server listens for incoming calls
    :type listening_sock: socket
    :return: if the client unexpectedly disconnected in the middle of the conversation it
    returns True, otherwise it returns False
    :rtype: bool
    """
    listening_sock.listen(1)
    client_soc, client_address = listening_sock.accept()
    successful_authentication, req_code = check_password(client_soc)
    if successful_authentication == PASS_AUTHENTICATION_STATE["CLIENT_DISCONNECTED"]:
        return True
    elif successful_authentication == PASS_AUTHENTICATION_STATE["WRONG"]:
        try:
            server_msg = data.build_err_msg(REQUESTS["password"])
            print(server_msg)
            client_soc.sendall(server_msg.encode())
            return False
        except ConnectionResetError:
            print_client_disconnected_msg()
            return True
    try:
        server_msg = data.build_return_msg(req_code)
        print(server_msg)
        client_soc.sendall(server_msg.encode())

        msg = "Welcome to the Pink-Floyd Server!"
        client_soc.sendall(msg.encode())
    except ConnectionResetError:
        print_client_disconnected_msg()
        return True

    client_unexpectedly_disconnected = process_request_loop(client_soc, file_data)
    client_soc.close()
    return client_unexpectedly_disconnected


def identify_client_msg(client_msg):
    """
    This function receives the client's message and constructs a fitting server identifier
    :param client_msg: the client's message
    :type client_msg: str
    :return: the request code
    :rtype: int
    """
    try:
        client_msg_list = client_msg.split(CLIENT_MSG_SPLIT_KEY)
        req_code = int(client_msg_list[REQUEST_IDENTIFIER_INDEX])
        parameters = client_msg_list[REQUEST_PARAMETERS_INDEX]
        return req_code, parameters
    except (IndexError, ValueError) as e:
        print("Client message format isn't valid", e)
        # In case the function failed I return None which is the same as null
        # I learned it here: https://www.geeksforgeeks.org/how-to-return-null-in-python/
        return None, None
    except Exception as e:
        print("Error: ", e)
        return None


def main():
    successful_db_reading = True
    try:
        file = open(FILE_PATH, "r")
        file_data = data.make_data_structure(file)
        if file_data == FILE_OPEN_ERR_MSG:
            print(UNREACHABLE_DB_MSG)
            successful_db_reading = False
    except Exception as e:
        print(UNREACHABLE_DB_MSG, e)
        successful_db_reading = False
    if successful_db_reading:
        try:
            listening_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = ('', LISTEN_PORT)
            listening_sock.bind(server_address)
            client_unexpectedly_disconnected = True
            while client_unexpectedly_disconnected:
                client_unexpectedly_disconnected = pink_floyd_client_conversation(listening_sock, file_data)
            listening_sock.close()
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
