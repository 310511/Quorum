import unittest
from records_003 import without_last_3

class RecordTests(unittest.TestCase):
    def test_result_drops_last(self):
        self.assertEqual(without_last_3([19, 20, 21]), [19, 20])

if __name__ == "__main__":
    unittest.main()
