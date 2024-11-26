import pygame
import sys
from sos_game_logic import GameLogic, GameBoard
from typing import Optional, List, Dict, Tuple
from database import GameDatabase
import logging

pygame.init()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Colors
BACKGROUND = (24, 24, 27)  # zinc-900
TEXT = (161, 161, 170)  # zinc-400
BUTTON = (63, 63, 70)  # zinc-700
BUTTON_HOVER = (82, 82, 91)  # zinc-600
LINE = (113, 113, 122)  # zinc-500
BOARD_BG = (39, 39, 42)  # zinc-800
TITLE_COLOR = (244, 244, 245)  # zinc-100

# Screen setup
WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SOS Game")

# Fonts
font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 64)

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

class AIControls:
    def __init__(self):
        self.enabled = Checkbox(50, 120, "Enable AI players")
        
        # Blue player controls
        self.blue_group = RadioGroup()
        self.blue_human = RadioButton(80, 190, "Human", self.blue_group)
        self.blue_simple = RadioButton(80, 220, "Simple AI", self.blue_group)
        self.blue_advanced = RadioButton(80, 250, "Advanced AI", self.blue_group)
        self.blue_group.add(self.blue_human)
        self.blue_group.add(self.blue_simple)
        self.blue_group.add(self.blue_advanced)
        
        # Red player controls
        self.red_group = RadioGroup()
        self.red_human = RadioButton(400, 190, "Human", self.red_group)
        self.red_simple = RadioButton(400, 220, "Simple AI", self.red_group)
        self.red_advanced = RadioButton(400, 250, "Advanced AI", self.red_group)
        self.red_group.add(self.red_human)
        self.red_group.add(self.red_simple)
        self.red_group.add(self.red_advanced)

    def draw(self):
        self.enabled.draw()
        
        if self.enabled.checked:
            # Draw player labels with better spacing
            blue_label = font.render("Blue Player:", True, (0, 0, 255))
            red_label = font.render("Red Player:", True, (255, 0, 0))
            screen.blit(blue_label, (80, 160))
            screen.blit(red_label, (400, 160))
            
            for button in self.blue_group.buttons:
                button.draw()
            for button in self.red_group.buttons:
                button.draw()

    def handle_event(self, event):
        self.enabled.handle_event(event)
        if self.enabled.checked:
            for button in self.blue_group.buttons:
                button.handle_event(event)
            for button in self.red_group.buttons:
                button.handle_event(event)

    def get_player_types(self) -> Tuple[str, str]:
        """Get the selected player types for blue and red players"""
        if not self.enabled.checked:
            return "human", "human"
        
        blue_type = "human"
        if self.blue_simple.selected:
            blue_type = "simple_computer"
        elif self.blue_advanced.selected:
            blue_type = "smart_computer"
            
        red_type = "human"
        if self.red_simple.selected:
            red_type = "simple_computer"
        elif self.red_advanced.selected:
            red_type = "smart_computer"
            
        return blue_type, red_type

# Replace the old AI controls with the new class
ai_controls = AIControls()

# Board size options (moved down)
board_size_group = RadioGroup()
board_size_group.add(RadioButton(50, 310, "3x3", board_size_group))
board_size_group.add(RadioButton(50, 350, "4x4", board_size_group))
board_size_group.add(RadioButton(50, 390, "5x5", board_size_group))

def start_game():
    global game_logic, game_started, game_over
    board_size = int(next(btn.text[0] for btn in board_size_group.buttons if btn.selected))
    game_mode = "Simple" if simple_mode_radio.selected else "General"
    
    # Get player types from AI controls
    blue_player_type, red_player_type = ai_controls.get_player_types()
    
    game_logic = GameLogic(
        size=board_size, 
        game_mode=game_mode,
        blue_player_type=blue_player_type,
        red_player_type=red_player_type
    )
    
    game_started = True
    game_over = False  # Reset game_over flag
    logging.info(f"Starting new game: Size {board_size}x{board_size}, Mode: {game_mode}")
    logging.info(f"Blue Player: {blue_player_type}, Red Player: {red_player_type}")

def new_game():
    global game_started, game_logic, game_over
    game_started = False
    game_over = False
    
    # If game was in progress, save its state before ending
    if game_logic:
        if game_logic.game_over:
            try:
                game_logic.db.end_game(
                    game_logic.game_id,
                    game_logic.winner,
                    game_logic.board.blue_score,
                    game_logic.board.red_score
                )
                logging.info(f"Saved final state for game {game_logic.game_id}")
            except Exception as e:
                logging.error(f"Error saving game end state: {e}")
        
        # Stop the game completely
        game_logic.stop()
    
    # Refresh the replay screen if it exists
    if replay_screen:
        replay_screen.refresh_games()

# Create UI elements
title = title_font.render("SOS Game", True, TITLE_COLOR)
start_button = Button(WIDTH // 2 - 80, HEIGHT - 100, 160, 50, "Start Game", start_game)
new_game_button = Button(WIDTH - 180, 20, 160, 50, "New Game", new_game)

mode_group = RadioGroup()
simple_mode_radio = RadioButton(50, 480, "Simple Game", mode_group)
general_mode_radio = RadioButton(50, 520, "General Game", mode_group)
mode_group.add(simple_mode_radio)
mode_group.add(general_mode_radio)

letter_group = RadioGroup()
s_radio = RadioButton(50, HEIGHT - 150, "S", letter_group)
o_radio = RadioButton(50, HEIGHT - 110, "O", letter_group)
letter_group.add(s_radio)
letter_group.add(o_radio)

game_logic = None
game_started = False
game_over = False

REPLAY_MOVE_DELAY = 1000  # 1 second between moves

class ReplayScreen:
    def __init__(self, screen, db: GameDatabase):
        self.screen = screen
        self.db = db
        self.selected_game: Optional[Dict] = None
        self.moves: List[Dict] = []
        self.current_move_index = 0
        self.replay_board: Optional[GameBoard] = None
        self.last_move_time = 0
        self.is_playing = False
        self.back_button = Button(20, 20, 100, 40, "Back", self.go_back)
        self.refresh_games()  # Initial load of games
        self.sos_lines = []
        self.current_sos_index = 0
        self.blue_score = 0
        self.red_score = 0
        
    def refresh_games(self):
        """Refresh the list of games from the database"""
        self.games = self.db.get_recent_games()
        logging.info(f"Refreshed games list - Found {len(self.games)} recent games")
        for game in self.games:
            logging.info(f"Game ID: {game['game_id']}, Mode: {game['game_mode']}, Winner: {game['winner']}")
        
        # Recreate game list buttons
        self.game_buttons = []
        for i, game in enumerate(self.games):
            y_pos = 100 + i * 60
            button_text = f"Game {game['game_id']} - {game['game_mode']} - Winner: {game['winner']}"
            self.game_buttons.append(
                Button(50, y_pos, 400, 50, button_text, lambda g=game: self.select_game(g))
            )

    def select_game(self, game: Dict):
        self.selected_game = game
        self.moves = self.db.get_game_moves(game['game_id'])
        self.sos_lines = self.db.get_game_sos_lines(game['game_id'])
        logging.info(f"Selected game {game['game_id']}, found {len(self.moves)} moves and {len(self.sos_lines)} SOS lines")
        self.current_move_index = 0
        self.current_sos_index = 0
        self.replay_board = GameBoard(game['board_size'])
        self.is_playing = True
        self.last_move_time = pygame.time.get_ticks()
        self.visible_sos_lines = []
        self.blue_score = 0
        self.red_score = 0

    def go_back(self):
        global game_started, viewing_replays  # Add viewing_replays
        logging.info("Exiting replay screen")
        viewing_replays = False  # Set this to False instead of game_started
        self.selected_game = None

    def update(self):
        if self.is_playing and self.selected_game:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_move_time >= REPLAY_MOVE_DELAY:
                if self.current_move_index < len(self.moves):
                    move = self.moves[self.current_move_index]
                    self.replay_board.make_move(move['row'], move['col'], move['letter'])
                    
                    # Update SOS lines and scores based on move number
                    while (self.current_sos_index < len(self.sos_lines) and 
                           self.sos_lines[self.current_sos_index]['move_number'] <= self.current_move_index + 1):
                        sos_line = self.sos_lines[self.current_sos_index]
                        self.visible_sos_lines.append((
                            sos_line['start_pos'],
                            sos_line['end_pos'],
                            sos_line['player']
                        ))
                        if sos_line['player'] == 'Blue':
                            self.blue_score += 1
                        else:
                            self.red_score += 1
                        self.current_sos_index += 1
                        logging.info(f"Added SOS line for {sos_line['player']}, scores now Blue: {self.blue_score}, Red: {self.red_score}")
                    
                    self.current_move_index += 1
                    self.last_move_time = current_time
                else:
                    self.is_playing = False

    def draw(self):
        self.screen.fill(BACKGROUND)
        self.back_button.draw()

        if not self.selected_game:
            # Draw game list
            title = title_font.render("Recent Games", True, TITLE_COLOR)
            self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))
            
            for button in self.game_buttons:
                button.draw()
        else:
            # Draw replay board
            board_size = self.replay_board.size
            cell_size = min((WIDTH - 400) // board_size, (HEIGHT - 250) // board_size)
            board_width = cell_size * board_size
            board_height = cell_size * board_size
            board_left = (WIDTH - board_width) // 2 + 100
            board_top = 150

            # Draw board background
            pygame.draw.rect(self.screen, BOARD_BG, 
                           (board_left - 10, board_top - 10, 
                            board_width + 20, board_height + 20), 
                           border_radius=15)
            
            # Draw grid and moves
            for row in range(board_size):
                for col in range(board_size):
                    rect = pygame.Rect(
                        board_left + col * cell_size,
                        board_top + row * cell_size,
                        cell_size,
                        cell_size
                    )
                    pygame.draw.rect(self.screen, LINE, rect, 1)
                    
                    cell_value = self.replay_board.get_cell(row, col)
                    if cell_value:
                        text = font.render(cell_value, True, TEXT)
                        text_rect = text.get_rect(center=rect.center)
                        self.screen.blit(text, text_rect)

            # Draw SOS lines
            for start_pos, end_pos, player in self.visible_sos_lines:
                start_x = board_left + start_pos[1] * cell_size + cell_size // 2
                start_y = board_top + start_pos[0] * cell_size + cell_size // 2
                end_x = board_left + end_pos[1] * cell_size + cell_size // 2
                end_y = board_top + end_pos[0] * cell_size + cell_size // 2
                color = (0, 0, 255) if player == 'Blue' else (255, 0, 0)
                pygame.draw.line(self.screen, color, (start_x, start_y), (end_x, end_y), 3)

            # Draw game info
            info_text = [
                f"Game Mode: {self.selected_game['game_mode']}",
                f"Blue: {self.selected_game['blue_player_type']}",
                f"Red: {self.selected_game['red_player_type']}",
                f"Move: {self.current_move_index}/{len(self.moves)}"
            ]
            
            for i, text in enumerate(info_text):
                surf = font.render(text, True, TEXT)
                self.screen.blit(surf, (20, 100 + i * 30))

            # Draw scores
            blue_score_text = font.render(f"Blue Score: {self.blue_score}", True, (0, 0, 255))
            red_score_text = font.render(f"Red Score: {self.red_score}", True, (255, 0, 0))
            self.screen.blit(blue_score_text, (20, HEIGHT - 80))
            self.screen.blit(red_score_text, (20, HEIGHT - 40))

    def handle_event(self, event):
        self.back_button.handle_event(event)
        if not self.selected_game:
            for button in self.game_buttons:
                button.handle_event(event)

# Add after other global variables
replay_screen = None
viewing_replays = False

def main():
    global game_logic, game_started, replay_screen, viewing_replays, game_over

    # Initialize replay screen
    replay_screen = ReplayScreen(screen, GameDatabase())
    logging.info("Game started")
    clock = pygame.time.Clock()  # Add this for consistent frame rate

    running = True
    while running:
        clock.tick(60)  # Limit to 60 FPS
        
        # Only update game logic if game is started and not viewing replays
        if game_logic and not game_over and not viewing_replays:
            game_logic.update()
            if game_logic.game_over and not game_over:
                game_over = True
                logging.info("Game ended - Refreshing replay list")
                replay_screen.refresh_games()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Stop game before quitting
                if game_logic:
                    game_logic.stop()
                    if game_logic.game_over:
                        try:
                            game_logic.db.end_game(
                                game_logic.game_id,
                                game_logic.winner,
                                game_logic.board.blue_score,
                                game_logic.board.red_score
                            )
                        except Exception as e:
                            logging.error(f"Error saving game end state: {e}")
                running = False

            if viewing_replays:
                replay_screen.handle_event(event)
            elif not game_started:
                # Handle menu events
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    replay_button_rect = pygame.Rect(WIDTH // 2 - 80, HEIGHT - 160, 160, 50)
                    if replay_button_rect.collidepoint(event.pos):
                        replay_screen.refresh_games()
                        viewing_replays = True
                        logging.info("Entering replay screen")
                        continue
                    
                    # Handle menu buttons
                    start_button.handle_event(event)
                    ai_controls.handle_event(event)  # Handle AI controls events
                    for btn in board_size_group.buttons:
                        btn.handle_event(event)
                    simple_mode_radio.handle_event(event)
                    general_mode_radio.handle_event(event)
            else:
                # Handle game events
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    new_game_button.handle_event(event)
                    
                    # Only handle board clicks for human players
                    current_player = game_logic.board.current_player
                    current_player_type = (game_logic.players[current_player].__class__.__name__)
                    
                    if current_player_type == "HumanPlayer":
                        s_radio.handle_event(event)
                        o_radio.handle_event(event)

                        # Handle board clicks
                        if not game_logic.game_over and not game_logic.pending_computer_move:
                            board_size = game_logic.board.size
                            cell_size = min((WIDTH - 400) // board_size, (HEIGHT - 250) // board_size)
                            board_left = (WIDTH - board_size * cell_size) // 2 + 100
                            board_top = 150

                            mouse_x, mouse_y = event.pos
                            if (board_left <= mouse_x <= board_left + board_size * cell_size and
                                board_top <= mouse_y <= board_top + board_size * cell_size):
                                col = (mouse_x - board_left) // cell_size
                                row = (mouse_y - board_top) // cell_size
                                letter = 'S' if s_radio.selected else 'O'
                                game_logic.make_move(int(row), int(col), letter)

        # Draw current screen
        screen.fill(BACKGROUND)

        if viewing_replays:
            replay_screen.update()
            replay_screen.draw()
        elif not game_started:
            draw_menu()
            replay_button = Button(WIDTH // 2 - 80, HEIGHT - 160, 160, 50, "View Replays", lambda: None)
            replay_button.draw()
        else:
            draw_game()

        pygame.display.flip()

    pygame.quit()
    sys.exit()

def draw_menu():
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))
    
    # Adjust spacing of horizontal lines
    pygame.draw.line(screen, LINE, (30, 90), (WIDTH - 30, 90), 3)     # Below title
    pygame.draw.line(screen, LINE, (30, 300), (WIDTH - 30, 300), 3)   # Below AI controls
    pygame.draw.line(screen, LINE, (30, 460), (WIDTH - 30, 460), 3)   # Below board size

    # Draw AI controls
    ai_controls.draw()

    # Draw board size options with adjusted spacing
    board_size_label = font.render("Select board size:", True, TEXT)
    screen.blit(board_size_label, (50, 330))  # Moved down
    
    # Adjust board size radio buttons
    board_size_group.buttons[0].rect.y = 370  # 3x3
    board_size_group.buttons[1].rect.y = 400  # 4x4
    board_size_group.buttons[2].rect.y = 430  # 5x5
    
    for btn in board_size_group.buttons:
        btn.draw()

    # Draw game mode options
    mode_label = font.render("Select game mode:", True, TEXT)
    screen.blit(mode_label, (50, 490))  # Moved down
    
    # Adjust game mode radio buttons
    simple_mode_radio.rect.y = 520
    general_mode_radio.rect.y = 550
    simple_mode_radio.draw()
    general_mode_radio.draw()

    # Draw buttons at the bottom
    replay_button = Button(WIDTH // 2 - 80, HEIGHT - 160, 160, 50, "View Replays", lambda: None)
    replay_button.draw()
    start_button.draw()  # Already positioned at HEIGHT - 100

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

    # Only show letter selection for human players
    current_player = game_logic.board.current_player
    current_player_type = (game_logic.players[current_player].__class__.__name__)
    
    if current_player_type == "HumanPlayer":
        # Draw S and O radio buttons
        letter_label = font.render("Select letter:", True, TEXT)
        screen.blit(letter_label, (50, HEIGHT - 180))
        s_radio.draw()
        o_radio.draw()

    # Draw SOS lines
    for start_pos, end_pos, player in game_logic.get_sos_lines():
        start_x = board_left + start_pos[1] * cell_size + cell_size // 2
        start_y = board_top + start_pos[0] * cell_size + cell_size // 2
        end_x = board_left + end_pos[1] * cell_size + cell_size // 2
        end_y = board_top + end_pos[0] * cell_size + cell_size // 2
        color = (0, 0, 255) if player == 'Blue' else (255, 0, 0)  # Blue or Red
        pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), 3)

    # Draw scores for General game mode
    if game_logic.game_mode == "General":
        scores = game_logic.get_scores()
        blue_score = font.render(f"Blue: {scores['Blue']}", True, (0, 0, 255))
        red_score = font.render(f"Red: {scores['Red']}", True, (255, 0, 0))
        screen.blit(blue_score, (20, 20))
        screen.blit(red_score, (20, 60))

    # Show winner if game is over
    if game_logic.game_over:
        winner_text = font.render(
            f"Winner: {game_logic.winner}" if game_logic.winner != 'Draw' else "Game Draw!",
            True, TEXT
        )
        screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, 20))

if __name__ == "__main__":
    main()
