import unittest
from sos_game_logic import GameLogic, GameBoard

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

    # TODO: Implement this test when SOS checking logic is completed
    # def test_make_move_general_game_sos(self):
    #     """Test making a move that forms SOS in a General game"""
    #     game_logic = GameLogic(3, "General")
    #     initial_player = game_logic.board.current_player
    #     game_logic.make_move(0, 0, 'S')
    #     game_logic.make_move(0, 1, 'O')
    #     self.assertTrue(game_logic.make_move(0, 2, 'S'))
    #     self.assertEqual(game_logic.board.current_player, initial_player)

if __name__ == '__main__':
    unittest.main()
