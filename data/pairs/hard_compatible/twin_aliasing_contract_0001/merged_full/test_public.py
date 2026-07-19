import unittest
from records_001 import without_last_1

class RecordTests(unittest.TestCase):
    def test_result_drops_last(self):
        self.assertEqual(without_last_1([7, 8, 9]), [7, 8])

if __name__ == "__main__":
    unittest.main()
