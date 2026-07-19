import unittest
from parser_ok28_base import identity_parser_ok28

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_parser_ok28(5), 5)

if __name__ == "__main__":
    unittest.main()
