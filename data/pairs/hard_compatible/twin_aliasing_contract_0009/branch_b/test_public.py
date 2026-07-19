import unittest
from records_009 import without_last_9

class RecordTests(unittest.TestCase):
    def test_result_drops_last(self):
        self.assertEqual(without_last_9([55, 56, 57]), [55, 56])

if __name__ == "__main__":
    unittest.main()
