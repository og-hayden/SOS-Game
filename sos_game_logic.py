from typing import Dict, List, Tuple, Optional
from player import Player, HumanPlayer, SimpleComputerPlayer, AdvancedComputerPlayer
import pygame

class GameBoard:
    def __init__(self, size):
        self.size = size
        self.board = [['' for _ in range(size)] for _ in range(size)]
        self.current_player = 'Blue'
        self.sos_lines = []
        self.blue_score = 0
        self.red_score = 0

    def make_move(self, row: int, col: int, letter: str) -> bool:
        """Make a move on the board.
        
        Args:
            row (int): Row index
            col (int): Column index
            letter (str): Either 'S' or 'O'
            
        Returns:
            bool: True if move was successful, False otherwise
        """
        if not self.is_valid_move(row, col, letter):
            return False
        self.board[row][col] = letter
        return True

    def is_valid_move(self, row: int, col: int, letter: str) -> bool:
        """Check if a move is valid."""
        return (0 <= row < self.size and 
                0 <= col < self.size and 
                self.board[row][col] == '' and 
                letter in ['S', 'O'])

    def is_empty(self, row: int, col: int) -> bool:
        """Check if a cell is empty."""
        return self.board[row][col] == ''

    def get_cell(self, row: int, col: int) -> str:
        """Get the value of a cell."""
        return self.board[row][col]

    def copy(self) -> 'GameBoard':
        """Create a deep copy of the board."""
        new_board = GameBoard(self.size)
        new_board.board = [row[:] for row in self.board]
        new_board.current_player = self.current_player
        new_board.sos_lines = self.sos_lines.copy()
        new_board.blue_score = self.blue_score
        new_board.red_score = self.red_score
        return new_board

    def check_sos(self, row: int, col: int) -> bool:
        """Check if the last move at (row, col) created an SOS."""
        letter = self.board[row][col]
        if letter not in ['S', 'O']:
            return False

        found_sos = False  # Track if any SOS is found

        # Define all possible SOS patterns
        if letter == 'S':
            # Check for S-O-S patterns starting with this S
            patterns = [
                [(0, 1), (0, 2)],    # Horizontal right
                [(0, -1), (0, -2)],  # Horizontal left
                [(1, 0), (2, 0)],    # Vertical down
                [(-1, 0), (-2, 0)],  # Vertical up
                [(1, 1), (2, 2)],    # Diagonal down-right
                [(-1, -1), (-2, -2)], # Diagonal up-left
                [(1, -1), (2, -2)],  # Diagonal down-left
                [(-1, 1), (-2, 2)]   # Diagonal up-right
            ]
            for pattern in patterns:
                (dr1, dc1), (dr2, dc2) = pattern
                r1, c1 = row + dr1, col + dc1
                r2, c2 = row + dr2, col + dc2
                if (0 <= r1 < self.size and 0 <= c1 < self.size and
                    0 <= r2 < self.size and 0 <= c2 < self.size and
                    self.board[r1][c1] == 'O' and self.board[r2][c2] == 'S'):
                    self.add_sos_line([row, col], [r2, c2])
                    found_sos = True

        elif letter == 'O':
            # Check for S-O-S patterns with this O in the middle
            patterns = [
                [(-1, 0), (1, 0)],   # Vertical
                [(0, -1), (0, 1)],   # Horizontal
                [(-1, -1), (1, 1)],  # Diagonal \
                [(-1, 1), (1, -1)]   # Diagonal /
            ]
            for pattern in patterns:
                (dr1, dc1), (dr2, dc2) = pattern
                r1, c1 = row + dr1, col + dc1
                r2, c2 = row + dr2, col + dc2
                if (0 <= r1 < self.size and 0 <= c1 < self.size and
                    0 <= r2 < self.size and 0 <= c2 < self.size and
                    self.board[r1][c1] == 'S' and self.board[r2][c2] == 'S'):
                    self.add_sos_line([r1, c1], [r2, c2])
                    found_sos = True

        return found_sos

    def switch_player(self):
        """Switch the current player."""
        self.current_player = 'Red' if self.current_player == 'Blue' else 'Blue'

    def is_full(self) -> bool:
        """Check if the board is completely filled."""
        return all(cell != '' for row in self.board for cell in row)

    def add_sos_line(self, start_pos: List[int], end_pos: List[int]):
        """Add an SOS line and update score."""
        # Always store coordinates in consistent order (left to right, or top to bottom)
        if (start_pos[1] > end_pos[1]) or (start_pos[1] == end_pos[1] and start_pos[0] > end_pos[0]):
            start_pos, end_pos = end_pos, start_pos
            
        line = (tuple(start_pos), tuple(end_pos), self.current_player)
        
        if line not in self.sos_lines:
            self.sos_lines.append(line)
            if self.current_player == 'Blue':
                self.blue_score += 1
            else:
                self.red_score += 1

class GameLogic:
    def __init__(self, size: int, game_mode: str, blue_player_type: str = "human", red_player_type: str = "human"):
        self.board = GameBoard(size)
        self.game_mode = game_mode
        self.game_over = False
        self.winner = None
        self.computer_move_timer = None
        self.pending_computer_move = False
        
        # Initialize players
        self.players = {
            'Blue': self._create_player('Blue', blue_player_type),
            'Red': self._create_player('Red', red_player_type)
        }

    def _create_player(self, symbol: str, player_type: str) -> Player:
        """Create appropriate player based on type"""
        if player_type.lower() == "human":
            return HumanPlayer(symbol)
        elif player_type.lower() == "simple_computer":
            return SimpleComputerPlayer(symbol)
        elif player_type.lower() == "smart_computer":
            return AdvancedComputerPlayer(symbol)
        else:
            raise ValueError(f"Invalid player type: {player_type}")

    def make_move(self, row: int, col: int, letter: str) -> bool:
        """Make a move and handle game logic"""
        if self.game_over:
            return False

        print(f"Attempting move: {letter} at ({row}, {col})")  # Debug print
        
        # Make the move
        if not self.board.make_move(row, col, letter):
            return False

        # Process the move
        self._process_move(row, col)

        # Schedule computer move if it's computer's turn and this wasn't a computer move
        if (not self.game_over and 
            not self.pending_computer_move and  # Only schedule if not already pending
            isinstance(self.players[self.board.current_player], (SimpleComputerPlayer, AdvancedComputerPlayer))):
            self.pending_computer_move = True
            self.computer_move_timer = pygame.time.get_ticks()

        return True

    def update(self):
        """Update game state - call this in your game loop"""
        if self.pending_computer_move and pygame.time.get_ticks() - self.computer_move_timer >= 500:
            self._make_computer_move()
            self.pending_computer_move = False

    def _process_move(self, row: int, col: int):
        """Process a move and update game state"""
        sos_formed = self.board.check_sos(row, col)
        
        # Handle game over conditions
        if self.game_mode == "Simple" and sos_formed:
            self.game_over = True
            self.winner = self.board.current_player
        elif self.board.is_full():
            self.game_over = True
            if self.game_mode == "General":
                if self.board.blue_score > self.board.red_score:
                    self.winner = 'Blue'
                elif self.board.red_score > self.board.blue_score:
                    self.winner = 'Red'
                else:
                    self.winner = 'Draw'

        # Switch player if no SOS was formed OR if in General mode
        # This ensures the game continues in General mode even after an SOS is formed
        if not sos_formed or self.game_mode == "General":
            self.board.switch_player()

    def _make_computer_move(self):
        """Handle computer move"""
        if self.game_over:
            return

        current_player = self.board.current_player
        computer = self.players[current_player]
        
        try:
            # Get the computer's move
            comp_row, comp_col, comp_letter = computer.make_move(self.board)
            print(f"Computer ({current_player}) plays: {comp_letter} at ({comp_row}, {comp_col})")
            
            # Temporarily clear pending_computer_move to allow the move
            was_pending = self.pending_computer_move
            self.pending_computer_move = False
            
            # Make the move
            success = self.make_move(comp_row, comp_col, comp_letter)
            
            # Restore pending state if move failed
            if not success:
                self.pending_computer_move = was_pending
                print(f"Invalid computer move: {comp_letter} at ({comp_row}, {comp_col})")
                
        except Exception as e:
            print(f"Error during computer move: {e}")

    def get_scores(self) -> Dict[str, int]:
        """Get the current scores"""
        return {
            'Blue': self.board.blue_score,
            'Red': self.board.red_score
        }

    def get_sos_lines(self) -> List[Tuple[Tuple[int, int], Tuple[int, int], str]]:
        """Get the list of SOS lines"""
        return self.board.sos_lines.copy()

    def get_current_player(self) -> str:
        """Get the current player"""
        return self.board.current_player

    def is_game_over(self) -> bool:
        """Check if the game is over"""
        return self.game_over

    def get_winner(self) -> Optional[str]:
        """Get the winner of the game"""
        return self.winner

    def get_board_size(self) -> int:
        """Get the size of the game board"""
        return self.board.size

    def get_cell(self, row: int, col: int) -> str:
        """Get the value of a cell on the board"""
        return self.board.get_cell(row, col)
