import socket, html, sys, threading

from commands import commandHandler

from connection_handling import handler

from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit import print_formatted_text, PromptSession



class everything:
    def safe_print(self, sender_and_room = "[OwnSock]", message = ""):
        safe_message = html.escape(message)
        print_formatted_text(HTML(f"<b>{sender_and_room}:</b> {safe_message}"))


    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(5)
        
        self.running = True

        self.promptses = PromptSession()
    
    def connect_to_a_server(self):
        while self.running:
            with patch_stdout():

                try:
                    self.safe_print("[OwnSock]", "/connect <ip> <port>")
                    cmd = self.promptses.prompt("[OwnSock]: ")
                    split_cmd = cmd.split(" ")
                    _, ip, port, *_ = split_cmd + [None, None]  # pad with None
                    if not port:
                        pass # !! search for the shit !!
                    
                    self.sock.connect((ip, int(port)))
                    self.safe_print(message="You have been connected\nYou joined 'lobby'.")
                    break
                except KeyboardInterrupt:
                    self.running = False
                    sys.exit()
                except IndexError:
                    self.safe_print(message="Invalid.")
                    continue
                except socket.timeout:
                    self.safe_print(message="Request timed out. Is the server reachable?")
                    continue
                except Exception as e: 
                    print(e)


    def input_loop(self):
        while self.running:
            with patch_stdout():
                current_message = self.promptses.prompt("[You]: ")
                if current_message.startswith("/"):
                    reply = self.command_handler.give(current_message)
                    if reply:
                        print(reply)
                    continue
                elif current_message.strip() == "":
                    self.safe_print(message="No empty messages allowed.")
                    continue
                if not self.command_handler.room:
                    self.safe_print(message="You haven't joined a room et. /join <room name> or /create <room>")
                    continue
                self.command_handler.message = current_message
                self.command_handler.command = None
                self.command_handler.send()

    def run(self):
        self.connect_to_a_server()
        with patch_stdout():
            username = self.promptses.prompt("Username: ").strip()
        self.command_handler = commandHandler(self, username, "lobby", self.sock)
        self.connection_handler = handler(self.sock, self.command_handler, self)
        self.command_handler.cnh = self.connection_handler
        
        self.command_handler.register_to_server()
        # ^ Now with this, the scripts can talk to each other ^

        

        threading.Thread(target=self.connection_handler.get_messages, daemon=True).start()
        self.input_loop()
    
    def shutdown(self):
        self.command_handler.disconnect_from_server()
        self.running = False
        self.safe_print(message="Exiting. Goodbye!")
        self.sock.close()
        sys.exit(0)


ALL_HANDLE = everything()
ALL_HANDLE.run()

while True:
    try:
        pass
    except KeyboardInterrupt:
        pass 
