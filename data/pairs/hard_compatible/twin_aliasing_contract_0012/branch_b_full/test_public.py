import unittest
from records_012 import without_last_12

class RecordTests(unittest.TestCase):
    def test_result_drops_last(self):
        self.assertEqual(without_last_12([73, 74, 75]), [73, 74])

if __name__ == "__main__":
    unittest.main()
