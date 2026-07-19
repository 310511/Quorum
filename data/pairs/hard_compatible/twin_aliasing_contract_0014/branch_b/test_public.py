import unittest
from records_014 import without_last_14

class RecordTests(unittest.TestCase):
    def test_result_drops_last(self):
        self.assertEqual(without_last_14([85, 86, 87]), [85, 86])

if __name__ == "__main__":
    unittest.main()
