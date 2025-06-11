import pygame
from settings import *


def draw_text(screen, text, font, color, center_pos):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=center_pos)
    screen.blit(text_surface, text_rect)


def draw_button(screen, text, pos, size, action=None, events=[]):
    button_rect = pygame.Rect(pos, size)
    mouse_pos = pygame.mouse.get_pos()

    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER, button_rect, border_radius=10)

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if action:
                    return action
    else:
        pygame.draw.rect(screen, COLOR_BUTTON, button_rect, border_radius=10)

    draw_text(screen, text, FONT_MEDIUM, COLOR_WHITE, button_rect.center)
    return None


def draw_grid(screen):
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, COLOR_GRID, (0, y), (SCREEN_WIDTH, y))


def draw_main_menu(screen):
    screen.fill(COLOR_BG)
    draw_text(
        screen, "SNAKE", FONT_LARGE, COLOR_TEXT, (SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.2)
    )

    actions = {
        "single_player": draw_button(
            screen,
            "Single Player",
            (SCREEN_WIDTH / 2 - 150, 250),
            (300, 50),
            "map_select_sp",
        ),
        "player_vs_bot": draw_button(
            screen,
            "Player vs Bot",
            (SCREEN_WIDTH / 2 - 150, 320),
            (300, 50),
            "map_select_bot",
        ),
        "local_multiplayer": draw_button(
            screen,
            "Local Multiplayer",
            (SCREEN_WIDTH / 2 - 150, 390),
            (300, 50),
            "map_select_local",
        ),
        "online_multiplayer": draw_button(
            screen,
            "Online Multiplayer",
            (SCREEN_WIDTH / 2 - 150, 460),
            (300, 50),
            "online_lobby",
        ),
        "load_game": draw_button(
            screen, "Load Game", (SCREEN_WIDTH / 2 - 150, 530), (300, 50), "load_game"
        ),
        "quit": draw_button(
            screen, "Quit", (SCREEN_WIDTH / 2 - 150, 600), (300, 50), "quit"
        ),
    }
    for action in actions.values():
        if action:
            return action
    return "main_menu"


def draw_map_select(screen, next_state_prefix, events=[]):
    screen.fill(COLOR_BG)
    draw_text(
        screen,
        "Wybierz Mapę",
        FONT_LARGE,
        COLOR_TEXT,
        (SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.2),
    )

    actions = {
        "map1": draw_button(
            screen,
            "Pusta Mapa",
            (SCREEN_WIDTH / 2 - 150, 300),
            (300, 50),
            f"{next_state_prefix}_map1",
            events,
        ),
        "map2": draw_button(
            screen,
            "Mapa z Przeszkodami",
            (SCREEN_WIDTH / 2 - 150, 370),
            (300, 50),
            f"{next_state_prefix}_map2",
            events,
        ),
        "back": draw_button(
            screen,
            "Powrót",
            (SCREEN_WIDTH / 2 - 150, 440),
            (300, 50),
            "main_menu",
            events,
        ),
    }
    for action in actions.values():
        if action:
            return action
    return f"map_select_{next_state_prefix.split('_')[1]}"


def draw_pause_menu(screen, events=[]):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    draw_text(
        screen,
        "PAUZA",
        FONT_LARGE,
        COLOR_WHITE,
        (SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.3),
    )

    actions = {
        "resume": draw_button(
            screen, "Wznów", (SCREEN_WIDTH / 2 - 150, 350), (300, 50), "resume", events
        ),
        "save": draw_button(
            screen,
            "Zapisz Grę",
            (SCREEN_WIDTH / 2 - 150, 420),
            (300, 50),
            "save_game",
            events,
        ),
        "main_menu": draw_button(
            screen,
            "Menu Główne",
            (SCREEN_WIDTH / 2 - 150, 490),
            (300, 50),
            "main_menu",
            events,
        ),
    }
    for action in actions.values():
        if action:
            return action
    return "paused"


def draw_game_over_screen(screen, scores, events=[]):
    screen.fill(COLOR_RED)
    draw_text(
        screen,
        "KONIEC GRY",
        FONT_LARGE,
        COLOR_WHITE,
        (SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.2),
    )

    y_offset = SCREEN_HEIGHT * 0.4
    for i, (player_id, score) in enumerate(scores.items()):
        draw_text(
            screen,
            f"Gracz {player_id}: {score}",
            FONT_MEDIUM,
            COLOR_WHITE,
            (SCREEN_WIDTH / 2, y_offset + i * 50),
        )

    actions = {
        "play_again": draw_button(
            screen,
            "Zagraj Ponownie",
            (SCREEN_WIDTH / 2 - 150, 600),
            (300, 50),
            "restart",
            events,
        ),
        "main_menu": draw_button(
            screen,
            "Menu Główne",
            (SCREEN_WIDTH / 2 - 150, 670),
            (300, 50),
            "main_menu",
            events,
        ),
    }
    for action in actions.values():
        if action:
            return action
    return "game_over"


class TextInputBox:
    def __init__(self, x, y, w, h, text=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = COLOR_GRID
        self.color_active = COLOR_TEXT
        self.color = self.color_inactive
        self.text = text
        self.txt_surface = FONT_MEDIUM.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return "connect"
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = FONT_MEDIUM.render(self.text, True, COLOR_TEXT)

    def draw(self, screen):
        pygame.draw.rect(screen, COLOR_WHITE, self.rect)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)


def draw_join_game_screen(screen, input_box, events=[]):
    screen.fill(COLOR_BG)
    draw_text(screen, "Dołącz do Gry", FONT_LARGE, COLOR_TEXT, (SCREEN_WIDTH / 2, 150))
    draw_text(
        screen,
        "Wpisz adres IP serwera:",
        FONT_MEDIUM,
        COLOR_TEXT,
        (SCREEN_WIDTH / 2, 250),
    )
    input_box.draw(screen)

    actions = {
        "connect": draw_button(
            screen,
            "Połącz",
            (SCREEN_WIDTH / 2 - 150, 400),
            (300, 50),
            "connect",
            events,
        ),
        "back": draw_button(
            screen,
            "Powrót",
            (SCREEN_WIDTH / 2 - 150, 470),
            (300, 50),
            "main_menu",
            events,
        ),
    }
    for action in actions.values():
        if action:
            return action
    return "join_game"


def draw_lobby_screen(screen, is_host, host_ip, players, events=[]):
    screen.fill(COLOR_BG)
    title = "Lobby Hosta" if is_host else "Poczekalnia"
    draw_text(screen, title, FONT_LARGE, COLOR_TEXT, (SCREEN_WIDTH / 2, 100))

    if is_host:
        draw_text(
            screen,
            f"Twój adres IP: {host_ip}",
            FONT_MEDIUM,
            COLOR_TEXT,
            (SCREEN_WIDTH / 2, 180),
        )
        draw_text(
            screen,
            "Oczekiwanie na graczy...",
            FONT_SMALL,
            COLOR_TEXT,
            (SCREEN_WIDTH / 2, 220),
        )

    draw_text(
        screen, "Gracze w lobby:", FONT_MEDIUM, COLOR_TEXT, (SCREEN_WIDTH / 2, 300)
    )
    for i, player_name in enumerate(players):
        draw_text(
            screen,
            player_name,
            FONT_MEDIUM,
            COLOR_WHITE,
            (SCREEN_WIDTH / 2, 350 + i * 40),
        )

    action = None
    if is_host:
        if len(players) > 1:
            action = draw_button(
                screen,
                "Rozpocznij Grę",
                (SCREEN_WIDTH / 2 - 150, 500),
                (300, 50),
                "start_online_game",
                events,
            )
        else:
            pygame.draw.rect(
                screen,
                COLOR_GRID,
                (SCREEN_WIDTH / 2 - 150, 500, 300, 50),
                border_radius=10,
            )
            draw_text(
                screen,
                "Oczekiwanie...",
                FONT_MEDIUM,
                COLOR_WHITE,
                (SCREEN_WIDTH / 2, 525),
            )
    else:
        draw_text(
            screen,
            "Oczekiwanie na start hosta...",
            FONT_MEDIUM,
            COLOR_WHITE,
            (SCREEN_WIDTH / 2, 525),
        )

    return action

