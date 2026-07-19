import unittest
from parser_006 import valid_count_6

class SemanticOracle(unittest.TestCase):
    def test_invalid_number_is_rejected(self):
        self.assertFalse(valid_count_6("not-a-number-36"))
