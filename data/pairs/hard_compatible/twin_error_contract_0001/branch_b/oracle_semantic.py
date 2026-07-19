import unittest
from parser_001 import valid_count_1

class SemanticOracle(unittest.TestCase):
    def test_invalid_number_is_rejected(self):
        self.assertFalse(valid_count_1("not-a-number-6"))
