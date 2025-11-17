import socket, time
from connection_handler import bot_connection


class BotMain:
    def __init__(self, name : str, ip_address : str, port : int):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True
        self.handler = bot_connection(name, sock, ip_address, port, self)

    def start(self):
        print("Start")
        self.handler.start()

    def shutdown(self):
        exit()
    

bot = BotMain("IDONTKNOW", "localhost", 9999)
bot.start()

while bot.running:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        bot.shutdown()