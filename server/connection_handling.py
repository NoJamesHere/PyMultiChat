import socket, json

class user_connection: # This class is used for every connection.
    def __init__(self, sock : socket.socket, cmd, main):
        self.sock = sock
        self.username = None
        self.command = None
        self.other = None
        self.extra = None
        self.room = None
        self.parent = main
        self.command_handler = cmd

    def disconnect_current_client(self):
        disconnect_message = f"[Server]: {self.username} has disconnected."

        for client in list(self.parent.all_clients):
            try:
                if(client.room == self.room):
                    client.sock.sendall(disconnect_message.encode())
            except:
                self.parent.all_clients.pop(self, None)
        try:
            self.parent.sock.close()
        except:
            pass

        self.parent.running = False
        if(self in self.parent.all_clients):
            self.parent.all_clients.pop(self, None)
            
        

    def broadcast(self, message: str, sender=None):
        if sender and not isinstance(sender, socket.socket):
            raise TypeError(f"'sender' is not the type of 'socket.socket'. Received: '{type(sender)}'")

        sender_room = None
        if sender:
            for client in self.parent.all_clients:
                if client.sock == sender:
                    sender_room = client.room
                    break

        disconnected = []

        for client in list(self.parent.all_clients):
            try:
                if sender is not None:
                    if client.sock == sender or client.room != sender_room:
                        continue
                client.sock.sendall(message.encode())
            except Exception:
                disconnected.append(client)

        for dead in disconnected:
            if dead in self.parent.all_clients:
                self.parent.all_clients.remove(dead)    

    def update_values(self, whole):
        index_current = self.parent.all_clients.index(self)
        self.username = whole["username"]
        self.other = whole["other"]
        self.extra = whole["extra"]
        self.command = whole["command"]
        self.room = whole["room"]
        self.parent.all_clients[index_current] = self


    def listener(self):
        while self.parent.running:
            try:
                data = self.sock.recv(5012).decode()
                if not data:
                    self.disconnect_current_client()
                    break
                self.parent.debugprint(data)
                message = json.loads(data)
                if message["command"]:
                    self.update_values(message)
                    self.command_handler.give(message)
                    continue
                line = message["message"]
                user_room = message["room"]
                username = message["username"]
                formatted = f"({user_room})[{username}]: {line}"
                self.parent.debugprint(message)
                self.update_values(message)
                self.broadcast(formatted, sender=self.sock)

            except Exception as e:
                self.parent.debugprint(f"connection_handling.listener: {e}")
                continue
