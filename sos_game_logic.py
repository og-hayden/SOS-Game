class GameBoard:
    def __init__(self, size):
        self.size = size
        self.board = [['' for _ in range(size)] for _ in range(size)]
        self.current_player = 'Blue'
        self.sos_lines = []
        self.blue_score = 0
        self.red_score = 0

    def make_move(self, row, col, letter):
        """Make a move on the board.
        
        Args:
            row (int): Row index
            col (int): Column index
            letter (str): Either 'S' or 'O'
            
        Returns:
            bool: True if move was successful, False otherwise
        """
        if not self.is_valid_move(row, col) or letter not in ['S', 'O']:
            return False
        self.board[row][col] = letter
        return True

    def is_valid_move(self, row, col):
        return 0 <= row < self.size and 0 <= col < self.size and self.board[row][col] == ''

    def switch_player(self):
        self.current_player = 'Red' if self.current_player == 'Blue' else 'Blue'

    def is_full(self):
        """Check if the board is completely filled."""
        for row in self.board:
            for cell in row:
                if cell == '':
                    return False
        return True

    def add_sos_line(self, start_pos, end_pos):
        # Convert positions to tuples for consistent comparison
        line = (tuple(start_pos), tuple(end_pos), self.current_player)
        reverse_line = (tuple(end_pos), tuple(start_pos), self.current_player)
        
        # Check if this line or its reverse already exists
        if line not in self.sos_lines and reverse_line not in self.sos_lines:
            self.sos_lines.append(line)
            if self.current_player == 'Blue':
                self.blue_score += 1
            else:
                self.red_score += 1

class GameLogic:
    def __init__(self, board_size, game_mode):
        self.board = GameBoard(board_size)
        self.game_mode = game_mode
        self.game_over = False
        self.winner = None
        self.sos_formed = False  # New flag to track if SOS was formed

    def make_move(self, row, col, letter):
        """Make a move on the board."""
        # Don't check game_over if we're in a potential draw situation
        if self.game_over and self.winner is not None:
            return False
            
        if not self.board.make_move(row, col, letter):
            return False

        # Check for SOS formation
        self.sos_formed = self.check_sos(row, col)
        
        if self.game_mode == "Simple":
            if self.sos_formed:
                self.game_over = True
                self.winner = self.board.current_player
            else:
                # Check for draw before switching player
                if self.board.is_full():
                    self.game_over = True
                    self.winner = None
                self.board.switch_player()
        else:  # General mode
            if self.board.is_full():
                self.game_over = True
                self.determine_winner()
            self.board.switch_player()
        
        return True

    def check_sos(self, row, col):
        """Check for SOS formations around the last move."""
        letter = self.board.board[row][col]
        
        # Define possible SOS patterns based on the placed letter
        if letter == 'S':
            patterns = [
                [(0, 0), (0, 1), (0, 2)],  # Horizontal right
                [(0, -2), (0, -1), (0, 0)], # Horizontal left
                [(0, 0), (1, 0), (2, 0)],   # Vertical down
                [(-2, 0), (-1, 0), (0, 0)], # Vertical up
                [(0, 0), (1, 1), (2, 2)],   # Diagonal down-right
                [(-2, -2), (-1, -1), (0, 0)], # Diagonal up-left
                [(0, 0), (1, -1), (2, -2)],   # Diagonal down-left
                [(-2, 2), (-1, 1), (0, 0)]    # Diagonal up-right
            ]
        elif letter == 'O':
            patterns = [
                [(-1, 0), (0, 0), (1, 0)],  # Vertical
                [(0, -1), (0, 0), (0, 1)],  # Horizontal
                [(-1, -1), (0, 0), (1, 1)], # Diagonal down-right
                [(-1, 1), (0, 0), (1, -1)]  # Diagonal down-left
            ]
        else:
            return False

        sos_found = False
        for pattern in patterns:
            if self.check_sos_sequence(row, col, pattern):
                start_pos = (row + pattern[0][0], col + pattern[0][1])
                end_pos = (row + pattern[2][0], col + pattern[2][1])
                self.board.add_sos_line(start_pos, end_pos)
                sos_found = True
        return sos_found

    def check_sos_sequence(self, row, col, positions):
        """Check if the three positions form an SOS sequence."""
        try:
            chars = []
            for dx, dy in positions:
                new_row, new_col = row + dx, col + dy
                if not (0 <= new_row < self.board.size and 0 <= new_col < self.board.size):
                    return False
                chars.append(self.board.board[new_row][new_col])
            return chars == ['S', 'O', 'S']
        except IndexError:
            return False

    def determine_winner(self):
        scores = self.get_scores()
        if scores['Blue'] > scores['Red']:
            self.winner = 'Blue'
        elif scores['Red'] > scores['Blue']:
            self.winner = 'Red'
        else:
            self.winner = 'Draw'

    def get_scores(self):
        return {
            'Blue': self.board.blue_score,
            'Red': self.board.red_score
        }

    def get_sos_lines(self):
        return self.board.sos_lines
