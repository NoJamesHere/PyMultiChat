import socket, threading, time

from connection_handling import user_connection

from command_handler import handler

class everything:
    def __init__(self, ip_address : str, port : int):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((ip_address, port))
        self.debugprint(f"Server has binded to {ip_address}:{port}.")
        self.sock.settimeout(5.0)
        self.sock.listen()
        self.running = True
        self.all_clients = [] # all 'connection_handling.user_connection' belong here
        self.all_bots = []
        self.rooms = {"lobby": "Welcome to the lobby!"} 
    def shutdown(self):
        self.debugprint("Shutting down..")
        for client in self.all_clients:
            try:
                client.sock.sendall("[Server]: Server is shutting down!".encode())
                client.sock.close()
            except Exception as e: self.debugprint(str(e))
        try:
            self.sock.close()
        except Exception as e:
            self.debugprint(str(e))
        self.running = False
    def debugprint(self, message : str):
        print("Debug:", message)
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


    def start(self):
        self.debugprint("Server is starting to listen.")
        threading.Thread(target=self.listen_constantly, daemon=True).start()

server = everything("0.0.0.0", 9999)
server.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    server.debugprint("Trying to shutdown properly.")

    server.shutdown()
