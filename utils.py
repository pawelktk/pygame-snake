import json
import pygame
from settings import *

def save_game_state(game_instance, filename="savegame.json"):
    if game_instance.game_mode == "online":
        print("Nie można zapisać gry w trybie online.")
        return
        
    state = {
        "game_mode": game_instance.game_mode,
        "map_path": game_instance.map_path,
        "food_pos": [game_instance.food.x, game_instance.food.y],
        "players": []
    }
    for snake in game_instance.snakes:
        player_data = {
            "id": snake.player_id,
            "body": [[v.x, v.y] for v in snake.body],
            "direction": [snake.direction.x, snake.direction.y],
            "score": snake.score,
            "alive": snake.alive,
            "is_bot": isinstance(snake, BotSnake)
        }
        state["players"].append(player_data)
    
    try:
        with open(filename, 'w') as f:
            json.dump(state, f, indent=4)
        print(f"Gra zapisana w {filename}")
    except IOError as e:
        print(f"Błąd zapisu gry: {e}")

def load_game_state(filename="savegame.json"):
    try:
        with open(filename, 'r') as f:
            state = json.load(f)
        
        state["food_pos"] = pygame.Vector2(state["food_pos"])
        for player_data in state["players"]:
            player_data["body"] = [pygame.Vector2(v) for v in player_data["body"]]
            player_data["direction"] = pygame.Vector2(player_data["direction"])
        
        print(f"Gra wczytana z {filename}")
        return state
    except (IOError, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Błąd wczytywania gry: {e}")
        return None


from bot import BotSnake
