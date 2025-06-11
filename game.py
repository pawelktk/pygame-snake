import pygame
import random
from settings import *
from snake import Snake
from bot import BotSnake
from ui import draw_grid
import utils

class Game:
    def __init__(self, screen, game_mode, map_path, loaded_state=None, headless=False):
        self.screen = screen
        self.game_mode = game_mode
        self.map_path = map_path
        self.is_game_over = False
        self.headless = headless

        if not self.headless:
            self.load_assets()
        
        self.load_map()

        if loaded_state:
            self.setup_from_load(loaded_state)
        else:
            self.setup_new_game()

    def load_assets(self):
        try:
            self.apple_img = pygame.image.load(GRAPHICS["apple"]).convert_alpha()
            self.wall_img = pygame.image.load(GRAPHICS["wall"]).convert_alpha()
            self.eat_sound = pygame.mixer.Sound(EAT_SOUND)
            self.game_over_sound = pygame.mixer.Sound(GAMEOVER_SOUND)
        except pygame.error as e:
            print(f"Błąd ładowania zasobów: {e}")
            pygame.quit()
            exit()

    def load_map(self):
        self.walls = []
        try:
            with open(self.map_path, 'r') as f:
                for y, line in enumerate(f):
                    for x, char in enumerate(line.strip()):
                        if char == 'W':
                            self.walls.append(pygame.Vector2(x, y))
        except FileNotFoundError:
            print(f"Nie znaleziono pliku mapy: {self.map_path}")
            self.walls = []

    def setup_new_game(self):
        self.snakes = []
        if self.game_mode == "single_player":
            controls = {"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d}
            self.snakes.append(Snake((5, 5), COLOR_BLUE, controls, 1))
        elif self.game_mode == "player_vs_bot":
            controls1 = {"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d}
            self.snakes.append(Snake((5, 5), COLOR_BLUE, controls1, 1))
            self.snakes.append(BotSnake((15, 15), COLOR_RED, 2))
        elif self.game_mode == "local_multiplayer":
            controls1 = {
                "up": pygame.K_w,
                "down": pygame.K_s,
                "left": pygame.K_a,
                "right": pygame.K_d,
            }
            controls2 = {
                "up": pygame.K_UP,
                "down": pygame.K_DOWN,
                "left": pygame.K_LEFT,
                "right": pygame.K_RIGHT,
            }

            snake1 = Snake((5, 5), COLOR_BLUE, controls1, 1)
            snake1.direction = pygame.Vector2(1, 0)
            self.snakes.append(snake1)

            start_pos_p2 = (CELL_NUMBER_W - 6, CELL_NUMBER_H - 6)
            snake2 = Snake(start_pos_p2, COLOR_RED, controls2, 2)
            snake2.direction = pygame.Vector2(-1, 0)
            self.snakes.append(snake2)
        
        self.place_food()

    def setup_from_load(self, state):
        self.snakes = []
        for p_data in state["players"]:
            controls = {}
            if p_data["id"] == 1:
                controls = {"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d}
            elif p_data["id"] == 2 and not p_data["is_bot"]:
                 controls = {"up": pygame.K_UP, "down": pygame.K_DOWN, "left": pygame.K_LEFT, "right": pygame.K_RIGHT}

            if p_data["is_bot"]:
                snake = BotSnake(p_data["body"][0], COLOR_RED, p_data["id"])
            else:
                snake = Snake(p_data["body"][0], COLOR_BLUE if p_data["id"] == 1 else COLOR_RED, controls, p_data["id"])
            
            snake.body = p_data["body"]
            snake.direction = p_data["direction"]
            snake.score = p_data["score"]
            snake.alive = p_data["alive"]
            self.snakes.append(snake)
        
        self.food = state["food_pos"]

    def place_food(self):
        while True:
            x = random.randint(0, CELL_NUMBER_W - 1)
            y = random.randint(0, CELL_NUMBER_H - 1)
            self.food = pygame.Vector2(x, y)
            
            on_snake = any(self.food in snake.body for snake in self.snakes)
            on_wall = self.food in self.walls
            if not on_snake and not on_wall:
                break

    def update(self):
        if self.is_game_over:
            return

        for snake in self.snakes:
            if snake.alive:
                if isinstance(snake, BotSnake):
                    other_snakes = [s for s in self.snakes if s != snake]
                    snake.decide_move(
                        self.food,
                        self.walls,
                        other_snakes,
                        (CELL_NUMBER_W, CELL_NUMBER_H),
                    )
                snake.move()

        for snake in self.snakes:
            self.check_collisions(snake)

        game_over_condition = False
        if self.game_mode in ["single_player", "player_vs_bot"]:
            player_snake = self.snakes[0]
            if not player_snake.alive:
                game_over_condition = True
        elif self.game_mode == "local_multiplayer":
            alive_count = sum(1 for s in self.snakes if s.alive)
            if len(self.snakes) > 1 and alive_count <= 1:
                game_over_condition = True

        if game_over_condition and not self.is_game_over:
            self.is_game_over = True
            self.game_over_sound.play()

    def draw(self):
        self.screen.fill(COLOR_BG)
        draw_grid(self.screen)
        self.draw_elements()

    def draw_elements(self):
        # ściany
        for wall_pos in self.walls:
            wall_rect = pygame.Rect(wall_pos.x * CELL_SIZE, wall_pos.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            self.screen.blit(self.wall_img, wall_rect)

        # jedzenie
        food_rect = pygame.Rect(self.food.x * CELL_SIZE, self.food.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        self.screen.blit(self.apple_img, food_rect)

        # węże
        for snake in self.snakes:
            snake.draw(self.screen)
        
        # wyniki
        for i, snake in enumerate(self.snakes):
            score_text = f"P{snake.player_id}: {snake.score}"
            score_surface = FONT_SMALL.render(score_text, True, COLOR_TEXT)
            self.screen.blit(score_surface, (10 + i * 150, 10))

    def check_collisions(self, snake):
        if not snake.alive:
            return

        # Kolizja z jedzeniem
        if snake.body[0] == self.food:
            snake.add_block()
            self.eat_sound.play()
            self.place_food()

        # Kolizja ze ścianami i krawędziami
        snake.check_collision_walls(self.walls)

        # Kolizja z samym sobą
        snake.check_collision_self()

        # Kolizja z innymi wężami
        for other_snake in self.snakes:
            if snake != other_snake and other_snake.alive:
                snake.check_collision_other_snake(other_snake)

    def handle_event(self, event):
        for snake in self.snakes:
            snake.handle_input(event)

    def get_scores(self):
        return {snake.player_id: snake.score for snake in self.snakes}
