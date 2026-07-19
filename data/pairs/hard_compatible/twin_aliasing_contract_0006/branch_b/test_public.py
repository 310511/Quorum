import unittest
from records_006 import without_last_6

class RecordTests(unittest.TestCase):
    def test_result_drops_last(self):
        self.assertEqual(without_last_6([37, 38, 39]), [37, 38])

if __name__ == "__main__":
    unittest.main()
