import socket, json, queue


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from connection_handling import handler



class commandHandler:
    def __init__(self, main, username, room, sock):
        if not isinstance(username, str) or not isinstance(room, str) or not isinstance(sock, socket.socket):
            raise TypeError("username: String, room: String, sock: socket.socket")
        self.username = username
        self.other = None
        self.message = None
        self.extra = None
        self.room = room
        self.command = None
        
        self.cnh: handler | None = None
 

        self.sock = sock
        self.last_user_dm = None
        self.running = True # !!!! PLS PLS PLS DONT HAVE THIS WE NEED TO CHECK PARENT'S 'running' !!!
        
        self.parent = main
        
        


        self.all_command_dict = {
            "/help": {
                "function": self.get_list_help,
                "usage": "/help",
                "needs_whole": False
            },
            "/rooms": {
                "function": self.get_list_room,
                "usage": "/rooms",
                "needs_whole": False
            },
            "/users": {
                "function": self.get_list_user,
                "usage": "/users",
                "needs_whole": False
            },
            "/whoami": {
                "function": self.get_current_nick,
                "usage": "/whoami",
                "needs_whole": False
            },
            "/ping": {
                "function": self.get_response_ping,
                "usage": "/ping",
                "needs_whole": False
            },
            "/topic": {
                "function": self.set_new_topic,
                "usage": "/topic <room> <new topic>",
                "needs_whole": True
            },
            "/nick": {
                "function": self.set_new_nick,
                "usage": "/nick <nickname>",
                "needs_whole": True
            },
            "/disconnect": {
                "function": self.disconnect_from_server,
                "usage": "/disconnect",
                "needs_whole": False
            },
            "/msg": {
                "function": self.message_user,
                "usage": "/message <user> <your message>",
                "needs_whole": True
            },
            "/join": {
                "function": self.join_room,
                "usage": "/join <room>",
                "needs_whole": True
            },
            "/create": {
                "function": self.create_room,
                "usage": "/create <room name>",
                "needs_whole": True
            },
            "/reply": {
                "function": self.reply_last,
                "usage": "/reply <message>",
                "needs_whole": True
            },
    }
   
    @property # "Make sure ts is NOT None (aka. a seatbelt)
    def con_handler(self) -> "handler":
        if self.cnh is None:
            raise RuntimeError("sock_handler not set")
        return self.cnh

    def to_json(self):
        cur_user = self.__dict__.copy()
        cur_user.pop("sock", None)
        cur_user.pop("all_command_dict", None)
        cur_user.pop("con_handler", None)
        cur_user.pop("parent", None)
        cur_user.pop("cnh", None)
        cur_user.pop("running", None)
        cur_user.pop("last_user_dm", None)

        return json.dumps(cur_user, indent=4)
    

    def send(self):
        self.sock.sendall(self.to_json().encode())
        return
    

    def reset_everything(self):
        self.username = None
        self.room = None
        self.extra = None
        self.other = None
        self.command = None
        self.message = None
        self.last_user_dm = None

    
    def get_current_nick(self):
        self.parent.safe_print("[OwnSock]", f"Your current nick is {self.username}.")
        return


    def set_new_topic(self, whole):
        room_name = ""
        try:
            room_name = whole.split(" ")[1]
            set_topic = " ".join(whole.split(" ")[2:])
        except IndexError:
            return self.all_command_dict[whole.split(" ")[0]]["usage"]
        self.command = "SET_TOPIC"
        self.other = room_name
        self.extra = set_topic
        self.send()
        return

    def reply_last(self, whole):
        if not self.last_user_dm:
            self.parent.safe_print(message="You have no open DMs.")
            return
        try:
            message = " ".join(whole.split(" ")[1:])
            if not message:
                self.parent.safe_print(message="/reply <your message>")
                return
            self.other = self.last_user_dm
            self.command = "MESSAGE_USER"
            self.message = message
            self.send()
            return 
        except IndexError:
            return self.all_command_dict[whole.split(" ")[0]]["usage"]


    def process_queue_for_room(self, room_name : str) -> bool:
        while True:
            try:
                joined_string = self.con_handler.info_string_queue.get(timeout=3)
                joined = True if joined_string == "INFO: JOINED_ROOM" else False
                if joined:
                    self.room = room_name
                    return True
            except queue.Empty:
                self.parent.safe_print(message="Server failed to confirm information.")
                return False


    def join_room(self, whole):
        try:
            room_name = whole.split(" ")[1]
            if not self.con_handler.check_room(room_name):
                self.parent.safe_print("[Server]", "Room does not exist.")
                return
            self.parent.safe_print(message="ROOM EXISTS!")
            self.command = "JOIN_ROOM"
            self.other = room_name
            self.send()
            if not self.process_queue_for_room(room_name):
                self.parent.safe_print(message="Server failed to confirm information")
                return
            self.room = room_name
            
                
        except IndexError:
            return self.all_command_dict[whole.split(" ")[0]]["usage"]
    

    def create_room(self, whole):
        try:
            room_name = whole.split(" ")[1]
            if self.con_handler.check_room(room_name):
                self.parent.safe_print("[Server]", "Room already exists.")
                return
            self.command = "CREATE_ROOM"
            self.other = room_name
            self.send()
            self.process_queue_for_room(room_name)
            return
        except IndexError:
            return self.all_command_dict[whole.split(" ")[0]]["usage"]


    def get_response_ping(self):
        self.command = "GET_PING"
        self.send()
        return


    def message_user(self, whole):
        try:
            username = whole.split(" ")[1]
            message = " ".join(whole.split(" ")[2:])

            self.command = "MESSAGE_USER"
            self.other = username
            self.message = message
            self.send()
            self.last_user_dm = username
            return

        except IndexError:
            return self.all_command_dict[whole.split(" ")[0]]["usage"]
        

    def register_to_server(self):
        self.command = "REGISTER"
        self.send()


    def disconnect_from_server(self):
        try:
            self.command = "CLIENT_DISCONNECT"
            self.send()
        except:
            self.parent.safe_print("[OwnSock]", "Server is probably already closed.")
            pass
        self.reset_everything()
        self.running = False
        try:
            self.sock.close()
        except: pass

    def reset_extra_things(self, message_too = False):
        if not isinstance(message_too, bool):
            raise TypeError(f"Excpected bool for 'message_too', got: {type(message_too).__name__}")
        self.other = None
        self.message = None if message_too else self.message
        self.extra = None
        return
    
    
    def get_list_room(self):
        self.command = "GET_LIST_ROOM"
        self.send()
        return


    def get_list_user(self):
        self.command = "GET_LIST_USER"
        self.send()
        return


    def get_list_help(self):
        self.reset_extra_things(True)
        self.command = "GET_LIST_HELP"
        self.send()
        return

    
    def set_new_nick(self, whole):
        self.reset_extra_things(True)
        self.command = "SET_NEW_NICK"
        try:
            self.other = whole.split(" ")[1]
        except IndexError:
            return self.all_command_dict["/nick"]["usage"]
        self.send()
        self.username = self.other
        return
    

    def give(self, whole : str):
        if not isinstance(whole, str):
            raise TypeError("Gave an argument that isn't a string.")
        cmd = whole.split(" ")[0]
        if not cmd in self.all_command_dict:
            return f"{cmd} is not a valid command."
        self.reset_extra_things()
        entry = self.all_command_dict[cmd]
        func = entry["function"]
        if entry.get("needs_whole", False):
            return func(whole)
        return func()
