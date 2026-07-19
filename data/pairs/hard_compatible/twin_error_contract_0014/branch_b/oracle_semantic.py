import unittest
from parser_014 import valid_count_14

class SemanticOracle(unittest.TestCase):
    def test_invalid_number_is_rejected(self):
        self.assertFalse(valid_count_14("not-a-number-84"))
