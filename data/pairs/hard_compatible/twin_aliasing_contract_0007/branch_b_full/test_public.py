import unittest
from records_007 import without_last_7

class RecordTests(unittest.TestCase):
    def test_result_drops_last(self):
        self.assertEqual(without_last_7([43, 44, 45]), [43, 44])

if __name__ == "__main__":
    unittest.main()
