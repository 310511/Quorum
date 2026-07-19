import unittest
from records_015 import without_last_15

class RecordTests(unittest.TestCase):
    def test_result_drops_last(self):
        self.assertEqual(without_last_15([91, 92, 93]), [91, 92])

if __name__ == "__main__":
    unittest.main()
