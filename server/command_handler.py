import socket
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import everything
    from connection_handling import user_connection

class handler:
    def __init__(self, main: "everything"):    
        if not isinstance(main, main.__class__):
            raise TypeError(f"args: 'main' = main.everything. Received: {type(main)}.")
        self.cnh: user_connection | None = None
        
        self.parent = main
        self.all_commands = {
            "SET_TOPIC": {
                "function": self.set_topic,
                "usage": "/topic <room> <new topic>",
                "description": "Set a new topic for a room",
                "needs_whole": True
            },
            "MESSAGE_USER": {
                "function": self.message_user,
                "usage": "/msg <user> <your message>",
                "description": "Send another user a direct message.",
                "needs_whole": True
            },
            "CREATE_ROOM": {
                "function": self.create_room,
                "usage": "/create <room name>",
                "description": "Create a new room and instantly join it.",
                "needs_whole": True
            },
            "JOIN_ROOM": {
                "function": self.join_room,
                "usage": "/join <room name>",
                "description": "Join a room.",
                "needs_whole": True
            },
            "GET_LIST_ROOM": {
                "function": self.list_rooms,
                "usage": "/rooms",
                "description": "Get a list from all rooms.",
                "needs_whole": False
            },
            "REGISTER": { # No-End-User-Display (N-EUD)
                "function": self.register_username,
                "usage": None,
                "description": None,
                "needs_whole": True
            },
            "CLIENT_DISCONNECT": {
                "function": self.disconnect,
                "usage": "/disconnect",
                "description": "Disconnect from the server you are currently connected to.",
                "needs_whole": False
            },
            "ROOM_EXIST": { # N-EUD
                "function": self.send_info_if_room_exists,
                "usage": None,
                "description": None,
                "needs_whole": True
            },
            "GET_PING": {
                "function": self.send_ping,
                "usage": "/ping",
                "description": "Get a ping from the server.",
                "needs_whole": False
            }
        }


    @property # "Make sure ts is NOT None (aka. a seatbelt)
    def sock_handler(self) -> "user_connection":
        if self.cnh is None:
            raise RuntimeError("sock_handler not set")
        return self.cnh

    
    # N-EUD
    def register_username(self, whole : dict):
        self.sock_handler.username = whole["username"]
        self.sock_handler.broadcast(f"[Server]: {self.sock_handler.username} has joined", self.sock_handler.sock)
        return


    # /disconnect
    def disconnect(self):
        self.sock_handler.disconnect_current_client()
        return

    
    # /rooms
    def list_rooms(self):
        pass

    
    # /ping
    def send_ping(self):
        self.sock_handler.sock.sendall("[Server]: Ping received!".encode())
        return


    # !! join_room + create_room are not finished yet !!
    # /join
    def join_room(self, whole : dict):
        room_name = whole["other"] 
        if self.room_exists(room_name):
            pass

    
    # /create
    def create_room(self, whole : dict):
            if self.room_exists(whole["other"]):
                self.parent.sock.sendall(f"[Server]: Room already exists.".encode())
                return
            self.parent.rooms[whole["other"]] = "Default topic."
            self.join_room(whole)

    
    # N-EUD, server side
    def room_exists(self, whole : dict) -> bool :
        for room,_ in self.parent.rooms.items():
            if room == whole["other"]:
                return True
        return False
    

    # N-EUD
    def send_info_if_room_exists(self, whole : dict):
        confirmation = "INFO: ROOM_EXIST_TRUE" if self.room_exists(whole) else "INFO: ROOM_EXIST_FALSE"
        self.parent.sock.sendall(confirmation.encode())
    
    
    # /msg
    def message_user(self, whole : dict):
        message = whole["message"]
        username = whole["other"]
        cur_username = self.sock_handler.username
        receiver = None
        for client in self.parent.all_clients:
            if client.username == username:
                receiver = client.sock
                break
        if not receiver:
            self.sock_handler.sock.sendall("[Server]: User does not exist.".encode())
            return
        
        receiver.sendall(f"(DM)[{cur_username}]: {message}".encode())
        self.sock_handler.sock.sendall(f"(DM)[TO: {username}]: {message}".encode())


    # /topic
    def set_topic(self, whole : dict):
        if not (self.room_exists(whole["other"])):
            self.sock_handler.sock.sendall(f"[Server]: Room does not exist.".encode())

            return
        if(whole["extra"]):
            self.parent.rooms[whole["other"]] = whole["extra"]
            self.sock_handler.sock.sendall(f"[Server]: Set {whole['other']}'s topic to:\n{whole['extra']}".encode())
            

    # /help
    def send_help_list(self):
        help_string = "All commands:\n"
        for _, entry in self.all_commands.items():
            if(entry.get("description")):
                help_string += f"{entry.get("")} : {entry['description']}\n"
        self.sock_handler.sock.sendall(f"[Server]: {help_string}".encode())

    def give(self, whole : dict):
        if not isinstance(whole, dict):
            raise TypeError("Gave an argument that isn't a dict.")
        cmd = whole.get("command")
        if not cmd in self.all_commands:
            return f"{cmd} is not a valid command."

        entry = self.all_commands[cmd]
        func = entry["function"]
        if entry.get("needs_whole", False):
            return func(whole)
        return func()
