import unittest
from records_005 import without_last_5

class RecordTests(unittest.TestCase):
    def test_result_drops_last(self):
        self.assertEqual(without_last_5([31, 32, 33]), [31, 32])

if __name__ == "__main__":
    unittest.main()
