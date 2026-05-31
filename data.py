ALBUM_SPLIT_KEY = "#"
SONG_SPLIT_KEY = "*"
PARAMETERS_SPLIT_KEY = "::"
ALBUM_TITLE_INDEX = 0
ALBUM_NAME_INDEX = 0
ALBUM_RELEASE_YEAR_INDEX = 1
SONG_NAME_INDEX = 0
AFTER_TITLE_INDEX = 1
FIRST_SONG_INDEX = 1
LYRICS_INDEX_IN_SONG_PARAMETERS = 2
DURATION_INDEX_IN_SONG_PARAMETERS = 1
MSG_IDENTIFIER_AND_PARAMETERS_SPLIT_KEY = ":"
PARAMETERS_JOIN_KEY = ", "
FILE_OPEN_ERR_MSG = "Couldn't open file"
UNWANTED_NEW_LINE_INDEX = -1
REQUESTS = {
    "GET_ALBUMS": 101,
    "GET_ALBUM_SONGS": 102,
    "GET_SONG_LENGTH": 103,
    "GET_SONG_LYRICS": 104,
    "GET_SONG_ALBUM": 105,
    "SEARCH_SONG_BY_NAME": 106,
    "SEARCH_SONG_BY_LYRICS": 107,
    "QUIT": 108,
    "PASSWORD": 109
}
SERVER_ERR_ANSWERS = {
    401: "Request failed",
    402: "No album was found under that name",
    403: "Couldn't find song",
    404: "Couldn't find song",
    405: "Couldn't find song",
    406: "Couldn't find songs names that include the word you entered",
    407: "Couldn't find songs that contain the word you entered",
    409: "Access denied"
}
MSG_LABELS = {
    201: "The albums list:\n",
    202: "The songs in the album:\n",
    203: "The song length:\n",
    204: "The song lyrics:\n",
    205: "The album with this song is:\n",
    206: "The list of songs:\n",
    207: "The list of songs:\n",
    208: "Thank you for using the Pink-Floyd Server! Bye Bye!",
    209: "Access granted!"
}


def make_data_structure(file):
    """
    makes a data structure from a file of pink floyd songs and albums that is
    organized in the following way:
    A dict where the key is the song's name and the value is a list containing its
    author, duration and the words
    Another dict where each key is the song's name and each value is a list that
    is made of all the songs dicts in the album and the album's release year
    A list that contains all the album dicts
    :param file: the file that we make the data structure with
    :type file: _io.TextIOWrapper
    :return a sorted data structure:
    """
    try:
        file_content = file.read()
    except AttributeError:
        return FILE_OPEN_ERR_MSG
    albums_list = file_content.split(ALBUM_SPLIT_KEY)
    albums_list = albums_list[1:]  # The first index is empty
    list_of_albums = []
    for album in albums_list:
        song_and_albums = album.split(SONG_SPLIT_KEY)
        album_title = song_and_albums[ALBUM_TITLE_INDEX][:-1]  # Removing the \n at the end of the album's name
        album_title = album_title.split(PARAMETERS_SPLIT_KEY)
        album_name = album_title[ALBUM_NAME_INDEX]
        album_release_year = album_title[ALBUM_RELEASE_YEAR_INDEX]
        song_and_albums = song_and_albums[1:]  # 'deleting' the album's names from the file
        album_value = [album_release_year]
        for curr_song in song_and_albums:
            split_title = curr_song.split(PARAMETERS_SPLIT_KEY)
            song_dict = {split_title[SONG_NAME_INDEX]: split_title[AFTER_TITLE_INDEX:]}
            # Adding the dict to the list that is the key in the album's dict
            album_value.append(song_dict)
        album_dict = {album_name: album_value}
        list_of_albums.append(album_dict)
    return list_of_albums


# In the get keys and values functions I'm using something that look like this: list(album.keys())[0] and I
# learned it from here: https://stackoverflow.com/questions/18552001/accessing-dict-keys-element-by-index-in-python3
# for example if I have {"apples": 52} and I want to access the 52 I have to use the
# .values() function and it will be ([52]), but this is not a list, this is a "view object"
# so I convert it to a list, and then it will be [52] and to access it as a string I get
# the first index which is 52
# BTW this works both for the keys and the values, so I'm using it for the both of them


def get_keys(dictionary):
    """
    Returns the keys in a dict
    :param dictionary: the dict to get the keys from
    :type dictionary: dict
    :return: the keys in the dict
    :rtype: str
    """
    return list(dictionary.keys())[0]


def get_values(dictionary):
    """
    Returns the values in a dict
    :param dictionary: the dict to get the values from
    :type dictionary: dict
    :return: the values in the dict
    :rtype: it depends on which dict it's called on because there are some
    dicts where the values are a list but there are some dicts where the vales
    are a str
    """
    return list(dictionary.values())[0]


def get_albums(file_data):
    """
    Extracts all the albums from the data structure
    :param file_data: the data structure returned by make_data_structure, containing albums and their songs
    :type file_data: list
    :return: a formatted message with all album names or an error message if the request fails
    :rtype: it depends on which dict it's called on because there are some
    dicts where the values are a list but there are some dicts where the vales
    are a str
    """
    albums_list = []
    try:
        for album in file_data:
            album_title = get_keys(album)
            albums_list.append(album_title)
        albums = PARAMETERS_JOIN_KEY.join(albums_list)
        return_msg = build_return_msg(REQUESTS["GET_ALBUMS"], albums)
        return return_msg
    except (TypeError, IndexError):
        return_msg = build_err_msg(REQUESTS["GET_ALBUMS"])
        return return_msg


def get_album_songs(file_data, album):
    """
    Retrieves the list of songs from a specific album in the data structure.
    :param file_data: the data structure returned by make_data_structure, containing albums and their songs
    :type file_data: list
    :param album: the name of the album to search for
    :type album: str
    :return: a formatted message containing the songs of the album or an error message if the album is not found
    :rtype: str
    """
    found_album = False
    songs_data_list = []
    try:
        for curr_album in file_data:
            album_name = get_keys(curr_album)
            if album_name == album:
                found_album = True
                album_data = get_values(curr_album)
                album_data = album_data[FIRST_SONG_INDEX:]
                for song in album_data:
                    song_title = get_keys(song)
                    songs_data_list.append(song_title)
                break
        songs_data = PARAMETERS_JOIN_KEY.join(songs_data_list)
    except (TypeError, IndexError):
        return_msg = build_exception_response(REQUESTS["GET_ALBUM_SONGS"])
        return return_msg
    if found_album:
        return_msg = build_return_msg(REQUESTS["GET_ALBUM_SONGS"], songs_data)
    else:
        return_msg = build_err_msg(REQUESTS["GET_ALBUM_SONGS"])
    return return_msg


def get_song_duration(file_data, song):
    """
    Retrieves the duration of a specified song from the data structure.
    :param file_data: the data structure returned by make_data_structure, containing albums and their songs
    :type file_data: list
    :param song: the name of the song to find the duration for
    :type song: str
    :return: a formatted message with the song's duration or an error message if the song is not found
    :rtype: str
    """
    found_song = False
    duration = ""
    for album in file_data:
        album_data = get_values(album)
        album_data = album_data[FIRST_SONG_INDEX:]
        for curr_song in album_data:
            try:
                song_title = get_keys(curr_song)
                if song_title == song:
                    song_parameters = get_values(curr_song)
                    duration = song_parameters[DURATION_INDEX_IN_SONG_PARAMETERS]
                    found_song = True
                    break
            except (IndexError, TypeError):
                return_msg = build_exception_response(REQUESTS["GET_SONG_LENGTH"])
                return return_msg
    if found_song:
        return_msg = build_return_msg(REQUESTS["GET_SONG_LENGTH"], duration)
    else:
        return_msg = build_err_msg(REQUESTS["GET_SONG_LENGTH"])
    return return_msg


def get_song_lyrics(file_data, song):
    """
    Retrieves the lyrics of a specified song from the data structure.
    :param file_data: the data structure returned by make_data_structure, containing albums and their songs
    :type file_data: list
    :param song: the name of the song to find the lyrics for
    :type song: str
    :return: a formatted message with the song's lyrics or an error message if the song is not found
    :rtype: str
    """
    found_song = False
    lyrics = ""
    for album in file_data:
        album_data = get_values(album)
        album_data = album_data[FIRST_SONG_INDEX:]
        for curr_song in album_data:
            try:
                song_title = get_keys(curr_song)
                if song_title == song:
                    song_parameters = get_values(curr_song)
                    lyrics = song_parameters[LYRICS_INDEX_IN_SONG_PARAMETERS]
                    found_song = True
                    break
            except (IndexError, TypeError):
                return_msg = build_exception_response(REQUESTS["GET_SONG_LYRICS"])
                return return_msg
    if found_song:
        lyrics = lyrics[:UNWANTED_NEW_LINE_INDEX]
        return_msg = build_return_msg(REQUESTS["GET_SONG_LYRICS"], lyrics)
    else:
        return_msg = build_err_msg(REQUESTS["GET_SONG_LYRICS"])
    return return_msg


def get_song_album(file_data, song):
    """
    Finds the album that contains a specified song in the data structure.
    :param file_data: the data structure returned by make_data_structure, containing albums and their songs
    :type file_data: list
    :param song: the name of the song to find the album for
    :type song: str
    :return: a formatted message with the album name containing the song, or an error message if not found
    :rtype: str
    """
    found_song = False
    final_album = ""
    try:
        for album in file_data:
            album_data = get_values(album)
            album_data = album_data[FIRST_SONG_INDEX:]
            for curr_song in album_data:
                song_title = get_keys(curr_song)
                if song_title == song:
                    final_album = get_keys(album)
                    found_song = True
                    break
            if found_song:
                break
    except (IndexError, TypeError):
        return_msg = build_exception_response(REQUESTS["GET_SONG_ALBUM"])
        return return_msg
    if found_song:
        return_msg = build_return_msg(REQUESTS["GET_SONG_ALBUM"], final_album)
    else:
        return_msg = build_err_msg(REQUESTS["GET_SONG_ALBUM"])
    return return_msg


def search_song_by_name(file_data, word):
    """
    Searches for songs whose titles contain a given word in the data structure.
    :param file_data: the data structure returned by make_data_structure, containing albums and their songs
    :type file_data: list
    :param word: the word to search for within song titles
    :type word: str
    :return: a formatted message listing matching song titles or an error message if none are found
    :rtype: str
    """
    found_title = False
    titles_list = []
    for album in file_data:
        album_data = get_values(album)
        album_data = album_data[FIRST_SONG_INDEX:]
        for song in album_data:
            title = get_keys(song)
            try:
                if word.lower() in title.lower():
                    titles_list.append(title)
                    found_title = True
            except (AttributeError, TypeError):
                return_msg = build_exception_response(REQUESTS["SEARCH_SONG_BY_NAME"])
                return return_msg
    titles = PARAMETERS_JOIN_KEY.join(titles_list)
    if found_title:
        return_msg = build_return_msg(REQUESTS["SEARCH_SONG_BY_NAME"], titles)
    else:
        return_msg = build_err_msg(REQUESTS["SEARCH_SONG_BY_NAME"])
    return return_msg


def search_song_by_lyrics(file_data, word):
    """
    Searches for songs containing a given word in their lyrics within the data structure.
    :param file_data: the data structure returned by make_data_structure, containing albums and their songs
    :type file_data: list
    :param word: the word to search for within song lyrics
    :type word: str
    :return: a formatted message listing song titles with matching lyrics or an error message if none are found
    :rtype: str
    """
    found_title = False
    titles_list = []
    for album in file_data:
        album_parameters = get_values(album)
        album_data = album_parameters[FIRST_SONG_INDEX:]
        for song in album_data:
            title = get_keys(song)
            song_parameters = get_values(song)
            lyrics = song_parameters[LYRICS_INDEX_IN_SONG_PARAMETERS]
            try:
                if word.lower() in lyrics.lower():
                    titles_list.append(title)
                    found_title = True
            except (AttributeError, TypeError, IndexError):
                return_msg = build_exception_response(REQUESTS["SEARCH_SONG_BY_LYRICS"])
                return return_msg
    titles = PARAMETERS_JOIN_KEY.join(titles_list)
    if found_title:
        return_msg = build_return_msg(REQUESTS["SEARCH_SONG_BY_LYRICS"], titles)
    else:
        return_msg = build_err_msg(REQUESTS["SEARCH_SONG_BY_LYRICS"])
    return return_msg


def build_err_msg(action):
    """
    Constructs an error message string based on the given action code.
    :param action: the numeric code representing the user's request
    :type action: int
    :return: a formatted error message corresponding to the action
    :rtype: str
    """
    action += 300  # Turning the client's request identifier into an error message identifier. 101 -> 401
    err_msg = str(action) + MSG_IDENTIFIER_AND_PARAMETERS_SPLIT_KEY + SERVER_ERR_ANSWERS[action]
    return err_msg


def build_return_msg(action, parameters=""):
    """
    Constructs a success message string based on the given action code and parameters.
    :param action: the numeric code representing the user's request
    :type action: int
    :param parameters: the content to include in the message
    :type parameters: str
    :return: a formatted success message corresponding to the action with the provided parameters
    :rtype: str
    """
    action += 100  # Converting to valid success message format (101 -> 201)
    return str(action) + MSG_IDENTIFIER_AND_PARAMETERS_SPLIT_KEY + MSG_LABELS[action] + parameters


def build_exception_response(action):
    """
    Build an error message in case on of the exceptions was triggered
    :param action: the action the user chose
    :type action: int
    :return: a fitting error message
    :rtype: str
    """
    action += 300  # Converting to valid error message format (101 -> 401)
    return str(action) + MSG_IDENTIFIER_AND_PARAMETERS_SPLIT_KEY + "Request Failed"
