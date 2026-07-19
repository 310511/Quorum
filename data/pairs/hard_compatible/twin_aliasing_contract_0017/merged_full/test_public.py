import unittest
from records_017 import without_last_17

class RecordTests(unittest.TestCase):
    def test_result_drops_last(self):
        self.assertEqual(without_last_17([103, 104, 105]), [103, 104])

if __name__ == "__main__":
    unittest.main()
