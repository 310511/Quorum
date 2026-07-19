import unittest
from parser_ok8_base import identity_parser_ok8

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_parser_ok8(5), 5)

if __name__ == "__main__":
    unittest.main()
