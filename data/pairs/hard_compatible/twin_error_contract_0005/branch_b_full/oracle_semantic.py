import unittest
from parser_005 import valid_count_5

class SemanticOracle(unittest.TestCase):
    def test_invalid_number_is_rejected(self):
        self.assertFalse(valid_count_5("not-a-number-30"))
