import socket, threading, json, requests, queue
from threading import Lock

class bot_connection:
    def __init__(self, username : str, sock : socket.socket, ip_address : str, port : int, parent):
        self.username = username
        self.other = None
        self.extra = None
        self.message = None
        self.room = "lobby"
        self.command = None
        self.current_dict = {}
        self.sock = sock
        self.ip = ip_address
        self.port = port
        self.parent = parent 
        self.url_queue = queue.Queue()
        self.send_lock = Lock()
 

    def extract_title(self):
        while True:
            try:
                url, room = self.url_queue.get(timeout=5)
                print("Trying to extract title")
                if not(url.startswith("http")):
                    url = "https://" + url
                headers = {"User-Agent": "Mozilla/5.0"}
                resp = requests.get(url, headers=headers, timeout=5)
                html = resp.text
                title_index = html.find("<title>")
                start_index = title_index + len("<title>")
                end_index = html.find("</title>")
                title = html[start_index:end_index]
                self.message = f"[{self.username}] ^ {title}"
                self.room = room
                self.command = None
                self.send()
            except queue.Empty:
                continue
            except Exception as e:
                print(e)
                return

    def to_json(self):
        self.current_dict = {
            "username": self.username,
            "other": self.other,
            "extra": self.extra,
            "message": self.message or "",
            "room": self.room,
            "command": self.command
        }
        print(self.current_dict)
        return json.dumps(self.current_dict)
    


    def listener(self):
        self.sock.settimeout(5.0)
        while self.parent.running:
            try:
                data = self.sock.recv(5012).decode("utf-8", errors="ignore")
                if not data:
                    self.parent.running = False
                    break
                message = json.loads(data)
                print(message)
                if message.get("message") and ("http" in message["message"] or "www." in message["message"]):
                    breaker = message["message"].split(" ")
                    for word in breaker:
                        if(word.startswith("http") or word.startswith("www.")):
                            self.url_queue.put((word, message.get("room")))
                    
                
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error in listener: {e}")
                continue

    def send(self):
        json_data = self.to_json()
        with self.send_lock:
            self.sock.sendall(json_data.encode())
            print("sent bitch yasss")


    def start(self):
        self.sock.connect((self.ip, self.port))
        self.command = "I_AM_A_BOT"
        self.send()
        self.sock.settimeout(5.0)
        threading.Thread(target=self.listener, daemon=True).start()
        threading.Thread(target=self.extract_title, daemon=True).start()

