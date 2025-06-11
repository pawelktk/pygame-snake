import pygame

# Ustawienia okna
INFO = pygame.display.Info()
CELL_SIZE = 35
CELL_NUMBER_W = 40
CELL_NUMBER_H = 30
SCREEN_WIDTH = CELL_SIZE * CELL_NUMBER_W   # 800
SCREEN_HEIGHT = CELL_SIZE * CELL_NUMBER_H  # 600
FPS = 60

# Kolory
COLOR_BG = (175, 215, 70)
COLOR_GRID = (167, 209, 61)
COLOR_TEXT = (56, 74, 12)
COLOR_RED = (200, 50, 50)
COLOR_BLUE = (50, 50, 200)
COLOR_GREEN = (50, 200, 50)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_BUTTON = (120, 180, 80)
COLOR_BUTTON_HOVER = (140, 200, 100)

# Czcionki
try:
    pygame.font.init()
    FONT_PATH = pygame.font.match_font("consolas")
    FONT_LARGE = pygame.font.Font(FONT_PATH, 50)
    FONT_MEDIUM = pygame.font.Font(FONT_PATH, 30)
    FONT_SMALL = pygame.font.Font(FONT_PATH, 20)
except:
    print("Nie znaleziono czcionki 'consolas', używam domyślnej.")
    FONT_LARGE = pygame.font.Font(None, 60)
    FONT_MEDIUM = pygame.font.Font(None, 40)
    FONT_SMALL = pygame.font.Font(None, 30)

# Dźwięki i grafiki
EAT_SOUND = "assets/sounds/eat.wav"
GAMEOVER_SOUND = "assets/sounds/game_over.wav"
GRAPHICS = {
    "apple": "assets/graphics/apple.png",
    "wall": "assets/graphics/wall.png",
    "body": "assets/graphics/body.png",
    "head_up": "assets/graphics/head_up.png",
    "head_down": "assets/graphics/head_down.png",
    "head_left": "assets/graphics/head_left.png",
    "head_right": "assets/graphics/head_right.png",
}
