import unittest
from records_013 import without_last_13

class RecordTests(unittest.TestCase):
    def test_result_drops_last(self):
        self.assertEqual(without_last_13([79, 80, 81]), [79, 80])

if __name__ == "__main__":
    unittest.main()
