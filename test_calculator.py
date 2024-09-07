import unittest
from calculator import Calculator

class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()
    
    def test_add(self):
        self.assertEqual(self.calc.add(3, 5), 8)
        self.assertEqual(self.calc.add(-1, 1), 0)
    
    def test_subtract(self):
        self.assertEqual(self.calc.subtract(10, 5), 5)
        self.assertEqual(self.calc.subtract(-1, -1), 0)

if __name__ == '__main__':
    unittest.main()