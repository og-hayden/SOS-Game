import pygame
import sys

pygame.init()

# Colors
BACKGROUND = (240, 248, 255)
TEXT = (70, 130, 180)
BUTTON = (100, 149, 237)
BUTTON_HOVER = (30, 144, 255)
LINE = (176, 196, 222)

# Screen setup
WIDTH, HEIGHT = 400, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SOS Game Setup")

# Fonts
font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 24)

class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False

    def draw(self):
        color = BUTTON_HOVER if self.hovered else BUTTON
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
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
        self.rect = pygame.Rect(x, y, 20, 20)
        self.text = text
        self.checked = False

    def draw(self):
        pygame.draw.rect(screen, TEXT, self.rect, 2)
        if self.checked:
            pygame.draw.line(screen, TEXT, (self.rect.left + 3, self.rect.centery),
                             (self.rect.centerx, self.rect.bottom - 3), 2)
            pygame.draw.line(screen, TEXT, (self.rect.centerx, self.rect.bottom - 3),
                             (self.rect.right - 3, self.rect.top + 3), 2)
        text_surf = small_font.render(self.text, True, TEXT)
        screen.blit(text_surf, (self.rect.right + 10, self.rect.centery - text_surf.get_height() // 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked

class RadioButton:
    def __init__(self, x, y, text, group):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.text = text
        self.group = group
        self.selected = False

    def draw(self):
        pygame.draw.circle(screen, TEXT, self.rect.center, 10, 2)
        if self.selected:
            pygame.draw.circle(screen, TEXT, self.rect.center, 6)
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
    print(f"AI opponent: {'Yes' if ai_checkbox.checked else 'No'}")
    print(f"Board size: {next(btn.text for btn in board_size_group.buttons if btn.selected)}")

# Create UI elements
title = font.render("Welcome to the SOS Game Setup", True, TEXT)
ai_checkbox = Checkbox(50, 150, "Enable AI opponent")
board_size_group = RadioGroup()
board_size_group.add(RadioButton(50, 250, "3x3", board_size_group))
board_size_group.add(RadioButton(50, 290, "4x4", board_size_group))
board_size_group.add(RadioButton(50, 330, "5x5", board_size_group))
start_button = Button(WIDTH // 2 - 60, HEIGHT - 80, 120, 40, "Start Game", start_game)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        ai_checkbox.handle_event(event)
        for btn in board_size_group.buttons:
            btn.handle_event(event)
        start_button.handle_event(event)

    screen.fill(BACKGROUND)

    # Draw title
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

    # Draw lines
    pygame.draw.line(screen, LINE, (30, 100), (WIDTH - 30, 100), 2)
    pygame.draw.line(screen, LINE, (30, 200), (WIDTH - 30, 200), 2)
    pygame.draw.line(screen, LINE, (30, 370), (WIDTH - 30, 370), 2)

    # Draw UI elements
    ai_checkbox.draw()
    for btn in board_size_group.buttons:
        btn.draw()
    start_button.draw()

    # Draw labels
    board_size_label = font.render("Select board size:", True, TEXT)
    screen.blit(board_size_label, (50, 210))

    pygame.display.flip()

pygame.quit()
sys.exit()