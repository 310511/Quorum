import unittest

from calculator import add_v2, calculate_total


class CalculatorTests(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add_v2(2, 3), 5)

    def test_total(self):
        self.assertEqual(calculate_total([2, 3]), 5)


if __name__ == "__main__":
    unittest.main()
