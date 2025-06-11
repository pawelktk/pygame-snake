import pygame
from settings import *

class Snake:
    def __init__(self, start_pos, color, controls, player_id=1):
        self.body = [pygame.Vector2(start_pos)]
        self.direction = pygame.Vector2(1, 0)
        self.new_block = False
        self.color = color
        self.controls = controls
        self.player_id = player_id
        self.score = 0
        self.alive = True
        self.load_graphics()

    def load_graphics(self):
        self.graphics = {
            "head_up": pygame.image.load(GRAPHICS["head_up"]).convert_alpha(),
            "head_down": pygame.image.load(GRAPHICS["head_down"]).convert_alpha(),
            "head_left": pygame.image.load(GRAPHICS["head_left"]).convert_alpha(),
            "head_right": pygame.image.load(GRAPHICS["head_right"]).convert_alpha(),
            "body": pygame.image.load(GRAPHICS["body"]).convert_alpha(),
        }

    def draw(self, screen):
        if not self.alive:
            return
        self.update_head_graphics()
        for index, block in enumerate(self.body):
            x_pos = int(block.x * CELL_SIZE)
            y_pos = int(block.y * CELL_SIZE)
            block_rect = pygame.Rect(x_pos, y_pos, CELL_SIZE, CELL_SIZE)

            if index == 0:
                screen.blit(self.head, block_rect)
            else:
                screen.blit(self.graphics["body"], block_rect)

    def update_head_graphics(self):
        head_relation = self.body[1] - self.body[0] if len(self.body) > 1 else self.direction * -1
        if head_relation == pygame.Vector2(1, 0): self.head = self.graphics["head_left"]
        elif head_relation == pygame.Vector2(-1, 0): self.head = self.graphics["head_right"]
        elif head_relation == pygame.Vector2(0, 1): self.head = self.graphics["head_up"]
        elif head_relation == pygame.Vector2(0, -1): self.head = self.graphics["head_down"]


    def move(self):
        if not self.alive:
            return

        body_copy = self.body[:]
        new_head = body_copy[0] + self.direction
        body_copy.insert(0, new_head)

        if self.new_block:
            self.new_block = False
        else:
            body_copy.pop()

        self.body = body_copy

    def add_block(self):
        self.new_block = True
        self.score += 1

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.controls["up"] and self.direction.y != 1:
                self.direction = pygame.Vector2(0, -1)
            elif event.key == self.controls["down"] and self.direction.y != -1:
                self.direction = pygame.Vector2(0, 1)
            elif event.key == self.controls["left"] and self.direction.x != 1:
                self.direction = pygame.Vector2(-1, 0)
            elif event.key == self.controls["right"] and self.direction.x != -1:
                self.direction = pygame.Vector2(1, 0)

    def check_collision_self(self):
        if len(self.body) > 1 and self.body[0] in self.body[1:]:
            self.alive = False

    def check_collision_walls(self, walls):
        head = self.body[0]
        if not (0 <= head.x < CELL_NUMBER_W and 0 <= head.y < CELL_NUMBER_H):
            self.alive = False
        for wall in walls:
            if head == wall:
                self.alive = False

    def check_collision_other_snake(self, other_snake):
        if self.body[0] in other_snake.body:
            self.alive = False
