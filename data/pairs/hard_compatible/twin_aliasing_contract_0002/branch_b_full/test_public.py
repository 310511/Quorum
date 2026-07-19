import unittest
from records_002 import without_last_2

class RecordTests(unittest.TestCase):
    def test_result_drops_last(self):
        self.assertEqual(without_last_2([13, 14, 15]), [13, 14])

if __name__ == "__main__":
    unittest.main()
