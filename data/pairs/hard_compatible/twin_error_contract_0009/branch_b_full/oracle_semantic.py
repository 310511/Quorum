import unittest
from parser_009 import valid_count_9

class SemanticOracle(unittest.TestCase):
    def test_invalid_number_is_rejected(self):
        self.assertFalse(valid_count_9("not-a-number-54"))
