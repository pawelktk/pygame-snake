import pygame
import random
from snake import Snake
from settings import CELL_NUMBER_W, CELL_NUMBER_H

class BotSnake(Snake):
    def __init__(self, start_pos, color, player_id=2):
        super().__init__(start_pos, color, {}, player_id)

    def handle_input(self, event):
        pass

    def decide_move(self, food_pos, walls, other_snakes, screen_dims):
        if not self.alive:
            return

        head = self.body[0]
        possible_directions = [
            pygame.Vector2(0, -1),
            pygame.Vector2(0, 1),
            pygame.Vector2(-1, 0),
            pygame.Vector2(1, 0),
        ]

        # 1. Znajdź wszystkie bezpieczne ruchy
        safe_moves = []
        for move in possible_directions:
            # Zapobiegaj zawracaniu
            if len(self.body) > 1 and move == -self.direction:
                continue

            next_pos = head + move
            # Sprawdź kolizje ze ścianami, krawędziami, sobą i innymi wężami
            is_safe = True
            if not (0 <= next_pos.x < screen_dims[0] and 0 <= next_pos.y < screen_dims[1]):
                is_safe = False
            if next_pos in self.body:
                is_safe = False
            if next_pos in walls:
                is_safe = False
            for snake in other_snakes:
                if next_pos in snake.body:
                    is_safe = False

            if is_safe:
                safe_moves.append(move)

        if not safe_moves:
            # Jeśli nie ma bezpiecznych ruchów, idź prosto na pewną śmierć
            return

        # 2. Znajdź ruchy, które przybliżają do jedzenia
        current_dist = head.distance_to(food_pos)
        improving_moves = []
        for move in safe_moves:
            if (head + move).distance_to(food_pos) < current_dist:
                improving_moves.append(move)

        # 3. Wybierz najlepszy ruch
        if improving_moves:
            # Jeśli są ruchy, które przybliżają do celu, wybierz losowy z nich
            self.direction = random.choice(improving_moves)
        else:
            # Jeśli nie, wybierz dowolny bezpieczny ruch, aby uniknąć kręcenia się w kółko
            self.direction = random.choice(safe_moves)