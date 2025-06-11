import socket
import pickle

class Network:
    def __init__(self, server_ip):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server_ip
        self.port = 5555
        self.addr = (self.server, self.port)
        self.player_id = None

    def connect(self):
        try:
            self.client.connect(self.addr)
            self.player_id = pickle.loads(self.client.recv(2048))
            return self.player_id
        except (socket.error, ConnectionRefusedError) as e:
            print(f"Błąd połączenia: {e}")
            return None

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(4096))
        except socket.error as e:
            print(f"Błąd wysyłania/odbierania danych: {e}")
            return None
            
    def disconnect(self):
        self.client.close()