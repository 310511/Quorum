import unittest
from parser_016 import valid_count_16

class SemanticOracle(unittest.TestCase):
    def test_invalid_number_is_rejected(self):
        self.assertFalse(valid_count_16("not-a-number-96"))
