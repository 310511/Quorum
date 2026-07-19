import unittest
from records_011 import without_last_11

class RecordTests(unittest.TestCase):
    def test_result_drops_last(self):
        self.assertEqual(without_last_11([67, 68, 69]), [67, 68])

if __name__ == "__main__":
    unittest.main()
