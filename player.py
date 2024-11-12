from abc import ABC, abstractmethod
from typing import Tuple, List, Optional, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from sos_game_logic import GameBoard

class Player(ABC):
    """Abstract base class for all players (human and computer)"""
    def __init__(self, symbol: str):
        self.symbol = symbol  # 'Blue' or 'Red'
    
    @abstractmethod
    def make_move(self, board: 'GameBoard') -> Tuple[int, int, str]:
        """Return (row, col, letter) for the next move"""
        pass

class HumanPlayer(Player):
    """Human player implementation"""
    def make_move(self, board: 'GameBoard') -> Tuple[int, int, str]:
        # This will be handled by the UI
        # The UI should validate moves before passing them to the game logic
        pass

class SimpleComputerPlayer(Player):
    """Computer player that makes random moves"""
    def make_move(self, board: 'GameBoard') -> Tuple[int, int, str]:
        # Get all valid moves
        valid_moves = []
        for row in range(board.size):
            for col in range(board.size):
                if board.is_empty(row, col):
                    valid_moves.append((row, col))
        
        # Make a random move
        row, col = random.choice(valid_moves)
        letter = random.choice(['S', 'O'])
        return (row, col, letter)

class AdvancedComputerPlayer(Player):
    """Advanced computer player with strategic moves"""
    def make_move(self, board: 'GameBoard') -> Tuple[int, int, str]:
        """Make a move on the board"""
        print("\nComputer thinking about move...")
        valid_moves = self._get_valid_moves(board)
        
        # Check each position for a winning move with 'S'
        for row, col in valid_moves:
            if self._would_complete_sos(board, row, col, 'S'):
                print(f"Found winning move: S at ({row}, {col})")
                return (row, col, 'S')
                
        # Check each position for a winning move with 'O'
        for row, col in valid_moves:
            if self._would_complete_sos(board, row, col, 'O'):
                print(f"Found winning move: O at ({row}, {col})")
                return (row, col, 'O')
        
        print("No winning move found, trying other strategies...")
        
        # If no winning move, try blocking
        blocking_move = self._find_blocking_move(board, valid_moves)
        if blocking_move:
            return blocking_move
            
        # Try setup move
        setup_move = self._find_setup_move(board, valid_moves)
        if setup_move:
            return setup_move
            
        # Random move as last resort
        row, col = random.choice(valid_moves)
        letter = random.choice(['S', 'O'])
        print(f"Making random move: {(row, col, letter)}")
        return (row, col, letter)

    def _get_valid_moves(self, board: 'GameBoard') -> List[Tuple[int, int]]:
        """Return list of empty cells"""
        valid_moves = []
        for row in range(board.size):
            for col in range(board.size):
                if board.is_empty(row, col):
                    valid_moves.append((row, col))
        return valid_moves

    def _would_complete_sos(self, board: 'GameBoard', row: int, col: int, letter: str) -> bool:
        """Check if placing letter at (row, col) would complete an SOS"""
        if letter == 'S':
            # Check for S-O-_ pattern (where _ is our current position)
            # Check horizontally for S-O-_
            if col == 2:  # We're at the right end
                if board.get_cell(row, 0) == 'S' and board.get_cell(row, 1) == 'O':
                    print(f"Found S-O-_ pattern at ({row}, {col})")
                    return True
                    
            # Check horizontally for _-O-S
            if col == 0:  # We're at the left end
                if board.get_cell(row, 1) == 'O' and board.get_cell(row, 2) == 'S':
                    return True
                    
            # Check vertically for S-O-_
            if row == 2:  # We're at the bottom
                if board.get_cell(0, col) == 'S' and board.get_cell(1, col) == 'O':
                    return True
                    
            # Check vertically for _-O-S
            if row == 0:  # We're at the top
                if board.get_cell(1, col) == 'O' and board.get_cell(2, col) == 'S':
                    return True
                    
            # Check diagonally
            if row == col:  # We're on the main diagonal
                if row == 2 and board.get_cell(0, 0) == 'S' and board.get_cell(1, 1) == 'O':
                    return True
                if row == 0 and board.get_cell(1, 1) == 'O' and board.get_cell(2, 2) == 'S':
                    return True
                    
            # Check other diagonal
            if row + col == 2:  # We're on the other diagonal
                if row == 0 and board.get_cell(1, 1) == 'O' and board.get_cell(2, 0) == 'S':
                    return True
                if row == 2 and board.get_cell(1, 1) == 'O' and board.get_cell(0, 2) == 'S':
                    return True
                    
        return False

    def _find_winning_move(self, board: 'GameBoard', valid_moves: List[Tuple[int, int]]) -> Optional[Tuple[int, int, str]]:
        """Look for moves that complete an SOS"""
        print("Looking for winning move...")
        print(f"Valid moves: {valid_moves}")
        
        # First try 'S' to complete an SOS
        for row, col in valid_moves:
            print(f"Checking S at ({row}, {col})")
            if self._would_complete_sos(board, row, col, 'S'):
                print(f"Found winning move: S at ({row}, {col})")
                return (row, col, 'S')
        
        # Then try 'O' to complete an SOS
        for row, col in valid_moves:
            print(f"Checking O at ({row}, {col})")
            if self._would_complete_sos(board, row, col, 'O'):
                print(f"Found winning move: O at ({row}, {col})")
                return (row, col, 'O')
        
        print("No winning move found")
        return None

    def _find_blocking_move(self, board: 'GameBoard', valid_moves: List[Tuple[int, int]]) -> Optional[Tuple[int, int, str]]:
        """Look for moves that block opponent's potential SOS"""
        # Simulate opponent's next move
        for row, col in valid_moves:
            for letter in ['S', 'O']:
                if self._would_create_opportunity(board, row, col, letter):
                    return (row, col, letter)
        return None

    def _find_setup_move(self, board: 'GameBoard', valid_moves: List[Tuple[int, int]]) -> Optional[Tuple[int, int, str]]:
        """Look for moves that create future opportunities"""
        # Prefer center and corners for 'S'
        center = board.size // 2
        corners = [(0, 0), (0, board.size-1), (board.size-1, 0), (board.size-1, board.size-1)]
        
        # Try center first
        if (center, center) in valid_moves:
            return (center, center, 'S')
        
        # Try corners
        for corner in corners:
            if corner in valid_moves:
                return (*corner, 'S')
        
        # Try to place 'O' between existing 'S's
        for row, col in valid_moves:
            if self._has_adjacent_s(board, row, col):
                return (row, col, 'O')
        
        return None

    def _has_adjacent_s(self, board: 'GameBoard', row: int, col: int) -> bool:
        """Check if there are any 'S's adjacent to the given position"""
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dx, dy in directions:
            new_row, new_col = row + dx, col + dy
            if (0 <= new_row < board.size and 
                0 <= new_col < board.size and 
                board.get_cell(new_row, new_col) == 'S'):
                return True
        return False

    def _would_create_opportunity(self, board: 'GameBoard', row: int, col: int, letter: str) -> bool:
        """Check if a move would create an opportunity for the next move"""
        temp_board = board.copy()
        temp_board.make_move(row, col, letter)
        
        # Check if any subsequent move would complete an SOS
        for r in range(board.size):
            for c in range(board.size):
                if temp_board.is_empty(r, c):
                    for l in ['S', 'O']:
                        if self._would_complete_sos(temp_board, r, c, l):
                            return True
        return False 