# 🎸 Pink Floyd Client-Server Database Engine

## 📖 Overview

This project is a custom client-server application built in Python that allows users to securely query a dedicated Pink Floyd music database over a TCP network. It implements low-level socket programming, custom application-layer protocols, and in-memory data structures to deliver fast and reliable query results.

## ✨ Key Features

* **Secure Authentication:** Implements SHA-256 password hashing to authenticate clients on connection before granting any access to the database.


* **Custom Communication Protocol:** Uses a proprietary text-based protocol structured as `ActionCode:Parameters` (e.g., passing action codes like `104` to fetch song lyrics) to streamline network communication.


* **Robust Error Handling:** Engineered to survive unexpected network drops and edge cases. The server gracefully catches `ConnectionResetError`, `KeyboardInterrupt`, and input parsing exceptions without crashing, ensuring high availability.


* **Advanced File I/O & Parsing:** Extracts raw text from `Pink_Floyd_DB.txt` and normalizes it into highly efficient, nested Python data structures (dictionaries and lists) for instant, iteration-based querying.



## 🏗️ Architecture & Modules

* **`server.py`**: The multi-stage TCP server. It binds to a designated port (447), authenticates incoming users, receives custom protocol messages, and routes the validated queries to the data processor.


* **`client.py`**: The interactive CLI frontend. It hashes the user's password locally, displays the interactive menu, manages inputs, and handles secure socket communication with the server.


* **`data.py`**: The backend query engine. Parses the text database upon server boot and processes all isolated user queries, such as fetching album lists, calculating song durations, and searching for specific lyric substrings.



## 🚀 Getting Started

### Prerequisites

* Python 3.x

### Installation & Execution

1. **Clone the repository:**
```bash
git clone https://github.com/yoavlach/Pink-Floyd-Client-Server
cd pink-floyd-client-server

```

2. **Start the Server:**
Ensure `Pink_Floyd_DB.txt` is in the same root directory as the server script.
 ```bash
 python server.py
 ```
3. **Launch the Client:**
Open a separate terminal window and run:
```bash
python client.py
```
4. **Authenticate:**
   Enter the required password when prompted (the default hashed password validates against the server's internal signature).
## 🔍 Query Capabilities
Once securely connected, users can interact with the server via the command-line menu to:
```
1. List all available albums
2. List all songs within a specific album
3. Retrieve the duration (length) of a specific song
4. Retrieve the full lyrics of a specific song
5. Find which album a specific song belongs to
6. Search for songs by partial title matches
7. Search for songs by partial lyric matches
```
*Developed by Yoav Lach as part of advanced network programming and infrastructure tooling research.*
