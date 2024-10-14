import pygame
import sys
from sos_game_logic import GameLogic

pygame.init()

# Colors
BACKGROUND = (24, 24, 27)  # zinc-900
TEXT = (161, 161, 170)  # zinc-400
BUTTON = (63, 63, 70)  # zinc-700
BUTTON_HOVER = (82, 82, 91)  # zinc-600
LINE = (113, 113, 122)  # zinc-500
BOARD_BG = (39, 39, 42)  # zinc-800
TITLE_COLOR = (244, 244, 245)  # zinc-100

# Screen setup
WIDTH, HEIGHT = 900, 700  # Increased screen size for better layout
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SOS Game")

# Fonts
font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 64)  # Larger title font

class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False

    def draw(self):
        color = BUTTON_HOVER if self.hovered else BUTTON
        pygame.draw.rect(screen, color, self.rect, border_radius=15)
        pygame.draw.rect(screen, TEXT, self.rect, border_radius=15, width=2)
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.action()

class Checkbox:
    def __init__(self, x, y, text):
        self.rect = pygame.Rect(x, y, 24, 24)
        self.text = text
        self.checked = False

    def draw(self):
        pygame.draw.rect(screen, TEXT, self.rect, 2, border_radius=5)
        if self.checked:
            pygame.draw.rect(screen, TEXT, self.rect.inflate(-8, -8), border_radius=3)
        text_surf = small_font.render(self.text, True, TEXT)
        screen.blit(text_surf, (self.rect.right + 10, self.rect.centery - text_surf.get_height() // 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked

class RadioButton:
    def __init__(self, x, y, text, group):
        self.rect = pygame.Rect(x, y, 24, 24)
        self.text = text
        self.group = group
        self.selected = False

    def draw(self):
        pygame.draw.circle(screen, TEXT, self.rect.center, 12, 2)
        if self.selected:
            pygame.draw.circle(screen, TEXT, self.rect.center, 8)
        text_surf = small_font.render(self.text, True, TEXT)
        screen.blit(text_surf, (self.rect.right + 10, self.rect.centery - text_surf.get_height() // 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.group.select(self)

class RadioGroup:
    def __init__(self):
        self.buttons = []

    def add(self, button):
        self.buttons.append(button)
        if not self.buttons[0].selected:
            self.buttons[0].selected = True

    def select(self, selected):
        for button in self.buttons:
            button.selected = (button == selected)

def start_game():
    global game_logic, game_started
    board_size = int(next(btn.text[0] for btn in board_size_group.buttons if btn.selected))
    game_mode = "Simple" if simple_mode_radio.selected else "General"
    game_logic = GameLogic(board_size, game_mode)
    game_started = True
    print(f"Starting new game: Size {board_size}x{board_size}, Mode: {game_mode}")

def new_game():
    global game_started
    game_started = False

# Create UI elements
title = title_font.render("SOS Game", True, TITLE_COLOR)
ai_checkbox = Checkbox(50, 180, "Enable AI opponent")
board_size_group = RadioGroup()
board_size_group.add(RadioButton(50, 280, "3x3", board_size_group))
board_size_group.add(RadioButton(50, 320, "4x4", board_size_group))
board_size_group.add(RadioButton(50, 360, "5x5", board_size_group))
start_button = Button(WIDTH // 2 - 80, HEIGHT - 100, 160, 50, "Start Game", start_game)
new_game_button = Button(WIDTH - 180, 20, 160, 50, "New Game", new_game)

mode_group = RadioGroup()
simple_mode_radio = RadioButton(50, 460, "Simple Game", mode_group)
general_mode_radio = RadioButton(50, 500, "General Game", mode_group)
mode_group.add(simple_mode_radio)
mode_group.add(general_mode_radio)

# Add radio buttons for S and O selection
letter_group = RadioGroup()
s_radio = RadioButton(50, HEIGHT - 150, "S", letter_group)
o_radio = RadioButton(50, HEIGHT - 110, "O", letter_group)
letter_group.add(s_radio)
letter_group.add(o_radio)

game_logic = None
game_started = False

def main():
    global game_logic, game_started

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if not game_started:
                ai_checkbox.handle_event(event)
                for btn in board_size_group.buttons:
                    btn.handle_event(event)
                simple_mode_radio.handle_event(event)
                general_mode_radio.handle_event(event)
                start_button.handle_event(event)
            else:
                new_game_button.handle_event(event)
                s_radio.handle_event(event)
                o_radio.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = pygame.mouse.get_pos()
                    board_size = game_logic.board.size
                    cell_size = min((WIDTH - 400) // board_size, (HEIGHT - 250) // board_size)
                    board_width = cell_size * board_size
                    board_height = cell_size * board_size
                    board_left = (WIDTH - board_width) // 2 + 100
                    board_top = 150
                    col = (x - board_left) // cell_size
                    row = (y - board_top) // cell_size
                    if 0 <= row < board_size and 0 <= col < board_size:
                        letter = 'S' if s_radio.selected else 'O'
                        game_logic.make_move(row, col, letter)

        screen.fill(BACKGROUND)

        if not game_started:
            draw_menu()
        else:
            draw_game()

        pygame.display.flip()

    pygame.quit()
    sys.exit()

def draw_menu():
    # Draw title
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

    # Draw decorative elements
    pygame.draw.line(screen, LINE, (30, 130), (WIDTH - 30, 130), 3)
    pygame.draw.line(screen, LINE, (30, 230), (WIDTH - 30, 230), 3)
    pygame.draw.line(screen, LINE, (30, 420), (WIDTH - 30, 420), 3)

    # Draw UI elements
    ai_checkbox.draw()
    for btn in board_size_group.buttons:
        btn.draw()
    start_button.draw()

    # Draw labels
    board_size_label = font.render("Select board size:", True, TEXT)
    screen.blit(board_size_label, (50, 240))

    # Draw game mode options
    mode_label = font.render("Select game mode:", True, TEXT)
    screen.blit(mode_label, (50, 420))
    simple_mode_radio.draw()
    general_mode_radio.draw()

def draw_game():
    # Draw game board
    board_size = game_logic.board.size
    cell_size = min((WIDTH - 400) // board_size, (HEIGHT - 250) // board_size)
    board_width = cell_size * board_size
    board_height = cell_size * board_size
    board_left = (WIDTH - board_width) // 2 + 100
    board_top = 150

    # Draw board background
    pygame.draw.rect(screen, BOARD_BG, (board_left - 10, board_top - 10, board_width + 20, board_height + 20), border_radius=15)
    pygame.draw.rect(screen, LINE, (board_left - 10, board_top - 10, board_width + 20, board_height + 20), 3, border_radius=15)

    for row in range(board_size):
        for col in range(board_size):
            rect = pygame.Rect(board_left + col * cell_size, board_top + row * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, LINE, rect, 1)
            if game_logic.board.board[row][col]:
                text = font.render(game_logic.board.board[row][col], True, TEXT)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)

    current_player_text = font.render(f"Current player: {game_logic.board.current_player}", True, TEXT)
    screen.blit(current_player_text, (20, HEIGHT - 60))

    game_mode_text = font.render(f"Game Mode: {game_logic.game_mode}", True, TEXT)
    screen.blit(game_mode_text, (WIDTH - game_mode_text.get_width() - 20, HEIGHT - 60))

    new_game_button.draw()

    # Draw S and O radio buttons
    letter_label = font.render("Select letter:", True, TEXT)
    screen.blit(letter_label, (50, HEIGHT - 180))
    s_radio.draw()
    o_radio.draw()

if __name__ == "__main__":
    main()
