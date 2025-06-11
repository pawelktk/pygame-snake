import socket
import pickle
import threading
import pygame
from game import Game
from snake import Snake

class Server:
    def __init__(self, host="0.0.0.0", port=5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.game = Game(None, "online_multiplayer", "maps/map1.txt", headless=True)
        self.clients = {}
        self.player_data = {}
        self.game_started = False
        self.lock = threading.Lock()

    def get_host_ip(self):
        try:
            return socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
            return "127.0.0.1"

    def start(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()
            print(f"[SERWER] Uruchomiony na {self.get_host_ip()}:{self.port}")
            threading.Thread(target=self._game_loop, daemon=True).start()
            threading.Thread(target=self._listen_for_connections, daemon=True).start()
        except OSError as e:
            print(f"[BŁĄD SERWERA] Nie można uruchomić serwera: {e}")

    def _listen_for_connections(self):
        while True:
            conn, addr = self.server_socket.accept()
            with self.lock:
                if self.game_started or len(self.clients) >= 4:
                    conn.close()
                    continue
                
                player_id = len(self.clients) + 1
                self.clients[conn] = player_id
                self.player_data[player_id] = {"name": f"Gracz {player_id}"}
                
                start_pos = (5 + (player_id-1) * 10, 5)
                color = [(0,0,255), (255,0,0), (0,255,0), (255,255,0)][player_id-1]
                snake = Snake(start_pos, color, {}, player_id)
                self.game.snakes.append(snake)
                print(f"[SERWER] Połączono z {addr} jako Gracz {player_id}")
            
            threading.Thread(target=self._threaded_client, args=(conn, player_id), daemon=True).start()

    def _threaded_client(self, conn, player_id):
        conn.send(pickle.dumps(player_id))

        while True:
            try:
                move_intent = pickle.loads(conn.recv(2048))
                
                with self.lock:
                    if self.game_started:
                        if isinstance(move_intent, pygame.math.Vector2):
                            for s in self.game.snakes:
                                if s.player_id == player_id:
                                    if s.direction + move_intent != pygame.Vector2(0, 0):
                                        s.direction = move_intent
                                    break
                    
                    if self.game_started:
                        response = {"status": "in_game", "state": self._get_game_state_dto()}
                    else:
                        player_names = [p["name"] for p in self.player_data.values()]
                        response = {"status": "lobby", "players": player_names}
                
                conn.sendall(pickle.dumps(response))

            except (EOFError, ConnectionResetError, pickle.UnpicklingError):
                break

        print(f"[SERWER] Rozłączono gracza {player_id}")
        with self.lock:
            if conn in self.clients:
                del self.clients[conn]
            if player_id in self.player_data:
                del self.player_data[player_id]
            self.game.snakes = [s for s in self.game.snakes if s.player_id != player_id]
        conn.close()

    def _game_loop(self):
        clock = pygame.time.Clock()
        while True:
            if self.game_started:
                with self.lock:
                    self.game.update()
            clock.tick(10)

    def start_game(self):
        if not self.game_started:
            print("[SERWER] Host rozpoczął grę!")
            self.game_started = True

    def _get_game_state_dto(self):
        state = {
            "snakes": [],
            "food": (self.game.food.x, self.game.food.y),
            "walls": [(w.x, w.y) for w in self.game.walls],
            "is_game_over": self.game.is_game_over
        }
        for snake in self.game.snakes:
            state["snakes"].append({
                "player_id": snake.player_id,
                "body": [(v.x, v.y) for v in snake.body],
                "direction": (snake.direction.x, snake.direction.y),
                "score": snake.score,
                "alive": snake.alive,
                "color": snake.color
            })
        return state