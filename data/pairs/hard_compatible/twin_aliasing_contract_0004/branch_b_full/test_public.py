import unittest
from records_004 import without_last_4

class RecordTests(unittest.TestCase):
    def test_result_drops_last(self):
        self.assertEqual(without_last_4([25, 26, 27]), [25, 26])

if __name__ == "__main__":
    unittest.main()
