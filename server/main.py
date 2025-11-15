import socket, threading, time

from connection_handling import user_connection

from command_handler import handler

class everything:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("0.0.0.0", 9999))
        self.sock.settimeout(5.0)
        self.sock.listen()
        self.running = True
        self.all_clients = [] # all 'connection_handling.user_connection' belong here
        self.rooms = {"lobby": "Welcome to the lobby!", "custom": "Default."}
    

    def debugprint(self, message : str):
        print(message)
        return


    def listen_constantly(self):
        while self.running:
            try:
                connection,_ = self.sock.accept()
                cmd = handler(self)
                client = user_connection(connection, cmd, self)
                cmd.cnh = client
                self.all_clients.append(client)
                threading.Thread(target=client.listener, daemon=True).start()
                self.debugprint("new connection")
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                pass


    def start(self):
        threading.Thread(target=self.listen_constantly, daemon=True).start()

server = everything()
server.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass # Do a server shutdown here
