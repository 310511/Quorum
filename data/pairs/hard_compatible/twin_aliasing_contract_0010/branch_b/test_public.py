import unittest
from records_010 import without_last_10

class RecordTests(unittest.TestCase):
    def test_result_drops_last(self):
        self.assertEqual(without_last_10([61, 62, 63]), [61, 62])

if __name__ == "__main__":
    unittest.main()
