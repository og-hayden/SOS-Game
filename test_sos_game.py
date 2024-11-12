import unittest
from sos_game_logic import GameLogic, GameBoard
from player import SimpleComputerPlayer, AdvancedComputerPlayer
import pygame

class TestGameLogicInitialization(unittest.TestCase):

    def test_initialize_3x3_board(self):
        """Test if GameLogic initializes with a 3x3 GameBoard"""
        game_logic = GameLogic(3, "Simple")
        self.assertIsInstance(game_logic.board, GameBoard)
        self.assertEqual(game_logic.board.size, 3)

    def test_initialize_4x4_board(self):
        """Test if GameLogic initializes with a 4x4 GameBoard"""
        game_logic = GameLogic(4, "Simple")
        self.assertIsInstance(game_logic.board, GameBoard)
        self.assertEqual(game_logic.board.size, 4)

    def test_initialize_5x5_board(self):
        """Test if GameLogic initializes with a 5x5 GameBoard"""
        game_logic = GameLogic(5, "Simple")
        self.assertIsInstance(game_logic.board, GameBoard)
        self.assertEqual(game_logic.board.size, 5)

    def test_initialize_simple_game_mode(self):
        """Test if GameLogic initializes with Simple game mode"""
        game_logic = GameLogic(3, "Simple")
        self.assertEqual(game_logic.game_mode, "Simple")

    def test_initialize_general_game_mode(self):
        """Test if GameLogic initializes with General game mode"""
        game_logic = GameLogic(3, "General")
        self.assertEqual(game_logic.game_mode, "General")

class TestGamePlay(unittest.TestCase):

    def test_start_game_4x4_simple(self):
        """Test starting a new 4x4 Simple game"""
        game_logic = GameLogic(4, "Simple")
        self.assertEqual(game_logic.board.size, 4)
        self.assertEqual(game_logic.game_mode, "Simple")

    def test_start_game_5x5_general(self):
        """Test starting a new 5x5 General game"""
        game_logic = GameLogic(5, "General")
        self.assertEqual(game_logic.board.size, 5)
        self.assertEqual(game_logic.game_mode, "General")

    def test_make_move_simple_game(self):
        """Test making a move in a Simple game"""
        game_logic = GameLogic(3, "Simple")
        initial_player = game_logic.board.current_player
        self.assertTrue(game_logic.make_move(0, 0, 'S'))
        self.assertNotEqual(game_logic.board.current_player, initial_player)

    def test_invalid_move_simple_game(self):
        """Test making an invalid move in a Simple game"""
        game_logic = GameLogic(3, "Simple")
        initial_player = game_logic.board.current_player
        game_logic.make_move(0, 0, 'S')
        self.assertFalse(game_logic.make_move(0, 0, 'O'))
        self.assertNotEqual(game_logic.board.current_player, initial_player)

    def test_make_move_general_game(self):
        """Test making a move in a General game"""
        game_logic = GameLogic(3, "General")
        initial_player = game_logic.board.current_player
        self.assertTrue(game_logic.make_move(0, 0, 'O'))
        self.assertNotEqual(game_logic.board.current_player, initial_player)

    def test_make_move_general_game_sos(self):
        """Test making a move that forms SOS in a General game"""
        game_logic = GameLogic(3, "General")
        initial_player = game_logic.board.current_player
        
        # Create an SOS sequence
        game_logic.make_move(0, 0, 'S')
        game_logic.make_move(0, 1, 'O')
        self.assertTrue(game_logic.make_move(0, 2, 'S'))
        
        # Check that a point was awarded
        scores = game_logic.get_scores()
        self.assertEqual(scores[initial_player], 1)
        
        # Check that the SOS line was recorded
        sos_lines = game_logic.get_sos_lines()
        self.assertEqual(len(sos_lines), 1)
        self.assertEqual(sos_lines[0], ((0, 0), (0, 2), initial_player))

    def test_simple_game_win(self):
        """Test winning condition in Simple game mode"""
        game_logic = GameLogic(3, "Simple")
        initial_player = game_logic.board.current_player
        
        # Create an SOS sequence
        game_logic.make_move(0, 0, 'S')
        game_logic.make_move(0, 1, 'O')
        game_logic.make_move(0, 2, 'S')
        
        self.assertTrue(game_logic.game_over)
        self.assertEqual(game_logic.winner, initial_player)

    def test_general_game_scoring(self):
        """Test scoring in General game mode"""
        game_logic = GameLogic(3, "General")
        
        # Blue player creates an SOS
        game_logic.make_move(0, 0, 'S')
        game_logic.make_move(0, 1, 'O')
        game_logic.make_move(0, 2, 'S')
        
        # Red player creates an SOS
        game_logic.make_move(1, 0, 'S')
        game_logic.make_move(1, 1, 'O')
        game_logic.make_move(1, 2, 'S')
        
        scores = game_logic.get_scores()
        self.assertEqual(scores['Blue'], 1)
        self.assertEqual(scores['Red'], 1)

    def test_simple_game_over_with_sos(self):
        """Test game over condition in Simple mode when SOS is formed"""
        game_logic = GameLogic(3, "Simple")
        
        # Create an SOS sequence
        game_logic.make_move(0, 0, 'S')
        game_logic.make_move(0, 1, 'O')
        game_logic.make_move(0, 2, 'S')
        
        self.assertTrue(game_logic.game_over)
        self.assertIsNotNone(game_logic.winner)
        self.assertNotEqual(game_logic.winner, 'Draw')

    def test_simple_game_draw(self):
        """Test draw condition in Simple mode when board is full without SOS"""
        game_logic = GameLogic(3, "Simple")
        
        # Fill board without forming SOS - using alternating O and S pattern
        moves = [
            (0, 0, 'O'), (0, 1, 'O'), (0, 2, 'O'),
            (1, 0, 'S'), (1, 1, 'S'), (1, 2, 'S'),
            (2, 0, 'O'), (2, 1, 'O'), (2, 2, 'O')
        ]
        
        # Make each move and verify it's successful
        for row, col, letter in moves:
            success = game_logic.make_move(row, col, letter)
            self.assertTrue(success, f"Move at ({row}, {col}) with {letter} failed")
        
        # Verify final state
        self.assertTrue(game_logic.board.is_full(), "Board should be full")
        self.assertTrue(game_logic.game_over, "Game should be over")
        self.assertIsNone(game_logic.winner, "There should be no winner")

    def test_general_game_over_full_board(self):
        """Test game over condition in General mode when board is full"""
        game_logic = GameLogic(3, "General")
        
        # Fill the board with some moves
        moves = [
            (0, 0, 'S'), (0, 1, 'O'), (0, 2, 'S'),  # Forms SOS
            (1, 0, 'O'), (1, 1, 'S'), (1, 2, 'O'),
            (2, 0, 'S'), (2, 1, 'O'), (2, 2, 'S')   # Forms SOS
        ]
        
        for row, col, letter in moves:
            game_logic.make_move(row, col, letter)
        
        self.assertTrue(game_logic.board.is_full())
        self.assertTrue(game_logic.game_over)
        self.assertIsNotNone(game_logic.winner)

    def test_general_game_draw(self):
        """Test draw condition in General mode when scores are equal"""
        game_logic = GameLogic(3, "General")
        
        # Both players make one SOS each
        # Blue player's SOS
        game_logic.make_move(0, 0, 'S')
        game_logic.make_move(0, 1, 'O')
        game_logic.make_move(0, 2, 'S')
        
        # Red player's SOS
        game_logic.make_move(1, 0, 'S')
        game_logic.make_move(1, 1, 'O')
        game_logic.make_move(1, 2, 'S')
        
        # Fill remaining cells
        game_logic.make_move(2, 0, 'O')
        game_logic.make_move(2, 1, 'O')
        game_logic.make_move(2, 2, 'O')
        
        self.assertTrue(game_logic.board.is_full())
        self.assertTrue(game_logic.game_over)
        self.assertEqual(game_logic.winner, 'Draw')
        
        # Verify scores are equal
        scores = game_logic.get_scores()
        self.assertEqual(scores['Blue'], scores['Red'])

    def test_game_not_over_when_moves_remain(self):
        """Test game is not over when valid moves remain"""
        game_logic = GameLogic(3, "General")
        
        # Make some moves but don't fill board
        game_logic.make_move(0, 0, 'S')
        game_logic.make_move(0, 1, 'O')
        
        self.assertFalse(game_logic.board.is_full())
        self.assertFalse(game_logic.game_over)
        self.assertIsNone(game_logic.winner)

class TestComputerPlayer(unittest.TestCase):
    def test_computer_player_creation(self):
        """Test if computer players are correctly created with specified types"""
        game_logic = GameLogic(3, "Simple", "human", "simple_computer")
        self.assertIsInstance(game_logic.players['Red'], SimpleComputerPlayer)
        
        game_logic = GameLogic(3, "Simple", "human", "smart_computer")
        self.assertIsInstance(game_logic.players['Red'], AdvancedComputerPlayer)

    def test_computer_valid_move(self):
        """Test if computer makes valid moves"""
        game_logic = GameLogic(3, "Simple", "human", "simple_computer")
        # Make human move first
        game_logic.make_move(0, 0, 'S')
        # Trigger computer move
        game_logic._make_computer_move()
        
        # Count filled cells to verify computer made a move
        filled_cells = sum(1 for row in game_logic.board.board 
                         for cell in row if cell != '')
        self.assertEqual(filled_cells, 2)

    def test_computer_sos_completion(self):
        """Test if advanced computer player can complete SOS when possible"""
        # Create game with advanced computer player as Red
        game_logic = GameLogic(3, "Simple", "human", "smart_computer")
        
        # Set up the board state directly
        game_logic.board.board[0][0] = 'S'  # First S
        game_logic.board.board[0][1] = 'O'  # Middle O
        game_logic.board.current_player = 'Red'  # Make sure it's computer's turn
        
        # Print board state before computer move
        print("\nBoard state before computer move:")
        for row in range(game_logic.board.size):
            print([game_logic.board.get_cell(row, c) for c in range(game_logic.board.size)])
        
        # Get the computer's move directly
        computer_player = game_logic.players['Red']
        row, col, letter = computer_player.make_move(game_logic.board)
        
        # Make the move
        game_logic.make_move(row, col, letter)
        
        # Print board state after computer move
        print("\nBoard state after computer move:")
        for row in range(game_logic.board.size):
            print([game_logic.board.get_cell(row, c) for c in range(game_logic.board.size)])
        
        # Verify the computer completed the SOS by checking the board state
        self.assertEqual(game_logic.board.get_cell(0, 2), 'S')  # Should be an S in the right position
        self.assertTrue(game_logic.game_over)  # Game should be over
        self.assertEqual(game_logic.winner, 'Red')  # Computer (Red) should win

    def test_computer_move_timing(self):
        """Test if computer moves have appropriate delay"""
        game_logic = GameLogic(3, "Simple", "human", "simple_computer")
        game_logic.make_move(0, 0, 'S')
        
        # Set pending computer move
        game_logic.pending_computer_move = True
        game_logic.computer_move_timer = pygame.time.get_ticks()
        
        # Update immediately - should not make move
        game_logic.update()
        self.assertTrue(game_logic.pending_computer_move)
        
        # Simulate time passing (500ms)
        game_logic.computer_move_timer -= 501
        game_logic.update()
        self.assertFalse(game_logic.pending_computer_move)

if __name__ == '__main__':
    unittest.main()
