import socket
import queue

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import everything



class handler:
    def __init__(self, sock, cmd, parent: "everything"):
        self.last_user_dm = ""
        self.error_count = 0
        self.sock = sock
        self.cmd_handler = cmd
        self.info_string_queue = queue.Queue()
        self.parent = parent

    def get_messages(self):
        while self.parent.running:
            try:
                data = self.sock.recv(5012).decode("utf-8", errors="ignore")
                if not data:
                    self.parent.safe_print("[OwnSock]", "Connection closed by server.")
                    self.parent.running = False
                    break
                
                # Catching N-EUD (Non-End-User-Display)
                if data.startswith("INFO"):
                    self.info_string_queue.put(data)
                    continue

                index_1 = data.find("[")
                index_2 = data.find("]")
                
                # Update last_user_dm for /reply
                if data.startswith("(DM") and index_1 != -1 and index_2 != -1:
                    self.cmd_handler.last_user_dm = data[index_1 + 1:index_2]

                sender_and_room = data[:index_2 + 1]

                if data.startswith("[Server]:"):
                    message_of_data = data[len("[Server]: "):]
                    self.parent.safe_print("[Server]", message_of_data)
                else:
                    message_of_data = data[index_2 + 3:].lstrip()
                    self.parent.safe_print(sender_and_room, message_of_data)

            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error in get_messages: {e}")
                self.error_count += 1
                continue

    def check_room(self, room_name):
        self.cmd_handler.command = "ROOM_EXIST"
        self.cmd_handler.other = room_name
        self.cmd_handler.send()
        while True:
            try:
                info_string = self.info_string_queue.get(timeout=3)
                if info_string.startswith("INFO: ROOM_EXIST_"):
                    return info_string == "INFO: ROOM_EXIST_TRUE"
            except queue.Empty:
                self.parent.safe_print("[OwnSock]", "Server timed out on room check.")
                continue
