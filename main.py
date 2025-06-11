import pygame
import sys

pygame.init()
pygame.mixer.init()

from settings import *
from ui import *
from game import Game
from network import Network
from server import Server
from snake import Snake
import utils

SCREEN_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SCREEN_UPDATE, 90)


class Main:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.game_state = "main_menu"
        self.game_instance = None
        self.network = None
        self.server_instance = None
        self.last_game_params = {}
        self.ip_input_box = TextInputBox(
            SCREEN_WIDTH / 2 - 150, 300, 300, 40, "127.0.0.1"
        )
        self.lobby_data = {}

    def run(self):
        while True:
            events = pygame.event.get()
            self.handle_events(events)
            self.update_state()
            self.draw(events)
            pygame.display.update()
            self.clock.tick(FPS)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                if self.server_instance:
                    print("[INFO] Zamykanie serwera...")
                pygame.quit()
                sys.exit()

            if self.game_state == "join_game":
                action = self.ip_input_box.handle_event(event)
                if action == "connect":
                    self.connect_to_server()

            if self.game_state == "in_game" and event.type == SCREEN_UPDATE:
                self.game_instance.update()

            if self.game_state == "in_game":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.game_state = "paused"
                else:
                    self.game_instance.handle_event(event)
            elif self.game_state == "online_game":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.go_to_main_menu()

    def update_state(self):
        if self.game_state == "in_game" and self.game_instance.is_game_over:
            self.game_state = "game_over"
        elif self.game_state in ["host_lobby", "client_lobby", "online_game"]:
            self.update_online_state()

    def update_online_state(self):
        if not self.network:
            return

        payload = "get_state"
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            payload = pygame.Vector2(0, -1)
        elif keys[pygame.K_s]:
            payload = pygame.Vector2(0, 1)
        elif keys[pygame.K_a]:
            payload = pygame.Vector2(-1, 0)
        elif keys[pygame.K_d]:
            payload = pygame.Vector2(1, 0)

        response = self.network.send(payload)
        if response is None:
            print("Utracono połączenie z serwerem.")
            self.go_to_main_menu()
            return

        if response["status"] == "lobby":
            self.lobby_data = response
            self.game_state = (
                "client_lobby" if not self.server_instance else "host_lobby"
            )
        elif response["status"] == "in_game":
            self.game_state = "online_game"
            self.update_game_state_from_dto(response["state"])

    def draw(self, events):
        self.screen.fill(COLOR_BG)
        if self.game_state == "main_menu":
            action = self.draw_custom_main_menu(events)
            self.handle_menu_action(action)
        elif self.game_state == "join_game":
            action = draw_join_game_screen(self.screen, self.ip_input_box, events)
            if action == "connect":
                self.connect_to_server()
            else:
                self.handle_menu_action(action)
        elif self.game_state == "host_lobby":
            players = self.server_instance.player_data.keys()
            player_names = [f"Gracz {p}" for p in players]
            action = draw_lobby_screen(
                self.screen,
                True,
                self.server_instance.get_host_ip(),
                player_names,
                events,
            )
            if action == "start_online_game":
                self.server_instance.start_game()
        elif self.game_state == "client_lobby":
            draw_lobby_screen(
                self.screen, False, "", self.lobby_data.get("players", []), events
            )
        elif self.game_state == "in_game" or self.game_state == "online_game":
            if self.game_instance:
                self.game_instance.draw()
        elif self.game_state.startswith("map_select"):
            prefix = self.game_state.split("_")[-1]
            action = draw_map_select(self.screen, f"start_{prefix}", events)
            self.handle_menu_action(action)
        elif self.game_state == "paused":
            self.game_instance.draw()
            action = draw_pause_menu(self.screen, events)
            self.handle_menu_action(action)
        elif self.game_state == "game_over":
            scores = self.game_instance.get_scores()
            action = draw_game_over_screen(self.screen, scores, events)
            self.handle_menu_action(action)

    def draw_custom_main_menu(self, events):
        draw_text(
            self.screen,
            "SNAKE",
            FONT_LARGE,
            COLOR_TEXT,
            (SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.1),
        )
        actions = {
            "sp": draw_button(
                self.screen,
                "Single Player",
                (SCREEN_WIDTH / 2 - 150, 150),
                (300, 50),
                "map_select_sp",
                events,
            ),
            "bot": draw_button(
                self.screen,
                "Player vs Bot",
                (SCREEN_WIDTH / 2 - 150, 220),
                (300, 50),
                "map_select_bot",
                events,
            ),
            "local": draw_button(
                self.screen,
                "Local Multiplayer",
                (SCREEN_WIDTH / 2 - 150, 290),
                (300, 50),
                "map_select_local",
                events,
            ),
            "host": draw_button(
                self.screen,
                "Hostuj Grę",
                (SCREEN_WIDTH / 2 - 150, 360),
                (300, 50),
                "host_game",
                events,
            ),
            "join": draw_button(
                self.screen,
                "Dołącz do Gry",
                (SCREEN_WIDTH / 2 - 150, 430),
                (300, 50),
                "join_game",
                events,
            ),
            "load": draw_button(
                self.screen,
                "Wczytaj Grę",
                (SCREEN_WIDTH / 2 - 150, 500),
                (300, 50),
                "load_game",
                events,
            ),
            "quit": draw_button(
                self.screen,
                "Wyjdź",
                (SCREEN_WIDTH / 2 - 150, 570),
                (300, 50),
                "quit",
                events,
            ),
        }
        for action in actions.values():
            if action:
                return action
        return "main_menu"

    def handle_menu_action(self, action):
        if not action:
            return
        if action == "host_game":
            self.server_instance = Server()
            self.server_instance.start()
            self.network = Network("127.0.0.1")
            if self.network.connect():
                self.game_state = "host_lobby"
            else:
                print("Nie udało się uruchomić lobby hosta.")
                self.go_to_main_menu()
        elif action == "join_game":
            self.game_state = "join_game"
        elif action == "main_menu":
            self.go_to_main_menu()
        elif action == "quit":
            pygame.quit()
            sys.exit()
        elif action.startswith("map_select"):
            self.game_state = action
        elif action.startswith("start_"):
            _, mode, map_file = action.split("_")
            map_path = f"maps/{map_file}.txt"
            game_mode_map = {
                "sp": "single_player",
                "bot": "player_vs_bot",
                "local": "local_multiplayer",
            }
            game_mode = game_mode_map[mode]
            self.last_game_params = {"game_mode": game_mode, "map_path": map_path}
            self.game_instance = Game(self.screen, game_mode, map_path)
            self.game_state = "in_game"
        elif action == "resume":
            self.game_state = "in_game"
        elif action == "restart":
            self.game_instance = Game(self.screen, **self.last_game_params)
            self.game_state = "in_game"
        elif action == "save_game":
            utils.save_game_state(self.game_instance)
            self.game_state = "paused"
        elif action == "load_game":
            loaded_state = utils.load_game_state()
            if loaded_state:
                self.last_game_params = {
                    "game_mode": loaded_state["game_mode"],
                    "map_path": loaded_state["map_path"],
                }
                self.game_instance = Game(
                    self.screen,
                    loaded_state["game_mode"],
                    loaded_state["map_path"],
                    loaded_state=loaded_state,
                )
                self.game_state = "in_game"
            else:
                self.game_state = "main_menu"

    def connect_to_server(self):
        ip = self.ip_input_box.text
        self.network = Network(ip)
        if self.network.connect():
            self.game_state = "client_lobby"
        else:
            print(f"Nie udało się połączyć z serwerem pod adresem {ip}")
            self.network = None

    def go_to_main_menu(self):
        if self.network:
            self.network.disconnect()
        self.network = None
        self.server_instance = None
        self.game_instance = None
        self.game_state = "main_menu"

    def update_game_state_from_dto(self, state_dto):
        if not self.game_instance:
            self.game_instance = Game(
                self.screen, "online_multiplayer", "maps/map1.txt"
            )

        self.game_instance.food = pygame.Vector2(state_dto["food"])
        self.game_instance.walls = [pygame.Vector2(w) for w in state_dto["walls"]]
        self.game_instance.is_game_over = state_dto["is_game_over"]

        new_snakes = []
        for snake_data in state_dto["snakes"]:
            new_snake = Snake(
                snake_data["body"][0], snake_data["color"], {}, snake_data["player_id"]
            )

            new_snake.body = [pygame.Vector2(b) for b in snake_data["body"]]
            new_snake.direction = pygame.Vector2(snake_data["direction"])
            new_snake.score = snake_data["score"]
            new_snake.alive = snake_data["alive"]
            new_snakes.append(new_snake)

    def get_online_direction(self):
        if self.game_instance and self.network and self.game_instance.snakes:
            my_id = self.network.player_id
            for snake in self.game_instance.snakes:
                if snake.player_id == my_id:
                    return snake.direction
        return pygame.Vector2(0, 0)


if __name__ == "__main__":
    main_app = Main()
    main_app.run()

